#!/usr/bin/env python3
"""Build the Signal design system from DTCG tokens.

Single source of truth: tokens/**/*.tokens.json
Outputs (never edit by hand): dist/**

    python build/build.py            # build everything
    python build/build.py --check    # validate only, no writes

No third-party dependencies. Aliases use DTCG syntax: {"$value": "{color.navy.700}"}
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "tokens"
DIST = ROOT / "dist"

ALIAS = re.compile(r"^\{([a-zA-Z0-9._-]+)\}$")

# ---------------------------------------------------------------- loading

def deep_merge(base: dict, add: dict) -> dict:
    out = dict(base)
    for k, v in add.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_tree(paths: list[Path]) -> dict:
    tree: dict = {}
    for p in sorted(paths):
        with p.open(encoding="utf-8") as fh:
            tree = deep_merge(tree, json.load(fh))
    return tree


def is_token(node) -> bool:
    return isinstance(node, dict) and "$value" in node


def flatten(tree: dict, prefix: str = "") -> dict[str, dict]:
    """Walk the token tree, returning {dotted.name: node} for every token."""
    out: dict[str, dict] = {}
    for key, val in tree.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if is_token(val):
            out[path] = val
        elif isinstance(val, dict):
            out.update(flatten(val, path))
    return out


# ---------------------------------------------------------------- resolving

def resolve_aliases(tokens: dict[str, dict]) -> dict[str, dict]:
    resolved: dict[str, dict] = {}
    stack: list[str] = []

    def resolve(name: str):
        if name in resolved:
            return resolved[name]
        if name not in tokens:
            raise KeyError(f"alias target not found: {{{name}}}")
        if name in stack:
            raise KeyError("alias cycle: " + " -> ".join(stack + [name]))
        stack.append(name)
        node = dict(tokens[name])
        value = node["$value"]
        if isinstance(value, str):
            m = ALIAS.match(value.strip())
            if m:
                target = resolve(m.group(1))
                node["$value"] = target["$value"]
                node.setdefault("$type", target.get("$type"))
                node["$alias"] = m.group(1)
        elif isinstance(value, dict) and "value" in value and "unit" in value:
            pass
        stack.pop()
        resolved[name] = node
        return node

    for name in tokens:
        resolve(name)
    return resolved


# ---------------------------------------------------------------- formatting

def kebab(name: str) -> str:
    name = name.replace("_", "-")
    name = re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", name)
    return name.replace(".", "-").lower()


def css_value(node: dict) -> str:
    v, t = node["$value"], node.get("$type", "")
    if t == "dimension" and isinstance(v, dict):
        return f"{v['value']}{v['unit']}"
    if t == "duration" and isinstance(v, dict):
        return f"{v['value']}{v['unit']}"
    if t == "fontFamily":
        fams = [f"'{f}'" if " " in f else f for f in v]
        return ", ".join(fams)
    if t == "shadow" and isinstance(v, dict):
        return (f"{v['offsetX']['value']}{v['offsetX']['unit']} "
                f"{v['offsetY']['value']}{v['offsetY']['unit']} "
                f"{v['blur']['value']}{v['blur']['unit']} "
                f"{v['spread']['value']}{v['spread']['unit']} {v['color']}")
    if isinstance(v, (int, float)):
        return str(v)
    return str(v)


def var_name(name: str) -> str:
    return "--ds-" + kebab(name)


def emit_css(tokens: dict[str, dict], selector: str, header: str) -> str:
    lines = [header, f"{selector} {{"]
    groups: dict[str, list[str]] = {}
    for name in sorted(tokens):
        top = name.split(".")[0]
        groups.setdefault(top, []).append(name)
    for top in sorted(groups):
        lines.append(f"  /* {top} */")
        for name in groups[top]:
            lines.append(f"  {var_name(name)}: {css_value(tokens[name])};")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append("}")
    return "\n".join(lines) + "\n"


def emit_tailwind(tokens: dict[str, dict]) -> str:
    def pick(prefix: str) -> dict:
        out = {}
        for name, node in tokens.items():
            if not name.startswith(prefix + "."):
                continue
            key = kebab(name[len(prefix) + 1:])
            out[key] = f"var({var_name(name)})"
        return out

    colors = {}
    for name in tokens:
        if name.startswith(("color.", "surface.", "text.", "border.", "brand.", "status.", "overlay.")):
            colors[kebab(name)] = f"var({var_name(name)})"

    theme = {
        "colors": colors,
        "spacing": pick("space"),
        "borderRadius": pick("radius"),
        "boxShadow": pick("shadow"),
        "fontFamily": pick("type.family"),
        "fontSize": pick("type.size"),
        "transitionDuration": pick("duration"),
    }
    body = json.dumps(theme, indent=2)
    return (
        "/** Signal — Tailwind preset (generated, do not edit) */\n"
        "module.exports = {\n"
        "  theme: {\n"
        "    extend: " + body.replace("\n", "\n    ") + "\n"
        "  }\n"
        "};\n"
    )


def emit_ts(tokens: dict[str, dict]) -> str:
    lines = ["/** Signal — token names (generated, do not edit) */", ""]
    lines.append("export const tokens = {")
    for name in sorted(tokens):
        lines.append(f"  '{name}': 'var({var_name(name)})',")
    lines.append("} as const;")
    lines.append("")
    lines.append("export type TokenName = keyof typeof tokens;")
    lines.append("")
    return "\n".join(lines)


def emit_office_theme(tokens: dict[str, dict]) -> str:
    """OOXML <a:clrScheme> + <a:fontScheme> block for .potx / .dotx themes."""
    def hexof(name: str) -> str:
        return css_value(tokens[name]).lstrip("#").upper()

    mapping = [
        ("dk1", "text.primary"),
        ("lt1", "surface.raised"),
        ("dk2", "brand.active"),
        ("lt2", "surface.base"),
        ("accent1", "brand.primary"),
        ("accent2", "brand.hover"),
        ("accent3", "status.success"),
        ("accent4", "status.warning"),
        ("accent5", "status.danger"),
        ("accent6", "color.sage.500"),
        ("hlink", "text.link"),
        ("folHlink", "color.olive.500"),
    ]
    clr = "\n".join(
        f'      <a:{slot}><a:srgbClr val="{hexof(tok)}"/></a:{slot}>' for slot, tok in mapping
    )
    heading = css_value(tokens["type.family.heading"]).split(",")[0].strip("'")
    body = css_value(tokens["type.family.body"]).split(",")[0].strip("'")
    return f"""<!-- Signal — paste into ppt/theme/theme1.xml (generated) -->
<a:clrScheme name="Signal">
{clr}
</a:clrScheme>
<a:fontScheme name="Signal">
  <a:majorFont>
    <a:latin typeface="{heading}"/>
    <a:ea typeface=""/>
    <a:cs typeface=""/>
  </a:majorFont>
  <a:minorFont>
    <a:latin typeface="{body}"/>
    <a:ea typeface=""/>
    <a:cs typeface=""/>
  </a:minorFont>
</a:fontScheme>
"""


# ---------------------------------------------------------------- contrast

def srgb_to_lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")[:6]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * srgb_to_lin(r) + 0.7152 * srgb_to_lin(g) + 0.0722 * srgb_to_lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


CHECKS = {
    "light": [
        ("text.primary on surface.base", "text.primary", "surface.base", 7.0),
        ("text.secondary on surface.base", "text.secondary", "surface.base", 4.5),
        ("text.on-brand on brand.primary", "text.on-brand", "brand.primary", 4.5),
        ("text.link on surface.base", "text.link", "surface.base", 4.5),
        ("brand.accent-text on surface.base", "brand.accent-text", "surface.base", 4.5),
        ("brand.accent-text on surface.raised", "brand.accent-text", "surface.raised", 4.5),
        ("status.success on surface.base", "status.success", "surface.base", 3.0),
        ("status.danger on surface.base", "status.danger", "surface.base", 3.0),
    ],
    "dark": [
        ("text.primary on surface.base", "text.primary", "surface.base", 7.0),
        ("text.secondary on surface.base", "text.secondary", "surface.base", 4.5),
        ("text.on-brand on brand.primary", "text.on-brand", "brand.primary", 4.5),
        ("text.link on surface.base", "text.link", "surface.base", 4.5),
        ("brand.accent-text on surface.base", "brand.accent-text", "surface.base", 4.5),
        ("brand.accent-text on surface.raised", "brand.accent-text", "surface.raised", 4.5),
        ("status.success on surface.base", "status.success", "surface.base", 3.0),
        ("status.danger on surface.base", "status.danger", "surface.base", 3.0),
    ],
}


def run_contrast(tokens: dict[str, dict], theme: str = "light") -> list[str]:
    problems = []
    for label, fg, bg, minimum in CHECKS.get(theme, CHECKS["light"]):
        if fg not in tokens or bg not in tokens:
            continue
        ratio = contrast(css_value(tokens[fg]), css_value(tokens[bg]))
        status = "ok" if ratio >= minimum else "FAIL"
        print(f"  {status:4} {label:42} {ratio:5.2f}:1  (min {minimum})")
        if ratio < minimum:
            problems.append(f"{theme}: {label}: {ratio:.2f}:1 < {minimum}:1")
    return problems


# ---------------------------------------------------------------- docs

def emit_docs(light: dict, dark: dict, label: str = "navy / teal / sage / olive / ivory") -> str:
    def swatches(tokens, prefix):
        rows = []
        for name in sorted(tokens):
            if not name.startswith(prefix + "."):
                continue
            val = css_value(tokens[name])
            if not val.startswith("#"):
                continue
            fg = "#12304F" if luminance(val) > 0.45 else "#FFFFFF"
            rows.append(
                f'<div class="sw"><div class="chip" style="background:{val};color:{fg}">'
                f'<span>{name}</span><span>{val}</span></div></div>'
            )
        return "\n".join(rows)

    def type_rows(tokens):
        rows = []
        for key in ["display", "h1", "h2", "h3", "h4", "body-lg", "body", "body-sm", "caption", "label"]:
            name = f"type.size.{key}"
            if name in tokens:
                size = css_value(tokens[name])
                fam = css_value(tokens["type.family.heading"] if key.startswith(("display", "h")) else tokens["type.family.body"])
                rows.append(
                    f'<div class="tr"><code>type.size.{key}</code>'
                    f'<span style="font-family:{fam};font-size:{size};line-height:1.25">Commissioning Report</span>'
                    f'<em>{size}</em></div>'
                )
        return "\n".join(rows)

    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>Signal — pitch deck system</title>
<link rel="stylesheet" href="../css/tokens.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--ds-surface-base);color:var(--ds-text-primary);
  font-family:var(--ds-type-family-body);font-size:var(--ds-type-size-body);line-height:var(--ds-type-leading-relaxed);
  max-width:1000px;margin:0 auto;padding:var(--ds-space-11) var(--ds-space-8)}}
h1{{font-family:var(--ds-type-family-heading);font-size:var(--ds-type-size-h1);line-height:var(--ds-type-leading-tight);
  letter-spacing:var(--ds-type-tracking-tight);margin-bottom:var(--ds-space-3)}}
h2{{font-family:var(--ds-type-family-heading);font-size:var(--ds-type-size-h2);margin:var(--ds-space-10) 0 var(--ds-space-5);
  padding-top:var(--ds-space-5);border-top:1px solid var(--ds-border-subtle)}}
h3{{font-size:var(--ds-type-size-h4);margin:var(--ds-space-7) 0 var(--ds-space-3)}}
p.lead{{color:var(--ds-text-secondary);max-width:640px;margin-bottom:var(--ds-space-8)}}
.kicker{{font-family:var(--ds-type-family-mono);font-size:var(--ds-type-size-label);letter-spacing:var(--ds-type-tracking-caps);
  text-transform:uppercase;color:var(--ds-text-secondary);margin-bottom:var(--ds-space-4)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:var(--ds-space-3)}}
.chip{{border:1px solid var(--ds-border-subtle);border-radius:var(--ds-radius-md);padding:var(--ds-space-4);
  display:flex;flex-direction:column;gap:2px;font-family:var(--ds-type-family-mono);font-size:10.5px;min-height:74px;justify-content:flex-end}}
.tr{{display:flex;align-items:baseline;gap:var(--ds-space-5);padding:var(--ds-space-3) 0;border-bottom:1px solid var(--ds-border-subtle)}}
.tr code{{font-family:var(--ds-type-family-mono);font-size:11px;color:var(--ds-text-secondary);width:180px;flex:none}}
.tr em{{font-family:var(--ds-type-family-mono);font-size:11px;color:var(--ds-text-secondary);margin-left:auto;font-style:normal}}
.demo{{display:flex;gap:var(--ds-space-4);align-items:center;flex-wrap:wrap;margin:var(--ds-space-4) 0}}
.btn{{font-family:var(--ds-type-family-body);font-size:var(--ds-type-size-body-sm);font-weight:600;
  padding:var(--ds-space-4) var(--ds-space-6);border-radius:var(--ds-radius-md);border:1px solid transparent;cursor:pointer}}
.btn.p{{background:var(--ds-brand-primary);color:var(--ds-text-on-brand)}}
.btn.p:hover{{background:var(--ds-brand-hover)}}
.btn.s{{background:transparent;color:var(--ds-text-primary);border-color:var(--ds-border-default)}}
.card{{background:var(--ds-surface-raised);border:1px solid var(--ds-border-subtle);border-radius:var(--ds-radius-md);
  padding:var(--ds-space-7);box-shadow:var(--ds-shadow-sm);flex:1;min-width:240px}}
.card h4{{font-family:var(--ds-type-family-heading);font-size:var(--ds-type-size-h4);margin-bottom:var(--ds-space-2)}}
.card p{{font-size:var(--ds-type-size-body-sm);color:var(--ds-text-secondary);line-height:var(--ds-type-leading-normal)}}
.tag{{display:inline-block;font-family:var(--ds-type-family-mono);font-size:10px;letter-spacing:var(--ds-type-tracking-wide);
  text-transform:uppercase;padding:3px var(--ds-space-3);border-radius:var(--ds-radius-sm);
  background:var(--ds-brand-subtle);color:var(--ds-brand-primary);margin-top:var(--ds-space-4)}}
table{{width:100%;border-collapse:collapse;font-size:var(--ds-type-size-body-sm);margin-top:var(--ds-space-4)}}
th{{text-align:left;font-family:var(--ds-type-family-mono);font-size:10px;letter-spacing:var(--ds-type-tracking-wide);
  text-transform:uppercase;color:var(--ds-table-header-fg);padding:var(--ds-space-3) 0;border-bottom:1px solid var(--ds-table-row-border);font-weight:500}}
td{{padding:var(--ds-space-4) 0;border-bottom:1px solid var(--ds-table-row-border)}}
tbody tr:hover{{background:var(--ds-table-row-hover-bg)}}
.meta{{font-family:var(--ds-type-family-mono);font-size:11px;color:var(--ds-text-secondary);margin-top:var(--ds-space-11)}}
</style></head><body>
<div class="kicker">Signal · v0.7.0 · {label}</div>
<h1>Signal</h1>
<p class="lead">Gabungan dua bahasa: disiplin deck pitch (satu ide per slide, display besar) dan bahasa infografik (garis hairline, label small-caps, modul bernomor). Nilai mentah hanya hidup di lapis core.</p>

<h2>Surface &amp; text</h2>
<div class="grid">
{swatches(light, "surface")}
{swatches(light, "text")}
</div>

<h2>Brand</h2>
<div class="grid">
{swatches(light, "brand")}
</div>

<h2>Status</h2>
<div class="grid">
{swatches(light, "status")}
</div>

<h2>Type scale</h2>
{type_rows(light)}

<h2>Components</h2>
<div class="demo">
  <button class="btn p">Primary action</button>
  <button class="btn s">Secondary</button>
  <div class="card"><h4>Card title</h4><p>Surface, border, radius, dan shadow semuanya dari token — tidak ada nilai hardcoded.</p><span class="tag">status · active</span></div>
</div>

<h2>Data table</h2>
<table><thead><tr><th>Equipment</th><th>Status</th><th>Verified</th></tr></thead>
<tbody>
<tr><td>Chiller CH-01</td><td>Passed</td><td>24 Nov 2026</td></tr>
<tr><td>AHU-03</td><td>Pending</td><td>—</td></tr>
</tbody></table>

<p class="meta">Generated by build/build.py — jangan edit dist/ secara manual.</p>
</body></html>
"""


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate tokens only")
    args = ap.parse_args()

    core_paths = list((TOKENS / "core").glob("*.json"))
    comp_paths = list((TOKENS / "component").glob("*.json"))
    # semantic files are named <palette>.<mode>.tokens.json -> key "professional.light"
    theme_paths = {p.stem.replace(".tokens", ""): p
                   for p in sorted((TOKENS / "semantic").glob("*.tokens.json"))}

    core = flatten(load_tree(core_paths))
    comp_raw = flatten(load_tree(comp_paths))
    themes = {name: flatten(load_tree([p])) for name, p in theme_paths.items() if p.exists()}

    print(f"tokens: core={len(core)} component={len(comp_raw)} "
          + " ".join(f"{k}={len(v)}" for k, v in themes.items()))

    built = {}
    for theme, sem in themes.items():
        merged = {**core, **sem, **comp_raw}
        built[theme] = resolve_aliases(merged)

    print("\ncontrast checks:")
    problems = []
    for theme in built:
        print(f" [{theme}]")
        problems += run_contrast(built[theme], theme.split(".")[-1])

    if args.check:
        if problems:
            print("\nFAILED: " + "; ".join(problems))
            return 1
        print("\nAll checks passed.")
        return 0

    for sub in ["css", "tailwind", "ts", "json", "office", "docs"]:
        (DIST / sub).mkdir(parents=True, exist_ok=True)

    palettes = sorted({k.split(".")[0] for k in built})
    default = "professional" if "professional" in palettes else palettes[0]
    written: set[pathlib.Path] = set()

    def key(palette, mode):
        return f"{palette}.{mode}"

    # one CSS file per palette; the default palette also owns :root
    for palette in palettes:
        light_k, dark_k = key(palette, "light"), key(palette, "dark")
        if palette == default:
            name, root_sel = "tokens.css", ":root"
        else:
            name, root_sel = f"tokens-{palette}.css", f'[data-palette="{palette}"]'
        if light_k not in built:
            continue
        blocks = [emit_css(built[light_k], root_sel,
                           f"/* Signal — {palette} (generated) */\n")]
        if dark_k in built:
            sel = '[data-theme="dark"]' if palette == default else \
                  f'[data-palette="{palette}"][data-theme="dark"]'
            blocks.append(emit_css(built[dark_k], sel,
                                   f"/* Signal — {palette} dark (generated) */\n"))
        path = DIST / "css" / name
        path.write_text("\n".join(blocks), encoding="utf-8")
        written.add(path)

    for palette in palettes:
        k = key(palette, "light")
        if k not in built:
            continue
        suffix = "" if palette == default else f"-{palette}"
        for rel, text in (
            (f"tailwind/preset{suffix}.js", emit_tailwind(built[k])),
            (f"ts/tokens{suffix}.ts", emit_ts(built[k])),
            (f"office/theme-scheme{suffix}.xml", emit_office_theme(built[k])),
        ):
            path = DIST / rel
            path.write_text(text, encoding="utf-8")
            written.add(path)
        label = "navy / teal / sage / olive / ivory" if palette == "professional" \
                else "cream / sand / orange / charcoal"
        path = DIST / "docs" / f"index{suffix}.html"
        path.write_text(emit_docs(built[k], built.get(key(palette, "dark"), {}), label),
                        encoding="utf-8")
        written.add(path)

    json_path = DIST / "json" / "tokens.resolved.json"
    json_path.write_text(
        json.dumps({k: {n: v.get("$value") for n, v in t.items()} for k, t in built.items()},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    written.add(json_path)

    # dist/ must contain exactly what this run generated; anything else is stale
    # from an older emitter (e.g. the retired tokens-dark.css) and would ship
    # wrong values that no contrast check ever sees.
    for stale in sorted(set(DIST.rglob("*")) - written):
        if stale.is_file():
            stale.unlink()
            print(f"removed stale {stale.relative_to(DIST)}")

    count = sum(len(p.read_text(encoding="utf-8")) for p in DIST.rglob("*") if p.is_file())
    print(f"\nwrote {len(list(DIST.rglob('*.*')))} files, {count:,} bytes into dist/")
    if problems:
        print("WARNING: contrast failures: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
