"""Edge case tests for shapes in _shapes.py and _shapes_ext.py."""
import math
import pytest
from vectormation.objects import (
    Polygon, Circle, Ellipse, Rectangle, Dot,
    Line, FunctionGraph, Arc, Annulus, CubicBezier, Path,
    ArcBetweenPoints, Wedge, Spiral,
)


# ── Zero-size shapes ───────────────────────────────────────────────────

class TestZeroSizeShapes:
    def test_circle_r0_area(self):
        c = Circle(r=0, cx=100, cy=100)
        assert c.get_area() == 0

    def test_circle_r0_perimeter(self):
        c = Circle(r=0, cx=100, cy=100)
        assert c.get_perimeter() == 0

    def test_circle_r0_renders(self):
        c = Circle(r=0, cx=100, cy=100)
        svg = c.to_svg(0)
        assert svg is not None

    def test_rectangle_0x0(self):
        r = Rectangle(0, 0, x=100, y=100)
        assert r.get_area() == 0
        assert r.get_perimeter() == 0

    def test_rectangle_0x0_aspect_ratio(self):
        r = Rectangle(0, 0, x=100, y=100)
        assert r.aspect_ratio() == math.inf

    def test_rectangle_zero_height_aspect(self):
        r = Rectangle(100, 0, x=100, y=100)
        assert r.aspect_ratio() == math.inf

    def test_rectangle_zero_width(self):
        r = Rectangle(0, 100, x=100, y=100)
        assert r.aspect_ratio() == 0

    def test_ellipse_zero_radii(self):
        e = Ellipse(rx=0, ry=0, cx=100, cy=100)
        assert e.get_area() == 0

    def test_dot_renders(self):
        d = Dot(cx=100, cy=100, r=0)
        svg = d.to_svg(0)
        assert svg is not None


# ── Annulus edge cases ──────────────────────────────────────────────────

class TestAnnulusEdgeCases:
    def test_equal_radii(self):
        """Annulus with inner == outer radius should raise ValueError."""
        with pytest.raises(ValueError, match="inner_radius.*outer_radius"):
            Annulus(inner_radius=100, outer_radius=100, cx=500, cy=500)

    def test_zero_inner_radius(self):
        """Annulus with inner=0 is a full circle."""
        a = Annulus(inner_radius=0, outer_radius=100, cx=500, cy=500)
        assert a.get_area() == pytest.approx(math.pi * 100**2, rel=0.01)

    def test_renders(self):
        a = Annulus(inner_radius=50, outer_radius=100, cx=500, cy=500)
        svg = a.to_svg(0)
        assert svg is not None


# ── Path edge cases ─────────────────────────────────────────────────────

class TestPathEdgeCases:
    def test_empty_path_length(self):
        p = Path('')
        assert p.get_length(0) == 0

    def test_empty_path_point(self):
        p = Path('')
        assert p.point_from_proportion(0.5, 0) == (0, 0)

    def test_empty_path_tangent(self):
        p = Path('')
        assert p.tangent_at(0.5, 0) == (0.0, 0.0)

    def test_simple_line_path(self):
        p = Path('M 0 0 L 100 0')
        length = p.get_length(0)
        assert length == pytest.approx(100, rel=0.01)

    def test_point_at_start(self):
        p = Path('M 0 0 L 100 0')
        pt = p.point_from_proportion(0, 0)
        assert pt[0] == pytest.approx(0, abs=1)

    def test_point_at_end(self):
        p = Path('M 0 0 L 100 0')
        pt = p.point_from_proportion(1, 0)
        assert pt[0] == pytest.approx(100, abs=1)


# ── Arc edge cases ──────────────────────────────────────────────────────

class TestArcEdgeCases:
    def test_zero_sweep(self):
        a = Arc(r=100, start_angle=0, end_angle=0, cx=500, cy=500)
        svg = a.to_svg(0)
        assert svg is not None

    def test_full_circle_sweep(self):
        a = Arc(r=100, start_angle=0, end_angle=360, cx=500, cy=500)
        svg = a.to_svg(0)
        assert svg is not None

    def test_negative_sweep(self):
        a = Arc(r=100, start_angle=90, end_angle=0, cx=500, cy=500)
        svg = a.to_svg(0)
        assert svg is not None

    def test_zero_radius(self):
        a = Arc(r=0, start_angle=0, end_angle=90, cx=500, cy=500)
        assert a.get_arc_length(0) == 0

    def test_sagitta_zero_sweep(self):
        a = Arc(r=100, start_angle=0, end_angle=0, cx=500, cy=500)
        assert a.get_sagitta(0) == 0


# ── CubicBezier edge cases ─────────────────────────────────────────────

class TestCubicBezierEdgeCases:
    def test_all_same_point(self):
        """All four control points identical."""
        cb = CubicBezier(p0=(100, 100), p1=(100, 100), p2=(100, 100), p3=(100, 100))
        svg = cb.to_svg(0)
        assert svg is not None

    def test_collinear_points(self):
        cb = CubicBezier(p0=(0, 0), p1=(100, 0), p2=(200, 0), p3=(300, 0))
        svg = cb.to_svg(0)
        assert svg is not None

    def test_point_at_start(self):
        cb = CubicBezier(p0=(0, 0), p1=(50, 100), p2=(150, 100), p3=(200, 0))
        pt = cb.point_at(0, 0)
        assert pt[0] == pytest.approx(0, abs=1)
        assert pt[1] == pytest.approx(0, abs=1)

    def test_point_at_end(self):
        cb = CubicBezier(p0=(0, 0), p1=(50, 100), p2=(150, 100), p3=(200, 0))
        pt = cb.point_at(1, 0)
        assert pt[0] == pytest.approx(200, abs=1)
        assert pt[1] == pytest.approx(0, abs=1)

    def test_tangent_at_zero_magnitude(self):
        """Tangent at degenerate point should return fallback."""
        cb = CubicBezier(p0=(100, 100), p1=(100, 100), p2=(100, 100), p3=(100, 100))
        tx, ty = cb.tangent_at(0.5, 0)
        assert math.isfinite(tx)
        assert math.isfinite(ty)


# ── FunctionGraph edge cases ────────────────────────────────────────────

class TestFunctionGraphEdgeCases:
    def test_constant_function(self):
        fg = FunctionGraph(lambda x: 5, x_range=(-5, 5))
        svg = fg.to_svg(0)
        assert svg is not None

    def test_zero_range(self):
        """FunctionGraph with x_min == x_max should not crash."""
        fg = FunctionGraph(lambda x: x, x_range=(0, 0))
        svg = fg.to_svg(0)
        assert svg is not None

    def test_get_slope(self):
        fg = FunctionGraph(lambda x: x**2, x_range=(-5, 5))
        slope = fg.get_slope_at(3)
        assert slope == pytest.approx(6, abs=0.01)

    def test_get_point(self):
        fg = FunctionGraph(lambda x: x, x_range=(-5, 5))
        pt = fg.get_point_from_x(0)
        assert isinstance(pt, tuple)
        assert len(pt) == 2


# ── Polygon edge cases ─────────────────────────────────────────────────

class TestPolygonEdgeCases:
    def test_triangle_centroid(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        cx, cy = p.centroid(time=0)
        assert cx == pytest.approx(50, abs=1)
        assert cy == pytest.approx(100 / 3, abs=1)

    def test_degenerate_polygon(self):
        """Polygon with all points at same location."""
        p = Polygon((0, 0), (0, 0), (0, 0))
        cx, cy = p.centroid(time=0)
        assert math.isfinite(cx) and math.isfinite(cy)


# ── ArcBetweenPoints edge cases ────────────────────────────────────────

class TestArcBetweenPointsEdgeCases:
    def test_basic(self):
        abp = ArcBetweenPoints((100, 100), (300, 100), angle=90)
        svg = abp.to_svg(0)
        assert svg is not None

    def test_same_point(self):
        """Arc between identical points should not crash."""
        abp = ArcBetweenPoints((100, 100), (100, 100), angle=90)
        svg = abp.to_svg(0)
        assert svg is not None

    def test_near_zero_angle(self):
        """Arc with very small angle should still render."""
        abp = ArcBetweenPoints((100, 100), (300, 100), angle=0.01)
        svg = abp.to_svg(0)
        assert svg is not None


# ── Wedge edge cases ───────────────────────────────────────────────────

class TestWedgeEdgeCases:
    def test_full_circle_wedge(self):
        w = Wedge(r=100, start_angle=0, end_angle=360, cx=500, cy=500)
        svg = w.to_svg(0)
        assert svg is not None

    def test_zero_radius_wedge(self):
        w = Wedge(r=0, start_angle=0, end_angle=90, cx=500, cy=500)
        svg = w.to_svg(0)
        assert svg is not None

    def test_wedge_area(self):
        w = Wedge(r=100, start_angle=0, end_angle=90, cx=500, cy=500)
        area = w.get_area(0)
        expected = 0.5 * 100 * 100 * math.radians(90)
        assert area == pytest.approx(expected, rel=0.01)


# ── Line edge cases ────────────────────────────────────────────────────

class TestLineEdgeCases:
    def test_zero_length_line(self):
        l = Line(100, 100, 100, 100)
        assert l.get_length(0) == 0

    def test_set_length_zero_line(self):
        """set_length on zero-length line should be no-op."""
        l = Line(100, 100, 100, 100)
        l.set_length(50)
        # Should not crash

    def test_extend_to_zero_line(self):
        l = Line(100, 100, 100, 100)
        l.extend_to(200)
        # Should not crash


# ── Spiral edge cases ──────────────────────────────────────────────────

class TestSpiralEdgeCases:
    def test_basic_spiral(self):
        s = Spiral(a=0, b=15, turns=3, cx=500, cy=500)
        svg = s.to_svg(0)
        assert svg is not None

    def test_zero_turns(self):
        s = Spiral(a=10, b=15, turns=0, cx=500, cy=500)
        svg = s.to_svg(0)
        assert svg is not None

    def test_log_spiral(self):
        s = Spiral(a=5, b=0.1, turns=2, log_spiral=True, cx=500, cy=500)
        svg = s.to_svg(0)
        assert svg is not None


# ── ValueTracker / DecimalNumber / Paragraph edge cases ──────────────

class TestValueTrackerProperties:
    def test_last_change(self):
        from vectormation.objects import ValueTracker
        vt = ValueTracker(10)
        vt.set_value(20, start=0.5)
        assert vt.last_change == 0.5

    def test_at_time_alias(self):
        from vectormation.objects import ValueTracker
        vt = ValueTracker(42)
        assert vt.at_time(0) == 42
        assert vt.get_value(0) == 42


class TestDecimalNumberTracker:
    def test_tracker_property(self):
        from vectormation.objects import DecimalNumber
        dn = DecimalNumber(3.14, x=100, y=100)
        assert dn.tracker is not None
        assert dn.tracker.at_time(0) == pytest.approx(3.14)


class TestParagraphLines:
    def test_lines_getter(self):
        from vectormation.objects import Paragraph
        p = Paragraph('Hello', 'World')
        assert len(p.lines) == 2

    def test_lines_setter(self):
        from vectormation.objects import Paragraph
        p = Paragraph('A', 'B')
        p.lines = ['X', 'Y', 'Z']
        assert len(p.lines) == 3
