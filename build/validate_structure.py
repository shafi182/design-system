#!/usr/bin/env python3
"""
M7.1 — Validate generated artifact structure (not byte-level).

Validates:
  - dist/json/tokens.resolved.json exists and has 6 palette/appearance entries
  - CSS token output has semantic families
  - Resolved tokens are non-empty per palette

Usage:
  python3 build/validate_structure.py

Exit code:
  0 if all checks pass
  1 if any check fails
"""

import json
import sys
from pathlib import Path


def validate_resolved_tokens() -> int:
    """Validate tokens.resolved.json structure."""
    resolved_file = Path("dist/json/tokens.resolved.json")
    
    if not resolved_file.exists():
        print(f"✗ {resolved_file} not found")
        return 1
    
    try:
        tokens = json.loads(resolved_file.read_text())
    except Exception as e:
        print(f"✗ {resolved_file} parse error: {e}")
        return 1
    
    print("Validating tokens.resolved.json:")
    all_pass = True
    
    # Expected entries: 6 (3 palettes × 2 appearances)
    expected_keys = [
        "professional.light",
        "professional.dark",
        "adventurous.light",
        "adventurous.dark",
        "consulting.light",
        "consulting.dark",
    ]
    
    for key in expected_keys:
        if key not in tokens:
            print(f"✗ {key} not found")
            all_pass = False
            continue
        
        # Check that value is dict and non-empty
        value = tokens[key]
        if not isinstance(value, dict):
            print(f"✗ {key} is not a dict")
            all_pass = False
            continue
        
        if len(value) == 0:
            print(f"✗ {key} is empty")
            all_pass = False
            continue
        
        # Count entries (flattened tokens)
        count = len(value)
        print(f"✓ {key}: {count} entries")
    
    return 0 if all_pass else 1


def validate_css_output() -> int:
    """Validate CSS token output has expected semantic families."""
    css_file = Path("dist/css/tokens.css")
    
    if not css_file.exists():
        print(f"\n✗ {css_file} not found")
        return 1
    
    print("\nValidating CSS output (semantic tokens):")
    
    css_content = css_file.read_text()
    
    # Check for expected semantic token families
    # Format: --ds-<family>-<token>: value;
    
    families = [
        "border",
        "brand",
        "surface",
        "text",
        "status",
        "overlay",
    ]
    
    all_pass = True
    for family in families:
        pattern = f"--ds-{family}-"
        if pattern in css_content:
            print(f"✓ CSS contains {family} family")
        else:
            print(f"✗ CSS missing {family} family")
            all_pass = False
    
    return 0 if all_pass else 1


def main():
    checks = [
        ("Resolved tokens", validate_resolved_tokens()),
        ("CSS output", validate_css_output()),
    ]
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, result in checks:
        status = "✓ PASS" if result == 0 else "✗ FAIL"
        print(f"{status}: {name}")
    
    # Exit with failure if any check failed
    exit_code = max(result for _, result in checks)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
