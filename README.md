# PyDocEnhancer

AI-powered Python plugin to enhance documentation with summaries, code explanations, examples, semantic search, **automated example testing**, and **multilingual documentation**.

## Features
- **Auto-Generated Summaries**: Summarize modules, classes, and functions.
- **Code Explanations**: Plain-English explanations of code logic.
- **Semantic Search**: Query documentation with natural language (e.g., "find data processing functions").
- **Auto-Generated Examples**: Create working code examples from docstrings.
- **Automated Example Testing**: Extracts and runs code examples from docstrings, reporting results in the docs.
- **Multilingual Documentation**: Generate documentation in multiple languages (e.g., English, French, Spanish, Chinese) using LLM translation.
- **Local LLM Support**: Privacy-first processing with local models (e.g., LLaMA 3.2, ctransformers backend).
- **Integrations**: Works with Sphinx, MkDocs, and Jupyter Notebooks.

## LLM Requirement

> **PyDocEnhancer requires a real LLM provider and model.**
>
> - Specify a valid provider (`local` for ctransformers/Ollama, or `openai` for OpenAI API) and a model (e.g., `ollama/llama3.2:latest`).
> - Mock mode is not supported.
> - This is enforced in both the Python API and CLI.

## Installation
```bash
pip install pydocenhancer[local]
```
For most users, the `[local]` extra is recommended. This uses the ctransformers backend, which does not require C++ build tools and works on most platforms. Only use the base install or cloud extras if you specifically need those features.

If you want to use the `llama-cpp-python` backend, install with:
```bash
pip install pydocenhancer[llama]
```
Note: This requires C++ build tools on Windows (see Troubleshooting below).

## Quick Start
```python
from pydocenhancer import DocEnhancer

# Initialize with a real LLM (Ollama or LLaMA)
enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest", language="fr")
enhancer.generate_docs(module_path="my_project/utils.py", output_dir="docs", language="fr")

# Search documentation
results = enhancer.search_docs("file handling functions", "docs")
print(results)
```

> **Note:** You must specify a real LLM provider and model. The tool will not work without a valid provider (e.g., `local` or `openai`) and model (e.g., `ollama/llama3.2:latest`).

## CLI Usage
```bash
# Generate documentation with Ollama in English, with example testing
pydocenhancer enhance --module my_project/utils.py --output docs/ --provider local --model ollama/llama3.2:latest --language en

# Search documentation
pydocenhancer search --query "data processing functions" --docs-dir docs/
```

## Requirements
- Python 3.8+
- Local LLM (e.g., LLaMA 3.2 via `ctransformers`)
- Optional: Sphinx or MkDocs for integration

### Windows Users
If you want to use local LLMs, install with:
```
pip install pydocenhancer[local]
```
No C++ build tools required for ctransformers wheels.

### Troubleshooting Installation (Windows)

Some features (such as local LLMs using `llama-cpp-python`) require compiling native code. If you see errors like:

```
CMake Error: CMAKE_C_COMPILER not set, after EnableLanguage
CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
CMake Error at CMakeLists.txt:3 (project):
  Running 'nmake' '-?' failed with: no such file or directory
```

This means your system is missing the required C/C++ build tools for compiling Python packages with native code.

#### How to Fix (Windows)
1. **Install Visual Studio Build Tools**
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - During installation, select:
     - "Desktop development with C++"
     - Ensure "C++ build tools", "Windows 10 SDK", and "CMake" are checked.
2. **Restart your terminal** (or use the "Developer Command Prompt for VS").
3. **Retry installation**:
   ```sh
   pip install pydocenhancer
   ```

#### Debugging Tips
- If you see errors about missing `nmake` or C/C++ compilers, the build tools are not installed or not in your PATH.
- Try installing `llama-cpp-python` directly to see detailed errors:
  ```sh
  pip install llama-cpp-python
  ```
- If you want to avoid C++ build tools, use the `[local]` extra to install with `ctransformers` backend (pre-built wheels):
  ```sh
  pip install pydocenhancer[local]
  ```
- For advanced debugging, check the full error log and search for the first error message.

#### Alternative: Use WSL
If you have trouble with Windows build tools, consider using [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/) for easier compilation of native code.

### Common Errors & Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `ImportError: ctransformers is required for local LLMs.` | You tried to use a local LLM without installing ctransformers. | Run `pip install pydocenhancer[local]` |
| `FileNotFoundError: [Errno 2] No such file or directory` | The module path you provided does not exist. | Check the path and try again. |
| `RuntimeError: Local LLM is not initialized.` | The local model failed to load or is not available. | Check your model name and installation. |
| `requests.exceptions.ConnectionError` | Ollama is not running or not reachable. | Start Ollama and ensure the model is pulled. |
| `Error: ...` in Example Test Result | The example code in the docstring is invalid or raises an exception. | Fix the example code in your docstring. |
| `CMake Error: CMAKE_C_COMPILER not set...` | Missing C++ build tools on Windows. | See Troubleshooting Installation (Windows) above. |
| `ModuleNotFoundError: No module named 'llama_cpp_python'` | You tried to use the llama backend without installing it. | Run `pip install pydocenhancer[llama]` |

### Additional Debugging Steps

- **Verbose Output:** Run with `-v` or `--verbose` if available, or set environment variable `PYTHONVERBOSE=1` for more details.
- **Check Python Version:** Ensure you are using Python 3.8+.
- **Check Dependencies:** Run `pip check` to see if any dependencies are missing or incompatible.
- **Update pip:** Sometimes, upgrading pip helps: `python -m pip install --upgrade pip`.

### Packaging Note for Windows Users
- If you want to use local LLMs **without** C++ build tools, install with:
  ```sh
  pip install pydocenhancer[local]
  ```
  This uses the `ctransformers` backend, which provides pre-built wheels and does not require compilation.
- If you want to use the `llama-cpp-python` backend, you **must** have Visual Studio Build Tools installed as described above, and install with:
  ```sh
  pip install pydocenhancer[llama]
  ```

## Documentation
Full documentation is available in this README and at [GitHub](https://github.com/utachicodes/PyDocEnhancer#readme).

## License
MIT © Abdoullah Ndao <abdoullahaljersi@gmail.com> 