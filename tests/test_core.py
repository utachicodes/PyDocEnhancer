import pytest
from pydocenhancer.core import DocEnhancer
import os

@pytest.fixture
def enhancer():
    return DocEnhancer(provider="mock")

def test_parse_module(enhancer, tmp_path):
    # Create a sample Python file
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("""
def example_function(x):
    '''Example function that doubles x.'''
    return x * 2
""")
    functions = enhancer.parse_module(str(sample_file))
    assert len(functions) == 1
    assert functions[0]["name"] == "example_function"
    assert functions[0]["docstring"] == "Example function that doubles x."
    assert "Summary" in functions[0]["summary"]

def test_generate_docs(enhancer, tmp_path):
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("""
def example_function(x):
    '''Example function that doubles x.'''
    return x * 2
""")
    output_dir = tmp_path / "docs"
    enhancer.generate_docs(str(sample_file), str(output_dir))
    output_file = output_dir / "sample.py.md"
    assert output_file.exists()
    content = output_file.read_text()
    assert "example_function" in content
    assert "Summary" in content 