#!/usr/bin/env python3
"""
Check skill quality and generate a quality score.
Evaluates description, structure, examples, and documentation.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Find the SKILL.md file in a skill directory."""
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def parse_skill(skill_dir: Path) -> Tuple[Dict, str, List[str]]:
    """Parse skill metadata and body."""
    errors = []
    skill_md = find_skill_md(skill_dir)
    
    if not skill_md:
        errors.append("SKILL.md not found")
        return {}, "", errors
    
    content = skill_md.read_text()
    
    if not content.startswith("---"):
        errors.append("Missing frontmatter")
        return {}, content, errors
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter")
        return {}, content, errors
    
    try:
        metadata = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return metadata or {}, body, errors
    except yaml.YAMLError as e:
        errors.append(f"YAML error: {e}")
        return {}, parts[2] if len(parts) > 2 else "", errors


def score_description(description: str) -> Tuple[int, List[str]]:
    """Score description quality (0-20 points)."""
    score = 0
    feedback = []
    
    if not description:
        feedback.append("Missing description")
        return 0, feedback
    
    # Length check (5 points)
    length = len(description)
    if length >= 100:
        score += 5
    elif length >= 50:
        score += 3
        feedback.append("Description could be more detailed")
    else:
        score += 1
        feedback.append("Description is too short")
    
    # Contains "when to use" trigger (5 points)
    trigger_patterns = [
        r"use when",
        r"use for",
        r"when.*(?:need|want|working)",
        r"for (?:creating|editing|processing|analyzing)"
    ]
    has_trigger = any(re.search(p, description, re.I) for p in trigger_patterns)
    if has_trigger:
        score += 5
    else:
        feedback.append("Description should include when to use the skill")
    
    # Contains action keywords (5 points)
    action_words = ["create", "edit", "process", "analyze", "generate", "validate",
                    "extract", "convert", "manage", "build", "deploy"]
    action_count = sum(1 for word in action_words if word in description.lower())
    if action_count >= 2:
        score += 5
    elif action_count >= 1:
        score += 3
    else:
        feedback.append("Description should include action keywords")
    
    # Clarity - no TODO or placeholder (5 points)
    if "TODO" not in description and "[" not in description:
        score += 5
    else:
        feedback.append("Description contains placeholder text")
    
    return score, feedback


def score_structure(body: str) -> Tuple[int, List[str]]:
    """Score body structure (0-25 points)."""
    score = 0
    feedback = []
    
    lines = body.split("\n")
    
    # Has headers (10 points)
    headers = [l for l in lines if l.startswith("#")]
    if len(headers) >= 5:
        score += 10
    elif len(headers) >= 3:
        score += 7
    elif len(headers) >= 1:
        score += 4
    else:
        feedback.append("Add section headers for better organization")
    
    # Has multiple sections (5 points)
    h2_headers = [l for l in lines if l.startswith("## ")]
    if len(h2_headers) >= 4:
        score += 5
    elif len(h2_headers) >= 2:
        score += 3
    else:
        feedback.append("Add more sections (## headers)")
    
    # Reasonable length (5 points)
    if 100 <= len(lines) <= 500:
        score += 5
    elif 50 <= len(lines) <= 600:
        score += 3
    elif len(lines) < 50:
        feedback.append("Content is too brief")
    else:
        feedback.append("Content exceeds recommended length")
    
    # Has lists or tables (5 points)
    has_lists = any(l.strip().startswith(("-", "*", "1.")) for l in lines)
    has_tables = "|" in body and "---" in body
    if has_lists and has_tables:
        score += 5
    elif has_lists or has_tables:
        score += 3
    else:
        feedback.append("Add lists or tables for better readability")
    
    return score, feedback


def score_examples(body: str) -> Tuple[int, List[str]]:
    """Score examples and code samples (0-20 points)."""
    score = 0
    feedback = []
    
    # Count code blocks
    code_blocks = re.findall(r"```[\s\S]*?```", body)
    
    if len(code_blocks) >= 5:
        score += 10
    elif len(code_blocks) >= 3:
        score += 7
    elif len(code_blocks) >= 1:
        score += 4
    else:
        feedback.append("Add code examples")
    
    # Has bash/command examples (5 points)
    bash_blocks = re.findall(r"```(?:bash|sh|shell)[\s\S]*?```", body)
    if bash_blocks:
        score += 5
    else:
        feedback.append("Add command-line usage examples")
    
    # Has realistic examples (5 points)
    example_patterns = [
        r"example",
        r"for instance",
        r"such as",
        r"e\.g\.",
        r"sample"
    ]
    has_examples = any(re.search(p, body, re.I) for p in example_patterns)
    if has_examples:
        score += 5
    else:
        feedback.append("Add concrete usage examples")
    
    return score, feedback


def score_resources(skill_dir: Path) -> Tuple[int, List[str]]:
    """Score bundled resources (0-15 points)."""
    score = 0
    feedback = []
    
    # Check scripts
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
        if len(scripts) >= 3:
            score += 5
        elif len(scripts) >= 1:
            score += 3
        
        # Check for docstrings
        for script in scripts[:3]:
            content = script.read_text()
            if '"""' in content or "'''" in content:
                score += 1
                break
    else:
        feedback.append("Consider adding scripts for automation")
    
    # Check references
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        refs = list(refs_dir.glob("*.md"))
        if len(refs) >= 2:
            score += 5
        elif len(refs) >= 1:
            score += 3
    else:
        feedback.append("Consider adding reference documentation")
    
    # Check templates
    templates_dir = skill_dir / "templates"
    if templates_dir.exists():
        templates = list(templates_dir.iterdir())
        if templates:
            score += 3
    
    # No example files remaining (2 points)
    example_files = list(skill_dir.rglob("example*"))
    if not example_files:
        score += 2
    else:
        feedback.append("Remove unused example files")
    
    return min(15, score), feedback


def score_documentation(body: str, skill_dir: Path) -> Tuple[int, List[str]]:
    """Score documentation quality (0-20 points)."""
    score = 0
    feedback = []
    
    # Has "When to Use" section (5 points)
    if re.search(r"##.*when.*use|##.*usage", body, re.I):
        score += 5
    else:
        feedback.append("Add a 'When to Use' section")
    
    # Has workflow or steps (5 points)
    if re.search(r"##.*workflow|##.*steps|1\.\s+\*\*", body, re.I):
        score += 5
    else:
        feedback.append("Add workflow or step-by-step instructions")
    
    # References bundled resources (5 points)
    if "scripts/" in body or "references/" in body or "templates/" in body:
        score += 5
    elif (skill_dir / "scripts").exists() or (skill_dir / "references").exists():
        feedback.append("Reference bundled resources in documentation")
    
    # No TODO/placeholder text (5 points)
    if "TODO" not in body and "[TODO" not in body:
        score += 5
    else:
        feedback.append("Remove TODO placeholders")
    
    return score, feedback


def calculate_quality_score(skill_dir: Path) -> Dict:
    """Calculate overall quality score for a skill."""
    result = {
        "path": str(skill_dir),
        "scores": {},
        "feedback": [],
        "total_score": 0,
        "max_score": 100,
        "grade": "F"
    }
    
    metadata, body, parse_errors = parse_skill(skill_dir)
    
    if parse_errors:
        result["feedback"].extend(parse_errors)
        return result
    
    # Score each category
    desc_score, desc_feedback = score_description(metadata.get("description", ""))
    result["scores"]["description"] = {"score": desc_score, "max": 20}
    result["feedback"].extend(desc_feedback)
    
    struct_score, struct_feedback = score_structure(body)
    result["scores"]["structure"] = {"score": struct_score, "max": 25}
    result["feedback"].extend(struct_feedback)
    
    example_score, example_feedback = score_examples(body)
    result["scores"]["examples"] = {"score": example_score, "max": 20}
    result["feedback"].extend(example_feedback)
    
    resource_score, resource_feedback = score_resources(skill_dir)
    result["scores"]["resources"] = {"score": resource_score, "max": 15}
    result["feedback"].extend(resource_feedback)
    
    doc_score, doc_feedback = score_documentation(body, skill_dir)
    result["scores"]["documentation"] = {"score": doc_score, "max": 20}
    result["feedback"].extend(doc_feedback)
    
    # Calculate total
    total = sum(s["score"] for s in result["scores"].values())
    result["total_score"] = total
    
    # Assign grade
    if total >= 90:
        result["grade"] = "A"
    elif total >= 80:
        result["grade"] = "B"
    elif total >= 70:
        result["grade"] = "C"
    elif total >= 60:
        result["grade"] = "D"
    else:
        result["grade"] = "F"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Check skill quality")
    parser.add_argument("--skill", required=True, help="Path to skill directory")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    skill_path = Path(args.skill)
    
    if not skill_path.exists():
        print(f"Error: Path does not exist: {skill_path}")
        sys.exit(1)
    
    result = calculate_quality_score(skill_path)
    
    # Print report
    print(f"\nQuality Report: {result['path']}")
    print("=" * 50)
    print(f"\nOverall Score: {result['total_score']}/{result['max_score']} (Grade: {result['grade']})")
    print("\nCategory Scores:")
    
    for category, scores in result["scores"].items():
        bar_length = int(scores["score"] / scores["max"] * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {category.capitalize():15} [{bar}] {scores['score']}/{scores['max']}")
    
    if result["feedback"]:
        print("\nImprovement Suggestions:")
        for item in result["feedback"]:
            print(f"  • {item}")
    
    # Output to JSON
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if result["grade"] in ["A", "B", "C"] else 1)


if __name__ == "__main__":
    main()
