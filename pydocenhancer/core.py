import ast
import inspect
from typing import Dict, List, Optional
import os
import sys
import io
import contextlib
import requests

class DocEnhancer:
    def __init__(self, provider: str = "mock", api_key: str = None, model: str = "mock-model", language: str = "en"):
        """
        Initialize PyDocEnhancer with an AI provider.
        :param provider: AI provider ("mock", "openai", "local").
        :param api_key: API key for cloud providers (optional).
        :param model: Model name for LLM (e.g., "llama3.2" for local).
        :param language: Output language for documentation (default: "en").
        """
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
        elif self.provider == "local" and "ollama" in self.model.lower():
            # No client needed, will use requests to localhost
            return "ollama"
        elif self.provider == "local":
            from llama_cpp import Llama
            return Llama(model_path=self.model)
        return None

    def _llm_ollama(self, prompt: str) -> str:
        # Assumes Ollama is running locally with the desired model pulled
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model.split("/", 1)[-1], "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    def _llm_openai(self, prompt: str) -> str:
        completion = self.llm.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()

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
        elif self.provider == "local" and "ollama" in self.model.lower():
            return self._llm_ollama(prompt)
        else:
            return self._mock_llm(text, task, lang)

    def _mock_llm(self, text: str, task: str, language: Optional[str] = None) -> str:
        """Mock LLM response for demo purposes."""
        lang = language or self.language
        if task == "summarize":
            return f"[{lang}] Summary of {text[:50]}...: This code performs a specific function."
        elif task == "explain":
            return f"[{lang}] Explanation of {text[:50]}...: This function processes input data."
        elif task == "translate":
            return f"[{lang}] {text}"
        elif task == "example":
            return f"# Example usage in {lang}\n{text}"
        return ""

    def parse_module(self, module_path: str) -> List[Dict]:
        """Parse a Python module and extract function details."""
        with open(module_path, "r") as file:
            code = file.read()
        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node) or "No docstring"
                source = inspect.getsource(getattr(inspect.getmodule(node), func_name, None))
                example = self.extract_example_from_docstring(docstring)
                functions.append({
                    "name": func_name,
                    "docstring": self._llm(docstring, "translate", self.language),
                    "source": source,
                    "summary": self._llm(docstring, "summarize", self.language),
                    "explanation": self._llm(source, "explain", self.language),
                    "example": self._llm(source, "example", self.language),
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
            os.makedirs(output_dir)
        lang = language or self.language
        functions = self.parse_module(module_path)
        output_file = os.path.join(output_dir, f"{os.path.basename(module_path)}.{lang}.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Documentation for {os.path.basename(module_path)} [{lang}]\n\n")
            for func in functions:
                f.write(f"## Function: {func['name']}\n")
                f.write(f"**Docstring**: {self._llm(func['docstring'], 'translate', lang)}\n\n")
                f.write(f"**Summary**: {self._llm(func['docstring'], 'summarize', lang)}\n\n")
                f.write(f"**Explanation**: {self._llm(func['source'], 'explain', lang)}\n\n")
                if func['example']:
                    f.write(f"**Example**:\n```python\n{func['example']}\n```\n\n")
                    f.write(f"**Example Test Result**: {func['example_test_result']}\n\n")
                f.write("```python\n" + func['source'] + "\n```\n\n")

    def search_docs(self, query: str, docs_dir: str) -> List[str]:
        """Search documentation using a natural language query (mock implementation)."""
        return [f"Found match for '{query}' in {docs_dir} (mock result)"] 