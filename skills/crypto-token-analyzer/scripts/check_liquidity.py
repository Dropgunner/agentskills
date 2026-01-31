#!/usr/bin/env python3
"""
Check token liquidity health across DEX pools.
Analyzes liquidity depth, lock status, and trading volume.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests

# DEX Factory addresses for LP detection
DEX_FACTORIES = {
    "eth": {
        "uniswap_v2": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "uniswap_v3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "sushiswap": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    },
    "bsc": {
        "pancakeswap_v2": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        "pancakeswap_v3": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"
    },
    "polygon": {
        "quickswap": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",
        "sushiswap": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4"
    }
}

# Common wrapped native tokens
WRAPPED_NATIVE = {
    "eth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
    "polygon": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"  # WMATIC
}

# Stablecoins
STABLECOINS = {
    "eth": [
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "0x6B175474E89094C44Da98b954EescdeCB5BE3830"   # DAI
    ],
    "bsc": [
        "0x55d398326f99059fF775485246999027B3197955",  # USDT
        "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"   # USDC
    ],
    "polygon": [
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT
        "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"   # USDC
    ]
}

# Chain API configs
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


def find_liquidity_pairs(token_address: str, chain: str) -> List[Dict]:
    """Find liquidity pairs for the token."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    # Search for token transfers to identify LP contracts
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": token_address,
        "page": 1,
        "offset": 500,
        "sort": "desc",
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    if data.get("status") != "1":
        return []
    
    # Identify potential LP contracts (contracts that receive tokens)
    lp_candidates = {}
    for tx in data.get("result", []):
        to_addr = tx.get("to", "").lower()
        if to_addr and to_addr not in lp_candidates:
            lp_candidates[to_addr] = {
                "address": to_addr,
                "tx_count": 0,
                "total_value": 0
            }
        if to_addr:
            lp_candidates[to_addr]["tx_count"] += 1
            lp_candidates[to_addr]["total_value"] += int(tx.get("value", 0))
    
    # Filter for likely LP contracts (high transaction count)
    lp_pairs = [
        lp for lp in lp_candidates.values()
        if lp["tx_count"] >= 5
    ]
    lp_pairs.sort(key=lambda x: x["total_value"], reverse=True)
    
    return lp_pairs[:10]


def check_lp_lock_status(lp_address: str, chain: str) -> Dict:
    """Check if LP tokens are locked."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    # Known locker contracts
    lockers = {
        "eth": [
            "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",  # Unicrypt
            "0xDba68f07d1b7Ca219f78ae8582C213d975c25cAf"   # Team Finance
        ],
        "bsc": [
            "0xC765bddB93b0D1c1A88282BA0fa6B2d00E3e0c83",  # PinkLock
            "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE"   # DxLock
        ],
        "polygon": [
            "0xAA3d85aD9D128e0a4466F7B0d6a8D4c3dF8d9E8F"   # QuickLock
        ]
    }
    
    # Check LP token transfers to locker contracts
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": lp_address,
        "page": 1,
        "offset": 100,
        "sort": "desc",
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    lock_info = {
        "is_locked": False,
        "locker_contract": None,
        "locked_amount": 0,
        "lock_percentage": 0
    }
    
    if data.get("status") != "1":
        return lock_info
    
    chain_lockers = [l.lower() for l in lockers.get(chain, [])]
    
    for tx in data.get("result", []):
        to_addr = tx.get("to", "").lower()
        if to_addr in chain_lockers:
            lock_info["is_locked"] = True
            lock_info["locker_contract"] = to_addr
            lock_info["locked_amount"] += int(tx.get("value", 0))
    
    return lock_info


def estimate_liquidity_value(token_address: str, chain: str) -> Dict:
    """Estimate total liquidity value in USD."""
    # This would typically use a price oracle or DEX API
    # For now, we return a placeholder that indicates manual verification needed
    return {
        "estimated_usd": "Requires price oracle",
        "native_token_reserve": "Unknown",
        "token_reserve": "Unknown",
        "note": "Use DEX analytics (DexTools, DexScreener) for accurate values"
    }


def assess_liquidity_risk(lp_pairs: List[Dict], lock_status: Dict) -> str:
    """Assess overall liquidity risk."""
    if not lp_pairs:
        return "Critical - No liquidity found"
    
    if not lock_status.get("is_locked"):
        return "High - Liquidity not locked"
    
    if lock_status.get("lock_percentage", 0) < 80:
        return "Medium - Partial liquidity lock"
    
    return "Low - Liquidity appears locked"


def main():
    parser = argparse.ArgumentParser(description="Check token liquidity health")
    parser.add_argument("--token", required=True, help="Token contract address")
    parser.add_argument("--chain", default="eth", choices=["eth", "bsc", "polygon"],
                        help="Blockchain network (default: eth)")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"Checking liquidity for: {args.token}")
    print(f"Chain: {args.chain}")
    print("-" * 50)
    
    try:
        # Find liquidity pairs
        print("Finding liquidity pairs...")
        lp_pairs = find_liquidity_pairs(args.token, args.chain)
        
        # Check lock status for main LP
        lock_status = {"is_locked": False}
        if lp_pairs:
            print(f"Found {len(lp_pairs)} potential LP pairs")
            print("Checking lock status...")
            lock_status = check_lp_lock_status(lp_pairs[0]["address"], args.chain)
        
        # Estimate liquidity value
        liquidity_value = estimate_liquidity_value(args.token, args.chain)
        
        # Assess risk
        risk_level = assess_liquidity_risk(lp_pairs, lock_status)
        
        # Prepare result
        result = {
            "token": args.token,
            "chain": args.chain,
            "liquidity_pairs": lp_pairs,
            "lock_status": lock_status,
            "liquidity_value": liquidity_value,
            "risk_assessment": risk_level,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Print summary
        print(f"\nLiquidity Analysis Summary:")
        print(f"  LP pairs found: {len(lp_pairs)}")
        print(f"  Liquidity locked: {'Yes' if lock_status['is_locked'] else 'No'}")
        if lock_status.get("locker_contract"):
            print(f"  Locker: {lock_status['locker_contract'][:20]}...")
        print(f"  Risk level: {risk_level}")
        
        # Output
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nFull data saved to: {args.output}")
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
