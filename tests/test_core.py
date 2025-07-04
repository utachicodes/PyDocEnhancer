import pytest
from pydocenhancer.core import DocEnhancer
import os
import tempfile
import shutil
from unittest import mock
import click
from click.testing import CliRunner
from pydocenhancer import cli

@pytest.fixture
def enhancer():
    return DocEnhancer(provider="local", model="ollama/llama3.2:latest")

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

def test_parse_module_file_not_found():
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    with pytest.raises(FileNotFoundError):
        enhancer.parse_module("nonexistent_file.py")

def test_parse_module_permission_denied(tmp_path):
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("def foo():\n    return 1\n")
    os.chmod(sample_file, 0)  # Remove all permissions
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    try:
        with pytest.raises(PermissionError):
            enhancer.parse_module(str(sample_file))
    finally:
        os.chmod(sample_file, 0o644)  # Restore permissions

def test_parse_module_syntax_error(tmp_path):
    sample_file = tmp_path / "bad.py"
    sample_file.write_text("def bad(:\n    pass\n")
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    with pytest.raises(SyntaxError):
        enhancer.parse_module(str(sample_file))

def test_llm_ollama_network_error(monkeypatch):
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    def fail_post(*args, **kwargs):
        raise Exception("Network down!")
    monkeypatch.setattr("requests.post", fail_post)
    with pytest.raises(RuntimeError):
        enhancer._llm_ollama("prompt")

def test_function_with_decorator(tmp_path):
    sample_file = tmp_path / "decorated.py"
    sample_file.write_text("""
@staticmethod
def foo():
    '''Docstring.'''
    return 1
""")
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    functions = enhancer.parse_module(str(sample_file))
    assert functions[0]["name"] == "foo"

def test_function_no_docstring(tmp_path):
    sample_file = tmp_path / "nodoc.py"
    sample_file.write_text("""
def foo():
    return 1
""")
    enhancer = DocEnhancer(provider="local", model="ollama/llama3.2:latest")
    functions = enhancer.parse_module(str(sample_file))
    assert functions[0]["docstring"]

def test_cli_enhance(tmp_path):
    sample_file = tmp_path / "cli.py"
    sample_file.write_text("""
def foo():
    '''Docstring.'''
    return 1
""")
    output_dir = tmp_path / "docs"
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["enhance", "--module", str(sample_file), "--output", str(output_dir), "--provider", "local", "--model", "ollama/llama3.2:latest"])
    assert result.exit_code == 0 