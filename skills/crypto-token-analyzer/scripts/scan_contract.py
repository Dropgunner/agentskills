#!/usr/bin/env python3
"""
Scan smart contract source code for rug pull indicators and security risks.
Analyzes verified contracts for dangerous patterns and functions.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple

import requests

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

# Dangerous function patterns
DANGEROUS_PATTERNS = {
    "critical": [
        {
            "name": "Hidden Mint",
            "pattern": r"function\s+\w*[Mm]int\w*\s*\([^)]*\)\s*(external|public|internal)",
            "description": "Owner can create unlimited tokens"
        },
        {
            "name": "Honeypot - Transfer Block",
            "pattern": r"require\s*\(\s*\w+\s*==\s*owner|require\s*\(\s*msg\.sender\s*==\s*owner",
            "description": "Transfer may be restricted to owner only"
        },
        {
            "name": "Blacklist Function",
            "pattern": r"function\s+\w*[Bb]lacklist\w*|mapping\s*\([^)]*\)\s*(public|private|internal)?\s*\w*[Bb]lacklist",
            "description": "Contract can blacklist addresses from trading"
        },
        {
            "name": "Self-Destruct",
            "pattern": r"selfdestruct\s*\(|suicide\s*\(",
            "description": "Contract can be destroyed, potentially stealing funds"
        },
        {
            "name": "Delegatecall",
            "pattern": r"\.delegatecall\s*\(",
            "description": "Can execute arbitrary code from external contract"
        }
    ],
    "high": [
        {
            "name": "Ownership Not Renounced",
            "pattern": r"function\s+renounceOwnership|Ownable|owner\s*\(\s*\)",
            "description": "Contract has owner privileges (check if renounced)"
        },
        {
            "name": "Pause Function",
            "pattern": r"function\s+pause\s*\(|whenNotPaused|Pausable",
            "description": "Trading can be paused by owner"
        },
        {
            "name": "Max Transaction Limit",
            "pattern": r"maxTx|_maxTxAmount|maxTransactionAmount",
            "description": "Transaction limits can trap buyers"
        },
        {
            "name": "High Tax/Fee",
            "pattern": r"(tax|fee|Tax|Fee)\s*=\s*(\d{2,})|setTax|setFee",
            "description": "Adjustable fees could be set extremely high"
        },
        {
            "name": "External Call in Transfer",
            "pattern": r"function\s+_transfer[^}]+\.call\{",
            "description": "External calls during transfer can be exploited"
        }
    ],
    "medium": [
        {
            "name": "Proxy Pattern",
            "pattern": r"Proxy|upgradeable|implementation|_implementation",
            "description": "Upgradeable contract - logic can be changed"
        },
        {
            "name": "Anti-Bot Measures",
            "pattern": r"antiBot|_isBot|botWallet|sniper",
            "description": "Anti-bot code can be used to block legitimate users"
        },
        {
            "name": "Cooldown Period",
            "pattern": r"cooldown|_cooldown|buyCooldown|sellCooldown",
            "description": "Trading cooldowns can prevent selling"
        },
        {
            "name": "Max Wallet Limit",
            "pattern": r"maxWallet|_maxWalletSize|maxWalletAmount",
            "description": "Wallet limits can restrict accumulation"
        }
    ],
    "info": [
        {
            "name": "Reflection/Rewards",
            "pattern": r"reflect|_rOwned|_tOwned|dividend",
            "description": "Reflection mechanism (complex tokenomics)"
        },
        {
            "name": "Liquidity Generation",
            "pattern": r"swapAndLiquify|addLiquidity|_swapTokensForEth",
            "description": "Auto-liquidity feature"
        },
        {
            "name": "Marketing Wallet",
            "pattern": r"marketingWallet|_marketingAddress|marketingFee",
            "description": "Marketing fee collection"
        }
    ]
}


def get_api_key(chain: str) -> str:
    """Get API key for the specified chain."""
    env_var = CHAIN_APIS[chain]["api_key_env"]
    return os.environ.get(env_var, "")


def fetch_contract_source(token_address: str, chain: str) -> Tuple[bool, str, str]:
    """Fetch contract source code."""
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
    
    if data.get("status") != "1" or not data.get("result"):
        return False, "", ""
    
    result = data["result"][0]
    source_code = result.get("SourceCode", "")
    contract_name = result.get("ContractName", "Unknown")
    
    # Handle multi-file contracts (JSON format)
    if source_code.startswith("{{"):
        try:
            # Remove extra braces and parse
            source_json = json.loads(source_code[1:-1])
            sources = source_json.get("sources", {})
            source_code = "\n".join(
                src.get("content", "") for src in sources.values()
            )
        except json.JSONDecodeError:
            pass
    elif source_code.startswith("{"):
        try:
            source_json = json.loads(source_code)
            sources = source_json.get("sources", {})
            source_code = "\n".join(
                src.get("content", "") for src in sources.values()
            )
        except json.JSONDecodeError:
            pass
    
    is_verified = bool(source_code)
    return is_verified, source_code, contract_name


def scan_for_patterns(source_code: str) -> Dict[str, List[Dict]]:
    """Scan source code for dangerous patterns."""
    findings = {
        "critical": [],
        "high": [],
        "medium": [],
        "info": []
    }
    
    for severity, patterns in DANGEROUS_PATTERNS.items():
        for pattern_info in patterns:
            matches = re.findall(pattern_info["pattern"], source_code, re.IGNORECASE)
            if matches:
                findings[severity].append({
                    "name": pattern_info["name"],
                    "description": pattern_info["description"],
                    "occurrences": len(matches),
                    "sample": matches[0] if matches else ""
                })
    
    return findings


def check_ownership_status(token_address: str, chain: str) -> Dict:
    """Check if contract ownership is renounced."""
    api_url = CHAIN_APIS[chain]["explorer"]
    api_key = get_api_key(chain)
    
    # Check for OwnershipTransferred events to zero address
    params = {
        "module": "logs",
        "action": "getLogs",
        "address": token_address,
        "topic0": "0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0",  # OwnershipTransferred
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    
    ownership_info = {
        "renounced": False,
        "current_owner": "Unknown",
        "transfer_events": 0
    }
    
    if data.get("status") == "1" and data.get("result"):
        events = data["result"]
        ownership_info["transfer_events"] = len(events)
        
        # Check last event for zero address
        if events:
            last_event = events[-1]
            topics = last_event.get("topics", [])
            if len(topics) >= 3:
                new_owner = topics[2]
                # Check if new owner is zero address
                if new_owner == "0x" + "0" * 64:
                    ownership_info["renounced"] = True
                    ownership_info["current_owner"] = "0x0000000000000000000000000000000000000000"
                else:
                    ownership_info["current_owner"] = "0x" + new_owner[-40:]
    
    return ownership_info


def calculate_risk_score(findings: Dict, is_verified: bool, ownership: Dict) -> Tuple[int, str]:
    """Calculate overall risk score (1-10)."""
    score = 0
    
    # Unverified contract is high risk
    if not is_verified:
        score += 4
    
    # Ownership not renounced
    if not ownership.get("renounced"):
        score += 2
    
    # Critical findings
    score += len(findings.get("critical", [])) * 3
    
    # High findings
    score += len(findings.get("high", [])) * 1.5
    
    # Medium findings
    score += len(findings.get("medium", [])) * 0.5
    
    # Cap at 10
    score = min(10, max(1, int(score)))
    
    # Risk level
    if score >= 8:
        level = "Critical"
    elif score >= 6:
        level = "High"
    elif score >= 4:
        level = "Medium"
    else:
        level = "Low"
    
    return score, level


def main():
    parser = argparse.ArgumentParser(description="Scan contract for rug pull indicators")
    parser.add_argument("--token", required=True, help="Token contract address")
    parser.add_argument("--chain", default="eth", choices=["eth", "bsc", "polygon"],
                        help="Blockchain network (default: eth)")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"Scanning contract: {args.token}")
    print(f"Chain: {args.chain}")
    print("-" * 50)
    
    try:
        # Fetch source code
        print("Fetching contract source...")
        is_verified, source_code, contract_name = fetch_contract_source(args.token, args.chain)
        
        if not is_verified:
            print("WARNING: Contract source code is NOT verified!")
            print("This is a significant red flag.")
        else:
            print(f"Contract verified: {contract_name}")
        
        # Scan for patterns
        findings = {}
        if source_code:
            print("Scanning for dangerous patterns...")
            findings = scan_for_patterns(source_code)
        
        # Check ownership
        print("Checking ownership status...")
        ownership = check_ownership_status(args.token, args.chain)
        
        # Calculate risk score
        risk_score, risk_level = calculate_risk_score(findings, is_verified, ownership)
        
        # Prepare result
        result = {
            "token": args.token,
            "chain": args.chain,
            "contract_name": contract_name,
            "is_verified": is_verified,
            "ownership": ownership,
            "findings": findings,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "scanned_at": datetime.utcnow().isoformat()
        }
        
        # Print summary
        print(f"\nContract Scan Summary:")
        print(f"  Contract: {contract_name}")
        print(f"  Verified: {'Yes' if is_verified else 'NO - RED FLAG'}")
        print(f"  Ownership renounced: {'Yes' if ownership['renounced'] else 'No'}")
        print(f"\nFindings:")
        print(f"  Critical: {len(findings.get('critical', []))}")
        print(f"  High: {len(findings.get('high', []))}")
        print(f"  Medium: {len(findings.get('medium', []))}")
        print(f"  Info: {len(findings.get('info', []))}")
        print(f"\nRisk Score: {risk_score}/10 ({risk_level})")
        
        # Print critical findings
        if findings.get("critical"):
            print("\nCRITICAL FINDINGS:")
            for finding in findings["critical"]:
                print(f"  - {finding['name']}: {finding['description']}")
        
        # Output
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nFull report saved to: {args.output}")
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
