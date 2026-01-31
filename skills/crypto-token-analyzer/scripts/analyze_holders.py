#!/usr/bin/env python3
"""
Analyze token holder distribution for concentration risks.
"""

import argparse
import json
import os
import sys
from typing import List, Dict

import requests

# API endpoints
CHAIN_APIS = {
    "eth": {
        "explorer": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY"
    },
    "bsc": {
        "explorer": "https://api.bscscan.com/api",
        "api_key_env": "BSCSCAN_API_KEY"
    },
    "polygon": {
        "explorer": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY"
    }
}


def get_api_key(chain: str) -> str:
    """Get API key for the specified chain."""
    env_var = CHAIN_APIS[chain]["api_key_env"]
    return os.environ.get(env_var, "")


def fetch_top_holders(token_address: str, chain: str, limit: int = 100) -> List[Dict]:
    """
    Fetch top token holders.
    Note: This requires a paid API plan on most explorers.
    Falls back to transfer analysis if not available.
    """
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    # Try to get token holders (may require paid API)
    params = {
        "module": "token",
        "action": "tokenholderlist",
        "contractaddress": token_address,
        "page": 1,
        "offset": limit,
        "apikey": api_key
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=30)
        data = response.json()
        
        if data.get("status") == "1" and data.get("result"):
            holders = []
            for holder in data["result"]:
                holders.append({
                    "address": holder.get("TokenHolderAddress", ""),
                    "balance": holder.get("TokenHolderQuantity", "0"),
                    "percentage": 0  # Will be calculated
                })
            return holders
    except Exception:
        pass
    
    # Fallback: Analyze from transfers
    print("Note: Direct holder list not available. Analyzing from transfers...")
    return analyze_from_transfers(token_address, chain)


def analyze_from_transfers(token_address: str, chain: str) -> List[Dict]:
    """Analyze holder distribution from transfer events."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": token_address,
        "page": 1,
        "offset": 1000,
        "sort": "desc",
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    if data.get("status") != "1":
        return []
    
    # Build holder balances from transfers
    balances = {}
    for tx in data.get("result", []):
        from_addr = tx.get("from", "").lower()
        to_addr = tx.get("to", "").lower()
        value = int(tx.get("value", 0))
        
        if from_addr:
            balances[from_addr] = balances.get(from_addr, 0) - value
        if to_addr:
            balances[to_addr] = balances.get(to_addr, 0) + value
    
    # Filter positive balances and sort
    holders = [
        {"address": addr, "balance": str(bal), "percentage": 0}
        for addr, bal in balances.items()
        if bal > 0
    ]
    holders.sort(key=lambda x: int(x["balance"]), reverse=True)
    
    return holders[:100]


def calculate_concentration_metrics(holders: List[Dict]) -> Dict:
    """Calculate holder concentration metrics."""
    if not holders:
        return {
            "total_holders": 0,
            "top_holder_pct": 0,
            "top_10_pct": 0,
            "top_50_pct": 0,
            "gini_coefficient": 0,
            "concentration_risk": "Unknown"
        }
    
    # Calculate total supply from holders
    total_supply = sum(int(h["balance"]) for h in holders)
    
    if total_supply == 0:
        return {
            "total_holders": len(holders),
            "top_holder_pct": 0,
            "top_10_pct": 0,
            "top_50_pct": 0,
            "gini_coefficient": 0,
            "concentration_risk": "Unknown"
        }
    
    # Calculate percentages
    for holder in holders:
        holder["percentage"] = (int(holder["balance"]) / total_supply) * 100
    
    # Top holder percentage
    top_holder_pct = holders[0]["percentage"] if holders else 0
    
    # Top 10 holders percentage
    top_10_pct = sum(h["percentage"] for h in holders[:10])
    
    # Top 50 holders percentage
    top_50_pct = sum(h["percentage"] for h in holders[:50])
    
    # Calculate Gini coefficient (measure of inequality)
    n = len(holders)
    balances = [int(h["balance"]) for h in holders]
    balances.sort()
    
    if n > 1 and sum(balances) > 0:
        cumulative = 0
        gini_sum = 0
        for i, balance in enumerate(balances):
            cumulative += balance
            gini_sum += cumulative
        gini = (2 * gini_sum) / (n * sum(balances)) - (n + 1) / n
    else:
        gini = 0
    
    # Determine concentration risk
    if top_holder_pct > 50:
        risk = "Critical"
    elif top_holder_pct > 20 or top_10_pct > 80:
        risk = "High"
    elif top_10_pct > 60:
        risk = "Medium"
    else:
        risk = "Low"
    
    return {
        "total_holders": len(holders),
        "top_holder_pct": round(top_holder_pct, 2),
        "top_10_pct": round(top_10_pct, 2),
        "top_50_pct": round(top_50_pct, 2),
        "gini_coefficient": round(gini, 4),
        "concentration_risk": risk
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze token holder distribution")
    parser.add_argument("--token", required=True, help="Token contract address")
    parser.add_argument("--chain", default="eth", choices=["eth", "bsc", "polygon"],
                        help="Blockchain network (default: eth)")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"Analyzing holders for: {args.token}")
    print("-" * 50)
    
    try:
        # Fetch holders
        holders = fetch_top_holders(args.token, args.chain)
        
        # Calculate metrics
        metrics = calculate_concentration_metrics(holders)
        
        # Prepare result
        result = {
            "token": args.token,
            "chain": args.chain,
            "metrics": metrics,
            "top_holders": holders[:20]  # Include top 20 in output
        }
        
        # Print summary
        print(f"\nHolder Analysis Summary:")
        print(f"  Total holders analyzed: {metrics['total_holders']}")
        print(f"  Top holder: {metrics['top_holder_pct']:.2f}%")
        print(f"  Top 10 holders: {metrics['top_10_pct']:.2f}%")
        print(f"  Gini coefficient: {metrics['gini_coefficient']:.4f}")
        print(f"  Concentration risk: {metrics['concentration_risk']}")
        
        # Output
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nFull data saved to: {args.output}")
        else:
            print("\nTop 10 Holders:")
            for i, holder in enumerate(holders[:10], 1):
                print(f"  {i}. {holder['address'][:10]}...{holder['address'][-6:]}: {holder['percentage']:.2f}%")
                
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
