---
name: github-repo-manager
description: Streamlined GitHub repository management workflows using the GitHub CLI. Use when creating repositories, managing issues and PRs, configuring workflows, or automating GitHub operations. Optimized for personal workflow efficiency.
license: MIT
metadata:
  author: Prayer
  version: "1.0"
---

# GitHub Repository Manager

Efficient GitHub repository management using the `gh` CLI.

## When to Use

- Creating new repositories with proper configuration
- Managing issues and pull requests
- Setting up GitHub Actions workflows
- Configuring repository settings and secrets
- Automating release processes

## Prerequisites

The GitHub CLI (`gh`) must be authenticated:

```bash
# Check authentication status
gh auth status

# Login if needed
gh auth login
```

## Quick Start

```bash
# Create a new private repository
gh repo create my-project --private --clone

# List open issues
gh issue list

# Create a pull request
gh pr create --title "Feature: Add new functionality" --body "Description"

# View repository info
gh repo view
```

## Repository Operations

### Create Repository

```bash
# Create private repo (default for privacy)
gh repo create project-name --private

# Create with description
gh repo create project-name --private --description "Project description"

# Create and clone
gh repo create project-name --private --clone

# Create from template
gh repo create project-name --template owner/template-repo

# Create organization repo
gh repo create org-name/project-name --private
```

### Clone Repository

```bash
# Clone by name
gh repo clone owner/repo

# Clone to specific directory
gh repo clone owner/repo ./local-dir
```

### Repository Settings

```bash
# View repo info
gh repo view owner/repo

# Edit description
gh repo edit --description "New description"

# Add topics
gh repo edit --add-topic "web3,solidity,defi"

# Set homepage
gh repo edit --homepage "https://example.com"

# Enable/disable features
gh repo edit --enable-wiki=false --enable-issues=true
```

## Issue Management

### Create Issues

```bash
# Interactive creation
gh issue create

# With title and body
gh issue create --title "Bug: Description" --body "Details here"

# With labels
gh issue create --title "Feature request" --label "enhancement,priority:high"

# Assign to user
gh issue create --title "Task" --assignee @me
```

### List and Filter Issues

```bash
# List all open issues
gh issue list

# Filter by label
gh issue list --label "bug"

# Filter by assignee
gh issue list --assignee @me

# Show closed issues
gh issue list --state closed

# Limit results
gh issue list --limit 10
```

### Manage Issues

```bash
# View issue details
gh issue view 123

# Close issue
gh issue close 123

# Reopen issue
gh issue reopen 123

# Add comment
gh issue comment 123 --body "Comment text"

# Edit issue
gh issue edit 123 --title "New title" --add-label "in-progress"
```

## Pull Request Workflow

### Create Pull Requests

```bash
# Interactive creation
gh pr create

# With details
gh pr create --title "Feature: Add X" --body "Description"

# Draft PR
gh pr create --draft --title "WIP: Feature"

# Set reviewers
gh pr create --reviewer user1,user2

# Set base branch
gh pr create --base develop
```

### Review Pull Requests

```bash
# List PRs
gh pr list

# View PR details
gh pr view 123

# Check out PR locally
gh pr checkout 123

# Review PR
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Please fix X"
gh pr review 123 --comment --body "Looks good overall"

# Merge PR
gh pr merge 123 --squash
gh pr merge 123 --rebase
gh pr merge 123 --merge
```

### PR Checks

```bash
# View PR checks status
gh pr checks 123

# Wait for checks to complete
gh pr checks 123 --watch
```

## GitHub Actions

### View Workflows

```bash
# List workflows
gh workflow list

# View workflow runs
gh run list

# View specific run
gh run view 123456

# Watch run in progress
gh run watch 123456
```

### Trigger Workflows

```bash
# Run workflow manually
gh workflow run workflow-name.yml

# Run with inputs
gh workflow run workflow-name.yml -f input1=value1 -f input2=value2
```

### View Logs

```bash
# View run logs
gh run view 123456 --log

# Download logs
gh run download 123456
```

## Releases

### Create Releases

```bash
# Create release from tag
gh release create v1.0.0

# With title and notes
gh release create v1.0.0 --title "Version 1.0.0" --notes "Release notes"

# Generate notes automatically
gh release create v1.0.0 --generate-notes

# Upload assets
gh release create v1.0.0 ./dist/app.zip ./dist/app.tar.gz

# Create draft release
gh release create v1.0.0 --draft
```

### Manage Releases

```bash
# List releases
gh release list

# View release
gh release view v1.0.0

# Download release assets
gh release download v1.0.0

# Delete release
gh release delete v1.0.0
```

## Secrets Management

```bash
# Set repository secret
gh secret set SECRET_NAME

# Set from file
gh secret set SECRET_NAME < secret.txt

# Set with value
echo "secret-value" | gh secret set SECRET_NAME

# List secrets
gh secret list

# Delete secret
gh secret delete SECRET_NAME
```

## Repository Templates

### Standard Project Setup

```bash
# Create repo with full setup
gh repo create project-name --private --clone && \
cd project-name && \
git checkout -b develop && \
mkdir -p .github/workflows src tests docs && \
touch README.md LICENSE .gitignore && \
git add . && \
git commit -m "Initial project structure" && \
git push -u origin develop
```

### GitHub Actions Workflow Template

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: echo "Add test commands here"
```

## Automation Scripts

### Batch Issue Creation

```bash
#!/bin/bash
# Create multiple issues from a file
while IFS= read -r title; do
    gh issue create --title "$title" --label "task"
done < issues.txt
```

### PR Auto-merge Setup

```bash
# Enable auto-merge for a PR
gh pr merge 123 --auto --squash
```

## Best Practices

### Repository Hygiene
- Use descriptive commit messages
- Keep PRs focused and small
- Use labels consistently
- Close stale issues regularly

### Security
- Never commit secrets
- Use repository secrets for sensitive data
- Enable branch protection on main
- Require PR reviews

### Workflow Efficiency
- Use PR templates
- Set up issue templates
- Configure CODEOWNERS
- Use GitHub Actions for automation
