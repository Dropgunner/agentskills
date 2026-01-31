---
name: skill-validator
description: Validate and test Agent Skills for compliance with the specification. Use when creating new skills, reviewing skill quality, or preparing skills for publication. Checks frontmatter, structure, and best practices.
license: MIT
metadata:
  author: Prayer
  version: "1.0"
---

# Skill Validator

Comprehensive validation and testing for Agent Skills.

## When to Use

- Creating a new skill and need to verify compliance
- Reviewing skill quality before publication
- Debugging skill loading or activation issues
- Batch validating a skill repository
- Generating skill metadata for agent integration

## Quick Start

```bash
# Validate a single skill
python scripts/validate_skill.py --skill /path/to/skill-name

# Validate all skills in a directory
python scripts/validate_skill.py --directory /path/to/skills

# Generate prompt XML for skills
python scripts/generate_prompt.py --skills /path/to/skill1 /path/to/skill2

# Check skill quality score
python scripts/quality_check.py --skill /path/to/skill-name
```

## Validation Workflow

1. **Structure check** - Verify required files and directories
2. **Frontmatter validation** - Check YAML syntax and required fields
3. **Naming conventions** - Validate skill name format
4. **Content analysis** - Check body content quality
5. **Resource verification** - Validate bundled scripts and references

## Validation Rules

### Required Elements

| Element | Requirement |
|---------|-------------|
| SKILL.md | Must exist in skill root |
| Frontmatter | Must have valid YAML with `---` delimiters |
| `name` field | Required, 1-64 chars, lowercase alphanumeric + hyphens |
| `description` field | Required, 1-1024 chars, non-empty |

### Name Field Rules

- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only
- Cannot start or end with hyphen
- No consecutive hyphens (`--`)
- Must match parent directory name

**Valid examples:**
- `pdf-processing`
- `data-analysis`
- `code-review`

**Invalid examples:**
- `PDF-Processing` (uppercase)
- `-pdf` (starts with hyphen)
- `pdf--processing` (consecutive hyphens)

### Description Field Rules

- Maximum 1024 characters
- Must describe what the skill does
- Should include when to use it
- Should contain relevant keywords for discovery

**Good example:**
```yaml
description: Extract text and tables from PDF files, fill PDF forms, and merge multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor example:**
```yaml
description: Helps with PDFs.
```

### Optional Fields

| Field | Constraints |
|-------|-------------|
| `license` | License name or reference to LICENSE file |
| `compatibility` | Max 500 chars, environment requirements |
| `metadata` | Key-value mapping for additional properties |
| `allowed-tools` | Space-delimited list of pre-approved tools |

## Quality Metrics

### Content Quality Score (0-100)

| Metric | Weight | Criteria |
|--------|--------|----------|
| Description quality | 20% | Length, keywords, clarity |
| Body structure | 25% | Headers, sections, organization |
| Examples provided | 20% | Code samples, usage examples |
| Resource organization | 15% | Scripts, references, templates |
| Documentation | 20% | Comments, explanations |

### Size Guidelines

| Element | Recommendation |
|---------|----------------|
| SKILL.md body | < 500 lines |
| Description | 50-200 characters |
| Individual reference files | < 10,000 words |
| Total skill size | < 1 MB |

## Error Messages

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Missing required file: SKILL.md" | No SKILL.md in directory | Create SKILL.md with frontmatter |
| "SKILL.md must start with YAML frontmatter" | Missing `---` delimiter | Add `---` at start of file |
| "Missing required field: name" | No name in frontmatter | Add `name: skill-name` |
| "Skill name must be lowercase" | Uppercase in name | Convert to lowercase |
| "Directory name must match skill name" | Mismatch | Rename directory or update name |

## Integration with skills-ref

The official `skills-ref` library provides additional validation:

```bash
# Install skills-ref
pip install skills-ref

# Validate skill
skills-ref validate /path/to/skill

# Read properties as JSON
skills-ref read-properties /path/to/skill

# Generate prompt XML
skills-ref to-prompt /path/to/skill1 /path/to/skill2
```

## Prompt XML Format

For Claude and compatible models:

```xml
<available_skills>
<skill>
<name>skill-name</name>
<description>What this skill does and when to use it</description>
<location>/path/to/skill-name/SKILL.md</location>
</skill>
</available_skills>
```

## Best Practices Checklist

### Structure
- [ ] SKILL.md exists with valid frontmatter
- [ ] Name matches directory name
- [ ] Description is comprehensive and includes usage triggers
- [ ] Body content is under 500 lines

### Content
- [ ] Clear step-by-step instructions
- [ ] Concrete examples with realistic scenarios
- [ ] Error handling guidance
- [ ] References to bundled resources

### Resources
- [ ] Scripts are tested and functional
- [ ] References are focused and not duplicated
- [ ] Templates are complete and usable
- [ ] Unused example files removed

### Documentation
- [ ] All scripts have docstrings/comments
- [ ] Complex logic is explained
- [ ] Dependencies are documented
- [ ] Version/author metadata included
