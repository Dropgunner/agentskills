# Risk Scoring Methodology

## Overview

The risk scoring system evaluates tokens on a scale of 1-10, where:
- **1-3**: Low risk (relatively safe)
- **4-5**: Medium risk (proceed with caution)
- **6-7**: High risk (significant concerns)
- **8-10**: Critical risk (likely scam or rug pull)

## Scoring Components

### 1. Contract Verification (Max: 3 points)

| Status | Points |
|--------|--------|
| Verified source code | 0 |
| Unverified source code | +3 |

Unverified contracts are a major red flag as the code cannot be audited.

### 2. Ownership Status (Max: 2 points)

| Status | Points |
|--------|--------|
| Ownership renounced | 0 |
| Ownership active | +2 |

Active ownership means the owner can potentially modify contract behavior.

### 3. Holder Concentration (Max: 3 points)

| Metric | Threshold | Points |
|--------|-----------|--------|
| Top holder | >50% | +3 |
| Top holder | >20% | +2 |
| Top 10 holders | >80% | +2 |
| Top 10 holders | >60% | +1 |

High concentration enables market manipulation and rug pulls.

### 4. Liquidity Analysis (Max: 3 points)

| Metric | Threshold | Points |
|--------|-----------|--------|
| Total liquidity | <$10,000 | +3 |
| Total liquidity | <$50,000 | +2 |
| Total liquidity | <$100,000 | +1 |
| LP not locked | Any | +2 |
| LP lock <6 months | Any | +1 |

Low liquidity enables easy manipulation; unlocked LP can be pulled.

### 5. Contract Red Flags (Variable)

| Finding | Points |
|---------|--------|
| Hidden mint function | +3 |
| Honeypot indicators | +3 |
| Blacklist function | +2 |
| Self-destruct | +3 |
| Pause function | +1 |
| High/adjustable fees | +1 |
| Proxy/upgradeable | +1 |

### 6. Project Signals (Max: 2 points)

| Signal | Points |
|--------|--------|
| Anonymous team | +1 |
| No audit | +1 |
| <7 days old | +1 |
| No social presence | +1 |

## Score Calculation

```python
def calculate_risk_score(analysis: dict) -> tuple[int, str]:
    score = 0
    
    # Contract verification
    if not analysis.get("is_verified"):
        score += 3
    
    # Ownership
    if not analysis.get("ownership_renounced"):
        score += 2
    
    # Holder concentration
    top_holder = analysis.get("top_holder_pct", 0)
    top_10 = analysis.get("top_10_pct", 0)
    
    if top_holder > 50:
        score += 3
    elif top_holder > 20:
        score += 2
    
    if top_10 > 80:
        score += 2
    elif top_10 > 60:
        score += 1
    
    # Liquidity
    liquidity = analysis.get("liquidity_usd", 0)
    if liquidity < 10000:
        score += 3
    elif liquidity < 50000:
        score += 2
    elif liquidity < 100000:
        score += 1
    
    if not analysis.get("lp_locked"):
        score += 2
    
    # Contract findings
    findings = analysis.get("contract_findings", {})
    score += len(findings.get("critical", [])) * 3
    score += len(findings.get("high", [])) * 1.5
    score += len(findings.get("medium", [])) * 0.5
    
    # Cap score
    score = min(10, max(1, int(score)))
    
    # Determine level
    if score >= 8:
        level = "Critical"
    elif score >= 6:
        level = "High"
    elif score >= 4:
        level = "Medium"
    else:
        level = "Low"
    
    return score, level
```

## Risk Level Recommendations

### Low Risk (1-3)
- Token appears relatively safe
- Standard due diligence recommended
- Monitor for changes in ownership/liquidity

### Medium Risk (4-5)
- Proceed with caution
- Limit investment size
- Set stop-losses
- Monitor closely

### High Risk (6-7)
- Significant concerns identified
- Only invest what you can afford to lose
- Consider avoiding entirely
- If investing, use small amounts

### Critical Risk (8-10)
- Strong indicators of scam or rug pull
- **Avoid investment**
- If already invested, consider exiting
- Report to community

## Ouroboros-Specific Scoring

For post-rug analysis (Ouroboros project), additional metrics apply:

### Post-Rug Opportunity Score

| Factor | Weight |
|--------|--------|
| Remaining liquidity | 30% |
| Active trading volume | 25% |
| Community sentiment | 20% |
| Recovery potential | 15% |
| Legal exposure | 10% |

```python
def calculate_ouroboros_score(post_rug_data: dict) -> float:
    """Calculate opportunity score for post-rug tokens."""
    weights = {
        "remaining_liquidity": 0.30,
        "trading_volume": 0.25,
        "community_sentiment": 0.20,
        "recovery_potential": 0.15,
        "legal_exposure": 0.10
    }
    
    score = 0
    for factor, weight in weights.items():
        factor_score = post_rug_data.get(factor, 0)  # 0-100 scale
        score += factor_score * weight
    
    return score  # 0-100 scale
```

## Automated Alerts

Configure alerts for:
- Score changes >2 points
- Ownership transfer events
- Large liquidity removals (>10%)
- Unusual trading patterns
- Contract upgrades (for proxies)
