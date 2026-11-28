#!/usr/bin/env python3
"""Semantic palette identity gate for Signal generated artifacts (MI-1B).

The hash baselines (M7.1, ``build/verify_baselines.py``) answer "are the bytes the
bytes we accepted?". This gate answers a different question: "do the bytes carry the
palette identity their filename and metadata claim?". MI-1 demonstrated that a hash
recorded from a defective artifact passes forever, so hash verification cannot
detect wrong-but-stable output. This gate closes that gap; it does not replace it.

Taxonomy (verified against ``build/compat.py``):

* Supported palettes (renderer layer): ``professional``, ``adventurous``.
  ``compat.SUPPORTED_PALETTES`` has exactly these two entries.
* ``consulting`` is a **document type**, not a palette: ``compat.validate_palette``
  raises for it (``compat.py:84``). It exists only in the CSS/dist layer, where
  three document types are emitted.

Coverage therefore splits:

* HTML renderer: 2 palettes x 2 appearances = 4 combinations.
* CSS/dist: 3 document types x 2 appearances = 6 combinations.

All expected values are derived from ``dist/json/tokens.resolved.json`` at runtime,
serialized through :func:`css_gen.serialize_css_value` — the generator's own value
serializer. No palette values are duplicated in this module. The gate compares the
complete declaration set of every block (191 declarations per cell: colour and
non-colour alike), and fails on wrong values, missing declarations, unexpected extra
declarations, and duplicate declarations. It proves identity with the serializer, not
browser-level CSS syntax validity.

Usage::

    python build/validate_palette_identity.py            # validate repo artifacts
    python build/validate_palette_identity.py --self-test # prove the gate can fail
    python build/validate_palette_identity.py --json      # machine-readable result
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import compat as _compat  # same package dir; no import side effects
import css_gen as _css_gen  # expected-value oracle: the generator's own serializer

ROOT = Path(__file__).resolve().parent.parent
TOKENS_PATH = ROOT / "dist" / "json" / "tokens.resolved.json"
EXAMPLES = ROOT / "examples"
CSS_DIR = ROOT / "dist" / "css"
FIXTURES = ROOT / "build" / "fixtures" / "mi1"

#: Renderer palettes — derived from ``compat.SUPPORTED_PALETTES`` so this gate can
#: never desynchronise from the taxonomy the renderers actually enforce.
PALETTES: Tuple[str, ...] = tuple(_compat.SUPPORTED_PALETTES)

#: CSS/dist document types — includes ``consulting``, which is *not* a palette.
DOCUMENT_TYPES: Tuple[str, ...] = ("professional", "adventurous", "consulting")

CSS_FILES: Dict[str, str] = {
    "professional": "tokens.css",
    "adventurous": "tokens-adventurous.css",
    "consulting": "tokens-consulting.css",
}

#: (relative path, expected palette) for the HTML preview artifacts.
HTML_TARGETS: Tuple[Tuple[str, str], ...] = (
    ("examples/preview-professional.html", "professional"),
    ("examples/preview-adventurous.html", "adventurous"),
    ("examples/preview-analyst-professional.html", "professional"),
    ("examples/preview-analyst-adventurous.html", "adventurous"),
)

#: Pairs that must remain semantically distinct (professional vs adventurous).
DISTINCT_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("examples/preview-professional.html", "examples/preview-adventurous.html"),
    ("examples/preview-analyst-professional.html", "examples/preview-analyst-adventurous.html"),
)

_HTML_TAG = re.compile(r"<html\b[^>]*>", re.I)
_ATTR = re.compile(r'([a-zA-Z-]+)="([^"]*)"')
_TITLE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
_CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)


# --------------------------------------------------------------------------- tokens


def load_tokens(path: Path = TOKENS_PATH) -> Dict[str, Dict[str, str]]:
    """Load the resolved token map: ``{"<document-type>.<appearance>": {token: value}}``."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [f"{t}.{a}" for t in DOCUMENT_TYPES for a in ("light", "dark") if f"{t}.{a}" not in data]
    if missing:
        raise ValueError(f"tokens file {path} lacks cells: {missing}")
    return data


def expected_values(tokens: Dict[str, Dict[str, str]], doc_type: str, appearance: str) -> Dict[str, str]:
    """Representative token values for one cell, read from the resolved tokens."""
    cell = tokens[f"{doc_type}.{appearance}"]
    return {
        "surface.base": cell["surface.base"],
        "brand.primary": cell["brand.primary"],
        "text.primary": cell["text.primary"],
    }


#: Declarations every resolved cell carries. Pinned so the gate cannot silently
#: shrink its own coverage if a token disappears from ``tokens.resolved.json``.
EXPECTED_DECLARATIONS_PER_CELL = 191

_DECLARATION = re.compile(r"(--ds-[a-z0-9-]+)\s*:\s*([^;]+);")


def expected_declarations(tokens: Dict[str, Dict[str, str]], doc_type: str, appearance: str) -> Dict[str, str]:
    """Every expected declaration for one cell: ``{"--ds-var": css_value}``.

    The value oracle is :func:`css_gen.serialize_css_value`, the serializer the
    generator itself uses, applied to the resolved cell — so a green result proves
    the artifact matches the serializer's output for all 191 declarations. It does
    not prove browser-level CSS syntax validity (unchanged, documented limitation).

    Colour values stay verbatim; structured leaves (``{"value","unit"}`` dimensions,
    five-key shadows, font-family lists) are serialized exactly as the generator
    serializes them, which is what makes non-colour regressions detectable.
    """
    cell = tokens[f"{doc_type}.{appearance}"]
    return {
        _css_gen.token_name_to_css_var(name): _css_gen.serialize_css_value(value, name)
        for name, value in cell.items()
    }


def declaration_tokens(tokens: Dict[str, Dict[str, str]], doc_type: str, appearance: str) -> Dict[str, str]:
    """Map ``--ds-var`` -> dotted token name, for diagnostics only."""
    return {_css_gen.token_name_to_css_var(name): name for name in tokens[f"{doc_type}.{appearance}"]}


def declarations(body: Optional[str]) -> List[Tuple[str, str]]:
    """Ordered ``(css_var, value)`` pairs for every ``--ds-*`` declaration in *body*.

    Duplicates are preserved: the caller needs the raw count to report a variable
    declared twice (last-wins would otherwise hide a duplicated block entry).
    """
    return [(m.group(1), m.group(2).strip()) for m in _DECLARATION.finditer(body or "")]


def compare_declarations(
    label: str,
    body: Optional[str],
    expected: Dict[str, str],
    *,
    cell: str = "",
    token_names: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Compare one CSS block against the complete expected declaration map.

    Reports four distinct defect classes: missing declaration, wrong value
    (colour or non-colour alike), unexpected extra declaration, and duplicate
    declaration. Value comparison is case-insensitive because CSS hex digits and
    keywords are case-insensitive, and the pre-F-3 fixtures legitimately differ
    from current output only in hex case.
    """
    pairs = declarations(body)
    counts: Dict[str, int] = {}
    seen: Dict[str, str] = {}
    for name, value in pairs:
        counts[name] = counts.get(name, 0) + 1
        seen.setdefault(name, value)

    names = token_names or {}
    failures: List[str] = []

    for var in sorted(expected):
        want = expected[var]
        token = names.get(var, var)
        if var not in seen:
            failures.append(f"{label} lacks {var} ({token})")
        elif seen[var].lower() != want.lower():
            where = f"{cell} wants {want}" if cell else f"wants {want}"
            failures.append(f"{label} {var} ({token})={seen[var]} but {where}")

    for var in sorted(set(seen) - set(expected)):
        failures.append(f"{label} unexpected extra declaration {var}={seen[var]}")

    for var in sorted(name for name, count in counts.items() if count > 1):
        failures.append(f"{label} duplicate declaration {var} ({counts[var]} occurrences)")

    return failures


def require_palette(name: str) -> str:
    """Return *name* if it is a supported palette identity, else raise ``ValueError``.

    Delegates to ``compat.validate_palette`` so the gate rejects exactly what the
    renderers reject — notably ``"consulting"``, which is a document type.
    """
    return _compat.validate_palette(name)


# ------------------------------------------------------------------------ parsing


def html_identity(text: str) -> Dict[str, Optional[str]]:
    """Extract ``data-palette`` / ``data-theme`` / ``<title>`` from an HTML document."""
    tag = _HTML_TAG.search(text)
    attrs = dict(_ATTR.findall(tag.group(0))) if tag else {}
    title = _TITLE.search(text)
    return {
        "palette": attrs.get("data-palette"),
        "appearance": attrs.get("data-theme"),
        "title": title.group(1).strip() if title else None,
    }


def css_rules(text: str) -> List[Tuple[str, str]]:
    """Return ``(selector, body)`` pairs for a generated stylesheet.

    Line-oriented scanner, because the generated CSS carries un-stringified token
    objects as declaration values (``--ds-type-...: {'value': 0.06, 'unit': 'em'};``),
    so brace counting and ``[^{}]+`` regexes both mis-split rules. The generator
    emits one rule per block with the closing ``}`` on its own line, plus a handful
    of single-line rules (``*{...}``).
    """
    rules: List[Tuple[str, str]] = []
    selector_parts: List[str] = []
    body: List[str] = []
    in_rule = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("/*"):
            continue
        if in_rule:
            if line == "}":
                rules.append((" ".join(selector_parts).strip(), "\n".join(body)))
                selector_parts, body, in_rule = [], [], False
            else:
                body.append(line)
            continue
        if "{" in line:
            head, rest = line.split("{", 1)
            if head.strip():
                selector_parts.append(head.strip())
            if "}" in rest:
                inner, _ = rest.rsplit("}", 1)
                rules.append((" ".join(selector_parts).strip(), inner))
                selector_parts = []
            else:
                in_rule = True
                if rest.strip():
                    body.append(rest.strip())
        else:
            selector_parts.append(line)
    return rules


def css_var(body: Optional[str], name: str) -> Optional[str]:
    """Return the value of ``--ds-<name>`` inside a rule body, if declared."""
    if not body:
        return None
    css_name = name.replace(".", "-")
    m = re.search(r"--ds-" + re.escape(css_name) + r"\s*:\s*([^;]+);", body)
    return m.group(1).strip() if m else None


def _block_for(rules: Sequence[Tuple[str, str]], selector: str, *, exact: bool = False) -> Optional[str]:
    for sel, body in rules:
        if (sel == selector) if exact else (selector in sel):
            return body
    return None


# ------------------------------------------------------------------------- checks


def check_html(path: Path, expected_palette: str, tokens: Dict[str, Dict[str, str]]) -> List[str]:
    """Validate one HTML artifact against *expected_palette*.

    Raises ``ValueError`` for anything that is not a supported palette identity —
    the gate refuses to validate against a category it does not own.
    """
    expected_palette = require_palette(expected_palette)
    path = Path(path)
    if not path.exists():
        return [f"{path}: missing"]
    text = path.read_text(encoding="utf-8")
    failures: List[str] = []

    ident = html_identity(text)
    if ident["palette"] != expected_palette:
        failures.append(
            f"{path.name}: data-palette={ident['palette']!r}, filename/metadata implies {expected_palette!r}"
        )
    if ident["appearance"] not in ("light", "dark"):
        failures.append(f"{path.name}: data-theme={ident['appearance']!r} is not light/dark")
    if not ident["title"]:
        failures.append(f"{path.name}: no <title>")
    elif expected_palette not in ident["title"].lower():
        failures.append(f"{path.name}: title {ident['title']!r} does not name palette {expected_palette!r}")

    # Scoped CSS: both appearance blocks for this palette, with the expected values.
    rules = css_rules(text)
    for appearance in ("light", "dark"):
        selector = f'[data-palette="{expected_palette}"][data-theme="{appearance}"]'
        body = _block_for(rules, selector)
        if body is None:
            failures.append(f"{path.name}: missing scoped block {selector}")
            continue
        failures += compare_declarations(
            f"{path.name}: {selector}",
            body,
            expected_declarations(tokens, expected_palette, appearance),
            cell=f"{expected_palette}.{appearance}",
            token_names=declaration_tokens(tokens, expected_palette, appearance),
        )

    # A document must not carry another palette's scoped rules (the MI-1 signature).
    for other in PALETTES:
        if other != expected_palette and f'[data-palette="{other}"]' in text:
            failures.append(f"{path.name}: carries foreign scoped rules for palette {other!r}")
    return failures


def check_css(path: Path, doc_type: str, tokens: Dict[str, Dict[str, str]]) -> List[str]:
    """Validate one CSS/dist document-type file against the resolved tokens."""
    path = Path(path)
    if not path.exists():
        return [f"{path}: missing"]
    rules = css_rules(path.read_text(encoding="utf-8"))
    failures: List[str] = []

    light_selector = ":root" if doc_type == "professional" else f'[data-palette="{doc_type}"]'
    dark_selector = f'[data-palette="{doc_type}"][data-theme="dark"]'
    light_body = _block_for(rules, light_selector, exact=(doc_type == "professional"))
    dark_body = _block_for(rules, dark_selector)

    if light_body is None:
        failures.append(f"{path.name}: missing light block ({light_selector})")
    if dark_body is None:
        failures.append(f"{path.name}: missing dark block ({dark_selector})")

    for appearance, body, selector in (("light", light_body, light_selector), ("dark", dark_body, dark_selector)):
        if body is None:
            continue
        failures += compare_declarations(
            f"{path.name}: {selector}",
            body,
            expected_declarations(tokens, doc_type, appearance),
            cell=f"{doc_type}.{appearance}",
            token_names=declaration_tokens(tokens, doc_type, appearance),
        )

    for other in DOCUMENT_TYPES:
        if other != doc_type and f'[data-palette="{other}"]' in path.read_text(encoding="utf-8"):
            failures.append(f"{path.name}: carries selectors for document type {other!r}")
    return failures


def check_distinct(path_a: Path, path_b: Path, tokens: Dict[str, Dict[str, str]]) -> List[str]:
    """Two artifacts meant to differ must not collapse onto one palette.

    Compares declared identity, the rendered light-block ``surface.base``, bytes,
    and the resolved token cells — the last catches a token-level collapse even if
    the files were generated from different code paths.
    """
    path_a, path_b = Path(path_a), Path(path_b)
    failures: List[str] = []
    if not (path_a.exists() and path_b.exists()):
        return [f"distinctness: missing {path_a if not path_a.exists() else path_b}"]

    text_a = path_a.read_text(encoding="utf-8")
    text_b = path_b.read_text(encoding="utf-8")
    ident_a, ident_b = html_identity(text_a), html_identity(text_b)

    if ident_a["palette"] == ident_b["palette"]:
        failures.append(
            f"{path_a.name} and {path_b.name}: both declare data-palette={ident_a['palette']!r} (palette collapse)"
        )
    if text_a == text_b:
        failures.append(f"{path_a.name} and {path_b.name}: byte-identical (palette collapse)")

    rendered = []
    for path, text, ident in ((path_a, text_a, ident_a), (path_b, text_b, ident_b)):
        body = _block_for(css_rules(text), f'[data-palette="{ident["palette"]}"][data-theme="light"]')
        rendered.append((path, css_var(body, "surface.base") if body else None))
    (pa, va), (pb, vb) = rendered
    if va is not None and va == vb:
        failures.append(f"{pa.name} and {pb.name}: rendered surface.base identical ({va})")

    for appearance in ("light", "dark"):
        a = expected_values(tokens, "professional", appearance)
        b = expected_values(tokens, "adventurous", appearance)
        for name in a:
            if a[name].lower() == b[name].lower():
                failures.append(
                    f"distinctness: professional.{appearance} and adventurous.{appearance} share {name}={a[name]}"
                )
    return failures


def validate(root: Path = ROOT, tokens: Optional[Dict[str, Dict[str, str]]] = None) -> List[str]:
    """Run every check against the artifacts under *root*. Returns failure strings."""
    root = Path(root)
    tokens = tokens or load_tokens(root / "dist" / "json" / "tokens.resolved.json")
    failures: List[str] = []

    # Coverage guard: the gate validates whatever the token file declares, so a
    # shrinking token file would silently shrink the gate. Pin the target count.
    for doc_type in DOCUMENT_TYPES:
        for appearance in ("light", "dark"):
            count = len(tokens[f"{doc_type}.{appearance}"])
            if count != EXPECTED_DECLARATIONS_PER_CELL:
                failures.append(
                    f"tokens: {doc_type}.{appearance} declares {count} tokens, "
                    f"expected {EXPECTED_DECLARATIONS_PER_CELL}"
                )

    for rel, palette in HTML_TARGETS:
        failures += check_html(root / rel, palette, tokens)
    for doc_type, filename in CSS_FILES.items():
        failures += check_css(root / "dist" / "css" / filename, doc_type, tokens)
    for a, b in DISTINCT_PAIRS:
        failures += check_distinct(root / a, root / b, tokens)
    return failures


# ----------------------------------------------------------------------- self-test


def self_test(tmp: Optional[Path] = None, tokens: Optional[Dict[str, Dict[str, str]]] = None) -> List[str]:
    """Prove the gate rejects known-bad input.

    Returns a list of self-test failures (empty means the gate behaves correctly).
    Nothing under ``mi1_tmp/`` is modified: tampered copies are written to *tmp*.
    """
    tokens = tokens or load_tokens()
    tmp = Path(tmp) if tmp else Path(tempfile.mkdtemp(prefix="mi1b_selftest_"))
    tmp.mkdir(parents=True, exist_ok=True)
    problems: List[str] = []

    def expect(name: str, failures: Sequence[str], *, should_fail: bool) -> None:
        if should_fail and not failures:
            problems.append(f"self-test: {name} passed but must fail")
        if not should_fail and failures:
            problems.append(f"self-test: {name} failed unexpectedly: {failures[:3]}")

    # Positive controls: value-complete artifacts must pass.
    # These are the shipped preview artifacts (191 declarations per cell). The
    # pre-F-3 fixtures B/E are no longer valid positives: they carry un-stringified
    # token dicts for the 64 structured declarations, which is the F-3 defect the
    # value-complete gate now detects (see test_D3_05 / test_F3T21).
    expect(
        "examples/preview-professional.html as professional",
        check_html(ROOT / "examples" / "preview-professional.html", "professional", tokens),
        should_fail=False,
    )
    expect(
        "examples/preview-adventurous.html as adventurous",
        check_html(ROOT / "examples" / "preview-adventurous.html", "adventurous", tokens),
        should_fail=False,
    )
    expect(
        "examples/preview-analyst-adventurous.html as adventurous",
        check_html(ROOT / "examples" / "preview-analyst-adventurous.html", "adventurous", tokens),
        should_fail=False,
    )

    # Negative controls: the MI-1 defect and its variants must fail.
    expect("A_default.html as adventurous", check_html(FIXTURES / "A_default.html", "adventurous", tokens), should_fail=True)
    expect("D_default.html as adventurous", check_html(FIXTURES / "D_default.html", "adventurous", tokens), should_fail=True)

    flipped = tmp / "flipped_palette.html"
    flipped.write_text(
        (ROOT / "examples" / "preview-adventurous.html").read_text(encoding="utf-8").replace(
            'data-palette="adventurous"', 'data-palette="professional"', 1
        ),
        encoding="utf-8",
    )
    expect("flipped data-palette", check_html(flipped, "adventurous", tokens), should_fail=True)

    swapped = tmp / "swapped_surface.html"
    light_surface = expected_values(tokens, "adventurous", "light")["surface.base"]
    pro_surface = expected_values(tokens, "professional", "light")["surface.base"]
    swapped.write_text(
        (ROOT / "examples" / "preview-adventurous.html").read_text(encoding="utf-8").replace(light_surface, pro_surface),
        encoding="utf-8",
    )
    expect("swapped surface.base value", check_html(swapped, "adventurous", tokens), should_fail=True)

    collapsed = tmp / "collapsed_adventurous.html"
    collapsed.write_bytes((ROOT / "examples" / "preview-professional.html").read_bytes())
    expect(
        "collapsed professional/adventurous pair",
        check_distinct(ROOT / "examples" / "preview-professional.html", collapsed, tokens),
        should_fail=True,
    )

    return problems


# ----------------------------------------------------------------------------- CLI


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic palette identity gate (MI-1B)")
    parser.add_argument("--root", default=str(ROOT), help="repository root to validate")
    parser.add_argument("--tokens", default=None, help="path to tokens.resolved.json")
    parser.add_argument("--self-test", action="store_true", help="prove the gate rejects known-bad input")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root)
    tokens = load_tokens(Path(args.tokens) if args.tokens else root / "dist" / "json" / "tokens.resolved.json")

    if args.self_test:
        problems = self_test(tokens=tokens)
        payload = {"mode": "self-test", "ok": not problems, "problems": problems}
        print(json.dumps(payload, indent=2) if args.json else (
            "self-test OK — gate rejects all defective fixtures" if not problems else
            "\n".join(["self-test BROKEN:"] + [f"  ✗ {p}" for p in problems])
        ))
        return 2 if problems else 0

    failures = validate(root, tokens)
    payload = {"mode": "validate", "ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(payload, indent=2))
    elif failures:
        print(f"palette identity: {len(failures)} failure(s)")
        for f in failures:
            print(f"  ✗ {f}")
    else:
        print("palette identity: OK (4 HTML cells, 6 CSS cells, 2 distinctness pairs)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
