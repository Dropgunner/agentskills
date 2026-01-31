#!/usr/bin/env python3
"""
Fetch token data from blockchain explorers.
Supports Ethereum, BSC, and Polygon networks.
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

# API endpoints for different chains
CHAIN_APIS = {
    "eth": {
        "explorer": "https://api.etherscan.io/api",
        "name": "Ethereum",
        "api_key_env": "ETHERSCAN_API_KEY"
    },
    "bsc": {
        "explorer": "https://api.bscscan.com/api",
        "name": "Binance Smart Chain",
        "api_key_env": "BSCSCAN_API_KEY"
    },
    "polygon": {
        "explorer": "https://api.polygonscan.com/api",
        "name": "Polygon",
        "api_key_env": "POLYGONSCAN_API_KEY"
    }
}


def get_api_key(chain: str) -> str:
    """Get API key for the specified chain."""
    env_var = CHAIN_APIS[chain]["api_key_env"]
    api_key = os.environ.get(env_var, "")
    if not api_key:
        print(f"Warning: {env_var} not set. Rate limits may apply.")
    return api_key


def fetch_token_info(token_address: str, chain: str) -> dict:
    """Fetch basic token information."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    # Get token supply
    params = {
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": token_address,
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    token_info = {
        "address": token_address,
        "chain": CHAIN_APIS[chain]["name"],
        "total_supply": data.get("result", "Unknown"),
        "fetched_at": datetime.utcnow().isoformat()
    }
    
    return token_info


def fetch_contract_info(token_address: str, chain: str) -> dict:
    """Fetch contract source code and verification status."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": token_address,
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    result = data.get("result", [{}])[0] if data.get("result") else {}
    
    contract_info = {
        "verified": bool(result.get("SourceCode")),
        "contract_name": result.get("ContractName", "Unknown"),
        "compiler_version": result.get("CompilerVersion", "Unknown"),
        "optimization_used": result.get("OptimizationUsed", "Unknown"),
        "source_code": result.get("SourceCode", ""),
        "abi": result.get("ABI", "")
    }
    
    return contract_info


def fetch_creation_info(token_address: str, chain: str) -> dict:
    """Fetch contract creation transaction info."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    params = {
        "module": "contract",
        "action": "getcontractcreation",
        "contractaddresses": token_address,
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    result = data.get("result", [{}])[0] if data.get("result") else {}
    
    creation_info = {
        "creator": result.get("contractCreator", "Unknown"),
        "creation_tx": result.get("txHash", "Unknown")
    }
    
    return creation_info


def main():
    parser = argparse.ArgumentParser(description="Fetch token data from blockchain explorers")
    parser.add_argument("--token", required=True, help="Token contract address")
    parser.add_argument("--chain", required=True, choices=["eth", "bsc", "polygon"],
                        help="Blockchain network")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"Fetching data for token: {args.token}")
    print(f"Chain: {CHAIN_APIS[args.chain]['name']}")
    print("-" * 50)
    
    try:
        # Fetch all data
        token_info = fetch_token_info(args.token, args.chain)
        contract_info = fetch_contract_info(args.token, args.chain)
        creation_info = fetch_creation_info(args.token, args.chain)
        
        # Combine results
        result = {
            "token": token_info,
            "contract": contract_info,
            "creation": creation_info
        }
        
        # Output
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Data saved to: {args.output}")
        else:
            print(json.dumps(result, indent=2))
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
