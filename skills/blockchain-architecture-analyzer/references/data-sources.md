# Data Sources & Validation Guide

## Table of Contents
1. Primary Data Sources
2. Cross-Validation Matrix
3. Common Data Pitfalls
4. Brand Colors Registry

## 1. Primary Data Sources

| Source | URL | Data | Reliability |
|--------|-----|------|-------------|
| DeFi Llama | defillama.com/chains | TVL, fees, DEX volume, protocol count | High — aggregates on-chain data |
| L2Beat | l2beat.com | L2 TVL, risk assessment, stage classification | High — independent research |
| CoinGecko | coingecko.com | Token price, market cap, FDV, volume | High — aggregates exchange data |
| Messari | messari.io | Governance, tokenomics, quarterly reports | High — analyst-verified |
| Blockworks Research | blockworksresearch.com | Deep technical analysis, protocol reviews | High — peer-reviewed |
| Delphi Digital | delphidigital.io | Market analysis, ecosystem reports | Medium-High |
| Token Terminal | tokenterminal.com | Revenue, P/E ratios, active users | High — on-chain verified |
| Official Docs | docs.{chain}.xyz | Architecture, specs, roadmap | Primary source but biased |
| Block Explorers | Various per chain | Actual TPS, gas prices, active addresses | High — direct on-chain |

### Block Explorer URLs
- Ethereum: etherscan.io
- Solana: solscan.io
- Injective: explorer.injective.network
- Monad: explorer.monad.xyz (post-mainnet)
- Sui: suiscan.xyz
- Avalanche: snowscan.xyz
- Aptos: aptoscan.com

## 2. Cross-Validation Matrix

Always validate claims from at least 2 independent sources:

| Metric | Primary Source | Validation Source |
|--------|---------------|-------------------|
| TPS (claimed) | Official docs | Blockworks/Messari reports |
| TPS (actual) | Block explorer | DeFi Llama activity metrics |
| TVL | DeFi Llama | Individual protocol dashboards |
| Gas cost | Block explorer (recent txs) | Gas tracker tools |
| Token supply | CoinGecko | Official tokenomics page |
| Funding | Crunchbase/official announcements | The Block, CoinDesk |
| Team | LinkedIn, official site | Conference talks, GitHub |

## 3. Common Data Pitfalls

**TPS inflation**: Many chains report theoretical max TPS from testnets. Always distinguish "theoretical" vs "observed mainnet" TPS. If mainnet data unavailable, label as "theoretical."

**TVL manipulation**: Check if TVL is inflated by:
- Counting same assets across multiple protocols (double-counting)
- Native token staking counted as TVL
- Incentivized liquidity mining inflating short-term TVL

**Gas cost variability**: Gas costs vary 10-100x based on network congestion and tx complexity. Report:
- Simple transfer cost (baseline)
- DEX swap cost (typical DeFi)
- Note congestion conditions

**Funding vs valuation**: Distinguish between total raised and last-round valuation. A $225M raise at $3B valuation means the project sold ~7.5% equity equivalent.

## 4. Brand Colors Registry

Use official brand colors for visual consistency:

| Chain | Primary Hex | Secondary Hex | Notes |
|-------|------------|---------------|-------|
| Injective | #00F2FE | #0B1426 | Cyan/teal on dark navy |
| Monad | #836EF9 | #200052 | Purple on deep violet |
| Ethereum | #627EEA | #1C1C28 | Blue-purple |
| Solana | #9945FF | #14F195 | Purple + green gradient |
| Sui | #4DA2FF | #0B1B35 | Blue on dark |
| Avalanche | #E84142 | #1A1A2E | Red on dark |
| MegaETH | #FF6B35 | #1A0A2E | Orange on dark |
| Aptos | #2DD8A3 | #0A0A0A | Teal-green on black |
