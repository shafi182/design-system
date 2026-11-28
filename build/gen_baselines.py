#!/usr/bin/env python3
"""
M7.1 — Generate SHA-256 baselines from verified artifacts.

Authoritative sources (M6 closure state):
  examples/pitch-deck-{professional,adventurous,consulting}.pptx
  examples/analyst-{professional,adventurous,consulting}.pptx
  examples/preview-{professional,adventurous,consulting}.html
  examples/preview-analyst-{professional,adventurous,consulting}.html

Usage:
  python3 build/gen_baselines.py [--output baselines.json]

Output format:
  {
    "pitch-deck-professional": "sha256:...",
    "pitch-deck-adventurous": "sha256:...",
    ...
  }
"""

import hashlib
import json
import sys
from pathlib import Path

ARTIFACTS = [
    # Pitch decks (3 palettes)
    "examples/pitch-deck-professional.pptx",
    "examples/pitch-deck-adventurous.pptx",
    "examples/pitch-deck-consulting.pptx",
    # Analyst PPTX (3 palettes)
    "examples/analyst-professional.pptx",
    "examples/analyst-adventurous.pptx",
    "examples/analyst-consulting.pptx",
    # Preview HTML (3 palettes)
    "examples/preview-professional.html",
    "examples/preview-adventurous.html",
    "examples/preview-consulting.html",
    # Analyst HTML (3 palettes)
    "examples/preview-analyst-professional.html",
    "examples/preview-analyst-adventurous.html",
    "examples/preview-analyst-consulting.html",
]


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def artifact_key(path: str) -> str:
    """Extract key name from artifact path."""
    # examples/pitch-deck-professional.pptx -> pitch-deck-professional
    name = Path(path).stem
    return name


def main():
    output_file = Path("baselines.json")
    
    # Parse args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--output" and len(sys.argv) > 2:
            output_file = Path(sys.argv[2])
    
    repo_root = Path(__file__).parent.parent
    baselines = {}
    missing = []
    
    for artifact_path in ARTIFACTS:
        full_path = repo_root / artifact_path
        key = artifact_key(artifact_path)
        
        if not full_path.exists():
            missing.append(artifact_path)
            baselines[key] = None
            print(f"✗ {artifact_path} — NOT FOUND", file=sys.stderr)
            continue
        
        try:
            hash_val = sha256_file(full_path)
            baselines[key] = hash_val
            print(f"✓ {artifact_path}")
            print(f"  SHA-256: {hash_val}")
        except Exception as e:
            print(f"✗ {artifact_path} — ERROR: {e}", file=sys.stderr)
            baselines[key] = None
    
    # Write output
    output_path = repo_root / output_file
    output_path.write_text(json.dumps(baselines, indent=2) + "\n")
    print(f"\nBaselines written to {output_file}")
    
    if missing:
        print(f"\n⚠ {len(missing)} artifact(s) not found:")
        for path in missing:
            print(f"  - {path}")
    
    # Exit code
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
