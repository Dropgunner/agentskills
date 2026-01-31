# Solidity Best Practices

## Compiler Settings

### Pragma Version
```solidity
// GOOD - Locked version
pragma solidity 0.8.19;

// AVOID - Floating version
pragma solidity ^0.8.0;
```

### Optimizer Settings
- Enable optimizer for production: `--optimize --optimize-runs 200`
- Higher runs = cheaper execution, larger bytecode
- Lower runs = cheaper deployment, more expensive execution

## Code Organization

### Contract Structure Order
1. Type declarations (enums, structs)
2. State variables
3. Events
4. Errors (custom errors preferred)
5. Modifiers
6. Constructor
7. Receive/fallback functions
8. External functions
9. Public functions
10. Internal functions
11. Private functions

### Function Visibility Order
```solidity
contract Example {
    // External first
    function externalFunc() external {}
    
    // Then public
    function publicFunc() public {}
    
    // Then internal
    function internalFunc() internal {}
    
    // Then private
    function privateFunc() private {}
}
```

## Security Patterns

### Checks-Effects-Interactions
```solidity
function withdraw(uint256 amount) external {
    // CHECKS
    require(balances[msg.sender] >= amount, "Insufficient balance");
    
    // EFFECTS
    balances[msg.sender] -= amount;
    
    // INTERACTIONS
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### Pull Over Push
```solidity
// AVOID - Push pattern
function distribute(address[] calldata recipients) external {
    for (uint i = 0; i < recipients.length; i++) {
        payable(recipients[i]).transfer(amount);  // Can fail, blocking all
    }
}

// GOOD - Pull pattern
mapping(address => uint256) public pendingWithdrawals;

function withdraw() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    payable(msg.sender).transfer(amount);
}
```

### Reentrancy Guard
```solidity
abstract contract ReentrancyGuard {
    uint256 private constant _NOT_ENTERED = 1;
    uint256 private constant _ENTERED = 2;
    uint256 private _status;

    constructor() {
        _status = _NOT_ENTERED;
    }

    modifier nonReentrant() {
        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
        _status = _ENTERED;
        _;
        _status = _NOT_ENTERED;
    }
}
```

## Access Control

### Two-Step Ownership Transfer
```solidity
address public owner;
address public pendingOwner;

function transferOwnership(address newOwner) external onlyOwner {
    pendingOwner = newOwner;
}

function acceptOwnership() external {
    require(msg.sender == pendingOwner, "Not pending owner");
    owner = pendingOwner;
    pendingOwner = address(0);
}
```

### Role-Based Access
```solidity
// Use OpenZeppelin AccessControl
import "@openzeppelin/contracts/access/AccessControl.sol";

contract MyContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        // ...
    }
}
```

## Error Handling

### Custom Errors (Gas Efficient)
```solidity
// GOOD - Custom errors (Solidity 0.8.4+)
error InsufficientBalance(uint256 available, uint256 required);
error Unauthorized(address caller);

function withdraw(uint256 amount) external {
    if (balances[msg.sender] < amount) {
        revert InsufficientBalance(balances[msg.sender], amount);
    }
}

// AVOID - String errors (expensive)
require(balances[msg.sender] >= amount, "Insufficient balance");
```

### Return Value Checks
```solidity
// GOOD - Check return values
(bool success, bytes memory data) = target.call(callData);
require(success, "Call failed");

// For ERC-20 transfers
IERC20(token).safeTransfer(to, amount);  // Use SafeERC20
```

## Gas Optimization

### Storage vs Memory
```solidity
// EXPENSIVE - Multiple storage reads
function bad(uint256[] storage arr) internal {
    for (uint i = 0; i < arr.length; i++) {  // arr.length read each iteration
        total += arr[i];  // Storage read each iteration
    }
}

// GOOD - Cache in memory
function good(uint256[] storage arr) internal {
    uint256 len = arr.length;
    uint256[] memory cached = arr;
    for (uint i = 0; i < len; i++) {
        total += cached[i];
    }
}
```

### Unchecked Arithmetic
```solidity
// When overflow is impossible
function increment(uint256 i) internal pure returns (uint256) {
    unchecked {
        return i + 1;  // Saves gas when overflow is impossible
    }
}
```

### Packing Storage
```solidity
// BAD - 3 storage slots
struct Bad {
    uint256 a;  // Slot 0
    uint128 b;  // Slot 1
    uint256 c;  // Slot 2
    uint128 d;  // Slot 3
}

// GOOD - 2 storage slots
struct Good {
    uint256 a;  // Slot 0
    uint256 c;  // Slot 1
    uint128 b;  // Slot 2 (packed)
    uint128 d;  // Slot 2 (packed)
}
```

## Events

### Emit Events for State Changes
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);
event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

function transfer(address to, uint256 amount) external {
    // ... logic ...
    emit Transfer(msg.sender, to, amount);
}
```

### Index Important Parameters
- Index up to 3 parameters for efficient filtering
- Index addresses and IDs, not amounts

## Testing Requirements

### Minimum Coverage
- 100% line coverage for critical functions
- Branch coverage for all conditionals
- Fuzz testing for arithmetic operations
- Invariant testing for protocol properties

### Test Categories
1. Unit tests (individual functions)
2. Integration tests (contract interactions)
3. Fuzz tests (random inputs)
4. Invariant tests (protocol properties)
5. Fork tests (mainnet state)
