from setuptools import setup, find_packages

setup(
    name="pydocenhancer",
    version="0.1.0",
    author="Abdoullah Ndao",
    author_email="abdoullahaljersi@gmail.com",
    description="AI-powered Python documentation enhancer supporting local LLMs (LLaMA, Ollama) and cloud providers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pydocenhancer",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers>=2.2.2",
        "llama-cpp-python>=0.2.0",
        "click>=8.1.0",
    ],
    extras_require={
        "cloud": ["openai>=1.0.0", "anthropic>=0.3.0"],
    },
    entry_points={
        "console_scripts": [
            "pydocenhancer=pydocenhancer.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 