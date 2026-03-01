"""Extended tests for _svg_utils: boolean ops, ConvexHull, vector fields, etc."""
import math
import pytest
from vectormation.objects import (
    Circle, Rectangle, VectorMathAnim, VCollection,
)
from vectormation._svg_utils import (
    Union, Difference, Intersection, Exclusion,
    ArrowVectorField, StreamLines, ConvexHull,
    Cutout, ZoomedInset, Spotlight, AnimatedBoundary,
    ClipPath, BlurFilter, DropShadowFilter,
    Angle, RightAngle, Cross,
    _parse_svg_points, _parse_inline_style, _convex_hull, _cross,
)


# ── Boolean operations edge cases ────────────────────────────────────

class TestBooleanOpsEdgeCases:
    def test_union_non_overlapping(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=500, cy=500)
        u = Union(c1, c2)
        svg = u.to_svg(0)
        assert svg is not None

    def test_union_identical_shapes(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=100, cy=100)
        u = Union(c1, c2)
        svg = u.to_svg(0)
        assert svg is not None

    def test_difference_swapped(self):
        big = Circle(r=100, cx=200, cy=200)
        small = Circle(r=30, cx=200, cy=200)
        d = Difference(big, small)
        svg = d.to_svg(0)
        assert svg is not None

    def test_intersection_non_overlapping(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=500, cy=500)
        inter = Intersection(c1, c2)
        svg = inter.to_svg(0)
        assert svg is not None

    def test_exclusion_identical(self):
        c1 = Circle(r=50, cx=200, cy=200)
        c2 = Circle(r=50, cx=200, cy=200)
        exc = Exclusion(c1, c2)
        svg = exc.to_svg(0)
        assert svg is not None

    def test_union_renders_in_canvas(self):
        canvas = VectorMathAnim('/tmp')
        c1 = Circle(r=60, cx=200, cy=200)
        c2 = Circle(r=60, cx=260, cy=200)
        u = Union(c1, c2, fill='#FF0000')
        canvas.add(u)
        svg = canvas.generate_frame_svg(time=0)
        assert '<path' in svg or '<g' in svg


# ── ArrowVectorField edge cases ──────────────────────────────────────

class TestArrowVectorFieldEdgeCases:
    def test_zero_vector_field(self):
        """All-zero field should produce arrows (some may be skipped)."""
        avf = ArrowVectorField(lambda x, y: (0, 0),
                                x_range=(100, 300, 100),
                                y_range=(100, 300, 100))
        assert isinstance(avf, VCollection)

    def test_constant_field(self):
        avf = ArrowVectorField(lambda x, y: (1, 0),
                                x_range=(100, 500, 200),
                                y_range=(100, 500, 200))
        assert len(avf.objects) > 0

    def test_custom_max_length(self):
        avf = ArrowVectorField(lambda x, y: (x, y),
                                x_range=(100, 500, 200),
                                y_range=(100, 500, 200),
                                max_length=30)
        assert isinstance(avf, VCollection)


# ── StreamLines edge cases ───────────────────────────────────────────

class TestStreamLinesEdgeCases:
    def test_basic(self):
        sl = StreamLines(lambda x, y: (-y, x),
                          x_range=(100, 500, 100),
                          y_range=(100, 500, 100))
        assert isinstance(sl, VCollection)

    def test_custom_steps(self):
        sl = StreamLines(lambda x, y: (1, 0),
                          x_range=(100, 300, 100),
                          y_range=(100, 300, 100),
                          n_steps=20, step_size=5)
        assert isinstance(sl, VCollection)


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

    def test_convex_hull_object(self):
        c1 = Circle(r=30, cx=100, cy=100)
        c2 = Circle(r=30, cx=300, cy=100)
        c3 = Circle(r=30, cx=200, cy=300)
        hull = ConvexHull(c1, c2, c3)
        svg = hull.to_svg(0)
        assert svg is not None


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


# ── Cutout edge cases ───────────────────────────────────────────────

class TestCutoutEdgeCases:
    def test_basic_renders(self):
        canvas = VectorMathAnim('/tmp')
        c = Cutout(400, 300, 200, 150)
        canvas.add(c)
        svg = canvas.generate_frame_svg(time=0)
        assert svg is not None

    def test_zero_size_hole(self):
        c = Cutout(100, 100, 0, 0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_rounded_corners(self):
        c = Cutout(400, 300, 200, 150, rx=20, ry=20)
        svg = c.to_svg(0)
        assert svg is not None


# ── ZoomedInset edge cases ───────────────────────────────────────────

class TestZoomedInsetEdgeCases:
    def test_basic_creation(self):
        canvas = VectorMathAnim('/tmp')
        zi = ZoomedInset(canvas, source=(100, 100, 200, 200),
                          display=(600, 100, 400, 400))
        assert zi is not None

    def test_renders(self):
        canvas = VectorMathAnim('/tmp')
        c = Circle(r=50, cx=200, cy=200)
        canvas.add(c)
        zi = ZoomedInset(canvas, source=(100, 100, 200, 200),
                          display=(600, 100, 400, 400))
        canvas.add(zi)
        svg = canvas.generate_frame_svg(time=0)
        assert svg is not None


# ── Spotlight edge cases ─────────────────────────────────────────────

class TestSpotlightEdgeCases:
    def test_basic(self):
        s = Spotlight(target=(960, 540), radius=200)
        svg = s.to_svg(0)
        assert svg is not None

    def test_zero_radius(self):
        s = Spotlight(target=(960, 540), radius=0)
        svg = s.to_svg(0)
        assert svg is not None

    def test_from_vobject(self):
        c = Circle(r=50, cx=200, cy=200)
        s = Spotlight(target=c, radius=100)
        svg = s.to_svg(0)
        assert svg is not None


# ── AnimatedBoundary edge cases ──────────────────────────────────────

class TestAnimatedBoundaryEdgeCases:
    def test_basic(self):
        r = Rectangle(200, 100, x=400, y=300)
        ab = AnimatedBoundary(r)
        svg = ab.to_svg(0)
        assert svg is not None

    def test_custom_colors(self):
        r = Rectangle(200, 100, x=400, y=300)
        ab = AnimatedBoundary(r, colors=['#FF0000', '#00FF00', '#0000FF'])
        svg = ab.to_svg(0)
        assert svg is not None


# ── Angle edge cases ─────────────────────────────────────────────────

class TestAngleEdgeCases:
    def test_zero_angle(self):
        a = Angle((0, 0), (1, 0), (1, 0))
        svg = a.to_svg(0)
        assert svg is not None

    def test_right_angle(self):
        a = Angle((0, 0), (1, 0), (0, 1))
        svg = a.to_svg(0)
        assert svg is not None

    def test_obtuse_angle(self):
        a = Angle((0, 0), (1, 0), (-1, 1))
        svg = a.to_svg(0)
        assert svg is not None

    def test_label_true(self):
        canvas = VectorMathAnim('/tmp')
        a = Angle((200, 200), (300, 200), (200, 100), label=True)
        canvas.add(a)
        svg = canvas.generate_frame_svg(time=0)
        assert svg is not None


# ── ClipPath / Filters ───────────────────────────────────────────────

class TestFiltersEdgeCases:
    def test_blur_default(self):
        bf = BlurFilter()
        svg_def = bf.to_svg_def()
        assert 'filter' in svg_def

    def test_drop_shadow_default(self):
        ds = DropShadowFilter()
        svg_def = ds.to_svg_def()
        assert 'filter' in svg_def

    def test_clip_path_with_rectangle(self):
        r = Rectangle(100, 50, x=0, y=0)
        cp = ClipPath(r)
        svg_def = cp.to_svg_def(time=0)
        assert 'clipPath' in svg_def
