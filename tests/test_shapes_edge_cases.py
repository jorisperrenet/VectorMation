"""Edge case tests for shapes in _shapes.py and _shapes_ext.py."""
import math
import pytest
from vectormation.objects import (
    Polygon, Circle, Ellipse, Rectangle, Line, FunctionGraph, Arc, Annulus,
    CubicBezier, Path, Wedge,
)


# -- Zero-size shapes --

class TestZeroSizeShapes:
    def test_circle_r0_area(self):
        c = Circle(r=0, cx=100, cy=100)
        assert c.get_area() == 0

    def test_circle_r0_perimeter(self):
        c = Circle(r=0, cx=100, cy=100)
        assert c.get_perimeter() == 0

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


# -- Annulus edge cases --

class TestAnnulusEdgeCases:
    def test_equal_radii(self):
        """Annulus with inner == outer radius should raise ValueError."""
        with pytest.raises(ValueError, match="inner_radius.*outer_radius"):
            Annulus(inner_radius=100, outer_radius=100, cx=500, cy=500)

    def test_zero_inner_radius(self):
        """Annulus with inner=0 is a full circle."""
        a = Annulus(inner_radius=0, outer_radius=100, cx=500, cy=500)
        assert a.get_area() == pytest.approx(math.pi * 100**2, rel=0.01)


# -- Path edge cases --

class TestPathEdgeCases:
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


# -- Arc edge cases --

class TestArcEdgeCases:
    def test_zero_radius(self):
        a = Arc(r=0, start_angle=0, end_angle=90, cx=500, cy=500)
        assert a.get_arc_length(0) == 0

    def test_sagitta_zero_sweep(self):
        a = Arc(r=100, start_angle=0, end_angle=0, cx=500, cy=500)
        assert a.get_sagitta(0) == 0


# -- CubicBezier edge cases --

class TestCubicBezierEdgeCases:
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


# -- FunctionGraph edge cases --

class TestFunctionGraphEdgeCases:
    def test_get_slope(self):
        fg = FunctionGraph(lambda x: x**2, x_range=(-5, 5))
        slope = fg.get_slope_at(3)
        assert slope == pytest.approx(6, abs=0.01)


# -- Polygon edge cases --

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


# -- Wedge edge cases --

class TestWedgeEdgeCases:
    def test_wedge_area(self):
        w = Wedge(r=100, start_angle=0, end_angle=90, cx=500, cy=500)
        area = w.get_area(0)
        expected = 0.5 * 100 * 100 * math.radians(90)
        assert area == pytest.approx(expected, rel=0.01)


# -- Line edge cases --

class TestLineEdgeCases:
    def test_zero_length_line(self):
        line = Line(100, 100, 100, 100)
        assert line.get_length(0) == 0


# -- ValueTracker / DecimalNumber / Paragraph edge cases --

class TestDecimalNumberTracker:
    def test_tracker_property(self):
        from vectormation.objects import DecimalNumber
        dn = DecimalNumber(3.14, x=100, y=100)
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
