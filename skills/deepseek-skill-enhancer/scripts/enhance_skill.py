#!/usr/bin/env python3
"""
Enhance an existing skill with DeepSeek integration for cost-optimized LLM operations.

Usage:
    python scripts/enhance_skill.py <skill_path> [--dry-run]

Example:
    python scripts/enhance_skill.py /home/ubuntu/skills/my-skill
    python scripts/enhance_skill.py /home/ubuntu/skills/my-skill --dry-run
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

DEEPSEEK_ROUTER_PATH = Path("/home/ubuntu/skills/deepseek-router/scripts")
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def check_deepseek_router():
    """Verify DeepSeek Router skill is available."""
    required_files = ["deepseek_client.py", "task_router.py", "cache_manager.py"]
    for f in required_files:
        if not (DEEPSEEK_ROUTER_PATH / f).exists():
            print(f"ERROR: DeepSeek Router not found at {DEEPSEEK_ROUTER_PATH}")
            print("Please ensure the deepseek-router skill is installed.")
            return False
    return True


def analyze_skill(skill_path: Path) -> dict:
    """Analyze the target skill structure."""
    analysis = {
        "path": skill_path,
        "has_scripts": (skill_path / "scripts").exists(),
        "has_references": (skill_path / "references").exists(),
        "has_templates": (skill_path / "templates").exists(),
        "skill_md_exists": (skill_path / "SKILL.md").exists(),
        "existing_scripts": [],
        "content_types": [],
    }
    
    if analysis["has_scripts"]:
        analysis["existing_scripts"] = list((skill_path / "scripts").glob("*.py"))
    
    # Detect content types from SKILL.md
    if analysis["skill_md_exists"]:
        content = (skill_path / "SKILL.md").read_text().lower()
        if any(kw in content for kw in ["tweet", "social", "discord", "telegram"]):
            analysis["content_types"].append("social")
        if any(kw in content for kw in ["blog", "article", "post"]):
            analysis["content_types"].append("blog")
        if any(kw in content for kw in ["investor", "pitch", "deck"]):
            analysis["content_types"].append("investor")
        if any(kw in content for kw in ["technical", "documentation", "api"]):
            analysis["content_types"].append("technical")
        if any(kw in content for kw in ["community", "welcome", "onboard"]):
            analysis["content_types"].append("community")
    
    return analysis


def create_generator_script(skill_path: Path, skill_name: str, content_types: list) -> str:
    """Generate a customized content generator script."""
    template_path = TEMPLATE_DIR / "generator_template.py"
    
    if template_path.exists():
        template = template_path.read_text()
    else:
        # Fallback to embedded template
        template = '''#!/usr/bin/env python3
"""
{skill_name} Content Generator with DeepSeek Integration
Cost-optimized LLM content generation.

Usage:
    python scripts/{script_name}_generator.py "Your prompt here"
    python scripts/{script_name}_generator.py --type TYPE "Your prompt here"
"""

import os
import sys
from pathlib import Path

# Add DeepSeek router to path
DEEPSEEK_PATH = Path("/home/ubuntu/skills/deepseek-router/scripts")
sys.path.insert(0, str(DEEPSEEK_PATH))

from task_router import TaskRouter

SKILL_ROOT = Path(__file__).parent.parent


class {class_name}Generator:
    """Cost-optimized content generator."""
    
    def __init__(self):
        self.router = TaskRouter()
    
    def generate(self, prompt: str, content_type: str = "general") -> dict:
        """Generate content using DeepSeek routing."""
        system = self._get_system_prompt(content_type)
        result = self.router.route(
            prompt=prompt,
            system=system,
            force_deepseek=True
        )
        result["content_type"] = content_type
        return result
    
    def _get_system_prompt(self, content_type: str) -> str:
        """Get system prompt for content type."""
        prompts = {
            "general": "You are a helpful assistant.",
            {content_type_prompts}
        }
        return prompts.get(content_type, prompts["general"])


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Content generation prompt")
    parser.add_argument("--type", "-t", default="general", help="Content type")
    args = parser.parse_args()
    
    generator = {class_name}Generator()
    result = generator.generate(args.prompt, args.type)
    
    print(f"Content Type: {{result['content_type'].upper()}}")
    print(f"Cost: ${{result['cost']:.6f}}")
    print("=" * 60)
    print(result["content"])


if __name__ == "__main__":
    main()
'''
    
    # Customize template
    script_name = skill_name.lower().replace("-", "_").replace(" ", "_")
    class_name = "".join(word.capitalize() for word in skill_name.replace("-", " ").split())
    
    # Build content type prompts
    type_prompts = []
    for ct in content_types:
        type_prompts.append(f'            "{ct}": "You are generating {ct} content.",')
    content_type_prompts = "\n".join(type_prompts) if type_prompts else '            # Add content-specific prompts here'
    
    script = template.format(
        skill_name=skill_name,
        script_name=script_name,
        class_name=class_name,
        content_type_prompts=content_type_prompts
    )
    
    return script


def enhance_skill(skill_path: Path, dry_run: bool = False):
    """Enhance a skill with DeepSeek integration."""
    skill_name = skill_path.name
    
    print(f"Enhancing skill: {skill_name}")
    print(f"Location: {skill_path}")
    print()
    
    # Check prerequisites
    if not check_deepseek_router():
        return False
    
    if not skill_path.exists():
        print(f"ERROR: Skill path does not exist: {skill_path}")
        return False
    
    # Analyze skill
    analysis = analyze_skill(skill_path)
    print("Skill Analysis:")
    print(f"  - Has scripts/: {analysis['has_scripts']}")
    print(f"  - Has references/: {analysis['has_references']}")
    print(f"  - Has templates/: {analysis['has_templates']}")
    print(f"  - Detected content types: {analysis['content_types'] or ['general']}")
    print()
    
    if dry_run:
        print("[DRY RUN] Would perform the following actions:")
        print(f"  1. Create scripts/ directory (if needed)")
        print(f"  2. Add {skill_name}_generator.py")
        print(f"  3. Add references/routing_config.md")
        print(f"  4. Update SKILL.md with DeepSeek integration section")
        return True
    
    # Create scripts directory if needed
    scripts_dir = skill_path / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # Create generator script
    generator_script = create_generator_script(
        skill_path, 
        skill_name, 
        analysis["content_types"] or ["general"]
    )
    script_name = skill_name.lower().replace("-", "_").replace(" ", "_")
    generator_path = scripts_dir / f"{script_name}_generator.py"
    generator_path.write_text(generator_script)
    print(f"Created: {generator_path}")
    
    # Create routing config reference
    refs_dir = skill_path / "references"
    refs_dir.mkdir(exist_ok=True)
    
    routing_config = f"""# DeepSeek Routing Configuration for {skill_name}

## Task Routing Settings

| Content Type | Temperature | Max Tokens | Routing |
|--------------|-------------|------------|---------|
| general | 0.5 | 1500 | DeepSeek |
{chr(10).join(f'| {ct} | 0.5 | 1500 | DeepSeek |' for ct in analysis['content_types'])}

## Cost Optimization

- **Semantic caching**: Enabled at `/home/ubuntu/.deepseek_cache/`
- **Estimated savings**: 90-96% vs premium models

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `DEEPSEEK_API_KEY` | Primary API key |
| `manus` | Alternative API key |
| `SONAR_API_KEY` | Fallback (Perplexity) |
"""
    
    routing_path = refs_dir / "routing_config.md"
    routing_path.write_text(routing_config)
    print(f"Created: {routing_path}")
    
    # Update SKILL.md
    skill_md_path = skill_path / "SKILL.md"
    if skill_md_path.exists():
        content = skill_md_path.read_text()
        
        # Add DeepSeek integration section if not present
        if "DeepSeek" not in content:
            integration_section = f"""

## DeepSeek Integration

This skill is enhanced with DeepSeek Router for cost-optimized LLM operations.

### Quick Start

```bash
python scripts/{script_name}_generator.py "Your prompt here"
```

### Cost Savings

| Operation | Savings vs Premium |
|-----------|-------------------|
| Content generation | 90-96% |

For routing configuration, see `references/routing_config.md`.
"""
            content += integration_section
            skill_md_path.write_text(content)
            print(f"Updated: {skill_md_path}")
    
    print()
    print(f"Successfully enhanced {skill_name} with DeepSeek integration!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Enhance a skill with DeepSeek integration"
    )
    parser.add_argument("skill_path", help="Path to the skill to enhance")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    skill_path = Path(args.skill_path).resolve()
    
    success = enhance_skill(skill_path, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
