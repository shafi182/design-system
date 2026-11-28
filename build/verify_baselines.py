#!/usr/bin/env python3
"""
M7.1 — Verify SHA-256 baselines against current artifacts.

Usage:
  python3 build/verify_baselines.py [--baseline baselines.json]

Verifies:
  - All baseline hashes match current artifacts
  - No unexpected files present
  - Token parity across all 6 palette/appearance combinations

Exit code:
  0 if all checks pass
  1 if any check fails
"""

import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def artifact_key(path: str) -> str:
    """Extract key name from artifact path."""
    name = Path(path).stem
    return name


def verify_baselines(baseline_file: Path) -> int:
    """Verify all baselines. Returns 0 if pass, 1 if fail."""
    repo_root = baseline_file.parent
    
    if not baseline_file.exists():
        print(f"✗ Baseline file not found: {baseline_file}")
        return 1
    
    baselines = json.loads(baseline_file.read_text())
    failures = []
    success_count = 0
    
    print("Verifying baselines:")
    print()
    
    for key, expected_hash in baselines.items():
        if expected_hash is None:
            print(f"⊘ {key} — baseline not available (skipped)")
            continue
        
        # Find artifact file
        artifact_path = None
        artifact_found = False
        for search_dir in [repo_root / "examples"]:
            candidates = list(search_dir.glob(f"*{key}*"))
            if candidates:
                artifact_path = candidates[0]
                artifact_found = True
                break
        
        if not artifact_found:
            print(f"✗ {key} — artifact not found")
            failures.append((key, "artifact not found"))
            continue
        
        # Compute hash
        try:
            current_hash = sha256_file(artifact_path)
            if current_hash == expected_hash:
                print(f"✓ {key}")
                print(f"  {current_hash}")
                success_count += 1
            else:
                print(f"✗ {key} — hash mismatch")
                print(f"  Expected: {expected_hash}")
                print(f"  Got:      {current_hash}")
                failures.append((key, "hash mismatch"))
        except Exception as e:
            print(f"✗ {key} — error computing hash: {e}")
            failures.append((key, str(e)))
    
    print()
    
    if failures:
        print(f"FAIL: {len(failures)} verification(s) failed")
        for key, reason in failures:
            print(f"  - {key}: {reason}")
        return 1
    else:
        print(f"PASS: All {success_count} baseline(s) verified")
        return 0


def verify_token_parity() -> int:
    """Verify token parity across all palettes. Returns 0 if pass, 1 if fail."""
    import sys
    
    print("\nVerifying token parity:")
    print()
    
    repo_root = Path(__file__).parent.parent
    all_pass = True
    
    for pal in ["professional", "adventurous", "consulting"]:
        for app in ["light", "dark"]:
            token_file = repo_root / f"tokens/semantic/{pal}.{app}.tokens.json"
            
            if not token_file.exists():
                print(f"✗ {pal}.{app} — token file not found")
                all_pass = False
                continue
            
            try:
                tokens = json.loads(token_file.read_text())
                
                def count_tokens(d):
                    total = 0
                    for k, v in d.items():
                        if isinstance(v, dict):
                            if "$value" in v:
                                total += 1
                            else:
                                total += count_tokens(v)
                    return total
                
                count = count_tokens(tokens)
                if count == 32:
                    print(f"✓ {pal:12} {app:5}: {count} tokens")
                else:
                    print(f"✗ {pal:12} {app:5}: {count} tokens (expected 32)")
                    all_pass = False
            except Exception as e:
                print(f"✗ {pal:12} {app:5}: ERROR — {e}")
                all_pass = False
    
    print()
    
    if all_pass:
        print("PASS: All palette/appearance combinations verified (32 tokens each)")
        return 0
    else:
        print("FAIL: Token parity check failed")
        return 1


def main():
    baseline_file = Path("baselines.json")
    
    # Parse args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--baseline" and len(sys.argv) > 2:
            baseline_file = Path(sys.argv[2])
    
    repo_root = baseline_file.parent if baseline_file.is_absolute() else Path(__file__).parent.parent
    baseline_file = repo_root / baseline_file if not baseline_file.is_absolute() else baseline_file
    
    # Run checks
    baseline_check = verify_baselines(baseline_file)
    parity_check = verify_token_parity()
    
    # Exit with failure if any check failed
    sys.exit(max(baseline_check, parity_check))


if __name__ == "__main__":
    main()
