#!/usr/bin/env python3
"""
Generate API documentation from Python source files.
Extracts docstrings and type hints to create Markdown documentation.
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    signature: str
    docstring: str
    args: List[Dict]
    returns: Optional[str]
    raises: List[str]
    is_async: bool
    decorators: List[str]


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    docstring: str
    bases: List[str]
    methods: List[FunctionDoc]
    attributes: List[Dict]


@dataclass
class ModuleDoc:
    """Documentation for a module."""
    name: str
    path: str
    docstring: str
    functions: List[FunctionDoc]
    classes: List[ClassDoc]
    imports: List[str]


def parse_google_docstring(docstring: str) -> Dict:
    """Parse Google-style docstring into structured format."""
    result = {
        "description": "",
        "args": [],
        "returns": None,
        "raises": [],
        "examples": []
    }
    
    if not docstring:
        return result
    
    lines = docstring.strip().split("\n")
    current_section = "description"
    current_content = []
    
    section_patterns = {
        "args": r"^\s*Args?:\s*$",
        "returns": r"^\s*Returns?:\s*$",
        "raises": r"^\s*Raises?:\s*$",
        "examples": r"^\s*Examples?:\s*$",
    }
    
    for line in lines:
        # Check for section headers
        matched_section = None
        for section, pattern in section_patterns.items():
            if re.match(pattern, line, re.I):
                matched_section = section
                break
        
        if matched_section:
            # Save previous section
            if current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = matched_section
            current_content = []
        else:
            current_content.append(line)
    
    # Handle last section
    if current_section == "description":
        result["description"] = "\n".join(current_content).strip()
    elif current_section == "args":
        # Parse argument lines
        arg_text = "\n".join(current_content)
        arg_pattern = r"(\w+)(?:\s*\(([^)]+)\))?:\s*(.+?)(?=\n\s*\w+(?:\s*\([^)]+\))?:|$)"
        for match in re.finditer(arg_pattern, arg_text, re.DOTALL):
            result["args"].append({
                "name": match.group(1),
                "type": match.group(2) or "",
                "description": match.group(3).strip()
            })
    elif current_section == "returns":
        result["returns"] = "\n".join(current_content).strip()
    elif current_section == "raises":
        result["raises"] = [line.strip() for line in current_content if line.strip()]
    elif current_section == "examples":
        result["examples"] = current_content
    
    return result


def extract_function_signature(node: ast.FunctionDef) -> str:
    """Extract function signature from AST node."""
    args = []
    
    # Handle positional args
    for i, arg in enumerate(node.args.args):
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        
        # Check for default value
        defaults_offset = len(node.args.args) - len(node.args.defaults)
        if i >= defaults_offset:
            default = node.args.defaults[i - defaults_offset]
            arg_str += f" = {ast.unparse(default)}"
        
        args.append(arg_str)
    
    # Handle *args
    if node.args.vararg:
        vararg = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            vararg += f": {ast.unparse(node.args.vararg.annotation)}"
        args.append(vararg)
    
    # Handle **kwargs
    if node.args.kwarg:
        kwarg = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            kwarg += f": {ast.unparse(node.args.kwarg.annotation)}"
        args.append(kwarg)
    
    # Return type
    return_type = ""
    if node.returns:
        return_type = f" -> {ast.unparse(node.returns)}"
    
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    return f"{prefix}def {node.name}({', '.join(args)}){return_type}"


def extract_function_doc(node: ast.FunctionDef) -> FunctionDoc:
    """Extract documentation from a function node."""
    docstring = ast.get_docstring(node) or ""
    parsed = parse_google_docstring(docstring)
    
    decorators = [ast.unparse(d) for d in node.decorator_list]
    
    return FunctionDoc(
        name=node.name,
        signature=extract_function_signature(node),
        docstring=parsed["description"],
        args=parsed["args"],
        returns=parsed["returns"],
        raises=parsed["raises"],
        is_async=isinstance(node, ast.AsyncFunctionDef),
        decorators=decorators
    )


def extract_class_doc(node: ast.ClassDef) -> ClassDoc:
    """Extract documentation from a class node."""
    docstring = ast.get_docstring(node) or ""
    bases = [ast.unparse(base) for base in node.bases]
    
    methods = []
    attributes = []
    
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(extract_function_doc(item))
        elif isinstance(item, ast.AnnAssign):
            attr = {
                "name": ast.unparse(item.target),
                "type": ast.unparse(item.annotation) if item.annotation else "",
                "value": ast.unparse(item.value) if item.value else ""
            }
            attributes.append(attr)
    
    return ClassDoc(
        name=node.name,
        docstring=docstring,
        bases=bases,
        methods=methods,
        attributes=attributes
    )


def parse_module(file_path: Path) -> ModuleDoc:
    """Parse a Python module and extract documentation."""
    content = file_path.read_text()
    tree = ast.parse(content)
    
    module_docstring = ast.get_docstring(tree) or ""
    
    functions = []
    classes = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.append(extract_function_doc(node))
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                classes.append(extract_class_doc(node))
    
    return ModuleDoc(
        name=file_path.stem,
        path=str(file_path),
        docstring=module_docstring,
        functions=functions,
        classes=classes,
        imports=list(set(imports))
    )


def generate_function_markdown(func: FunctionDoc) -> str:
    """Generate Markdown documentation for a function."""
    lines = []
    
    # Function header
    lines.append(f"### `{func.name}`")
    lines.append("")
    
    # Decorators
    if func.decorators:
        for dec in func.decorators:
            lines.append(f"*@{dec}*")
        lines.append("")
    
    # Signature
    lines.append("```python")
    lines.append(func.signature)
    lines.append("```")
    lines.append("")
    
    # Description
    if func.docstring:
        lines.append(func.docstring)
        lines.append("")
    
    # Parameters
    if func.args:
        lines.append("**Parameters:**")
        lines.append("")
        lines.append("| Name | Type | Description |")
        lines.append("|------|------|-------------|")
        for arg in func.args:
            lines.append(f"| `{arg['name']}` | `{arg['type']}` | {arg['description']} |")
        lines.append("")
    
    # Returns
    if func.returns:
        lines.append("**Returns:**")
        lines.append("")
        lines.append(func.returns)
        lines.append("")
    
    # Raises
    if func.raises:
        lines.append("**Raises:**")
        lines.append("")
        for exc in func.raises:
            lines.append(f"- {exc}")
        lines.append("")
    
    return "\n".join(lines)


def generate_class_markdown(cls: ClassDoc) -> str:
    """Generate Markdown documentation for a class."""
    lines = []
    
    # Class header
    bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
    lines.append(f"## Class `{cls.name}`{bases_str}")
    lines.append("")
    
    # Description
    if cls.docstring:
        lines.append(cls.docstring)
        lines.append("")
    
    # Attributes
    if cls.attributes:
        lines.append("### Attributes")
        lines.append("")
        lines.append("| Name | Type | Default |")
        lines.append("|------|------|---------|")
        for attr in cls.attributes:
            lines.append(f"| `{attr['name']}` | `{attr['type']}` | `{attr['value']}` |")
        lines.append("")
    
    # Methods
    public_methods = [m for m in cls.methods if not m.name.startswith("_")]
    if public_methods:
        lines.append("### Methods")
        lines.append("")
        for method in public_methods:
            lines.append(generate_function_markdown(method))
    
    return "\n".join(lines)


def generate_module_markdown(module: ModuleDoc) -> str:
    """Generate Markdown documentation for a module."""
    lines = []
    
    # Module header
    lines.append(f"# Module: `{module.name}`")
    lines.append("")
    
    # Description
    if module.docstring:
        lines.append(module.docstring)
        lines.append("")
    
    # Functions
    if module.functions:
        lines.append("## Functions")
        lines.append("")
        for func in module.functions:
            lines.append(generate_function_markdown(func))
    
    # Classes
    for cls in module.classes:
        lines.append(generate_class_markdown(cls))
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate API documentation from Python source")
    parser.add_argument("--source", required=True, help="Path to source directory or file")
    parser.add_argument("--output", required=True, help="Output directory for documentation")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown")
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    
    if not source_path.exists():
        print(f"Error: Source path does not exist: {source_path}")
        sys.exit(1)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find Python files
    if source_path.is_file():
        py_files = [source_path]
    else:
        py_files = list(source_path.rglob("*.py"))
    
    print(f"Processing {len(py_files)} Python files...")
    
    # Generate documentation
    index_content = ["# API Reference", ""]
    
    for py_file in py_files:
        if py_file.name.startswith("_"):
            continue
        
        try:
            module = parse_module(py_file)
            
            if not module.functions and not module.classes:
                continue
            
            # Generate module docs
            doc_content = generate_module_markdown(module)
            
            # Write to file
            relative_path = py_file.relative_to(source_path) if source_path.is_dir() else py_file.name
            doc_file = output_path / f"{relative_path.stem}.md"
            doc_file.write_text(doc_content)
            
            # Add to index
            index_content.append(f"- [{module.name}]({doc_file.name})")
            
            print(f"  Generated: {doc_file}")
            
        except Exception as e:
            print(f"  Error processing {py_file}: {e}")
    
    # Write index
    index_file = output_path / "index.md"
    index_file.write_text("\n".join(index_content))
    print(f"\nIndex generated: {index_file}")


if __name__ == "__main__":
    main()
