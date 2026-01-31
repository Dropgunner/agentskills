#!/usr/bin/env python3
"""
Wrapper script for running Slither static analysis on Solidity contracts.
Provides formatted output and JSON export.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def check_slither_installed() -> bool:
    """Check if Slither is installed."""
    try:
        result = subprocess.run(
            ["slither", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_slither() -> bool:
    """Attempt to install Slither."""
    print("Installing Slither...")
    try:
        result = subprocess.run(
            ["pip", "install", "slither-analyzer"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to install Slither: {e}")
        return False


def run_slither(
    contract_path: str,
    output_json: Optional[str] = None,
    exclude_detectors: Optional[List[str]] = None,
    include_detectors: Optional[List[str]] = None
) -> Dict:
    """Run Slither analysis on a contract."""
    
    cmd = ["slither", contract_path, "--json", "-"]
    
    if exclude_detectors:
        cmd.extend(["--exclude", ",".join(exclude_detectors)])
    
    if include_detectors:
        cmd.extend(["--detect", ",".join(include_detectors)])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Slither outputs JSON to stdout when using --json -
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If JSON parsing fails, return error info
            output = {
                "success": False,
                "error": result.stderr or result.stdout,
                "detectors": []
            }
        
        return output
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Analysis timed out after 5 minutes",
            "detectors": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detectors": []
        }


def format_findings(slither_output: Dict) -> Dict:
    """Format Slither output into a structured report."""
    
    findings = {
        "summary": {
            "total": 0,
            "by_impact": {},
            "by_confidence": {}
        },
        "detectors": []
    }
    
    detectors = slither_output.get("results", {}).get("detectors", [])
    
    for detector in detectors:
        impact = detector.get("impact", "Unknown")
        confidence = detector.get("confidence", "Unknown")
        
        # Update summary
        findings["summary"]["total"] += 1
        findings["summary"]["by_impact"][impact] = \
            findings["summary"]["by_impact"].get(impact, 0) + 1
        findings["summary"]["by_confidence"][confidence] = \
            findings["summary"]["by_confidence"].get(confidence, 0) + 1
        
        # Format detector result
        formatted = {
            "check": detector.get("check", "Unknown"),
            "impact": impact,
            "confidence": confidence,
            "description": detector.get("description", ""),
            "elements": []
        }
        
        # Extract element locations
        for element in detector.get("elements", []):
            elem_info = {
                "type": element.get("type", ""),
                "name": element.get("name", ""),
                "source_mapping": {}
            }
            
            source = element.get("source_mapping", {})
            if source:
                elem_info["source_mapping"] = {
                    "filename": source.get("filename_relative", ""),
                    "lines": source.get("lines", []),
                    "start": source.get("start", 0),
                    "length": source.get("length", 0)
                }
            
            formatted["elements"].append(elem_info)
        
        findings["detectors"].append(formatted)
    
    return findings


def print_report(findings: Dict):
    """Print a formatted report."""
    
    print("\n" + "=" * 60)
    print("SLITHER ANALYSIS REPORT")
    print("=" * 60)
    
    summary = findings["summary"]
    print(f"\nTotal Findings: {summary['total']}")
    
    if summary["by_impact"]:
        print("\nBy Impact:")
        for impact, count in sorted(summary["by_impact"].items()):
            print(f"  {impact}: {count}")
    
    if summary["by_confidence"]:
        print("\nBy Confidence:")
        for conf, count in sorted(summary["by_confidence"].items()):
            print(f"  {conf}: {count}")
    
    if findings["detectors"]:
        print("\n" + "-" * 60)
        print("DETAILED FINDINGS")
        print("-" * 60)
        
        # Sort by impact (High first)
        impact_order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
        sorted_detectors = sorted(
            findings["detectors"],
            key=lambda x: impact_order.get(x["impact"], 4)
        )
        
        for i, detector in enumerate(sorted_detectors, 1):
            print(f"\n[{i}] {detector['check']}")
            print(f"    Impact: {detector['impact']}")
            print(f"    Confidence: {detector['confidence']}")
            print(f"    Description: {detector['description'][:200]}...")
            
            if detector["elements"]:
                print("    Locations:")
                for elem in detector["elements"][:3]:  # Limit to 3 locations
                    src = elem.get("source_mapping", {})
                    if src.get("filename"):
                        lines = src.get("lines", [])
                        line_str = f"L{lines[0]}-{lines[-1]}" if lines else ""
                        print(f"      - {src['filename']}:{line_str}")


def main():
    parser = argparse.ArgumentParser(description="Run Slither analysis on Solidity contracts")
    parser.add_argument("--contract", required=True, help="Path to contract file or directory")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--exclude", help="Comma-separated list of detectors to exclude")
    parser.add_argument("--detect", help="Comma-separated list of detectors to run")
    parser.add_argument("--install", action="store_true", help="Install Slither if not found")
    
    args = parser.parse_args()
    
    # Check if Slither is installed
    if not check_slither_installed():
        if args.install:
            if not install_slither():
                print("Failed to install Slither. Please install manually:")
                print("  pip install slither-analyzer")
                sys.exit(1)
        else:
            print("Slither is not installed. Run with --install or install manually:")
            print("  pip install slither-analyzer")
            sys.exit(1)
    
    # Verify contract path exists
    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"Error: Path does not exist: {contract_path}")
        sys.exit(1)
    
    print(f"Running Slither analysis on: {contract_path}")
    print("-" * 50)
    
    # Parse detector options
    exclude = args.exclude.split(",") if args.exclude else None
    detect = args.detect.split(",") if args.detect else None
    
    # Run analysis
    slither_output = run_slither(
        str(contract_path),
        exclude_detectors=exclude,
        include_detectors=detect
    )
    
    # Check for errors
    if slither_output.get("success") is False:
        print(f"Analysis failed: {slither_output.get('error', 'Unknown error')}")
        sys.exit(1)
    
    # Format findings
    findings = format_findings(slither_output)
    
    # Print report
    print_report(findings)
    
    # Save to JSON if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(findings, f, indent=2)
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
