from setuptools import setup, find_packages

setup(
    name="graphfusionai",
    version="0.1.0",
    description="A Python framework for building multi-agent systems with Knowledge Graph integration",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=[
        "flask-login>=0.6.3",
        "flask-wtf>=1.2.2",
        "hatchling>=1.27.0",
        "networkx>=3.4.2",
        "numpy>=2.2.3",
        "oauthlib>=3.2.2",
        "openai>=1.64.0",
        "pydantic>=2.10.6",
        "rich>=13.9.4",
        "scikit-learn>=1.6.1",
        "spacy>=3.8.4",
        "transformers>=4.49.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
