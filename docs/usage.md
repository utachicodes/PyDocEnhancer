# Usage Guide

## CLI Commands
### Enhance
Generate documentation for a Python module (with Ollama):
```bash
pydocenhancer enhance --module my_project/utils.py --output docs/ --provider local --model ollama/llama3
```

### Search
Search documentation with a natural language query:
```bash
pydocenhancer search --query "file handling functions" --docs-dir docs/
```

## Python API
```python
from pydocenhancer import DocEnhancer

# Initialize with Ollama
enhancer = DocEnhancer(provider="local", model="ollama/llama3")

# Generate docs
enhancer.generate_docs(module_path="my_project/utils.py", output_dir="docs")

# Search docs
results = enhancer.search_docs("file handling functions", "docs")
print(results)
```

## Example Output
For a file `utils.py`:
```python
def calculate_metrics(data):
    """Calculate statistical metrics from a dataset."""
    return sum(data) / len(data)
```

Generated `docs/utils.py.md`:
```markdown
# Documentation for utils.py

## Function: calculate_metrics
**Docstring**: Calculate statistical metrics from a dataset.

**Summary**: This function computes the average of a dataset.

**Explanation**: The function takes a list of numbers, sums them, and divides by the count to return the mean.

```python
def calculate_metrics(data):
    """Calculate statistical metrics from a dataset."""
    return sum(data) / len(data)
```
``` 