#!/usr/bin/env python3
"""
Generate README.md files from project structure and metadata.
Analyzes project files to create comprehensive documentation.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def detect_project_type(project_dir: Path) -> str:
    """Detect the type of project based on files present."""
    indicators = {
        "npm": ["package.json"],
        "python": ["setup.py", "pyproject.toml", "requirements.txt"],
        "solidity": ["hardhat.config.js", "truffle-config.js", "foundry.toml"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
    }
    
    for project_type, files in indicators.items():
        for file in files:
            if (project_dir / file).exists():
                return project_type
    
    return "general"


def extract_package_info(project_dir: Path, project_type: str) -> Dict:
    """Extract package information from project files."""
    info = {
        "name": project_dir.name,
        "description": "",
        "version": "",
        "author": "",
        "license": "",
        "keywords": [],
        "dependencies": []
    }
    
    if project_type == "npm":
        package_json = project_dir / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                info["name"] = data.get("name", info["name"])
                info["description"] = data.get("description", "")
                info["version"] = data.get("version", "")
                info["author"] = data.get("author", "")
                info["license"] = data.get("license", "")
                info["keywords"] = data.get("keywords", [])
                info["dependencies"] = list(data.get("dependencies", {}).keys())
            except json.JSONDecodeError:
                pass
    
    elif project_type == "python":
        pyproject = project_dir / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            # Simple TOML parsing for common fields
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if name_match:
                info["name"] = name_match.group(1)
            desc_match = re.search(r'description\s*=\s*"([^"]+)"', content)
            if desc_match:
                info["description"] = desc_match.group(1)
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                info["version"] = version_match.group(1)
    
    return info


def find_source_files(project_dir: Path) -> Dict[str, List[Path]]:
    """Find source files organized by type."""
    extensions = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "solidity": [".sol"],
        "markdown": [".md"],
    }
    
    files = {}
    for file_type, exts in extensions.items():
        files[file_type] = []
        for ext in exts:
            files[file_type].extend(project_dir.rglob(f"*{ext}"))
    
    return files


def extract_exports(project_dir: Path, project_type: str) -> List[str]:
    """Extract main exports/functions from the project."""
    exports = []
    
    if project_type == "python":
        init_file = project_dir / "__init__.py"
        if not init_file.exists():
            # Try to find package directory
            for subdir in project_dir.iterdir():
                if subdir.is_dir() and (subdir / "__init__.py").exists():
                    init_file = subdir / "__init__.py"
                    break
        
        if init_file.exists():
            content = init_file.read_text()
            # Find __all__ definition
            all_match = re.search(r'__all__\s*=\s*\[([^\]]+)\]', content)
            if all_match:
                exports = re.findall(r'"([^"]+)"|\'([^\']+)\'', all_match.group(1))
                exports = [e[0] or e[1] for e in exports]
    
    return exports[:10]  # Limit to 10 exports


def generate_installation_section(project_type: str, info: Dict) -> str:
    """Generate installation instructions based on project type."""
    name = info.get("name", "package-name")
    
    templates = {
        "npm": f"""## Installation

```bash
npm install {name}
# or
yarn add {name}
# or
pnpm add {name}
```""",
        "python": f"""## Installation

```bash
pip install {name}
# or
poetry add {name}
```""",
        "solidity": """## Installation

```bash
# Using Hardhat
npm install --save-dev hardhat
npx hardhat compile

# Using Foundry
forge build
```""",
        "general": """## Installation

```bash
git clone <repository-url>
cd <project-name>
# Follow setup instructions
```"""
    }
    
    return templates.get(project_type, templates["general"])


def generate_usage_section(project_type: str, info: Dict, exports: List[str]) -> str:
    """Generate usage examples based on project type."""
    name = info.get("name", "package")
    
    if project_type == "npm":
        if exports:
            import_list = ", ".join(exports[:3])
            return f"""## Usage

```javascript
import {{ {import_list} }} from '{name}';

// Example usage
```"""
        return f"""## Usage

```javascript
import {name.replace('-', '')} from '{name}';

// Example usage
```"""
    
    elif project_type == "python":
        if exports:
            import_list = ", ".join(exports[:3])
            return f"""## Usage

```python
from {name.replace('-', '_')} import {import_list}

# Example usage
```"""
        return f"""## Usage

```python
import {name.replace('-', '_')}

# Example usage
```"""
    
    elif project_type == "solidity":
        return """## Usage

```solidity
// Import the contract
import "./Contract.sol";

// Deploy and interact
```"""
    
    return """## Usage

See documentation for usage examples."""


def generate_readme(project_dir: Path) -> str:
    """Generate complete README content."""
    project_type = detect_project_type(project_dir)
    info = extract_package_info(project_dir, project_type)
    source_files = find_source_files(project_dir)
    exports = extract_exports(project_dir, project_type)
    
    # Build README sections
    sections = []
    
    # Title and description
    title = info["name"].replace("-", " ").title()
    sections.append(f"# {title}")
    
    if info["description"]:
        sections.append(f"\n{info['description']}")
    else:
        sections.append(f"\n[Add project description here]")
    
    # Badges (if applicable)
    if info["version"]:
        sections.append(f"\n![Version](https://img.shields.io/badge/version-{info['version']}-blue)")
    if info["license"]:
        sections.append(f"![License](https://img.shields.io/badge/license-{info['license']}-green)")
    
    # Features section
    sections.append("""
## Features

- Feature 1: [Describe key feature]
- Feature 2: [Describe key feature]
- Feature 3: [Describe key feature]
""")
    
    # Installation
    sections.append(generate_installation_section(project_type, info))
    
    # Usage
    sections.append(generate_usage_section(project_type, info, exports))
    
    # API/Exports section if applicable
    if exports:
        sections.append("\n## API\n")
        for export in exports:
            sections.append(f"### `{export}`\n")
            sections.append("[Add description]\n")
    
    # Project structure
    sections.append("""
## Project Structure

```
├── src/           # Source files
├── tests/         # Test files
├── docs/          # Documentation
└── README.md      # This file
```
""")
    
    # Contributing
    sections.append("""## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
""")
    
    # License
    license_text = info["license"] if info["license"] else "MIT"
    sections.append(f"""## License

This project is licensed under the {license_text} License - see the [LICENSE](LICENSE) file for details.
""")
    
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Generate README.md from project")
    parser.add_argument("--project", required=True, help="Path to project directory")
    parser.add_argument("--output", help="Output file path (default: PROJECT/README.md)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout instead of writing")
    
    args = parser.parse_args()
    
    project_path = Path(args.project)
    
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"Error: Not a directory: {project_path}")
        sys.exit(1)
    
    # Generate README
    readme_content = generate_readme(project_path)
    
    # Output
    if args.dry_run:
        print(readme_content)
    else:
        output_path = Path(args.output) if args.output else project_path / "README.md"
        output_path.write_text(readme_content)
        print(f"README generated: {output_path}")


if __name__ == "__main__":
    main()
