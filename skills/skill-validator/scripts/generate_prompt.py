#!/usr/bin/env python3
"""
Generate <available_skills> XML for agent system prompts.
Parses skill metadata and outputs formatted XML.
"""

import argparse
import html
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Find the SKILL.md file in a skill directory."""
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def parse_skill_metadata(skill_dir: Path) -> Optional[Dict]:
    """Parse skill metadata from SKILL.md frontmatter."""
    skill_md = find_skill_md(skill_dir)
    if not skill_md:
        return None
    
    content = skill_md.read_text()
    
    if not content.startswith("---"):
        return None
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    
    try:
        metadata = yaml.safe_load(parts[1])
        if not isinstance(metadata, dict):
            return None
        
        if "name" not in metadata or "description" not in metadata:
            return None
        
        return {
            "name": metadata["name"],
            "description": metadata["description"],
            "location": str(skill_md.resolve())
        }
    except yaml.YAMLError:
        return None


def generate_xml(skills: List[Dict]) -> str:
    """Generate <available_skills> XML block."""
    if not skills:
        return "<available_skills>\n</available_skills>"
    
    lines = ["<available_skills>"]
    
    for skill in skills:
        lines.append("<skill>")
        lines.append("<name>")
        lines.append(html.escape(skill["name"]))
        lines.append("</name>")
        lines.append("<description>")
        lines.append(html.escape(skill["description"]))
        lines.append("</description>")
        lines.append("<location>")
        lines.append(skill["location"])
        lines.append("</location>")
        lines.append("</skill>")
    
    lines.append("</available_skills>")
    
    return "\n".join(lines)


def generate_compact_xml(skills: List[Dict]) -> str:
    """Generate compact XML format (single line per skill)."""
    if not skills:
        return "<available_skills></available_skills>"
    
    lines = ["<available_skills>"]
    
    for skill in skills:
        name = html.escape(skill["name"])
        desc = html.escape(skill["description"])
        loc = skill["location"]
        lines.append(f'  <skill name="{name}" location="{loc}">{desc}</skill>')
    
    lines.append("</available_skills>")
    
    return "\n".join(lines)


def generate_json(skills: List[Dict]) -> str:
    """Generate JSON format for skills."""
    import json
    return json.dumps({"available_skills": skills}, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate skill prompt XML")
    parser.add_argument("--skills", nargs="+", required=True,
                        help="Paths to skill directories")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["xml", "compact", "json"],
                        default="xml", help="Output format (default: xml)")
    
    args = parser.parse_args()
    
    skills = []
    errors = []
    
    for skill_path in args.skills:
        path = Path(skill_path)
        
        if not path.exists():
            errors.append(f"Path does not exist: {skill_path}")
            continue
        
        if not path.is_dir():
            errors.append(f"Not a directory: {skill_path}")
            continue
        
        metadata = parse_skill_metadata(path)
        if metadata:
            skills.append(metadata)
        else:
            errors.append(f"Failed to parse skill: {skill_path}")
    
    # Print errors
    if errors:
        print("Errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(file=sys.stderr)
    
    # Generate output
    if args.format == "xml":
        output = generate_xml(skills)
    elif args.format == "compact":
        output = generate_compact_xml(skills)
    else:
        output = generate_json(skills)
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output saved to: {args.output}")
    else:
        print(output)
    
    print(f"\nProcessed {len(skills)} skills successfully", file=sys.stderr)
    
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
