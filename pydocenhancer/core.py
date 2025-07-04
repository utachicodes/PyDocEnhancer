import ast
import inspect
from typing import Dict, List, Optional
import os
import sys
import io
import contextlib
import requests

class DocEnhancer:
    def __init__(self, provider: str, api_key: str = None, model: str = None, language: str = "en"):
        """
        Initialize PyDocEnhancer with an AI provider.
        :param provider: AI provider ("openai", "local").
        :param api_key: API key for cloud providers (optional).
        :param model: Model name for LLM (e.g., "llama3.2" for local).
        :param language: Output language for documentation (default: "en").
        """
        if provider is None or provider == "mock":
            raise ValueError("A real LLM provider is required. Please specify --provider local or --provider openai and a valid model.")
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.language = language
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "openai":
            import openai
            openai.api_key = self.api_key
            return openai
        elif self.provider == "local" and self.model and "ollama" in self.model.lower():
            # No client needed, will use requests to localhost
            return "ollama"
        elif self.provider == "local":
            try:
                from ctransformers import AutoModelForCausalLM
                llm = AutoModelForCausalLM.from_pretrained(self.model)
                return llm
            except ImportError:
                raise ImportError("ctransformers is required for local LLMs. Install with 'pip install pydocenhancer[local]'.")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported providers are 'openai' and 'local'.")

    def _llm_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self.model.split("/", 1)[-1], "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama LLM request failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error from Ollama LLM: {e}")

    def _llm_openai(self, prompt: str) -> str:
        try:
            completion = self.llm.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI LLM request failed: {e}")

    def _llm_local(self, prompt: str) -> str:
        if not self.llm:
            raise RuntimeError("Local LLM is not initialized.")
        return self.llm(prompt)

    def _llm(self, text: str, task: str, language: str = None) -> str:
        lang = language or self.language
        prompt = ""
        if task == "summarize":
            prompt = f"Summarize the following Python code in {lang}:\n{text}"
        elif task == "explain":
            prompt = f"Explain what the following Python code does in {lang}:\n{text}"
        elif task == "translate":
            prompt = f"Translate the following documentation to {lang}:\n{text}"
        elif task == "example":
            prompt = f"Generate a usage example for the following Python function in {lang}:\n{text}"
        else:
            prompt = text

        if self.provider == "openai":
            return self._llm_openai(prompt)
        elif self.provider == "local" and self.model and "ollama" in self.model.lower():
            return self._llm_ollama(prompt)
        elif self.provider == "local":
            return self._llm_local(prompt)
        else:
            raise ValueError("A real LLM provider is required. The 'mock' provider is not supported.")

    def parse_module(self, module_path: str) -> List[Dict]:
        """Parse a Python module and extract function details."""
        try:
            with open(module_path, "r") as file:
                code = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Module file not found: {module_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied when reading: {module_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading file {module_path}: {e}")
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {module_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing AST for {module_path}: {e}")
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node) or "No docstring"
                # Safely extract source code from the AST node
                try:
                    # Try to use ast.unparse (Python 3.9+)
                    source = ast.unparse(node)
                except AttributeError:
                    # Fallback for older Python versions: extract from original code
                    source_lines = code.splitlines()
                    start_line = node.lineno - 1  # AST line numbers are 1-indexed
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                    source = '\n'.join(source_lines[start_line:end_line])
                except Exception as e:
                    source = f"Error extracting source: {e}"
                example = self.extract_example_from_docstring(docstring)
                try:
                    docstring_translated = self._llm(docstring, "translate", self.language)
                except Exception as e:
                    docstring_translated = f"Error from LLM: {e}"
                try:
                    summary = self._llm(docstring, "summarize", self.language)
                except Exception as e:
                    summary = f"Error from LLM: {e}"
                try:
                    explanation = self._llm(source, "explain", self.language)
                except Exception as e:
                    explanation = f"Error from LLM: {e}"
                try:
                    example_out = self._llm(source, "example", self.language)
                except Exception as e:
                    example_out = f"Error from LLM: {e}"
                functions.append({
                    "name": func_name,
                    "docstring": docstring_translated,
                    "source": source,
                    "summary": summary,
                    "explanation": explanation,
                    "example": example_out,
                    "example_test_result": self.test_example_code(example) if example else None
                })
        return functions

    def extract_example_from_docstring(self, docstring: str) -> Optional[str]:
        """Extract example code from a docstring if present."""
        # Simple heuristic: look for lines starting with 'Example:' or code blocks
        lines = docstring.splitlines()
        example_lines = []
        in_example = False
        for line in lines:
            if 'Example' in line:
                in_example = True
                continue
            if in_example:
                if line.strip() == '' or line.strip().startswith('>>>'):
                    continue
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    break
                example_lines.append(line)
        return '\n'.join(example_lines).strip() if example_lines else None

    def test_example_code(self, code: str) -> str:
        """Run the example code and return the output or error."""
        if not code:
            return "No example to test."
        try:
            # Redirect stdout to capture print output
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exec(code, {})
            return f"Success. Output:\n{stdout.getvalue()}"
        except Exception as e:
            return f"Error: {e}"

    def generate_docs(self, module_path: str, output_dir: str, language: Optional[str] = None) -> None:
        """Generate markdown documentation for a module, optionally in a different language."""
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                raise RuntimeError(f"Could not create output directory {output_dir}: {e}")
        lang = language or self.language
        try:
            functions = self.parse_module(module_path)
        except Exception as e:
            raise RuntimeError(f"Failed to parse module: {e}")
        output_file = os.path.join(output_dir, f"{os.path.basename(module_path)}.{lang}.md")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Documentation for {os.path.basename(module_path)} [{lang}]\n\n")
                for func in functions:
                    f.write(f"## Function: {func['name']}\n")
                    f.write(f"**Docstring**: {func['docstring']}\n\n")
                    f.write(f"**Summary**: {func['summary']}\n\n")
                    f.write(f"**Explanation**: {func['explanation']}\n\n")
                    if func['example']:
                        f.write(f"**Example**:\n```python\n{func['example']}\n```\n\n")
                        f.write(f"**Example Test Result**: {func['example_test_result']}\n\n")
                    f.write("```python\n" + func['source'] + "\n```\n\n")
        except Exception as e:
            raise RuntimeError(f"Failed to write documentation file: {e}")

    def search_docs(self, query: str, docs_dir: str) -> List[str]:
        """Search documentation using a natural language query (mock implementation)."""
        return [f"Found match for '{query}' in {docs_dir} (mock result)"] 