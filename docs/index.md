# PyDocEnhancer Documentation

Welcome to PyDocEnhancer, an AI-powered tool for enhancing Python documentation with summaries, explanations, examples, and semantic search.

## Getting Started

Install PyDocEnhancer:
```bash
pip install pydocenhancer
```

Generate documentation (with Ollama):
```bash
pydocenhancer enhance --module my_project/utils.py --output docs/ --provider local --model ollama/llama3
```

Search documentation:
```bash
pydocenhancer search --query "data processing functions" --docs-dir docs/
```

## Features
- **Summaries**: Auto-generate concise summaries for functions, classes, and modules.
- **Explanations**: Plain-English explanations of code logic.
- **Examples**: Generate working code examples from docstrings.
- **Semantic Search**: Query documentation with natural language.
- **Local LLMs**: Privacy-first processing with local models (LLaMA, Ollama).
- **Integrations**: Supports Sphinx, MkDocs, and Jupyter.

## Configuration
- **provider**: Choose "local", "openai", or "anthropic".
- **model**: Specify the LLM (e.g., "llama3.2" for LLaMA, "ollama/llama3" for Ollama).
- **api_key**: Required for cloud providers.

See [usage.md](usage.md) for detailed examples.

## License
MIT © Abdoullah Ndao <abdoullahaljersi@gmail.com> 