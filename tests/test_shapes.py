"""Tests for shape classes: geometry, bbox, SVG output, animations."""
import math
import pytest

from vectormation._shapes import (
    Polygon, Circle, Ellipse, Rectangle, Dot, Lines, RoundedRectangle,
)
from vectormation._constants import ORIGIN
import vectormation.easings as easings


class TestPolygon:

    def test_triangle_area_shoelace(self):
        # Right triangle with legs 100 and 200: area = 10000
        tri = Polygon((0, 0), (100, 0), (0, 200))
        assert tri.area(0) == pytest.approx(10000)

    def test_signed_area_winding(self):
        # CW winding in SVG coords (y-down) should give positive signed area
        cw = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        ccw = Polygon((0, 0), (0, 100), (100, 100), (100, 0))
        assert cw.signed_area(0) > 0
        assert ccw.signed_area(0) < 0
        assert abs(cw.signed_area(0)) == pytest.approx(abs(ccw.signed_area(0)))

    def test_open_polyline_area_is_zero(self):
        poly = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        assert poly.area(0) == 0.0

    def test_perimeter_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.perimeter(0) == pytest.approx(400)

    def test_perimeter_open_polyline(self):
        poly = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        assert poly.perimeter(0) == pytest.approx(200)  # two edges only

    def test_centroid_of_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx, cy = sq.centroid(0)
        assert cx == pytest.approx(50)
        assert cy == pytest.approx(50)

    def test_centroid_vs_center_for_nonsymmetric(self):
        # For a non-uniform triangle, centroid and get_center differ
        tri = Polygon((0, 0), (300, 0), (0, 100))
        centroid = tri.centroid(0)
        avg_center = tri.get_center(0)
        # Centroid of triangle is (sum_x/3, sum_y/3) = (100, 33.33)
        assert centroid[0] == pytest.approx(100)
        assert centroid[1] == pytest.approx(100 / 3)
        # get_center is simple average of vertices = same for triangle
        assert avg_center == pytest.approx(centroid)

    def test_bbox(self):
        tri = Polygon((10, 20), (110, 20), (60, 120))
        x, y, w, h = tri.bbox(0)
        assert x == pytest.approx(10)
        assert y == pytest.approx(20)
        assert w == pytest.approx(100)
        assert h == pytest.approx(100)

    def test_path_output(self):
        tri = Polygon((10, 20), (30, 40), (50, 60))
        path = tri.path(0)
        assert path.startswith('M 10,20')
        assert 'L 30,40' in path
        assert path.endswith('Z')

    def test_path_open_polyline_no_z(self):
        poly = Polygon((0, 0), (100, 0), closed=False)
        path = poly.path(0)
        assert 'Z' not in path

    def test_move_vertex_animates(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        tri.move_vertex(2, 50, 200, start=0, end=1, easing=easings.linear)
        # At midpoint
        verts = tri.get_vertices(0.5)
        assert verts[2][1] == pytest.approx(150)

    def test_move_vertex_invalid_index(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        with pytest.raises(IndexError):
            tri.move_vertex(5, 0, 0)

    def test_contains_point(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.contains_point(50, 50) is True
        assert sq.contains_point(200, 200) is False

    def test_winding_number(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.winding_number(50, 50) != 0   # inside
        assert sq.winding_number(200, 200) == 0  # outside

    def test_is_convex(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.is_convex() is True
        # L-shaped polygon is not convex
        l_shape = Polygon((0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100))
        assert l_shape.is_convex() is False

    def test_is_regular_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.is_regular() is True

    def test_is_regular_rectangle_false(self):
        rect = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        assert rect.is_regular() is False

    def test_convex_hull(self):
        # hull of a set including interior points
        hull = Polygon.convex_hull(
            (0, 0), (100, 0), (100, 100), (0, 100),
            (50, 50),  # interior point
        )
        verts = hull.get_vertices(0)
        assert len(verts) == 4  # interior point excluded

    def test_inset_shrinks_area(self):
        sq = Polygon((0, 0), (200, 0), (200, 200), (0, 200))
        inset = sq.inset(10)
        assert inset.area(0) < sq.area(0)

    def test_inset_reduces_to_zero_at_half(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        inset = sq.inset(50)
        assert inset.area(0) == pytest.approx(0, abs=1)

    def test_offset_changes_size(self):
        # Offset direction depends on winding; just check area changes
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        expanded = sq.offset(10)
        assert expanded.area(0) != sq.area(0)

    def test_rotate_vertices(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        rotated = sq.rotate_vertices(90)
        # After 90° rotation around center (50,50), all vertices move
        verts = rotated.get_vertices(0)
        # (0,0) rotated 90° CW around (50,50) → (100,0)?
        # Actually rotation formula: (50 + 0*cos90 - (-50)*sin90, 50 + 0*sin90 + (-50)*cos90)
        # = (50+50, 50+0) = (100, 50)
        assert verts[0] == pytest.approx((100, 0), abs=1e-6)

    def test_from_svg_path(self):
        p = Polygon.from_svg_path("M 10 20 L 30 40 L 50 20 Z")
        verts = p.get_vertices(0)
        assert len(verts) == 3
        assert verts[0] == pytest.approx((10, 20))

    def test_edge_lengths(self):
        tri = Polygon((0, 0), (3, 0), (0, 4))
        lengths = tri.edge_lengths(0)
        assert len(lengths) == 3
        assert lengths[0] == pytest.approx(3)   # (0,0)→(3,0)
        assert lengths[1] == pytest.approx(5)   # (3,0)→(0,4) = hypotenuse
        assert lengths[2] == pytest.approx(4)   # (0,4)→(0,0)

    def test_shift_updates_vertices(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sq.shift(dx=50, dy=50, start=0)
        verts = sq.get_vertices(0)
        assert verts[0] == pytest.approx((50, 50))


class TestCircle:

    def test_area(self):
        c = Circle(r=100)
        assert c.get_area(0) == pytest.approx(math.pi * 100 ** 2)

    def test_perimeter(self):
        c = Circle(r=100)
        assert c.get_perimeter(0) == pytest.approx(2 * math.pi * 100)

    def test_bbox_centered(self):
        c = Circle(r=50, cx=100, cy=200)
        x, y, w, h = c.bbox(0)
        assert x == pytest.approx(50)
        assert y == pytest.approx(150)
        assert w == pytest.approx(100)
        assert h == pytest.approx(100)

    def test_center(self):
        c = Circle(r=50, cx=100, cy=200)
        assert c.center(0) == pytest.approx((100, 200))

    def test_point_at_angle(self):
        c = Circle(r=100, cx=0, cy=0)
        # 0° → right → (100, 0)
        px, py = c.point_at_angle(0)
        assert px == pytest.approx(100)
        assert py == pytest.approx(0)
        # 90° → top (y is negative in SVG) → (0, -100)
        px, py = c.point_at_angle(90)
        assert px == pytest.approx(0, abs=1e-6)
        assert py == pytest.approx(-100)

    def test_contains_point(self):
        c = Circle(r=100, cx=0, cy=0)
        assert c.contains_point(0, 0) is True
        assert c.contains_point(99, 0) is True
        assert c.contains_point(101, 0) is False

    def test_from_diameter(self):
        c = Circle.from_diameter((0, 0), (200, 0))
        assert c.rx.at_time(0) == pytest.approx(100)
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(0)

    def test_from_center_and_point(self):
        c = Circle.from_center_and_point((0, 0), (3, 4))
        assert c.rx.at_time(0) == pytest.approx(5)

    def test_shift_moves_center(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shift(dx=50, dy=-50, start=0)
        assert c.center(0) == pytest.approx((150, 50))

    def test_animated_shift(self):
        c = Circle(r=50, cx=0, cy=0)
        c.shift(dx=100, dy=0, start=0, end=1, easing=easings.linear)
        # At t=0.5, should be halfway
        cx, cy = c.center(0.5)
        assert cx == pytest.approx(50)
        assert cy == pytest.approx(0)
        # At t=1, should be at destination
        assert c.center(1)[0] == pytest.approx(100)

    def test_svg_output(self):
        c = Circle(r=50, cx=100, cy=200)
        svg = c.to_svg(0)
        assert "cx='100'" in svg
        assert "cy='200'" in svg
        assert "r='50'" in svg
        assert '<circle' in svg

    def test_r_property(self):
        c = Circle(r=50)
        assert c.r.at_time(0) == 50
        assert c.rx.at_time(0) == 50
        assert c.ry.at_time(0) == 50

    def test_zero_radius(self):
        c = Circle(r=0, cx=100, cy=100)
        assert c.get_area(0) == 0
        assert c.get_perimeter(0) == 0
        assert c.contains_point(100, 100) is False  # r=0 means no area
        assert c.contains_point(101, 100) is False


class TestEllipse:

    def test_area(self):
        e = Ellipse(rx=100, ry=50)
        assert e.get_area(0) == pytest.approx(math.pi * 100 * 50)

    def test_eccentricity_circle(self):
        e = Ellipse(rx=50, ry=50)
        assert e.eccentricity(0) == pytest.approx(0)

    def test_eccentricity_range(self):
        e = Ellipse(rx=100, ry=10)
        ecc = e.eccentricity(0)
        assert 0 < ecc < 1

    def test_foci_on_major_axis(self):
        e = Ellipse(rx=100, ry=50, cx=0, cy=0)
        f1, f2 = e.get_foci(0)
        # Foci are on x-axis (major axis)
        assert f1[1] == pytest.approx(0)
        assert f2[1] == pytest.approx(0)
        # Sum of distances from any point on ellipse to both foci = 2*a
        px, py = e.point_at_angle(45, 0)
        d1 = math.hypot(px - f1[0], py - f1[1])
        d2 = math.hypot(px - f2[0], py - f2[1])
        assert d1 + d2 == pytest.approx(200, abs=1)

    def test_perimeter_ramanujan(self):
        # For a circle (rx=ry=r), perimeter should be 2*pi*r
        e = Ellipse(rx=100, ry=100)
        assert e.get_perimeter(0) == pytest.approx(2 * math.pi * 100, rel=0.001)

    def test_get_point_at_parameter(self):
        e = Ellipse(rx=100, ry=50, cx=0, cy=0)
        # t=0 → (rx, 0) = (100, 0)
        px, py = e.get_point_at_parameter(0)
        assert px == pytest.approx(100)
        assert py == pytest.approx(0)


class TestRectangle:

    def test_bbox(self):
        r = Rectangle(200, 100, x=50, y=50)
        x, y, w, h = r.bbox(0)
        assert (x, y, w, h) == pytest.approx((50, 50, 200, 100))

    def test_center(self):
        r = Rectangle(200, 100, x=50, y=50)
        assert r.center(0) == pytest.approx((150, 100))

    def test_area(self):
        r = Rectangle(200, 100)
        assert r.get_area(0) == pytest.approx(20000)

    def test_perimeter(self):
        r = Rectangle(200, 100)
        assert r.get_perimeter(0) == pytest.approx(600)

    def test_diagonal(self):
        r = Rectangle(300, 400)
        assert r.get_diagonal_length(0) == pytest.approx(500)

    def test_is_square(self):
        assert Rectangle(100, 100).is_square() is True
        assert Rectangle(100, 101).is_square() is False

    def test_aspect_ratio(self):
        assert Rectangle(200, 100).aspect_ratio() == pytest.approx(2.0)

    def test_get_corners(self):
        r = Rectangle(100, 50, x=10, y=20)
        corners = r.get_corners(0)
        assert corners[0] == pytest.approx((10, 20))     # top-left
        assert corners[1] == pytest.approx((110, 20))    # top-right
        assert corners[2] == pytest.approx((110, 70))    # bottom-right
        assert corners[3] == pytest.approx((10, 70))     # bottom-left

    def test_sample_border_corners(self):
        r = Rectangle(100, 50, x=0, y=0)
        # t=0: top-left corner
        assert r.sample_border(0, 0) == pytest.approx((0, 0))
        # t=1/3: 1/3 of perimeter = 100 (top edge done) → (100, 0)
        perim = 300
        t_at_corner = 100 / perim
        assert r.sample_border(t_at_corner, 0) == pytest.approx((100, 0))

    def test_shift_moves_position(self):
        r = Rectangle(100, 50, x=10, y=20)
        r.shift(dx=5, dy=10, start=0)
        assert r.x.at_time(0) == pytest.approx(15)
        assert r.y.at_time(0) == pytest.approx(30)

    def test_svg_output(self):
        r = Rectangle(100, 50, x=10, y=20)
        svg = r.to_svg(0)
        assert '<rect' in svg
        assert "width='100'" in svg
        assert "height='50'" in svg

    def test_path_no_rounding(self):
        r = Rectangle(100, 50, x=0, y=0, rx=0, ry=0)
        path = r.path(0)
        assert 'a' not in path.lower()  # no arcs

    def test_path_with_rounding(self):
        r = Rectangle(100, 50, x=0, y=0, rx=10, ry=10)
        path = r.path(0)
        assert 'a' in path.lower()  # has arc commands


class TestDot:

    def test_dot_is_small_circle(self):
        d = Dot(cx=100, cy=200)
        # Dot has default small radius
        assert d.rx.at_time(0) == 11  # DEFAULT_DOT_RADIUS
        assert d.center(0) == pytest.approx((100, 200))


class TestLines:

    def test_lines_is_open_polygon(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        # Lines is a Polygon with closed=False
        assert l.closed is False
        assert l.area(0) == 0.0

    def test_lines_perimeter(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        assert l.perimeter(0) == pytest.approx(200)
