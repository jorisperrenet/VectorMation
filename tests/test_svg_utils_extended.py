"""Extended tests for _svg_utils: ConvexHull, helpers, filters."""
from vectormation.objects import Rectangle
from vectormation._svg_utils import (
    ClipPath,
    _parse_svg_points, _parse_inline_style, _convex_hull, _cross,
)


# ── _cross helper ────────────────────────────────────────────────────

class TestCrossHelper:
    def test_counterclockwise(self):
        assert _cross((0, 0), (1, 0), (0, 1)) > 0

    def test_clockwise(self):
        assert _cross((0, 0), (0, 1), (1, 0)) < 0

    def test_collinear(self):
        assert _cross((0, 0), (1, 0), (2, 0)) == 0


# ── _parse_svg_points ────────────────────────────────────────────────

class TestParseSvgPoints:
    def test_basic(self):
        pts = _parse_svg_points("0,0 100,200 300,400")
        assert pts == [(0, 0), (100, 200), (300, 400)]

    def test_space_separated(self):
        pts = _parse_svg_points("10 20 30 40")
        assert pts == [(10, 20), (30, 40)]

    def test_single_point(self):
        pts = _parse_svg_points("5,10")
        assert pts == [(5, 10)]

    def test_empty_string(self):
        pts = _parse_svg_points("")
        assert pts == []

    def test_odd_coordinates(self):
        """Odd number of coordinates drops the last one."""
        pts = _parse_svg_points("1,2 3,4 5")
        assert pts == [(1, 2), (3, 4)]


# ── _parse_inline_style ──────────────────────────────────────────────

class TestParseInlineStyle:
    def test_basic(self):
        result = _parse_inline_style("fill:red;stroke:blue")
        assert result == {'fill': 'red', 'stroke': 'blue'}

    def test_trailing_semicolon(self):
        result = _parse_inline_style("fill:red;")
        assert result == {'fill': 'red'}

    def test_empty_string(self):
        result = _parse_inline_style("")
        assert result == {}

    def test_whitespace(self):
        result = _parse_inline_style("fill : red ; stroke : blue")
        assert result == {'fill': 'red', 'stroke': 'blue'}


# ── ConvexHull edge cases ────────────────────────────────────────────

class TestConvexHullEdgeCases:
    def test_two_points(self):
        result = _convex_hull([(0, 0), (1, 0)])
        assert len(result) == 2

    def test_single_point(self):
        result = _convex_hull([(5, 5)])
        assert result == [(5, 5)]

    def test_duplicate_points(self):
        result = _convex_hull([(0, 0), (0, 0), (1, 1), (1, 1)])
        assert len(result) == 2

    def test_collinear_points(self):
        result = _convex_hull([(0, 0), (1, 0), (2, 0)])
        assert len(result) >= 2

    def test_square(self):
        result = _convex_hull([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert len(result) == 4


# ── ClipPath / Filters ───────────────────────────────────────────────

class TestFiltersEdgeCases:
    def test_clip_path_with_rectangle(self):
        r = Rectangle(100, 50, x=0, y=0)
        cp = ClipPath(r)
        svg_def = cp.to_svg_def(time=0)
        assert 'clipPath' in svg_def
