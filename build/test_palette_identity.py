#!/usr/bin/env python3
"""MI-1B — palette identity tests (17 cases).

Covers the three call-site fixes from MI-1A, the semantic gate from
``validate_palette_identity.py``, and the negative controls that prove the gate
cannot pass everything.

Taxonomy (verified against ``build/compat.py``):

* renderer palettes: professional, adventurous -> 2 x 2 appearances = 4 HTML cells
* document types (CSS/dist): professional, adventurous, consulting -> 3 x 2 = 6 cells
* ``consulting`` is a document type, never a palette (``compat.validate_palette`` raises)

Run: ``python build/test_palette_identity.py -v``

Two import-time facts drive the harness design:

* ``preview.PALETTE`` / ``analyst.PALETTE`` (and the analyst ``FOOT`` f-string) are
  evaluated at import from ``sys.argv``. Any test that asserts the footer must set
  ``sys.argv`` *before* importing the module, so those cases run in a subprocess.
* ``analyst.render_html`` and ``preview.build`` take keyword-only ``palette=`` and
  default to ``compat.DEFAULT_PALETTE``; passing ``None`` is the no-argument path.

Nothing here writes into the repository: every render goes to a temp directory,
and the CLI cases run against a sandbox copy of the tree.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
FIXTURES = BUILD / "fixtures" / "mi1"
sys.path.insert(0, str(BUILD))

# Neutralise argv before importing the renderers: preview/analyst/atlas evaluate
# their palette (and the analyst footer f-string) at import time from sys.argv[1],
# so a unittest flag like ``-v`` would otherwise be parsed as a palette.
_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
import analyst  # noqa: E402
import atlas  # noqa: E402
import compat  # noqa: E402
import css_gen  # noqa: E402
import preview  # noqa: E402
import validate_palette_identity as V  # noqa: E402

sys.argv = _argv

PALETTES = ("professional", "adventurous")
APPEARANCES = ("light", "dark")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ independent view
#
# These helpers deliberately share no code with ``validate_palette_identity``: the
# expected values come straight from the resolved token file, and the artifact is
# read with plain regexes. A parser bug in the validator therefore cannot make an
# assertion pass (O-5).

TOKENS_JSON = ROOT / "dist" / "json" / "tokens.resolved.json"


def independent_tokens(path: Path = TOKENS_JSON) -> dict:
    """Read the authoritative resolved token cells directly from JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def independent_identity(text: str) -> tuple:
    """(data-palette, data-theme, title) via regex only."""
    tag = re.search(r"<html\b[^>]*>", text)
    attrs = dict(re.findall(r'([a-z-]+)="([^"]*)"', tag.group(0))) if tag else {}
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    return attrs.get("data-palette"), attrs.get("data-theme"), (title.group(1).strip() if title else None)


def independent_var(text: str, palette: str, appearance: str, name: str) -> str | None:
    """Value of ``--ds-<name>`` inside the scoped block, via regex only."""
    block = re.search(
        r'\[data-palette="%s"\]\[data-theme="%s"\]\s*\{(.*?)\n\}'
        % (re.escape(palette), re.escape(appearance)),
        text,
        re.S,
    )
    if not block:
        return None
    decl = re.search(r"--ds-%s\s*:\s*([^;]+);" % re.escape(name.replace(".", "-")), block.group(1))
    return decl.group(1).strip() if decl else None


def independent_cell(text: str, palette: str, appearance: str, tokens: dict) -> dict:
    """All three representative values for one cell, expected side read from JSON."""
    cell = tokens[f"{palette}.{appearance}"]
    return {
        name: (independent_var(text, palette, appearance, name), cell[name])
        for name in ("surface.base", "brand.primary", "text.primary")
    }


def render_preview(out_dir: Path, *, palette=None, appearance=None) -> Path:
    """Render a preview deck into *out_dir*, bypassing the repo examples/ path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"preview-{palette or compat.DEFAULT_PALETTE}.html"
    target = out_dir / name
    preview.build(target, palette=palette, appearance=appearance)
    return target


def render_analyst_html(out_dir: Path, *, palette=None, appearance=None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"preview-analyst-{palette or compat.DEFAULT_PALETTE}.html"
    target = out_dir / name
    analyst.render_html(target, palette=palette, appearance=appearance)
    return target


def run_py(script: str, *, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(Path.home())},
        timeout=180,
    )


class PaletteIdentityTests(unittest.TestCase):
    """T-01 .. T-14."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = V.load_tokens()
        cls.tmp = Path(tempfile.mkdtemp(prefix="mi1b_tests_"))
        cls.out = cls.tmp / "out"
        cls.sandbox = cls.tmp / "sandbox"
        cls._make_sandbox()
        cls.official_atlas = {
            p.name: sha(p) for p in (ROOT / "examples").glob("preview-atlas-*.html")
        } | {p.name: sha(p) for p in (ROOT / "examples").glob("atlas-*.pptx")}

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def _make_sandbox(cls) -> None:
        cls.sandbox.mkdir(parents=True)
        shutil.copytree(BUILD, cls.sandbox / "build", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "tokens", cls.sandbox / "tokens")
        shutil.copytree(ROOT / "dist", cls.sandbox / "dist")
        (cls.sandbox / "examples").mkdir()
        shutil.copytree(ROOT / "examples" / "photos", cls.sandbox / "examples" / "photos")

    # ---------------------------------------------------------------- T-01 .. T-03

    def test_T01_preview_cli_forwards_palette(self) -> None:
        """T-01: preview.main(["adventurous"]) renders adventurous, not professional."""
        old = preview.ROOT
        preview.ROOT = self.tmp / "t01"
        (preview.ROOT / "examples").mkdir(parents=True, exist_ok=True)
        try:
            preview.main(["adventurous"])
            out = preview.ROOT / "examples" / "preview-adventurous.html"
        finally:
            preview.ROOT = old
        ident = V.html_identity(out.read_text(encoding="utf-8"))
        self.assertEqual(ident["palette"], "adventurous")
        self.assertEqual(V.check_html(out, "adventurous", self.tokens), [])

    def test_T02_analyst_cli_forwards_palette_and_footer(self) -> None:
        """T-02: argv set before import -> adventurous HTML, adventurous footer, pptx written."""
        target = self.tmp / "t02"
        (target / "examples").mkdir(parents=True, exist_ok=True)
        script = f"""
import pathlib, sys
sys.argv = ["analyst.py", "adventurous"]
sys.path.insert(0, {str(BUILD)!r})
import analyst
analyst.ROOT = pathlib.Path({str(target)!r})
analyst.main()
"""
        proc = run_py(script)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        html = target / "examples" / "preview-analyst-adventurous.html"
        pptx = target / "examples" / "analyst-adventurous.pptx"
        self.assertTrue(html.exists(), "adventurous HTML not written")
        self.assertTrue(pptx.exists(), "adventurous PPTX not written")
        ident = V.html_identity(html.read_text(encoding="utf-8"))
        self.assertEqual(ident["palette"], "adventurous")
        self.assertIn("palet adventurous", html.read_text(encoding="utf-8"))
        self.assertEqual(V.check_html(html, "adventurous", self.tokens), [])

    def test_T03_atlas_cli_forwards_palette_without_touching_official_artifacts(self) -> None:
        """T-03: `atlas.py adventurous` in a sandbox renders adventurous; repo artifacts untouched."""
        before = {p.name: sha(p) for p in (ROOT / "examples").glob("*atlas*")}
        proc = subprocess.run(
            [sys.executable, "build/atlas.py", "adventurous"],
            cwd=str(self.sandbox),
            capture_output=True,
            text=True,
            timeout=300,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(Path.home())},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        html = self.sandbox / "examples" / "preview-atlas-adventurous.html"
        self.assertTrue(html.exists(), "atlas sandbox HTML missing")
        self.assertEqual(V.html_identity(html.read_text(encoding="utf-8"))["palette"], "adventurous")
        self.assertEqual(V.check_html(html, "adventurous", self.tokens), [])
        after = {p.name: sha(p) for p in (ROOT / "examples").glob("*atlas*")}
        self.assertEqual(before, after, "official atlas artifacts changed")
        # source guard: the forwarding expression must stay explicit
        self.assertIn("palette=A.PALETTE", (BUILD / "atlas.py").read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- T-04 .. T-06

    def test_T04_preview_build_explicit_palette(self) -> None:
        """T-04: preview.build(palette="adventurous") is adventurous, not professional."""
        out = render_preview(self.out / "t04", palette="adventurous")
        ident = V.html_identity(out.read_text(encoding="utf-8"))
        self.assertEqual((ident["palette"], ident["appearance"]), ("adventurous", "dark"))
        self.assertEqual(V.check_html(out, "adventurous", self.tokens), [])

    def test_T05_analyst_render_html_explicit_palette(self) -> None:
        """T-05: analyst.render_html(palette="adventurous") is adventurous."""
        out = render_analyst_html(self.out / "t05", palette="adventurous")
        ident = V.html_identity(out.read_text(encoding="utf-8"))
        self.assertEqual((ident["palette"], ident["appearance"]), ("adventurous", "light"))
        self.assertEqual(V.check_html(out, "adventurous", self.tokens), [])

    def test_T06_no_argument_defaults_to_professional(self) -> None:
        """T-06: palette=None on both renderers -> compat.DEFAULT_PALETTE (professional)."""
        prev = render_preview(self.out / "t06", palette=None)
        ana = render_analyst_html(self.out / "t06", palette=None)
        self.assertEqual(V.html_identity(prev.read_text(encoding="utf-8"))["palette"], "professional")
        self.assertEqual(V.html_identity(ana.read_text(encoding="utf-8"))["palette"], "professional")
        self.assertEqual(V.check_html(prev, "professional", self.tokens), [])
        self.assertEqual(V.check_html(ana, "professional", self.tokens), [])

    # ---------------------------------------------------------------- T-07 .. T-08

    def test_T07_preview_all_four_cells(self) -> None:
        """T-07: 2 palettes x 2 appearances, expectations derived independently of the validator."""
        tokens = independent_tokens()
        for palette in PALETTES:
            for appearance in APPEARANCES:
                with self.subTest(palette=palette, appearance=appearance):
                    out = render_preview(self.out / "t07", palette=palette, appearance=appearance)
                    text = out.read_text(encoding="utf-8")
                    got_palette, got_appearance, title = independent_identity(text)
                    self.assertEqual((got_palette, got_appearance), (palette, appearance))
                    self.assertIn(palette, (title or "").lower())
                    for name, (got, want) in independent_cell(text, palette, appearance, tokens).items():
                        self.assertIsNotNone(got, f"{palette}.{appearance}: --ds-{name} absent")
                        self.assertEqual(got.lower(), want.lower(), f"{palette}.{appearance}: {name}")
                    self.assertEqual(V.check_html(out, palette, self.tokens), [])

    def test_T08_analyst_all_four_cells(self) -> None:
        """T-08: same 4-cell sweep for the analyst HTML renderer."""
        tokens = independent_tokens()
        for palette in PALETTES:
            for appearance in APPEARANCES:
                with self.subTest(palette=palette, appearance=appearance):
                    out = render_analyst_html(self.out / "t08", palette=palette, appearance=appearance)
                    text = out.read_text(encoding="utf-8")
                    self.assertEqual(independent_identity(text)[:2], (palette, appearance))
                    for name, (got, want) in independent_cell(text, palette, appearance, tokens).items():
                        self.assertIsNotNone(got, f"{palette}.{appearance}: --ds-{name} absent")
                        self.assertEqual(got.lower(), want.lower(), f"{palette}.{appearance}: {name}")
                    self.assertEqual(V.check_html(out, palette, self.tokens), [])

    # ---------------------------------------------------------------- T-09 .. T-13

    def test_T09_validator_accepts_correct_artifacts(self) -> None:
        """T-09: the gate passes real professional artifacts and freshly rendered adventurous ones."""
        pro_prev = ROOT / "examples" / "preview-professional.html"
        pro_ana = ROOT / "examples" / "preview-analyst-professional.html"
        self.assertEqual(V.check_html(pro_prev, "professional", self.tokens), [])
        self.assertEqual(V.check_html(pro_ana, "professional", self.tokens), [])
        adv_prev = render_preview(self.out / "t09", palette="adventurous")
        adv_ana = render_analyst_html(self.out / "t09", palette="adventurous")
        self.assertEqual(V.check_html(adv_prev, "adventurous", self.tokens), [])
        self.assertEqual(V.check_html(adv_ana, "adventurous", self.tokens), [])
        for doc_type, filename in V.CSS_FILES.items():
            self.assertEqual(V.check_css(ROOT / "dist" / "css" / filename, doc_type, self.tokens), [])

    def test_T10_defective_fixture_rejected(self) -> None:
        """T-10: mi1_tmp/A_default.html (professional content) must fail as adventurous."""
        failures = V.check_html(FIXTURES / "A_default.html", "adventurous", self.tokens)
        self.assertTrue(failures)
        self.assertTrue(any("data-palette" in f for f in failures), failures)

    def test_T11_wrong_data_palette_rejected(self) -> None:
        """T-11: flipping data-palette on a correct file must fail."""
        tampered = self.tmp / "t11_flipped.html"
        tampered.write_text(
            (FIXTURES / "B_explicit.html").read_text(encoding="utf-8").replace(
                'data-palette="adventurous"', 'data-palette="professional"', 1
            ),
            encoding="utf-8",
        )
        self.assertTrue(V.check_html(tampered, "adventurous", self.tokens))

    def test_T12_wrong_token_value_rejected(self) -> None:
        """T-12: substituting professional's surface.base into an adventurous file must fail."""
        adv = V.expected_values(self.tokens, "adventurous", "light")["surface.base"]
        pro = V.expected_values(self.tokens, "professional", "light")["surface.base"]
        tampered = self.tmp / "t12_surface.html"
        tampered.write_text((FIXTURES / "B_explicit.html").read_text(encoding="utf-8").replace(adv, pro), encoding="utf-8")
        failures = V.check_html(tampered, "adventurous", self.tokens)
        self.assertTrue(any("surface.base" in f for f in failures), failures)

    def test_T13_palette_collapse_rejected(self) -> None:
        """T-13: two artifacts that collapse onto one palette must fail distinctness."""
        collapsed = self.tmp / "t13_adventurous.html"
        collapsed.write_bytes((ROOT / "examples" / "preview-professional.html").read_bytes())
        failures = V.check_distinct(ROOT / "examples" / "preview-professional.html", collapsed, self.tokens)
        self.assertTrue(any("collapse" in f for f in failures), failures)
        # and the real, corrected pair is now distinct
        real = V.check_distinct(
            ROOT / "examples" / "preview-analyst-professional.html",
            ROOT / "examples" / "preview-analyst-adventurous.html",
            self.tokens,
        )
        self.assertEqual(real, [])

    # ---------------------------------------------------------------------- T-14

    def test_T14_end_to_end_cli_in_sandbox(self) -> None:
        """T-14: `python build/preview.py adventurous` in a sandbox writes adventurous HTML."""
        proc = subprocess.run(
            [sys.executable, "build/preview.py", "adventurous"],
            cwd=str(self.sandbox),
            capture_output=True,
            text=True,
            timeout=300,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(Path.home())},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = self.sandbox / "examples" / "preview-adventurous.html"
        self.assertTrue(out.exists())
        ident = V.html_identity(out.read_text(encoding="utf-8"))
        self.assertEqual(ident["palette"], "adventurous")
        self.assertEqual(V.check_html(out, "adventurous", self.tokens), [])
        # the sandbox's own professional twin, rendered the same way, stays professional
        proc = subprocess.run(
            [sys.executable, "build/preview.py"],
            cwd=str(self.sandbox),
            capture_output=True,
            text=True,
            timeout=300,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(Path.home())},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        pro = self.sandbox / "examples" / "preview-professional.html"
        self.assertEqual(V.html_identity(pro.read_text(encoding="utf-8"))["palette"], "professional")


    # ------------------------------------------------------------------ T-15 .. T-17

    def test_T15_palette_guard_rejects_unsupported_identities(self) -> None:
        """T-15: only supported palettes are accepted; 'consulting' is rejected as a document type."""
        for good in PALETTES:
            self.assertEqual(V.require_palette(good), good)
        # A value-complete professional artifact is accepted (D-3 scope: all 191 declarations).
        self.assertEqual(V.check_html(ROOT / "examples" / "preview-professional.html", "professional", self.tokens), [])

        for bad, needle in (
            ("consulting", "document type, not a palette"),
            ("Professional", "unsupported palette"),
            ("adventurous ", "unsupported palette"),
            ("corporate", "unsupported palette"),
            ("", "unsupported palette"),
            # None is not a palette identity: the message must name it, and both
            # check_html calls below must still refuse before touching the path.
            # ``cast`` is typing-only — at runtime the value stays None, which is the
            # invalid input this case exists to exercise.
            (cast(str, None), "unsupported palette None"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    V.require_palette(bad)
                message = str(ctx.exception)
                self.assertIn(needle, message)
                self.assertIn("professional, adventurous", message)
                # check_html must refuse the same values, before it touches the filesystem
                with self.assertRaises(ValueError):
                    V.check_html(FIXTURES / "B_explicit.html", bad, self.tokens)
                with self.assertRaises(ValueError):
                    V.check_html(Path("/nonexistent/none.html"), bad, self.tokens)

    def test_T16_professional_explicit_fixture_accepted(self) -> None:
        """T-16: mi1_tmp/C_explicit_prof.html is colour-identical but structured-incomplete.

        Pre-F-3 fixtures serialized only scalar strings: the 64 structured declarations
        per cell (dimensions, shadows, font-family lists) still carry raw Python reprs
        such as ``{'value': 1, 'unit': 'px'}``. Under the 3-token scope of T-16's
        original form the fixture passed; under D-3's 191-declaration scope it must be
        rejected, and exactly on those 64 declarations per cell (128 total). The
        colour declarations remain value-exact, which is what this test pins.
        """
        tokens = independent_tokens()
        text = (FIXTURES / "C_explicit_prof.html").read_text(encoding="utf-8")
        self.assertEqual(independent_identity(text)[0], "professional")
        self.assertIn(independent_identity(text)[1], APPEARANCES)
        for appearance in APPEARANCES:
            for name, (got, want) in independent_cell(text, "professional", appearance, tokens).items():
                self.assertIsNotNone(got, f"professional.{appearance}: --ds-{name} absent")
                self.assertEqual(got.lower(), want.lower(), f"professional.{appearance}: {name}")

        failures = V.check_html(FIXTURES / "C_explicit_prof.html", "professional", self.tokens)
        self.assertEqual(len(failures), 128, failures[:3])
        # 61 dict-valued + 3 list-valued tokens are the declarations the pre-F-3
        # fixture never serialized; the 13 int/float tokens (z, weights, leading)
        # went through ``str(value)`` and do match.
        structured = {
            n
            for n, v in tokens["professional.light"].items()
            if isinstance(v, (dict, list))
        }
        self.assertEqual(len(structured), 64)
        for message in failures:
            match = re.search(r"\(([a-z0-9.\-]+)\)", message)
            self.assertIsNotNone(match, message)
            self.assertIn(match.group(1), structured, message)
            self.assertIn("but professional.", message)
        # The value-complete professional artifact is the accepted positive control.
        self.assertEqual(V.check_html(ROOT / "examples" / "preview-professional.html", "professional", self.tokens), [])

    def test_T17_all_six_fixtures_accounted_for(self) -> None:
        """T-17: every preserved fixture has an explicit expected verdict, including Atlas.

        F_atlas.html is analyst-shaped output from the atlas path (``atlas.py`` calls
        ``analyst.render_html``): it carries ``data-palette="professional"`` and scoped
        token blocks, so it is structurally inside the semantic contract — and it is a
        defective fixture for an *adventurous* expectation. The preserved official
        ``examples/preview-atlas-*.html`` are a different, legacy format (inline styles,
        no ``data-palette``, no ``--ds-`` properties) and are therefore outside the
        contract; that exclusion is asserted below rather than assumed.
        """
        expectations = {
            "A_default.html": ("adventurous", False),
            # B/C/E are pre-F-3 fixtures: colour-exact, but their 64 structured
            # declarations per cell are raw Python reprs (the F-3 defect). The
            # value-complete gate must reject them; see the count assertions below.
            "B_explicit.html": ("adventurous", False),
            "C_explicit_prof.html": ("professional", False),
            "D_default.html": ("adventurous", False),
            "E_explicit.html": ("adventurous", False),
            "F_atlas.html": ("adventurous", False),
        }
        self.assertEqual(sorted(p.name for p in FIXTURES.glob("*.html")), sorted(expectations))
        for name, (palette, should_pass) in expectations.items():
            with self.subTest(fixture=name):
                failures = V.check_html(FIXTURES / name, palette, self.tokens)
                self.assertEqual(not failures, should_pass, failures)

        # The three pre-F-3 fixtures fail on exactly the structured half of each cell.
        for name, palette in (
            ("B_explicit.html", "adventurous"),
            ("C_explicit_prof.html", "professional"),
            ("E_explicit.html", "adventurous"),
        ):
            with self.subTest(structured=name):
                failures = V.check_html(FIXTURES / name, palette, self.tokens)
                self.assertEqual(len(failures), 128, failures[:3])
                self.assertTrue(all("={" in message or "=['" in message for message in failures))

        # Atlas fixture: analyst-shaped, professional-labelled — hence rejected for adventurous.
        atlas_text = (FIXTURES / "F_atlas.html").read_text(encoding="utf-8")
        self.assertEqual(independent_identity(atlas_text)[:2], ("professional", "light"))
        self.assertIn('--ds-surface-base: #E9E5D9', atlas_text)
        self.assertNotIn('[data-palette="adventurous"]', atlas_text)

        # Official atlas HTML: legacy inline-style render, structurally outside the contract.
        for name in ("preview-atlas-professional.html", "preview-atlas-adventurous.html"):
            text = (ROOT / "examples" / name).read_text(encoding="utf-8")
            with self.subTest(atlas=name):
                self.assertIsNone(independent_identity(text)[0])
                self.assertNotIn("--ds-", text)
                self.assertIn('style="background:', text)


# ------------------------------------------------- D-3 value-complete validation
#
# The gate compares all 191 declarations per cell against the generator's own
# serializer. These tests exercise that scope end to end: every artifact, every
# palette x appearance cell, and each of the four defect classes the comparator
# reports (wrong value, missing, extra, duplicate).


def scoped_body(text: str, palette: str, appearance: str) -> str | None:
    """Raw body of the ``[data-palette][data-theme]`` block, via regex only."""
    match = re.search(
        r'\[data-palette="%s"\]\[data-theme="%s"\]\s*\{(.*?)\n\}'
        % (re.escape(palette), re.escape(appearance)),
        text,
        re.S,
    )
    return match.group(1) if match else None


def edit_scoped(text: str, palette: str, appearance: str, var: str, new_value: str | None) -> str:
    """Set (or, when *new_value* is None, delete) one declaration inside one block."""
    pattern = re.compile(
        r'(\[data-palette="%s"\]\[data-theme="%s"\]\s*\{)(.*?)(\n\})'
        % (re.escape(palette), re.escape(appearance)),
        re.S,
    )

    def rewrite(match: "re.Match[str]") -> str:
        body = match.group(2)
        decl = re.compile(r"[ \t]*%s\s*:\s*[^;]+;" % re.escape(var))
        assert decl.search(body), var
        body = decl.sub("" if new_value is None else f" {var}: {new_value};", body, count=1)
        return match.group(1) + body + match.group(3)

    new_text, count = pattern.subn(rewrite, text, count=1)
    assert count == 1, (palette, appearance)
    return new_text


def insert_scoped(text: str, palette: str, appearance: str, declaration: str) -> str:
    """Append a raw declaration line inside one block (for extra/duplicate cases)."""
    pattern = re.compile(
        r'(\[data-palette="%s"\]\[data-theme="%s"\]\s*\{)(.*?)(\n\})'
        % (re.escape(palette), re.escape(appearance)),
        re.S,
    )
    new_text, count = pattern.subn(
        lambda m: m.group(1) + m.group(2) + f"\n  {declaration}" + m.group(3), text, count=1
    )
    assert count == 1, (palette, appearance)
    return new_text


class D3ValueCompleteTests(unittest.TestCase):
    """D-3-01 .. D-3-14: 191-declaration coverage, defect classes, mutations."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = V.load_tokens()
        cls.tmp = Path(tempfile.mkdtemp(prefix="d3_tests_"))

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _write(self, name: str, text: str) -> Path:
        out = self.tmp / name
        out.write_text(text, encoding="utf-8")
        return out

    def _artifact(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    # ------------------------------------------------------------------ positives

    def test_D3_01_every_html_cell_validates_all_191_declarations(self) -> None:
        """D-3-01: all four HTML artifacts pass, and each scoped block carries 191 declarations."""
        self.assertEqual(len(V.HTML_TARGETS), 4)
        for rel, palette in V.HTML_TARGETS:
            path = ROOT / rel
            with self.subTest(artifact=rel):
                self.assertEqual(V.check_html(path, palette, self.tokens), [])
                text = path.read_text(encoding="utf-8")
                for appearance in APPEARANCES:
                    expected = V.expected_declarations(self.tokens, palette, appearance)
                    self.assertEqual(len(expected), 191, appearance)
                    body = scoped_body(text, palette, appearance)
                    self.assertIsNotNone(body, f"{rel}: no {palette}.{appearance} block")
                    got = V.declarations(body)
                    self.assertEqual(len(got), 191, f"{rel}: {palette}.{appearance}")
                    self.assertEqual(
                        {name for name, _ in got}, set(expected), f"{rel}: {palette}.{appearance} names"
                    )

    def test_D3_02_every_css_cell_validates_all_191_declarations(self) -> None:
        """D-3-02: all three dist CSS files pass with 2 x 191 declarations each."""
        for doc_type, filename in V.CSS_FILES.items():
            path = V.CSS_DIR / filename
            with self.subTest(css=filename):
                self.assertEqual(V.check_css(path, doc_type, self.tokens), [])
                self.assertEqual(len(V.declarations(path.read_text(encoding="utf-8"))), 382)
                for appearance in APPEARANCES:
                    self.assertEqual(len(V.expected_declarations(self.tokens, doc_type, appearance)), 191)

    def test_D3_03_expected_declarations_cover_every_cell_identically(self) -> None:
        """D-3-03: six cells, same 191 variable names, no unserialized structure leaks."""
        cells = [(d, a) for d in V.DOCUMENT_TYPES for a in APPEARANCES]
        self.assertEqual(len(cells), 6)
        reference = None
        for doc_type, appearance in cells:
            expected = V.expected_declarations(self.tokens, doc_type, appearance)
            with self.subTest(cell=f"{doc_type}.{appearance}"):
                self.assertEqual(len(expected), V.EXPECTED_DECLARATIONS_PER_CELL)
                if reference is None:
                    reference = set(expected)
                else:
                    self.assertEqual(set(expected), reference)
                for var, value in expected.items():
                    self.assertNotIn("{", value, f"{doc_type}.{appearance} {var}")
                    self.assertNotIn("[", value, f"{doc_type}.{appearance} {var}")
                    self.assertTrue(value.strip(), f"{doc_type}.{appearance} {var}")

    def test_D3_04_non_colour_declarations_are_serialized_forms(self) -> None:
        """D-3-04: dimensions, shadows and font lists reach the oracle as CSS, not reprs."""
        cell = V.expected_declarations(self.tokens, "adventurous", "light")
        self.assertEqual(cell["--ds-space-4"], "12px")
        self.assertEqual(cell["--ds-radius-pill"], "999px")
        self.assertEqual(cell["--ds-type-tracking-caps"], "0.18em")
        self.assertEqual(cell["--ds-shadow-md"], "0px 6px 18px 0px #142C361F")
        self.assertEqual(cell["--ds-type-family-body"], "Manrope, Inter, 'Helvetica Neue', Arial, sans-serif")
        self.assertEqual(cell["--ds-type-weight-bold"], "700")

    # ------------------------------------------------------------------ negatives

    def test_D3_05_wrong_colour_value_detected(self) -> None:
        """D-3-05: a one-hex-digit colour change is reported against the right cell."""
        text = self._artifact("examples/preview-adventurous.html")
        want = V.expected_declarations(self.tokens, "adventurous", "light")["--ds-brand-primary"]
        mutated = edit_scoped(text, "adventurous", "light", "--ds-brand-primary", "#123456")
        path = self._write("wrong-colour.html", mutated)
        failures = V.check_html(path, "adventurous", self.tokens)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("--ds-brand-primary", failures[0])
        self.assertIn("brand.primary", failures[0])
        self.assertIn(f"adventurous.light wants {want}", failures[0])
        self.assertIn("#123456", failures[0])

    def test_D3_06_wrong_non_colour_values_detected(self) -> None:
        """D-3-06: spacing, surface and shadow regressions are all detected."""
        text = self._artifact("examples/preview-adventurous.html")
        cases = (
            ("--ds-space-4", "13px", "space.4"),
            ("--ds-surface-base", "#FFFFFF", "surface.base"),
            ("--ds-shadow-md", "0px 6px 18px 0px #00000000", "shadow.md"),
            ("--ds-radius-lg", "19px", "radius.lg"),
            ("--ds-type-family-body", "Inter, sans-serif", "type.family.body"),
        )
        for var, new_value, token in cases:
            with self.subTest(var=var):
                mutated = edit_scoped(text, "adventurous", "light", var, new_value)
                path = self._write(f"wrong-{var.strip('-')}.html", mutated)
                failures = V.check_html(path, "adventurous", self.tokens)
                self.assertEqual(len(failures), 1, failures)
                self.assertIn(var, failures[0])
                self.assertIn(token, failures[0])

    def test_D3_07_missing_declaration_detected(self) -> None:
        """D-3-07: a deleted declaration is reported as missing, not as a value mismatch."""
        text = self._artifact("examples/preview-professional.html")
        mutated = edit_scoped(text, "professional", "dark", "--ds-type-tracking-caps", None)
        path = self._write("missing.html", mutated)
        failures = V.check_html(path, "professional", self.tokens)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("lacks --ds-type-tracking-caps", failures[0])
        self.assertIn("type.tracking.caps", failures[0])

    def test_D3_08_unexpected_extra_declaration_detected(self) -> None:
        """D-3-08: an unknown ``--ds-*`` declaration fails the gate explicitly."""
        text = self._artifact("examples/preview-professional.html")
        mutated = insert_scoped(text, "professional", "light", "--ds-ghost-token: 1px;")
        path = self._write("extra.html", mutated)
        failures = V.check_html(path, "professional", self.tokens)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("unexpected extra declaration --ds-ghost-token=1px", failures[0])

    def test_D3_09_duplicate_declaration_detected(self) -> None:
        """D-3-09: declaring the same variable twice is reported as a duplicate."""
        text = self._artifact("examples/preview-professional.html")
        mutated = insert_scoped(text, "professional", "light", "--ds-space-4: 12px;")
        path = self._write("duplicate.html", mutated)
        failures = V.check_html(path, "professional", self.tokens)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("duplicate declaration --ds-space-4", failures[0])

    def test_D3_10_every_palette_and_appearance_combination_is_enforced(self) -> None:
        """D-3-10: each palette x appearance cell is validated and each is defect-sensitive."""
        for palette in PALETTES:
            rel = f"examples/preview-{palette}.html"
            text = self._artifact(rel)
            for appearance in APPEARANCES:
                with self.subTest(cell=f"{palette}.{appearance}"):
                    expected = V.expected_declarations(self.tokens, palette, appearance)
                    self.assertEqual(len(expected), 191)
                    self.assertEqual(V.check_html(ROOT / rel, palette, self.tokens), [])
                    mutated = edit_scoped(text, palette, appearance, "--ds-space-4", "13px")
                    path = self._write(f"combo-{palette}-{appearance}.html", mutated)
                    failures = V.check_html(path, palette, self.tokens)
                    self.assertEqual(len(failures), 1, failures)
                    self.assertIn(f"{palette}.{appearance} wants", failures[0])
                    self.assertIn("space.4", failures[0])

    def test_D3_11_css_dark_and_light_blocks_both_enforced(self) -> None:
        """D-3-11: dist CSS light and dark blocks are compared declaration by declaration."""
        for doc_type, filename in V.CSS_FILES.items():
            path = V.CSS_DIR / filename
            text = path.read_text(encoding="utf-8")
            for appearance in APPEARANCES:
                expected = V.expected_declarations(self.tokens, doc_type, appearance)
                var = "--ds-space-4"
                want = expected[var]
                with self.subTest(css=filename, appearance=appearance):
                    self.assertIn(f"{var}: {want};", text)
                    self.assertEqual(len(V.declarations(text)), 382)
                    # Replace the nth occurrence: light block precedes dark in every file.
                    index = 0 if appearance == "light" else 1
                    occurrences = [m.start() for m in re.finditer(re.escape(f"{var}: {want};"), text)]
                    self.assertEqual(len(occurrences), 2, filename)
                    at = occurrences[index]
                    mutated = text[:at] + f"{var}: 13px;" + text[at + len(f"{var}: {want};"):]
                    out = self._write(f"css-{doc_type}-{appearance}.css", mutated)
                    failures = V.check_css(out, doc_type, self.tokens)
                    self.assertEqual(len(failures), 1, failures)
                    self.assertIn(var, failures[0])
                    self.assertIn("space.4", failures[0])

    # ------------------------------------------------------------------- mutations

    def test_D3_12_oracle_mutation_is_detected(self) -> None:
        """D-3-12: if the serializer's output changes, the gate fails — the oracle is live."""
        path = ROOT / "examples" / "preview-adventurous.html"
        self.assertEqual(V.check_html(path, "adventurous", self.tokens), [])
        with mock.patch.object(V._css_gen, "serialize_css_value", side_effect=lambda v, n: "0px"):
            failures = V.check_html(path, "adventurous", self.tokens)
        # 382 declarations, minus the 4 whose correct serialized value already is "0px"
        # (space.0 and radius.none in each of the two cells).
        self.assertEqual(len(failures), 2 * 191 - 4, failures[:2])
        self.assertTrue(all("wants 0px" in message for message in failures))

    def test_D3_13_serializer_regression_on_one_type_is_detected(self) -> None:
        """D-3-13: a mutation limited to dimension serialization still fails all cells."""
        original = V._css_gen.serialize_css_value

        def broken(value, token):
            if isinstance(value, dict) and "unit" in value:
                return f"{value['value']}{value['unit']}!"
            return original(value, token)

        with mock.patch.object(V._css_gen, "serialize_css_value", side_effect=broken):
            failures = V.check_html(ROOT / "examples" / "preview-professional.html", "professional", self.tokens)
        self.assertGreater(len(failures), 60, failures[:2])
        self.assertTrue(all("wants " in message and "!" in message for message in failures))

    def test_D3_14_consulting_is_a_document_type_not_a_palette(self) -> None:
        """D-3-14: consulting validates as a document type and is refused as a palette."""
        self.assertNotIn("consulting", V.PALETTES)
        self.assertIn("consulting", V.DOCUMENT_TYPES)
        self.assertEqual(V.check_css(V.CSS_DIR / V.CSS_FILES["consulting"], "consulting", self.tokens), [])
        self.assertEqual(len(V.expected_declarations(self.tokens, "consulting", "light")), 191)
        with self.assertRaises(ValueError) as ctx:
            V.require_palette("consulting")
        self.assertIn("document type, not a palette", str(ctx.exception))


# ------------------------------------------------------------------ F-3 serialization
#
# The oracle is ``dist/css``, produced by the independent, type-aware serializer in
# ``build.py``. Nothing below derives an expectation from ``css_gen`` itself, so a
# broken serializer cannot validate its own output (F-3 §6.2 G2 rejection).

DIST_CSS_FILES = {
    "professional": ROOT / "dist" / "css" / "tokens.css",
    "adventurous": ROOT / "dist" / "css" / "tokens-adventurous.css",
    "consulting": ROOT / "dist" / "css" / "tokens-consulting.css",
}
EXPECTED_DIST_AGGREGATE = "e5d7a06cf2dc7d39b19f901db11913fdfe33d77152435259cf5e6c5a3b305a33"
EXPECTED_DIST_FILES = 16
F3_BACKUPS = BUILD / "fixtures" / "f3"
OFFICIAL_HTML = (
    "preview-professional",
    "preview-adventurous",
    "preview-analyst-professional",
    "preview-analyst-adventurous",
)
FIXTURE_INVALID_COUNT = 128
DECLARATION_RE = re.compile(r"--ds-[a-z0-9-]+\s*:\s*([^;]*);")

MUTATE_SERIALIZER = [
    (
        'lines.append(f"  {css_var}: {serialize_css_value(value, css_var)};")',
        'lines.append(f"  {css_var}: {value};")',
    )
]
MUTATE_FLATNESS = [
    ('if all("." in str(name) for name in token_dict):', "if isinstance(next(iter(token_dict.values())), str):")
]
MUTATE_FLATTEN = [
    (
        "            if isinstance(value, dict):\n"
        "                if not value:\n"
        "                    dropped.append(name)\n"
        "                elif set(value) == _DIMENSION_KEYS or set(value) == _SHADOW_KEYS:\n"
        "                    flat[name] = value          # structured leaf\n"
        "                else:\n"
        "                    walk(name, value)\n"
        "            else:\n"
        "                flat[name] = value              # str / int / float / list leaf",
        "            if isinstance(value, dict):\n"
        "                if not value:\n"
        "                    dropped.append(name)\n"
        "                else:\n"
        "                    walk(name, value)\n"
        '            elif isinstance(value, str) and value.startswith("#"):\n'
        "                flat[name] = value\n"
        "            else:\n"
        "                dropped.append(name)",
    )
]


def f3_dist_cells(palette: str) -> dict:
    """Parse the light/dark blocks of one ``dist/css`` file, values only."""
    text = DIST_CSS_FILES[palette].read_text(encoding="utf-8")
    out = {}
    for selector, body in re.findall(r"(?m)^([^\s@/][^{]*)\{\n(.*?)^\}", text, re.S):
        selector = selector.strip()
        if selector == ":root" or selector == f'[data-palette="{palette}"]':
            theme = "light"
        elif 'data-theme="dark"' in selector:
            theme = "dark"
        else:
            continue
        out[f"{palette}.{theme}"] = {
            name: value.strip() for name, value in re.findall(r"(--ds-[a-z0-9-]+)\s*:\s*([^;]+);", body)
        }
    return out


def f3_invalid_declarations(css_text: str) -> list:
    """Declarations whose value is a Python repr (dict/list) instead of CSS."""
    bad = []
    for match in DECLARATION_RE.finditer(css_text):
        value = match.group(1).strip()
        if value.startswith(("{", "[")) or "':" in value or "{'" in value:
            bad.append(match.group(0).strip())
    return bad


def f3_scoped_blocks(html_text: str) -> list:
    """[(palette, appearance, body)] for every scoped block in an artifact."""
    return re.findall(
        r'\[data-palette="([a-z]+)"\]\[data-theme="([a-z]+)"\]\s*\{(.*?)\n\}', html_text, re.S
    )


def f3_declarations(body: str) -> dict:
    return {name: value.strip() for name, value in re.findall(r"(--ds-[a-z0-9-]+)\s*:\s*([^;]+);", body)}


def f3_dist_aggregate() -> tuple:
    """(aggregate sha256, file count) over ``dist/`` exactly like ``sha256sum | sha256sum``."""
    digest = hashlib.sha256()
    files = sorted(p for p in (ROOT / "dist").rglob("*") if p.is_file())
    for path in files:
        digest.update(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n".encode())
    return digest.hexdigest(), len(files)


def f3_mutant(mutations: list) -> Any:
    """Import a mutated copy of ``css_gen`` from a temp dir; the repo file is untouched."""
    source = (BUILD / "css_gen.py").read_text(encoding="utf-8")
    for old, new in mutations:
        assert old in source, f"mutation target missing: {old[:60]}"
        source = source.replace(old, new, 1)
    directory = Path(tempfile.mkdtemp(prefix="f3mut_"))
    path = directory / "css_gen_mutant.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"css_gen_mutant_{directory.name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class F3SerializerTests(unittest.TestCase):
    """F-3a: shape-dispatched serialization, full 1 146-value oracle."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = independent_tokens()
        cls.themes = cls.tokens

    def test_F3T01_dimension_serialization(self):
        cases = [
            ({"value": 1, "unit": "px"}, "1px"),
            ({"value": 12, "unit": "px"}, "12px"),
            ({"value": 120, "unit": "ms"}, "120ms"),
            ({"value": -0.02, "unit": "em"}, "-0.02em"),
            ({"value": 0.18, "unit": "em"}, "0.18em"),
            ({"value": 999, "unit": "px"}, "999px"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(css_gen.serialize_css_value(value), expected)

    def test_F3T02_shadow_serialization(self):
        value = {
            "color": "#142C3614",
            "offsetX": {"value": 0, "unit": "px"},
            "offsetY": {"value": 1, "unit": "px"},
            "blur": {"value": 3, "unit": "px"},
            "spread": {"value": 0, "unit": "px"},
        }
        self.assertEqual(css_gen.serialize_css_value(value), "0px 1px 3px 0px #142C3614")
        value["blur"] = {"value": 18, "unit": "px"}
        value["offsetY"] = {"value": 6, "unit": "px"}
        self.assertEqual(css_gen.serialize_css_value(value), "0px 6px 18px 0px #142C3614")

    def test_F3T03_font_family_serialization(self):
        family = ["Manrope", "Inter", "Helvetica Neue", "Arial", "sans-serif"]
        self.assertEqual(
            css_gen.serialize_css_value(family),
            "Manrope, Inter, 'Helvetica Neue', Arial, sans-serif",
        )
        self.assertEqual(css_gen.serialize_css_value(["Manrope"]), "Manrope")
        self.assertEqual(css_gen.serialize_css_value(["IBM Plex Sans", "sans-serif"]), "'IBM Plex Sans', sans-serif")

    def test_F3T04_scalar_passthrough(self):
        for value, expected in [
            ("#E9E5D9", "#E9E5D9"),
            ("#142C3614", "#142C3614"),
            ("32px", "32px"),
            ("transparent", "transparent"),
            (400, "400"),
            (300, "300"),
            (1.0, "1.0"),
            (1.06, "1.06"),
            (0, "0"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(css_gen.serialize_css_value(value), expected)
        self.assertEqual(css_gen.serialize_css_value(1.0), "1.0")
        self.assertNotEqual(css_gen.serialize_css_value(1.0), "1")

    def test_F3T05_all_values_match_dist_css(self):
        """Oracle: every resolved value, all 6 cells, must equal the dist/css value."""
        compared = 0
        expected_total = 0
        for cell, tokens in sorted(self.tokens.items()):
            palette = cell.split(".", 1)[0]
            reference = f3_dist_cells(palette).get(cell, {})
            self.assertTrue(reference, f"dist/css reference empty for {cell}")
            expected_total += len(tokens)
            for name, value in sorted(tokens.items()):
                var = css_gen.token_name_to_css_var(name)
                with self.subTest(cell=cell, token=name):
                    self.assertIn(var, reference, f"{var} missing from dist/css for {cell}")
                    self.assertEqual(css_gen.serialize_css_value(value, var), reference[var])
                compared += 1
        self.assertEqual(compared, expected_total)
        self.assertEqual(compared, 1146)
        self.assertEqual(len(self.tokens), 6)

    def test_F3T06_every_structured_value_serialized(self):
        for cell, tokens in sorted(self.tokens.items()):
            structured = {k: v for k, v in tokens.items() if isinstance(v, (dict, list))}
            with self.subTest(cell=cell):
                self.assertEqual(len(structured), 64)
                for name, value in structured.items():
                    out = css_gen.serialize_css_value(value, name)
                    self.assertNotIn("{", out)
                    self.assertNotIn("[", out)
                    self.assertNotIn("': ", out)
                    self.assertTrue(out.strip())
                dimensions = [v for v in structured.values() if isinstance(v, dict) and set(v) == {"value", "unit"}]
                shadows = [v for v in structured.values() if isinstance(v, dict) and set(v) != {"value", "unit"}]
                families = [v for v in structured.values() if isinstance(v, list)]
                self.assertEqual((len(dimensions), len(shadows), len(families)), (57, 4, 3))

    def test_F3T07_malformed_values_fail_loudly(self):
        malformed = [
            None,
            True,
            False,
            {"foo": 1},
            {"value": 1},
            {"value": "1", "unit": "px"},
            {"value": 1, "unit": ""},
            {"value": 1, "unit": None},
            {"value": 1, "unit": "px;"},
            {"value": 1, "unit": "p x"},
            {"value": 1, "unit": "px", "extra": 2},
            {"color": "#000", "offsetX": {"value": 0, "unit": "px"}, "offsetY": {"value": 0, "unit": "px"},
             "spread": {"value": 0, "unit": "px"}},
            {"color": "#000", "offsetX": 0, "offsetY": {"value": 0, "unit": "px"},
             "blur": {"value": 0, "unit": "px"}, "spread": {"value": 0, "unit": "px"}},
            {"color": 0, "offsetX": {"value": 0, "unit": "px"}, "offsetY": {"value": 0, "unit": "px"},
             "blur": {"value": 0, "unit": "px"}, "spread": {"value": 0, "unit": "px"}},
            [],
            ["Manrope", 3],
            ["Manrope", ""],
            ["O'Neill"],
            "a;b",
            "a{b",
            "a\nb",
            "",
            ("a",),
            {1, 2},
            b"px",
        ]
        for value in malformed:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError) as caught:
                    css_gen.serialize_css_value(value, "--ds-example-token")
                self.assertIn("--ds-example-token", str(caught.exception))

    def test_F3T08_no_python_repr_emitted(self):
        rules = css_gen.generate_all_scoped_rules(self.themes)
        self.assertEqual(f3_invalid_declarations(rules), [])
        self.assertNotIn("{'", rules)
        self.assertNotIn("':", rules)
        for value in DECLARATION_RE.findall(rules):
            with self.subTest(value=value[:40]):
                self.assertRegex(value.strip(), r"^[^;{}]+$")

    def test_F3T09_all_declarations_present(self):
        rules = css_gen.generate_all_scoped_rules(self.themes)
        blocks = f3_scoped_blocks(rules)
        self.assertEqual(len(blocks), 6)
        for palette, appearance, body in blocks:
            cell = f"{palette}.{appearance}"
            with self.subTest(cell=cell):
                decls = f3_declarations(body)
                self.assertEqual(len(decls), len(self.tokens[cell]))
                expected = {css_gen.token_name_to_css_var(n) for n in self.tokens[cell]}
                self.assertEqual(set(decls), expected)

    def test_F3T10_all_palettes_and_appearances(self):
        palettes = sorted({cell.split(".", 1)[0] for cell in self.tokens})
        self.assertEqual(palettes, ["adventurous", "consulting", "professional"])
        for palette in palettes:
            reference = f3_dist_cells(palette)
            for appearance in APPEARANCES:
                cell = f"{palette}.{appearance}"
                with self.subTest(cell=cell):
                    self.assertIn(cell, reference)
                    rule = css_gen.generate_scoped_rule(palette, appearance, self.tokens[cell])
                    decls = f3_declarations(rule)
                    self.assertEqual(decls, reference[cell])
                    self.assertEqual(f3_invalid_declarations(rule), [])


class F3TraversalTests(unittest.TestCase):
    """F-3b: flatness by key shape, strict flattening, empty-cell guard."""

    NESTED = {
        "surface": {"base": "#E9E5D9", "raised": "#FAF7EE"},
        "space": {"4": {"value": 12, "unit": "px"}},
        "type": {"family": {"body": ["Manrope", "Helvetica Neue", "sans-serif"]}},
        "shadow": {"md": {"color": "#142C361F", "offsetX": {"value": 0, "unit": "px"},
                          "offsetY": {"value": 6, "unit": "px"}, "blur": {"value": 18, "unit": "px"},
                          "spread": {"value": 0, "unit": "px"}}},
    }

    @staticmethod
    def real_cell() -> dict:
        """A complete resolved cell, so the colour completeness check can pass."""
        return independent_tokens()["professional.light"]

    def test_F3T11_flatness_not_first_value(self):
        flat = css_gen.flatten_tokens(self.NESTED, strict=True)
        self.assertEqual(flat["surface.base"], "#E9E5D9")
        self.assertEqual(flat["space.4"], {"value": 12, "unit": "px"})
        self.assertEqual(flat["type.family.body"], ["Manrope", "Helvetica Neue", "sans-serif"])
        self.assertIn("shadow.md", flat)

        rule = css_gen.generate_scoped_rule(
            "professional", "light", {**self.real_cell(), **flat}
        )
        self.assertIn("--ds-space-4: 12px;", rule)
        self.assertIn("--ds-type-family-body: Manrope, 'Helvetica Neue', sans-serif;", rule)
        self.assertIn("--ds-shadow-md: 0px 6px 18px 0px #142C361F;", rule)
        self.assertEqual(f3_invalid_declarations(rule), [])

        # A resolved cell whose first value happens to be structured must pass through
        # untouched — order must not decide the code path.
        resolved = {"surface.base": "#E9E5D9", "space.4": {"value": 12, "unit": "px"}}
        reordered = {"space.4": resolved["space.4"], "surface.base": resolved["surface.base"]}
        self.assertIs(css_gen.flatten_tokens(reordered), reordered)
        for order in (resolved, reordered):
            with self.subTest(first=next(iter(order))):
                rules = css_gen.generate_all_scoped_rules(
                    {"professional.light": {**self.real_cell(), **order}}
                )
                self.assertIn("--ds-space-4: 12px;", rules)
                self.assertEqual(f3_invalid_declarations(rules), [])

    def test_F3T12_flatten_strict_raises_on_drop(self):
        with self.assertRaises(ValueError) as caught:
            css_gen.flatten_tokens({"surface": {}}, strict=True)
        self.assertIn("dropped", str(caught.exception))
        self.assertEqual(css_gen.flatten_tokens({"surface": {}}), {})

        # Non-colour leaves survive flattening (the historical silent-drop defect).
        flat = css_gen.flatten_tokens({"space": {"4": {"value": 12, "unit": "px"}}}, strict=True)
        self.assertEqual(flat, {"space.4": {"value": 12, "unit": "px"}})

    def test_F3T13_dist_unchanged(self):
        aggregate, count = f3_dist_aggregate()
        self.assertEqual(count, EXPECTED_DIST_FILES)
        self.assertEqual(aggregate, EXPECTED_DIST_AGGREGATE)
        for palette in DIST_CSS_FILES:
            cells = f3_dist_cells(palette)
            self.assertEqual(sorted(cells), [f"{palette}.dark", f"{palette}.light"])
            for cell, values in cells.items():
                with self.subTest(cell=cell):
                    self.assertEqual(len(values), 191)

    def test_F3T14_generator_does_not_write(self):
        themes = independent_tokens()
        with mock.patch.object(Path, "write_text", side_effect=AssertionError("serializer wrote a file")):
            rules = css_gen.generate_all_scoped_rules(themes)
        self.assertEqual(rules.count("{"), 6)

    def test_F3T15_empty_cell_guard(self):
        with self.assertRaises(ValueError) as caught:
            css_gen.generate_all_scoped_rules({"professional.light": {}})
        self.assertIn("no tokens for professional.light", str(caught.exception))


class F3NonVacuityTests(unittest.TestCase):
    """The detectors must fail on deliberately defective serialization/traversal."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = independent_tokens()

    def test_F3T16_detector_flags_legacy_output(self):
        legacy = "  --ds-space-4: {'value': 12, 'unit': 'px'};\n  --ds-type-family-body: ['Manrope'];\n"
        self.assertEqual(len(f3_invalid_declarations(legacy)), 2)
        clean = "  --ds-space-4: 12px;\n  --ds-type-family-body: Manrope, 'Helvetica Neue', sans-serif;\n"
        self.assertEqual(f3_invalid_declarations(clean), [])

    def test_F3T17_defective_serializer_fails(self):
        mutant = f3_mutant(MUTATE_SERIALIZER)
        rules = mutant.generate_all_scoped_rules(self.tokens)
        invalid = f3_invalid_declarations(rules)
        self.assertEqual(len(invalid), 64 * 6)
        self.assertGreater(len(invalid), 0)

        mismatches = 0
        blocks = f3_scoped_blocks(rules)
        self.assertEqual(len(blocks), 6)
        for palette, appearance, body in blocks:
            cell = f"{palette}.{appearance}"
            reference = f3_dist_cells(palette)[cell]
            decls = f3_declarations(body)
            mismatches += sum(1 for var, value in decls.items() if reference.get(var) != value)
        self.assertEqual(mismatches, 64 * 6)

    def test_F3T18_defective_traversal_fails(self):
        nested = F3TraversalTests.NESTED
        mutant = f3_mutant(MUTATE_FLATTEN)
        dropped = mutant.flatten_tokens(nested)
        self.assertIn("surface.base", dropped)
        self.assertNotIn("space.4", dropped)
        self.assertNotIn("shadow.md", dropped)
        self.assertNotIn("type.family.body", dropped)
        with self.assertRaises(ValueError):
            mutant.flatten_tokens(nested, strict=True)

        flatness = f3_mutant(MUTATE_FLATNESS)
        with self.assertRaises(ValueError):
            flatness.generate_all_scoped_rules({"professional.light": dict(nested)})

        flat = css_gen.flatten_tokens(nested, strict=True)
        self.assertIn("space.4", flat)
        rules = css_gen.generate_scoped_rule(
            "professional", "light", {**F3TraversalTests.real_cell(), **flat}
        )
        self.assertIn("--ds-space-4: 12px;", rules)
        self.assertEqual(f3_invalid_declarations(rules), [])


class F3ArtifactTests(unittest.TestCase):
    """Post-regeneration artifact evidence (4 authorized HTML files only)."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = independent_tokens()

    def test_F3T19_official_artifacts_have_zero_invalid_declarations(self):
        for name in OFFICIAL_HTML:
            text = (ROOT / "examples" / f"{name}.html").read_text(encoding="utf-8")
            with self.subTest(artifact=name):
                self.assertEqual(f3_invalid_declarations(text), [])
                blocks = f3_scoped_blocks(text)
                self.assertEqual(len(blocks), 2)
                for palette, appearance, body in blocks:
                    cell = f"{palette}.{appearance}"
                    decls = f3_declarations(body)
                    self.assertEqual(len(decls), len(self.tokens[cell]))
                    self.assertEqual(decls, f3_dist_cells(palette)[cell])

    def test_F3T20_artifact_diff_is_value_only(self):
        for name in OFFICIAL_HTML:
            old_path = F3_BACKUPS / f"{name}.PRE_F3.html"
            with self.subTest(artifact=name):
                self.assertTrue(old_path.exists(), old_path)
                old_lines = old_path.read_text(encoding="utf-8").splitlines()
                new_lines = (ROOT / "examples" / f"{name}.html").read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(old_lines), len(new_lines))
                changed = [
                    (old, new) for old, new in zip(old_lines, new_lines) if old != new
                ]
                self.assertEqual(len(changed), 128)
                for old, new in changed:
                    self.assertTrue(old.strip().startswith("--ds-"), old[:80])
                    self.assertTrue(new.strip().startswith("--ds-"), new[:80])
                    self.assertEqual(old.split(":")[0], new.split(":")[0])
                changed_vars = {line.split(":")[0].strip().lstrip("-").replace("ds-", "", 1) for _, line in changed}
                self.assertEqual(len(changed_vars), 64)
                structured = {
                    name_.replace(".", "-")
                    for name_, value in self.tokens["professional.light"].items()
                    if isinstance(value, (dict, list))
                }
                self.assertEqual(changed_vars, structured)

    def test_F3T21_fixtures_still_reproduce_defect(self):
        fixtures = sorted(FIXTURES.glob("*.html"))
        self.assertEqual(len(fixtures), 6)
        for path in fixtures:
            with self.subTest(fixture=path.name):
                self.assertEqual(len(f3_invalid_declarations(path.read_text(encoding="utf-8"))), FIXTURE_INVALID_COUNT)

    def test_F3T22_atlas_artifacts_untouched(self):
        for name, expected in (
            ("preview-atlas-professional.html", "5e429982f6f861a269fcca34b8a64f97d28ad99b3ca48229bcb7ac959a519f7d"),
            ("preview-atlas-adventurous.html", "8141d51ca879016914063ca6cfa3bf4b17547511d1d02e23b4f46c50ff653945"),
        ):
            with self.subTest(artifact=name):
                self.assertEqual(sha(ROOT / "examples" / name), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
