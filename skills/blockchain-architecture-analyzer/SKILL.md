---
name: blockchain-architecture-analyzer
description: Research blockchain architectures and generate interactive comparison webpages or comprehensive analysis reports. Use when analyzing L1/L2 blockchain technical specs, comparing chain performance (TPS, finality, gas costs, TVL), creating visual blockchain comparison sites, or producing deep research reports on crypto projects. Supports both single-chain deep dives and multi-chain comparative analysis.
---

# Blockchain Architecture Analyzer

End-to-end workflow for researching blockchain protocols and producing either interactive comparison webpages or comprehensive written reports.

## Workflow Decision Tree

Determine the output type, then follow the appropriate path:

**Producing a comparison webpage?** → Follow all 6 phases below.
**Producing a written report only?** → Follow Phases 1-3, skip 4-6, use report template from `templates/research-report-template.md`.
**Adding a chain to an existing comparison?** → Skip to Phase 2 for the new chain, then Phase 5 to integrate.

## Phase 1: Scope & Planning

1. Identify target chains (user-specified or inferred from context)
2. Determine output type: webpage, report, or both
3. Create `{project}_research/` directory for incremental findings
4. If building a webpage, initialize webdev project and brainstorm design

## Phase 2: Research & Data Collection

For each chain, collect data in this order:

1. **Official docs** — Architecture, consensus, execution model, VM, languages
2. **Block explorers** — Actual TPS, gas prices, active addresses
3. **DeFi Llama** — TVL, protocol count, fee revenue
4. **Research reports** — Blockworks, Messari, Delphi Digital analysis
5. **News/announcements** — Funding, team changes, incidents, partnerships

Save findings incrementally to `{project}_research/0X_{topic}.md` files. Never rely on browser context alone.

For data source URLs and cross-validation rules, read `references/data-sources.md`.

## Phase 3: Analysis & Structuring

Structure data using the TypeScript interfaces in `templates/chain-data-template.ts`:
- `ChainData` for per-chain metrics (TPS, gas, TVL, etc.)
- `FeatureCategory` + `FeatureRow` for the boolean feature matrix

Apply the sceptical analysis framework from `references/sceptical-analysis.md`:
- Distinguish theoretical vs observed performance
- Calculate tokenomics concentration risk score
- Flag insider control percentages
- Note any trust incidents or centralization concerns

**Feature matrix categories** (expand as needed):
- Execution Model: parallel execution, optimistic concurrency, async execution
- Consensus: BFT-based, single-slot finality, pipelined consensus
- State Management: custom database, async I/O, native trie
- Developer Experience: EVM compatibility, multi-VM, Solidity support
- DeFi Infrastructure: native order book, MEV resistance, IBC/cross-chain

## Phase 4: Image Generation

Generate 3-5 high-quality images before coding:
- Hero background (cosmic/data visualization aesthetic)
- Architecture diagram visual
- Consensus mechanism visual
- Database/state management visual
- Comparison chart background

Use detailed prompts tailored to the "Data Observatory" theme. Upload to CDN via `manus-upload-file`.

## Phase 5: Webpage Implementation

Use webdev static template (React + Tailwind + shadcn/ui). For design system details, component patterns, and chart implementations, read `references/design-patterns.md`.

**Section order:**
1. Hero with key stats
2. Chain selector pills
3. Side-by-side comparison cards
4. Architecture deep-dive tabs (for featured chains)
5. Feature matrix table
6. Performance charts (TPS, block time, finality)
7. Gas cost comparison (logarithmic scale)
8. TVL comparison with adoption context
9. Key takeaways
10. Footer with sources and methodology

**Critical implementation notes:**
- Use `React.Fragment` with `key` prop (not bare `<>`) when mapping categories with sub-items
- Use logarithmic scales when max/min ratio exceeds 10x
- Include "Last updated" timestamp and data source attribution
- Wrap tables in `overflow-x-auto` for mobile
- Chain order should match user preference (ask if not specified)

## Phase 6: Validation & Delivery

1. Verify zero TypeScript errors
2. Check all sections render correctly
3. Confirm responsive layout on mobile
4. Save checkpoint and deliver

## Resources

- **Data sources & validation**: Read `references/data-sources.md` for source URLs, cross-validation rules, brand colors
- **Design patterns**: Read `references/design-patterns.md` for CSS system, component patterns, chart implementations
- **Sceptical analysis**: Read `references/sceptical-analysis.md` for research methodology, red flags, tokenomics evaluation
- **Chain data template**: Copy `templates/chain-data-template.ts` into project for TypeScript interfaces
- **Report template**: Copy `templates/research-report-template.md` for written analysis output
