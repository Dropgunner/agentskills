---
name: deepseek-skill-enhancer
description: >
  Integrate DeepSeek Router into existing skills for 90-96% cost savings on LLM operations.
  Use when: enhancing a skill with cost-optimized content generation, adding LLM-powered
  analysis to a skill, or reducing API costs for any skill that uses language models.
---

# DeepSeek Skill Enhancer

Integrate DeepSeek Router into any skill for cost-optimized LLM operations.

## Quick Start

**Automatic enhancement:**
```bash
python scripts/enhance_skill.py /home/ubuntu/skills/your-skill
```

**Manual enhancement:** Follow the workflow below.

## Prerequisites

The **deepseek-router** skill must be installed at `/home/ubuntu/skills/deepseek-router/`.

## Integration Workflow

### 1. Analyze Target Skill

Identify what the skill needs:

| Need | Solution |
|------|----------|
| Content generation (tweets, blogs, docs) | Add generator script |
| Document analysis (summarize, compare) | Add analyzer script |
| Both | Add both scripts |

### 2. Choose Integration Method

**Automatic (recommended):**
```bash
python scripts/enhance_skill.py /path/to/skill
```

**Manual:** Copy and customize templates from `templates/`.

### 3. Configure Content Types

For each content type, define:

| Setting | Purpose | Range |
|---------|---------|-------|
| Temperature | Creativity level | 0.2-0.8 |
| Max tokens | Output length | 500-3000 |
| System prompt | AI behavior | See `references/system_prompts.md` |

**Guidelines:**
- **Low temp (0.2-0.3)**: Factual, consistent (investor, technical)
- **Medium temp (0.4-0.6)**: Balanced (blog, analysis)
- **High temp (0.7-0.8)**: Creative, varied (social, community)

### 4. Test Integration

```bash
# Test generator
python scripts/skill_generator.py "Test prompt"

# Test analyzer (if added)
python scripts/skill_analyzer.py summarize "topic"
```

## Script Templates

### Generator Template

Use `templates/generator_template.py` for content generation. Customize:

1. `ContentType` enum with your content types
2. `SYSTEM_PROMPTS` dict with type-specific prompts
3. Temperature and token settings
4. Classification logic

### Analyzer Template

Use `templates/analyzer_template.py` for document analysis. Customize:

1. `DOCUMENTS` dict with your reference files
2. Analysis prompts if needed

## Example: Enhancing a Project Skill

**Before:** Skill has manual content templates, no LLM integration.

**After:**
```
my-project/
├── SKILL.md (updated with DeepSeek section)
├── scripts/
│   ├── my_project_generator.py  ← NEW
│   └── my_project_analyzer.py   ← NEW (optional)
├── references/
│   ├── glossary.md
│   └── routing_config.md        ← NEW
└── templates/
    └── content_templates.md
```

**Usage:**
```bash
# Generate a tweet
python scripts/my_project_generator.py --type social "Announce new feature"

# Generate investor pitch
python scripts/my_project_generator.py --type investor "Summarize value prop"

# Analyze whitepaper
python scripts/my_project_analyzer.py summarize "tokenomics"
```

## Cost Savings

| Operation | Premium Model | DeepSeek | Savings |
|-----------|---------------|----------|---------|
| Tweet | ~$0.02 | ~$0.001 | 95% |
| Blog post | ~$0.08 | ~$0.004 | 95% |
| Document summary | ~$0.15 | ~$0.008 | 95% |
| Term lookup | ~$0.01 | ~$0.0005 | 95% |

## References

| File | When to Read |
|------|--------------|
| `references/integration_checklist.md` | Manual integration step-by-step |
| `references/system_prompts.md` | Writing effective system prompts |

## When to Use This Skill

- Adding LLM-powered content generation to any skill
- Reducing API costs for existing LLM integrations
- Creating cost-optimized document analysis pipelines
- Standardizing LLM usage across multiple skills
