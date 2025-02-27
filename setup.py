from setuptools import setup, find_packages

setup(
    name="graphfusionai",
    version="0.1.1",  # Updated version number
    description="A Python framework for building multi-agent systems with Knowledge Graph integration",
    python_requires=">=3.11",
    packages=find_packages(),
    package_data={
        'graphfusionai': ['examples/*.py'],
    },
    install_requires=[
        "flask-login>=0.6.3",
        "flask-wtf>=1.2.2",
        "hatchling>=1.27.0",
        "networkx>=3.4.2",
        "numpy>=1.24.0",  # Fixed NumPy version requirement
        "oauthlib>=3.2.2",
        "openai>=1.64.0",
        "pydantic>=2.10.6",
        "rich>=13.9.4",
        "scikit-learn>=1.6.1",
        "spacy>=3.8.4",
        "transformers>=4.49.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",  # Explicitly marks it as an early-stage release
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
)
