#!/usr/bin/env python3
"""Signal compatibility layer — palette x appearance resolution.

Leaf module: imports nothing from other ``build/`` modules, so every rendering
boundary can depend on it without creating a cycle.

Two independent dimensions (M3):

    palette     = which token set is used ("professional" | "adventurous")
    appearance  = which side of that palette ("light" | "dark")

Historically one string ("theme") did both jobs: it selected the palette *and*
implied the appearance. ``theme=`` is kept as a deprecated alias for
``appearance=`` only. It never selects a palette.

Precedence, highest first (D1/D6):

    1. per-element IR ``appearance`` (falling back to the legacy IR key ``theme``)
    2. per-slide spec ``appearance`` (falling back to the legacy ``theme``)
    3. explicit ``appearance=`` passed to the renderer
    4. the document default: the first slide's appearance
    5. ``DEFAULT_APPEARANCE`` ("light")

Palette never comes from IR or from ``theme=``: it comes from an explicit
``palette=`` argument, the ``SIGNAL_PALETTE`` environment variable, or
``DEFAULT_PALETTE`` ("professional").

Error contract (intentional API change vs. pre-M3):

    unknown palette     -> ValueError  (was KeyError from a dict lookup)
    unknown appearance  -> ValueError
    conflicting args    -> ValueError
"""
from __future__ import annotations

import warnings

#: Explicitly supported palette identifiers. "consulting" is a document type,
#: not a palette, and deliberately has no alias here.
SUPPORTED_PALETTES = ("professional", "adventurous")

#: Appearance values. A palette has exactly these two sides.
SUPPORTED_APPEARANCES = ("light", "dark")

DEFAULT_PALETTE = "professional"
DEFAULT_APPEARANCE = "light"

#: The key every existing IR node and primitive still uses for appearance.
LEGACY_APPEARANCE_KEY = "theme"

_PALETTES = frozenset(SUPPORTED_PALETTES)
_APPEARANCES = frozenset(SUPPORTED_APPEARANCES)

# One warning per (kind, value) per process: internal delegation must not spam.
_WARNED: set[tuple[str, str]] = set()

__all__ = [
    "DEFAULT_APPEARANCE", "DEFAULT_PALETTE", "LEGACY_APPEARANCE_KEY",
    "SUPPORTED_APPEARANCES", "SUPPORTED_PALETTES",
    "appearance_of", "first_slide_appearance", "is_appearance", "is_palette",
    "reset_warnings", "resolve", "resolve_document", "resolve_slide",
    "validate_appearance", "validate_palette",
]


# ------------------------------------------------------------------ predicates

def is_palette(name) -> bool:
    """True when *name* is a supported palette identifier."""
    return isinstance(name, str) and name in _PALETTES


def is_appearance(name) -> bool:
    """True when *name* is a supported appearance."""
    return isinstance(name, str) and name in _APPEARANCES


# ------------------------------------------------------------------ validation

def validate_palette(name) -> str:
    """Return *name* if supported, else raise ``ValueError``."""
    if is_palette(name):
        return name
    hint = " ('consulting' is a document type, not a palette)" if name == "consulting" else ""
    raise ValueError(
        f"unsupported palette {name!r}{hint}; "
        f"expected one of: {', '.join(SUPPORTED_PALETTES)}"
    )


def validate_appearance(name, *, what: str = "appearance") -> str:
    """Return *name* if it is "light" or "dark", else raise ``ValueError``."""
    if is_appearance(name):
        return name
    raise ValueError(
        f"unsupported {what} {name!r}; "
        f"expected one of: {', '.join(SUPPORTED_APPEARANCES)}"
    )


# ------------------------------------------------------------------ warnings

def _warn_deprecated(theme: str, stacklevel: int) -> None:
    key = ("theme", theme)
    if key in _WARNED:
        return
    _WARNED.add(key)
    warnings.warn(
        f"theme={theme!r} is deprecated; pass appearance={theme!r} instead. "
        "'theme' now means appearance, never palette.",
        DeprecationWarning,
        stacklevel=stacklevel + 1,
    )


def reset_warnings() -> None:
    """Forget which deprecation warnings were already emitted (tests only)."""
    _WARNED.clear()


# ------------------------------------------------------------------ resolution

def _resolve(palette=None, appearance=None, theme=None, *, warn: bool, stacklevel: int):
    """Core resolver. Returns ``(palette, appearance_or_None)``.

    ``appearance`` stays ``None`` when the caller specified neither
    ``appearance=`` nor ``theme=``, so document-level defaults can apply.
    """
    resolved_palette = DEFAULT_PALETTE if palette is None else validate_palette(palette)

    if theme is not None:
        legacy = validate_appearance(theme, what="theme")
        if appearance is None:
            if warn:
                _warn_deprecated(legacy, stacklevel)
            return resolved_palette, legacy
        explicit = validate_appearance(appearance)
        if explicit != legacy:
            raise ValueError(
                f"conflicting appearance={explicit!r} and deprecated theme={legacy!r}; "
                "pass only appearance="
            )
        return resolved_palette, explicit

    if appearance is None:
        return resolved_palette, None
    return resolved_palette, validate_appearance(appearance)


def resolve(palette=None, appearance=None, theme=None, *, warn: bool = True,
            stacklevel: int = 3) -> tuple[str, str]:
    """Resolve render options to ``(palette, appearance)``.

    ``theme=`` is accepted as a deprecated alias for ``appearance=`` and emits
    one ``DeprecationWarning`` per value per process. Supplying both with
    different values is an error rather than a silent choice.

    >>> resolve()
    ('professional', 'light')
    >>> resolve("adventurous", "dark")
    ('adventurous', 'dark')
    """
    p, a = _resolve(palette, appearance, theme, warn=warn, stacklevel=stacklevel)
    return p, DEFAULT_APPEARANCE if a is None else a


def first_slide_appearance(slides) -> str | None:
    """Appearance declared by the first slide, or ``None``."""
    for spec in slides or ():
        a = appearance_of(spec, None)
        if a is not None:
            return a
        break
    return None


def resolve_document(slides, palette=None, appearance=None, theme=None, *,
                     warn: bool = True, stacklevel: int = 3) -> tuple[str, str]:
    """Resolve ``(palette, document_appearance)`` for a slide list.

    The document default is the first slide's appearance (D1), unless the
    caller passed ``appearance=``/``theme=`` explicitly, which takes precedence
    over the first slide but never over a per-slide override.
    """
    p, a = _resolve(palette, appearance, theme, warn=warn, stacklevel=stacklevel)
    if a is None:
        a = first_slide_appearance(slides) or DEFAULT_APPEARANCE
    return p, a


def appearance_of(node, fallback: str | None = None) -> str | None:
    """Appearance declared by an IR node or slide spec, else *fallback*.

    ``appearance`` wins over the legacy ``theme`` key when both are present.
    """
    if node:
        declared = node.get("appearance")
        if declared is None:
            declared = node.get(LEGACY_APPEARANCE_KEY)
        if declared is not None:
            return validate_appearance(declared)
    return fallback


def resolve_slide(spec, document_appearance: str = DEFAULT_APPEARANCE) -> str:
    """Appearance for one slide: its own override, else the document default."""
    resolved = appearance_of(spec, document_appearance)
    return DEFAULT_APPEARANCE if resolved is None else resolved
