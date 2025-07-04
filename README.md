# PyDocEnhancer

AI-powered Python plugin to enhance documentation with summaries, code explanations, examples, semantic search, **automated example testing**, and **multilingual documentation**.

## Features
- **Auto-Generated Summaries**: Summarize modules, classes, and functions.
- **Code Explanations**: Plain-English explanations of code logic.
- **Semantic Search**: Query documentation with natural language (e.g., "find data processing functions").
- **Auto-Generated Examples**: Create working code examples from docstrings.
- **Automated Example Testing**: Extracts and runs code examples from docstrings, reporting results in the docs.
- **Multilingual Documentation**: Generate documentation in multiple languages (e.g., English, French, Spanish, Chinese) using LLM translation.
- **Local LLM Support**: Privacy-first processing with local models (e.g., LLaMA 3.2, Ollama).
- **Integrations**: Works with Sphinx, MkDocs, and Jupyter Notebooks.

## Installation
```bash
pip install pydocenhancer
```

## Quick Start
```python
from pydocenhancer import DocEnhancer

# Initialize with a local LLM (Ollama or LLaMA), generate docs in French
enhancer = DocEnhancer(provider="local", model="ollama/llama3", language="fr")
enhancer.generate_docs(module_path="my_project/utils.py", output_dir="docs", language="fr")

# Search documentation
results = enhancer.search_docs("file handling functions", "docs")
print(results)
```

## CLI Usage
```bash
# Generate documentation with Ollama in Spanish, with example testing
pydocenhancer enhance --module my_project/utils.py --output docs/ --provider local --model ollama/llama3 --language es

# Search documentation
pydocenhancer search --query "data processing functions" --docs-dir docs/
```

## Requirements
- Python 3.8+
- Local LLM (e.g., LLaMA 3.2 via `llama-cpp-python` or Ollama)
- Optional: Sphinx or MkDocs for integration

## Documentation
Full documentation is available at [ReadTheDocs](https://pydocenhancer.readthedocs.io).

## License
MIT © Abdoullah Ndao <abdoullahaljersi@gmail.com> 