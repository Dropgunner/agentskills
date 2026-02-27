#!/usr/bin/env python3
"""
{skill_name} Content Generator with DeepSeek Integration
Cost-optimized LLM content generation.

Usage:
    python scripts/{script_name}_generator.py "Your prompt here"
    python scripts/{script_name}_generator.py --type TYPE "Your prompt here"
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

# Add DeepSeek router to path
DEEPSEEK_PATH = Path("/home/ubuntu/skills/deepseek-router/scripts")
sys.path.insert(0, str(DEEPSEEK_PATH))

from task_router import TaskRouter

SKILL_ROOT = Path(__file__).parent.parent


class ContentType(Enum):
    GENERAL = "general"
    # Add more content types as needed
    {content_type_enums}


# System prompts for each content type
SYSTEM_PROMPTS = {{
    ContentType.GENERAL: "You are a helpful assistant.",
    {content_type_prompts}
}}


class {class_name}Generator:
    """Cost-optimized content generator for {skill_name}."""
    
    def __init__(self, force_deepseek: bool = True):
        """
        Initialize generator with DeepSeek routing.
        
        Args:
            force_deepseek: Always use DeepSeek (recommended for cost savings)
        """
        self.router = TaskRouter()
        self.force_deepseek = force_deepseek
    
    def _classify_content_type(self, prompt: str) -> ContentType:
        """Auto-classify content type from prompt."""
        prompt_lower = prompt.lower()
        # Add classification logic based on your content types
        return ContentType.GENERAL
    
    def _get_temperature(self, content_type: ContentType) -> float:
        """Get optimal temperature for content type."""
        temps = {{
            ContentType.GENERAL: 0.5,
            # Add temperature settings for each content type
        }}
        return temps.get(content_type, 0.5)
    
    def _get_max_tokens(self, content_type: ContentType) -> int:
        """Get optimal max tokens for content type."""
        tokens = {{
            ContentType.GENERAL: 1500,
            # Add token limits for each content type
        }}
        return tokens.get(content_type, 1500)
    
    def generate(
        self,
        prompt: str,
        content_type: Optional[ContentType] = None
    ) -> Dict[str, Any]:
        """
        Generate content using DeepSeek routing.
        
        Args:
            prompt: User's content request
            content_type: Override auto-detected content type
            
        Returns:
            Dict with: content, content_type, tokens, cost, routed_to
        """
        if content_type is None:
            content_type = self._classify_content_type(prompt)
        
        system = SYSTEM_PROMPTS.get(content_type, SYSTEM_PROMPTS[ContentType.GENERAL])
        temperature = self._get_temperature(content_type)
        max_tokens = self._get_max_tokens(content_type)
        
        result = self.router.route(
            prompt=prompt,
            system=system,
            force_deepseek=self.force_deepseek,
            max_tokens=max_tokens
        )
        
        result["content_type"] = content_type.value
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative usage statistics."""
        return self.router.get_stats()


def main():
    """CLI interface for content generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate content with DeepSeek cost optimization"
    )
    parser.add_argument("prompt", nargs="?", help="Content generation prompt")
    parser.add_argument(
        "--type", "-t",
        choices=[ct.value for ct in ContentType],
        help="Content type (auto-detected if not specified)"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show usage statistics"
    )
    
    args = parser.parse_args()
    
    generator = {class_name}Generator()
    
    if args.stats:
        stats = generator.get_stats()
        print(json.dumps(stats, indent=2))
        return
    
    if not args.prompt:
        parser.print_help()
        sys.exit(1)
    
    content_type = None
    if args.type:
        content_type = ContentType(args.type)
    
    result = generator.generate(args.prompt, content_type)
    
    print(f"Content Type: {{result['content_type'].upper()}}")
    print(f"Routed to: {{result['routed_to']}}")
    print(f"Tokens: {{result['tokens']['input']}} in / {{result['tokens']['output']}} out")
    print(f"Cost: ${{result['cost']:.6f}}")
    print("=" * 60)
    print(f"\\n{{result['content']}}")


if __name__ == "__main__":
    main()
