# Blockchain API Reference

## Table of Contents
1. [Etherscan API](#etherscan-api)
2. [BscScan API](#bscscan-api)
3. [PolygonScan API](#polygonscan-api)
4. [Rate Limits](#rate-limits)
5. [API Key Setup](#api-key-setup)

## Etherscan API

Base URL: `https://api.etherscan.io/api`

### Token Information

```python
# Get token total supply
params = {
    "module": "stats",
    "action": "tokensupply",
    "contractaddress": "<token_address>",
    "apikey": "<api_key>"
}

# Get token holder list (Pro API required)
params = {
    "module": "token",
    "action": "tokenholderlist",
    "contractaddress": "<token_address>",
    "page": 1,
    "offset": 100,
    "apikey": "<api_key>"
}
```

### Contract Information

```python
# Get contract source code
params = {
    "module": "contract",
    "action": "getsourcecode",
    "address": "<contract_address>",
    "apikey": "<api_key>"
}

# Get contract creation info
params = {
    "module": "contract",
    "action": "getcontractcreation",
    "contractaddresses": "<contract_address>",
    "apikey": "<api_key>"
}

# Get contract ABI
params = {
    "module": "contract",
    "action": "getabi",
    "address": "<contract_address>",
    "apikey": "<api_key>"
}
```

### Transaction History

```python
# Get token transfers
params = {
    "module": "account",
    "action": "tokentx",
    "contractaddress": "<token_address>",
    "address": "<wallet_address>",  # Optional
    "page": 1,
    "offset": 100,
    "sort": "desc",
    "apikey": "<api_key>"
}

# Get internal transactions
params = {
    "module": "account",
    "action": "txlistinternal",
    "address": "<address>",
    "startblock": 0,
    "endblock": 99999999,
    "apikey": "<api_key>"
}
```

### Event Logs

```python
# Get logs by topic
params = {
    "module": "logs",
    "action": "getLogs",
    "address": "<contract_address>",
    "topic0": "<event_signature_hash>",
    "fromBlock": 0,
    "toBlock": "latest",
    "apikey": "<api_key>"
}
```

## BscScan API

Base URL: `https://api.bscscan.com/api`

Same endpoints as Etherscan with identical parameters.

### BNB-Specific Endpoints

```python
# Get BNB balance
params = {
    "module": "account",
    "action": "balance",
    "address": "<address>",
    "apikey": "<api_key>"
}

# Get BEP-20 token transfers
params = {
    "module": "account",
    "action": "tokentx",
    "contractaddress": "<bep20_token>",
    "address": "<wallet>",
    "apikey": "<api_key>"
}
```

## PolygonScan API

Base URL: `https://api.polygonscan.com/api`

Same endpoints as Etherscan with identical parameters.

## Rate Limits

| Tier | Requests/Second | Daily Limit |
|------|-----------------|-------------|
| Free | 5 | 100,000 |
| Standard | 10 | 500,000 |
| Pro | 20 | Unlimited |

### Handling Rate Limits

```python
import time
from functools import wraps

def rate_limit(calls_per_second=5):
    """Decorator to enforce rate limiting."""
    min_interval = 1.0 / calls_per_second
    last_call = [0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def api_call(url, params):
    return requests.get(url, params=params)
```

## API Key Setup

### Environment Variables

Set API keys as environment variables:

```bash
# Ethereum
export ETHERSCAN_API_KEY="your_etherscan_key"

# BSC
export BSCSCAN_API_KEY="your_bscscan_key"

# Polygon
export POLYGONSCAN_API_KEY="your_polygonscan_key"
```

### Obtaining API Keys

1. **Etherscan**: Register at https://etherscan.io/register
2. **BscScan**: Register at https://bscscan.com/register
3. **PolygonScan**: Register at https://polygonscan.com/register

Free tier provides sufficient access for most analysis tasks.

## Common Event Signatures

| Event | Topic0 Hash |
|-------|-------------|
| Transfer | `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` |
| Approval | `0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925` |
| OwnershipTransferred | `0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0` |
| Swap (Uniswap V2) | `0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822` |
