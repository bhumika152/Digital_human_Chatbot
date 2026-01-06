from setuptools import setup, find_packages

setup(
    name="digital-human-sdk",
    version="0.1.0",
    description="Digital Human Orchestration SDK",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0",
        "openai-agents[litellm]",
    ],
)
