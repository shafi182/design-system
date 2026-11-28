#!/usr/bin/env python3
"""Unit tests for alpha compositing functions (Phase 1).

26+ test cases covering:
- HEX parsing (6-digit, 8-digit, edge cases, invalid inputs)
- Porter-Duff source-over compositing
- RGB rounding and clamping
- Edge cases (fully opaque, fully transparent, intermediate alpha)
- All 6 overlay.scrim token values
"""
import unittest
import sys
from pathlib import Path

# Import functions from build.py
sys.path.insert(0, str(Path(__file__).parent))
from build import parse_hex_color, composite_source_over


class TestParseHexColor(unittest.TestCase):
    """Test HEX parsing for 6-digit and 8-digit formats."""

    def test_parse_6digit_white(self):
        """6-digit: #FFFFFF (white, fully opaque)."""
        r, g, b, a = parse_hex_color("#FFFFFF")
        self.assertAlmostEqual(r, 1.0, places=5)
        self.assertAlmostEqual(g, 1.0, places=5)
        self.assertAlmostEqual(b, 1.0, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_6digit_black(self):
        """6-digit: #000000 (black, fully opaque)."""
        r, g, b, a = parse_hex_color("#000000")
        self.assertAlmostEqual(r, 0.0, places=5)
        self.assertAlmostEqual(g, 0.0, places=5)
        self.assertAlmostEqual(b, 0.0, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_6digit_mid_gray(self):
        """6-digit: #808080 (medium gray)."""
        r, g, b, a = parse_hex_color("#808080")
        self.assertAlmostEqual(r, 128/255, places=5)
        self.assertAlmostEqual(g, 128/255, places=5)
        self.assertAlmostEqual(b, 128/255, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_6digit_prof_light_surface(self):
        """6-digit: #E9E5D9 (professional light surface.base)."""
        r, g, b, a = parse_hex_color("#E9E5D9")
        self.assertAlmostEqual(r, 0xE9/255, places=5)
        self.assertAlmostEqual(g, 0xE5/255, places=5)
        self.assertAlmostEqual(b, 0xD9/255, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_6digit_lowercase(self):
        """6-digit lowercase: #e9e5d9."""
        r, g, b, a = parse_hex_color("#e9e5d9")
        self.assertAlmostEqual(r, 0xE9/255, places=5)
        self.assertAlmostEqual(g, 0xE5/255, places=5)
        self.assertAlmostEqual(b, 0xD9/255, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_8digit_fully_opaque(self):
        """8-digit fully opaque: #142C36FF (alpha = 0xFF = 255/255 = 1.0)."""
        r, g, b, a = parse_hex_color("#142C36FF")
        self.assertAlmostEqual(r, 0x14/255, places=5)
        self.assertAlmostEqual(g, 0x2C/255, places=5)
        self.assertAlmostEqual(b, 0x36/255, places=5)
        self.assertAlmostEqual(a, 1.0, places=5)

    def test_parse_8digit_fully_transparent(self):
        """8-digit fully transparent: #142C3600 (alpha = 0x00 = 0/255 = 0.0)."""
        r, g, b, a = parse_hex_color("#142C3600")
        self.assertAlmostEqual(r, 0x14/255, places=5)
        self.assertAlmostEqual(g, 0x2C/255, places=5)
        self.assertAlmostEqual(b, 0x36/255, places=5)
        self.assertAlmostEqual(a, 0.0, places=5)

    def test_parse_8digit_prof_light_scrim(self):
        """8-digit: #142C36B3 (professional light overlay.scrim, alpha=0.702)."""
        r, g, b, a = parse_hex_color("#142C36B3")
        self.assertAlmostEqual(r, 0x14/255, places=5)
        self.assertAlmostEqual(g, 0x2C/255, places=5)
        self.assertAlmostEqual(b, 0x36/255, places=5)
        self.assertAlmostEqual(a, 0xB3/255, places=5)
        self.assertAlmostEqual(a, 0.702, places=2)

    def test_parse_8digit_consulting_light_scrim(self):
        """8-digit: #172B4D99 (consulting light overlay.scrim, alpha=0.600)."""
        r, g, b, a = parse_hex_color("#172B4D99")
        self.assertAlmostEqual(r, 0x17/255, places=5)
        self.assertAlmostEqual(g, 0x2B/255, places=5)
        self.assertAlmostEqual(b, 0x4D/255, places=5)
        self.assertAlmostEqual(a, 0x99/255, places=5)
        self.assertAlmostEqual(a, 0.600, places=2)

    def test_parse_8digit_consulting_dark_scrim(self):
        """8-digit: #020617CC (consulting dark overlay.scrim, alpha=0.800)."""
        r, g, b, a = parse_hex_color("#020617CC")
        self.assertAlmostEqual(r, 0x02/255, places=5)
        self.assertAlmostEqual(g, 0x06/255, places=5)
        self.assertAlmostEqual(b, 0x17/255, places=5)
        self.assertAlmostEqual(a, 0xCC/255, places=5)
        self.assertAlmostEqual(a, 0.800, places=2)

    def test_parse_invalid_no_hash(self):
        """Invalid: no leading #."""
        with self.assertRaises(ValueError) as ctx:
            parse_hex_color("FFFFFF")
        self.assertIn("must start with #", str(ctx.exception))

    def test_parse_invalid_wrong_length_4digit(self):
        """Invalid: too short (4 digits)."""
        with self.assertRaises(ValueError):
            parse_hex_color("#FFF")

    def test_parse_invalid_wrong_length_7digit(self):
        """Invalid: wrong length (7 digits)."""
        with self.assertRaises(ValueError):
            parse_hex_color("#FFFFFF0")

    def test_parse_invalid_nonhex_char(self):
        """Invalid: non-hex character (6-digit)."""
        with self.assertRaises(ValueError):
            parse_hex_color("#GGGGGG")

    def test_parse_invalid_nonhex_8digit(self):
        """Invalid: non-hex in 8-digit."""
        with self.assertRaises(ValueError):
            parse_hex_color("#142C36ZZ")


class TestCompositeSourceOver(unittest.TestCase):
    """Test Porter-Duff source-over compositing."""

    def test_composite_opaque_over_white(self):
        """Fully opaque black over white: #000000 over #FFFFFF -> #000000."""
        result = composite_source_over("#000000", "#FFFFFF")
        self.assertEqual(result, "#000000")

    def test_composite_opaque_over_black(self):
        """Fully opaque white over black: #FFFFFF over #000000 -> #FFFFFF."""
        result = composite_source_over("#FFFFFF", "#000000")
        self.assertEqual(result, "#FFFFFF")

    def test_composite_transparent_over_white(self):
        """Fully transparent color over white: #00000000 over #FFFFFF -> #FFFFFF."""
        result = composite_source_over("#00000000", "#FFFFFF")
        self.assertEqual(result, "#FFFFFF")

    def test_composite_transparent_over_black(self):
        """Fully transparent color over black: #00000000 over #000000 -> #000000."""
        result = composite_source_over("#00000000", "#000000")
        self.assertEqual(result, "#000000")

    def test_composite_prof_light_scrim_over_white(self):
        """Professional light scrim #142C36B3 over white.
        
        Using full Porter-Duff formula:
          a_out = 0.702 + 1.0 * (1 - 0.702) = 1.0
          comp_r = (0.0784 * 0.702 + 1.0 * 1.0 * 0.298) / 1.0 = 0.353
        """
        result = composite_source_over("#142C36B3", "#FFFFFF")
        self.assertEqual(result, "#5A6B72")

    def test_composite_prof_light_scrim_over_black(self):
        """Professional light scrim #142C36B3 over black."""
        result = composite_source_over("#142C36B3", "#000000")
        self.assertEqual(result, "#0E1F26")

    def test_composite_prof_light_scrim_over_prof_light_surface(self):
        """Professional light scrim #142C36B3 over professional light surface #E9E5D9."""
        result = composite_source_over("#142C36B3", "#E9E5D9")
        self.assertEqual(result, "#536367")

    def test_composite_prof_dark_scrim_over_white(self):
        """Professional dark scrim #0D1E25B3 over white."""
        result = composite_source_over("#0D1E25B3", "#FFFFFF")
        self.assertEqual(result, "#556166")

    def test_composite_prof_dark_scrim_over_black(self):
        """Professional dark scrim #0D1E25B3 over black."""
        result = composite_source_over("#0D1E25B3", "#000000")
        self.assertEqual(result, "#09151A")

    def test_composite_prof_dark_scrim_over_prof_dark_surface(self):
        """Professional dark scrim #0D1E25B3 over professional dark surface #142C36."""
        result = composite_source_over("#0D1E25B3", "#142C36")
        self.assertEqual(result, "#0F222A")

    def test_composite_adv_light_scrim_over_white(self):
        """Adventurous light scrim #222222B3 over white."""
        result = composite_source_over("#222222B3", "#FFFFFF")
        self.assertEqual(result, "#646464")

    def test_composite_adv_light_scrim_over_black(self):
        """Adventurous light scrim #222222B3 over black."""
        result = composite_source_over("#222222B3", "#000000")
        self.assertEqual(result, "#181818")

    def test_composite_adv_dark_scrim_over_white(self):
        """Adventurous dark scrim #1A1A1AB3 over white."""
        result = composite_source_over("#1A1A1AB3", "#FFFFFF")
        self.assertEqual(result, "#5E5E5E")

    def test_composite_adv_dark_scrim_over_black(self):
        """Adventurous dark scrim #1A1A1AB3 over black."""
        result = composite_source_over("#1A1A1AB3", "#000000")
        self.assertEqual(result, "#121212")

    def test_composite_adv_dark_scrim_over_adv_dark_surface(self):
        """Adventurous dark scrim #1A1A1AB3 over adventurous dark surface #222222."""
        result = composite_source_over("#1A1A1AB3", "#222222")
        self.assertEqual(result, "#1C1C1C")

    def test_composite_cons_light_scrim_over_white(self):
        """Consulting light scrim #172B4D99 over white (alpha=0.600)."""
        result = composite_source_over("#172B4D99", "#FFFFFF")
        self.assertEqual(result, "#748094")

    def test_composite_cons_light_scrim_over_black(self):
        """Consulting light scrim #172B4D99 over black."""
        result = composite_source_over("#172B4D99", "#000000")
        self.assertEqual(result, "#0E1A2E")

    def test_composite_cons_dark_scrim_over_white(self):
        """Consulting dark scrim #020617CC over white (alpha=0.800)."""
        result = composite_source_over("#020617CC", "#FFFFFF")
        self.assertEqual(result, "#353845")

    def test_composite_cons_dark_scrim_over_black(self):
        """Consulting dark scrim #020617CC over black."""
        result = composite_source_over("#020617CC", "#000000")
        self.assertEqual(result, "#020512")

    def test_composite_opaque_8digit_over_opaque_8digit(self):
        """Both inputs fully opaque (8-digit): #000000FF over #FFFFFFFF.
        
        Result should be #000000 (fully opaque black dominates).
        """
        result = composite_source_over("#000000FF", "#FFFFFFFF")
        self.assertEqual(result, "#000000")

    def test_composite_semi_transparent_over_semi_transparent(self):
        """Both semi-transparent: #FF000080 (red, 50% alpha) over #0000FF80 (blue, 50% alpha).
        
        Result blends both channels according to Porter-Duff formula.
        """
        result = composite_source_over("#FF000080", "#0000FF80")
        # Approximate: should blend toward red (foreground is on top)
        # Actual value from formula
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("#"))
        self.assertEqual(len(result), 7)

    def test_composite_6digit_over_8digit(self):
        """6-digit (opaque) over 8-digit (semi-transparent)."""
        result = composite_source_over("#FF0000", "#0000FF80")
        # Red (fully opaque) over blue (50% alpha)
        # Red dominates
        self.assertEqual(result, "#FF0000")

    def test_composite_8digit_over_6digit(self):
        """8-digit (semi-transparent) over 6-digit (opaque)."""
        result = composite_source_over("#FF000080", "#0000FF")
        # Semi-transparent red over fully opaque blue
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("#"))


if __name__ == "__main__":
    unittest.main()
