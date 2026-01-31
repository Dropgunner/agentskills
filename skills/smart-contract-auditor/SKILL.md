---
name: smart-contract-auditor
description: Security audit workflows for Solidity and Vyper smart contracts. Use when reviewing contract code for vulnerabilities, performing security assessments, or preparing audit reports. Covers common attack vectors, gas optimization, and best practices.
license: MIT
metadata:
  author: Prayer
  version: "1.0"
---

# Smart Contract Auditor

Comprehensive security audit workflow for EVM-compatible smart contracts.

## When to Use

- Reviewing smart contract code before deployment
- Auditing third-party contracts before integration
- Preparing formal security audit reports
- Identifying vulnerabilities in DeFi protocols
- Assessing gas optimization opportunities

## Audit Workflow

A thorough audit follows these sequential steps:

1. **Scope definition** - Identify contracts and functionality to audit
2. **Static analysis** - Run automated tools (Slither, Mythril)
3. **Manual review** - Line-by-line code inspection
4. **Vulnerability testing** - Test identified issues
5. **Report generation** - Document findings and recommendations

## Quick Start

```bash
# Run static analysis
python scripts/run_slither.py --contract <path_to_contract.sol>

# Check for common vulnerabilities
python scripts/vulnerability_scan.py --contract <path_to_contract.sol>

# Generate audit report
python scripts/generate_report.py --contract <path> --findings <findings.json>
```

## Vulnerability Categories

### Critical Vulnerabilities

| Vulnerability | Description | Impact |
|--------------|-------------|--------|
| Reentrancy | External call before state update | Fund theft |
| Access Control | Missing/incorrect modifiers | Unauthorized actions |
| Integer Overflow | Unchecked arithmetic (pre-0.8.0) | Logic manipulation |
| Delegatecall Injection | Arbitrary code execution | Complete compromise |
| Self-destruct | Unprotected contract destruction | Fund loss |

### High Vulnerabilities

| Vulnerability | Description | Impact |
|--------------|-------------|--------|
| Front-running | Transaction ordering exploitation | Value extraction |
| Oracle Manipulation | Price feed attacks | Incorrect valuations |
| Flash Loan Attacks | Uncollateralized borrowing exploits | Protocol drain |
| Signature Replay | Reusing signed messages | Unauthorized transactions |
| Denial of Service | Blocking contract functionality | Service disruption |

### Medium Vulnerabilities

| Vulnerability | Description | Impact |
|--------------|-------------|--------|
| Centralization Risks | Single points of failure | Trust assumptions |
| Timestamp Dependence | Block.timestamp manipulation | Minor exploitation |
| Gas Griefing | Excessive gas consumption | Economic attacks |
| Floating Pragma | Inconsistent compiler versions | Unexpected behavior |

### Low/Informational

| Issue | Description |
|-------|-------------|
| Missing Events | No event emission for state changes |
| Magic Numbers | Hardcoded values without explanation |
| Code Complexity | Overly complex logic |
| Documentation | Missing or outdated comments |

## Manual Review Checklist

### Access Control
- [ ] All external/public functions have appropriate modifiers
- [ ] Owner privileges are clearly documented
- [ ] Role-based access is properly implemented
- [ ] Ownership transfer is two-step

### State Management
- [ ] State changes follow checks-effects-interactions pattern
- [ ] Reentrancy guards on vulnerable functions
- [ ] Storage variables properly initialized
- [ ] No uninitialized storage pointers

### External Calls
- [ ] Return values checked for low-level calls
- [ ] Reentrancy protection in place
- [ ] Gas limits considered for external calls
- [ ] Untrusted contracts handled safely

### Arithmetic
- [ ] SafeMath used (pre-0.8.0) or unchecked blocks justified
- [ ] Division by zero prevented
- [ ] Rounding handled correctly
- [ ] Token decimals accounted for

### Token Handling
- [ ] ERC-20 return values checked
- [ ] Fee-on-transfer tokens considered
- [ ] Rebasing tokens handled
- [ ] Approval race condition mitigated

## Report Template

```markdown
# Smart Contract Security Audit Report

## Executive Summary
[Brief overview of audit scope, methodology, and key findings]

## Audit Details
- **Client**: [Name]
- **Contract(s)**: [List of contracts]
- **Commit Hash**: [Git commit]
- **Audit Period**: [Start - End dates]
- **Auditor(s)**: [Names]

## Scope
[Description of what was audited and any limitations]

## Methodology
1. Static Analysis (Slither, Mythril)
2. Manual Code Review
3. Test Coverage Analysis
4. Attack Vector Testing

## Findings Summary

| Severity | Count |
|----------|-------|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |
| Informational | X |

## Detailed Findings

### [SEVERITY-001] Finding Title

**Severity**: Critical/High/Medium/Low/Info

**Location**: `Contract.sol:L123-L145`

**Description**:
[Detailed description of the vulnerability]

**Impact**:
[Potential consequences if exploited]

**Proof of Concept**:
```solidity
// Attack code or scenario
```

**Recommendation**:
[Specific fix recommendation]

**Status**: [Open/Acknowledged/Fixed]

---

## Recommendations
[General recommendations for improving security]

## Conclusion
[Summary and overall assessment]
```

## Tool Integration

### Slither (Static Analysis)
```bash
# Install
pip install slither-analyzer

# Run analysis
slither contract.sol --json output.json
```

### Mythril (Symbolic Execution)
```bash
# Install
pip install mythril

# Analyze contract
myth analyze contract.sol
```

### Foundry (Testing)
```bash
# Run tests with coverage
forge test --coverage

# Fuzz testing
forge test --fuzz-runs 10000
```

## References

For detailed guidance:
- **Vulnerability Patterns**: See [references/vulnerability-patterns.md](references/vulnerability-patterns.md)
- **Solidity Best Practices**: See [references/solidity-best-practices.md](references/solidity-best-practices.md)
- **Gas Optimization**: See [references/gas-optimization.md](references/gas-optimization.md)

## Common Attack Patterns

### Reentrancy Attack
```solidity
// VULNERABLE
function withdraw() external {
    uint256 balance = balances[msg.sender];
    (bool success, ) = msg.sender.call{value: balance}("");
    require(success);
    balances[msg.sender] = 0;  // State update AFTER external call
}

// SECURE
function withdraw() external nonReentrant {
    uint256 balance = balances[msg.sender];
    balances[msg.sender] = 0;  // State update BEFORE external call
    (bool success, ) = msg.sender.call{value: balance}("");
    require(success);
}
```

### Access Control Bypass
```solidity
// VULNERABLE
function setOwner(address newOwner) external {
    owner = newOwner;  // No access control!
}

// SECURE
function setOwner(address newOwner) external onlyOwner {
    require(newOwner != address(0), "Invalid address");
    owner = newOwner;
}
```
