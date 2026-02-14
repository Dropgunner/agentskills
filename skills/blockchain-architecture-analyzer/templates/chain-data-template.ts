/**
 * Template: Chain data structure for blockchain comparison pages.
 * Copy this file into your project and populate with researched data.
 * 
 * Usage: Import into your React page component and map over the array.
 */

export interface ChainData {
  id: string;              // lowercase slug, e.g., "injective"
  name: string;            // display name, e.g., "Injective"
  color: string;           // hex brand color, e.g., "#00F2FE"
  tps: string;             // formatted TPS, e.g., "25,000+"
  tpsValue: number;        // numeric for charts, e.g., 25000
  blockTime: string;       // formatted, e.g., "0.65s"
  blockTimeValue: number;  // numeric seconds, e.g., 0.65
  finality: string;        // formatted, e.g., "Instant"
  finalityValue: number;   // numeric seconds, e.g., 0.65
  evmCompatible: boolean;
  language: string;        // e.g., "CosmWasm / Solidity (inEVM)"
  consensus: string;       // e.g., "Tendermint BFT"
  execution: string;       // e.g., "Parallel (Cosmos SDK)"
  database: string;        // e.g., "IAVL+ Tree"
  mainnetDate: string;     // e.g., "April 2023"
  funding: string;         // e.g., "$40M"
  gasCost: string;         // formatted, e.g., "$0.0003"
  gasCostValue: number;    // numeric USD, e.g., 0.0003
  tvl: string;             // formatted, e.g., "$55M"
  tvlValue: number;        // numeric USD millions, e.g., 55
  description: string;     // one-line summary
}

export interface FeatureCategory {
  category: string;        // e.g., "Execution Model"
  features: FeatureRow[];
}

export interface FeatureRow {
  name: string;            // e.g., "Parallel Execution"
  [chainId: string]: boolean | "partial" | string;
}

/**
 * Example chain entry — replace with researched data:
 */
export const EXAMPLE_CHAIN: ChainData = {
  id: "example",
  name: "Example Chain",
  color: "#836EF9",
  tps: "10,000",
  tpsValue: 10000,
  blockTime: "0.4s",
  blockTimeValue: 0.4,
  finality: "~0.8s",
  finalityValue: 0.8,
  evmCompatible: true,
  language: "Solidity",
  consensus: "Custom BFT",
  execution: "Parallel (Optimistic)",
  database: "Custom DB",
  mainnetDate: "2025",
  funding: "$244M",
  gasCost: "$0.001",
  gasCostValue: 0.001,
  tvl: "$100M",
  tvlValue: 100,
  description: "High-performance EVM-compatible L1 blockchain.",
};
