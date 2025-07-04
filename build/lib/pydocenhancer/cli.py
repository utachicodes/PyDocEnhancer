import click
from .core import DocEnhancer

@click.group()
def cli():
    """PyDocEnhancer CLI for AI-powered documentation."""
    pass

@cli.command()
@click.option("--module", required=True, help="Path to Python module")
@click.option("--output", default="docs", help="Output directory for documentation")
@click.option("--provider", default="mock", help="AI provider (mock, openai, local [ctransformers])")
@click.option("--model", default="mock-model", help="Model name (e.g., llama3.2)")
@click.option("--api-key", default=None, help="API key for cloud providers")
@click.option("--language", default="en", help="Language code for documentation (e.g., en, fr, es, zh)")
def enhance(module, output, provider, model, api_key, language):
    """Generate enhanced documentation for a Python module, with optional language translation and example testing."""
    enhancer = DocEnhancer(provider=provider, model=model, api_key=api_key, language=language)
    enhancer.generate_docs(module_path=module, output_dir=output, language=language)
    click.echo(f"Documentation generated in {output} (language: {language})")

@cli.command()
@click.option("--query", required=True, help="Search query")
@click.option("--docs-dir", default="docs", help="Directory with documentation")
def search(query, docs_dir):
    """Search documentation with a natural language query."""
    enhancer = DocEnhancer()
    results = enhancer.search_docs(query, docs_dir)
    for result in results:
        click.echo(result)

def main():
    cli() 