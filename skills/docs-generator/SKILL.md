---
name: docs-generator
description: Generate documentation from code, specifications, and project files. Use when creating README files, API documentation, code comments, or technical specifications. Supports multiple output formats including Markdown, HTML, and reStructuredText.
license: MIT
metadata:
  author: Prayer
  version: "1.0"
---

# Documentation Generator

Automated documentation generation from source code and specifications.

## When to Use

- Creating README files for new projects
- Generating API documentation from code
- Documenting smart contracts or blockchain projects
- Creating technical specifications
- Updating existing documentation

## Quick Start

```bash
# Generate README from project structure
python scripts/generate_readme.py --project /path/to/project

# Generate API docs from Python code
python scripts/generate_api_docs.py --source /path/to/src --output docs/

# Generate docs from Solidity contracts
python scripts/generate_contract_docs.py --contracts /path/to/*.sol

# Create documentation site structure
python scripts/init_docs_site.py --project /path/to/project --format mintlify
```

## Documentation Workflow

1. **Analyze project** - Scan source files and structure
2. **Extract metadata** - Parse docstrings, comments, and annotations
3. **Generate content** - Create documentation from templates
4. **Format output** - Apply styling and structure
5. **Validate** - Check for completeness and accuracy

## README Generation

### Standard README Structure

```markdown
# Project Name

Brief description of the project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
npm install project-name
# or
pip install project-name
```

## Quick Start

```javascript
// Example usage code
```

## Documentation

Link to full documentation.

## Contributing

Guidelines for contributors.

## License

License information.
```

### README Templates

Use templates based on project type:

| Project Type | Template |
|--------------|----------|
| npm package | `templates/readme-npm.md` |
| Python package | `templates/readme-python.md` |
| Smart contract | `templates/readme-solidity.md` |
| General | `templates/readme-general.md` |

## API Documentation

### Python Docstring Extraction

```python
# Supported docstring formats:
# - Google style
# - NumPy style
# - Sphinx style

def example_function(param1: str, param2: int) -> bool:
    """Short description of function.
    
    Longer description with more details about
    what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> example_function("hello", 42)
        True
    """
    pass
```

### TypeScript/JavaScript JSDoc

```typescript
/**
 * Short description of function.
 * 
 * @param {string} param1 - Description of param1
 * @param {number} param2 - Description of param2
 * @returns {boolean} Description of return value
 * @throws {Error} When param2 is negative
 * @example
 * exampleFunction("hello", 42);
 */
function exampleFunction(param1: string, param2: number): boolean {
    // ...
}
```

### Solidity NatSpec

```solidity
/// @title Token Contract
/// @author Developer Name
/// @notice This contract implements an ERC-20 token
/// @dev Inherits from OpenZeppelin ERC20
contract Token is ERC20 {
    /// @notice Transfer tokens to recipient
    /// @param to The recipient address
    /// @param amount The amount to transfer
    /// @return success Whether the transfer succeeded
    function transfer(address to, uint256 amount) 
        public 
        returns (bool success) 
    {
        // ...
    }
}
```

## Documentation Formats

### Markdown (Default)
- GitHub-flavored Markdown
- Compatible with most platforms
- Easy to read and write

### Mintlify
- Modern documentation platform
- Interactive components
- API playground support

### Sphinx/reStructuredText
- Python ecosystem standard
- Rich cross-referencing
- PDF generation support

### MkDocs
- Simple and fast
- Material theme available
- Plugin ecosystem

## Output Templates

### API Reference Template

```markdown
# API Reference

## Module: `module_name`

### Functions

#### `function_name(param1, param2)`

Description of the function.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| param1 | `str` | Description |
| param2 | `int` | Description |

**Returns:**

| Type | Description |
|------|-------------|
| `bool` | Description |

**Example:**

```python
result = function_name("hello", 42)
```
```

## Integration

### With GitHub Actions

```yaml
name: Generate Docs
on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate documentation
        run: python scripts/generate_api_docs.py --source src/ --output docs/
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### With Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: update-readme
        name: Update README
        entry: python scripts/generate_readme.py --project .
        language: python
        pass_filenames: false
```

## Best Practices

### Documentation Quality

- Write for your audience (developers, users, or both)
- Include working code examples
- Keep documentation up to date with code
- Use consistent formatting and terminology
- Add diagrams for complex concepts

### Code Comments

- Document "why" not "what"
- Keep comments concise
- Update comments when code changes
- Use TODO/FIXME for pending work

### API Documentation

- Document all public interfaces
- Include parameter types and descriptions
- Provide usage examples
- Document error conditions
