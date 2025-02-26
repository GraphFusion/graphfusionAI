# Dependencies Documentation

## Core Dependencies

The following Python packages are required for the graphfusionAI Framework:

### Required Packages
- **networkx** (>=2.5)
  - Purpose: Knowledge graph implementation and graph operations
  - Usage: Core component for knowledge representation

- **spacy** (>=3.0.0)
  - Purpose: Natural Language Processing and entity extraction
  - Usage: Text analysis and knowledge extraction
  - Required Model: en_core_web_sm

- **pydantic** (>=1.10.0)
  - Purpose: Data validation and model definitions
  - Usage: Type checking and data structure validation

### Language Models

The following language models are required:

- **spaCy English Model**
  ```bash
  python -m spacy download en_core_web_sm
  ```

## Installation

The required packages can be installed using the Replit package manager or pip:

```bash
# Using Replit package manager
python -m pip install networkx spacy pydantic

# Install spaCy English language model
python -m spacy download en_core_web_sm
```

## Optional Dependencies

For extended features and examples:

- **numpy** - For advanced numerical operations
- **scikit-learn** - For machine learning capabilities
- **transformers** - For advanced NLP tasks
- **rich** - For enhanced console output

## Development Dependencies

These packages are recommended for development:

- **pytest** - For running tests
- **black** - For code formatting
- **flake8** - For linting
- **mypy** - For static type checking

## System Requirements

- Python 3.8 or higher
- Sufficient memory for loading language models (minimum 4GB recommended)
- Disk space for language models and knowledge graph storage

## Version Compatibility

The framework has been tested with the following version combinations:

- Python 3.8-3.11
- networkx 2.5+
- spacy 3.0+
- pydantic 1.10+

## Notes

1. Memory requirements may vary based on the size of your knowledge graphs and the number of concurrent agents.
2. For production deployments, consider using more comprehensive language models (e.g., en_core_web_md or en_core_web_lg).
3. Some examples may require additional dependencies not listed here. Check individual example documentation for specific requirements.
