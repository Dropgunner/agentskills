#!/usr/bin/env python3
"""
Generate a formatted security audit report from findings.
Outputs Markdown format suitable for professional delivery.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


REPORT_TEMPLATE = """# Smart Contract Security Audit Report

## Executive Summary

{executive_summary}

## Audit Details

| Field | Value |
|-------|-------|
| **Contract(s)** | {contracts} |
| **Audit Date** | {audit_date} |
| **Auditor** | {auditor} |
| **Commit/Version** | {commit} |

## Scope

{scope}

## Methodology

The audit was conducted using a combination of:

1. **Static Analysis**: Automated tools (Slither, custom scanners) to identify common vulnerability patterns
2. **Manual Review**: Line-by-line code inspection focusing on business logic and security
3. **Pattern Matching**: Comparison against known vulnerability patterns and attack vectors

## Findings Summary

| Severity | Count |
|----------|-------|
| Critical | {critical_count} |
| High | {high_count} |
| Medium | {medium_count} |
| Low | {low_count} |
| Informational | {info_count} |

**Total Findings: {total_count}**

## Detailed Findings

{detailed_findings}

## Recommendations

{recommendations}

## Conclusion

{conclusion}

---

*This report was generated on {generation_date}.*
"""

FINDING_TEMPLATE = """### [{severity_upper}-{index:03d}] {title}

**Severity**: {severity}

**Location**: `{location}`

**Description**:
{description}

**Impact**:
{impact}

**Recommendation**:
{recommendation}

**Status**: {status}

---
"""


def load_findings(findings_path: str) -> Dict:
    """Load findings from JSON file."""
    with open(findings_path, "r") as f:
        return json.load(f)


def count_by_severity(findings: List[Dict]) -> Dict[str, int]:
    """Count findings by severity."""
    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0
    }
    
    for finding in findings:
        severity = finding.get("severity", "informational").lower()
        if severity in counts:
            counts[severity] += 1
    
    return counts


def generate_executive_summary(findings: List[Dict], counts: Dict[str, int]) -> str:
    """Generate executive summary based on findings."""
    total = sum(counts.values())
    
    if counts["critical"] > 0:
        risk_level = "**Critical**"
        assessment = "The audit identified critical vulnerabilities that require immediate attention before deployment."
    elif counts["high"] > 0:
        risk_level = "**High**"
        assessment = "The audit identified high-severity issues that should be addressed before production use."
    elif counts["medium"] > 0:
        risk_level = "**Medium**"
        assessment = "The audit identified medium-severity issues that should be reviewed and addressed."
    elif counts["low"] > 0:
        risk_level = "**Low**"
        assessment = "The audit identified minor issues. The contract appears generally well-structured."
    else:
        risk_level = "**Minimal**"
        assessment = "No significant security issues were identified. Standard best practices are recommended."
    
    summary = f"""This security audit reviewed the smart contract(s) for common vulnerabilities, 
access control issues, and adherence to best practices.

**Overall Risk Assessment**: {risk_level}

{assessment}

A total of **{total} findings** were identified:
- {counts['critical']} Critical
- {counts['high']} High  
- {counts['medium']} Medium
- {counts['low']} Low
- {counts['informational']} Informational"""
    
    return summary


def format_detailed_findings(findings: List[Dict]) -> str:
    """Format all findings into detailed sections."""
    if not findings:
        return "*No findings to report.*"
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
    sorted_findings = sorted(
        findings,
        key=lambda x: severity_order.get(x.get("severity", "informational").lower(), 5)
    )
    
    sections = []
    for i, finding in enumerate(sorted_findings, 1):
        severity = finding.get("severity", "informational")
        
        section = FINDING_TEMPLATE.format(
            severity_upper=severity.upper(),
            index=i,
            title=finding.get("title", "Untitled Finding"),
            severity=severity.capitalize(),
            location=finding.get("location", "Unknown"),
            description=finding.get("description", "No description provided."),
            impact=finding.get("impact", "Impact not assessed."),
            recommendation=finding.get("recommendation", "No recommendation provided."),
            status=finding.get("status", "Open")
        )
        sections.append(section)
    
    return "\n".join(sections)


def generate_recommendations(counts: Dict[str, int]) -> str:
    """Generate general recommendations based on findings."""
    recommendations = []
    
    if counts["critical"] > 0 or counts["high"] > 0:
        recommendations.append(
            "1. **Address Critical/High Issues Immediately**: Do not deploy until all critical "
            "and high-severity issues are resolved and verified."
        )
    
    recommendations.extend([
        "2. **Implement Comprehensive Testing**: Ensure test coverage exceeds 90% for all "
        "critical paths and edge cases.",
        
        "3. **Consider Formal Verification**: For high-value contracts, formal verification "
        "can provide mathematical guarantees of correctness.",
        
        "4. **Establish Monitoring**: Implement on-chain monitoring for unusual activity "
        "patterns post-deployment.",
        
        "5. **Plan for Upgrades**: Consider implementing a transparent upgrade mechanism "
        "with appropriate timelocks and governance.",
        
        "6. **Bug Bounty Program**: Consider launching a bug bounty program to incentivize "
        "responsible disclosure of vulnerabilities."
    ])
    
    return "\n\n".join(recommendations)


def generate_conclusion(counts: Dict[str, int]) -> str:
    """Generate conclusion based on overall findings."""
    total = sum(counts.values())
    
    if counts["critical"] > 0:
        return """The audit has identified **critical security vulnerabilities** that must be 
addressed before the contract can be considered safe for deployment. We strongly recommend 
resolving all critical and high-severity issues and conducting a follow-up audit to verify 
the fixes."""
    
    elif counts["high"] > 0:
        return """The audit has identified **high-severity issues** that require attention. 
While the contract shows reasonable security practices in some areas, the identified issues 
should be resolved before production deployment. A follow-up review of the fixes is recommended."""
    
    elif counts["medium"] > 0:
        return """The audit has identified some **medium-severity issues** that should be 
addressed. The contract demonstrates generally sound security practices, but improvements 
can be made. We recommend addressing the identified issues and implementing the suggested 
best practices."""
    
    else:
        return """The audit found **no critical or high-severity issues**. The contract 
demonstrates good security practices. Minor improvements have been suggested to further 
enhance security and code quality. The contract appears suitable for deployment after 
addressing the minor findings."""


def main():
    parser = argparse.ArgumentParser(description="Generate security audit report")
    parser.add_argument("--contract", required=True, help="Contract name or path")
    parser.add_argument("--findings", required=True, help="Path to findings JSON file")
    parser.add_argument("--output", help="Output Markdown file path")
    parser.add_argument("--auditor", default="Automated Audit", help="Auditor name")
    parser.add_argument("--commit", default="N/A", help="Git commit hash")
    
    args = parser.parse_args()
    
    # Load findings
    findings_data = load_findings(args.findings)
    
    # Handle different input formats
    if isinstance(findings_data, dict):
        if "findings" in findings_data:
            # Format from vulnerability_scan.py
            all_findings = []
            for file_findings in findings_data["findings"].values():
                all_findings.extend(file_findings)
            findings = all_findings
        elif "detectors" in findings_data:
            # Format from run_slither.py
            findings = [
                {
                    "severity": d.get("impact", "informational").lower(),
                    "title": d.get("check", "Unknown"),
                    "description": d.get("description", ""),
                    "location": d.get("elements", [{}])[0].get("source_mapping", {}).get("filename", "Unknown"),
                    "recommendation": "See Slither documentation for remediation guidance."
                }
                for d in findings_data.get("detectors", [])
            ]
        else:
            findings = findings_data.get("results", [])
    else:
        findings = findings_data
    
    # Count by severity
    counts = count_by_severity(findings)
    
    # Generate report sections
    executive_summary = generate_executive_summary(findings, counts)
    detailed_findings = format_detailed_findings(findings)
    recommendations = generate_recommendations(counts)
    conclusion = generate_conclusion(counts)
    
    # Fill template
    report = REPORT_TEMPLATE.format(
        executive_summary=executive_summary,
        contracts=args.contract,
        audit_date=datetime.now().strftime("%Y-%m-%d"),
        auditor=args.auditor,
        commit=args.commit,
        scope=f"Full security audit of {args.contract}",
        critical_count=counts["critical"],
        high_count=counts["high"],
        medium_count=counts["medium"],
        low_count=counts["low"],
        info_count=counts["informational"],
        total_count=sum(counts.values()),
        detailed_findings=detailed_findings,
        recommendations=recommendations,
        conclusion=conclusion,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
