# Contributing to GraphFusionAI

Thank you for your interest in contributing to the GraphFusion Core project! This document outlines the guidelines and best practices for contributing to ensure a smooth and collaborative workflow.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Code of Conduct](#code-of-conduct)
3. [Submitting Changes](#submitting-changes)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#Documentation)


### 1. Getting Started

1. **Fork the Repository**: Fork the repository to your GitHub account to start working on any changes.
2. **Clone Your Fork**: Clone your fork to your local machine.
   ```bash
   git clone https://github.com/your-username/graphfusion-core.git
   cd graphfusionai
   ```
3. **Create a Branch**: Create a new branch for each feature or bug fix.
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 2. Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please read it to understand the expected behavior in all project interactions.

### 3. Submitting Changes

1. **Commit Changes**: Make small, focused commits with clear messages explaining the purpose of each change.
2. **Push to Your Fork**: Push your changes to your forked repository.
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Submit a Pull Request (PR)**: Open a pull request on the main repository. Link any related issues and add reviewers if needed.

4. **Review Process**: A project maintainer will review your PR. Address any feedback and make updates if required. Ensure that all automated checks pass before final review and approval.

### 4. Development Workflow

- **Sync with Main Branch**: Regularly sync your branch with the main branch to avoid merge conflicts.
   ```bash
   git fetch origin
   git merge origin/main
   ```

- **Run Tests Locally**: Before submitting a pull request, ensure all tests pass on your local setup.
   ```bash
   poetry run pytest
   ```

### 5. Coding Standards

- **Follow PEP 8**: Adhere to the PEP 8 style guide for Python.
- **Use Type Hints**: Type hints improve readability and maintainability. Add type hints for all public methods and functions.
- **Linting**: We use `black` for code formatting and `flake8` for linting. Please run both before submitting your changes.
   ```bash
   poetry run black src/
   poetry run flake8 src/
   ```

### 6. Testing

- **Unit Tests**: Write unit tests for new features and bug fixes to ensure they work as expected.
- **Test Coverage**: Aim to maintain high test coverage. We recommend a minimum of 90% coverage for new code.
- **Test Naming**: Name test functions descriptively (e.g., `test_confidence_score_calculation`).
- **Mocking**: Use mocks for external dependencies where appropriate to isolate the unit being tested.

### 7. Documentation

- **Docstrings**: Add docstrings to all public functions and classes using Google style.
- **README and Guides**: Update the `README.md` or relevant `docs/` guides if you are adding significant functionality.
- **Changelog**: Document any user-facing changes in `CHANGELOG.md`.

Thank you for contributing to GraphFusion! We’re excited to have you involved and look forward to working together to build a powerful platform.
