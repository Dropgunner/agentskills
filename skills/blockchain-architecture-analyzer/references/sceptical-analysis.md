# Sceptical Analysis Framework

## Table of Contents
1. Research Methodology
2. Red Flag Checklist
3. Tokenomics Evaluation
4. Risk Assessment Template

## 1. Research Methodology

Apply a structured sceptical lens to every chain analyzed:

**Source hierarchy** (most to least trustworthy):
1. On-chain data from block explorers (immutable facts)
2. Independent research firms (Blockworks, Messari, Delphi)
3. Audited financial disclosures
4. Official documentation (biased but primary)
5. Community/social media sentiment (noisy, verify claims)

**Triangulation rule**: Never report a metric from a single source. Cross-reference with at least one independent source. If sources disagree, report the range and note the discrepancy.

## 2. Red Flag Checklist

Evaluate each chain against these flags. Document findings for each:

### Performance Claims
- [ ] Are TPS numbers from mainnet or testnet?
- [ ] Is finality "theoretical" or "observed under load"?
- [ ] Has the chain been stress-tested by real DeFi activity?
- [ ] Any documented network outages or degraded performance?

### Tokenomics
- [ ] What % of supply is controlled by team/investors?
- [ ] Are vesting schedules public and verifiable on-chain?
- [ ] Is there a Foundation with discretionary unlocked tokens?
- [ ] What was the insider vs public allocation ratio?

### Ecosystem Health
- [ ] Is TVL organic or driven by token incentives?
- [ ] How many unique active addresses (not bots)?
- [ ] Are there real revenue-generating protocols?
- [ ] Any insider airdrop scandals or trust incidents?

### Centralization Risks
- [ ] How many validators? What's the Nakamoto coefficient?
- [ ] Is there a kill switch or admin key?
- [ ] Can the Foundation unilaterally upgrade the protocol?
- [ ] Geographic/jurisdictional concentration of validators?

## 3. Tokenomics Evaluation

When analyzing token distribution, calculate and report:

```
Insider Control % = (Team + Investors + Foundation) / Total Supply × 100
Public Access % = (Airdrop + Public Sale + Ecosystem Rewards) / Total Supply × 100
Concentration Risk = Insider Control % / Public Access %
```

**Interpretation:**
- Concentration Risk < 2: Reasonable distribution
- Concentration Risk 2-5: Moderate centralization concern
- Concentration Risk > 5: High centralization risk

## 4. Risk Assessment Template

For each chain, produce a risk summary:

```markdown
### [Chain Name] Risk Assessment

**Overall Risk Level**: [Low / Medium / High / Very High]

**Technical Risk**: [description]
- Mainnet maturity: [months since launch]
- Observed vs claimed TPS: [ratio]
- Known incidents: [list]

**Tokenomics Risk**: [description]
- Insider control: [X]%
- Public access: [X]%
- Concentration risk score: [X]

**Ecosystem Risk**: [description]
- TVL trend: [growing/stable/declining]
- Protocol diversity: [X protocols across Y categories]
- Revenue sustainability: [description]

**Regulatory Risk**: [description]
- Token classification concerns
- Jurisdictional risks
```
