# DEX API Reference

## Table of Contents
1. [DexScreener API](#dexscreener-api)
2. [DexTools API](#dextools-api)
3. [Uniswap Subgraph](#uniswap-subgraph)
4. [PancakeSwap Subgraph](#pancakeswap-subgraph)

## DexScreener API

Base URL: `https://api.dexscreener.com`

Free, no API key required. Best for quick token lookups.

### Get Token Pairs

```python
import requests

# Search by token address
def get_token_pairs(token_address: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    response = requests.get(url)
    return response.json()

# Response structure
{
    "pairs": [
        {
            "chainId": "ethereum",
            "dexId": "uniswap",
            "pairAddress": "0x...",
            "baseToken": {
                "address": "0x...",
                "name": "Token Name",
                "symbol": "TKN"
            },
            "quoteToken": {
                "address": "0x...",
                "name": "Wrapped Ether",
                "symbol": "WETH"
            },
            "priceNative": "0.0001234",
            "priceUsd": "0.25",
            "liquidity": {
                "usd": 150000,
                "base": 1000000,
                "quote": 75
            },
            "volume": {
                "h24": 50000,
                "h6": 12000,
                "h1": 2000
            },
            "txns": {
                "h24": {"buys": 150, "sells": 120}
            }
        }
    ]
}
```

### Search Pairs

```python
# Search by query
def search_pairs(query: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    response = requests.get(url)
    return response.json()
```

### Get Pair by Address

```python
# Get specific pair
def get_pair(chain: str, pair_address: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pair_address}"
    response = requests.get(url)
    return response.json()
```

## DexTools API

Base URL: `https://api.dextools.io/v1`

Requires API key for full access.

### Get Token Info

```python
def get_token_info(chain: str, token_address: str, api_key: str) -> dict:
    url = f"https://api.dextools.io/v1/token"
    headers = {"X-API-Key": api_key}
    params = {
        "chain": chain,  # "ether", "bsc", "polygon"
        "address": token_address
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### Get Token Score

```python
def get_token_score(chain: str, token_address: str, api_key: str) -> dict:
    url = f"https://api.dextools.io/v1/token/score"
    headers = {"X-API-Key": api_key}
    params = {
        "chain": chain,
        "address": token_address
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Response includes:
# - dextScore: Overall score (0-99)
# - holders: Holder analysis
# - liquidity: Liquidity analysis
# - contract: Contract analysis
```

## Uniswap Subgraph

GraphQL endpoint for Uniswap V2/V3 data.

### V2 Subgraph

```python
import requests

UNISWAP_V2_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"

def query_uniswap_v2(query: str) -> dict:
    response = requests.post(
        UNISWAP_V2_SUBGRAPH,
        json={"query": query}
    )
    return response.json()

# Get pair by token
query = '''
{
  pairs(where: {token0: "<token_address>"}, first: 10) {
    id
    token0 {
      symbol
      name
    }
    token1 {
      symbol
      name
    }
    reserve0
    reserve1
    reserveUSD
    volumeUSD
    txCount
  }
}
'''
```

### V3 Subgraph

```python
UNISWAP_V3_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# Get pool data
query = '''
{
  pools(where: {token0: "<token_address>"}, first: 10) {
    id
    token0 {
      symbol
      decimals
    }
    token1 {
      symbol
      decimals
    }
    liquidity
    sqrtPrice
    tick
    volumeUSD
    txCount
  }
}
'''
```

## PancakeSwap Subgraph

```python
PANCAKESWAP_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2"

# Get pair data
query = '''
{
  pairs(where: {token0: "<token_address>"}, first: 10) {
    id
    token0 {
      symbol
      name
    }
    token1 {
      symbol
      name
    }
    reserve0
    reserve1
    reserveUSD
    volumeUSD
  }
}
'''
```

## Liquidity Analysis Helper

```python
def analyze_liquidity(token_address: str) -> dict:
    """Comprehensive liquidity analysis using DexScreener."""
    data = get_token_pairs(token_address)
    
    if not data.get("pairs"):
        return {"status": "No liquidity found", "risk": "Critical"}
    
    total_liquidity = sum(p.get("liquidity", {}).get("usd", 0) for p in data["pairs"])
    total_volume_24h = sum(p.get("volume", {}).get("h24", 0) for p in data["pairs"])
    
    # Risk assessment
    if total_liquidity < 10000:
        risk = "Critical"
    elif total_liquidity < 50000:
        risk = "High"
    elif total_liquidity < 200000:
        risk = "Medium"
    else:
        risk = "Low"
    
    return {
        "total_liquidity_usd": total_liquidity,
        "total_volume_24h": total_volume_24h,
        "pair_count": len(data["pairs"]),
        "main_dex": data["pairs"][0].get("dexId") if data["pairs"] else None,
        "liquidity_risk": risk
    }
```
