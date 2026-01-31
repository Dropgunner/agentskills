#!/usr/bin/env python3
"""
Validate Agent Skills for compliance with the specification.
Checks frontmatter, naming conventions, and structure.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


# Validation constants
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_SKILL_MD_LINES = 500

ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Find the SKILL.md file in a skill directory."""
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def parse_frontmatter(content: str) -> Tuple[Dict, str, List[str]]:
    """Parse YAML frontmatter from SKILL.md content."""
    errors = []
    
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return {}, "", errors
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("SKILL.md frontmatter not properly closed with ---")
        return {}, "", errors
    
    frontmatter_str = parts[1]
    body = parts[2].strip()
    
    try:
        metadata = yaml.safe_load(frontmatter_str)
        if not isinstance(metadata, dict):
            errors.append("SKILL.md frontmatter must be a YAML mapping")
            return {}, body, errors
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return {}, body, errors
    
    return metadata, body, errors


def validate_name(name: str, skill_dir: Path) -> List[str]:
    """Validate skill name format and directory match."""
    errors = []
    
    if not name or not isinstance(name, str) or not name.strip():
        errors.append("Field 'name' must be a non-empty string")
        return errors
    
    name = unicodedata.normalize("NFKC", name.strip())
    
    if len(name) > MAX_SKILL_NAME_LENGTH:
        errors.append(
            f"Skill name '{name}' exceeds {MAX_SKILL_NAME_LENGTH} character limit "
            f"({len(name)} chars)"
        )
    
    if name != name.lower():
        errors.append(f"Skill name '{name}' must be lowercase")
    
    if name.startswith("-") or name.endswith("-"):
        errors.append("Skill name cannot start or end with a hyphen")
    
    if "--" in name:
        errors.append("Skill name cannot contain consecutive hyphens")
    
    if not all(c.isalnum() or c == "-" for c in name):
        errors.append(
            f"Skill name '{name}' contains invalid characters. "
            "Only letters, digits, and hyphens are allowed."
        )
    
    if skill_dir:
        dir_name = unicodedata.normalize("NFKC", skill_dir.name)
        if dir_name != name:
            errors.append(
                f"Directory name '{skill_dir.name}' must match skill name '{name}'"
            )
    
    return errors


def validate_description(description: str) -> List[str]:
    """Validate description format."""
    errors = []
    
    if not description or not isinstance(description, str) or not description.strip():
        errors.append("Field 'description' must be a non-empty string")
        return errors
    
    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"Description exceeds {MAX_DESCRIPTION_LENGTH} character limit "
            f"({len(description)} chars)"
        )
    
    # Quality warnings (not errors)
    if len(description) < 50:
        errors.append("Warning: Description is very short. Consider adding more detail.")
    
    return errors


def validate_compatibility(compatibility: str) -> List[str]:
    """Validate compatibility format."""
    errors = []
    
    if not isinstance(compatibility, str):
        errors.append("Field 'compatibility' must be a string")
        return errors
    
    if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
        errors.append(
            f"Compatibility exceeds {MAX_COMPATIBILITY_LENGTH} character limit "
            f"({len(compatibility)} chars)"
        )
    
    return errors


def validate_metadata_fields(metadata: dict) -> List[str]:
    """Validate that only allowed fields are present."""
    errors = []
    
    extra_fields = set(metadata.keys()) - ALLOWED_FIELDS
    if extra_fields:
        errors.append(
            f"Unexpected fields in frontmatter: {', '.join(sorted(extra_fields))}. "
            f"Only {sorted(ALLOWED_FIELDS)} are allowed."
        )
    
    return errors


def validate_body(body: str) -> List[str]:
    """Validate SKILL.md body content."""
    errors = []
    
    lines = body.split("\n")
    if len(lines) > MAX_SKILL_MD_LINES:
        errors.append(
            f"Warning: SKILL.md body has {len(lines)} lines. "
            f"Recommended maximum is {MAX_SKILL_MD_LINES} lines."
        )
    
    # Check for headers
    headers = [line for line in lines if line.startswith("#")]
    if not headers:
        errors.append("Warning: SKILL.md has no headers. Consider adding structure.")
    
    return errors


def validate_resources(skill_dir: Path) -> List[str]:
    """Validate bundled resources."""
    errors = []
    
    # Check scripts directory
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py"))
        for script in scripts:
            content = script.read_text()
            if "def main" not in content and "if __name__" not in content:
                errors.append(f"Warning: Script {script.name} may not be executable")
    
    # Check references directory
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        refs = list(refs_dir.glob("*.md"))
        for ref in refs:
            content = ref.read_text()
            word_count = len(content.split())
            if word_count > 10000:
                errors.append(
                    f"Warning: Reference {ref.name} has {word_count} words. "
                    "Consider splitting into smaller files."
                )
    
    return errors


def validate_skill(skill_dir: Path) -> Dict:
    """Validate a skill directory."""
    result = {
        "path": str(skill_dir),
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not skill_dir.exists():
        result["valid"] = False
        result["errors"].append(f"Path does not exist: {skill_dir}")
        return result
    
    if not skill_dir.is_dir():
        result["valid"] = False
        result["errors"].append(f"Not a directory: {skill_dir}")
        return result
    
    skill_md = find_skill_md(skill_dir)
    if skill_md is None:
        result["valid"] = False
        result["errors"].append("Missing required file: SKILL.md")
        return result
    
    # Parse content
    content = skill_md.read_text()
    metadata, body, parse_errors = parse_frontmatter(content)
    
    for error in parse_errors:
        result["valid"] = False
        result["errors"].append(error)
    
    if not metadata:
        return result
    
    # Validate fields
    field_errors = validate_metadata_fields(metadata)
    for error in field_errors:
        result["valid"] = False
        result["errors"].append(error)
    
    # Validate name
    if "name" not in metadata:
        result["valid"] = False
        result["errors"].append("Missing required field in frontmatter: name")
    else:
        name_errors = validate_name(metadata["name"], skill_dir)
        for error in name_errors:
            if error.startswith("Warning"):
                result["warnings"].append(error)
            else:
                result["valid"] = False
                result["errors"].append(error)
    
    # Validate description
    if "description" not in metadata:
        result["valid"] = False
        result["errors"].append("Missing required field in frontmatter: description")
    else:
        desc_errors = validate_description(metadata["description"])
        for error in desc_errors:
            if error.startswith("Warning"):
                result["warnings"].append(error)
            else:
                result["valid"] = False
                result["errors"].append(error)
    
    # Validate optional fields
    if "compatibility" in metadata:
        compat_errors = validate_compatibility(metadata["compatibility"])
        for error in compat_errors:
            result["valid"] = False
            result["errors"].append(error)
    
    # Validate body
    body_errors = validate_body(body)
    for error in body_errors:
        if error.startswith("Warning"):
            result["warnings"].append(error)
        else:
            result["errors"].append(error)
    
    # Validate resources
    resource_errors = validate_resources(skill_dir)
    for error in resource_errors:
        if error.startswith("Warning"):
            result["warnings"].append(error)
        else:
            result["errors"].append(error)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Validate Agent Skills")
    parser.add_argument("--skill", help="Path to skill directory")
    parser.add_argument("--directory", help="Path to directory containing multiple skills")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    if not args.skill and not args.directory:
        parser.error("Either --skill or --directory is required")
    
    results = []
    
    if args.skill:
        skill_path = Path(args.skill)
        result = validate_skill(skill_path)
        results.append(result)
    
    if args.directory:
        dir_path = Path(args.directory)
        for skill_dir in dir_path.iterdir():
            if skill_dir.is_dir() and find_skill_md(skill_dir):
                result = validate_skill(skill_dir)
                results.append(result)
    
    # Apply strict mode
    if args.strict:
        for result in results:
            if result["warnings"]:
                result["valid"] = False
                result["errors"].extend(result["warnings"])
    
    # Print results
    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    
    print(f"\nValidation Results: {valid}/{total} skills valid")
    print("=" * 50)
    
    for result in results:
        status = "✓ VALID" if result["valid"] else "✗ INVALID"
        print(f"\n{status}: {result['path']}")
        
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        
        for warning in result["warnings"]:
            print(f"  {warning}")
    
    # Output to JSON
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit code
    sys.exit(0 if all(r["valid"] for r in results) else 1)


if __name__ == "__main__":
    main()
