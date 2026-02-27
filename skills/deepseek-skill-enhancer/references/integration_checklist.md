# DeepSeek Integration Checklist

Use this checklist when manually integrating DeepSeek into a skill.

## Prerequisites

- [ ] DeepSeek Router skill installed at `/home/ubuntu/skills/deepseek-router/`
- [ ] API key available (`$DEEPSEEK_API_KEY`, `$manus`, or fallback)
- [ ] Target skill has `scripts/` directory (create if needed)

## Integration Steps

### 1. Analyze Target Skill

- [ ] Identify content types (social, blog, technical, etc.)
- [ ] Identify documents that need analysis
- [ ] Identify repetitive LLM tasks

### 2. Create Generator Script

- [ ] Copy `templates/generator_template.py` to target skill
- [ ] Customize `ContentType` enum for skill's content types
- [ ] Customize `SYSTEM_PROMPTS` for each content type
- [ ] Customize temperature and token settings
- [ ] Add content type classification logic

### 3. Create Analyzer Script (if needed)

- [ ] Copy `templates/analyzer_template.py` to target skill
- [ ] Configure `DOCUMENTS` dict with skill's reference files
- [ ] Customize analysis prompts if needed

### 4. Create Routing Config

- [ ] Add `references/routing_config.md` with:
  - Task routing settings table
  - Cost optimization notes
  - Environment variable documentation

### 5. Update SKILL.md

- [ ] Add DeepSeek integration section
- [ ] Document new CLI commands
- [ ] Add cost savings table
- [ ] Reference routing config

### 6. Test Integration

- [ ] Test generator with sample prompts
- [ ] Test analyzer with sample documents
- [ ] Verify cost tracking works
- [ ] Check cache functionality

## Content Type Configuration

| Content Type | Temperature | Max Tokens | Use Case |
|--------------|-------------|------------|----------|
| social | 0.7-0.8 | 500 | Tweets, Discord messages |
| blog | 0.5-0.6 | 2000 | Articles, posts |
| investor | 0.2-0.3 | 1500 | Pitches, summaries |
| technical | 0.2-0.3 | 2500 | Documentation, specs |
| community | 0.6-0.7 | 800 | Welcome messages, announcements |
| general | 0.5 | 1500 | Default fallback |

## System Prompt Guidelines

Effective system prompts should include:

1. **Role definition**: Who the AI is acting as
2. **Voice/tone**: How to communicate
3. **Key terminology**: Domain-specific terms
4. **Output structure**: Expected format
5. **Constraints**: What to avoid

Example:
```
You are the voice of [PROJECT], a [DESCRIPTION].

VOICE & TONE:
- [Style guidelines]

KEY TERMS:
- Term1: Definition
- Term2: Definition

OUTPUT FORMAT:
- [Structure requirements]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not found | Check `$DEEPSEEK_API_KEY`, `$manus`, or fallback keys |
| Import errors | Verify DeepSeek Router path in sys.path |
| High costs | Enable caching, reduce max_tokens |
| Poor quality | Adjust temperature, improve system prompts |
