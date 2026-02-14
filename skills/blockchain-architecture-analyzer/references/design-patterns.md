# Webpage Design Patterns for Blockchain Comparisons

## Table of Contents
1. Design System
2. Section Architecture
3. Chart Patterns
4. Interaction Patterns
5. Common Pitfalls

## 1. Design System

### Theme: "Data Observatory"
Dark theme with chain-branded accent colors. Scientific visualization aesthetic.

**Typography:**
- Headings: `Space Grotesk` (weights: 500, 600, 700)
- Body: `Inter` (weights: 400, 500, 600)
- Code/metrics: `IBM Plex Mono` (weights: 400, 500)

**Google Fonts import:**
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

**CSS custom properties (OKLCH for Tailwind 4):**
```css
:root {
  --background: oklch(0.12 0.02 260);    /* Deep space navy */
  --foreground: oklch(0.92 0.01 260);    /* Light text */
  --card: oklch(0.16 0.025 260);         /* Slightly lighter navy */
  --primary: oklch(0.65 0.2 280);        /* Purple accent */
  --secondary: oklch(0.65 0.15 180);     /* Teal accent */
  --accent: oklch(0.75 0.15 70);         /* Amber highlights */
  --muted: oklch(0.25 0.02 260);         /* Subdued backgrounds */
  --border: oklch(0.3 0.03 260);         /* Subtle borders */
}
```

**Glass card pattern:**
```css
.glass-card {
  @apply bg-card/60 backdrop-blur-md border border-border/50 rounded-lg;
}
.glow-purple {
  box-shadow: 0 0 40px rgba(131, 110, 249, 0.15);
}
```

## 2. Section Architecture

Recommended page sections in order:

1. **Hero** — Background image + headline + key stats (3-4 metric cards)
2. **Chain Selector** — Interactive pills to filter/highlight chains
3. **Side-by-Side Comparison** — Expandable cards per chain with key specs
4. **Architecture Deep Dive** — Tabbed sections for featured chain(s)
5. **Feature Matrix** — Boolean grid table with category groupings
6. **Performance Charts** — Animated bar charts (TPS, block time, finality)
7. **Gas Cost Comparison** — Logarithmic bar chart with contextual notes
8. **TVL Comparison** — Bar chart with ecosystem adoption context
9. **Key Takeaways** — Summary cards with actionable insights
10. **Footer** — Data sources, methodology notes, last updated date

### Hero Section Pattern
```tsx
<section className="relative min-h-[80vh] flex items-center overflow-hidden">
  <div className="absolute inset-0 z-0">
    <img src={HERO_BG} className="w-full h-full object-cover opacity-40" />
    <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent" />
  </div>
  <div className="container relative z-10">
    {/* Content with light text on dark image */}
  </div>
</section>
```

### Chain Selector Pattern
```tsx
const [selectedChain, setSelectedChain] = useState<string | null>(null);
// Render pills with chain brand colors
{chains.map(chain => (
  <button
    key={chain.id}
    onClick={() => setSelectedChain(chain.id === selectedChain ? null : chain.id)}
    style={{ borderColor: chain.color, color: selected ? '#fff' : chain.color,
             backgroundColor: selected ? chain.color : 'transparent' }}
  />
))}
```

## 3. Chart Patterns

### When to use logarithmic scales
Use log scales when the ratio between max and min values exceeds 10x:
- TVL: $55M vs $55.9B → log scale
- Gas: $0.0003 vs $5.00 → log scale
- TPS: 15 vs 25,000 → log scale OK, but linear also works

### Animated bar implementation
```tsx
import { motion } from "framer-motion";

<motion.div
  className="h-8 rounded-r"
  style={{ backgroundColor: chain.color }}
  initial={{ width: 0 }}
  whileInView={{ width: `${percentage}%` }}
  viewport={{ once: true }}
  transition={{ duration: 1, delay: index * 0.1 }}
/>
```

### Feature matrix icons
```tsx
const FeatureStatus = ({ value }: { value: boolean | "partial" }) => {
  if (value === true) return <CheckCircle className="text-green-400" />;
  if (value === "partial") return <Minus className="text-amber-400" />;
  return <XCircle className="text-red-400/50" />;
};
```

## 4. Interaction Patterns

- **Chain selector pills**: Toggle highlight on click, show all when none selected
- **Expandable comparison cards**: Click to reveal full specs
- **Tabbed architecture sections**: One tab per featured chain
- **Hover tooltips**: Explain technical terms inline
- **Smooth scroll anchors**: Hero CTAs scroll to comparison section

## 5. Common Pitfalls

- **Missing React keys**: Use `React.Fragment` with `key` prop when mapping categories with sub-items in tables, not bare `<>...</>`
- **Text invisible on hero**: Always add gradient overlay on background images; use light text on dark overlays
- **Table overflow on mobile**: Wrap tables in `overflow-x-auto` container
- **Chart scale misleading**: Always label axes and note if using logarithmic scale
- **Stale data**: Include "Last updated" timestamp and data source attribution
