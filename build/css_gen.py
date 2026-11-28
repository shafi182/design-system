#!/usr/bin/env python3
"""Generate CSS custom properties from resolved design tokens.

Produces scoped CSS rules for all palette × appearance combinations.
Variables are embedded in HTML <style> blocks with [data-palette][data-theme] selectors.
"""

import json
from typing import Dict, Tuple


def token_name_to_css_var(token_name: str) -> str:
    """Convert token path to CSS custom property name.
    
    Example: "text.primary" → "--ds-text-primary"
             "brand.accent-text" → "--ds-brand-accent-text"
             "chart.series.1" → "--ds-chart-series-1"
    
    All dots become hyphens.
    """
    return f"--ds-{token_name.replace('.', '-')}"


_DIMENSION_KEYS = frozenset({"value", "unit"})
_SHADOW_KEYS = frozenset({"color", "offsetX", "offsetY", "blur", "spread"})
_SHADOW_SIDES = ("offsetX", "offsetY", "blur", "spread")
_FORBIDDEN_IN_VALUE = (";", "{", "}", "\n", "\r")


def _dimension(value: Dict, token: str) -> str:
    """Serialize a ``{"value": number, "unit": str}`` dimension/duration value.

    Units are kept verbatim and are not whitelisted: the resolved cells carry
    ``px``, ``ms`` and ``em`` (``type.tracking.*`` is negative ``em``).
    """
    if not isinstance(value, dict) or set(value) != _DIMENSION_KEYS:
        raise ValueError(
            f"{token}: unserializable token value {value!r} "
            f"(shape: dict{sorted(value) if isinstance(value, dict) else type(value).__name__})"
        )
    number, unit = value["value"], value["unit"]
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        raise ValueError(f"{token}: non-numeric dimension value {number!r}")
    if not isinstance(unit, str) or not unit:
        raise ValueError(f"{token}: invalid dimension unit {unit!r}")
    if any(ch in unit for ch in _FORBIDDEN_IN_VALUE + (",",)) or any(ch.isspace() for ch in unit):
        raise ValueError(f"{token}: invalid dimension unit {unit!r}")
    return f"{number}{unit}"


def serialize_css_value(value, token: str = "<token>") -> str:
    """Serialize one resolved token value to a CSS value string.

    Resolved cells carry no ``$type`` (``base.LIGHT`` / ``base.DARK`` are plain
    ``{name: value}`` dicts), so dispatch is by shape. Semantics intentionally
    mirror ``build.py:css_value()``; ``dist/css`` is the independent oracle that
    pins the two implementations together (see F-3 tests).

    Supported shapes:
      ``str``                       -> verbatim (hex, "32px", "transparent")
      ``int`` / ``float``           -> ``str(value)`` (``1.0`` stays ``1.0``)
      ``{"value", "unit"}``         -> ``f"{value}{unit}"`` (``12px``, ``120ms``, ``-0.02em``)
      shadow dict (5 keys)          -> ``"<offsetX> <offsetY> <blur> <spread> <color>"``
      ``list[str]``                 -> font stack, entries with spaces quoted with ``'``

    Everything else raises ``ValueError``; arbitrary Python objects are never
    stringified into CSS.
    """
    if isinstance(value, dict):
        if set(value) == _SHADOW_KEYS:
            color = value["color"]
            if not isinstance(color, str) or not color:
                raise ValueError(f"{token}: invalid shadow color {color!r}")
            parts = [_dimension(value[side], token) for side in _SHADOW_SIDES]
            return f"{' '.join(parts)} {color}"
        return _dimension(value, token)

    if isinstance(value, list):
        if not value:
            raise ValueError(f"{token}: empty font-family list")
        for entry in value:
            if not isinstance(entry, str) or not entry:
                raise ValueError(f"{token}: invalid font-family entry {entry!r}")
            if "'" in entry or any(ch in entry for ch in _FORBIDDEN_IN_VALUE):
                raise ValueError(f"{token}: invalid font-family entry {entry!r}")
        return ", ".join(f"'{entry}'" if " " in entry else entry for entry in value)

    if value is None:
        raise ValueError(f"{token}: unserializable token value None")
    if isinstance(value, bool):
        raise ValueError(f"{token}: unserializable token value {value!r} (shape: bool)")
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if not value:
            raise ValueError(f"{token}: empty token value")
        if any(ch in value for ch in _FORBIDDEN_IN_VALUE):
            raise ValueError(f"{token}: token string contains CSS delimiters: {value!r}")
        return value
    raise ValueError(f"{token}: unserializable token value {value!r} (shape: {type(value).__name__})")


def flatten_tokens(token_dict: Dict, *, strict: bool = False) -> Dict:
    """Flatten a nested token dict to ``{"family.slot": value}``, or pass through if flat.

    Input (nested): ``{"surface": {"base": "#E9E5D9"}, "space": {"4": {"value": 12, "unit": "px"}}}``
    Output: ``{"surface.base": "#E9E5D9", "space.4": {"value": 12, "unit": "px"}}``

    Input (already flat, every key dotted): passed through unchanged.

    Non-colour leaves are preserved: ``{"value","unit"}``, shadow and ``list``
    leaves are emitted as-is for :func:`serialize_css_value`. With
    ``strict=True`` a node that yields no token (e.g. an empty dict) raises
    instead of disappearing silently. DTCG ``$``-prefixed metadata is skipped.
    """
    sample_key = next(iter(token_dict.keys()), "")
    if "." in str(sample_key):
        # Already flat (resolved cell): no flattening, no filtering.
        return token_dict

    flat: Dict = {}
    dropped: list = []

    def walk(prefix: str, node: Dict) -> None:
        for key, value in node.items():
            key = str(key)
            if key.startswith("$"):
                continue
            name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                if not value:
                    dropped.append(name)
                elif set(value) == _DIMENSION_KEYS or set(value) == _SHADOW_KEYS:
                    flat[name] = value          # structured leaf
                else:
                    walk(name, value)
            else:
                flat[name] = value              # str / int / float / list leaf

    walk("", token_dict)
    if strict and dropped:
        raise ValueError(
            f"flatten_tokens dropped {len(dropped)} token node(s) with no value: {sorted(dropped)[:10]}"
        )
    return flat


def validate_tokens(flat_tokens: Dict[str, str]) -> Tuple[bool, list]:
    """Validate token completeness and format.
    
    Returns (is_valid, error_messages).
    """
    errors = []
    
    # Map flat tokens (e.g., "surface.base") to families
    families_found = {}
    for name in flat_tokens.keys():
        if "." in name:
            family = name.split(".", 1)[0]
            families_found.setdefault(family, []).append(name)
    
    # Expected tokens per family (non-exhaustive check)
    expected = {
        "surface": ["base", "raised", "sunken", "inverse", "band"],
        "text": ["primary", "secondary", "muted", "inverse", "link", "on-brand"],
        "border": ["subtle", "default", "strong", "focus"],
        "brand": ["primary", "hover", "active", "subtle", "calm", "accent-text"],
        "status": ["success", "success-subtle", "warning", "warning-subtle", "danger", "danger-subtle"],
        "overlay": ["scrim"],
    }
    
    for family, slots in expected.items():
        for slot in slots:
            name = f"{family}.{slot}"
            if name not in flat_tokens:
                errors.append(f"Missing token: {name}")
            else:
                val = flat_tokens[name]
                if not (val.startswith("#") or val.startswith("rgb")):
                    errors.append(f"Invalid color format for {name}: {val}")
    
    return len(errors) == 0, errors


def generate_scoped_rule(palette: str, appearance: str, flat_tokens: Dict[str, str]) -> str:
    """Generate CSS scoped rule for one palette × appearance combination.
    
    Output:
        [data-palette="professional"][data-theme="light"] {
          --ds-surface-base: #E9E5D9;
          --ds-text-primary: #142C36;
          ...
        }
    """
    is_valid, errors = validate_tokens(flat_tokens)
    if not is_valid:
        raise ValueError(f"Token validation failed for {palette}.{appearance}: {errors}")
    
    lines = [f'[data-palette="{palette}"][data-theme="{appearance}"] {{']
    
    # Sort by token name for deterministic output
    sorted_tokens = sorted(flat_tokens.items())
    
    for name, value in sorted_tokens:
        css_var = token_name_to_css_var(name)
        lines.append(f"  {css_var}: {serialize_css_value(value, css_var)};")
    
    lines.append("}")
    return "\n".join(lines)


def generate_all_scoped_rules(themes: Dict[str, Dict]) -> str:
    """Generate all scoped CSS rules for all palette × appearance combinations.
    
    Input: {
        "professional.light": {flat token dict},
        "professional.dark": {flat token dict},
        ...
    }
    
    Returns: Full CSS string with all scoped rules (blank lines between rules).
    """
    rules = []
    for key in sorted(themes.keys()):
        palette, appearance = key.split(".", 1)
        token_dict = themes[key]
        if not token_dict:
            raise ValueError(f"no tokens for {key}")
        # Flatness is decided by key shape, never by the first value's type:
        # a resolved cell has only dotted keys; nested input has family keys.
        if all("." in str(name) for name in token_dict):
            flat = token_dict
        else:
            flat = flatten_tokens(token_dict, strict=True)
        rule = generate_scoped_rule(palette, appearance, flat)
        rules.append(rule)
    
    return "\n\n".join(rules)
