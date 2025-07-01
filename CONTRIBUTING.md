# Contributing to Analytics Agent CLI

Thank you for your interest in contributing to Analytics Agent CLI! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/analytics-agent-cli.git
   cd analytics-agent-cli
   ```
3. **Set up development environment**:
   ```bash
   # Install in development mode
   pip install -e .
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run code quality checks**:
   ```bash
   black staffer/
   flake8 staffer/
   isort staffer/
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "add new analytics feature"
   ```

6. **Push and create a Pull Request**

## Coding Standards

- **Python Style**: Follow PEP 8, use `black` for formatting
- **Imports**: Use `isort` for import organization
- **Testing**: Write tests for new functionality
- **Documentation**: Update relevant documentation

## Testing

- Run the full test suite: `pytest`
- Run with coverage: `pytest --cov=staffer`
- Test specific modules: `pytest tests/test_specific_module.py`

## Adding New Analytics Functions

1. **Create the function** in `staffer/functions/analytics/tools/`
2. **Register it** in `staffer/function_registries/analytics_registry.py`
3. **Add tests** in `tests/`
4. **Update documentation** if needed

## Pull Request Guidelines

- **Clear description** of what the PR does
- **Link to related issues** if applicable
- **Include tests** for new functionality
- **Update documentation** if needed
- **Ensure CI passes** before requesting review

## Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** first
2. **Use clear, descriptive titles**
3. **Include steps to reproduce** (for bugs)
4. **Provide system information** (OS, Python version, etc.)
5. **Include relevant error messages**

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment for all contributors

## Questions?

Feel free to open an issue with the `question` label if you need help or clarification on anything!