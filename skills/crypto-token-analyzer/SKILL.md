---
name: crypto-token-analyzer
description: Analyze cryptocurrency tokens for rug pull indicators, liquidity health, holder distribution, and smart contract risks. Use when evaluating new tokens, investigating suspicious projects, or performing due diligence on DeFi investments.
license: MIT
metadata:
  author: Prayer
  version: "1.0"
---

# Crypto Token Analyzer

Comprehensive token analysis for identifying rug pull risks and evaluating token health.

## When to Use

- Evaluating a new token before investment
- Investigating suspicious token behavior
- Analyzing post-rug market dynamics (Ouroboros use case)
- Performing due diligence on DeFi projects

## Analysis Workflow

Token analysis follows these sequential steps:

1. **Gather token data** (run `scripts/fetch_token_data.py`)
2. **Analyze holder distribution** (run `scripts/analyze_holders.py`)
3. **Check liquidity health** (run `scripts/check_liquidity.py`)
4. **Scan contract for risks** (run `scripts/scan_contract.py`)
5. **Generate risk report** (compile findings into report)

## Quick Start

For a complete token analysis:

```bash
# Fetch token data from blockchain explorers
python scripts/fetch_token_data.py --token <contract_address> --chain <eth|bsc|polygon>

# Analyze holder concentration
python scripts/analyze_holders.py --token <contract_address>

# Check liquidity pools
python scripts/check_liquidity.py --token <contract_address>

# Scan contract for red flags
python scripts/scan_contract.py --token <contract_address>
```

## Rug Pull Indicators

### High-Risk Signals (Immediate Red Flags)

| Indicator | Description | Risk Level |
|-----------|-------------|------------|
| Honeypot code | Contract prevents selling | Critical |
| Hidden mint function | Owner can create unlimited tokens | Critical |
| Ownership not renounced | Owner retains control | High |
| Single holder >50% | Extreme concentration | High |
| Liquidity <$10k | Easy to drain | High |

### Medium-Risk Signals

| Indicator | Description | Risk Level |
|-----------|-------------|------------|
| Top 10 holders >80% | High concentration | Medium |
| Unlocked liquidity | LP tokens not locked | Medium |
| No verified source | Contract not verified | Medium |
| Recent deployment | Less than 7 days old | Medium |

### Low-Risk Signals (Due Diligence Items)

| Indicator | Description | Risk Level |
|-----------|-------------|------------|
| Anonymous team | No public identities | Low |
| No audit | Not professionally audited | Low |
| Low social presence | Limited community | Low |

## Report Template

Generate reports using this structure:

```markdown
# Token Analysis Report: [TOKEN_NAME]

## Executive Summary
[One-paragraph risk assessment with overall score]

## Token Overview
- Contract: [address]
- Chain: [network]
- Deployment Date: [date]
- Total Supply: [supply]

## Risk Assessment

### Critical Findings
[List any critical red flags]

### Holder Analysis
- Top holder: [percentage]%
- Top 10 holders: [percentage]%
- Unique holders: [count]
- Concentration risk: [Low/Medium/High]

### Liquidity Analysis
- Total liquidity: $[amount]
- LP lock status: [Locked/Unlocked]
- Lock duration: [if locked]
- Liquidity risk: [Low/Medium/High]

### Contract Analysis
- Source verified: [Yes/No]
- Ownership: [Renounced/Active]
- Dangerous functions: [List]
- Contract risk: [Low/Medium/High]

## Overall Risk Score
[1-10 scale with justification]

## Recommendations
[Specific actionable recommendations]
```

## API References

For detailed API documentation:
- **Blockchain APIs**: See [references/blockchain-apis.md](references/blockchain-apis.md)
- **DEX APIs**: See [references/dex-apis.md](references/dex-apis.md)
- **Risk Scoring**: See [references/risk-scoring.md](references/risk-scoring.md)

## Chain-Specific Notes

### Ethereum
- Use Etherscan API for contract data
- Check Uniswap V2/V3 for liquidity
- Verify on Etherscan before analysis

### BSC (Binance Smart Chain)
- Use BscScan API
- Check PancakeSwap for liquidity
- Higher rug pull frequency—apply stricter criteria

### Polygon
- Use PolygonScan API
- Check QuickSwap for liquidity
- Lower gas costs enable more frequent scams
