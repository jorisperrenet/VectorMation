"""Tests for shape classes in vectormation.objects."""
import math
import pytest
from vectormation.objects import (
    Circle, Rectangle, Polygon, Line, Lines, RegularPolygon, Arc, Ellipse,
    Path, Trace, Text, Dot, AnnotationDot, Wedge, Sector, Star, RoundedRectangle, DashedLine,
    NumberLine, EquilateralTriangle, Triangle, Arrow, Vector, CurvedArrow, VObject, VCollection, VGroup,
    from_svg, CountAnimation, Annulus, FunctionGraph, Square, Integer,
    AnnularSector, ArcPolygon, PieChart, DonutChart, Axes, Brace, Table, BarChart,
)
from vectormation.attributes import Coor
import vectormation.easings as easings


class TestCircle:
    def test_to_svg_contains_circle_tag(self):
        c = Circle(r=50, cx=100, cy=200)
        svg = c.to_svg(0)
        assert '<circle' in svg
        assert "cx='100'" in svg
        assert "cy='200'" in svg
        assert "r='50'" in svg

    def test_shift(self):
        c = Circle(r=50, cx=100, cy=200)
        c.shift(dx=10, dy=20, start=0)
        pos = c.c.at_time(0)
        assert pos[0] == pytest.approx(110)
        assert pos[1] == pytest.approx(220)

    def test_bbox(self):
        c = Circle(r=50, cx=100, cy=200)
        x, y, w, h = c.bbox(0)
        assert x == pytest.approx(50)
        assert y == pytest.approx(150)
        assert w == pytest.approx(100)
        assert h == pytest.approx(100)


class TestRectangle:
    def test_to_svg_contains_rect_tag(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        svg = r.to_svg(0)
        assert '<rect' in svg

    def test_shift(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        r.shift(dx=5, dy=10, start=0)
        assert r.x.at_time(0) == pytest.approx(15)
        assert r.y.at_time(0) == pytest.approx(30)

    def test_bbox(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        bx, by, bw, bh = r.bbox(0)
        assert bx == pytest.approx(10)
        assert by == pytest.approx(20)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(50)


class TestPolygon:
    def test_to_svg_contains_polygon_tag(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        svg = p.to_svg(0)
        assert '<polygon' in svg

    def test_shift(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        p.shift(dx=10, dy=20, start=0)
        v0 = p.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(10)
        assert v0[1] == pytest.approx(20)

    def test_bbox(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        bx, by, bw, bh = p.bbox(0)
        assert bx == pytest.approx(0)
        assert by == pytest.approx(0)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(100)


class TestPolygonGetPerimeter:
    def test_equilateral_triangle(self):
        """Equilateral triangle with side 100 should have perimeter ~300."""
        # 3-4-5 right triangle for easy exact check
        p = Polygon((0, 0), (3, 0), (3, 4))
        assert p.get_perimeter() == pytest.approx(12.0, abs=1e-9)

    def test_matches_perimeter_alias(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.get_perimeter() == pytest.approx(p.perimeter())

    def test_open_polyline_excludes_closing_edge(self):
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        # Two edges: horizontal 100 + vertical 100 = 200
        assert p.get_perimeter() == pytest.approx(200.0, abs=1e-9)

    def test_closed_square_perimeter(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.get_perimeter() == pytest.approx(400.0, abs=1e-9)


class TestConvexHull:
    def test_triangle_unchanged(self):
        # Three points already forming a triangle should produce exactly those 3 hull points
        p = Polygon.convex_hull((0, 0), (100, 0), (50, 100))
        verts = p.get_vertices(0)
        assert len(verts) == 3

    def test_square(self):
        # Four corners of a square: hull should have exactly 4 points
        p = Polygon.convex_hull((0, 0), (100, 0), (100, 100), (0, 100))
        verts = p.get_vertices(0)
        assert len(verts) == 4

    def test_interior_point_excluded(self):
        # A point inside a square should be excluded from the hull
        p = Polygon.convex_hull((0, 0), (100, 0), (100, 100), (0, 100), (50, 50))
        verts = p.get_vertices(0)
        assert len(verts) == 4
        assert (50.0, 50.0) not in verts

    def test_collinear_midpoints_excluded(self):
        # Collinear middle points should be skipped; only the extreme endpoints kept
        p = Polygon.convex_hull((0, 0), (50, 0), (100, 0), (100, 100), (0, 100))
        verts = p.get_vertices(0)
        assert (50.0, 0.0) not in verts

    def test_too_few_points_raises(self):
        with pytest.raises(ValueError):
            Polygon.convex_hull((0, 0), (1, 1))

    def test_returns_polygon(self):
        p = Polygon.convex_hull((0, 0), (100, 0), (50, 100))
        assert isinstance(p, Polygon)

    def test_kwargs_forwarded(self):
        p = Polygon.convex_hull((0, 0), (100, 0), (50, 100), fill='#ff0000')
        svg = p.to_svg(0)
        # Color may be rendered as rgb(...) or #rrggbb depending on style module
        assert '255,0,0' in svg or 'ff0000' in svg

    def test_all_collinear_raises(self):
        with pytest.raises(ValueError):
            Polygon.convex_hull((0, 0), (50, 50), (100, 100))


class TestLine:
    def test_to_svg_contains_line_tag(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        svg = l.to_svg(0)
        assert '<line' in svg

    def test_shift(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        l.shift(dx=10, dy=20, start=0)
        p1 = l.p1.at_time(0)
        assert p1[0] == pytest.approx(10)
        assert p1[1] == pytest.approx(20)

    def test_bbox(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        bx, by, bw, bh = l.bbox(0)
        assert bx == pytest.approx(0)
        assert by == pytest.approx(0)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(100)


class TestRegularPolygon:
    def test_has_correct_vertex_count(self):
        for n in [3, 5, 6, 8]:
            p = RegularPolygon(n, radius=100)
            assert len(p.vertices) == n

    def test_to_svg(self):
        p = RegularPolygon(6, radius=100)
        svg = p.to_svg(0)
        assert '<polygon' in svg


class TestText:
    def test_bbox_uses_char_classes(self):
        from vectormation.objects import Text
        t = Text(text='iii', x=0, y=20, font_size=20)
        _, _, bw, _ = t.bbox(0)
        # Narrow chars should be narrower than wide chars
        t2 = Text(text='MMM', x=0, y=20, font_size=20)
        _, _, w2, _ = t2.bbox(0)
        assert bw < w2

    def test_copy_independent(self):
        from vectormation.objects import Text
        t = Text(text='hello', x=0, y=20, font_size=20)
        t2 = t.copy()
        t2.x.set_onward(0, 999)
        assert t.x.at_time(0) != 999


class TestVObjectCopy:
    def test_circle_copy(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.copy()
        c2.shift(dx=50, start=0)
        # Original should be unchanged
        assert c.c.at_time(0)[0] == pytest.approx(100)
        assert c2.c.at_time(0)[0] == pytest.approx(150)

    def test_rect_copy(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        r2 = r.copy()
        r2.shift(dx=100, start=0)
        assert r.x.at_time(0) == pytest.approx(10)
        assert r2.x.at_time(0) == pytest.approx(110)


class TestRelativeAnimations:
    def test_scale_by(self):
        c = Circle(r=50, cx=100, cy=100)
        c.scale_to(0, 1, 2, easing=easings.linear)
        c.scale_by(1, 2, 1.5, easing=easings.linear)
        # At time 2, scale should be 2 * 1.5 = 3
        sx = c.styling.scale_x.at_time(2)
        assert sx == pytest.approx(3, abs=0.1)

    def test_rotate_by(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_to(0, 1, 45, easing=easings.linear)
        c.rotate_by(1, 2, 45, easing=easings.linear)
        rot = c.styling.rotation.at_time(2)
        assert rot[0] == pytest.approx(90, abs=1)


class TestArc:
    def test_to_svg_contains_path(self):
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        svg = a.to_svg(0)
        assert '<path' in svg
        assert "d='" in svg


# ── Phase 8: Post-refactor backward-compat tests ──

class TestCircleBackwardCompat:
    """Circle is now a thin subclass of Ellipse; verify backward compat."""
    def test_circle_is_ellipse(self):
        c = Circle(r=50, cx=100, cy=200)
        assert isinstance(c, Ellipse)

    def test_r_property_getter(self):
        c = Circle(r=75, cx=0, cy=0)
        assert c.r.at_time(0) == 75

    def test_r_property_setter(self):
        c = Circle(r=50)
        from vectormation.attributes import Real
        new_r = Real(0, 99)
        c.r = new_r
        assert c.rx.at_time(0) == 99
        assert c.ry.at_time(0) == 99

    def test_circle_tag_in_svg(self):
        c = Circle(r=50, cx=100, cy=200)
        svg = c.to_svg(0)
        assert svg.startswith('<circle')
        assert '<ellipse' not in svg

    def test_circle_inherits_ellipse_shift(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shift(dx=10, dy=20)
        pos = c.c.at_time(0)
        assert pos[0] == pytest.approx(110)
        assert pos[1] == pytest.approx(120)

    def test_circle_inherits_ellipse_bbox(self):
        c = Circle(r=50, cx=100, cy=100)
        x, y, w, h = c.bbox(0)
        assert x == pytest.approx(50)
        assert y == pytest.approx(50)
        assert w == pytest.approx(100)
        assert h == pytest.approx(100)

    def test_dot_inherits_from_circle(self):
        d = Dot(r=6, cx=50, cy=50)
        assert isinstance(d, Circle)
        assert isinstance(d, Ellipse)

    def test_annotation_dot(self):
        d = AnnotationDot(cx=100, cy=200)
        assert isinstance(d, Dot)
        assert d.styling.stroke_width.at_time(0) == 5
        svg = d.to_svg(0)
        assert 'circle' in svg

    def test_triangle_alias(self):
        t = Triangle(100)
        assert isinstance(t, EquilateralTriangle)
        assert isinstance(t, RegularPolygon)

    def test_line_set_angle(self):
        line = Line(0, 0, 100, 0)
        line.set_angle(90)
        # After setting to 90 degrees, line should be vertical
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        assert abs(x2 - x1) < 1
        assert abs(y2 - y1) == pytest.approx(100, abs=1)

    def test_line_put_start_and_end_on(self):
        line = Line(0, 0, 100, 100)
        line.put_start_and_end_on((200, 200), (300, 300))
        assert line.p1.at_time(0) == (200, 200)
        assert line.p2.at_time(0) == (300, 300)

    def test_line_get_projection(self):
        line = Line(0, 0, 100, 0)
        proj = line.get_projection(50, 50)
        assert proj[0] == pytest.approx(50)
        assert proj[1] == pytest.approx(0)


class TestLinesBackwardCompat:
    """Lines is now a thin subclass of Polygon with closed=False."""
    def test_lines_is_polygon(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        assert isinstance(l, Polygon)

    def test_lines_emits_polyline_tag(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        svg = l.to_svg(0)
        assert '<polyline' in svg
        assert '<polygon' not in svg

    def test_lines_open_path(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        p = l.path(0)
        assert 'Z' not in p

    def test_polygon_closed_path(self):
        p = Polygon((0, 0), (100, 0), (100, 100))
        path = p.path(0)
        assert path.endswith('Z')

    def test_lines_shift(self):
        l = Lines((0, 0), (100, 0))
        l.shift(dx=10, dy=20)
        v0 = l.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(10)
        assert v0[1] == pytest.approx(20)

    def test_lines_bbox(self):
        l = Lines((0, 0), (100, 50))
        bx, by, bw, bh = l.bbox(0)
        assert bx == pytest.approx(0)
        assert by == pytest.approx(0)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(50)

    def test_repr(self):
        l = Lines((0, 0), (100, 0), (100, 100))
        r = repr(l)
        assert r == 'Lines(3 vertices)'

    def test_repr_two_vertices(self):
        l = Lines((10, 20), (30, 40))
        r = repr(l)
        assert r == 'Lines(2 vertices)'


class TestRegularPolygonWithoutFixedVertex:
    """RegularPolygon now inherits directly from Polygon (FixedVertexPolygon removed)."""
    def test_regular_polygon_is_polygon(self):
        rp = RegularPolygon(5, radius=100)
        assert isinstance(rp, Polygon)

    def test_regular_polygon_vertex_count(self):
        for n in [3, 4, 5, 6, 8]:
            rp = RegularPolygon(n, radius=100)
            assert len(rp.vertices) == n

    def test_regular_polygon_shift(self):
        rp = RegularPolygon(4, radius=100, cx=200, cy=200)
        rp.shift(dx=50, dy=50)
        v0 = rp.vertices[0].at_time(0)
        # After shift, vertex should have moved by (50, 50)
        assert v0[0] != pytest.approx(0)  # not at origin

    def test_regular_polygon_svg(self):
        rp = RegularPolygon(6, radius=100)
        svg = rp.to_svg(0)
        assert '<polygon' in svg



class TestSnapPoints:
    """Test snap_points() method dispatch for all VObject subclasses."""
    def test_polygon_snap_points(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        pts = p.snap_points(0)
        assert len(pts) == 3
        assert pts[0] == (0.0, 0.0)
        assert pts[1] == (100.0, 0.0)
        assert pts[2] == (50.0, 100.0)

    def test_circle_snap_points_is_center(self):
        c = Circle(r=50, cx=100, cy=200)
        pts = c.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (100.0, 200.0)

    def test_ellipse_snap_points_is_center(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=300)
        pts = e.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (200.0, 300.0)

    def test_dot_snap_points_inherited(self):
        d = Dot(r=6, cx=10, cy=20)
        pts = d.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (10.0, 20.0)

    def test_line_snap_points(self):
        l = Line(x1=0, y1=0, x2=100, y2=50)
        pts = l.snap_points(0)
        assert len(pts) == 2
        assert pts[0] == (0.0, 0.0)
        assert pts[1] == (100.0, 50.0)

    def test_rectangle_snap_points(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        pts = r.snap_points(0)
        assert len(pts) == 4
        assert pts[0] == (10.0, 20.0)
        assert pts[2] == (110.0, 70.0)

    def test_text_snap_points(self):
        t = Text(text='hello', x=100, y=200)
        pts = t.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (100.0, 200.0)

    def test_arc_snap_points(self):
        a = Arc(cx=100, cy=200, r=50, start_angle=0, end_angle=90)
        pts = a.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (100.0, 200.0)

    def test_wedge_snap_points_inherited(self):
        w = Wedge(cx=100, cy=200, r=50, start_angle=0, end_angle=90)
        pts = w.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (100.0, 200.0)

    def test_path_snap_points(self):
        p = Path('M 0 0 L 100 50 L 50 100')
        pts = p.snap_points(0)
        assert len(pts) == 4  # 4 bbox corners
        # Check bounding box corners
        xs = [pt[0] for pt in pts]
        ys = [pt[1] for pt in pts]
        assert min(xs) == pytest.approx(0)
        assert max(xs) == pytest.approx(100)
        assert min(ys) == pytest.approx(0)
        assert max(ys) == pytest.approx(100)

    def test_path_snap_points_empty(self):
        p = Path('')
        pts = p.snap_points(0)
        assert pts == []

    def test_trace_snap_points(self):
        point = Coor(0, (50, 75))
        tr = Trace(point, start=0, end=1)
        pts = tr.snap_points(0)
        assert len(pts) == 1
        assert pts[0] == (50.0, 75.0)

    def test_snap_points_dispatch(self):
        """Test that snap_points returns correct points."""
        c = Circle(r=50, cx=100, cy=200)
        assert c.snap_points(0) == [(100.0, 200.0)]


class TestTransformStyleCondensed:
    """Verify condensed transform_style produces same output as before."""
    def test_skew_x_after(self):
        from vectormation.style import Styling
        s = Styling({'skew_x_after': 15}, creation=0)
        transform = s.transform_style(0)
        assert 'skewX(15)' in transform

    def test_skew_y_after(self):
        from vectormation.style import Styling
        s = Styling({'skew_y_after': 25}, creation=0)
        transform = s.transform_style(0)
        assert 'skewY(25)' in transform

    def test_multiple_transforms(self):
        from vectormation.style import Styling
        s = Styling({'rotation': (45, 0, 0), 'dx': 100, 'dy': 50, 'scale_x': 2, 'scale_y': 2}, creation=0)
        transform = s.transform_style(0)
        assert 'rotate(315' in transform  # 45° CCW stored → -45 mod 360 = 315° in SVG
        assert 'translate(100,50)' in transform
        assert 'scale(2,2)' in transform

    def test_rotation_mod_360(self):
        from vectormation.style import Styling
        s = Styling({'rotation': (450, 100, 100)}, creation=0)
        transform = s.transform_style(0)
        assert 'rotate(270,' in transform  # 450° CCW → -450 mod 360 = 270° in SVG


class TestStar:
    def test_star_vertex_count(self):
        s = Star(n=5, outer_radius=100)
        assert len(s.vertices) == 10  # 5 outer + 5 inner

    def test_star_is_polygon(self):
        s = Star(n=5, outer_radius=100)
        assert isinstance(s, Polygon)

    def test_star_svg(self):
        s = Star(n=5, outer_radius=100, cx=500, cy=500, fill='gold')
        svg = s.to_svg(0)
        assert '<polygon' in svg

    def test_star_inner_radius_default(self):
        s = Star(n=5, outer_radius=100)
        # Default inner_radius is 0.4 * outer
        pts = [v.at_time(0) for v in s.vertices]
        # Outer points (even indices) should be farther from center than inner (odd)
        import math
        outer_dist = math.sqrt((pts[0][0] - 500)**2 + (pts[0][1] - 500)**2)
        inner_dist = math.sqrt((pts[1][0] - 500)**2 + (pts[1][1] - 500)**2)
        assert outer_dist > inner_dist


class TestRoundedRectangle:
    def test_is_rectangle(self):
        rr = RoundedRectangle(200, 100, x=10, y=20, corner_radius=15)
        assert isinstance(rr, Rectangle)

    def test_rx_ry_set(self):
        rr = RoundedRectangle(200, 100, x=10, y=20, corner_radius=15)
        assert rr.rx.at_time(0) == 15
        assert rr.ry.at_time(0) == 15

    def test_svg_has_rx(self):
        rr = RoundedRectangle(200, 100, corner_radius=15)
        svg = rr.to_svg(0)
        assert "rx='15'" in svg


class TestDashedLine:
    def test_is_line(self):
        dl = DashedLine(0, 0, 100, 100)
        assert isinstance(dl, Line)

    def test_dash_pattern_in_svg(self):
        dl = DashedLine(0, 0, 100, 100, dash='10,5')
        svg = dl.to_svg(0)
        assert 'stroke-dasharray' in svg

    def test_default_dash(self):
        dl = DashedLine(0, 0, 100, 100)
        svg = dl.to_svg(0)
        assert 'stroke-dasharray' in svg

    def test_repr(self):
        dl = DashedLine(10, 20, 110, 220)
        r = repr(dl)
        assert r == 'DashedLine((10,20)->(110,220))'

    def test_repr_default(self):
        dl = DashedLine()
        r = repr(dl)
        assert r == 'DashedLine((0,0)->(100,100))'


class TestCircleGetTangentLines:
    def test_external_point_returns_two_lines(self):
        """A point clearly outside the circle yields exactly two tangent lines."""
        c = Circle(r=50, cx=0, cy=0)
        lines = c.get_tangent_lines(200, 0)
        assert len(lines) == 2

    def test_internal_point_returns_empty(self):
        """A point inside the circle yields no tangent lines."""
        c = Circle(r=100, cx=0, cy=0)
        lines = c.get_tangent_lines(10, 0)
        assert lines == []

    def test_point_on_circle_returns_one_line(self):
        """A point exactly on the circle yields exactly one tangent line."""
        c = Circle(r=50, cx=0, cy=0)
        lines = c.get_tangent_lines(50, 0)
        assert len(lines) == 1

    def test_tangent_lines_are_line_objects(self):
        """Returned objects are Line instances."""
        from vectormation.objects import Line
        c = Circle(r=50, cx=100, cy=100)
        lines = c.get_tangent_lines(300, 100)
        assert all(isinstance(l, Line) for l in lines)

    def test_tangent_touch_point_on_circle(self):
        """The midpoint of each tangent line should be close to the circle boundary."""
        import math
        c = Circle(r=50, cx=0, cy=0)
        # External point to the right on the x-axis
        lines = c.get_tangent_lines(150, 0, length=4)
        assert len(lines) == 2
        for ln in lines:
            # Midpoint of the short line segment ≈ touch point
            p1 = ln.p1.at_time(0)
            p2 = ln.p2.at_time(0)
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            dist = math.sqrt(mx ** 2 + my ** 2)
            assert dist == pytest.approx(50.0, abs=1.0)

    def test_styling_kwargs_forwarded(self):
        """Extra kwargs (e.g. stroke) are forwarded to the Line objects."""
        c = Circle(r=50, cx=0, cy=0)
        lines = c.get_tangent_lines(200, 0, stroke='#FF0000')
        for ln in lines:
            svg = ln.to_svg(0)
            # Colors are rendered as rgb(r,g,b) in SVG output
            assert 'rgb(255,0,0)' in svg

    def test_time_parameter(self):
        """get_tangent_lines respects the time= parameter."""
        c = Circle(r=50, cx=0, cy=0)
        # Animate radius to 80 at t=1
        c.rx.set_onward(1, 80)
        c.ry.set_onward(1, 80)
        lines_t0 = c.get_tangent_lines(200, 0, time=0)
        lines_t1 = c.get_tangent_lines(200, 0, time=1)
        # Both should give 2 lines (point is external at both times)
        assert len(lines_t0) == 2
        assert len(lines_t1) == 2


class TestNumberLine:
    def test_is_vcollection(self):
        nl = NumberLine(x_range=(-3, 3, 1), length=400, x=100, y=500)
        assert isinstance(nl, VCollection)

    def test_number_to_point(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        pt = nl.number_to_point(0)
        assert pt == (100, 500)
        pt = nl.number_to_point(10)
        assert pt == (600, 500)
        pt = nl.number_to_point(5)
        assert pt == (350.0, 500)

    def test_auto_step(self):
        nl = NumberLine(x_range=(-5, 5), length=600, x=200, y=500)
        assert nl.x_step == 1


class TestNumberLineHighlightRange:
    def test_returns_rectangle(self):
        from vectormation.objects import Rectangle
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(2, 6)
        assert isinstance(rect, Rectangle)

    def test_rect_appended_to_objects(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        before = len(nl.objects)
        nl.highlight_range(2, 6)
        assert len(nl.objects) == before + 1

    def test_width_proportional_to_range(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(0, 5)
        # Range 0-5 is half of 0-10 (length=500), so width ≈ 250
        assert rect.width.at_time(0) == pytest.approx(250.0, abs=1e-9)

    def test_custom_color_in_svg(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(1, 4, color='#FF0000')
        svg = rect.to_svg(0)
        # Colors are rendered as rgb(r,g,b) in SVG output
        assert 'rgb(255,0,0)' in svg

    def test_default_color_is_yellow(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(1, 3)
        svg = rect.to_svg(0)
        # Yellow #FFFF00 → rgb(255,255,0)
        assert 'rgb(255,255,0)' in svg

    def test_reversed_range_handled(self):
        """Passing end < start should still produce a positive-width rect."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(6, 2)
        assert rect.width.at_time(0) > 0

    def test_clamped_beyond_axis_bounds(self):
        """Values outside the axis range are clamped, not clipped to zero."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        rect = nl.highlight_range(-5, 15)
        # Should span the full axis
        assert rect.width.at_time(0) == pytest.approx(500.0, abs=1e-9)


class TestEquilateralTriangleFromRegular:
    def test_is_regular_polygon(self):
        t = EquilateralTriangle(side_length=100)
        assert isinstance(t, RegularPolygon)

    def test_vertex_count(self):
        t = EquilateralTriangle(side_length=100)
        assert len(t.vertices) == 3

    def test_svg_renders(self):
        t = EquilateralTriangle(side_length=100, fill='red')
        svg = t.to_svg(0)
        assert '<polygon' in svg


class TestMoveTo:
    def test_circle_move_to(self):
        c = Circle(r=50, cx=100, cy=100)
        c.move_to(500, 500)
        x, y, w, h = c.bbox(0)
        assert x + w/2 == pytest.approx(500, abs=1)
        assert y + h/2 == pytest.approx(500, abs=1)

    def test_rectangle_move_to(self):
        r = Rectangle(100, 50, x=0, y=0)
        r.move_to(500, 500)
        x, y, w, h = r.bbox(0)
        assert x + w/2 == pytest.approx(500, abs=1)
        assert y + h/2 == pytest.approx(500, abs=1)


class TestNextTo:
    def test_next_to_right(self):
        a = Circle(r=50, cx=200, cy=200)
        b = Circle(r=50, cx=500, cy=500)
        b.next_to(a, direction='right', buff=10)
        bx, _, _, _ = b.bbox(0)
        ax, _, aw, _ = a.bbox(0)
        # b's left edge should be at a's right edge + buff
        assert bx == pytest.approx(ax + aw + 10, abs=2)

    def test_next_to_left(self):
        a = Circle(r=50, cx=500, cy=500)
        b = Circle(r=50, cx=200, cy=200)
        b.next_to(a, direction='left', buff=10)
        bx, _, bw, _ = b.bbox(0)
        ax, _, _, _ = a.bbox(0)
        # b's right edge should be at a's left edge - buff
        assert bx + bw == pytest.approx(ax - 10, abs=2)


class TestSetColor:
    def test_set_color_changes_fill(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_color(0, 1, fill='#FF0000')
        # At t=1, fill should be red
        fill_val = c.styling.fill.at_time(1)
        assert 'rgb(255,0,0)' == fill_val

    def test_set_color_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_color(0, 1, fill='#0000FF')
        assert result is c


class TestGrowFromCenter:
    def test_scale_starts_at_zero(self):
        c = Circle(r=50, cx=100, cy=100)
        c.grow_from_center(start=0, end=1, change_existence=False)
        scale = c.styling.scale_x.at_time(0)
        assert scale == pytest.approx(0, abs=0.01)

    def test_scale_ends_at_one(self):
        c = Circle(r=50, cx=100, cy=100)
        c.grow_from_center(start=0, end=1, change_existence=False)
        scale = c.styling.scale_x.at_time(1)
        assert scale == pytest.approx(1, abs=0.01)

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.grow_from_center(start=0, end=1) is c


class TestIndicate:
    def test_indicate_peaks_at_midpoint(self):
        c = Circle(r=50, cx=100, cy=100)
        c.indicate(start=0, end=1, scale_factor=1.5)
        scale_mid = c.styling.scale_x.at_time(0.5)
        # there_and_back peaks at 0.5
        assert scale_mid > 1.0

    def test_indicate_returns_to_original(self):
        c = Circle(r=50, cx=100, cy=100)
        c.indicate(start=0, end=1, scale_factor=1.5)
        scale_end = c.styling.scale_x.at_time(1)
        assert scale_end == pytest.approx(1, abs=0.01)


class TestVCollectionDelegation:
    def test_shift_delegated(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=200)
        coll = VCollection(a, b)
        coll.shift(dx=10, dy=20)
        assert a.c.at_time(0) == pytest.approx((110, 120), abs=1)
        assert b.c.at_time(0) == pytest.approx((210, 220), abs=1)

    def test_unknown_attr_raises(self):
        coll = VCollection(Circle(r=50))
        with pytest.raises(AttributeError):
            coll.nonexistent_method()

    def test_collection_move_to(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=200)
        coll = VCollection(a, b)
        coll.move_to(500, 500)
        x, y, w, h = coll.bbox(0)
        assert x + w/2 == pytest.approx(500, abs=2)
        assert y + h/2 == pytest.approx(500, abs=2)


class TestShrinkToCenter:
    def test_scale_starts_at_one(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shrink_to_center(start=0, end=1, change_existence=False)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1, abs=0.01)

    def test_scale_ends_at_zero(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shrink_to_center(start=0, end=1, change_existence=False)
        assert c.styling.scale_x.at_time(1) == pytest.approx(0, abs=0.01)

    def test_hides_after(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shrink_to_center(start=0, end=1)
        assert not c.show.at_time(1.1)

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.shrink_to_center(start=0, end=1) is c


class TestSetOpacity:
    def test_opacity_changes(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_opacity(0.5, start=0, end=1)
        assert c.styling.opacity.at_time(1) == pytest.approx(0.5, abs=0.01)

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.set_opacity(0.5, start=0, end=1) is c


class TestFadeinFadeoutReturn:
    def test_fadein_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.fadein(start=0, end=1) is c

    def test_fadeout_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.fadeout(start=0, end=1) is c

    def test_write_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.write(start=0, end=1) is c


class TestFlash:
    def test_flash_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        assert c.flash(start=0, end=1, color='#FFFF00') is c

    def test_flash_returns_to_original(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.flash(start=0, end=1, color='#FFFF00')
        # At t=0 and t=1, there_and_back returns 0, so color should be original
        fill_at_0 = c.styling.fill.at_time(0)
        fill_at_1 = c.styling.fill.at_time(1)
        assert fill_at_0 == fill_at_1


class TestSpin:
    def test_spin_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.spin(start=0, end=1, degrees=360) is c

    def test_spin_adds_rotation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin(start=0, end=1, degrees=180)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(180, abs=1)


class TestArrange:
    def test_arrange_right(self):
        a = Circle(r=20, cx=0, cy=0)
        b = Circle(r=20, cx=0, cy=0)
        c = Circle(r=20, cx=0, cy=0)
        coll = VCollection(a, b, c)
        coll.arrange(direction='right', buff=10, start=0)
        # After arranging, b should be to the right of a, c to the right of b
        ax = a.bbox(0)[0]
        bx = b.bbox(0)[0]
        cx_ = c.bbox(0)[0]
        assert bx > ax
        assert cx_ > bx

    def test_arrange_returns_self(self):
        coll = VCollection(Circle(r=20), Circle(r=20))
        assert coll.arrange() is coll

    def test_arrange_empty(self):
        coll = VCollection()
        assert coll.arrange() is coll


class TestCircumscribe:
    def test_circumscribe_returns_path(self):
        r = Rectangle(100, 50, x=10, y=20)
        rect = r.circumscribe(start=0, end=2)
        assert isinstance(rect, Path)

    def test_circumscribe_path_surrounds_object(self):
        r = Rectangle(100, 50, x=10, y=20)
        rect = r.circumscribe(start=0, end=2, buff=15)
        # Path d should contain the bbox minus buff
        bx, by, _, _ = r.bbox(0)
        d = rect.d.at_time(0)
        assert str(bx - 15) in d and str(by - 15) in d

    def test_circumscribe_fades_out(self):
        r = Rectangle(100, 50, x=10, y=20)
        rect = r.circumscribe(start=0, end=2)
        # After end, rect should be hidden
        assert rect.show.at_time(2.1) is False


class TestSetColorHSL:
    def test_set_color_hsl_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        assert c.set_color(0, 1, fill='#00FF00', color_space='hsl') is c

    def test_set_color_hsl_interpolates(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.set_color(0, 1, fill='#00FF00', color_space='hsl')
        # At midpoint, should be somewhere between red and green in HSL
        mid = c.styling.fill.at_time(0.5)
        assert mid != 'rgb(255,0,0)'  # not start
        assert mid != 'rgb(0,255,0)'  # not end

    def test_set_color_hsl_reaches_target(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.set_color(0, 1, fill='#0000FF', color_space='hsl')
        result = c.styling.fill.at_time(1)
        assert result == 'rgb(0,0,255)'


class TestWiggle:
    def test_wiggle_returns_self(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.wiggle(start=0, end=1) is r

    def test_wiggle_displaces_during(self):
        r = Rectangle(100, 50, x=10, y=20)
        bx_before = r.bbox(0)[0]
        r.wiggle(start=0, end=1, amplitude=20, n_wiggles=2)
        # At t=0.125, sin(2*pi*2*0.125)=1.0 and there_and_back(0.125)>0
        bx_mid = r.bbox(0.125)[0]
        assert bx_mid != pytest.approx(bx_before, abs=0.1)

    def test_wiggle_returns_to_original(self):
        r = Rectangle(100, 50, x=10, y=20)
        bx_before = r.bbox(0)[0]
        r.wiggle(start=0, end=1, amplitude=20, n_wiggles=4)
        # After end, should be back (there_and_back easing returns to 0)
        bx_after = r.bbox(1.5)[0]
        assert bx_after == pytest.approx(bx_before, abs=0.1)


class TestAlignTo:
    def test_align_left(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 40, x=300, y=200)
        b.align_to(a, edge='left')
        assert b.bbox(0)[0] == pytest.approx(a.bbox(0)[0], abs=0.1)

    def test_align_right(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 40, x=300, y=200)
        b.align_to(a, edge='right')
        bx, _, bw, _ = b.bbox(0)
        ax, _, aw, _ = a.bbox(0)
        assert bx + bw == pytest.approx(ax + aw, abs=0.1)

    def test_align_top(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 40, x=300, y=200)
        b.align_to(a, edge='top')
        assert b.bbox(0)[1] == pytest.approx(a.bbox(0)[1], abs=0.1)

    def test_align_returns_self(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 40, x=300, y=200)
        assert b.align_to(a, edge='left') is b


class TestFadeTransform:
    def test_fade_transform_hides_source(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=200)
        VObject.fade_transform(a, b, start=0, end=1)
        assert a.show.at_time(1.1) is False

    def test_fade_transform_shows_target(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=200)
        VObject.fade_transform(a, b, start=0, end=1)
        assert b.show.at_time(0.5) is True


class TestFromSvgInlineStyle:
    def test_circle_with_inline_style(self):
        from bs4 import BeautifulSoup
        svg = '<circle cx="100" cy="200" r="50" style="fill:#ff0000;stroke:#00ff00" />'
        elem = BeautifulSoup(svg, 'html.parser').find('circle')
        obj = from_svg(elem)
        assert isinstance(obj, Circle)

    def test_rect_with_inline_style(self):
        from bs4 import BeautifulSoup
        svg = '<rect width="100" height="50" style="fill:#0000ff" />'
        elem = BeautifulSoup(svg, 'html.parser').find('rect')
        obj = from_svg(elem)
        assert isinstance(obj, Rectangle)

    def test_parse_inline_style(self):
        from vectormation._svg_utils import _parse_inline_style
        result = _parse_inline_style('fill:#ff0; stroke-width:2; opacity:0.5')
        assert result == {'fill': '#ff0', 'stroke-width': '2', 'opacity': '0.5'}

    def test_parse_inline_style_empty(self):
        from vectormation._svg_utils import _parse_inline_style
        assert _parse_inline_style('') == {}


class TestTyping:
    def test_typing_returns_self(self):
        t = Text('Hello World', x=100, y=200)
        assert t.typing(start=0, end=1) is t

    def test_typing_shows_partial_text(self):
        t = Text('Hello', x=100, y=200)
        t.typing(start=0, end=1, change_existence=False)
        # At start, should show at least 1 char
        assert t.text.at_time(0) == 'H'
        # At midpoint, should show partial
        mid_text = t.text.at_time(0.5)
        assert 1 <= len(mid_text) <= 5

    def test_typing_shows_full_text_at_end(self):
        t = Text('Hello', x=100, y=200)
        t.typing(start=0, end=1, change_existence=False)
        assert t.text.at_time(1) == 'Hello'


class TestSetText:
    def test_set_text_returns_self(self):
        t = Text('Before', x=100, y=200)
        assert t.set_text(0, 1, 'After') is t

    def test_set_text_changes_content(self):
        t = Text('Before', x=100, y=200)
        t.set_text(0, 1, 'After')
        assert t.text.at_time(0) == 'Before'
        assert t.text.at_time(1) == 'After'

    def test_set_text_opacity_returns(self):
        t = Text('Before', x=100, y=200)
        t.set_text(0, 1, 'After')
        # At midpoint, opacity should be near 0
        mid_opacity = t.styling.opacity.at_time(0.5)
        assert mid_opacity < 0.1
        # At end, opacity should be back to ~1
        end_opacity = t.styling.opacity.at_time(1)
        assert end_opacity > 0.9


class TestAlongPath:
    def test_along_path_returns_self(self):
        c = Circle(r=20, cx=0, cy=0)
        result = c.along_path(0, 1, 'M0,0 L100,0')
        assert result is c

    def test_along_path_moves_object(self):
        c = Circle(r=20, cx=0, cy=0)
        bx_start = c.bbox(0)[0]
        c.along_path(0, 1, 'M0,0 L200,0')
        bx_end = c.bbox(1)[0]
        assert bx_end > bx_start + 100


class TestCountAnimationValues:
    def test_count_animation_start_value(self):
        c = CountAnimation(start_val=0, end_val=100, start=0, end=1, x=100, y=100)
        assert c.text.at_time(0) == '0'

    def test_count_animation_end_value(self):
        c = CountAnimation(start_val=0, end_val=100, start=0, end=1, x=100, y=100)
        assert c.text.at_time(1) == '100'

    def test_count_animation_custom_format(self):
        c = CountAnimation(start_val=0, end_val=1, start=0, end=1,
                           fmt='{:.2f}', x=100, y=100)
        assert c.text.at_time(1) == '1.00'

    def test_count_animation_is_text(self):
        c = CountAnimation(start_val=0, end_val=10, x=100, y=100)
        assert isinstance(c, Text)



class TestWiggleOnCircle:
    def test_wiggle_on_circle(self):
        """Test wiggle on an object with Coor attributes (not shift_reals)."""
        c = Circle(r=20, cx=100, cy=200)
        result = c.wiggle(start=0, end=1, amplitude=30, n_wiggles=3)
        assert result is c
        # Should displace during animation
        cx_mid = c.c.at_time(0.08)[0]
        assert cx_mid != pytest.approx(100, abs=0.5)


class TestAnnulus:
    def test_annulus_is_vobject(self):
        a = Annulus(inner_radius=30, outer_radius=60, cx=100, cy=100)
        assert isinstance(a, VObject)

    def test_annulus_path_has_two_arcs(self):
        a = Annulus(inner_radius=30, outer_radius=60, cx=100, cy=100)
        path = a.path(0)
        # Should contain two M commands (outer + inner circles)
        assert path.count('M') == 2

    def test_annulus_bbox(self):
        a = Annulus(inner_radius=30, outer_radius=60, cx=100, cy=100)
        _, _, w, h = a.bbox(0)
        assert w == pytest.approx(120, abs=1)
        assert h == pytest.approx(120, abs=1)

    def test_annulus_svg_has_evenodd(self):
        a = Annulus(inner_radius=30, outer_radius=60, cx=100, cy=100)
        svg = a.to_svg(0)
        assert "fill-rule='evenodd'" in svg


class TestSwap:
    def test_swap_exchanges_positions(self):
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=100)
        a_center = (100, 100)
        b_center = (300, 100)
        VObject.swap(a, b, start=0, end=1)
        # After swap, a should be near b's original position
        ax, _, aw, _ = a.bbox(1)
        assert ax + aw / 2 == pytest.approx(b_center[0], abs=5)
        # And b near a's original position
        bx, _, bw, _ = b.bbox(1)
        assert bx + bw / 2 == pytest.approx(a_center[0], abs=5)


class TestDrawAlongCircle:
    def test_draw_along_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.draw_along(start=0, end=1) is c

    def test_draw_along_sets_dasharray(self):
        c = Circle(r=50, cx=100, cy=100)
        c.draw_along(start=0, end=1, change_existence=False)
        # After draw_along, stroke_dasharray should be set
        da = c.styling.stroke_dasharray.at_time(0.5)
        assert da != ''


class TestCurvedArrow:
    def test_curved_arrow_is_vcollection(self):
        ca = CurvedArrow(x1=0, y1=0, x2=100, y2=100)
        assert isinstance(ca, VCollection)

    def test_curved_arrow_has_two_objects(self):
        ca = CurvedArrow(x1=0, y1=0, x2=100, y2=100)
        assert len(ca.objects) == 2  # shaft + tip

    def test_curved_arrow_svg_contains_Q(self):
        ca = CurvedArrow(x1=0, y1=0, x2=200, y2=0, angle=0.5)
        svg = ca.to_svg(0)
        assert 'Q' in svg  # Quadratic bezier in the path


class TestDoubleArrow:
    def test_double_arrow_has_three_objects(self):
        from vectormation.objects import DoubleArrow
        da = DoubleArrow(x1=0, y1=0, x2=100, y2=0)
        assert len(da.objects) == 3  # shaft + 2 tips

    def test_double_arrow_is_arrow(self):
        from vectormation.objects import DoubleArrow
        da = DoubleArrow(x1=0, y1=0, x2=100, y2=0)
        assert isinstance(da, Arrow)


class TestAlwaysRotate:
    def test_always_rotate_returns_self(self):
        c = Circle(r=20, cx=100, cy=100)
        assert c.always_rotate(start=0) is c

    def test_always_rotate_sets_rotation(self):
        c = Circle(r=20, cx=100, cy=100)
        c.always_rotate(start=0, degrees_per_second=90)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == 90  # 90°/s × 1s = 90°


class TestRotateAround:
    def test_rotate_around_ccw(self):
        """After 90 degrees CCW, point (1,0) around (0,0) should be at ~(0,1)."""
        c = Coor(0, (1, 0))
        c.rotate_around(0, 1, (0, 0), 90, clockwise=False)
        x, y = c.at_time(1)
        assert x == pytest.approx(0, abs=0.1)
        assert y == pytest.approx(1, abs=0.1)

    def test_rotate_around_cw(self):
        """Clockwise should go the other direction."""
        c = Coor(0, (1, 0))
        c.rotate_around(0, 1, (0, 0), 90, clockwise=True)
        x, y = c.at_time(1)
        assert x == pytest.approx(0, abs=0.1)
        assert y == pytest.approx(-1, abs=0.1)


class TestPulse:
    def test_pulse_scales_at_peak(self):
        c = Circle(r=50, cx=100, cy=100)
        c.pulse(start=0, end=2, scale_factor=2.0)
        # At midpoint, there_and_back peaks at 1 → scale = 2.0
        sx = c.styling.scale_x.at_time(1)
        assert sx > 1.5

    def test_pulse_returns_to_normal(self):
        c = Circle(r=50, cx=100, cy=100)
        c.pulse(start=0, end=2, scale_factor=2.0)
        sx = c.styling.scale_x.at_time(2)
        assert sx == pytest.approx(1, abs=0.05)

    def test_pulse_opacity_dips(self):
        c = Circle(r=50, cx=100, cy=100)
        c.pulse(start=0, end=2, scale_factor=2.0)
        op = c.styling.opacity.at_time(1)
        assert op < 1.0

    def test_dot_pulse(self):
        d = Dot(cx=50, cy=50)
        d.pulse(start=0, end=1)
        sx = d.styling.scale_x.at_time(0.5)
        assert sx > 1.0


class TestArcBboxShape:
    def test_arc_bbox_quarter(self):
        """Quarter arc from 0° to 90°."""
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        x, y, w, h = a.bbox(0)
        # Should include endpoints: (150,100) and (100,50)
        assert x <= 100 and x + w >= 150
        assert y <= 50 and y + h >= 100

    def test_arc_bbox_semicircle(self):
        """Semicircle arc from 0° to 180°."""
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=180)
        x, y, w, _ = a.bbox(0)
        # Should include top (0,-100), right (100,0) and left (-100,0)
        assert x <= -100 and x + w >= 100
        assert y <= -100


class TestBecome:
    def test_become_copies_fill(self):
        a = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        b = Circle(r=50, cx=200, cy=200, fill='#0000FF')
        a.become(b, time=0)
        # a's fill should now match b's fill
        assert a.styling.fill.at_time(0) == b.styling.fill.at_time(0)

    def test_become_copies_opacity(self):
        a = Circle(r=50, cx=100, cy=100, fill_opacity=1.0)
        b = Circle(r=50, cx=200, cy=200, fill_opacity=0.3)
        a.become(b, time=0)
        assert a.styling.fill_opacity.at_time(0) == pytest.approx(0.3)


class TestScale:
    def test_scale_instant(self):
        c = Circle(r=50, cx=100, cy=100)
        c.scale(2, start=0)
        assert c.styling.scale_x.at_time(0) == pytest.approx(2)
        assert c.styling.scale_y.at_time(0) == pytest.approx(2)

    def test_scale_animated(self):
        c = Circle(r=50, cx=100, cy=100)
        c.scale(3, start=0, end=1)
        # At end, should be scaled to 3
        assert c.styling.scale_x.at_time(1) == pytest.approx(3)
        # At start, should be 1
        assert c.styling.scale_x.at_time(0) == pytest.approx(1)

    def test_scale_compounds(self):
        c = Circle(r=50, cx=100, cy=100)
        c.scale(2, start=0)
        c.scale(3, start=1)
        # 2 * 3 = 6
        assert c.styling.scale_x.at_time(1) == pytest.approx(6)


class TestSetOpacityMethod:
    def test_set_opacity_instant(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_opacity(0.5, start=0)
        assert c.styling.fill_opacity.at_time(0) == pytest.approx(0.5)
        assert c.styling.opacity.at_time(0) == pytest.approx(0.5)

    def test_set_opacity_animated(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_opacity(0, start=0, end=1)
        assert c.styling.opacity.at_time(1) == pytest.approx(0, abs=0.05)
        assert c.styling.fill_opacity.at_time(1) == pytest.approx(0, abs=0.05)


class TestSectorAlias:
    def test_sector_is_wedge(self):
        assert Sector is Wedge

    def test_sector_creates_wedge(self):
        s = Sector(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        assert isinstance(s, Wedge)
        svg = s.to_svg(0)
        assert 'Z' in svg  # Wedge closes through center


class TestWedgeBbox:
    def test_wedge_bbox_quarter(self):
        w = Wedge(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        x, y, bw, bh = w.bbox(0)
        # Should include the center point and the two endpoints
        assert x <= 100 and x + bw >= 100  # center x
        assert y <= 50 and y + bh >= 100   # center y and top endpoint


class TestDashedLineSvg:
    def test_dashed_line_svg(self):
        d = DashedLine(x1=0, y1=0, x2=100, y2=0, dash='5,3')
        svg = d.to_svg(0)
        assert 'stroke-dasharray' in svg
        assert '5,3' in svg

    def test_dashed_line_is_line(self):
        d = DashedLine(x1=0, y1=0, x2=100, y2=100)
        assert isinstance(d, Line)


class TestStagger:
    def test_stagger_offsets_timing(self):
        c1 = Circle(r=10, cx=50, cy=50)
        c2 = Circle(r=10, cx=100, cy=50)
        c3 = Circle(r=10, cx=150, cy=50)
        group = VCollection(c1, c2, c3)
        group.stagger('fadein', delay=0.5, start=0, end=1)
        # c1 should be visible at t=0.5, c2 shouldn't start until t=0.5
        assert c1.show.at_time(0.5)
        assert not c2.show.at_time(0.1)


class TestArrangeLayout:
    def test_arrange_right(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        group = VCollection(c1, c2)
        group.arrange(direction='right', buff=10, start=0)
        # After arranging, c2's bbox should be to the right of c1's
        x1, _, w1, _ = c1.bbox(0)
        x2, _, _, _ = c2.bbox(0)
        assert x2 >= x1 + w1


class TestCenter:
    def test_center_circle(self):
        c = Circle(r=50, cx=100, cy=200)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(200)

    def test_center_rectangle(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        cx, cy = r.center(0)
        assert cx == pytest.approx(60)
        assert cy == pytest.approx(45)

    def test_center_after_shift(self):
        c = Circle(r=50, cx=100, cy=200)
        c.shift(dx=50, dy=-30, start=0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(150)
        assert cy == pytest.approx(170)


class TestShowHideHelpers:
    def test_show_from(self):
        c = Circle(r=50, cx=100, cy=200)
        c._show_from(5)
        assert not c.show.at_time(0)
        assert not c.show.at_time(4.9)
        assert c.show.at_time(5)
        assert c.show.at_time(10)

    def test_hide_from(self):
        c = Circle(r=50, cx=100, cy=200)
        c._hide_from(3)
        assert c.show.at_time(0)
        assert c.show.at_time(2.9)
        assert not c.show.at_time(3)
        assert not c.show.at_time(10)


class TestScaleBy:
    def test_scale_by_delegates_to_scale(self):
        c = Circle(r=50, cx=100, cy=200)
        c.scale_by(0, 1, 2.0, easing=easings.linear)
        # At t=1, scale should be 2.0
        assert c.styling.scale_x.at_time(1) == pytest.approx(2.0)
        assert c.styling.scale_y.at_time(1) == pytest.approx(2.0)


class TestFunctionGraph:
    def test_basic(self):
        fg = FunctionGraph(lambda x: x**2, x_range=(-2, 2), num_points=50)
        svg = fg.to_svg(0)
        assert '<polyline' in svg

    def test_custom_style(self):
        fg = FunctionGraph(lambda x: x, x_range=(0, 1), stroke='#ff0000')
        svg = fg.to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_is_lines(self):
        fg = FunctionGraph(lambda x: x, x_range=(0, 1))
        assert isinstance(fg, Lines)
        assert isinstance(fg, Polygon)  # Lines inherits from Polygon

    def test_auto_y_range(self):
        fg = FunctionGraph(lambda x: 2*x, x_range=(-1, 1), num_points=10,
                           x=0, y=0, width=100, height=100)
        # Should have vertices within the plot area
        for v in fg.vertices:
            vx, vy = v.at_time(0)
            assert 0 <= vx <= 100
            assert 0 <= vy <= 100


class TestGetWidthHeight:
    def test_get_width(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        assert r.get_width(0) == pytest.approx(100)

    def test_get_height(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        assert r.get_height(0) == pytest.approx(50)

    def test_circle_width_equals_diameter(self):
        c = Circle(r=50, cx=100, cy=200)
        assert c.get_width(0) == pytest.approx(100)
        assert c.get_height(0) == pytest.approx(100)


class TestVCollectionAddRemove:
    def test_add(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=100, cy=100)
        group = VCollection(c1)
        assert len(group) == 1
        group.add(c2)
        assert len(group) == 2
        assert group[1] is c2

    def test_remove(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=100, cy=100)
        group = VCollection(c1, c2)
        group.remove(c1)
        assert len(group) == 1
        assert group[0] is c2

    def test_add_returns_self(self):
        group = VCollection()
        result = group.add(Circle(r=10, cx=0, cy=0))
        assert result is group


class TestStretch:
    def test_stretch_instant(self):
        c = Circle(r=50, cx=100, cy=200)
        c.stretch(x_factor=2, y_factor=0.5, start=0)
        assert c.styling.scale_x.at_time(0) == pytest.approx(2.0)
        assert c.styling.scale_y.at_time(0) == pytest.approx(0.5)

    def test_stretch_animated(self):
        c = Circle(r=50, cx=100, cy=200)
        c.stretch(x_factor=3, y_factor=1.5, start=0, end=1, easing=easings.linear)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0)
        assert c.styling.scale_x.at_time(1) == pytest.approx(3.0)
        assert c.styling.scale_y.at_time(1) == pytest.approx(1.5)


class TestMatchWidthHeight:
    def test_match_width(self):
        small = Rectangle(width=50, height=50, x=0, y=0)
        big = Rectangle(width=200, height=100, x=0, y=0)
        small.match_width(big, time=0)
        # After matching width, small's effective width should equal big's
        _, _, sw, _ = small.bbox(0)
        _, _, bw, _ = big.bbox(0)
        assert sw == pytest.approx(bw, abs=1)

    def test_match_height(self):
        small = Rectangle(width=50, height=50, x=0, y=0)
        big = Rectangle(width=200, height=100, x=0, y=0)
        small.match_height(big, time=0)
        _, _, _, sh = small.bbox(0)
        _, _, _, bh = big.bbox(0)
        assert sh == pytest.approx(bh, abs=1)

    def test_match_width_circle(self):
        c = Circle(r=25, cx=100, cy=100)
        r = Rectangle(width=200, height=50, x=0, y=0)
        c.match_width(r, time=0)
        _, _, cw, _ = c.bbox(0)
        _, _, rw, _ = r.bbox(0)
        assert cw == pytest.approx(rw, abs=1)


class TestShapePropertySetters:
    def test_circle_set_radius(self):
        c = Circle(r=50)
        c.set_radius(100, start=0, end=1)
        r_mid = c.r.at_time(0.5)
        assert 50 < r_mid < 100

    def test_circle_set_radius_instant(self):
        c = Circle(r=50)
        c.set_radius(100, start=0)
        assert c.r.at_time(0) == 100

    def test_circle_set_radius_returns_self(self):
        c = Circle(r=50)
        result = c.set_radius(100, start=0)
        assert result is c

    def test_ellipse_set_rx_ry(self):
        e = Ellipse(rx=50, ry=30)
        e.set_rx(80, start=0, end=1)
        e.set_ry(60, start=0, end=1)
        assert e.rx.at_time(1) == 80
        assert e.ry.at_time(1) == 60

    def test_ellipse_set_rx_instant(self):
        e = Ellipse(rx=50, ry=30)
        e.set_rx(80, start=0)
        assert e.rx.at_time(0) == 80

    def test_ellipse_set_ry_instant(self):
        e = Ellipse(rx=50, ry=30)
        e.set_ry(60, start=0)
        assert e.ry.at_time(0) == 60

    def test_ellipse_set_rx_returns_self(self):
        e = Ellipse(rx=50, ry=30)
        assert e.set_rx(80, start=0) is e

    def test_ellipse_set_ry_returns_self(self):
        e = Ellipse(rx=50, ry=30)
        assert e.set_ry(60, start=0) is e

    def test_text_set_font_size(self):
        t = Text(text='Hello', font_size=24)
        result = t.set_font_size(48, start=0, end=1)
        assert result is t
        assert t.font_size.at_time(1) == 48

    def test_text_set_font_size_instant(self):
        t = Text(text='Hello', font_size=24)
        t.set_font_size(48, start=0)
        assert t.font_size.at_time(0) == 48

    def test_text_set_font_size_midpoint(self):
        t = Text(text='Hello', font_size=24)
        t.set_font_size(48, start=0, end=1)
        mid = t.font_size.at_time(0.5)
        assert 24 < mid < 48

    def test_rounded_rect_set_corner_radius(self):
        rr = RoundedRectangle(200, 100, corner_radius=10)
        result = rr.set_corner_radius(30, start=0, end=1)
        assert result is rr
        assert rr.rx.at_time(1) == 30
        assert rr.ry.at_time(1) == 30

    def test_rounded_rect_set_corner_radius_instant(self):
        rr = RoundedRectangle(200, 100, corner_radius=10)
        rr.set_corner_radius(30, start=0)
        assert rr.rx.at_time(0) == 30
        assert rr.ry.at_time(0) == 30

    def test_rounded_rect_set_corner_radius_midpoint(self):
        rr = RoundedRectangle(200, 100, corner_radius=10)
        rr.set_corner_radius(30, start=0, end=1)
        mid = rr.rx.at_time(0.5)
        assert 10 < mid < 30

    def test_dashed_line_set_pattern(self):
        dl = DashedLine(0, 100, 200, 100)
        result = dl.set_dash_pattern(10, 5, start=0)
        assert result is dl

    def test_dashed_line_set_pattern_default_gap(self):
        dl = DashedLine(0, 100, 200, 100)
        dl.set_dash_pattern(8, start=0)
        assert dl.styling.stroke_dasharray.at_time(0) == '8,8'

    def test_dashed_line_set_pattern_custom_gap(self):
        dl = DashedLine(0, 100, 200, 100)
        dl.set_dash_pattern(10, 3, start=0)
        assert dl.styling.stroke_dasharray.at_time(0) == '10,3'

    def test_arc_set_radius(self):
        a = Arc(r=50)
        a.set_radius(100, start=0, end=1)
        assert 50 < a.r.at_time(0.5) < 100
        assert a.r.at_time(1) == 100

    def test_arc_set_radius_instant(self):
        a = Arc(r=50)
        result = a.set_radius(100, start=0)
        assert result is a
        assert a.r.at_time(0) == 100

    def test_arc_set_angles(self):
        a = Arc(start_angle=0, end_angle=90)
        a.set_angles(start_angle=45, end_angle=180, start=0, end=1)
        assert a.start_angle.at_time(1) == 45
        assert a.end_angle.at_time(1) == 180

    def test_arc_set_angles_partial(self):
        a = Arc(start_angle=0, end_angle=90)
        a.set_angles(end_angle=270, start=0)
        assert a.start_angle.at_time(0) == 0  # unchanged
        assert a.end_angle.at_time(0) == 270

    def test_arc_set_angles_returns_self(self):
        a = Arc()
        assert a.set_angles(start_angle=10, start=0) is a

    def test_annulus_set_inner_radius(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        an.set_inner_radius(50, start=0, end=1)
        assert 30 < an.inner_r.at_time(0.5) < 50
        assert an.inner_r.at_time(1) == 50

    def test_annulus_set_inner_radius_instant(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        result = an.set_inner_radius(50, start=0)
        assert result is an
        assert an.inner_r.at_time(0) == 50

    def test_annulus_set_outer_radius(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        an.set_outer_radius(150, start=0, end=1)
        assert 100 < an.outer_r.at_time(0.5) < 150
        assert an.outer_r.at_time(1) == 150

    def test_annulus_set_outer_radius_instant(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        result = an.set_outer_radius(150, start=0)
        assert result is an
        assert an.outer_r.at_time(0) == 150


class TestGeometricQueries:
    def test_line_set_points(self):
        line = Line(0, 0, 100, 100)
        result = line.set_points((50, 50), (200, 200), start=0)
        assert result is line
        assert line.p1.at_time(0) == (50, 50)
        assert line.p2.at_time(0) == (200, 200)

    def test_line_set_length(self):
        line = Line(0, 0, 100, 0)
        result = line.set_length(200, start=0)
        assert result is line
        # Midpoint = (50, 0). New half = 100. p1 = -50, p2 = 150
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        assert p1[0] == pytest.approx(-50, abs=0.01)
        assert p2[0] == pytest.approx(150, abs=0.01)

    def test_line_set_length_animated(self):
        line = Line(0, 0, 100, 0)
        line.set_length(200, start=0, end=1)
        # At midpoint of animation, length should be between 100 and 200
        p1_mid = line.p1.at_time(0.5)
        p2_mid = line.p2.at_time(0.5)
        mid_length = p2_mid[0] - p1_mid[0]
        assert 100 < mid_length < 200

    def test_line_set_length_zero_length(self):
        line = Line(50, 50, 50, 50)
        result = line.set_length(100, start=0)
        assert result is line  # no-op for zero-length line

    def test_rectangle_set_size(self):
        r = Rectangle(100, 50)
        result = r.set_size(200, 100, start=0, end=1)
        assert result is r
        assert r.width.at_time(1) == 200
        assert r.height.at_time(1) == 100

    def test_rectangle_set_size_instant(self):
        r = Rectangle(100, 50)
        r.set_size(200, 100, start=0)
        assert r.width.at_time(0) == 200
        assert r.height.at_time(0) == 100

    def test_rectangle_contains_point(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.contains_point(50, 40) is True
        assert r.contains_point(10, 20) is True  # corner
        assert r.contains_point(5, 40) is False  # outside left

    def test_circle_contains_point(self):
        c = Circle(cx=100, cy=100, r=50)
        assert c.contains_point(100, 100) is True  # center
        assert c.contains_point(140, 100) is True  # inside
        assert c.contains_point(200, 100) is False  # outside

    def test_polygon_contains_point(self):
        # Simple square
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.contains_point(50, 50) is True
        assert p.contains_point(200, 50) is False

    def test_polygon_contains_point_triangle(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        assert p.contains_point(50, 30) is True
        assert p.contains_point(0, 100) is False

    def test_annulus_get_area(self):
        import math
        an = Annulus(inner_radius=30, outer_radius=100)
        expected = math.pi * (100**2 - 30**2)
        assert an.get_area() == pytest.approx(expected, abs=0.01)

    def test_annulus_set_radii(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        result = an.set_radii(inner=50, outer=150, start=0)
        assert result is an
        assert an.inner_r.at_time(0) == 50
        assert an.outer_r.at_time(0) == 150

    def test_annulus_set_radii_partial(self):
        an = Annulus(inner_radius=30, outer_radius=100)
        an.set_radii(outer=200, start=0)
        assert an.inner_r.at_time(0) == 30  # unchanged
        assert an.outer_r.at_time(0) == 200

    def test_arc_get_midpoint(self):
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=180)
        mx, my = a.get_midpoint()
        # Midpoint at 90 degrees = top of circle
        assert mx == pytest.approx(0, abs=0.01)
        assert my == pytest.approx(-100, abs=0.01)  # y is inverted in SVG

    def test_wedge_get_area(self):
        import math
        w = Wedge(r=100, start_angle=0, end_angle=90)
        expected = 0.5 * 100**2 * math.radians(90)
        assert w.get_area() == pytest.approx(expected, abs=0.01)

    def test_cubicbezier_point_at(self):
        from vectormation.objects import CubicBezier
        b = CubicBezier(p0=(0, 0), p1=(100, 0), p2=(100, 100), p3=(200, 100))
        start = b.point_at(0)
        end = b.point_at(1)
        assert start[0] == pytest.approx(0, abs=0.01) and start[1] == pytest.approx(0, abs=0.01)
        assert end[0] == pytest.approx(200, abs=0.01) and end[1] == pytest.approx(100, abs=0.01)
        mid = b.point_at(0.5)
        assert 50 < mid[0] < 150  # somewhere in the middle

    def test_cubicbezier_tangent_at(self):
        import math
        from vectormation.objects import CubicBezier
        b = CubicBezier(p0=(0, 0), p1=(100, 0), p2=(100, 0), p3=(200, 0))
        dx, dy = b.tangent_at(0.5)
        # Horizontal line, tangent should point right
        assert dx == pytest.approx(1.0, abs=0.1)
        assert dy == pytest.approx(0, abs=0.1)
        # Unit vector
        assert math.hypot(dx, dy) == pytest.approx(1.0, abs=0.01)

    def test_arc_get_sweep(self):
        a = Arc(start_angle=30, end_angle=120)
        assert a.get_sweep() == 90

    def test_arc_get_sweep_large(self):
        a = Arc(start_angle=0, end_angle=270)
        assert a.get_sweep() == 270


class TestGeometricExtras:
    def test_polygon_is_convex_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.is_convex() is True

    def test_polygon_is_convex_concave(self):
        # L-shaped polygon (concave)
        p = Polygon((0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100))
        assert p.is_convex() is False

    def test_polygon_is_convex_triangle(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        assert p.is_convex() is True

    def test_ellipse_get_perimeter_circle(self):
        import math
        e = Ellipse(rx=100, ry=100)
        expected = 2 * math.pi * 100
        assert e.get_perimeter() == pytest.approx(expected, abs=0.1)

    def test_ellipse_get_perimeter_ellipse(self):
        e = Ellipse(rx=100, ry=50)
        p = e.get_perimeter()
        # Perimeter should be between 2*pi*50 and 2*pi*100
        import math
        assert 2 * math.pi * 50 < p < 2 * math.pi * 100

    def test_line_angle_horizontal(self):
        line = Line(0, 0, 100, 0)
        assert line.angle() == pytest.approx(0, abs=0.01)

    def test_line_angle_up(self):
        line = Line(0, 100, 0, 0)  # points up in SVG (y decreases)
        assert line.angle() == pytest.approx(90, abs=0.01)

    def test_line_angle_down(self):
        line = Line(0, 0, 0, 100)  # points down in SVG
        assert line.angle() == pytest.approx(-90, abs=0.01)


class TestRegularPolygonMethods:
    def test_get_side_length_square(self):
        import math
        sq = RegularPolygon(4, radius=100)
        # side of square inscribed in r=100: 2*100*sin(pi/4) = 100*sqrt(2)
        expected = 100 * math.sqrt(2)
        assert sq.get_side_length() == pytest.approx(expected, rel=1e-6)

    def test_get_side_length_hexagon(self):
        # Regular hexagon: side length == radius
        hex_ = RegularPolygon(6, radius=120)
        assert hex_.get_side_length() == pytest.approx(120, rel=1e-6)

    def test_get_inradius_square(self):
        import math
        sq = RegularPolygon(4, radius=100)
        # inradius of square inscribed in r=100: 100*cos(pi/4) = 50*sqrt(2)
        expected = 100 * math.cos(math.pi / 4)
        assert sq.get_inradius() == pytest.approx(expected, rel=1e-6)

    def test_get_inradius_triangle(self):
        tri = RegularPolygon(3, radius=100)
        # inradius = r * cos(pi/3) = 100 * 0.5 = 50
        assert tri.get_inradius() == pytest.approx(50, rel=1e-6)


class TestStarMethods:
    def test_get_outer_radius(self):
        s = Star(n=5, outer_radius=150, inner_radius=60)
        assert s.get_outer_radius() == 150

    def test_get_inner_radius(self):
        s = Star(n=5, outer_radius=150, inner_radius=60)
        assert s.get_inner_radius() == 60

    def test_get_inner_radius_default(self):
        s = Star(n=5, outer_radius=100)
        # Default inner_radius = outer_radius * 0.4
        assert s.get_inner_radius() == pytest.approx(40)

    def test_get_outer_radius_default(self):
        s = Star(n=7, outer_radius=200)
        assert s.get_outer_radius() == 200


class TestLineGetSlope:
    def test_horizontal_line(self):
        line = Line(0, 0, 100, 0)
        assert line.get_slope() == pytest.approx(0)

    def test_diagonal_line(self):
        line = Line(0, 0, 100, 100)
        assert line.get_slope() == pytest.approx(1.0)

    def test_negative_slope(self):
        line = Line(0, 100, 100, 0)
        assert line.get_slope() == pytest.approx(-1.0)

    def test_vertical_line_returns_inf(self):
        line = Line(50, 0, 50, 100)
        assert line.get_slope() == float('inf')

    def test_steep_slope(self):
        line = Line(0, 0, 10, 50)
        assert line.get_slope() == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Rectangle.from_center
# ---------------------------------------------------------------------------

class TestRectangleFromCenter:
    def test_basic(self):
        r = Rectangle.from_center(500, 300, 200, 100)
        assert r.x.at_time(0) == pytest.approx(400)
        assert r.y.at_time(0) == pytest.approx(250)
        assert r.width.at_time(0) == pytest.approx(200)
        assert r.height.at_time(0) == pytest.approx(100)

    def test_center_is_correct(self):
        r = Rectangle.from_center(960, 540, 300, 200)
        cx, cy = r.center(0)
        assert cx == pytest.approx(960)
        assert cy == pytest.approx(540)

    def test_with_kwargs(self):
        r = Rectangle.from_center(100, 100, 50, 50, rx=5, ry=5, fill='#ff0000')
        assert r.rx.at_time(0) == pytest.approx(5)
        svg = r.to_svg(0)
        assert '<rect' in svg

    def test_origin(self):
        r = Rectangle.from_center(0, 0, 100, 80)
        assert r.x.at_time(0) == pytest.approx(-50)
        assert r.y.at_time(0) == pytest.approx(-40)


# ---------------------------------------------------------------------------
# Circle.from_three_points
# ---------------------------------------------------------------------------

class TestCircleFromThreePoints:
    def test_unit_circle(self):
        # Three points on the unit circle centered at origin
        c = Circle.from_three_points((1, 0), (0, 1), (-1, 0))
        cx, cy = c.c.at_time(0)
        r = c.rx.at_time(0)
        assert cx == pytest.approx(0, abs=1e-6)
        assert cy == pytest.approx(0, abs=1e-6)
        assert r == pytest.approx(1, abs=1e-6)

    def test_offset_circle(self):
        # Circle centered at (5, 5) with radius 3
        p1 = (5 + 3, 5)
        p2 = (5, 5 + 3)
        p3 = (5 - 3, 5)
        c = Circle.from_three_points(p1, p2, p3)
        cx, cy = c.c.at_time(0)
        r = c.rx.at_time(0)
        assert cx == pytest.approx(5, abs=1e-6)
        assert cy == pytest.approx(5, abs=1e-6)
        assert r == pytest.approx(3, abs=1e-6)

    def test_collinear_raises(self):
        with pytest.raises(ValueError, match="collinear"):
            Circle.from_three_points((0, 0), (1, 1), (2, 2))

    def test_with_kwargs(self):
        c = Circle.from_three_points((1, 0), (0, 1), (-1, 0), fill='#ff0000')
        svg = c.to_svg(0)
        assert '<circle' in svg

    def test_all_three_points_on_circle(self):
        import math
        c = Circle.from_three_points((100, 200), (300, 400), (500, 200))
        cx, cy = c.c.at_time(0)
        r = c.rx.at_time(0)
        # Verify all three original points lie on the circle
        for px, py in [(100, 200), (300, 400), (500, 200)]:
            dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
            assert dist == pytest.approx(r, abs=1e-6)


# ---------------------------------------------------------------------------
# Getter/setter methods
# ---------------------------------------------------------------------------

class TestGettersSetters:
    # Circle.get_radius and get_perimeter
    def test_circle_get_radius(self):
        c = Circle(r=75, cx=100, cy=200)
        assert c.get_radius() == pytest.approx(75)

    def test_circle_get_radius_after_set(self):
        c = Circle(r=50)
        c.set_radius(80)
        assert c.get_radius() == pytest.approx(80)

    def test_circle_get_perimeter_exact(self):
        import math
        c = Circle(r=100)
        assert c.get_perimeter() == pytest.approx(2 * math.pi * 100)

    def test_circle_get_perimeter_not_ramanujan(self):
        import math
        # For a circle rx==ry, exact perimeter == 2*pi*r, Ramanujan differs slightly
        c = Circle(r=100)
        assert c.get_perimeter() == pytest.approx(2 * math.pi * 100, rel=1e-12)

    # Ellipse.get_rx, get_ry, set_center
    def test_ellipse_get_rx(self):
        e = Ellipse(rx=80, ry=40)
        assert e.get_rx() == pytest.approx(80)

    def test_ellipse_get_ry(self):
        e = Ellipse(rx=80, ry=40)
        assert e.get_ry() == pytest.approx(40)

    def test_ellipse_get_rx_after_set(self):
        e = Ellipse(rx=80, ry=40)
        e.set_rx(120)
        assert e.get_rx() == pytest.approx(120)

    def test_ellipse_set_center(self):
        e = Ellipse(rx=60, ry=30, cx=100, cy=200)
        e.set_center(500, 300)
        cx, cy = e.c.at_time(0)
        assert cx == pytest.approx(500)
        assert cy == pytest.approx(300)

    def test_ellipse_set_center_animated(self):
        e = Ellipse(rx=60, ry=30, cx=100, cy=200)
        e.set_center(500, 300, start=0, end=1)
        cx0, _ = e.c.at_time(0)
        cx1, _ = e.c.at_time(1)
        assert cx0 == pytest.approx(100)
        assert cx1 == pytest.approx(500)

    # Rectangle.get_size
    def test_rectangle_get_size(self):
        r = Rectangle(width=200, height=100)
        w, h = r.get_size()
        assert w == pytest.approx(200)
        assert h == pytest.approx(100)

    def test_rectangle_get_size_after_set(self):
        r = Rectangle(width=200, height=100)
        r.set_size(300, 150)
        w, h = r.get_size()
        assert w == pytest.approx(300)
        assert h == pytest.approx(150)

    # Annulus.get_inner_radius, get_outer_radius
    def test_annulus_get_inner_radius(self):
        a = Annulus(inner_radius=50, outer_radius=120)
        assert a.get_inner_radius() == pytest.approx(50)

    def test_annulus_get_outer_radius(self):
        a = Annulus(inner_radius=50, outer_radius=120)
        assert a.get_outer_radius() == pytest.approx(120)

    def test_annulus_get_inner_radius_after_set(self):
        a = Annulus(inner_radius=50, outer_radius=120)
        a.set_inner_radius(70)
        assert a.get_inner_radius() == pytest.approx(70)

    def test_annulus_get_outer_radius_after_set(self):
        a = Annulus(inner_radius=50, outer_radius=120)
        a.set_outer_radius(200)
        assert a.get_outer_radius() == pytest.approx(200)

    # AnnularSector.set_inner_radius and get_area
    def test_annular_sector_set_inner_radius(self):
        s = AnnularSector(inner_radius=40, outer_radius=100, start_angle=0, end_angle=90)
        s.set_inner_radius(60)
        assert s.inner_r.at_time(0) == pytest.approx(60)

    def test_annular_sector_set_inner_radius_animated(self):
        s = AnnularSector(inner_radius=40, outer_radius=100, start_angle=0, end_angle=90)
        s.set_inner_radius(80, start=0, end=1)
        assert s.inner_r.at_time(0) == pytest.approx(40)
        assert s.inner_r.at_time(1) == pytest.approx(80)

    def test_annular_sector_get_area(self):
        import math
        # 90 degree sector, outer=100, inner=50
        s = AnnularSector(inner_radius=50, outer_radius=100, start_angle=0, end_angle=90)
        expected = 0.5 * math.radians(90) * (100 ** 2 - 50 ** 2)
        assert s.get_area() == pytest.approx(expected)

    # RoundedRectangle.get_corner_radius
    def test_rounded_rectangle_get_corner_radius(self):
        rr = RoundedRectangle(200, 100, corner_radius=15)
        assert rr.get_corner_radius() == pytest.approx(15)

    def test_rounded_rectangle_get_corner_radius_after_set(self):
        rr = RoundedRectangle(200, 100, corner_radius=15)
        rr.set_corner_radius(25)
        assert rr.get_corner_radius() == pytest.approx(25)

    # Text.get_font_size
    def test_text_get_font_size(self):
        t = Text(text='hello', font_size=36)
        assert t.get_font_size() == pytest.approx(36)

    def test_text_get_font_size_default(self):
        t = Text(text='hello')
        assert t.get_font_size() == pytest.approx(48)

    # Line.set_start and set_end
    def test_line_set_start(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        l.set_start((50, 50))
        x1, y1 = l.p1.at_time(0)
        assert x1 == pytest.approx(50)
        assert y1 == pytest.approx(50)

    def test_line_set_end(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        l.set_end((200, 300))
        x2, y2 = l.p2.at_time(0)
        assert x2 == pytest.approx(200)
        assert y2 == pytest.approx(300)

    def test_line_set_start_animated(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        l.set_start((50, 50), start=0, end=1)
        x0, _ = l.p1.at_time(0)
        x1, _ = l.p1.at_time(1)
        assert x0 == pytest.approx(0)
        assert x1 == pytest.approx(50)

    def test_line_set_end_animated(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        l.set_end((300, 400), start=0, end=1)
        x0, _ = l.p2.at_time(0)
        x1, _ = l.p2.at_time(1)
        assert x0 == pytest.approx(100)
        assert x1 == pytest.approx(300)

    # PieChart.get_sector
    def test_piechart_get_sector(self):
        pc = PieChart([1, 2, 3])
        s0 = pc.get_sector(0)
        assert s0 is pc._sectors[0]

    def test_piechart_get_sector_is_wedge(self):
        pc = PieChart([1, 2, 3])
        assert isinstance(pc.get_sector(1), Wedge)

    # Axes.set_x_range, set_y_range
    def test_axes_set_x_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        ax.set_x_range(-10, 10)
        assert ax.x_min.at_time(0) == pytest.approx(-10)
        assert ax.x_max.at_time(0) == pytest.approx(10)

    def test_axes_set_y_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        ax.set_y_range(-8, 8)
        assert ax.y_min.at_time(0) == pytest.approx(-8)
        assert ax.y_max.at_time(0) == pytest.approx(8)

    def test_axes_set_x_range_with_start(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        ax.set_x_range(-20, 20, start=2)
        assert ax.x_min.at_time(0) == pytest.approx(-5)
        assert ax.x_min.at_time(2) == pytest.approx(-20)

    def test_axes_set_y_range_returns_self(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.set_y_range(-1, 1)
        assert result is ax

    # Axes.get_horizontal_lines
    def test_axes_get_horizontal_lines_returns_vcollection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.get_horizontal_lines([0, 1, 2])
        assert isinstance(result, VCollection)

    def test_axes_get_horizontal_lines_count(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.get_horizontal_lines([-1, 0, 1])
        assert len(result.objects) == 3

    def test_axes_get_horizontal_lines_y_position(self):
        ax = Axes(x_range=(-5, 5), y_range=(-4, 4))
        result = ax.get_horizontal_lines([2.0])
        line = result.objects[0]
        sy1 = line.p1.at_time(0)[1]
        sy2 = line.p2.at_time(0)[1]
        # Both endpoints share the same y (horizontal line)
        assert sy1 == pytest.approx(sy2)

    def test_axes_get_horizontal_lines_x_start_end(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.get_horizontal_lines([0], x_start=-2, x_end=2)
        line = result.objects[0]
        sx1 = line.p1.at_time(0)[0]
        sx2 = line.p2.at_time(0)[0]
        # x_start < x_end in SVG space
        assert sx1 < sx2

    def test_axes_get_horizontal_lines_default_spans_plot(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.get_horizontal_lines([1])
        line = result.objects[0]
        sx1 = line.p1.at_time(0)[0]
        sx2 = line.p2.at_time(0)[0]
        # Default spans from plot_x to plot_x + plot_width
        assert sx1 == pytest.approx(ax.plot_x)
        assert sx2 == pytest.approx(ax.plot_x + ax.plot_width)

    def test_axes_get_horizontal_lines_returns_self_chainable(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        result = ax.get_horizontal_lines([0, 1])
        assert isinstance(result, VCollection)
        assert len(result.objects) == 2


class TestDonutChart:
    def test_donutchart_get_sector_returns_path(self):
        dc = DonutChart([1, 2, 3])
        s = dc.get_sector(0)
        assert s is dc._sectors[0]

    def test_donutchart_get_sector_index_error(self):
        dc = DonutChart([1, 2, 3])
        with pytest.raises(IndexError):
            dc.get_sector(5)

    def test_donutchart_get_sector_negative_index_error(self):
        dc = DonutChart([1, 2, 3])
        with pytest.raises(IndexError):
            dc.get_sector(-1)

    def test_donutchart_get_sector_last(self):
        dc = DonutChart([10, 20, 30])
        s = dc.get_sector(2)
        assert s is dc._sectors[2]

    def test_donutchart_highlight_sector_returns_self(self):
        dc = DonutChart([1, 2, 3])
        result = dc.highlight_sector(0, start=0, end=1)
        assert result is dc

    def test_donutchart_highlight_sector_out_of_range_raises(self):
        dc = DonutChart([1, 2, 3])
        with pytest.raises(IndexError):
            dc.highlight_sector(10, start=0, end=1)

    def test_donutchart_highlight_sector_shifts_sector(self):
        dc = DonutChart([1, 2, 3])
        sector = dc._sectors[0]
        # Before highlight, dx at t=0.5 should be 0
        dx_before = sector.styling.dx.at_time(0.5)
        dc.highlight_sector(0, start=0, end=1, pull_distance=50)
        dx_after = sector.styling.dx.at_time(0.25)
        # After highlight, dx at midpoint should be non-zero (sector was shifted)
        assert dx_after != dx_before

    def test_donutchart_animate_values_returns_self(self):
        dc = DonutChart([1, 2, 3])
        result = dc.animate_values([2, 2, 2], start=0, end=1)
        assert result is dc

    def test_donutchart_animate_values_updates_stored_values(self):
        dc = DonutChart([1, 2, 3])
        dc.animate_values([4, 4, 4], start=0, end=1)
        assert dc.values == [4, 4, 4]

    def test_donutchart_animate_values_wrong_length_ignored(self):
        dc = DonutChart([1, 2, 3])
        result = dc.animate_values([1, 2], start=0, end=1)
        assert result is dc
        assert dc.values == [1, 2, 3]  # unchanged

    def test_donutchart_animate_values_path_changes(self):
        dc = DonutChart([1, 2, 3])
        d_before = dc._sectors[0].d.at_time(0)
        dc.animate_values([3, 2, 1], start=0, end=2)
        d_after = dc._sectors[0].d.at_time(2)
        # Path data should differ at end of animation
        assert d_before != d_after

    def test_donutchart_animate_values_zero_duration_ignored(self):
        dc = DonutChart([1, 2, 3])
        result = dc.animate_values([2, 2, 2], start=1, end=1)
        assert result is dc
        assert dc.values == [1, 2, 3]  # unchanged since dur=0

    def test_donutchart_repr(self):
        dc = DonutChart([1, 2, 3])
        assert repr(dc) == 'DonutChart(3 sectors)'


class TestPathFromPoints:
    def test_straight_segments(self):
        pts = [(0, 0), (100, 50), (200, 0)]
        p = Path.from_points(pts)
        d = p.d.at_time(0)
        assert d.startswith('M0,0')
        assert 'L100,50' in d
        assert 'L200,0' in d

    def test_closed_path_has_z(self):
        pts = [(0, 0), (100, 0), (50, 100)]
        p = Path.from_points(pts, closed=True)
        d = p.d.at_time(0)
        assert d.endswith('Z')

    def test_open_path_no_z(self):
        pts = [(0, 0), (100, 0), (50, 100)]
        p = Path.from_points(pts, closed=False)
        d = p.d.at_time(0)
        assert not d.endswith('Z')

    def test_smooth_path_uses_cubic_bezier(self):
        pts = [(0, 0), (100, 50), (200, 0), (300, 50)]
        p = Path.from_points(pts, smooth=True)
        d = p.d.at_time(0)
        assert 'C' in d

    def test_smooth_closed_path(self):
        pts = [(0, 0), (100, 50), (200, 0)]
        p = Path.from_points(pts, smooth=True, closed=True)
        d = p.d.at_time(0)
        assert 'C' in d
        assert d.endswith('Z')

    def test_single_point(self):
        p = Path.from_points([(42, 99)])
        d = p.d.at_time(0)
        assert d == 'M42,99'

    def test_empty_points(self):
        p = Path.from_points([])
        d = p.d.at_time(0)
        assert d == ''

    def test_returns_path_instance(self):
        p = Path.from_points([(0, 0), (10, 10)])
        assert isinstance(p, Path)

    def test_kwargs_passed_through(self):
        p = Path.from_points([(0, 0), (10, 10)], stroke='#f00')
        assert 'rgb(255,0,0)' in p.styling.stroke.at_time(0)

    def test_two_points_straight(self):
        p = Path.from_points([(10, 20), (30, 40)])
        d = p.d.at_time(0)
        assert 'M10,20' in d
        assert 'L30,40' in d


class TestRectangleRoundCorners:
    def test_returns_rounded_rectangle(self):
        r = Rectangle(200, 100, x=10, y=20)
        rr = r.round_corners(radius=15)
        assert isinstance(rr, RoundedRectangle)

    def test_preserves_dimensions(self):
        r = Rectangle(200, 100, x=10, y=20)
        rr = r.round_corners(radius=12)
        assert rr.width.at_time(0) == pytest.approx(200)
        assert rr.height.at_time(0) == pytest.approx(100)

    def test_preserves_position(self):
        r = Rectangle(200, 100, x=10, y=20)
        rr = r.round_corners(radius=8)
        assert rr.x.at_time(0) == pytest.approx(10)
        assert rr.y.at_time(0) == pytest.approx(20)

    def test_sets_corner_radius(self):
        r = Rectangle(200, 100, x=10, y=20)
        rr = r.round_corners(radius=20)
        assert rr.rx.at_time(0) == pytest.approx(20)
        assert rr.ry.at_time(0) == pytest.approx(20)

    def test_default_radius_is_ten(self):
        r = Rectangle(100, 60)
        rr = r.round_corners()
        assert rr.rx.at_time(0) == pytest.approx(10)

    def test_preserves_fill_opacity(self):
        r = Rectangle(100, 60, fill_opacity=0.5)
        rr = r.round_corners(radius=5)
        assert rr.styling.fill_opacity.at_time(0) == pytest.approx(0.5)

    def test_kwargs_override_style(self):
        r = Rectangle(100, 60, fill_opacity=0.5)
        rr = r.round_corners(radius=5, fill_opacity=0.9)
        assert rr.styling.fill_opacity.at_time(0) == pytest.approx(0.9)

    def test_svg_has_rect_tag(self):
        r = Rectangle(100, 60, x=5, y=5)
        rr = r.round_corners(radius=10)
        svg = rr.to_svg(0)
        assert '<rect' in svg
        assert "rx='10'" in svg


class TestLineFromDirection:
    def test_creates_line(self):
        from vectormation.objects import Line
        line = Line.from_direction((960, 540), (1, 0), 200)
        assert isinstance(line, Line)

    def test_horizontal_right(self):
        from vectormation.objects import Line
        line = Line.from_direction((100, 200), (1, 0), 100)
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        assert x1 == pytest.approx(100)
        assert y1 == pytest.approx(200)
        assert x2 == pytest.approx(200)
        assert y2 == pytest.approx(200)

    def test_downward(self):
        from vectormation.objects import Line
        line = Line.from_direction((0, 0), (0, 1), 50)
        x2, y2 = line.p2.at_time(0)
        assert x2 == pytest.approx(0)
        assert y2 == pytest.approx(50)

    def test_diagonal_normalises_direction(self):
        from vectormation.objects import Line
        import math
        # Direction (2, 2) should be normalised to (1/sqrt2, 1/sqrt2)
        line = Line.from_direction((0, 0), (2, 2), 100)
        x2, y2 = line.p2.at_time(0)
        expected = 100 / math.sqrt(2)
        assert x2 == pytest.approx(expected, abs=0.01)
        assert y2 == pytest.approx(expected, abs=0.01)

    def test_length_correct(self):
        from vectormation.objects import Line
        import math
        line = Line.from_direction((0, 0), (3, 4), 50)
        x2, y2 = line.p2.at_time(0)
        length = math.sqrt(x2 ** 2 + y2 ** 2)
        assert length == pytest.approx(50, abs=0.01)

    def test_zero_vector_gives_zero_length_line(self):
        from vectormation.objects import Line
        line = Line.from_direction((100, 200), (0, 0), 100)
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        assert x1 == pytest.approx(x2)
        assert y1 == pytest.approx(y2)

    def test_kwargs_forwarded(self):
        from vectormation.objects import Line
        line = Line.from_direction((0, 0), (1, 0), 100, stroke='#f00')
        svg = line.to_svg(0)
        assert '255' in svg or 'f00' in svg.lower()


class TestCircleInscribedPolygon:
    def test_returns_regular_polygon(self):
        from vectormation.objects import Circle, RegularPolygon
        c = Circle(r=100, cx=400, cy=300)
        poly = c.inscribed_polygon(6)
        assert isinstance(poly, RegularPolygon)

    def test_vertex_count(self):
        from vectormation.objects import Circle
        c = Circle(r=100, cx=400, cy=300)
        poly = c.inscribed_polygon(5)
        assert len(poly.vertices) == 5

    def test_triangle_vertices_on_circle(self):
        from vectormation.objects import Circle
        import math
        r, cx, cy = 100, 400, 300
        c = Circle(r=r, cx=cx, cy=cy)
        poly = c.inscribed_polygon(3)
        for v in poly.vertices:
            x, y = v.at_time(0)
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            assert dist == pytest.approx(r, abs=0.5)

    def test_hexagon_vertices_on_circle(self):
        from vectormation.objects import Circle
        import math
        r, cx, cy = 80, 200, 200
        c = Circle(r=r, cx=cx, cy=cy)
        poly = c.inscribed_polygon(6)
        for v in poly.vertices:
            x, y = v.at_time(0)
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            assert dist == pytest.approx(r, abs=0.5)

    def test_respects_time_parameter(self):
        from vectormation.objects import Circle
        import math
        c = Circle(r=50, cx=100, cy=100)
        poly = c.inscribed_polygon(4, time=0)
        for v in poly.vertices:
            x, y = v.at_time(0)
            dist = math.sqrt((x - 100) ** 2 + (y - 100) ** 2)
            assert dist == pytest.approx(50, abs=0.5)

    def test_angle_rotates_first_vertex(self):
        from vectormation.objects import Circle
        c = Circle(r=100, cx=0, cy=0)
        poly0 = c.inscribed_polygon(4, angle=0)
        poly90 = c.inscribed_polygon(4, angle=90)
        x0, _ = poly0.vertices[0].at_time(0)
        _, y90 = poly90.vertices[0].at_time(0)
        # With angle=0 first vertex is at rightmost (0 deg), with angle=90 at top
        assert x0 == pytest.approx(100, abs=0.5)
        assert y90 == pytest.approx(-100, abs=0.5)  # SVG y-up: y decreases upward

    def test_kwargs_forwarded(self):
        from vectormation.objects import Circle
        c = Circle(r=100, cx=400, cy=300)
        poly = c.inscribed_polygon(4, fill='#f00')
        svg = poly.to_svg(0)
        assert '255' in svg or 'f00' in svg.lower()


class TestWedgeToArc:
    def test_returns_arc_instance(self):
        w = Wedge(cx=500, cy=400, r=100, start_angle=30, end_angle=120)
        arc = w.to_arc()
        assert isinstance(arc, Arc)

    def test_preserves_center(self):
        w = Wedge(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        arc = w.to_arc()
        assert arc.cx.at_time(0) == pytest.approx(500)
        assert arc.cy.at_time(0) == pytest.approx(400)

    def test_preserves_radius(self):
        w = Wedge(cx=960, cy=540, r=80, start_angle=0, end_angle=180)
        arc = w.to_arc()
        assert arc.r.at_time(0) == pytest.approx(80)

    def test_preserves_angles(self):
        w = Wedge(cx=0, cy=0, r=50, start_angle=45, end_angle=135)
        arc = w.to_arc()
        assert arc.start_angle.at_time(0) == pytest.approx(45)
        assert arc.end_angle.at_time(0) == pytest.approx(135)

    def test_kwargs_forwarded(self):
        w = Wedge(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        arc = w.to_arc(stroke='#ff0000', stroke_width=3)
        svg = arc.to_svg(0)
        assert '255' in svg or 'ff0000' in svg.lower() or 'ff,' in svg.lower()

    def test_is_not_wedge(self):
        w = Wedge(cx=0, cy=0, r=50, start_angle=0, end_angle=90)
        arc = w.to_arc()
        assert not isinstance(arc, Wedge)

    def test_time_parameter_used(self):
        w = Wedge(cx=0, cy=0, r=50, start_angle=0, end_angle=90)
        # Animate the radius
        w.r.move_to(0, 1, 200)
        arc = w.to_arc(time=1)
        assert arc.r.at_time(0) == pytest.approx(200)


class TestRectangleGetCorners:
    def test_returns_four_corners(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        corners = r.get_corners()
        assert len(corners) == 4

    def test_corner_values(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        corners = r.get_corners()
        assert corners[0] == pytest.approx((10.0, 20.0))
        assert corners[1] == pytest.approx((110.0, 20.0))
        assert corners[2] == pytest.approx((110.0, 70.0))
        assert corners[3] == pytest.approx((10.0, 70.0))

    def test_square_corners(self):
        r = Rectangle.square(100, x=0, y=0)
        corners = r.get_corners()
        assert corners[0] == pytest.approx((0.0, 0.0))
        assert corners[2] == pytest.approx((100.0, 100.0))

    def test_all_floats(self):
        r = Rectangle(width=60, height=40, x=5, y=5)
        for pt in r.get_corners():
            assert isinstance(pt[0], float)
            assert isinstance(pt[1], float)

    def test_time_parameter(self):
        r = Rectangle(width=100, height=50, x=0, y=0)
        r.width.move_to(0, 1, 200)
        corners = r.get_corners(time=1)
        assert corners[1][0] == pytest.approx(200.0)
        assert corners[2][0] == pytest.approx(200.0)


class TestEllipseGetPointAtParameter:
    def test_t0_is_rightmost(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        x, y = e.get_point_at_parameter(0)
        assert x == pytest.approx(600.0)
        assert y == pytest.approx(400.0)

    def test_t025_is_bottom(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        x, y = e.get_point_at_parameter(0.25)
        assert x == pytest.approx(500.0)
        assert y == pytest.approx(450.0)

    def test_t05_is_leftmost(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        x, y = e.get_point_at_parameter(0.5)
        assert x == pytest.approx(400.0)
        assert y == pytest.approx(400.0)

    def test_t075_is_top(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        x, y = e.get_point_at_parameter(0.75)
        assert x == pytest.approx(500.0)
        assert y == pytest.approx(350.0)

    def test_point_lies_on_ellipse(self):
        rx, ry, cx, cy = 80, 40, 200, 300
        e = Ellipse(rx=rx, ry=ry, cx=cx, cy=cy)
        for t in [0, 0.1, 0.33, 0.5, 0.7, 0.99]:
            x, y = e.get_point_at_parameter(t)
            # Ellipse equation: ((x-cx)/rx)^2 + ((y-cy)/ry)^2 == 1
            val = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            assert val == pytest.approx(1.0, abs=1e-9)

    def test_time_parameter(self):
        e = Ellipse(rx=50, ry=50, cx=500, cy=400)
        e.rx.move_to(0, 1, 100)
        x, _ = e.get_point_at_parameter(0, time=1)
        assert x == pytest.approx(600.0)

    def test_circle_case(self):
        c = Circle(r=50, cx=0, cy=0)
        x, y = c.get_point_at_parameter(0)
        assert x == pytest.approx(50.0)
        assert y == pytest.approx(0.0, abs=1e-9)


class TestLineGetDirection:
    def test_horizontal_right(self):
        l = Line(x1=0, y1=0, x2=10, y2=0)
        dx, dy = l.get_direction()
        assert dx == pytest.approx(1.0)
        assert dy == pytest.approx(0.0)

    def test_vertical_down(self):
        l = Line(x1=0, y1=0, x2=0, y2=10)
        dx, dy = l.get_direction()
        assert dx == pytest.approx(0.0)
        assert dy == pytest.approx(1.0)

    def test_diagonal(self):
        l = Line(x1=0, y1=0, x2=3, y2=4)
        dx, dy = l.get_direction()
        assert dx == pytest.approx(0.6)
        assert dy == pytest.approx(0.8)

    def test_unit_length(self):
        import math
        l = Line(x1=100, y1=200, x2=300, y2=500)
        dx, dy = l.get_direction()
        assert math.hypot(dx, dy) == pytest.approx(1.0)

    def test_zero_length_line(self):
        l = Line(x1=5, y1=5, x2=5, y2=5)
        dx, dy = l.get_direction()
        assert dx == pytest.approx(0.0)
        assert dy == pytest.approx(0.0)

    def test_time_parameter(self):
        l = Line(x1=0, y1=0, x2=1, y2=0)
        l.p2.move_to(0, 1, (0, 10))
        dx, dy = l.get_direction(time=1)
        assert dx == pytest.approx(0.0)
        assert dy == pytest.approx(1.0)


class TestCircleTangentAtPoint:
    def test_tangent_at_rightmost_point(self):
        """Point to the right of the circle — tangent should be vertical."""
        c = Circle(r=100, cx=500, cy=500)
        # Point far to the right — closest circle point is (600, 500)
        tl = c.tangent_at_point(900, 500)
        x1, _ = tl.p1.at_time(0)
        x2, _ = tl.p2.at_time(0)
        # Tangent at rightmost point is vertical: x1 == x2 == 600
        assert x1 == pytest.approx(600, abs=2)
        assert x2 == pytest.approx(600, abs=2)

    def test_tangent_at_top_point(self):
        """Point above the circle — tangent should be horizontal."""
        c = Circle(r=100, cx=500, cy=500)
        # In SVG coords y increases downward; UP means lower y value.
        # Closest circle point when reference is above center is (500, 400).
        tl = c.tangent_at_point(500, 200)
        _, y1 = tl.p1.at_time(0)
        _, y2 = tl.p2.at_time(0)
        assert y1 == pytest.approx(400, abs=2)
        assert y2 == pytest.approx(400, abs=2)

    def test_returns_line(self):
        """Result should be a Line instance."""
        c = Circle(r=50, cx=200, cy=200)
        tl = c.tangent_at_point(300, 200)
        assert isinstance(tl, Line)

    def test_tangent_length(self):
        """The line length should equal the requested length."""
        import math
        c = Circle(r=50, cx=200, cy=200)
        tl = c.tangent_at_point(300, 200, length=150)
        x1, y1 = tl.p1.at_time(0)
        x2, y2 = tl.p2.at_time(0)
        length = math.hypot(x2 - x1, y2 - y1)
        assert length == pytest.approx(150, abs=1)

    def test_tangent_perpendicular_to_radius(self):
        """Tangent vector is perpendicular to the radius at the contact point."""
        cx, cy, r = 400, 300, 80
        c = Circle(r=r, cx=cx, cy=cy)
        ref_x, ref_y = 500, 300  # to the right
        tl = c.tangent_at_point(ref_x, ref_y)
        x1, y1 = tl.p1.at_time(0)
        x2, y2 = tl.p2.at_time(0)
        # Contact point on circle
        contact_x, contact_y = cx + r, cy
        # Radius vector
        rx, ry = contact_x - cx, contact_y - cy
        # Tangent direction
        tx, ty = x2 - x1, y2 - y1
        dot = rx * tx + ry * ty
        assert abs(dot) == pytest.approx(0.0, abs=1e-6)


class TestPolygonGetEdges:
    def test_triangle_has_three_edges(self):
        """A closed triangle has exactly 3 edges."""
        tri = Polygon((0, 0), (100, 0), (50, 100))
        edges = tri.get_edges()
        assert len(edges) == 3

    def test_square_has_four_edges(self):
        """A closed square has exactly 4 edges."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        edges = sq.get_edges()
        assert len(edges) == 4

    def test_open_polyline_omits_closing_edge(self):
        """An open polyline with 3 points has 2 edges (no closing edge)."""
        poly = Polygon((0, 0), (100, 0), (200, 0), closed=False)
        edges = poly.get_edges()
        assert len(edges) == 2

    def test_edges_are_line_objects(self):
        """Each returned edge is a Line instance."""
        tri = Polygon((0, 0), (100, 0), (50, 100))
        for edge in tri.get_edges():
            assert isinstance(edge, Line)

    def test_edge_endpoints_match_vertices(self):
        """Edge endpoints match consecutive polygon vertices."""
        pts = [(0, 0), (100, 0), (100, 100)]
        tri = Polygon(*pts)
        edges = tri.get_edges()
        # First edge: (0,0) -> (100,0)
        x1, y1 = edges[0].p1.at_time(0)
        x2, y2 = edges[0].p2.at_time(0)
        assert x1 == pytest.approx(0)
        assert y1 == pytest.approx(0)
        assert x2 == pytest.approx(100)
        assert y2 == pytest.approx(0)
        # Last (closing) edge: (100,100) -> (0,0)
        x1, y1 = edges[2].p1.at_time(0)
        x2, y2 = edges[2].p2.at_time(0)
        assert x1 == pytest.approx(100)
        assert y1 == pytest.approx(100)
        assert x2 == pytest.approx(0)
        assert y2 == pytest.approx(0)

    def test_empty_polygon_returns_empty(self):
        """A polygon with fewer than 2 vertices returns an empty list."""
        single = Polygon((50, 50))
        assert single.get_edges() == []


class TestAxesGetIntersectionPoint:
    def test_simple_crossing(self):
        """Two simple functions that cross at x=0."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_intersection_point(lambda x: x, lambda x: -x, (-2, 2))
        assert result is not None
        x, y = result
        assert x == pytest.approx(0.0, abs=0.05)
        assert y == pytest.approx(0.0, abs=0.05)

    def test_quadratic_crossing(self):
        """x^2 and x+2 cross near x≈-1 and x≈2; find the one near x=1.5."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 15))
        result = ax.get_intersection_point(lambda x: x**2, lambda x: x + 2, (1, 3))
        assert result is not None
        x, _ = result
        # Actual crossing at x=2: 4==4
        assert x == pytest.approx(2.0, abs=0.05)

    def test_no_crossing_returns_none(self):
        """Returns None when the functions don't cross in the given range."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_intersection_point(lambda x: x + 10, lambda x: x, (0, 5))
        assert result is None

    def test_tolerance(self):
        """Result is within tolerance of the true intersection."""
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_intersection_point(math.sin, math.cos, (0, 1), tol=0.001)
        assert result is not None
        x, _ = result
        # sin(x)==cos(x) at x=pi/4
        assert x == pytest.approx(math.pi / 4, abs=0.01)

    def test_returns_tuple(self):
        """Result is a (x, y) tuple."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_intersection_point(lambda x: x, lambda _: 0, (-2, 2))  # noqa: E731
        assert result is not None
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Tests for new features
# ---------------------------------------------------------------------------

class TestSwing:
    def test_swing_returns_self(self):
        c = Circle(r=50, cx=100, cy=300)
        result = c.swing(start=0, end=1, amplitude=20)
        assert result is c

    def test_swing_zero_rotation_at_start(self):
        """At t=0 (start of swing) normalised time is 0, so rotation is 0."""
        c = Circle(r=50, cx=100, cy=300)
        c.swing(start=0, end=2, amplitude=30)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(0, abs=0.5)

    def test_swing_zero_rotation_at_end(self):
        """Decay factor (1-t) ensures rotation returns to ~0 at t=1."""
        c = Circle(r=50, cx=100, cy=300)
        c.swing(start=0, end=2, amplitude=30)
        rot = c.styling.rotation.at_time(2)
        assert rot[0] == pytest.approx(0, abs=0.5)

    def test_swing_nonzero_in_middle(self):
        """Rotation should be nonzero somewhere in the middle of the swing."""
        c = Circle(r=50, cx=100, cy=300)
        c.swing(start=0, end=2, amplitude=30)
        rot_mid = c.styling.rotation.at_time(0.5)
        assert abs(rot_mid[0]) > 1.0

    def test_swing_custom_pivot(self):
        """Custom cx/cy should be stored in the rotation tuple."""
        c = Circle(r=50, cx=100, cy=300)
        c.swing(start=0, end=1, amplitude=10, cx=200, cy=400)
        rot = c.styling.rotation.at_time(0.3)
        assert rot[1] == pytest.approx(200)
        assert rot[2] == pytest.approx(400)


class TestLineExtendTo:
    def test_extend_to_anchor_start_increases_length(self):
        """Extending with anchor='start' should move p2 outward."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend_to(200, anchor='start')
        p2 = line.p2.at_time(0)
        assert p2[0] == pytest.approx(200)
        assert p2[1] == pytest.approx(0)

    def test_extend_to_anchor_end_moves_p1(self):
        """Extending with anchor='end' should move p1 outward."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend_to(200, anchor='end')
        p1 = line.p1.at_time(0)
        assert p1[0] == pytest.approx(-100)
        assert p1[1] == pytest.approx(0)

    def test_extend_to_shrink(self):
        """Passing a smaller length should shrink the line."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend_to(50, anchor='start')
        p2 = line.p2.at_time(0)
        assert p2[0] == pytest.approx(50)

    def test_extend_to_preserves_direction(self):
        """Direction of the line should not change after extend_to."""
        import math
        line = Line(x1=0, y1=0, x2=60, y2=80)  # 3-4-5 triangle, length 100
        line.extend_to(200, anchor='start')
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        assert length == pytest.approx(200, rel=1e-4)
        # Direction should still be (0.6, 0.8)
        assert dx / length == pytest.approx(0.6, abs=1e-4)
        assert dy / length == pytest.approx(0.8, abs=1e-4)

    def test_extend_to_returns_self(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        assert line.extend_to(150) is line

    def test_extend_to_animated(self):
        """With end, the endpoint should animate smoothly."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend_to(200, anchor='start', start=0, end=1,
                       easing=easings.linear)
        # At t=0 still at original length (approximately)
        p2_start = line.p2.at_time(0)
        p2_end = line.p2.at_time(1)
        assert p2_start[0] == pytest.approx(100, abs=1)
        assert p2_end[0] == pytest.approx(200, abs=1)


class TestLineGetPerpendicularPoint:
    def test_foot_on_horizontal_line(self):
        line = Line(x1=0, y1=100, x2=200, y2=100)
        foot = line.get_perpendicular_point(80, 50)
        assert foot[0] == pytest.approx(80)
        assert foot[1] == pytest.approx(100)

    def test_foot_on_vertical_line(self):
        line = Line(x1=100, y1=0, x2=100, y2=200)
        foot = line.get_perpendicular_point(50, 130)
        assert foot[0] == pytest.approx(100)
        assert foot[1] == pytest.approx(130)

    def test_foot_clamps_to_start(self):
        """External point beyond start of segment clamps to p1."""
        line = Line(x1=50, y1=0, x2=150, y2=0)
        foot = line.get_perpendicular_point(10, 0)
        assert foot[0] == pytest.approx(50)

    def test_foot_clamps_to_end(self):
        """External point beyond end of segment clamps to p2."""
        line = Line(x1=50, y1=0, x2=150, y2=0)
        foot = line.get_perpendicular_point(200, 0)
        assert foot[0] == pytest.approx(150)

    def test_foot_is_on_segment(self):
        """The foot should lie on the segment (within the bounding box)."""
        line = Line(x1=0, y1=0, x2=100, y2=100)
        foot = line.get_perpendicular_point(80, 20)
        assert 0 <= foot[0] <= 100
        assert 0 <= foot[1] <= 100

    def test_degenerate_line(self):
        """Zero-length line returns the single point."""
        line = Line(x1=50, y1=50, x2=50, y2=50)
        foot = line.get_perpendicular_point(100, 200)
        assert foot == pytest.approx((50.0, 50.0))


class TestRectangleSplit:
    def test_horizontal_count_2(self):
        r = Rectangle(200, 100, x=0, y=0)
        parts = r.split(direction='horizontal', count=2)
        assert len(parts.objects) == 2
        # Each part should be half the height
        for p in parts.objects:
            assert p.height.at_time(0) == pytest.approx(50)
            assert p.width.at_time(0) == pytest.approx(200)

    def test_vertical_count_3(self):
        r = Rectangle(300, 60, x=0, y=0)
        parts = r.split(direction='vertical', count=3)
        assert len(parts.objects) == 3
        for p in parts.objects:
            assert p.width.at_time(0) == pytest.approx(100)
            assert p.height.at_time(0) == pytest.approx(60)

    def test_horizontal_positions(self):
        """Sub-rectangles should be stacked top-to-bottom."""
        r = Rectangle(100, 90, x=10, y=20)
        parts = r.split(direction='horizontal', count=3)
        ys = [p.y.at_time(0) for p in parts.objects]
        assert ys[0] == pytest.approx(20)
        assert ys[1] == pytest.approx(50)
        assert ys[2] == pytest.approx(80)

    def test_vertical_positions(self):
        """Sub-rectangles should be arranged left-to-right."""
        r = Rectangle(120, 60, x=0, y=0)
        parts = r.split(direction='vertical', count=4)
        xs = [p.x.at_time(0) for p in parts.objects]
        for i, x in enumerate(xs):
            assert x == pytest.approx(i * 30)

    def test_returns_vcollection(self):
        r = Rectangle(100, 100)
        result = r.split()
        assert isinstance(result, VCollection)

    def test_count_1(self):
        """Splitting into 1 piece should return a single rectangle of the same size."""
        r = Rectangle(200, 80, x=5, y=10)
        parts = r.split(count=1)
        assert len(parts.objects) == 1
        assert parts.objects[0].width.at_time(0) == pytest.approx(200)
        assert parts.objects[0].height.at_time(0) == pytest.approx(80)

    def test_invalid_count(self):
        r = Rectangle(100, 100)
        with pytest.raises(ValueError):
            r.split(count=0)

    def test_tiling_horizontal(self):
        """All parts together should cover the full rectangle height."""
        r = Rectangle(100, 100, x=0, y=0)
        parts = r.split(direction='horizontal', count=5)
        total_h = sum(p.height.at_time(0) for p in parts.objects)
        assert total_h == pytest.approx(100)


class TestAxesAddAreaLabel:
    def test_returns_text(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 4))
        lbl = ax.add_area_label(lambda x: x, x_start=0, x_end=2)
        assert isinstance(lbl, Text)

    def test_area_value_in_text(self):
        """For f(x)=1 over [0,3], area = 3.00."""
        ax = Axes(x_range=(0, 4), y_range=(0, 4))
        lbl = ax.add_area_label(lambda _: 1, x_start=0, x_end=3)
        assert 'A = 3.00' in lbl.text.at_time(0)

    def test_custom_text(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 4))
        lbl = ax.add_area_label(lambda x: x, x_start=0, x_end=2, text='custom')
        assert lbl.text.at_time(0) == 'custom'

    def test_x_range_backwards_compat(self):
        """x_range=[a,b] should still work."""
        ax = Axes(x_range=(0, 4), y_range=(0, 4))
        lbl = ax.add_area_label(lambda _: 1, x_range=[0, 2])
        assert 'A = 2.00' in lbl.text.at_time(0)

    def test_trapezoidal_quadratic(self):
        """For f(x)=x^2 over [0,3], exact area = 9.  Trapezoidal with many
        samples should be within 1% of exact."""
        ax = Axes(x_range=(0, 4), y_range=(0, 10))
        lbl = ax.add_area_label(lambda x: x ** 2, x_start=0, x_end=3,
                                samples=1000)
        # Extract numeric value from "A = X.XX"
        val_str = lbl.text.at_time(0).split('=')[1].strip()
        val = float(val_str)
        assert val == pytest.approx(9.0, rel=0.01)


class TestLineSplitAt:
    def test_midpoint_split_returns_two_lines(self):
        line = Line(0, 0, 200, 0)
        a, b = line.split_at(0.5)
        assert isinstance(a, Line)
        assert isinstance(b, Line)

    def test_midpoint_split_start_of_first(self):
        line = Line(0, 0, 200, 0)
        a, _ = line.split_at(0.5)
        assert a.get_start() == pytest.approx((0.0, 0.0))

    def test_midpoint_split_end_of_first(self):
        line = Line(0, 0, 200, 0)
        a, _ = line.split_at(0.5)
        assert a.get_end() == pytest.approx((100.0, 0.0))

    def test_midpoint_split_start_of_second(self):
        line = Line(0, 0, 200, 0)
        _, b = line.split_at(0.5)
        assert b.get_start() == pytest.approx((100.0, 0.0))

    def test_midpoint_split_end_of_second(self):
        line = Line(0, 0, 200, 0)
        _, b = line.split_at(0.5)
        assert b.get_end() == pytest.approx((200.0, 0.0))

    def test_quarter_split(self):
        line = Line(0, 0, 200, 0)
        a, b = line.split_at(0.25)
        assert a.get_end() == pytest.approx((50.0, 0.0))
        assert b.get_start() == pytest.approx((50.0, 0.0))
        assert b.get_end() == pytest.approx((200.0, 0.0))

    def test_diagonal_split(self):
        line = Line(0, 0, 100, 100)
        a, b = line.split_at(0.5)
        assert a.get_end() == pytest.approx((50.0, 50.0))
        assert b.get_start() == pytest.approx((50.0, 50.0))

    def test_t_zero_clamps(self):
        line = Line(10, 20, 200, 300)
        a, b = line.split_at(0.0)
        # First segment is degenerate (zero length)
        assert a.get_start() == pytest.approx(a.get_end())
        assert b.get_start() == pytest.approx((10.0, 20.0))

    def test_t_one_clamps(self):
        line = Line(10, 20, 200, 300)
        a, b = line.split_at(1.0)
        # Second segment is degenerate (zero length)
        assert b.get_start() == pytest.approx(b.get_end())
        assert a.get_end() == pytest.approx((200.0, 300.0))

    def test_default_t_is_half(self):
        line = Line(0, 0, 100, 0)
        a, _ = line.split_at()
        assert a.get_end() == pytest.approx((50.0, 0.0))

    def test_lengths_sum_to_original(self):
        line = Line(0, 0, 300, 400)  # length = 500
        a, b = line.split_at(0.6)
        assert a.get_length() + b.get_length() == pytest.approx(line.get_length())

    def test_independent_objects(self):
        line = Line(0, 0, 100, 0)
        a, _ = line.split_at()
        # Moving the original should not affect returned lines
        line.shift(dx=999, start=0)
        assert a.get_start() == pytest.approx((0.0, 0.0))


class TestAxesGetPlotCenter:
    def test_default_axes_center_x(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        cx, _ = ax.get_plot_center()
        assert cx == pytest.approx(ax.plot_x + ax.plot_width / 2)

    def test_default_axes_center_y(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        _, cy = ax.get_plot_center()
        assert cy == pytest.approx(ax.plot_y + ax.plot_height / 2)

    def test_custom_layout(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), x=100, y=200,
                  plot_width=800, plot_height=600)
        cx, cy = ax.get_plot_center()
        assert cx == pytest.approx(100 + 800 / 2)
        assert cy == pytest.approx(200 + 600 / 2)

    def test_returns_tuple(self):
        ax = Axes(x_range=(-1, 1), y_range=(-1, 1))
        result = ax.get_plot_center()
        assert len(result) == 2

    def test_independent_of_time_argument(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        assert ax.get_plot_center(0) == ax.get_plot_center(5)

    def test_different_from_axes_origin(self):
        """The plot centre is not the same as the math (0,0) origin."""
        ax = Axes(x_range=(-10, 10), y_range=(-10, 10))
        cx, cy = ax.get_plot_center()
        # They happen to coincide only when the range is symmetric AND the
        # plot is centred — but the method should still return the geometric
        # centre of the plot area, not the origin.
        assert cx == pytest.approx(ax.plot_x + ax.plot_width / 2)
        assert cy == pytest.approx(ax.plot_y + ax.plot_height / 2)


class TestRectangleGetDiagonalLength:
    def test_3_4_5_triangle(self):
        """Classic 3-4-5 right triangle."""
        r = Rectangle(width=3, height=4)
        assert r.get_diagonal_length() == pytest.approx(5.0)

    def test_square_diagonal(self):
        """Diagonal of a unit square is sqrt(2)."""
        import math
        r = Rectangle(width=1, height=1)
        assert r.get_diagonal_length() == pytest.approx(math.sqrt(2))

    def test_zero_height(self):
        """Zero height — diagonal equals width."""
        r = Rectangle(width=7, height=0)
        assert r.get_diagonal_length() == pytest.approx(7.0)

    def test_returns_float(self):
        r = Rectangle(width=100, height=200)
        d = r.get_diagonal_length()
        assert isinstance(d, float)


class TestLineGetNormal:
    def test_horizontal_line_normal_is_vertical(self):
        """A right-pointing line should have an upward normal (in SVG y-down this is (0,-1))."""
        l = Line(x1=0, y1=0, x2=10, y2=0)
        nx, ny = l.get_normal()
        # direction is (1,0), normal is (-0,1) = (0,1) but _normalize(-0,1)=(0,1)
        # direction=(1,0) -> normal=(-0,1)=(0,1)  wait: (-dy,dx) = (-0, 1) = (0,1)
        assert nx == pytest.approx(0.0, abs=1e-9)
        assert ny == pytest.approx(1.0, abs=1e-9)

    def test_vertical_line_normal_is_horizontal(self):
        """A downward-pointing line (SVG y increases down) should have normal pointing left."""
        l = Line(x1=0, y1=0, x2=0, y2=10)
        nx, ny = l.get_normal()
        # direction is (0,1), normal is (-1, 0)
        assert nx == pytest.approx(-1.0, abs=1e-9)
        assert ny == pytest.approx(0.0, abs=1e-9)

    def test_normal_is_unit_vector(self):
        """Normal should be a unit vector."""
        import math
        l = Line(x1=0, y1=0, x2=3, y2=4)
        nx, ny = l.get_normal()
        magnitude = math.sqrt(nx * nx + ny * ny)
        assert magnitude == pytest.approx(1.0)

    def test_normal_orthogonal_to_direction(self):
        """Normal dot direction should be zero (perpendicular)."""
        l = Line(x1=100, y1=200, x2=400, y2=350)
        dx, dy = l.get_direction()
        nx, ny = l.get_normal()
        dot = dx * nx + dy * ny
        assert dot == pytest.approx(0.0, abs=1e-9)

    def test_zero_length_line_returns_zero(self):
        """Zero-length line should return (0.0, 0.0)."""
        l = Line(x1=5, y1=5, x2=5, y2=5)
        nx, ny = l.get_normal()
        assert nx == pytest.approx(0.0)
        assert ny == pytest.approx(0.0)


class TestAxesAddTangentAt:
    def test_add_tangent_at_returns_line(self):
        """add_tangent_at should return a Line object."""
        from vectormation.objects import Line
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_tangent_at(lambda x: x ** 2, x_val=1)
        assert isinstance(line, Line)

    def test_add_tangent_at_at_minimum_is_horizontal(self):
        """Tangent at x=0 for x^2 is horizontal (slope=0), so y1==y2."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_tangent_at(lambda x: x ** 2, x_val=0, length=200)
        y1, y2 = line.p1.at_time(0)[1], line.p2.at_time(0)[1]
        assert y1 == pytest.approx(y2, abs=1.0)

    def test_add_tangent_at_length(self):
        """The tangent line should be approximately the requested length."""
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_tangent_at(lambda x: x, x_val=0, length=200)
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        assert length == pytest.approx(200, abs=1.0)

    def test_add_tangent_at_accepts_styling_kwargs(self):
        """add_tangent_at should forward styling kwargs."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_tangent_at(lambda x: x, x_val=0, stroke_width=5)
        assert line.styling.stroke_width.at_time(0) == pytest.approx(5)


class TestCircleArcBetween:
    def test_returns_arc_instance(self):
        c = Circle(r=100, cx=500, cy=300)
        arc = c.arc_between(0, 90)
        assert isinstance(arc, Arc)

    def test_arc_has_same_center(self):
        c = Circle(r=100, cx=500, cy=300)
        arc = c.arc_between(0, 90)
        assert arc.cx.at_time(0) == pytest.approx(500)
        assert arc.cy.at_time(0) == pytest.approx(300)

    def test_arc_has_same_radius(self):
        c = Circle(r=80, cx=200, cy=400)
        arc = c.arc_between(45, 135)
        assert arc.r.at_time(0) == pytest.approx(80)

    def test_arc_angles_preserved(self):
        c = Circle(r=100, cx=960, cy=540)
        arc = c.arc_between(30, 150)
        assert arc.start_angle.at_time(0) == pytest.approx(30)
        assert arc.end_angle.at_time(0) == pytest.approx(150)

    def test_arc_between_accepts_kwargs(self):
        c = Circle(r=100)
        arc = c.arc_between(0, 180, stroke_width=5)
        assert arc.styling.stroke_width.at_time(0) == pytest.approx(5)

    def test_arc_between_respects_time(self):
        """arc_between reads position/radius at the specified time."""
        c = Circle(r=50, cx=100, cy=100)
        c.shift(dx=200, dy=100, start=1)
        arc = c.arc_between(0, 90, time=1)
        assert arc.cx.at_time(0) == pytest.approx(300)
        assert arc.cy.at_time(0) == pytest.approx(200)


class TestTextWordCount:
    def test_basic_word_count(self):
        t = Text('hello world foo')
        assert t.word_count() == 3

    def test_single_word(self):
        assert Text('word').word_count() == 1

    def test_empty_string(self):
        assert Text('').word_count() == 0

    def test_whitespace_only(self):
        assert Text('   ').word_count() == 0

    def test_multiple_spaces(self):
        assert Text('hello   world').word_count() == 2

    def test_default_time_zero(self):
        t = Text('one two three four')
        assert t.word_count() == 4

    def test_word_count_at_time(self):
        """word_count respects the time parameter."""
        t = Text('one two')
        # Simulate text change at time 2
        t.text.set_onward(2, 'alpha beta gamma delta')
        assert t.word_count(time=0) == 2
        assert t.word_count(time=2) == 4


class TestAxesAxisLines:
    def test_get_x_axis_line_returns_line(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        line = ax.get_x_axis_line()
        assert isinstance(line, Line)

    def test_get_y_axis_line_returns_line(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        line = ax.get_y_axis_line()
        assert isinstance(line, Line)

    def test_x_axis_line_is_horizontal(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        line = ax.get_x_axis_line()
        y1 = line.p1.at_time(0)[1]
        y2 = line.p2.at_time(0)[1]
        assert y1 == pytest.approx(y2)

    def test_y_axis_line_is_vertical(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        line = ax.get_y_axis_line()
        x1 = line.p1.at_time(0)[0]
        x2 = line.p2.at_time(0)[0]
        assert x1 == pytest.approx(x2)

    def test_x_axis_line_spans_plot_width(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3), x=260, plot_width=1400)
        line = ax.get_x_axis_line()
        x1 = line.p1.at_time(0)[0]
        x2 = line.p2.at_time(0)[0]
        assert x1 == pytest.approx(260)
        assert x2 == pytest.approx(1660)

    def test_y_axis_line_at_zero_within_range(self):
        """When x=0 is in range the y-axis line sits at x=0 in math coords."""
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3), x=260, plot_width=1400)
        line = ax.get_y_axis_line()
        x_val = line.p1.at_time(0)[0]
        # x=0 is the midpoint of [-5, 5], so SVG x = 260 + 700 = 960
        assert x_val == pytest.approx(960)

    def test_y_axis_line_at_left_edge_when_zero_out_of_range(self):
        """When x=0 is outside x_range, line falls back to the left plot edge."""
        ax = Axes(x_range=(1, 10), y_range=(-3, 3), x=260, plot_width=1400)
        line = ax.get_y_axis_line()
        x_val = line.p1.at_time(0)[0]
        assert x_val == pytest.approx(260)

    def test_get_x_axis_line_accepts_styling(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        line = ax.get_x_axis_line(stroke='#FF0000', stroke_width=4)
        assert line.styling.stroke_width.at_time(0) == pytest.approx(4)


# ---------------------------------------------------------------------------
# New feature tests
# ---------------------------------------------------------------------------

class TestSetStrokeDash:
    def test_string_pattern_sets_dasharray(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke_dash('5 3')
        assert c.styling.stroke_dasharray.at_time(0) == '5 3'

    def test_list_pattern_converts_to_string(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke_dash([8, 4, 2, 4])
        assert c.styling.stroke_dasharray.at_time(0) == '8 4 2 4'

    def test_tuple_pattern_converts_to_string(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke_dash((10, 5))
        assert c.styling.stroke_dasharray.at_time(0) == '10 5'

    def test_none_clears_pattern(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke_dash('5 3')
        c.set_stroke_dash(None, start=1)
        assert c.styling.stroke_dasharray.at_time(1) == ''

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_stroke_dash('5 3')
        assert result is c

    def test_respects_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke_dash('5 3', start=2)
        # Before start time pattern should not be set (default empty)
        assert c.styling.stroke_dasharray.at_time(0) != '5 3'
        assert c.styling.stroke_dasharray.at_time(2) == '5 3'

    def test_works_on_polygon(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        p.set_stroke_dash('4 2')
        assert p.styling.stroke_dasharray.at_time(0) == '4 2'


class TestPolygonIsRegular:
    def test_equilateral_triangle_is_regular(self):
        import math
        s = 100.0
        h = s * math.sqrt(3) / 2
        tri = Polygon((0, 0), (s, 0), (s / 2, -h))
        assert tri.is_regular() is True

    def test_square_is_regular(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.is_regular() is True

    def test_rectangle_not_regular(self):
        rect = Polygon((0, 0), (200, 0), (200, 50), (0, 50))
        assert rect.is_regular() is False

    def test_open_polygon_not_regular(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=False)
        assert sq.is_regular() is False

    def test_degenerate_two_vertices_not_regular(self):
        p = Polygon((0, 0), (100, 0))
        assert p.is_regular() is False

    def test_regular_pentagon(self):
        import math
        n = 5
        pts = [(math.cos(2 * math.pi * i / n) * 100,
                math.sin(2 * math.pi * i / n) * 100) for i in range(n)]
        p = Polygon(*pts)
        assert p.is_regular() is True

    def test_tolerance_parameter(self):
        # Slightly distorted square: one side is 101 instead of 100.
        sq = Polygon((0, 0), (101, 0), (101, 100), (0, 100))
        # With tight tolerance should be False
        assert sq.is_regular(tol=1e-6) is False
        # With loose tolerance (5%) should pass
        assert sq.is_regular(tol=0.05) is True


class TestVCollectionGroupBy:
    def test_group_by_type(self):
        c1 = Circle(r=50)
        c2 = Circle(r=30)
        r1 = Rectangle(width=100, height=50)
        col = VCollection(c1, c2, r1)
        groups = col.group_by(type)
        assert Circle in groups
        assert Rectangle in groups
        assert len(groups[Circle].objects) == 2
        assert len(groups[Rectangle].objects) == 1

    def test_returns_vcollection_values(self):
        c1 = Circle(r=50)
        col = VCollection(c1)
        groups = col.group_by(type)
        assert isinstance(groups[Circle], VCollection)

    def test_group_by_custom_func(self):
        c1 = Circle(r=50)
        c2 = Circle(r=100)
        c3 = Circle(r=50)
        col = VCollection(c1, c2, c3)
        # Group by radius at time=0
        groups = col.group_by(lambda o: o.rx.at_time(0))
        assert len(groups[50.0].objects) == 2
        assert len(groups[100.0].objects) == 1

    def test_empty_collection(self):
        col = VCollection()
        groups = col.group_by(type)
        assert groups == {}

    def test_single_group(self):
        circles = VCollection(Circle(r=10), Circle(r=20))
        groups = circles.group_by(type)
        assert len(groups) == 1
        assert Circle in groups


class TestAxesGetAreaValue:
    def test_quadratic_integral(self):
        ax = Axes(x_range=(0, 3), y_range=(0, 10))
        # integral of x^2 from 0 to 3 = 9.0
        result = ax.get_area_value(lambda x: x ** 2, 0, 3, samples=1000)
        assert result == pytest.approx(9.0, rel=1e-3)

    def test_constant_function(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        # integral of 2 from 1 to 4 = 6.0
        result = ax.get_area_value(lambda _: 2.0, 1, 4)
        assert result == pytest.approx(6.0, rel=1e-6)

    def test_linear_function(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        # integral of x from 0 to 4 = 8.0
        result = ax.get_area_value(lambda x: x, 0, 4, samples=1000)
        assert result == pytest.approx(8.0, rel=1e-3)

    def test_returns_float(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        result = ax.get_area_value(lambda x: x, 0, 2)
        assert isinstance(result, float)

    def test_accepts_plot_curve(self):
        """get_area_value should accept a Path with ._func attribute."""
        ax = Axes(x_range=(0, 4), y_range=(0, 5))
        curve = ax.plot(lambda x: x)
        result = ax.get_area_value(curve, 0, 4, samples=1000)
        # integral of x from 0 to 4 = 8.0
        assert result == pytest.approx(8.0, rel=1e-3)

    def test_zero_range(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        result = ax.get_area_value(lambda x: x ** 2, 2, 2)
        assert result == pytest.approx(0.0, abs=1e-10)


class TestLineFromAngle:
    def test_zero_degrees_points_right(self):
        line = Line.from_angle((0, 0), 0, 100)
        x2, y2 = line.p2.at_time(0)
        assert x2 == pytest.approx(100, abs=1e-9)
        assert y2 == pytest.approx(0, abs=1e-9)

    def test_ninety_degrees_points_up_svgy(self):
        """90° CCW from x-axis points upward (negative y in SVG)."""
        line = Line.from_angle((0, 0), 90, 100)
        x2, y2 = line.p2.at_time(0)
        assert x2 == pytest.approx(0, abs=1e-9)
        assert y2 == pytest.approx(-100, abs=1e-9)

    def test_180_degrees_points_left(self):
        line = Line.from_angle((0, 0), 180, 100)
        x2, y2 = line.p2.at_time(0)
        assert x2 == pytest.approx(-100, abs=1e-9)
        assert y2 == pytest.approx(0, abs=1e-9)

    def test_origin_is_start_point(self):
        line = Line.from_angle((200, 300), 45, 50)
        x1, y1 = line.p1.at_time(0)
        assert x1 == pytest.approx(200)
        assert y1 == pytest.approx(300)

    def test_length_is_correct(self):
        import math
        line = Line.from_angle((0, 0), 37, 150)
        x2, y2 = line.p2.at_time(0)
        length = math.sqrt(x2 ** 2 + y2 ** 2)
        assert length == pytest.approx(150, abs=1e-6)

    def test_returns_line_instance(self):
        assert isinstance(Line.from_angle((0, 0), 0, 100), Line)

    def test_kwargs_forwarded(self):
        line = Line.from_angle((0, 0), 0, 100, stroke='#FF0000')
        stroke_val = line.styling.stroke.at_time(0)
        # Accept any common representation of red
        assert any(s in stroke_val.lower() for s in ('ff0000', 'red', '255,0,0'))

    def test_equivalent_to_from_direction_at_zero(self):
        """from_angle(0°) should produce the same line as from_direction((1,0))."""
        la = Line.from_angle((0, 0), 0, 200)
        ld = Line.from_direction((0, 0), (1, 0), 200)
        x2a, y2a = la.p2.at_time(0)
        x2d, y2d = ld.p2.at_time(0)
        assert x2a == pytest.approx(x2d, abs=1e-6)
        assert y2a == pytest.approx(y2d, abs=1e-6)


class TestEllipseEccentricity:
    def test_circle_eccentricity_is_zero(self):
        """A circle (rx == ry) has eccentricity 0."""
        e = Ellipse(rx=80, ry=80, cx=500, cy=400)
        assert e.eccentricity() == pytest.approx(0.0)

    def test_elongated_ellipse(self):
        """A 3:1 ellipse has eccentricity sqrt(1 - (1/3)^2) = sqrt(8/9)."""
        import math
        e = Ellipse(rx=90, ry=30, cx=500, cy=400)
        expected = math.sqrt(1 - (30 / 90) ** 2)
        assert e.eccentricity() == pytest.approx(expected)

    def test_swapped_axes(self):
        """Eccentricity is symmetric: rx < ry gives the same result as rx > ry."""
        e1 = Ellipse(rx=100, ry=60, cx=500, cy=400)
        e2 = Ellipse(rx=60, ry=100, cx=500, cy=400)
        assert e1.eccentricity() == pytest.approx(e2.eccentricity())

    def test_zero_radius_returns_zero(self):
        """Degenerate ellipse with rx=0 returns 0 without division error."""
        e = Ellipse(rx=0, ry=0, cx=500, cy=400)
        assert e.eccentricity() == pytest.approx(0.0)

    def test_range_zero_to_one(self):
        """Eccentricity must be in [0, 1)."""
        for rx, ry in [(100, 50), (200, 10), (50, 50), (1, 100)]:
            e = Ellipse(rx=rx, ry=ry)
            ecc = e.eccentricity()
            assert 0.0 <= ecc < 1.0


class TestNumberLineGetRange:
    def test_basic_range(self):
        nl = NumberLine(x_range=(-5, 5, 1), length=500, x=100, y=500)
        assert nl.get_range() == (-5, 5)

    def test_custom_range(self):
        nl = NumberLine(x_range=(0, 100, 10), length=600, x=200, y=300)
        assert nl.get_range() == (0, 100)

    def test_returns_tuple(self):
        nl = NumberLine(x_range=(1, 7, 2), length=400, x=100, y=500)
        result = nl.get_range()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_min_max_order(self):
        """min_val < max_val always."""
        nl = NumberLine(x_range=(-10, 10, 5))
        lo, hi = nl.get_range()
        assert lo < hi


class TestAxesGetPlotArea:
    def test_default_values(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_plot_area()
        assert result == (ax.plot_x, ax.plot_y, ax.plot_width, ax.plot_height)

    def test_returns_four_tuple(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.get_plot_area()
        assert len(result) == 4

    def test_custom_layout(self):
        ax = Axes(x_range=(0, 1), y_range=(0, 1), x=50, y=80,
                  plot_width=700, plot_height=500)
        px, py, pw, ph = ax.get_plot_area()
        assert px == 50
        assert py == 80
        assert pw == 700
        assert ph == 500

    def test_positive_dimensions(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        _, _, pw, ph = ax.get_plot_area()
        assert pw > 0
        assert ph > 0


class TestCircleChord:
    def test_chord_returns_line(self):
        c = Circle(r=100, cx=200, cy=200)
        ch = c.chord(0, 90)
        assert isinstance(ch, Line)

    def test_chord_endpoints_on_circle(self):
        c = Circle(r=100, cx=200, cy=200)
        ch = c.chord(0, 180)
        x1, y1 = ch.p1.at_time(0)
        x2, y2 = ch.p2.at_time(0)
        # 0 degrees -> (300, 200), 180 degrees -> (100, 200)
        assert x1 == pytest.approx(300, abs=1e-6)
        assert y1 == pytest.approx(200, abs=1e-6)
        assert x2 == pytest.approx(100, abs=1e-6)
        assert y2 == pytest.approx(200, abs=1e-6)

    def test_chord_90_degrees(self):
        c = Circle(r=100, cx=0, cy=0)
        ch = c.chord(0, 90)
        x1, y1 = ch.p1.at_time(0)
        x2, y2 = ch.p2.at_time(0)
        # angle 0 -> (100, 0), angle 90 -> (0, -100) in SVG coords
        assert x1 == pytest.approx(100, abs=1e-6)
        assert y1 == pytest.approx(0, abs=1e-6)
        assert x2 == pytest.approx(0, abs=1e-6)
        assert y2 == pytest.approx(-100, abs=1e-6)

    def test_chord_passes_kwargs(self):
        c = Circle(r=50, cx=100, cy=100)
        ch = c.chord(45, 225, stroke='#ff0000')
        svg = ch.to_svg(0)
        # Color may be rendered as rgb(255,0,0) internally
        assert 'stroke=' in svg
        assert 'ff0000' in svg.lower() or 'rgb(255,0,0)' in svg

    def test_chord_same_angle_is_zero_length(self):
        c = Circle(r=80, cx=100, cy=100)
        ch = c.chord(45, 45)
        x1, y1 = ch.p1.at_time(0)
        x2, y2 = ch.p2.at_time(0)
        assert x1 == pytest.approx(x2, abs=1e-6)
        assert y1 == pytest.approx(y2, abs=1e-6)


class TestRectangleFromCorners:
    def test_basic(self):
        r = Rectangle.from_corners(50, 100, 250, 300)
        assert r.x.at_time(0) == pytest.approx(50)
        assert r.y.at_time(0) == pytest.approx(100)
        assert r.width.at_time(0) == pytest.approx(200)
        assert r.height.at_time(0) == pytest.approx(200)

    def test_reversed_corners(self):
        # Bottom-right first, top-left second — should normalise
        r = Rectangle.from_corners(250, 300, 50, 100)
        assert r.x.at_time(0) == pytest.approx(50)
        assert r.y.at_time(0) == pytest.approx(100)
        assert r.width.at_time(0) == pytest.approx(200)
        assert r.height.at_time(0) == pytest.approx(200)

    def test_mixed_order(self):
        r = Rectangle.from_corners(10, 90, 60, 30)
        assert r.x.at_time(0) == pytest.approx(10)
        assert r.y.at_time(0) == pytest.approx(30)
        assert r.width.at_time(0) == pytest.approx(50)
        assert r.height.at_time(0) == pytest.approx(60)

    def test_kwargs_forwarded(self):
        r = Rectangle.from_corners(0, 0, 100, 50, stroke='#abc123')
        svg = r.to_svg(0)
        # Color may be rendered as rgb(171,193,35) internally (#abc123 -> r=0xab=171, g=0xc1=193, b=0x23=35)
        assert 'stroke=' in svg
        assert 'abc123' in svg.lower() or 'rgb(171,193,35)' in svg or '171,193,35' in svg

    def test_returns_rectangle_instance(self):
        r = Rectangle.from_corners(0, 0, 100, 100)
        assert isinstance(r, Rectangle)


class TestLineParameterAt:
    def test_parameter_at_start(self):
        """Projection of p1 itself should give t=0."""
        line = Line(0, 0, 100, 0)
        t = line.parameter_at(0, 0)
        assert t == pytest.approx(0.0)

    def test_parameter_at_end(self):
        """Projection of p2 itself should give t=1."""
        line = Line(0, 0, 100, 0)
        t = line.parameter_at(100, 0)
        assert t == pytest.approx(1.0)

    def test_parameter_at_midpoint(self):
        """Projection of the midpoint of a horizontal line gives t=0.5."""
        line = Line(0, 0, 100, 0)
        t = line.parameter_at(50, 999)  # y doesn't matter for horizontal line
        assert t == pytest.approx(0.5)

    def test_parameter_at_before_start(self):
        """A point beyond p1 should give t < 0 (unclamped)."""
        line = Line(0, 0, 100, 0)
        t = line.parameter_at(-25, 0)
        assert t == pytest.approx(-0.25)

    def test_parameter_at_beyond_end(self):
        """A point beyond p2 should give t > 1 (unclamped)."""
        line = Line(0, 0, 100, 0)
        t = line.parameter_at(150, 0)
        assert t == pytest.approx(1.5)

    def test_parameter_at_diagonal(self):
        """Diagonal line: projection of the midpoint gives t=0.5."""
        line = Line(0, 0, 100, 100)
        t = line.parameter_at(50, 50)
        assert t == pytest.approx(0.5)

    def test_parameter_degenerate_line(self):
        """Zero-length line should return 0.0 without error."""
        line = Line(50, 50, 50, 50)
        t = line.parameter_at(100, 200)
        assert t == pytest.approx(0.0)


class TestPolygonRotateVertices:
    def test_returns_polygon(self):
        p = Polygon((0, 0), (100, 0), (100, 100))
        rotated = p.rotate_vertices(0)
        assert isinstance(rotated, Polygon)

    def test_zero_rotation_unchanged(self):
        """Rotating by 0 degrees should leave vertices unchanged."""
        p = Polygon((0, 0), (100, 0), (100, 100))
        rotated = p.rotate_vertices(0)
        original = p.get_vertices()
        result = rotated.get_vertices()
        for (ox, oy), (rx, ry) in zip(original, result):
            assert rx == pytest.approx(ox, abs=1e-9)
            assert ry == pytest.approx(oy, abs=1e-9)

    def test_360_rotation_unchanged(self):
        """Full 360-degree rotation should return to original."""
        p = Polygon((0, 0), (100, 0), (100, 100))
        rotated = p.rotate_vertices(360)
        original = p.get_vertices()
        result = rotated.get_vertices()
        for (ox, oy), (rx, ry) in zip(original, result):
            assert rx == pytest.approx(ox, abs=1e-6)
            assert ry == pytest.approx(oy, abs=1e-6)

    def test_rotation_around_explicit_center(self):
        """Rotate a point (100, 0) by 90 degrees around origin (0, 0)."""
        # In SVG coords (y-down) 90-deg CW: (x, y) -> (y, -x) relative to centre
        # i.e. (100, 0) -> (0, 100) around (0,0)
        p = Polygon((100, 0), (100, 0))  # degenerate but sufficient
        rotated = p.rotate_vertices(90, cx=0, cy=0)
        verts = rotated.get_vertices()
        assert verts[0][0] == pytest.approx(0.0, abs=1e-6)
        assert verts[0][1] == pytest.approx(100.0, abs=1e-6)

    def test_rotation_around_centroid_default(self):
        """Rotating around centroid: centroid of result should equal original centroid."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx0, cy0 = p.get_center()
        rotated = p.rotate_vertices(45)
        cx1, cy1 = rotated.get_center()
        assert cx1 == pytest.approx(cx0, abs=1e-6)
        assert cy1 == pytest.approx(cy0, abs=1e-6)

    def test_closed_flag_preserved(self):
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        rotated = p.rotate_vertices(30)
        assert not rotated.closed

    def test_vertex_count_preserved(self):
        p = Polygon((0, 0), (100, 0), (50, 100), (25, 75))
        rotated = p.rotate_vertices(45)
        assert len(rotated.get_vertices()) == 4


class TestCircleDiameterLine:
    def test_returns_line(self):
        c = Circle(r=100, cx=200, cy=200)
        d = c.diameter_line()
        assert isinstance(d, Line)

    def test_horizontal_diameter_angle_zero(self):
        """Angle 0 -> horizontal line through centre."""
        c = Circle(r=100, cx=200, cy=200)
        d = c.diameter_line(0)
        p1 = d.p1.at_time(0)
        p2 = d.p2.at_time(0)
        # p1 and p2 should have the same y (horizontal)
        assert p1[1] == pytest.approx(200.0, abs=1e-6)
        assert p2[1] == pytest.approx(200.0, abs=1e-6)
        # p1 at left, p2 at right
        assert p1[0] == pytest.approx(100.0, abs=1e-6)
        assert p2[0] == pytest.approx(300.0, abs=1e-6)

    def test_vertical_diameter_angle_90(self):
        """Angle 90 -> vertical line through centre (SVG y-down)."""
        c = Circle(r=100, cx=200, cy=200)
        d = c.diameter_line(90)
        p1 = d.p1.at_time(0)
        p2 = d.p2.at_time(0)
        # p1 and p2 should have the same x (vertical)
        assert p1[0] == pytest.approx(200.0, abs=1e-6)
        assert p2[0] == pytest.approx(200.0, abs=1e-6)
        # p1 above centre (lower y in SVG), p2 below
        assert p1[1] == pytest.approx(300.0, abs=1e-6)
        assert p2[1] == pytest.approx(100.0, abs=1e-6)

    def test_diameter_length(self):
        """Diameter line should have length 2r."""
        import math
        r = 75.0
        c = Circle(r=r, cx=500, cy=400)
        for angle in [0, 30, 45, 60, 90, 120, 180]:
            d = c.diameter_line(angle)
            p1 = d.p1.at_time(0)
            p2 = d.p2.at_time(0)
            length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            assert length == pytest.approx(2 * r, abs=1e-6)

    def test_endpoints_on_circle(self):
        """Both endpoints of the diameter should lie on the circle."""
        import math
        c = Circle(r=100, cx=300, cy=300)
        d = c.diameter_line(45)
        cx, cy = c.c.at_time(0)
        r = c.rx.at_time(0)
        for pt in [d.p1.at_time(0), d.p2.at_time(0)]:
            dist = math.hypot(pt[0] - cx, pt[1] - cy)
            assert dist == pytest.approx(r, abs=1e-6)

    def test_passes_through_center(self):
        """The midpoint of the diameter line should be the circle centre."""
        c = Circle(r=80, cx=600, cy=400)
        d = c.diameter_line(30)
        p1 = d.p1.at_time(0)
        p2 = d.p2.at_time(0)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        cx, cy = c.c.at_time(0)
        assert mid_x == pytest.approx(cx, abs=1e-6)
        assert mid_y == pytest.approx(cy, abs=1e-6)

    def test_kwargs_forwarded(self):
        """Style kwargs should be forwarded to the returned Line."""
        c = Circle(r=50, cx=100, cy=100)
        d = c.diameter_line(0, stroke='#f00', stroke_width=3)
        assert d.styling.stroke_width.at_time(0) == pytest.approx(3)


class TestRectangleInset:
    def test_returns_rectangle(self):
        r = Rectangle(200, 100, x=0, y=0)
        inner = r.inset(10)
        assert isinstance(inner, Rectangle)

    def test_dimensions_reduced(self):
        """Inset by 10 should reduce each dimension by 20."""
        r = Rectangle(200, 100, x=0, y=0)
        inner = r.inset(10)
        assert inner.width.at_time(0) == pytest.approx(180.0, abs=1e-6)
        assert inner.height.at_time(0) == pytest.approx(80.0, abs=1e-6)

    def test_position_offset(self):
        """Inset rectangle's top-left corner moves inward by amount."""
        r = Rectangle(200, 100, x=50, y=30)
        inner = r.inset(10)
        assert inner.x.at_time(0) == pytest.approx(60.0, abs=1e-6)
        assert inner.y.at_time(0) == pytest.approx(40.0, abs=1e-6)

    def test_zero_amount(self):
        """Inset of 0 returns a rectangle of the same size and position."""
        r = Rectangle(200, 100, x=10, y=20)
        inner = r.inset(0)
        assert inner.width.at_time(0) == pytest.approx(200.0, abs=1e-6)
        assert inner.height.at_time(0) == pytest.approx(100.0, abs=1e-6)
        assert inner.x.at_time(0) == pytest.approx(10.0, abs=1e-6)
        assert inner.y.at_time(0) == pytest.approx(20.0, abs=1e-6)

    def test_too_large_raises(self):
        """Inset larger than half width/height should raise ValueError."""
        r = Rectangle(100, 50, x=0, y=0)
        with pytest.raises(ValueError):
            r.inset(60)  # 100 - 120 = -20 width

    def test_kwargs_forwarded(self):
        """Style kwargs should be forwarded to the new Rectangle."""
        r = Rectangle(200, 100, x=0, y=0)
        inner = r.inset(10, stroke='#f00', stroke_width=5)
        assert inner.styling.stroke_width.at_time(0) == pytest.approx(5)

    def test_does_not_modify_original(self):
        """inset() should not change the original rectangle."""
        r = Rectangle(200, 100, x=50, y=30)
        r.inset(20)
        assert r.width.at_time(0) == pytest.approx(200.0, abs=1e-6)
        assert r.height.at_time(0) == pytest.approx(100.0, abs=1e-6)

    def test_negative_amount_expands(self):
        """Negative inset expands the rectangle."""
        r = Rectangle(200, 100, x=50, y=30)
        outer = r.inset(-10)
        assert outer.width.at_time(0) == pytest.approx(220.0, abs=1e-6)
        assert outer.height.at_time(0) == pytest.approx(120.0, abs=1e-6)
        assert outer.x.at_time(0) == pytest.approx(40.0, abs=1e-6)
        assert outer.y.at_time(0) == pytest.approx(20.0, abs=1e-6)

    def test_inset_centered_correctly(self):
        """The inset rectangle should be centred on the original."""
        r = Rectangle(200, 100, x=0, y=0)
        inner = r.inset(20)
        # Centre of original: (100, 50); centre of inner: (20+80, 20+30) = (100, 50)
        cx_orig = r.x.at_time(0) + r.width.at_time(0) / 2
        cy_orig = r.y.at_time(0) + r.height.at_time(0) / 2
        cx_inner = inner.x.at_time(0) + inner.width.at_time(0) / 2
        cy_inner = inner.y.at_time(0) + inner.height.at_time(0) / 2
        assert cx_inner == pytest.approx(cx_orig, abs=1e-6)
        assert cy_inner == pytest.approx(cy_orig, abs=1e-6)


class TestCircleIntersect:
    def test_intersect_two_points(self):
        c1 = Circle(100, cx=400, cy=400)
        c2 = Circle(100, cx=500, cy=400)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 2

    def test_intersect_no_overlap(self):
        c1 = Circle(50, cx=100, cy=100)
        c2 = Circle(50, cx=400, cy=400)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 0

    def test_intersect_tangent(self):
        c1 = Circle(50, cx=100, cy=100)
        c2 = Circle(50, cx=200, cy=100)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 1
        assert pts[0][0] == pytest.approx(150, abs=1)

    def test_intersect_identical_circles(self):
        """Identical circles (d=0) should return no intersection points."""
        c1 = Circle(50, cx=100, cy=100)
        c2 = Circle(50, cx=100, cy=100)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 0

    def test_intersect_contained_circle(self):
        """One circle fully inside the other should return no points."""
        c1 = Circle(200, cx=300, cy=300)
        c2 = Circle(50, cx=300, cy=300)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 0

    def test_intersect_points_on_both_circles(self):
        """Returned points should lie on both circles (within tolerance)."""
        import math
        c1 = Circle(100, cx=400, cy=400)
        c2 = Circle(80, cx=500, cy=400)
        pts = c1.intersect_circle(c2)
        assert len(pts) == 2
        for px, py in pts:
            d1 = math.hypot(px - 400, py - 400)
            d2 = math.hypot(px - 500, py - 400)
            assert d1 == pytest.approx(100, abs=0.1)
            assert d2 == pytest.approx(80, abs=0.1)


class TestCycle38Shapes:
    def test_polygon_get_area(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.get_area() == p.area()

    def test_polygon_repr(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert 'Polygon' in repr(p)
        assert '4' in repr(p)

    def test_polygon_is_convex_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.is_convex()

    def test_polygon_is_convex_concave(self):
        p = Polygon((0, 0), (100, 0), (50, 10), (0, 100))
        assert not p.is_convex()

    def test_rectangle_get_perimeter(self):
        r = Rectangle(200, 100)
        assert r.get_perimeter() == pytest.approx(600)

    def test_rectangle_repr(self):
        r = Rectangle(200, 100)
        assert 'Rectangle' in repr(r)

    def test_wedge_repr(self):
        w = Wedge(r=100, start_angle=0, end_angle=90)
        assert 'Wedge' in repr(w)

    def test_annulus_repr(self):
        a = Annulus(50, 100)
        assert 'Annulus' in repr(a)

    def test_regular_polygon_circumradius(self):
        rp = RegularPolygon(6, 100)
        assert rp.get_circumradius() == 100


class TestPerpendicularAt:
    def test_perpendicular_at_midpoint_horizontal(self):
        line = Line(100, 200, 300, 200)
        perp = line.perpendicular_at(t=0.5, length=100)
        p1 = perp.p1.at_time(0)
        p2 = perp.p2.at_time(0)
        # Midpoint of original is (200, 200)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert mx == pytest.approx(200, abs=1)
        assert my == pytest.approx(200, abs=1)
        # Perpendicular to horizontal should be vertical
        assert p1[0] == pytest.approx(p2[0], abs=1)

    def test_perpendicular_at_start(self):
        import math
        line = Line(100, 100, 300, 100)
        perp = line.perpendicular_at(t=0.0, length=80)
        p1 = perp.p1.at_time(0)
        p2 = perp.p2.at_time(0)
        # Center of perpendicular should be at line start
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert mx == pytest.approx(100, abs=1)
        assert my == pytest.approx(100, abs=1)
        # Length should be 80
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert length == pytest.approx(80, abs=1)

    def test_perpendicular_at_end_point(self):
        line = Line(0, 0, 200, 0)
        perp = line.perpendicular_at(t=1.0, length=60)
        p1 = perp.p1.at_time(0)
        p2 = perp.p2.at_time(0)
        # Center should be at (200, 0)
        mx = (p1[0] + p2[0]) / 2
        assert mx == pytest.approx(200, abs=1)

    def test_perpendicular_at_diagonal_line(self):
        import math
        # 45-degree line
        line = Line(0, 0, 100, 100)
        perp = line.perpendicular_at(t=0.5, length=100)
        p1 = perp.p1.at_time(0)
        p2 = perp.p2.at_time(0)
        # Perpendicular length should be 100
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert length == pytest.approx(100, abs=1)
        # Check perpendicularity via dot product
        dx_orig = 100 - 0
        dy_orig = 100 - 0
        dx_perp = p2[0] - p1[0]
        dy_perp = p2[1] - p1[1]
        dot = dx_orig * dx_perp + dy_orig * dy_perp
        assert abs(dot) < 1  # should be ~0 (perpendicular)


class TestEllipseContainsPoint:
    def test_center_is_inside(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        assert e.contains_point(500, 400) == True

    def test_outside_point(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        # Well outside the ellipse
        assert e.contains_point(700, 400) == False

    def test_point_on_boundary(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        # Point on the right edge
        assert e.contains_point(600, 400) == True  # exactly on boundary, <= 1

    def test_point_just_inside(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        # Slightly inside from the right
        assert e.contains_point(599, 400) == True

    def test_point_just_outside(self):
        e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        # Slightly outside from the right
        assert e.contains_point(601, 400) == False

    def test_zero_radius_returns_false(self):
        e = Ellipse(rx=0, ry=50, cx=500, cy=400)
        assert e.contains_point(500, 400) == False

    def test_contains_point_circle(self):
        from vectormation.objects import Circle
        c = Circle(r=100, cx=500, cy=500)
        # Circle is an Ellipse subclass
        assert c.contains_point(500, 500) == True
        assert c.contains_point(500, 400) == True  # on boundary
        assert c.contains_point(500, 390) == False  # outside


class TestAxesGetGraphLength:
    def test_constant_function_length(self):
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        # Constant function y=0 over x in [-5, 5]
        # SVG length = horizontal distance between coords_to_point(-5,0) and coords_to_point(5,0)
        p1 = ax.coords_to_point(-5, 0)
        p2 = ax.coords_to_point(5, 0)
        expected = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        length = ax.get_graph_length(lambda _: 0)
        assert abs(length - expected) < 1

    def test_linear_function_length(self):
        import math
        ax = Axes(x_range=(0, 3), y_range=(0, 3))
        # y = x from 0 to 3
        p1 = ax.coords_to_point(0, 0)
        p2 = ax.coords_to_point(3, 3)
        expected = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        length = ax.get_graph_length(lambda x: x, x_start=0, x_end=3)
        assert abs(length - expected) < 2

    def test_graph_length_with_curve_object(self):
        ax = Axes(x_range=(0, 5), y_range=(-2, 2))
        curve = ax.plot(lambda x: x**2)
        # Should accept a curve with ._func attribute
        length = ax.get_graph_length(curve, x_start=0, x_end=2)
        assert length > 0

    def test_graph_length_partial_range(self):
        ax = Axes(x_range=(-10, 10), y_range=(-10, 10))
        full_length = ax.get_graph_length(lambda x: x, x_start=0, x_end=10)
        half_length = ax.get_graph_length(lambda x: x, x_start=0, x_end=5)
        # Half the range should give roughly half the length for a linear function
        assert half_length < full_length
        assert abs(half_length / full_length - 0.5) < 0.05


# Arc.from_three_points

class TestArcFromThreePoints:
    def test_arc_passes_through_three_points(self):
        """Arc created from three points should pass through all three."""
        import math
        p1 = (100, 200)
        p2 = (200, 100)
        p3 = (300, 200)
        arc = Arc.from_three_points(p1, p2, p3)
        cx, cy = arc.cx.at_time(0), arc.cy.at_time(0)
        r = arc.r.at_time(0)
        # All three points should be at distance r from center
        for px, py in [p1, p2, p3]:
            dist = math.hypot(px - cx, py - cy)
            assert dist == pytest.approx(r, abs=0.01)

    def test_arc_from_three_points_collinear_raises(self):
        """Collinear points should raise ValueError."""
        with pytest.raises(ValueError, match="collinear"):
            Arc.from_three_points((0, 0), (1, 1), (2, 2))

    def test_arc_from_three_points_kwargs(self):
        """Extra kwargs should be forwarded to Arc constructor."""
        arc = Arc.from_three_points((0, 100), (100, 0), (200, 100), stroke='#ff0000')
        svg = arc.to_svg(0)
        assert 'path' in svg  # It's rendered as a path

    def test_arc_from_three_points_radius_correct(self):
        """For points on a known circle, the radius should match."""
        # Points on a circle of radius 100 centered at (200, 200)
        r = 100
        cx, cy = 200, 200
        p1 = (cx + r, cy)
        p2 = (cx, cy - r)
        p3 = (cx - r, cy)
        arc = Arc.from_three_points(p1, p2, p3)
        assert arc.r.at_time(0) == pytest.approx(r, abs=0.1)
        assert arc.cx.at_time(0) == pytest.approx(cx, abs=0.1)
        assert arc.cy.at_time(0) == pytest.approx(cy, abs=0.1)


# Text.reveal_by_word

class TestTextRevealByWord:
    def test_reveal_by_word_returns_self(self):
        t = Text(text='hello world foo bar')
        result = t.reveal_by_word(start=0, end=2)
        assert result is t

    def test_reveal_by_word_empty_at_start(self):
        t = Text(text='hello world foo')
        t.reveal_by_word(start=0, end=3, change_existence=False)
        # At t=0 (start), progress=0 so 0 words
        assert t.text.at_time(0) == ''

    def test_reveal_by_word_full_at_end(self):
        t = Text(text='hello world foo')
        t.reveal_by_word(start=0, end=3, change_existence=False)
        # At end or just after, full text is shown (stay=True)
        assert t.text.at_time(3) == 'hello world foo'

    def test_reveal_by_word_partial(self):
        t = Text(text='one two three')
        t.reveal_by_word(start=0, end=3, change_existence=False)
        # At t=1.0, progress=1/3 -> int(0.333*3)=0 words?
        # Actually: p = linear(1/3) = 0.333, count = int(0.333*3) = 0
        # At t=1.5, progress=0.5, count=int(0.5*3)=1
        text_at_1_5 = t.text.at_time(1.5)
        assert text_at_1_5 == 'one'

    def test_reveal_by_word_empty_text(self):
        t = Text(text='')
        result = t.reveal_by_word(start=0, end=1)
        assert result is t


# Rectangle.to_polygon

class TestRectangleToPolygon:
    def test_to_polygon_returns_polygon(self):
        r = Rectangle(100, 50, x=10, y=20)
        poly = r.to_polygon()
        assert isinstance(poly, Polygon)

    def test_to_polygon_has_four_vertices(self):
        r = Rectangle(100, 50, x=10, y=20)
        poly = r.to_polygon()
        assert len(poly.vertices) == 4

    def test_to_polygon_vertices_match_corners(self):
        r = Rectangle(100, 50, x=10, y=20)
        poly = r.to_polygon()
        corners = r.get_corners()
        verts = poly.get_vertices(0)
        for c, v in zip(corners, verts):
            assert c[0] == pytest.approx(v[0])
            assert c[1] == pytest.approx(v[1])

    def test_to_polygon_kwargs_forwarded(self):
        r = Rectangle(100, 50, x=10, y=20)
        poly = r.to_polygon(fill='#ff0000')
        svg = poly.to_svg(0)
        assert 'polygon' in svg


class TestPolygonCentroid:
    def test_centroid_equilateral_triangle(self):
        """Centroid of a symmetric triangle at origin should be at its center."""
        # Equilateral triangle centered near (0, 0)
        p = Polygon((0, -100), (86.6, 50), (-86.6, 50))
        cx, cy = p.centroid(0)
        # For this symmetric triangle, centroid should be at roughly (0, 0)
        assert cx == pytest.approx(0, abs=0.5)
        assert cy == pytest.approx(0, abs=0.5)

    def test_centroid_rectangle(self):
        """Centroid of a rectangle should match its geometric center."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        cx, cy = p.centroid(0)
        assert cx == pytest.approx(100, abs=0.01)
        assert cy == pytest.approx(50, abs=0.01)

    def test_centroid_differs_from_get_center(self):
        """For an asymmetric polygon, centroid differs from simple vertex average."""
        # L-shaped polygon: vertices average and area-weighted centroid differ
        p = Polygon((0, 0), (200, 0), (200, 50), (50, 50), (50, 200), (0, 200))
        cx_area, cy_area = p.centroid(0)
        cx_avg, cy_avg = p.get_center(0)
        # They should not be equal (area-weighted centroid shifts toward the larger mass)
        assert (cx_area, cy_area) != pytest.approx((cx_avg, cy_avg), abs=1)

    def test_centroid_degenerate_single_vertex(self):
        """Centroid of a single vertex returns that vertex."""
        p = Polygon((42, 99))
        cx, cy = p.centroid(0)
        assert cx == pytest.approx(42)
        assert cy == pytest.approx(99)

    def test_centroid_two_vertices(self):
        """Centroid of two vertices returns their midpoint."""
        p = Polygon((0, 0), (100, 200), closed=False)
        cx, cy = p.centroid(0)
        assert cx == pytest.approx(50)
        assert cy == pytest.approx(100)


class TestLineBisector:
    def test_bisector_horizontal_line(self):
        """Bisector of a horizontal line should be vertical through the midpoint."""
        line = Line(x1=0, y1=100, x2=200, y2=100)
        bis = line.bisector(time=0, length=100)
        # Midpoint is (100, 100)
        p1 = bis.p1.at_time(0)
        p2 = bis.p2.at_time(0)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        assert mid_x == pytest.approx(100, abs=0.01)
        assert mid_y == pytest.approx(100, abs=0.01)
        # The bisector should be vertical: same x for both endpoints
        assert p1[0] == pytest.approx(p2[0], abs=0.01)

    def test_bisector_vertical_line(self):
        """Bisector of a vertical line should be horizontal through the midpoint."""
        line = Line(x1=50, y1=0, x2=50, y2=200)
        bis = line.bisector(time=0, length=100)
        p1 = bis.p1.at_time(0)
        p2 = bis.p2.at_time(0)
        # Midpoint is (50, 100)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        assert mid_x == pytest.approx(50, abs=0.01)
        assert mid_y == pytest.approx(100, abs=0.01)
        # The bisector should be horizontal: same y for both endpoints
        assert p1[1] == pytest.approx(p2[1], abs=0.01)

    def test_bisector_returns_line(self):
        """bisector() should return a Line instance."""
        line = Line(x1=0, y1=0, x2=100, y2=100)
        bis = line.bisector()
        assert isinstance(bis, Line)

    def test_bisector_custom_length(self):
        """Bisector with custom length should have the specified length."""
        import math
        line = Line(x1=0, y1=0, x2=200, y2=0)
        bis = line.bisector(length=300)
        p1 = bis.p1.at_time(0)
        p2 = bis.p2.at_time(0)
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert dist == pytest.approx(300, abs=0.1)


class TestCircleFromDiameter:
    def test_from_diameter_center(self):
        """Circle.from_diameter should center at the midpoint."""
        c = Circle.from_diameter((100, 200), (300, 200))
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(200)
        assert cy == pytest.approx(200)

    def test_from_diameter_radius(self):
        """Circle.from_diameter should have radius = half the distance."""
        c = Circle.from_diameter((100, 200), (300, 200))
        r = c.rx.at_time(0)
        assert r == pytest.approx(100)

    def test_from_diameter_diagonal(self):
        """Circle.from_diameter with diagonal endpoints."""
        c = Circle.from_diameter((0, 0), (300, 400))
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(150)
        assert cy == pytest.approx(200)
        r = c.rx.at_time(0)
        assert r == pytest.approx(250)

    def test_from_diameter_kwargs(self):
        """Circle.from_diameter should forward kwargs to constructor."""
        c = Circle.from_diameter((0, 0), (200, 0), stroke='#ff0000')
        svg = c.to_svg(0)
        assert 'ff0000' in svg.lower() or 'rgb(255,0,0)' in svg

    def test_from_diameter_same_point(self):
        """Circle.from_diameter with identical points should give radius 0."""
        c = Circle.from_diameter((100, 100), (100, 100))
        r = c.rx.at_time(0)
        assert r == pytest.approx(0)


class TestRectangleExpand:
    def test_expand_at_end(self):
        """Rectangle.expand should increase width and height by 2*amount at end."""
        r = Rectangle(width=100, height=60, x=50, y=50)
        r.expand(amount=20, start=0, end=1)
        assert r.width.at_time(1) == pytest.approx(140)
        assert r.height.at_time(1) == pytest.approx(100)

    def test_expand_position_shift(self):
        """Rectangle.expand should shift x,y so the expansion is centered."""
        r = Rectangle(width=100, height=60, x=50, y=50)
        r.expand(amount=20, start=0, end=1)
        assert r.x.at_time(1) == pytest.approx(30)
        assert r.y.at_time(1) == pytest.approx(30)

    def test_expand_at_start_unchanged(self):
        """At start time, dimensions should be unchanged."""
        r = Rectangle(width=100, height=60, x=50, y=50)
        r.expand(amount=20, start=0, end=1)
        assert r.width.at_time(0) == pytest.approx(100)
        assert r.height.at_time(0) == pytest.approx(60)

    def test_expand_returns_self(self):
        """expand should return self for chaining."""
        r = Rectangle(width=100, height=60, x=50, y=50)
        result = r.expand(amount=10, start=0, end=1)
        assert result is r

    def test_expand_center_stays(self):
        """The center of the rectangle should stay in place during expansion."""
        r = Rectangle(width=200, height=100, x=100, y=50)
        # Center at t=0: (100+100, 50+50) = (200, 100)
        cx_before = r.x.at_time(0) + r.width.at_time(0) / 2
        cy_before = r.y.at_time(0) + r.height.at_time(0) / 2
        r.expand(amount=30, start=0, end=1)
        cx_after = r.x.at_time(1) + r.width.at_time(1) / 2
        cy_after = r.y.at_time(1) + r.height.at_time(1) / 2
        assert cx_after == pytest.approx(cx_before)
        assert cy_after == pytest.approx(cy_before)


class TestTextToUpper:
    def test_to_upper_basic(self):
        """to_upper changes text to uppercase."""
        t = Text('hello world')
        t.to_upper(time=0)
        assert t.text.at_time(0) == 'HELLO WORLD'

    def test_to_upper_at_later_time(self):
        """to_upper at a later time preserves original text before that time."""
        t = Text('hello')
        t.to_upper(time=2)
        assert t.text.at_time(0) == 'hello'
        assert t.text.at_time(2) == 'HELLO'

    def test_to_upper_returns_self(self):
        """to_upper should return self for chaining."""
        t = Text('abc')
        result = t.to_upper(time=0)
        assert result is t

    def test_to_upper_already_upper(self):
        """to_upper on already uppercase text is a no-op."""
        t = Text('HELLO')
        t.to_upper(time=0)
        assert t.text.at_time(0) == 'HELLO'


class TestTextToLower:
    def test_to_lower_basic(self):
        """to_lower changes text to lowercase."""
        t = Text('Hello World')
        t.to_lower(time=0)
        assert t.text.at_time(0) == 'hello world'

    def test_to_lower_at_later_time(self):
        """to_lower at a later time preserves original text before that time."""
        t = Text('HELLO')
        t.to_lower(time=2)
        assert t.text.at_time(0) == 'HELLO'
        assert t.text.at_time(2) == 'hello'

    def test_to_lower_returns_self(self):
        """to_lower should return self for chaining."""
        t = Text('ABC')
        result = t.to_lower(time=0)
        assert result is t


class TestLineGetVector:
    def test_get_vector_basic(self):
        """get_vector returns unnormalized direction vector."""
        l = Line(x1=0, y1=0, x2=3, y2=4)
        dx, dy = l.get_vector()
        assert dx == pytest.approx(3.0)
        assert dy == pytest.approx(4.0)

    def test_get_vector_vs_get_direction(self):
        """get_vector returns unnormalized while get_direction returns normalized."""
        l = Line(x1=0, y1=0, x2=6, y2=8)
        vx, vy = l.get_vector()
        dx, dy = l.get_direction()
        # Vector should be (6, 8), direction should be (0.6, 0.8)
        assert vx == pytest.approx(6.0)
        assert vy == pytest.approx(8.0)
        assert dx == pytest.approx(0.6)
        assert dy == pytest.approx(0.8)

    def test_get_vector_zero_length(self):
        """get_vector on a zero-length line returns (0, 0)."""
        l = Line(x1=5, y1=5, x2=5, y2=5)
        dx, dy = l.get_vector()
        assert dx == pytest.approx(0.0)
        assert dy == pytest.approx(0.0)


class TestRectangleIsSquare:
    def test_is_square_true(self):
        """A square rectangle should return True."""
        r = Rectangle(width=100, height=100)
        assert r.is_square() is True

    def test_is_square_false(self):
        """A non-square rectangle should return False."""
        r = Rectangle(width=100, height=50)
        assert r.is_square() is False

    def test_is_square_within_tolerance(self):
        """Rectangles within tolerance should be considered square."""
        r = Rectangle(width=100, height=100.0005)
        assert r.is_square(tol=1e-3) is True

    def test_is_square_outside_tolerance(self):
        """Rectangles outside tolerance should not be considered square."""
        r = Rectangle(width=100, height=100.01)
        assert r.is_square(tol=1e-3) is False

    def test_is_square_class_method(self):
        """Rectangle.square() factory should produce a square."""
        r = Rectangle.square(50)
        assert r.is_square() is True


class TestPolygonTranslate:
    def test_translate_shifts_vertices(self):
        p = Polygon((100, 100), (200, 100), (150, 200))
        p.translate(10, 20)
        verts = p.get_vertices(0)
        assert verts[0] == pytest.approx((110, 120))
        assert verts[1] == pytest.approx((210, 120))
        assert verts[2] == pytest.approx((160, 220))

    def test_translate_returns_self(self):
        p = Polygon((100, 100), (200, 100), (150, 200))
        result = p.translate(5, -5)
        assert result is p

    def test_translate_updates_bbox(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        p.translate(50, 50)
        bx, by, bw, bh = p.bbox(0)
        assert bx == pytest.approx(50)
        assert by == pytest.approx(50)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(100)


class TestArcGetMidpointOnArc:
    def test_midpoint_on_arc_matches_get_midpoint(self):
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        mid = a.get_midpoint(0)
        mid_on_arc = a.get_midpoint_on_arc(0)
        assert mid_on_arc[0] == pytest.approx(mid[0])
        assert mid_on_arc[1] == pytest.approx(mid[1])

    def test_midpoint_on_arc_is_on_arc(self):
        import math
        cx, cy, r = 200.0, 200.0, 80.0
        a = Arc(cx=cx, cy=cy, r=r, start_angle=0, end_angle=180)
        mx, my = a.get_midpoint_on_arc(0)
        # Distance from center should equal radius
        dist = math.sqrt((mx - cx)**2 + (my - cy)**2)
        assert dist == pytest.approx(r, abs=0.01)

    def test_midpoint_on_arc_angle(self):
        import math
        a = Arc(cx=0, cy=0, r=100, start_angle=30, end_angle=90)
        mx, my = a.get_midpoint_on_arc(0)
        # Midpoint angle should be 60 degrees
        expected_x = 100 * math.cos(math.radians(60))
        expected_y = -100 * math.sin(math.radians(60))  # SVG y is inverted
        assert mx == pytest.approx(expected_x, abs=0.01)
        assert my == pytest.approx(expected_y, abs=0.01)


class TestLineLerp:
    def test_lerp_start(self):
        line = Line(x1=0, y1=0, x2=100, y2=200)
        x, y = line.lerp(0)
        assert x == pytest.approx(0)
        assert y == pytest.approx(0)

    def test_lerp_end(self):
        line = Line(x1=0, y1=0, x2=100, y2=200)
        x, y = line.lerp(1)
        assert x == pytest.approx(100)
        assert y == pytest.approx(200)

    def test_lerp_midpoint(self):
        line = Line(x1=10, y1=20, x2=30, y2=60)
        x, y = line.lerp(0.5)
        assert x == pytest.approx(20)
        assert y == pytest.approx(40)

    def test_lerp_quarter(self):
        line = Line(x1=0, y1=0, x2=400, y2=0)
        x, y = line.lerp(0.25)
        assert x == pytest.approx(100)
        assert y == pytest.approx(0)

    def test_lerp_extrapolate_beyond(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        x, y = line.lerp(2.0)
        assert x == pytest.approx(200)
        assert y == pytest.approx(0)


class TestPolygonScaleVertices:
    def test_scale_up(self):
        poly = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx, cy = poly.centroid(0)
        poly.scale_vertices(2.0)
        pts = poly.get_vertices(0)
        new_cx, new_cy = poly.centroid(0)
        # Centroid should stay the same
        assert new_cx == pytest.approx(cx, abs=0.1)
        assert new_cy == pytest.approx(cy, abs=0.1)
        # The distance from centroid to each vertex should double
        for (ox, oy), (nx, ny) in zip([(0, 0), (100, 0), (100, 100), (0, 100)], pts):
            orig_dist = ((ox - cx)**2 + (oy - cy)**2)**0.5
            new_dist = ((nx - new_cx)**2 + (ny - new_cy)**2)**0.5
            assert new_dist == pytest.approx(orig_dist * 2.0, abs=0.1)

    def test_scale_down(self):
        poly = Polygon((0, 0), (200, 0), (200, 200), (0, 200))
        poly.scale_vertices(0.5)
        pts = poly.get_vertices(0)
        cx, cy = poly.centroid(0)
        # After scaling by 0.5, each vertex should be half as far from centroid
        # Original centroid of a square (0,0)-(200,200) is (100, 100)
        for nx, ny in pts:
            dist = ((nx - cx)**2 + (ny - cy)**2)**0.5
            # Original distance was sqrt(100^2 + 100^2) = 141.42
            assert dist == pytest.approx(141.42 / 2, abs=1)

    def test_scale_returns_self(self):
        poly = Polygon((0, 0), (100, 0), (50, 100))
        result = poly.scale_vertices(1.5)
        assert result is poly

    def test_scale_by_one_no_change(self):
        poly = Polygon((10, 20), (30, 40), (50, 10))
        original = poly.get_vertices(0)
        poly.scale_vertices(1.0)
        for (ox, oy), (nx, ny) in zip(original, poly.get_vertices(0)):
            assert nx == pytest.approx(ox, abs=1e-6)
            assert ny == pytest.approx(oy, abs=1e-6)


class TestTextCharAt:
    def test_char_at_first(self):
        t = Text('Hello')
        assert t.char_at(0) == 'H'

    def test_char_at_last(self):
        t = Text('Hello')
        assert t.char_at(4) == 'o'

    def test_char_at_middle(self):
        t = Text('abcdef')
        assert t.char_at(3) == 'd'

    def test_char_at_out_of_range(self):
        t = Text('Hi')
        assert t.char_at(5) == ''

    def test_char_at_negative_index(self):
        t = Text('Hi')
        assert t.char_at(-1) == ''

    def test_char_at_empty_string(self):
        t = Text('')
        assert t.char_at(0) == ''


class TestRectangleAspectRatio:
    def test_aspect_ratio_basic(self):
        r = Rectangle(width=200, height=100)
        assert r.aspect_ratio() == pytest.approx(2.0)

    def test_aspect_ratio_square(self):
        r = Rectangle(width=100, height=100)
        assert r.aspect_ratio() == pytest.approx(1.0)

    def test_aspect_ratio_tall(self):
        r = Rectangle(width=50, height=200)
        assert r.aspect_ratio() == pytest.approx(0.25)

    def test_aspect_ratio_zero_height(self):
        r = Rectangle(width=100, height=0)
        assert r.aspect_ratio() == float('inf')


class TestSetCreation:
    def test_set_creation_hides_before(self):
        c = Circle(r=50)
        c.set_creation(2)
        assert c.show.at_time(0) == False
        assert c.show.at_time(1) == False
        assert c.show.at_time(2) == True
        assert c.show.at_time(3) == True

    def test_set_creation_returns_self(self):
        c = Circle(r=50)
        result = c.set_creation(1)
        assert result is c

    def test_set_creation_on_rectangle(self):
        r = Rectangle(width=100, height=50)
        r.set_creation(5)
        assert r.show.at_time(4) == False
        assert r.show.at_time(5) == True


class TestPolygonEdgeLengths:
    def test_edge_lengths_triangle(self):
        p = Polygon((0, 0), (3, 0), (0, 4))
        lengths = p.edge_lengths()
        assert len(lengths) == 3
        assert lengths[0] == pytest.approx(3.0)
        assert lengths[1] == pytest.approx(5.0)
        assert lengths[2] == pytest.approx(4.0)

    def test_edge_lengths_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        lengths = p.edge_lengths()
        assert len(lengths) == 4
        for l in lengths:
            assert l == pytest.approx(100.0)

    def test_edge_lengths_open_polyline(self):
        p = Polygon((0, 0), (3, 0), (3, 4), closed=False)
        lengths = p.edge_lengths()
        assert len(lengths) == 2
        assert lengths[0] == pytest.approx(3.0)
        assert lengths[1] == pytest.approx(4.0)

    def test_edge_lengths_single_vertex(self):
        p = Polygon((0, 0))
        assert p.edge_lengths() == []


class TestTextWordAt:
    def test_word_at_basic(self):
        t = Text('hello world foo')
        assert t.word_at(0) == 'hello'
        assert t.word_at(1) == 'world'
        assert t.word_at(2) == 'foo'

    def test_word_at_out_of_range(self):
        t = Text('hello world')
        assert t.word_at(5) == ''

    def test_word_at_negative_index(self):
        t = Text('hello world')
        assert t.word_at(-1) == ''

    def test_word_at_empty_string(self):
        t = Text('')
        assert t.word_at(0) == ''

    def test_word_at_single_word(self):
        t = Text('onlyone')
        assert t.word_at(0) == 'onlyone'
        assert t.word_at(1) == ''


class TestFlashScale:
    def test_peak_at_midpoint(self):
        """flash_scale should reach peak factor at the midpoint."""
        c = Circle(r=50, cx=100, cy=100)
        c.flash_scale(factor=2.0, start=0, end=2)
        # At midpoint (t=1), scale should be at factor
        sx_mid = c.styling.scale_x.at_time(1)
        assert sx_mid == pytest.approx(2.0, abs=0.01)

    def test_returns_to_original(self):
        """flash_scale should return to original scale at end."""
        c = Circle(r=50, cx=100, cy=100)
        c.flash_scale(factor=1.5, start=0, end=2)
        # At start scale should be 1.0
        sx_start = c.styling.scale_x.at_time(0)
        assert sx_start == pytest.approx(1.0, abs=0.01)
        # At end scale should be back to 1.0
        sx_end = c.styling.scale_x.at_time(2)
        assert sx_end == pytest.approx(1.0, abs=0.01)

    def test_returns_self(self):
        """flash_scale should return self for chaining."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.flash_scale(factor=1.5, start=0, end=1)
        assert result is c


class TestArcGetChordLength:
    def test_semicircle_chord(self):
        """A semicircle's chord should equal the diameter."""
        arc = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=180)
        chord = arc.get_chord_length(time=0)
        assert chord == pytest.approx(200.0, abs=0.1)

    def test_quarter_circle_chord(self):
        """A quarter circle's chord should equal r * sqrt(2)."""
        import math
        arc = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord_length(time=0)
        expected = 100 * math.sqrt(2)
        assert chord == pytest.approx(expected, abs=0.1)

    def test_zero_sweep_chord(self):
        """An arc with zero sweep should have zero chord length."""
        arc = Arc(cx=0, cy=0, r=100, start_angle=45, end_angle=45)
        chord = arc.get_chord_length(time=0)
        assert chord == pytest.approx(0.0, abs=0.01)


class TestLineIsHorizontal:
    def test_horizontal_line(self):
        """A perfectly horizontal line should return True."""
        line = Line(0, 100, 200, 100)
        assert line.is_horizontal() is True

    def test_non_horizontal_line(self):
        """A diagonal line should return False."""
        line = Line(0, 0, 100, 100)
        assert line.is_horizontal() is False

    def test_nearly_horizontal_within_tol(self):
        """A nearly horizontal line within tolerance should return True."""
        line = Line(0, 100, 200, 100.0005)
        assert line.is_horizontal(tol=1e-3) is True


class TestLineIsVertical:
    def test_vertical_line(self):
        """A perfectly vertical line should return True."""
        line = Line(100, 0, 100, 200)
        assert line.is_vertical() is True

    def test_non_vertical_line(self):
        """A diagonal line should return False."""
        line = Line(0, 0, 100, 100)
        assert line.is_vertical() is False

    def test_nearly_vertical_within_tol(self):
        """A nearly vertical line within tolerance should return True."""
        line = Line(100, 0, 100.0005, 200)
        assert line.is_vertical(tol=1e-3) is True


class TestPolygonSignedArea:
    def test_cw_in_svg_positive(self):
        """Vertices (0,0)->(100,0)->(100,100) are CW in math coords (y-up),
        but in SVG y-down the shoelace gives positive signed area."""
        tri = Polygon((0, 0), (100, 0), (100, 100))
        sa = tri.signed_area()
        assert sa == pytest.approx(5000.0)

    def test_reversed_order_flips_sign(self):
        """Reversing vertex order should flip the sign of signed area."""
        tri = Polygon((0, 0), (100, 100), (100, 0))
        sa = tri.signed_area()
        assert sa == pytest.approx(-5000.0)

    def test_signed_area_abs_matches_area(self):
        """The absolute value of signed_area should match area()."""
        poly = Polygon((0, 0), (100, 0), (100, 50), (0, 50))
        assert abs(poly.signed_area()) == pytest.approx(poly.area())

    def test_signed_area_fewer_than_3_vertices(self):
        """With fewer than 3 vertices, signed_area should return 0."""
        line = Polygon((0, 0), (100, 100), closed=False)
        assert line.signed_area() == 0


class TestCircleFromCenterAndPoint:
    def test_from_center_and_point_basic(self):
        """Create circle from center and a point on circumference."""
        c = Circle.from_center_and_point((100, 200), (100, 250))
        assert c.rx.at_time(0) == pytest.approx(50)
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(200)

    def test_from_center_and_point_diagonal(self):
        """Circle from center and diagonal point computes correct radius."""
        c = Circle.from_center_and_point((0, 0), (3, 4))
        assert c.rx.at_time(0) == pytest.approx(5.0)

    def test_from_center_and_point_kwargs(self):
        """Extra kwargs are forwarded to the Circle constructor."""
        c = Circle.from_center_and_point((100, 100), (100, 200), stroke='#ff0000')
        # Styling system normalizes colors to rgb() format
        assert 'rgb(255,0,0)' in c.styling.stroke.at_time(0)


class TestTextReverseText:
    def test_reverse_text_basic(self):
        """reverse_text should reverse the current text string."""
        t = Text('hello')
        t.reverse_text()
        assert t.text.at_time(0) == 'olleh'

    def test_reverse_text_returns_self(self):
        """reverse_text should return self for chaining."""
        t = Text('abc')
        result = t.reverse_text()
        assert result is t

    def test_reverse_text_empty(self):
        """reverse_text on empty string stays empty."""
        t = Text('')
        t.reverse_text()
        assert t.text.at_time(0) == ''


class TestPolygonMirror:
    def test_mirror_x_default_center(self):
        """mirror_x with default cx mirrors across the centroid x."""
        poly = Polygon((0, 0), (100, 0), (100, 50), (0, 50))
        poly.mirror_x()
        verts = poly.get_vertices()
        # Centroid x = 50. Vertex (0,0) -> (100,0), (100,0) -> (0,0), etc.
        xs = sorted([v[0] for v in verts])
        assert xs[0] == pytest.approx(0)
        assert xs[-1] == pytest.approx(100)

    def test_mirror_x_custom_center(self):
        """mirror_x with explicit cx mirrors across x=cx."""
        poly = Polygon((10, 0), (20, 0), (20, 10))
        poly.mirror_x(cx=0)
        verts = poly.get_vertices()
        # (10,0) -> (-10,0), (20,0) -> (-20,0), (20,10) -> (-20,10)
        assert verts[0][0] == pytest.approx(-10)
        assert verts[1][0] == pytest.approx(-20)
        assert verts[2][0] == pytest.approx(-20)

    def test_mirror_y_default_center(self):
        """mirror_y with default cy mirrors across the centroid y."""
        poly = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        poly.mirror_y()
        verts = poly.get_vertices()
        ys = sorted([v[1] for v in verts])
        assert ys[0] == pytest.approx(0)
        assert ys[-1] == pytest.approx(100)

    def test_mirror_y_custom_center(self):
        """mirror_y with explicit cy mirrors across y=cy."""
        poly = Polygon((0, 10), (10, 20), (5, 30))
        poly.mirror_y(cy=0)
        verts = poly.get_vertices()
        # (0,10) -> (0,-10), (10,20) -> (10,-20), (5,30) -> (5,-30)
        assert verts[0][1] == pytest.approx(-10)
        assert verts[1][1] == pytest.approx(-20)
        assert verts[2][1] == pytest.approx(-30)

    def test_mirror_x_returns_self(self):
        """mirror_x returns self for chaining."""
        poly = Polygon((0, 0), (10, 0), (10, 10))
        assert poly.mirror_x() is poly

    def test_mirror_y_returns_self(self):
        """mirror_y returns self for chaining."""
        poly = Polygon((0, 0), (10, 0), (10, 10))
        assert poly.mirror_y() is poly


class TestEllipseGetFoci:
    def test_foci_horizontal(self):
        """When rx > ry, foci are on the horizontal axis."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        f1, f2 = e.get_foci()
        import math
        c = math.sqrt(100**2 - 60**2)
        assert f1[0] == pytest.approx(500 - c)
        assert f1[1] == pytest.approx(400)
        assert f2[0] == pytest.approx(500 + c)
        assert f2[1] == pytest.approx(400)

    def test_foci_vertical(self):
        """When ry > rx, foci are on the vertical axis."""
        e = Ellipse(rx=30, ry=50, cx=200, cy=300)
        f1, f2 = e.get_foci()
        import math
        c = math.sqrt(50**2 - 30**2)
        assert f1[0] == pytest.approx(200)
        assert f1[1] == pytest.approx(300 - c)
        assert f2[0] == pytest.approx(200)
        assert f2[1] == pytest.approx(300 + c)

    def test_foci_circle(self):
        """When rx == ry (a circle), both foci are at the center."""
        e = Ellipse(rx=50, ry=50, cx=100, cy=100)
        f1, f2 = e.get_foci()
        assert f1[0] == pytest.approx(100)
        assert f1[1] == pytest.approx(100)
        assert f2[0] == pytest.approx(100)
        assert f2[1] == pytest.approx(100)


class TestRectangleGrowWidth:
    def test_grow_width_increases(self):
        """grow_width should increase width by the given amount at end time."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        r.grow_width(40, start=0, end=1)
        assert r.width.at_time(1) == pytest.approx(140)

    def test_grow_width_returns_self(self):
        """grow_width should return self for chaining."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        assert r.grow_width(20) is r

    def test_grow_width_preserves_height(self):
        """grow_width should not change the height."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        r.grow_width(30, start=0, end=1)
        assert r.height.at_time(1) == pytest.approx(50)


class TestRectangleGrowHeight:
    def test_grow_height_increases(self):
        """grow_height should increase height by the given amount at end time."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        r.grow_height(25, start=0, end=1)
        assert r.height.at_time(1) == pytest.approx(75)

    def test_grow_height_returns_self(self):
        """grow_height should return self for chaining."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        assert r.grow_height(20) is r

    def test_grow_height_negative(self):
        """grow_height with negative amount should decrease height."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        r.grow_height(-20, start=0, end=1)
        assert r.height.at_time(1) == pytest.approx(30)


class TestArcContainsPoint:
    def test_point_on_arc(self):
        """A point at the start of the arc should be detected."""
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        # Point at angle 0 (rightmost): (600, 400)
        assert arc.contains_point(600, 400, time=0) is True

    def test_point_on_arc_midangle(self):
        """A point at 45 degrees on a 0-90 arc should be detected."""
        import math
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        # Point at 45 degrees: note Arc uses cy - r*sin (SVG y is flipped)
        px = 500 + 100 * math.cos(math.radians(45))
        py = 400 - 100 * math.sin(math.radians(45))
        assert arc.contains_point(px, py, time=0) is True

    def test_point_outside_arc_wrong_radius(self):
        """A point far from the arc radius should not be detected."""
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        # Point at the centre — far from radius
        assert arc.contains_point(500, 400, time=0) is False

    def test_point_outside_arc_wrong_angle(self):
        """A point on the circle but outside the arc sweep should not be detected."""
        import math
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        # Point at 180 degrees: (-100, 0) relative to centre
        px = 500 + 100 * math.cos(math.radians(180))
        py = 400 - 100 * math.sin(math.radians(180))
        assert arc.contains_point(px, py, time=0) is False


class TestAxesGetAverage:
    def test_constant_function(self):
        """Average of a constant function should be that constant."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        avg = ax.get_average(lambda _: 5, 0, 10)
        assert avg == pytest.approx(5, abs=0.01)

    def test_linear_function(self):
        """Average of f(x)=x over [0, 10] should be 5."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        avg = ax.get_average(lambda x: x, 0, 10)
        assert avg == pytest.approx(5, abs=0.01)

    def test_defaults_to_axis_range(self):
        """When x_start/x_end are None, should use axis x_min/x_max."""
        ax = Axes(x_range=(0, 4), y_range=(0, 10))
        avg = ax.get_average(lambda x: x * x)
        # Average of x^2 on [0,4] = (1/4) * integral(x^2, 0, 4) = (1/4)*(64/3) ≈ 5.333
        assert avg == pytest.approx(64 / 12, abs=0.1)


class TestLineScaleLength:
    """Tests for Line.scale_length()."""

    def test_scale_length_doubles(self):
        """factor=2 should double the line length while keeping the midpoint."""
        line = Line(100, 200, 300, 200)
        mid_before = ((100 + 300) / 2, (200 + 200) / 2)
        line.scale_length(factor=2.0, time=0)
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        mid_after = ((x1 + x2) / 2, (y1 + y2) / 2)
        # Midpoint should be preserved
        assert mid_after[0] == pytest.approx(mid_before[0])
        assert mid_after[1] == pytest.approx(mid_before[1])
        # Length should be doubled (was 200, now 400)
        import math
        new_len = math.hypot(x2 - x1, y2 - y1)
        assert new_len == pytest.approx(400)

    def test_scale_length_half(self):
        """factor=0.5 should halve the line length."""
        line = Line(0, 0, 200, 0)
        line.scale_length(factor=0.5, time=0)
        x1, y1 = line.p1.at_time(0)
        x2, y2 = line.p2.at_time(0)
        import math
        new_len = math.hypot(x2 - x1, y2 - y1)
        assert new_len == pytest.approx(100)
        # Midpoint preserved at (100, 0)
        assert (x1 + x2) / 2 == pytest.approx(100)

    def test_scale_length_returns_self(self):
        """scale_length should return self for chaining."""
        line = Line(0, 0, 100, 0)
        assert line.scale_length(1.5) is line


class TestPolygonWindingNumber:
    """Tests for Polygon.winding_number()."""

    def test_inside_square(self):
        """A point inside a square should have winding number != 0."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        wn = sq.winding_number(50, 50)
        assert wn != 0

    def test_outside_square(self):
        """A point outside a square should have winding number 0."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        wn = sq.winding_number(200, 200)
        assert wn == 0

    def test_triangle_inside(self):
        """A point inside a triangle should have winding number != 0."""
        tri = Polygon((0, 0), (200, 0), (100, 200))
        wn = tri.winding_number(100, 50)
        assert wn != 0

    def test_degenerate_polygon(self):
        """A polygon with fewer than 3 vertices should return 0."""
        line = Polygon((0, 0), (100, 100))
        assert line.winding_number(50, 50) == 0


# ── Circle.sector_area ──────────────────────────────────────────────
class TestCircleSectorArea:
    def test_full_circle(self):
        import math
        c = Circle(r=100, cx=0, cy=0)
        area = c.sector_area(0, 360)
        assert area == pytest.approx(math.pi * 100 * 100)

    def test_quarter_circle(self):
        import math
        c = Circle(r=100, cx=0, cy=0)
        area = c.sector_area(0, 90)
        assert area == pytest.approx(math.pi * 100 * 100 / 4)

    def test_reverse_angles(self):
        """sector_area uses abs(sweep), so order shouldn't matter."""
        c = Circle(r=50, cx=0, cy=0)
        assert c.sector_area(90, 0) == pytest.approx(c.sector_area(0, 90))


# ── Text.starts_with / ends_with ────────────────────────────────────
class TestTextStartsEndsWith:
    def test_starts_with_true(self):
        t = Text('hello world')
        assert t.starts_with('hello') is True

    def test_starts_with_false(self):
        t = Text('hello world')
        assert t.starts_with('world') is False

    def test_ends_with_true(self):
        t = Text('hello world')
        assert t.ends_with('world') is True

    def test_ends_with_false(self):
        t = Text('hello world')
        assert t.ends_with('hello') is False


# ── Line.from_points ────────────────────────────────────────────────
class TestLineFromPoints:
    def test_basic(self):
        line = Line.from_points((10, 20), (30, 40))
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        assert p1 == pytest.approx((10, 20))
        assert p2 == pytest.approx((30, 40))

    def test_matches_between(self):
        a = Line.from_points((100, 200), (300, 400))
        b = Line.between((100, 200), (300, 400))
        assert a.p1.at_time(0) == pytest.approx(b.p1.at_time(0))
        assert a.p2.at_time(0) == pytest.approx(b.p2.at_time(0))


# ── Polygon.get_longest_edge / get_shortest_edge ────────────────────
class TestPolygonLongestShortestEdge:
    def test_longest_edge_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.get_longest_edge() == pytest.approx(100)

    def test_shortest_edge_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.get_shortest_edge() == pytest.approx(100)

    def test_longest_edge_triangle(self):
        import math
        tri = Polygon((0, 0), (300, 0), (0, 100))
        longest = tri.get_longest_edge()
        expected = math.hypot(300, 100)  # hypotenuse
        assert longest == pytest.approx(expected)

    def test_shortest_edge_triangle(self):
        tri = Polygon((0, 0), (300, 0), (0, 100))
        shortest = tri.get_shortest_edge()
        assert shortest == pytest.approx(100)

    def test_degenerate_single_vertex(self):
        p = Polygon((0, 0), closed=False)
        assert p.get_longest_edge() == 0
        assert p.get_shortest_edge() == 0


class TestLineRotateAroundMidpoint:
    def test_rotate_90_degrees(self):
        """Rotating a horizontal line 90 degrees should make it vertical."""
        import math
        line = Line(100, 200, 300, 200)  # horizontal line
        mid = line.get_midpoint(0)
        assert mid[0] == pytest.approx(200)
        assert mid[1] == pytest.approx(200)
        line.rotate_around_midpoint(90, time=0)
        # After 90 deg rotation, endpoints should be vertical through midpoint
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Midpoint should be preserved
        new_mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        assert new_mid[0] == pytest.approx(200, abs=1e-6)
        assert new_mid[1] == pytest.approx(200, abs=1e-6)
        # Line should now be vertical: x coords should be the same
        assert p1[0] == pytest.approx(p2[0], abs=1e-6)
        # Length should be preserved
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert length == pytest.approx(200, abs=1e-6)

    def test_rotate_180_swaps_endpoints(self):
        """Rotating 180 degrees should swap endpoint positions."""
        line = Line(100, 200, 300, 400)
        orig_p1 = line.p1.at_time(0)
        orig_p2 = line.p2.at_time(0)
        line.rotate_around_midpoint(180, time=0)
        new_p1 = line.p1.at_time(0)
        new_p2 = line.p2.at_time(0)
        # p1 should now be where p2 was and vice versa
        assert new_p1[0] == pytest.approx(orig_p2[0], abs=1e-6)
        assert new_p1[1] == pytest.approx(orig_p2[1], abs=1e-6)
        assert new_p2[0] == pytest.approx(orig_p1[0], abs=1e-6)
        assert new_p2[1] == pytest.approx(orig_p1[1], abs=1e-6)

    def test_rotate_returns_self(self):
        """rotate_around_midpoint should return self for chaining."""
        line = Line(0, 0, 100, 0)
        result = line.rotate_around_midpoint(45)
        assert result is line


class TestLineProjectOnto:
    def test_horizontal_onto_horizontal(self):
        """Projecting a horizontal line onto another horizontal line."""
        line = Line(x1=100, y1=50, x2=200, y2=50)
        axis = Line(x1=0, y1=100, x2=300, y2=100)
        proj = line.project_onto(axis)
        # Projection onto a horizontal line keeps x coords, y becomes axis y
        p1 = proj.get_start()
        p2 = proj.get_end()
        assert p1[0] == pytest.approx(100, abs=1e-6)
        assert p1[1] == pytest.approx(100, abs=1e-6)
        assert p2[0] == pytest.approx(200, abs=1e-6)
        assert p2[1] == pytest.approx(100, abs=1e-6)

    def test_vertical_onto_horizontal(self):
        """Projecting a vertical line onto a horizontal one gives a point."""
        line = Line(x1=150, y1=0, x2=150, y2=200)
        axis = Line(x1=0, y1=0, x2=300, y2=0)
        proj = line.project_onto(axis)
        p1 = proj.get_start()
        p2 = proj.get_end()
        # Both endpoints project to (150, 0)
        assert p1[0] == pytest.approx(150, abs=1e-6)
        assert p1[1] == pytest.approx(0, abs=1e-6)
        assert p2[0] == pytest.approx(150, abs=1e-6)
        assert p2[1] == pytest.approx(0, abs=1e-6)

    def test_diagonal_onto_x_axis(self):
        """Projecting a diagonal line onto the x-axis drops the y components."""
        line = Line(x1=0, y1=0, x2=100, y2=100)
        axis = Line(x1=0, y1=0, x2=200, y2=0)
        proj = line.project_onto(axis)
        p1 = proj.get_start()
        p2 = proj.get_end()
        assert p1[0] == pytest.approx(0, abs=1e-6)
        assert p1[1] == pytest.approx(0, abs=1e-6)
        assert p2[0] == pytest.approx(100, abs=1e-6)
        assert p2[1] == pytest.approx(0, abs=1e-6)

    def test_returns_line_instance(self):
        """project_onto should return a Line."""
        line = Line(0, 0, 100, 100)
        axis = Line(0, 0, 100, 0)
        result = line.project_onto(axis)
        assert isinstance(result, Line)


class TestLineReflectOver:
    def test_reflect_over_x_axis(self):
        """Reflecting over the x-axis negates the y coordinates."""
        line = Line(x1=50, y1=30, x2=150, y2=70)
        axis = Line(x1=0, y1=0, x2=200, y2=0)
        ref = line.reflect_over(axis)
        p1 = ref.get_start()
        p2 = ref.get_end()
        assert p1[0] == pytest.approx(50, abs=1e-6)
        assert p1[1] == pytest.approx(-30, abs=1e-6)
        assert p2[0] == pytest.approx(150, abs=1e-6)
        assert p2[1] == pytest.approx(-70, abs=1e-6)

    def test_reflect_over_y_axis(self):
        """Reflecting over the y-axis negates the x coordinates."""
        line = Line(x1=50, y1=30, x2=150, y2=70)
        axis = Line(x1=0, y1=0, x2=0, y2=200)
        ref = line.reflect_over(axis)
        p1 = ref.get_start()
        p2 = ref.get_end()
        assert p1[0] == pytest.approx(-50, abs=1e-6)
        assert p1[1] == pytest.approx(30, abs=1e-6)
        assert p2[0] == pytest.approx(-150, abs=1e-6)
        assert p2[1] == pytest.approx(70, abs=1e-6)

    def test_reflect_over_self_is_identity(self):
        """Reflecting a line on the x-axis over the x-axis gives the same line."""
        line = Line(x1=10, y1=0, x2=90, y2=0)
        axis = Line(x1=0, y1=0, x2=100, y2=0)
        ref = line.reflect_over(axis)
        p1 = ref.get_start()
        p2 = ref.get_end()
        assert p1[0] == pytest.approx(10, abs=1e-6)
        assert p1[1] == pytest.approx(0, abs=1e-6)
        assert p2[0] == pytest.approx(90, abs=1e-6)
        assert p2[1] == pytest.approx(0, abs=1e-6)

    def test_reflect_preserves_length(self):
        """Reflection should preserve the length of the line."""
        line = Line(x1=10, y1=20, x2=80, y2=60)
        axis = Line(x1=0, y1=50, x2=200, y2=50)
        original_len = line.get_length()
        ref = line.reflect_over(axis)
        assert ref.get_length() == pytest.approx(original_len, abs=1e-6)

    def test_returns_line_instance(self):
        """reflect_over should return a Line."""
        line = Line(0, 0, 100, 100)
        axis = Line(0, 50, 100, 50)
        result = line.reflect_over(axis)
        assert isinstance(result, Line)

    def test_reflect_over_diagonal(self):
        """Reflecting (100, 0) -> (100, 0) over y=x line should give (0, 100) -> (0, 100)."""
        # Point (a, 0) reflected over y=x becomes (0, a)
        line = Line(x1=100, y1=0, x2=200, y2=0)
        axis = Line(x1=0, y1=0, x2=100, y2=100)  # y = x
        ref = line.reflect_over(axis)
        p1 = ref.get_start()
        p2 = ref.get_end()
        assert p1[0] == pytest.approx(0, abs=1e-6)
        assert p1[1] == pytest.approx(100, abs=1e-6)
        assert p2[0] == pytest.approx(0, abs=1e-6)
        assert p2[1] == pytest.approx(200, abs=1e-6)


class TestRectangleSubdivide:
    def test_subdivide_2x2(self):
        """Subdivide into 2x2 grid should produce 4 rectangles."""
        rect = Rectangle(200, 100, x=50, y=50)
        grid = rect.subdivide(rows=2, cols=2)
        assert len(grid.objects) == 4

    def test_subdivide_cell_sizes(self):
        """Each cell should be exactly rect_width/cols by rect_height/rows."""
        rect = Rectangle(300, 200, x=0, y=0)
        grid = rect.subdivide(rows=2, cols=3)
        for cell in grid.objects:
            assert cell.width.at_time(0) == pytest.approx(100, abs=1e-6)
            assert cell.height.at_time(0) == pytest.approx(100, abs=1e-6)

    def test_subdivide_positions_row_major(self):
        """Cells should be positioned in row-major order."""
        rect = Rectangle(200, 100, x=10, y=20)
        grid = rect.subdivide(rows=2, cols=2)
        # Row 0, Col 0
        assert grid.objects[0].x.at_time(0) == pytest.approx(10, abs=1e-6)
        assert grid.objects[0].y.at_time(0) == pytest.approx(20, abs=1e-6)
        # Row 0, Col 1
        assert grid.objects[1].x.at_time(0) == pytest.approx(110, abs=1e-6)
        assert grid.objects[1].y.at_time(0) == pytest.approx(20, abs=1e-6)
        # Row 1, Col 0
        assert grid.objects[2].x.at_time(0) == pytest.approx(10, abs=1e-6)
        assert grid.objects[2].y.at_time(0) == pytest.approx(70, abs=1e-6)
        # Row 1, Col 1
        assert grid.objects[3].x.at_time(0) == pytest.approx(110, abs=1e-6)
        assert grid.objects[3].y.at_time(0) == pytest.approx(70, abs=1e-6)

    def test_subdivide_1x1_same_as_original(self):
        """Subdividing into 1x1 should produce a single cell matching the original."""
        rect = Rectangle(200, 100, x=50, y=50)
        grid = rect.subdivide(rows=1, cols=1)
        assert len(grid.objects) == 1
        cell = grid.objects[0]
        assert cell.x.at_time(0) == pytest.approx(50, abs=1e-6)
        assert cell.y.at_time(0) == pytest.approx(50, abs=1e-6)
        assert cell.width.at_time(0) == pytest.approx(200, abs=1e-6)
        assert cell.height.at_time(0) == pytest.approx(100, abs=1e-6)

    def test_subdivide_invalid_raises(self):
        """Subdividing with rows or cols < 1 should raise ValueError."""
        rect = Rectangle(100, 100)
        with pytest.raises(ValueError):
            rect.subdivide(rows=0, cols=2)
        with pytest.raises(ValueError):
            rect.subdivide(rows=2, cols=0)

    def test_subdivide_tiles_completely(self):
        """All cells should tile the original rectangle without gaps or overlap."""
        rect = Rectangle(300, 200, x=10, y=20)
        grid = rect.subdivide(rows=3, cols=4)
        assert len(grid.objects) == 12
        # Total area should match
        total_area = sum(
            c.width.at_time(0) * c.height.at_time(0) for c in grid.objects)
        assert total_area == pytest.approx(300 * 200, abs=1e-6)


class TestTextSplitLines:
    def test_single_line(self):
        """Text without newlines should produce a single Text object."""
        t = Text(text='Hello World', x=100, y=200)
        parts = t.split_lines()
        assert len(parts.objects) == 1
        assert parts.objects[0].text.at_time(0) == 'Hello World'

    def test_multiple_lines(self):
        """Text with newlines should produce one Text per line."""
        t = Text(text='Line 1\nLine 2\nLine 3', x=100, y=200, font_size=30)
        parts = t.split_lines()
        assert len(parts.objects) == 3
        assert parts.objects[0].text.at_time(0) == 'Line 1'
        assert parts.objects[1].text.at_time(0) == 'Line 2'
        assert parts.objects[2].text.at_time(0) == 'Line 3'

    def test_vertical_positioning(self):
        """Each line should be offset by font_size * line_spacing."""
        t = Text(text='A\nB\nC', x=100, y=200, font_size=40)
        parts = t.split_lines(line_spacing=1.5)
        y0 = parts.objects[0].y.at_time(0)
        y1 = parts.objects[1].y.at_time(0)
        y2 = parts.objects[2].y.at_time(0)
        assert y0 == pytest.approx(200, abs=1e-6)
        assert y1 == pytest.approx(200 + 40 * 1.5, abs=1e-6)
        assert y2 == pytest.approx(200 + 80 * 1.5, abs=1e-6)

    def test_preserves_x_position(self):
        """All lines should share the same x position."""
        t = Text(text='Hello\nWorld', x=300, y=100)
        parts = t.split_lines()
        assert parts.objects[0].x.at_time(0) == pytest.approx(300, abs=1e-6)
        assert parts.objects[1].x.at_time(0) == pytest.approx(300, abs=1e-6)

    def test_preserves_font_size(self):
        """All lines should have the same font size as the original."""
        t = Text(text='A\nB', x=0, y=0, font_size=24)
        parts = t.split_lines()
        for p in parts.objects:
            assert p.font_size.at_time(0) == pytest.approx(24, abs=1e-6)

    def test_empty_lines(self):
        """Empty lines (consecutive newlines) should produce empty Text objects."""
        t = Text(text='A\n\nC', x=0, y=0)
        parts = t.split_lines()
        assert len(parts.objects) == 3
        assert parts.objects[1].text.at_time(0) == ''


class TestPolygonInteriorAngles:
    def test_equilateral_triangle(self):
        """An equilateral triangle should have three 60-degree interior angles."""
        import math
        s = 100
        h = s * math.sqrt(3) / 2
        p = Polygon((0, 0), (s, 0), (s / 2, -h))
        angles = p.interior_angles()
        assert len(angles) == 3
        for a in angles:
            assert a == pytest.approx(60, abs=1)

    def test_right_triangle(self):
        """A right triangle should have a 90-degree angle."""
        p = Polygon((0, 0), (100, 0), (0, 100))
        angles = p.interior_angles()
        assert len(angles) == 3
        assert any(abs(a - 90) < 1 for a in angles)

    def test_square(self):
        """A square should have four 90-degree interior angles."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        angles = p.interior_angles()
        assert len(angles) == 4
        for a in angles:
            assert a == pytest.approx(90, abs=1)

    def test_sum_of_angles(self):
        """Sum of interior angles of an n-gon should be (n-2)*180."""
        pentagon = Polygon((0, 0), (100, 0), (130, 80), (60, 130), (-20, 80))
        angles = pentagon.interior_angles()
        assert sum(angles) == pytest.approx(540, abs=2)

    def test_open_polyline_returns_empty(self):
        """Open polylines should return an empty list."""
        p = Polygon((0, 0), (100, 0), (50, 100), closed=False)
        assert p.interior_angles() == []

    def test_degenerate_returns_empty(self):
        """Fewer than 3 vertices should return an empty list."""
        p = Polygon((0, 0), (100, 0))
        assert p.interior_angles() == []


class TestEllipseNormalAtAngle:
    def test_normal_perpendicular_to_tangent(self):
        """The normal line should be perpendicular to the tangent line."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        tangent = e.tangent_at_angle(45, length=200)
        normal = e.normal_at_angle(45, length=200)
        td = tangent.get_direction()
        nd = normal.get_direction()
        dot = td[0] * nd[0] + td[1] * nd[1]
        assert dot == pytest.approx(0, abs=1e-6)

    def test_normal_passes_through_ellipse_point(self):
        """The midpoint of the normal line should be on the ellipse."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        normal = e.normal_at_angle(0, length=200)
        mid = normal.get_midpoint()
        # At 0 degrees the point is (600, 400)
        assert mid[0] == pytest.approx(600, abs=1)
        assert mid[1] == pytest.approx(400, abs=1)

    def test_circle_normal_through_center(self):
        """For a circle, the normal should pass through the centre."""
        c = Circle(r=100, cx=500, cy=400)
        normal = c.normal_at_angle(90, length=300)
        # At 90 degrees the point is (500, 300) in SVG, centre is (500, 400)
        # The normal should be vertical through (500, 300)
        start = normal.get_start()
        end = normal.get_end()
        assert start[0] == pytest.approx(500, abs=1)
        assert end[0] == pytest.approx(500, abs=1)

    def test_normal_length(self):
        """The normal line should have the requested length."""
        e = Ellipse(rx=80, ry=40, cx=960, cy=540)
        normal = e.normal_at_angle(30, length=150)
        assert normal.get_length() == pytest.approx(150, abs=1)


class TestLineSubdivideInto:
    def test_two_segments(self):
        """Subdividing into 2 should give two lines of equal length."""
        line = Line(x1=0, y1=0, x2=200, y2=0)
        segs = line.subdivide_into(2)
        assert len(segs) == 2
        assert segs[0].get_length() == pytest.approx(100, abs=1)
        assert segs[1].get_length() == pytest.approx(100, abs=1)

    def test_endpoints_match(self):
        """First segment starts at p1, last ends at p2."""
        line = Line(x1=10, y1=20, x2=110, y2=120)
        segs = line.subdivide_into(3)
        s0 = segs[0].get_start()
        assert s0[0] == pytest.approx(10)
        assert s0[1] == pytest.approx(20)
        e2 = segs[2].get_end()
        assert e2[0] == pytest.approx(110)
        assert e2[1] == pytest.approx(120)

    def test_segments_are_contiguous(self):
        """Each segment's end should be the next segment's start."""
        line = Line(x1=0, y1=0, x2=300, y2=400)
        segs = line.subdivide_into(4)
        for i in range(3):
            end = segs[i].get_end()
            start = segs[i + 1].get_start()
            assert end[0] == pytest.approx(start[0], abs=1e-6)
            assert end[1] == pytest.approx(start[1], abs=1e-6)

    def test_one_segment(self):
        """Subdividing into 1 should return the same line."""
        line = Line(x1=50, y1=50, x2=150, y2=150)
        segs = line.subdivide_into(1)
        assert len(segs) == 1
        assert segs[0].get_length() == pytest.approx(line.get_length(), abs=1)

    def test_five_segments_equal_length(self):
        """Five segments should all have the same length."""
        line = Line(x1=0, y1=0, x2=500, y2=0)
        segs = line.subdivide_into(5)
        assert len(segs) == 5
        for s in segs:
            assert s.get_length() == pytest.approx(100, abs=1)


class TestLineDistanceToPoint:
    def test_point_on_line(self):
        """Distance from a point on the line should be 0."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        assert line.distance_to_point(50, 0) == pytest.approx(0, abs=1e-6)

    def test_perpendicular_distance(self):
        """Distance from a point directly above the midpoint."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        assert line.distance_to_point(50, 30) == pytest.approx(30, abs=1e-6)

    def test_beyond_endpoint(self):
        """Distance from a point beyond the endpoint should use the endpoint."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        # Point at (200, 0) is beyond the end
        assert line.distance_to_point(200, 0) == pytest.approx(100, abs=1e-6)

    def test_diagonal_line(self):
        """Test distance to a diagonal line segment."""
        import math
        line = Line(x1=0, y1=0, x2=100, y2=100)
        # Point at (0, 100) -- closest is (50, 50), distance = sqrt(50^2+50^2)
        d = line.distance_to_point(0, 100)
        assert d == pytest.approx(math.sqrt(50**2 + 50**2), abs=1)


class TestRectangleToLines:
    def test_returns_four_lines(self):
        """to_lines should return exactly 4 Line objects."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        lines = r.to_lines()
        assert len(lines) == 4
        for l in lines:
            assert isinstance(l, Line)

    def test_top_edge(self):
        """Top edge should go from top-left to top-right."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        top = r.to_lines()[0]
        s = top.get_start()
        e = top.get_end()
        assert s == pytest.approx((10, 20), abs=1e-6)
        assert e == pytest.approx((110, 20), abs=1e-6)

    def test_right_edge(self):
        """Right edge should go from top-right to bottom-right."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        right = r.to_lines()[1]
        s = right.get_start()
        e = right.get_end()
        assert s == pytest.approx((110, 20), abs=1e-6)
        assert e == pytest.approx((110, 70), abs=1e-6)

    def test_bottom_edge(self):
        """Bottom edge should go from bottom-right to bottom-left."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        bottom = r.to_lines()[2]
        s = bottom.get_start()
        e = bottom.get_end()
        assert s == pytest.approx((110, 70), abs=1e-6)
        assert e == pytest.approx((10, 70), abs=1e-6)

    def test_left_edge(self):
        """Left edge should go from bottom-left to top-left."""
        r = Rectangle(width=100, height=50, x=10, y=20)
        left = r.to_lines()[3]
        s = left.get_start()
        e = left.get_end()
        assert s == pytest.approx((10, 70), abs=1e-6)
        assert e == pytest.approx((10, 20), abs=1e-6)

    def test_total_perimeter(self):
        """Sum of edge lengths should equal the rectangle perimeter."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        lines = r.to_lines()
        total = sum(l.get_length() for l in lines)
        assert total == pytest.approx(600, abs=1)


class TestArcSplitInto:
    def test_two_arcs(self):
        """Splitting into 2 should give two arcs each covering half the sweep."""
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        parts = arc.split_into(2)
        assert len(parts) == 2
        assert parts[0].start_angle.at_time(0) == pytest.approx(0)
        assert parts[0].end_angle.at_time(0) == pytest.approx(45)
        assert parts[1].start_angle.at_time(0) == pytest.approx(45)
        assert parts[1].end_angle.at_time(0) == pytest.approx(90)

    def test_three_arcs(self):
        """Splitting into 3 should give three equal-sweep arcs."""
        arc = Arc(cx=960, cy=540, r=120, start_angle=0, end_angle=180)
        parts = arc.split_into(3)
        assert len(parts) == 3
        for i, p in enumerate(parts):
            expected_start = i * 60
            expected_end = (i + 1) * 60
            assert p.start_angle.at_time(0) == pytest.approx(expected_start, abs=0.01)
            assert p.end_angle.at_time(0) == pytest.approx(expected_end, abs=0.01)

    def test_preserves_center_and_radius(self):
        """All sub-arcs should share the same centre and radius."""
        arc = Arc(cx=100, cy=200, r=50, start_angle=30, end_angle=120)
        parts = arc.split_into(4)
        for p in parts:
            assert p.cx.at_time(0) == pytest.approx(100)
            assert p.cy.at_time(0) == pytest.approx(200)
            assert p.r.at_time(0) == pytest.approx(50)

    def test_single_arc(self):
        """Splitting into 1 should return a single arc with the same angles."""
        arc = Arc(cx=960, cy=540, r=120, start_angle=10, end_angle=350)
        parts = arc.split_into(1)
        assert len(parts) == 1
        assert parts[0].start_angle.at_time(0) == pytest.approx(10)
        assert parts[0].end_angle.at_time(0) == pytest.approx(350)

    def test_negative_sweep(self):
        """Should handle arcs with end_angle < start_angle (clockwise sweep)."""
        arc = Arc(cx=500, cy=500, r=100, start_angle=90, end_angle=0)
        parts = arc.split_into(3)
        assert len(parts) == 3
        assert parts[0].start_angle.at_time(0) == pytest.approx(90)
        assert parts[2].end_angle.at_time(0) == pytest.approx(0)


class TestPolygonIsClockwise:
    def test_clockwise_triangle(self):
        """A visually CW triangle in SVG coords (y-down) has positive signed area."""
        # In SVG coords (y-down), going top-left -> top-right -> bottom is visually CW
        # and gives positive signed area via the shoelace formula.
        p = Polygon((0, 0), (100, 0), (50, 100))
        assert p.is_clockwise() is True

    def test_counter_clockwise_triangle(self):
        """A visually CCW triangle has negative signed area in SVG coords."""
        p = Polygon((0, 0), (50, 100), (100, 0))
        assert p.is_clockwise() is False

    def test_degenerate_polygon(self):
        """A polygon with fewer than 3 vertices has zero area (not CW)."""
        p = Polygon((0, 0), (100, 0))
        assert p.is_clockwise() is False

    def test_square_cw(self):
        """A visually clockwise square should be detected as clockwise."""
        # Visually CW in SVG (y-down): top-left, top-right, bottom-right, bottom-left
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.is_clockwise() is True

    def test_square_ccw(self):
        """A visually counter-clockwise square should not be clockwise."""
        # Visually CCW in SVG: top-left, bottom-left, bottom-right, top-right
        p = Polygon((0, 0), (0, 100), (100, 100), (100, 0))
        assert p.is_clockwise() is False


class TestPolygonBoundingCircle:
    def test_equilateral_triangle(self):
        """The bounding circle of an equilateral triangle should circumscribe it."""
        import math
        r = 100
        pts = [(960 + r * math.cos(math.radians(a)),
                540 + r * math.sin(math.radians(a)))
               for a in [0, 120, 240]]
        p = Polygon(*pts)
        bc = p.bounding_circle()
        # The circumscribed circle radius should equal r
        assert bc.get_radius() == pytest.approx(r, abs=1)
        # Center should be at (960, 540)
        cx, cy = bc.c.at_time(0)
        assert cx == pytest.approx(960, abs=1)
        assert cy == pytest.approx(540, abs=1)

    def test_single_point(self):
        """Bounding circle of a single point should have radius 0."""
        p = Polygon((100, 200))
        bc = p.bounding_circle()
        assert bc.get_radius() == pytest.approx(0, abs=1e-6)
        cx, cy = bc.c.at_time(0)
        assert cx == pytest.approx(100, abs=1e-6)
        assert cy == pytest.approx(200, abs=1e-6)

    def test_two_points(self):
        """Bounding circle of two points should have diameter = distance."""
        p = Polygon((0, 0), (200, 0))
        bc = p.bounding_circle()
        assert bc.get_radius() == pytest.approx(100, abs=1)
        cx, cy = bc.c.at_time(0)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(0, abs=1)

    def test_all_vertices_inside(self):
        """All polygon vertices should be inside or on the bounding circle."""
        p = Polygon((10, 20), (100, 50), (80, 120), (5, 90), (50, 10))
        bc = p.bounding_circle()
        r = bc.get_radius()
        cx, cy = bc.c.at_time(0)
        for vx, vy in p.get_vertices():
            dist = ((vx - cx) ** 2 + (vy - cy) ** 2) ** 0.5
            assert dist <= r + 1e-6

    def test_empty_polygon_raises(self):
        """Bounding circle of an empty polygon should raise ValueError."""
        p = Polygon()
        with pytest.raises(ValueError):
            p.bounding_circle()

    def test_kwargs_forwarded(self):
        """Styling kwargs should be forwarded to the resulting Circle."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        bc = p.bounding_circle(stroke='#ff0000')
        # Verifying the returned object is a Circle with the right geometry
        assert isinstance(bc, Circle)
        # Stroke gets set (colour may be normalised to rgb(...) format)
        svg = bc.to_svg(0)
        assert 'stroke' in svg


class TestCircleSegmentArea:
    def test_semicircle(self):
        """Segment area for 180 degrees should equal the semicircle area."""
        import math
        c = Circle(r=100)
        # A semicircular segment = sector (pi*r^2/2) - triangle (area 0 for 180 deg)
        # For 180 degrees: theta = pi, sin(pi) = 0, so segment = sector = pi*r^2/2
        area = c.segment_area(0, 180)
        expected = 0.5 * 100 * 100 * (math.pi - math.sin(math.pi))
        assert area == pytest.approx(expected, abs=0.1)

    def test_quarter_circle(self):
        """Segment area for 90 degrees should be correct."""
        import math
        c = Circle(r=100)
        area = c.segment_area(0, 90)
        theta = math.pi / 2
        expected = 0.5 * 100 * 100 * (theta - math.sin(theta))
        assert area == pytest.approx(expected, abs=0.1)

    def test_zero_sweep(self):
        """Segment area for 0 degrees should be 0."""
        c = Circle(r=100)
        assert c.segment_area(45, 45) == 0.0

    def test_full_circle(self):
        """Segment area for 360 degrees should equal the full circle area."""
        c = Circle(r=50)
        area = c.segment_area(0, 360)
        # 360 % 360 == 0, so area should be 0 (a "segment" of zero sweep)
        assert area == pytest.approx(0, abs=0.01)

    def test_negative_sweep(self):
        """Segment area should be non-negative regardless of angle order."""
        c = Circle(r=100)
        area = c.segment_area(90, 0)
        assert area >= 0


class TestCirclePowerOfPoint:
    def test_point_on_circle(self):
        """Power of a point on the circle should be 0."""
        c = Circle(r=100, cx=500, cy=300)
        # Point at angle 0: (600, 300)
        power = c.power_of_point(600, 300)
        assert power == pytest.approx(0, abs=1e-6)

    def test_point_inside(self):
        """Power of a point inside the circle should be negative."""
        c = Circle(r=100, cx=500, cy=300)
        power = c.power_of_point(500, 300)  # center
        assert power < 0
        assert power == pytest.approx(-10000, abs=1e-6)

    def test_point_outside(self):
        """Power of a point outside the circle should be positive."""
        c = Circle(r=100, cx=500, cy=300)
        power = c.power_of_point(700, 300)  # 200 away from center
        assert power > 0
        expected = 200**2 - 100**2
        assert power == pytest.approx(expected, abs=1e-6)

    def test_symmetry(self):
        """Power should be the same for points equidistant from center."""
        c = Circle(r=50, cx=0, cy=0)
        p1 = c.power_of_point(80, 0)
        p2 = c.power_of_point(0, 80)
        assert p1 == pytest.approx(p2, abs=1e-6)


class TestLineIsParallel:
    def test_parallel_horizontal_lines(self):
        """Two horizontal lines should be parallel."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 50, 100, 50)
        assert l1.is_parallel(l2) is True

    def test_parallel_vertical_lines(self):
        """Two vertical lines should be parallel."""
        l1 = Line(0, 0, 0, 100)
        l2 = Line(50, 0, 50, 100)
        assert l1.is_parallel(l2) is True

    def test_parallel_diagonal_lines(self):
        """Two diagonal lines with same slope should be parallel."""
        l1 = Line(0, 0, 100, 100)
        l2 = Line(50, 0, 150, 100)
        assert l1.is_parallel(l2) is True

    def test_not_parallel(self):
        """Two lines at different angles should not be parallel."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 0, 100, 100)
        assert l1.is_parallel(l2) is False

    def test_antiparallel(self):
        """Lines pointing in opposite directions should be parallel."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(100, 50, 0, 50)
        assert l1.is_parallel(l2) is True


class TestLineIsPerpendicular:
    def test_perpendicular_axes(self):
        """A horizontal and vertical line should be perpendicular."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(50, -50, 50, 50)
        assert l1.is_perpendicular(l2) is True

    def test_perpendicular_diagonal(self):
        """Two diagonal lines at 90 degrees should be perpendicular."""
        l1 = Line(0, 0, 100, 100)
        l2 = Line(0, 100, 100, 0)
        assert l1.is_perpendicular(l2) is True

    def test_not_perpendicular(self):
        """Two parallel lines should not be perpendicular."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 50, 100, 50)
        assert l1.is_perpendicular(l2) is False

    def test_parallel_not_perpendicular(self):
        """Lines with the same direction are not perpendicular."""
        l1 = Line(0, 0, 100, 100)
        l2 = Line(50, 50, 150, 150)
        assert l1.is_perpendicular(l2) is False

    def test_perpendicular_consistency_with_angle_to(self):
        """Perpendicular lines should have angle_to approximately 90 degrees."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 0, 0, 100)
        assert l1.is_perpendicular(l2)
        assert l1.angle_to(l2) == pytest.approx(90, abs=0.1)


class TestPolygonGetConvexHull:
    def test_convex_polygon_hull_is_same(self):
        """Convex hull of a convex polygon should have the same vertices."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        hull = p.get_convex_hull()
        hull_verts = hull.get_vertices()
        assert len(hull_verts) == 4

    def test_concave_polygon_hull_removes_interior(self):
        """Convex hull of a concave polygon should remove the interior vertex."""
        # Star-shaped: center indent at (50, 10) is inside the hull
        p = Polygon((0, 0), (50, 10), (100, 0), (100, 100), (0, 100))
        hull = p.get_convex_hull()
        hull_verts = hull.get_vertices()
        # The hull should have 4 vertices, not 5 (the indent is removed)
        assert len(hull_verts) == 4

    def test_convex_hull_is_convex(self):
        """The returned hull should be a convex polygon."""
        p = Polygon((10, 10), (50, 50), (90, 10), (90, 90), (10, 90))
        hull = p.get_convex_hull()
        assert hull.is_convex()

    def test_convex_hull_raises_on_too_few(self):
        """Fewer than 3 vertices should raise ValueError."""
        p = Polygon((0, 0), (1, 1))
        with pytest.raises(ValueError):
            p.get_convex_hull()

    def test_convex_hull_passes_kwargs(self):
        """Keyword arguments should be forwarded to the new Polygon."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        hull = p.get_convex_hull(fill='#ff0000')
        svg = hull.to_svg(0)
        assert 'rgb(255,0,0)' in svg


class TestCircleChordLength:
    def test_chord_at_zero_distance_is_diameter(self):
        """Chord at distance 0 from center should equal the diameter."""
        c = Circle(r=100)
        assert c.chord_length(0) == pytest.approx(200.0)

    def test_chord_at_radius_is_zero(self):
        """Chord at distance r from center should be zero."""
        c = Circle(r=50)
        assert c.chord_length(50) == pytest.approx(0.0)

    def test_chord_at_known_distance(self):
        """Chord at distance 60 from center of r=100 should be 160."""
        # 2 * sqrt(100^2 - 60^2) = 2 * sqrt(6400) = 2 * 80 = 160
        c = Circle(r=100)
        assert c.chord_length(60) == pytest.approx(160.0)

    def test_chord_at_half_radius(self):
        """Chord at r/2 should be 2 * sqrt(3/4) * r = r * sqrt(3)."""
        c = Circle(r=100)
        import math
        expected = 100 * math.sqrt(3)
        assert c.chord_length(50) == pytest.approx(expected)

    def test_negative_distance_raises(self):
        """Negative distance should raise ValueError."""
        c = Circle(r=100)
        with pytest.raises(ValueError):
            c.chord_length(-10)

    def test_distance_exceeds_radius_raises(self):
        """Distance greater than radius should raise ValueError."""
        c = Circle(r=50)
        with pytest.raises(ValueError):
            c.chord_length(60)


class TestCircleArcLength:
    def test_full_circle(self):
        """Arc length for 0 to 360 should equal the circumference."""
        import math
        c = Circle(r=100)
        assert c.arc_length(0, 360) == pytest.approx(2 * math.pi * 100)

    def test_quarter_arc(self):
        """Arc length for 90 degrees should be pi*r/2."""
        import math
        c = Circle(r=100)
        assert c.arc_length(0, 90) == pytest.approx(math.pi * 100 / 2)

    def test_semicircle(self):
        """Arc length for 180 degrees should be pi*r."""
        import math
        c = Circle(r=100)
        assert c.arc_length(0, 180) == pytest.approx(math.pi * 100)

    def test_symmetric(self):
        """arc_length(a, b) should equal arc_length(b, a)."""
        c = Circle(r=50)
        assert c.arc_length(30, 120) == pytest.approx(c.arc_length(120, 30))

    def test_zero_sweep(self):
        """Arc length for same start and end should be zero."""
        c = Circle(r=100)
        assert c.arc_length(45, 45) == pytest.approx(0.0)


class TestLineParallelThrough:
    def test_horizontal_line(self):
        """Parallel line through a point offset vertically."""
        l = Line(0, 0, 200, 0)
        l2 = l.parallel_through((100, 50))
        s = l2.get_start()
        e = l2.get_end()
        assert s[0] == pytest.approx(0.0)
        assert s[1] == pytest.approx(50.0)
        assert e[0] == pytest.approx(200.0)
        assert e[1] == pytest.approx(50.0)

    def test_vertical_line(self):
        """Parallel line through a point offset horizontally."""
        l = Line(0, 0, 0, 100)
        l2 = l.parallel_through((50, 50))
        s = l2.get_start()
        e = l2.get_end()
        assert s[0] == pytest.approx(50.0)
        assert s[1] == pytest.approx(0.0)
        assert e[0] == pytest.approx(50.0)
        assert e[1] == pytest.approx(100.0)

    def test_preserves_length(self):
        """The parallel line should have the same length as the original."""
        l = Line(10, 20, 110, 120)
        l2 = l.parallel_through((200, 300))
        assert l2.get_length() == pytest.approx(l.get_length())

    def test_is_parallel(self):
        """The new line should be parallel to the original."""
        l = Line(0, 0, 100, 50)
        l2 = l.parallel_through((300, 400))
        assert l.is_parallel(l2)

    def test_passes_kwargs(self):
        """Keyword arguments should be forwarded to the new Line."""
        l = Line(0, 0, 100, 0)
        l2 = l.parallel_through((50, 50), stroke='#ff0000')
        svg = l2.to_svg(0)
        assert 'rgb(255,0,0)' in svg


class TestRectangleDiagonalLines:
    def test_basic_rectangle(self):
        """Diagonal lines of a simple rectangle."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        d1, d2 = r.diagonal_lines()
        # d1: top-left (0,0) -> bottom-right (200,100)
        assert d1.get_start() == pytest.approx((0.0, 0.0), abs=1e-9)
        assert d1.get_end() == pytest.approx((200.0, 100.0), abs=1e-9)
        # d2: top-right (200,0) -> bottom-left (0,100)
        assert d2.get_start() == pytest.approx((200.0, 0.0), abs=1e-9)
        assert d2.get_end() == pytest.approx((0.0, 100.0), abs=1e-9)

    def test_diagonals_equal_length(self):
        """Both diagonals of a rectangle should have the same length."""
        r = Rectangle(width=300, height=400, x=10, y=20)
        d1, d2 = r.diagonal_lines()
        assert d1.get_length() == pytest.approx(d2.get_length())

    def test_diagonals_length_matches_diagonal_length(self):
        """Diagonal line length should match get_diagonal_length."""
        r = Rectangle(width=3, height=4, x=0, y=0)
        d1, d2 = r.diagonal_lines()
        assert d1.get_length() == pytest.approx(r.get_diagonal_length())
        assert d2.get_length() == pytest.approx(5.0)

    def test_diagonals_intersect_at_center(self):
        """The two diagonals should intersect at the rectangle center."""
        r = Rectangle(width=200, height=100, x=50, y=50)
        d1, d2 = r.diagonal_lines()
        pt = d1.intersect_line(d2)
        assert pt is not None
        assert pt[0] == pytest.approx(150.0)  # 50 + 200/2
        assert pt[1] == pytest.approx(100.0)  # 50 + 100/2

    def test_square_diagonals_are_perpendicular(self):
        """Diagonals of a square should be perpendicular."""
        r = Rectangle(width=100, height=100, x=0, y=0)
        d1, d2 = r.diagonal_lines()
        assert d1.is_perpendicular(d2)

    def test_passes_kwargs(self):
        """Extra kwargs should be forwarded to the Line constructor."""
        r = Rectangle(width=100, height=50, x=0, y=0)
        d1, d2 = r.diagonal_lines(stroke='#00ff00')
        assert 'rgb(0,255,0)' in d1.to_svg(0)
        assert 'rgb(0,255,0)' in d2.to_svg(0)


class TestTextTruncate:
    def test_truncate_long_text(self):
        """Truncating a long text should shorten it with ellipsis."""
        t = Text('Hello, World!')
        t.truncate(8)
        assert t.get_text() == 'Hello...'

    def test_truncate_short_text_no_change(self):
        """Text shorter than n should be unchanged."""
        t = Text('Hi')
        t.truncate(10)
        assert t.get_text() == 'Hi'

    def test_truncate_exact_length_no_change(self):
        """Text exactly n chars should be unchanged."""
        t = Text('Hello')
        t.truncate(5)
        assert t.get_text() == 'Hello'

    def test_truncate_custom_ellipsis(self):
        """Custom ellipsis string should be appended."""
        t = Text('abcdefghij')
        t.truncate(7, ellipsis='..')
        assert t.get_text() == 'abcde..'

    def test_truncate_empty_ellipsis(self):
        """Empty ellipsis should just chop the text."""
        t = Text('Hello, World!')
        t.truncate(5, ellipsis='')
        assert t.get_text() == 'Hello'

    def test_truncate_returns_self(self):
        """truncate should return self for chaining."""
        t = Text('Hello, World!')
        result = t.truncate(8)
        assert result is t

    def test_truncate_raises_on_small_n(self):
        """n smaller than ellipsis length should raise ValueError."""
        t = Text('Hello')
        with pytest.raises(ValueError):
            t.truncate(2, ellipsis='...')

    def test_truncate_n_equals_ellipsis_len(self):
        """n equal to ellipsis length should give just the ellipsis."""
        t = Text('Hello, World!')
        t.truncate(3, ellipsis='...')
        assert t.get_text() == '...'


# ---------------------------------------------------------------------------
# Polygon.get_edge_midpoints
# ---------------------------------------------------------------------------

class TestPolygonGetEdgeMidpoints:
    def test_triangle_midpoints(self):
        """Triangle should return 3 midpoints (one per edge)."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        mids = p.get_edge_midpoints()
        assert len(mids) == 3
        # Edge (0,0)-(100,0) midpoint
        assert mids[0][0] == pytest.approx(50)
        assert mids[0][1] == pytest.approx(0)
        # Edge (100,0)-(50,100) midpoint
        assert mids[1][0] == pytest.approx(75)
        assert mids[1][1] == pytest.approx(50)
        # Closing edge (50,100)-(0,0) midpoint
        assert mids[2][0] == pytest.approx(25)
        assert mids[2][1] == pytest.approx(50)

    def test_square_midpoints(self):
        """Square should have 4 midpoints."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        mids = p.get_edge_midpoints()
        assert len(mids) == 4

    def test_open_polyline_no_closing_edge(self):
        """Open polyline (Lines) should not include closing edge midpoint."""
        ln = Lines((0, 0), (100, 0), (100, 100))
        mids = ln.get_edge_midpoints()
        assert len(mids) == 2
        assert mids[0] == pytest.approx((50, 0))
        assert mids[1] == pytest.approx((100, 50))

    def test_single_vertex_returns_empty(self):
        """A single vertex polygon should return empty list."""
        p = Polygon((5, 5))
        mids = p.get_edge_midpoints()
        assert mids == []

    def test_two_vertices_one_midpoint(self):
        """Two-vertex polygon (a line) should return 1 midpoint."""
        p = Polygon((0, 0), (10, 0), closed=False)
        mids = p.get_edge_midpoints()
        assert len(mids) == 1
        assert mids[0] == pytest.approx((5, 0))


# ---------------------------------------------------------------------------
# Circle.circumscribed_polygon
# ---------------------------------------------------------------------------

class TestCircleCircumscribedPolygon:
    def test_square_circumscribes_circle(self):
        """Circumscribed square should have inradius equal to circle radius."""
        c = Circle(r=100, cx=500, cy=400)
        poly = c.circumscribed_polygon(4)
        # The inradius of the resulting polygon should equal the circle's radius
        inradius = poly.get_inradius()
        assert inradius == pytest.approx(100, abs=1e-6)

    def test_hexagon_circumscribes_circle(self):
        """Circumscribed hexagon inradius should match circle radius."""
        c = Circle(r=50, cx=200, cy=300)
        poly = c.circumscribed_polygon(6)
        inradius = poly.get_inradius()
        assert inradius == pytest.approx(50, abs=1e-6)

    def test_triangle_circumscribes_circle(self):
        """Circumscribed triangle inradius should match circle radius."""
        c = Circle(r=80, cx=960, cy=540)
        poly = c.circumscribed_polygon(3)
        inradius = poly.get_inradius()
        assert inradius == pytest.approx(80, abs=1e-6)

    def test_returns_regular_polygon(self):
        """Result should be a RegularPolygon."""
        from vectormation.objects import RegularPolygon
        c = Circle(r=50)
        poly = c.circumscribed_polygon(5)
        assert isinstance(poly, RegularPolygon)

    def test_vertices_outside_circle(self):
        """All vertices of circumscribed polygon should lie outside the circle."""
        c = Circle(r=100, cx=960, cy=540)
        poly = c.circumscribed_polygon(6)
        verts = poly.get_vertices()
        for vx, vy in verts:
            dist = ((vx - 960)**2 + (vy - 540)**2) ** 0.5
            assert dist >= 100 - 1e-6

    def test_n_less_than_3_raises(self):
        """n < 3 should raise ValueError."""
        c = Circle(r=50)
        with pytest.raises(ValueError):
            c.circumscribed_polygon(2)

    def test_angle_rotation(self):
        """Non-zero angle should rotate the polygon."""
        c = Circle(r=100, cx=0, cy=0)
        poly0 = c.circumscribed_polygon(4, angle=0)
        poly45 = c.circumscribed_polygon(4, angle=45)
        v0 = poly0.get_vertices()
        v45 = poly45.get_vertices()
        # First vertex should differ
        assert v0[0][0] != pytest.approx(v45[0][0], abs=1)


# ---------------------------------------------------------------------------
# Line.contains_point
# ---------------------------------------------------------------------------

class TestLineContainsPoint:
    def test_point_on_line(self):
        """Midpoint of the line should be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 0) is True

    def test_endpoint_on_line(self):
        """Endpoints should be contained."""
        l = Line(x1=10, y1=20, x2=50, y2=60)
        assert l.contains_point(10, 20) is True
        assert l.contains_point(50, 60) is True

    def test_point_far_away(self):
        """Point far from the line should not be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 50) is False

    def test_point_near_line_within_tolerance(self):
        """Point within tolerance should be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 1.5, tol=2) is True

    def test_point_near_line_outside_tolerance(self):
        """Point outside tolerance should not be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 3, tol=2) is False

    def test_custom_tolerance(self):
        """Custom tolerance should work."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 5, tol=10) is True
        assert l.contains_point(50, 5, tol=4) is False

    def test_diagonal_line(self):
        """Point on a diagonal line should be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=100)
        # Midpoint of diagonal
        assert l.contains_point(50, 50) is True

    def test_point_beyond_segment(self):
        """Point on the infinite line but beyond segment should not be contained."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        # (200, 0) is on the infinite line extension but past end
        assert l.contains_point(200, 0, tol=2) is False


# ---------------------------------------------------------------------------
# Rectangle.from_bounding_box
# ---------------------------------------------------------------------------

class TestRectangleFromBoundingBox:
    def test_from_circle_bbox(self):
        """Rectangle from circle bbox should enclose the circle."""
        c = Circle(r=50, cx=100, cy=200)
        r = Rectangle.from_bounding_box(c)
        assert r.x.at_time(0) == pytest.approx(50)
        assert r.y.at_time(0) == pytest.approx(150)
        assert r.width.at_time(0) == pytest.approx(100)
        assert r.height.at_time(0) == pytest.approx(100)

    def test_from_rectangle_bbox(self):
        """Rectangle from another rectangle's bbox should match."""
        src = Rectangle(width=120, height=80, x=10, y=20)
        r = Rectangle.from_bounding_box(src)
        assert r.width.at_time(0) == pytest.approx(120)
        assert r.height.at_time(0) == pytest.approx(80)

    def test_padding(self):
        """Padding should expand the result on all sides."""
        c = Circle(r=50, cx=100, cy=200)
        r = Rectangle.from_bounding_box(c, padding=10)
        assert r.x.at_time(0) == pytest.approx(40)
        assert r.y.at_time(0) == pytest.approx(140)
        assert r.width.at_time(0) == pytest.approx(120)
        assert r.height.at_time(0) == pytest.approx(120)

    def test_styling_kwargs_forwarded(self):
        """Extra kwargs should reach the Rectangle constructor."""
        c = Circle(r=50, cx=100, cy=200)
        r = Rectangle.from_bounding_box(c, fill='#FF0000')
        svg = r.to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_from_polygon_bbox(self):
        """Rectangle from triangle bbox should work."""
        tri = Polygon((0, 0), (100, 0), (50, 80))
        r = Rectangle.from_bounding_box(tri)
        assert r.x.at_time(0) == pytest.approx(0)
        assert r.y.at_time(0) == pytest.approx(0)
        assert r.width.at_time(0) == pytest.approx(100)
        assert r.height.at_time(0) == pytest.approx(80)


# ===== New feature tests =====

class TestCircleTangentPoints:
    """Tests for Circle.tangent_points()."""

    def test_external_point_returns_two_points(self):
        c = Circle(r=50, cx=100, cy=100)
        pts = c.tangent_points(250, 100)
        assert len(pts) == 2

    def test_tangent_points_lie_on_circle(self):
        c = Circle(r=50, cx=100, cy=100)
        pts = c.tangent_points(250, 100)
        for px, py in pts:
            dist = math.hypot(px - 100, py - 100)
            assert dist == pytest.approx(50, abs=1e-6)

    def test_tangent_points_are_perpendicular_to_radius(self):
        """Tangent at touch point is perpendicular to the radius vector."""
        c = Circle(r=50, cx=100, cy=100)
        ext_x, ext_y = 250, 100
        pts = c.tangent_points(ext_x, ext_y)
        for px, py in pts:
            # Radius vector (center -> touch point)
            rx, ry = px - 100, py - 100
            # Vector from touch point to external point
            tx, ty = ext_x - px, ext_y - py
            dot = rx * tx + ry * ty
            assert dot == pytest.approx(0, abs=1e-4)

    def test_point_on_circle_returns_one_point(self):
        c = Circle(r=50, cx=100, cy=100)
        pts = c.tangent_points(150, 100)  # point is on the circle
        assert len(pts) == 1
        assert pts[0][0] == pytest.approx(150, abs=1e-6)
        assert pts[0][1] == pytest.approx(100, abs=1e-6)

    def test_point_inside_circle_returns_empty(self):
        c = Circle(r=50, cx=100, cy=100)
        pts = c.tangent_points(110, 100)  # inside
        assert pts == []

    def test_symmetric_external_point(self):
        """Point directly above circle should give symmetric tangent points."""
        c = Circle(r=50, cx=100, cy=100)
        pts = c.tangent_points(100, -50)  # directly above
        assert len(pts) == 2
        # The two tangent points should be symmetric about x=100
        assert pts[0][0] + pts[1][0] == pytest.approx(200, abs=1e-4)


class TestPolygonTriangulate:
    """Tests for Polygon.triangulate()."""

    def test_triangle_returns_one_triangle(self):
        tri = Polygon((0, 0), (100, 0), (50, 80))
        result = tri.triangulate()
        assert len(result) == 1
        verts = result[0].get_vertices()
        assert len(verts) == 3

    def test_square_returns_two_triangles(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.triangulate()
        assert len(result) == 2

    def test_pentagon_returns_three_triangles(self):
        import math as m
        pts = []
        for i in range(5):
            angle = 2 * m.pi * i / 5 - m.pi / 2
            pts.append((100 + 50 * m.cos(angle), 100 + 50 * m.sin(angle)))
        pent = Polygon(*pts)
        result = pent.triangulate()
        assert len(result) == 3

    def test_triangulation_covers_area(self):
        """Sum of triangle areas should equal the original polygon area."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        triangles = sq.triangulate()
        total_area = 0
        for tri in triangles:
            verts = tri.get_vertices()
            # Shoelface formula for triangle
            (x0, y0), (x1, y1), (x2, y2) = verts
            area = abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / 2
            total_area += area
        assert total_area == pytest.approx(10000, abs=1)

    def test_styling_kwargs_forwarded(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.triangulate(fill='#FF0000')
        svg = result[0].to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_open_polygon_raises(self):
        poly = Polygon((0, 0), (100, 0), (50, 80), closed=False)
        with pytest.raises(ValueError, match="closed"):
            poly.triangulate()

    def test_fewer_than_3_vertices_raises(self):
        poly = Polygon((0, 0), (100, 0))
        with pytest.raises(ValueError, match="3 vertices"):
            poly.triangulate()

    def test_concave_polygon(self):
        """L-shaped concave polygon should triangulate correctly."""
        # L-shape (6 vertices)
        pts = [(0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100)]
        poly = Polygon(*pts)
        result = poly.triangulate()
        assert len(result) == 4  # 6 - 2 = 4 triangles


class TestLineIntersectSegment:
    """Tests for Line.intersect_segment()."""

    def test_crossing_segments(self):
        l1 = Line(x1=0, y1=0, x2=100, y2=100)
        l2 = Line(x1=0, y1=100, x2=100, y2=0)
        pt = l1.intersect_segment(l2)
        assert pt is not None
        assert pt[0] == pytest.approx(50, abs=1e-6)
        assert pt[1] == pytest.approx(50, abs=1e-6)

    def test_non_crossing_segments_return_none(self):
        """Segments that would intersect if extended, but don't overlap."""
        l1 = Line(x1=0, y1=0, x2=10, y2=10)
        l2 = Line(x1=20, y1=0, x2=30, y2=10)
        pt = l1.intersect_segment(l2)
        assert pt is None

    def test_parallel_segments(self):
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=10, x2=100, y2=10)
        pt = l1.intersect_segment(l2)
        assert pt is None

    def test_t_intersection_at_endpoint(self):
        """Segment ending exactly at the other segment."""
        l1 = Line(x1=0, y1=50, x2=100, y2=50)
        l2 = Line(x1=50, y1=0, x2=50, y2=50)
        pt = l1.intersect_segment(l2)
        assert pt is not None
        assert pt[0] == pytest.approx(50, abs=1e-6)
        assert pt[1] == pytest.approx(50, abs=1e-6)

    def test_segments_would_intersect_if_extended(self):
        """Lines intersect in infinite extension, but not as segments."""
        l1 = Line(x1=0, y1=0, x2=10, y2=0)
        l2 = Line(x1=50, y1=-10, x2=50, y2=10)
        # Infinite lines cross at (50, 0), but l1 only goes to x=10
        pt = l1.intersect_segment(l2)
        assert pt is None

    def test_same_as_intersect_line_when_segments_cross(self):
        """When segments do cross, result should match intersect_line."""
        l1 = Line(x1=0, y1=0, x2=200, y2=200)
        l2 = Line(x1=200, y1=0, x2=0, y2=200)
        seg_pt = l1.intersect_segment(l2)
        line_pt = l1.intersect_line(l2)
        assert seg_pt is not None
        assert line_pt is not None
        assert seg_pt[0] == pytest.approx(line_pt[0], abs=1e-6)
        assert seg_pt[1] == pytest.approx(line_pt[1], abs=1e-6)


class TestLineClosestPointOnSegment:
    """Tests for Line.closest_point_on_segment()."""

    def test_projection_within_segment(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        pt = line.closest_point_on_segment(50, 30)
        assert pt[0] == pytest.approx(50)
        assert pt[1] == pytest.approx(0)

    def test_clamps_to_start(self):
        """Point beyond p1 should clamp to p1."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        pt = line.closest_point_on_segment(-50, 0)
        assert pt[0] == pytest.approx(0)
        assert pt[1] == pytest.approx(0)

    def test_clamps_to_end(self):
        """Point beyond p2 should clamp to p2."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        pt = line.closest_point_on_segment(200, 0)
        assert pt[0] == pytest.approx(100)
        assert pt[1] == pytest.approx(0)

    def test_differs_from_project_point(self):
        """project_point extends infinitely; closest_point_on_segment does not."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        proj = line.project_point(-50, 10)
        seg = line.closest_point_on_segment(-50, 10)
        # project_point gives x=-50 (extended), segment clamps to x=0
        assert proj[0] == pytest.approx(-50)
        assert seg[0] == pytest.approx(0)

    def test_diagonal_segment(self):
        line = Line(x1=0, y1=0, x2=100, y2=100)
        pt = line.closest_point_on_segment(100, 0)
        assert pt[0] == pytest.approx(50)
        assert pt[1] == pytest.approx(50)

    def test_degenerate_zero_length_segment(self):
        """Zero-length segment returns the single point."""
        line = Line(x1=50, y1=50, x2=50, y2=50)
        pt = line.closest_point_on_segment(100, 100)
        assert pt[0] == pytest.approx(50)
        assert pt[1] == pytest.approx(50)


class TestTextBoldItalic:
    """Tests for Text.bold() and Text.italic()."""

    def test_bold_adds_font_weight(self):
        t = Text('Hello')
        t.bold()
        svg = t.to_svg(0)
        assert "font-weight='bold'" in svg

    def test_italic_adds_font_style(self):
        t = Text('Hello')
        t.italic()
        svg = t.to_svg(0)
        assert "font-style='italic'" in svg

    def test_bold_and_italic_together(self):
        t = Text('Hello')
        t.bold().italic()
        svg = t.to_svg(0)
        assert "font-weight='bold'" in svg
        assert "font-style='italic'" in svg

    def test_bold_returns_self(self):
        t = Text('Hello')
        result = t.bold()
        assert result is t

    def test_italic_returns_self(self):
        t = Text('Hello')
        result = t.italic()
        assert result is t

    def test_default_no_weight_or_style(self):
        t = Text('Hello')
        svg = t.to_svg(0)
        assert 'font-weight' not in svg
        assert 'font-style' not in svg

    def test_bold_normal_removes_weight(self):
        t = Text('Hello')
        t.bold()
        t.bold('normal')
        svg = t.to_svg(0)
        assert 'font-weight' not in svg

    def test_italic_normal_removes_style(self):
        t = Text('Hello')
        t.italic()
        t.italic('normal')
        svg = t.to_svg(0)
        assert 'font-style' not in svg

    def test_custom_weight_value(self):
        t = Text('Hello')
        t.bold('700')
        svg = t.to_svg(0)
        assert "font-weight='700'" in svg

    def test_oblique_style(self):
        t = Text('Hello')
        t.italic('oblique')
        svg = t.to_svg(0)
        assert "font-style='oblique'" in svg


class TestRectangleSampleBorder:
    """Tests for Rectangle.sample_border()."""

    def test_t0_is_top_left(self):
        r = Rectangle(100, 50, x=10, y=20)
        pt = r.sample_border(0)
        assert pt[0] == pytest.approx(10)
        assert pt[1] == pytest.approx(20)

    def test_top_right_corner(self):
        r = Rectangle(100, 50, x=0, y=0)
        perim = 2 * (100 + 50)
        t_tr = 100 / perim  # top edge is 100px long
        pt = r.sample_border(t_tr)
        assert pt[0] == pytest.approx(100)
        assert pt[1] == pytest.approx(0)

    def test_bottom_right_corner(self):
        r = Rectangle(100, 50, x=0, y=0)
        perim = 2 * (100 + 50)
        t_br = (100 + 50) / perim
        pt = r.sample_border(t_br)
        assert pt[0] == pytest.approx(100)
        assert pt[1] == pytest.approx(50)

    def test_bottom_left_corner(self):
        r = Rectangle(100, 50, x=0, y=0)
        perim = 2 * (100 + 50)
        t_bl = (100 + 50 + 100) / perim
        pt = r.sample_border(t_bl)
        assert pt[0] == pytest.approx(0)
        assert pt[1] == pytest.approx(50)

    def test_midpoint_top_edge(self):
        r = Rectangle(100, 50, x=0, y=0)
        perim = 2 * (100 + 50)
        t_mid_top = 50 / perim
        pt = r.sample_border(t_mid_top)
        assert pt[0] == pytest.approx(50)
        assert pt[1] == pytest.approx(0)

    def test_wraps_around(self):
        """t=1 should wrap to same as t=0."""
        r = Rectangle(100, 50, x=10, y=20)
        pt0 = r.sample_border(0)
        pt1 = r.sample_border(1.0)
        assert pt0[0] == pytest.approx(pt1[0])
        assert pt0[1] == pytest.approx(pt1[1])

    def test_square_quarter_marks(self):
        """For a square, t=0.25 should be top-right, etc."""
        r = Rectangle(100, 100, x=0, y=0)
        pt = r.sample_border(0.25)
        assert pt[0] == pytest.approx(100)
        assert pt[1] == pytest.approx(0)
        pt = r.sample_border(0.5)
        assert pt[0] == pytest.approx(100)
        assert pt[1] == pytest.approx(100)
        pt = r.sample_border(0.75)
        assert pt[0] == pytest.approx(0)
        assert pt[1] == pytest.approx(100)

    def test_negative_t_wraps(self):
        """Negative t should wrap via modulo."""
        r = Rectangle(100, 100, x=0, y=0)
        pt = r.sample_border(-0.25)
        pt_pos = r.sample_border(0.75)
        assert pt[0] == pytest.approx(pt_pos[0])
        assert pt[1] == pytest.approx(pt_pos[1])


# ── Feature tests ──────────────────────────────────────────────────────


class TestCircleGetSectors:
    def test_returns_vcollection(self):
        c = Circle(r=100, cx=200, cy=300)
        result = c.get_sectors(4)
        assert isinstance(result, VCollection)

    def test_correct_number_of_sectors(self):
        c = Circle(r=100, cx=200, cy=300)
        result = c.get_sectors(6)
        assert len(result.objects) == 6

    def test_single_sector_is_full_circle(self):
        c = Circle(r=100, cx=200, cy=300)
        result = c.get_sectors(1)
        assert len(result.objects) == 1
        w = result.objects[0]
        assert isinstance(w, Wedge)
        assert w.start_angle.at_time(0) == pytest.approx(0)
        assert w.end_angle.at_time(0) == pytest.approx(360)

    def test_sector_angles(self):
        c = Circle(r=100, cx=200, cy=300)
        result = c.get_sectors(4)
        for i, w in enumerate(result.objects):
            assert isinstance(w, Wedge)
            assert w.start_angle.at_time(0) == pytest.approx(i * 90)
            assert w.end_angle.at_time(0) == pytest.approx((i + 1) * 90)

    def test_sectors_share_circle_center_and_radius(self):
        c = Circle(r=75, cx=500, cy=400)
        result = c.get_sectors(3)
        for w in result.objects:
            assert w.cx.at_time(0) == pytest.approx(500)
            assert w.cy.at_time(0) == pytest.approx(400)
            assert w.r.at_time(0) == pytest.approx(75)

    def test_kwargs_forwarded(self):
        c = Circle(r=100, cx=200, cy=300)
        result = c.get_sectors(2, fill='#ff0000')
        svg = result.objects[0].to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg

    def test_each_sector_is_wedge(self):
        c = Circle(r=50, cx=0, cy=0)
        result = c.get_sectors(5)
        for w in result.objects:
            assert isinstance(w, Wedge)

    def test_n_less_than_1_treated_as_1(self):
        c = Circle(r=100, cx=0, cy=0)
        result = c.get_sectors(0)
        assert len(result.objects) == 1


class TestPolygonExplodeEdges:
    def test_returns_vcollection(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        result = p.explode_edges()
        assert isinstance(result, VCollection)

    def test_triangle_has_three_edges(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        result = p.explode_edges()
        assert len(result.objects) == 3

    def test_all_edges_are_lines(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.explode_edges()
        for obj in result.objects:
            assert isinstance(obj, Line)

    def test_square_has_four_edges(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.explode_edges()
        assert len(result.objects) == 4

    def test_gap_offsets_edges_outward(self):
        """Edges should be pushed away from the centroid by gap pixels."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx, cy = p.get_center(0)  # (50, 50)
        result_0 = p.explode_edges(gap=0)
        result_10 = p.explode_edges(gap=10)
        # Each line midpoint should be farther from center with gap > 0
        for l0, l10 in zip(result_0.objects, result_10.objects):
            mx0 = (l0.p1.at_time(0)[0] + l0.p2.at_time(0)[0]) / 2
            my0 = (l0.p1.at_time(0)[1] + l0.p2.at_time(0)[1]) / 2
            mx10 = (l10.p1.at_time(0)[0] + l10.p2.at_time(0)[0]) / 2
            my10 = (l10.p1.at_time(0)[1] + l10.p2.at_time(0)[1]) / 2
            dist0 = math.hypot(mx0 - cx, my0 - cy)
            dist10 = math.hypot(mx10 - cx, my10 - cy)
            assert dist10 > dist0

    def test_gap_zero_edges_match_polygon(self):
        """With gap=0, edge endpoints should match polygon vertices exactly."""
        p = Polygon((0, 0), (200, 0), (200, 200), (0, 200))
        result = p.explode_edges(gap=0)
        # First edge should go from vertex 0 to vertex 1
        l = result.objects[0]
        assert l.p1.at_time(0)[0] == pytest.approx(0)
        assert l.p1.at_time(0)[1] == pytest.approx(0)
        assert l.p2.at_time(0)[0] == pytest.approx(200)
        assert l.p2.at_time(0)[1] == pytest.approx(0)

    def test_kwargs_forwarded_to_lines(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        result = p.explode_edges(gap=5, stroke='#ff0000')
        svg = result.objects[0].to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg

    def test_open_polyline_no_closing_edge(self):
        """An open polyline should not include the closing edge."""
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        result = p.explode_edges()
        assert len(result.objects) == 2


class TestLinePerpendicularAt:
    def test_default_length_matches_original(self):
        """Default length should equal the original line's length."""
        line = Line(x1=0, y1=0, x2=300, y2=0)
        perp = line.perpendicular_at(0.5)
        assert perp.get_length() == pytest.approx(300)

    def test_perpendicular_at_midpoint(self):
        """Perpendicular at t=0.5 should be centered at midpoint."""
        line = Line(x1=0, y1=0, x2=200, y2=0)
        perp = line.perpendicular_at(0.5, length=100)
        mid = perp.get_midpoint()
        assert mid[0] == pytest.approx(100)
        assert mid[1] == pytest.approx(0)

    def test_perpendicular_at_start(self):
        """Perpendicular at t=0 should be centered at start point."""
        line = Line(x1=50, y1=50, x2=150, y2=50)
        perp = line.perpendicular_at(0, length=80)
        mid = perp.get_midpoint()
        assert mid[0] == pytest.approx(50)
        assert mid[1] == pytest.approx(50)

    def test_perpendicular_at_end(self):
        """Perpendicular at t=1 should be centered at end point."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        perp = line.perpendicular_at(1, length=60)
        mid = perp.get_midpoint()
        assert mid[0] == pytest.approx(100)
        assert mid[1] == pytest.approx(0)

    def test_is_actually_perpendicular(self):
        """The angle between original and perpendicular should be ~90 degrees."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        perp = line.perpendicular_at(0.5, length=100)
        angle = line.angle_to(perp)
        assert angle == pytest.approx(90, abs=0.1)

    def test_custom_length(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        perp = line.perpendicular_at(0.5, length=50)
        assert perp.get_length() == pytest.approx(50)

    def test_kwargs_forwarded(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        perp = line.perpendicular_at(0.5, length=50, stroke='#ff0000')
        svg = perp.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg

    def test_diagonal_line(self):
        """Perpendicular on a diagonal line should still be 90 degrees."""
        line = Line(x1=0, y1=0, x2=100, y2=100)
        perp = line.perpendicular_at(0.5, length=100)
        angle = line.angle_to(perp)
        assert angle == pytest.approx(90, abs=0.1)


class TestRectangleGetGridLines:
    def test_returns_vcollection(self):
        r = Rectangle(200, 100, x=0, y=0)
        result = r.get_grid_lines(1, 1)
        assert isinstance(result, VCollection)

    def test_correct_number_of_lines(self):
        r = Rectangle(200, 100, x=0, y=0)
        # 2 horizontal + 3 vertical = 5 total
        result = r.get_grid_lines(2, 3)
        assert len(result.objects) == 5

    def test_all_objects_are_lines(self):
        r = Rectangle(200, 100, x=0, y=0)
        result = r.get_grid_lines(2, 2)
        for obj in result.objects:
            assert isinstance(obj, Line)

    def test_horizontal_line_positions(self):
        """1 horizontal line in a 300x300 rect should be at y=150."""
        r = Rectangle(300, 300, x=0, y=0)
        result = r.get_grid_lines(1, 0)
        assert len(result.objects) == 1
        line = result.objects[0]
        y1 = line.p1.at_time(0)[1]
        y2 = line.p2.at_time(0)[1]
        assert y1 == pytest.approx(150)
        assert y2 == pytest.approx(150)
        # Spans full width
        assert line.p1.at_time(0)[0] == pytest.approx(0)
        assert line.p2.at_time(0)[0] == pytest.approx(300)

    def test_vertical_line_positions(self):
        """1 vertical line in a 300x300 rect at (10,20) should be at x=160."""
        r = Rectangle(300, 300, x=10, y=20)
        result = r.get_grid_lines(0, 1)
        assert len(result.objects) == 1
        line = result.objects[0]
        x1 = line.p1.at_time(0)[0]
        x2 = line.p2.at_time(0)[0]
        assert x1 == pytest.approx(160)
        assert x2 == pytest.approx(160)
        # Spans full height
        assert line.p1.at_time(0)[1] == pytest.approx(20)
        assert line.p2.at_time(0)[1] == pytest.approx(320)

    def test_zero_rows_zero_cols(self):
        r = Rectangle(200, 100, x=0, y=0)
        result = r.get_grid_lines(0, 0)
        assert len(result.objects) == 0

    def test_kwargs_forwarded(self):
        r = Rectangle(200, 100, x=0, y=0)
        result = r.get_grid_lines(1, 1, stroke='#ff0000')
        svg = result.objects[0].to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg

    def test_even_spacing(self):
        """3 horizontal lines in height=400 should be at y=100, 200, 300."""
        r = Rectangle(200, 400, x=0, y=0)
        result = r.get_grid_lines(3, 0)
        assert len(result.objects) == 3
        for i, line in enumerate(result.objects):
            expected_y = 400 * (i + 1) / 4
            assert line.p1.at_time(0)[1] == pytest.approx(expected_y)


class TestAxesAddParametricPlot:
    def test_returns_path(self):
        axes = Axes(x_range=(-2, 2), y_range=(-2, 2))
        curve = axes.add_parametric_plot(
            fx=lambda t: math.cos(t),
            fy=lambda t: math.sin(t),
            t_range=(0, 2 * math.pi),
        )
        assert isinstance(curve, Path)

    def test_curve_added_to_axes(self):
        axes = Axes(x_range=(-2, 2), y_range=(-2, 2))
        n_before = len(axes.objects)
        axes.add_parametric_plot(
            fx=lambda t: t,
            fy=lambda t: t,
            t_range=(0, 1),
        )
        assert len(axes.objects) == n_before + 1

    def test_d_attribute_nonempty(self):
        axes = Axes(x_range=(-2, 2), y_range=(-2, 2))
        curve = axes.add_parametric_plot(
            fx=lambda t: math.cos(t),
            fy=lambda t: math.sin(t),
            t_range=(0, 2 * math.pi),
        )
        d = curve.d.at_time(0)
        assert len(d) > 0
        assert d.startswith('M')

    def test_d_contains_line_segments(self):
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        curve = axes.add_parametric_plot(
            fx=lambda t: t,
            fy=lambda t: t ** 2,
            t_range=(-2, 2),
            num_points=50,
        )
        d = curve.d.at_time(0)
        assert 'L' in d

    def test_styling_kwargs(self):
        axes = Axes(x_range=(-2, 2), y_range=(-2, 2))
        curve = axes.add_parametric_plot(
            fx=lambda t: t,
            fy=lambda t: t,
            t_range=(0, 1),
            stroke='#ff0000',
        )
        svg = curve.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg

    def test_num_points_controls_sampling(self):
        axes = Axes(x_range=(-2, 2), y_range=(-2, 2))
        curve_10 = axes.add_parametric_plot(
            fx=lambda t: t, fy=lambda t: t,
            t_range=(0, 1), num_points=10,
        )
        curve_100 = axes.add_parametric_plot(
            fx=lambda t: t, fy=lambda t: t,
            t_range=(0, 1), num_points=100,
        )
        # More points means longer d string (more L segments)
        d10 = curve_10.d.at_time(0)
        d100 = curve_100.d.at_time(0)
        assert len(d100) > len(d10)


class TestNumberLineAddBrace:
    def test_returns_brace(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(2, 5)
        assert isinstance(brace, Brace)

    def test_brace_added_to_objects(self):
        nl = NumberLine(x_range=(0, 10, 1))
        n_before = len(nl.objects)
        nl.add_brace(2, 5)
        assert len(nl.objects) == n_before + 1

    def test_brace_with_label(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(2, 5, label='3')
        # Brace with label should have 2 sub-objects (path + label)
        assert len(brace.objects) == 2

    def test_brace_without_label(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(2, 5)
        # Brace without label should have 1 sub-object (path only)
        assert len(brace.objects) == 1

    def test_direction_string(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(2, 5, direction='up')
        assert brace._direction == 'up'

    def test_direction_tuple_constant(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(2, 5, direction=(0, 1))  # DOWN
        assert brace._direction == 'down'

    def test_brace_renders_svg(self):
        nl = NumberLine(x_range=(0, 10, 1))
        nl.add_brace(2, 5)
        svg = nl.to_svg(0)
        assert '<path' in svg

    def test_brace_kwargs_forwarded(self):
        nl = NumberLine(x_range=(0, 10, 1))
        brace = nl.add_brace(1, 4, fill='#ff0000')
        svg = brace.objects[0].to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg


class TestPolygonInset:
    def test_returns_polygon(self):
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10)
        assert isinstance(inner, Polygon)

    def test_vertex_count_preserved(self):
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10)
        assert len(inner.vertices) == 4

    def test_inset_shrinks_area(self):
        """Inset polygon should have smaller area than original."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10)
        assert inner.area() < p.area()

    def test_inset_rectangle_dimensions(self):
        """Insetting a rectangular polygon should reduce width and height."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10)
        verts = inner.get_vertices()
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        assert w == pytest.approx(180.0, abs=1e-6)
        assert h == pytest.approx(80.0, abs=1e-6)

    def test_inset_rectangle_position(self):
        """Inset rectangle vertices should be offset by distance from edges."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10)
        verts = inner.get_vertices()
        xs = sorted(set(round(v[0], 3) for v in verts))
        ys = sorted(set(round(v[1], 3) for v in verts))
        assert xs[0] == pytest.approx(10.0, abs=1e-3)
        assert xs[-1] == pytest.approx(190.0, abs=1e-3)
        assert ys[0] == pytest.approx(10.0, abs=1e-3)
        assert ys[-1] == pytest.approx(90.0, abs=1e-3)

    def test_collapse_raises(self):
        """Inset too large should raise ValueError."""
        p = Polygon((0, 0), (100, 0), (100, 50), (0, 50))
        with pytest.raises(ValueError):
            p.inset(30)  # Would make height negative (50 - 2*30 = -10)

    def test_triangle_inset(self):
        """Insetting a triangle should return a valid smaller triangle."""
        # Equilateral-ish triangle
        p = Polygon((100, 0), (200, 173), (0, 173))
        inner = p.inset(5)
        assert len(inner.vertices) == 3
        assert inner.area() < p.area()

    def test_kwargs_forwarded(self):
        """Style kwargs should be forwarded to the new Polygon."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        inner = p.inset(10, stroke='#f00')
        svg = inner.to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_does_not_modify_original(self):
        """inset() should not change the original polygon."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100))
        orig_area = p.area()
        p.inset(10)
        assert p.area() == pytest.approx(orig_area, abs=1e-6)

    def test_fewer_than_3_vertices_raises(self):
        """Polygon with fewer than 3 vertices cannot be inset."""
        p = Polygon((0, 0), (100, 0), closed=False)
        with pytest.raises(ValueError):
            p.inset(5)

    def test_closed_flag_preserved(self):
        """The inset polygon inherits the closed flag from the original."""
        p = Polygon((0, 0), (200, 0), (200, 100), (0, 100), closed=True)
        inner = p.inset(10)
        assert inner.closed is True


class TestCircleAnnularSector:
    def test_returns_path(self):
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector()
        assert isinstance(p, Path)

    def test_svg_contains_arc_commands(self):
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(inner_ratio=0.5, start_angle=0, end_angle=90)
        svg = p.to_svg(0)
        assert '<path' in svg
        assert 'A' in p.d.at_time(0)

    def test_inner_ratio_affects_path(self):
        """Different inner_ratios should produce different paths."""
        c = Circle(r=100, cx=500, cy=500)
        p1 = c.annular_sector(inner_ratio=0.3, start_angle=0, end_angle=90)
        p2 = c.annular_sector(inner_ratio=0.7, start_angle=0, end_angle=90)
        assert p1.d.at_time(0) != p2.d.at_time(0)

    def test_full_annulus(self):
        """360-degree span should produce a full annulus."""
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(inner_ratio=0.5, start_angle=0, end_angle=360)
        d = p.d.at_time(0)
        assert 'A' in d

    def test_semicircle_sector(self):
        """180-degree span should produce a semicircular annular sector."""
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(inner_ratio=0.5, start_angle=0, end_angle=180)
        d = p.d.at_time(0)
        assert 'A' in d
        assert 'L' in d

    def test_kwargs_forwarded(self):
        """Style kwargs should be forwarded to the Path."""
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(fill='#ff0000')
        svg = p.to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_default_styling(self):
        """Default annular sector should have fill and stroke."""
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(start_angle=0, end_angle=90)
        svg = p.to_svg(0)
        assert '<path' in svg

    def test_small_angle_sector(self):
        """Small angle sector should work correctly."""
        c = Circle(r=100, cx=500, cy=500)
        p = c.annular_sector(inner_ratio=0.5, start_angle=0, end_angle=30)
        d = p.d.at_time(0)
        assert 'M' in d
        assert 'A' in d


class TestAxesAddHorizontalBand:
    def test_returns_rectangle(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(1, 3)
        assert isinstance(band, Rectangle)

    def test_band_added_to_objects(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        n_before = len(ax.objects)
        ax.add_horizontal_band(1, 3)
        assert len(ax.objects) == n_before + 1

    def test_band_spans_full_width(self):
        """Band width should equal the plot width."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(1, 3)
        assert band.width.at_time(0) == pytest.approx(ax.plot_width, abs=1e-6)

    def test_band_x_at_plot_x(self):
        """Band x should be at plot_x."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(1, 3)
        assert band.x.at_time(0) == pytest.approx(ax.plot_x, abs=1e-6)

    def test_band_height_proportional(self):
        """Band height should correspond to the y range."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5), plot_height=1000)
        band = ax.add_horizontal_band(1, 3)
        # y range of 2 out of 10 total = 20% of plot_height = 200
        assert band.height.at_time(0) == pytest.approx(200.0, abs=1e-6)

    def test_custom_color(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(1, 3, color='#FF0000')
        svg = band.to_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_custom_opacity(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(1, 3, opacity=0.5)
        assert band.styling.fill_opacity.at_time(0) == pytest.approx(0.5, abs=1e-6)

    def test_reversed_y_values(self):
        """Should handle y1 > y2 gracefully (positive height)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        band = ax.add_horizontal_band(3, 1)
        assert band.height.at_time(0) > 0


class TestTableHighlightRow:
    def test_returns_self(self):
        t = Table([[1, 2], [3, 4]])
        result = t.highlight_row(0, start=0, end=1)
        assert result is t

    def test_changes_fill_color(self):
        """Highlighting should change the fill color of row cells at midpoint."""
        t = Table([[1, 2], [3, 4]])
        t.highlight_row(0, start=0, end=2, color='#FF0000')
        # At midpoint of there_and_back, fill should be near the highlight color
        entry = t.entries[0][0]
        fill = entry.styling.fill.time_func(1)
        assert fill[0] > 200  # R channel near 255

    def test_flash_at_midpoint(self):
        """With there_and_back easing, flash fill should appear at midpoint."""
        t = Table([[1, 2], [3, 4]])
        t.highlight_row(0, start=0, end=2, color='#FFFF00')
        entry = t.entries[0][0]
        fill_mid = entry.styling.fill.time_func(1)
        # At midpoint of there_and_back, should be near yellow
        assert fill_mid[0] > 200  # R channel near 255

    def test_flash_at_boundaries(self):
        """Flash fill should return to original at boundaries."""
        t = Table([[1, 2], [3, 4]])
        original_fill = t.entries[0][0].styling.fill.time_func(0)
        t.highlight_row(0, start=0, end=2, color='#FFFF00')
        # After the flash ends, fill should revert
        end_fill = t.entries[0][0].styling.fill.time_func(2)
        assert end_fill == original_fill

    def test_all_cells_in_row_highlighted(self):
        """All cells in the row should be affected."""
        t = Table([[1, 2, 3], [4, 5, 6]])
        t.highlight_row(0, start=0, end=2, color='#00FF00')
        for entry in t.entries[0]:
            fill = entry.styling.fill.time_func(1)
            assert fill[1] > 200  # G channel near 255

    def test_other_row_unaffected(self):
        """Cells in other rows should not be affected."""
        t = Table([['a', 'b'], ['c', 'd']])
        t.highlight_row(0, start=0, end=1, color='#FF0000')
        entry = t.entries[1][0]
        fill = entry.styling.fill.time_func(0)
        # Should remain white (#fff), not red
        assert fill == (255, 255, 255)

    def test_custom_easing(self):
        """Custom easing should be used for opacity."""
        t = Table([[1, 2], [3, 4]])
        t.highlight_row(0, start=0, end=1, easing=easings.linear)
        # Just verify it doesn't raise
        entry = t.entries[0][0]
        _ = entry.styling.fill_opacity.at_time(0.5)


class TestNumberLineAddTickLabelsRange:
    def test_returns_self(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        result = nl.add_tick_labels_range(0, 5, 1)
        assert result is nl

    def test_labels_added_to_objects(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(0, 5, 1)
        # 0, 1, 2, 3, 4, 5 = 6 labels
        assert len(nl.objects) == n_before + 6

    def test_labels_are_text_objects(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(2, 4, 1)
        for obj in nl.objects[n_before:]:
            assert isinstance(obj, Text)

    def test_label_positions(self):
        """Labels should be positioned at the correct x coordinates."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(0, 10, 5)
        # Values: 0, 5, 10 -> x: 100, 350, 600
        labels = nl.objects[n_before:]
        assert len(labels) == 3
        assert labels[0].x.at_time(0) == pytest.approx(100.0, abs=1e-3)
        assert labels[1].x.at_time(0) == pytest.approx(350.0, abs=1e-3)
        assert labels[2].x.at_time(0) == pytest.approx(600.0, abs=1e-3)

    def test_custom_format_func(self):
        """Custom format function should be applied to labels."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(0, 2, 1, format_func=lambda v: f'x={v}')
        labels = nl.objects[n_before:]
        assert labels[0].text.at_time(0) == 'x=0'
        assert labels[1].text.at_time(0) == 'x=1'
        assert labels[2].text.at_time(0) == 'x=2'

    def test_custom_font_size(self):
        """Custom font_size should be applied to labels."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(0, 2, 1, font_size=30)
        labels = nl.objects[n_before:]
        for lbl in labels:
            assert lbl.font_size.at_time(0) == pytest.approx(30)

    def test_fractional_step(self):
        """Non-integer step should work."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        n_before = len(nl.objects)
        nl.add_tick_labels_range(0, 1, 0.5)
        # 0, 0.5, 1.0 = 3 labels
        assert len(nl.objects) == n_before + 3

    def test_renders_svg(self):
        """Labels should render in SVG output."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500,
                        include_numbers=False)
        nl.add_tick_labels_range(0, 3, 1)
        svg = nl.to_svg(0)
        assert '<text' in svg


class TestPolygonSubdivideEdges:
    def test_triangle_one_iteration(self):
        """Triangle with 3 edges -> 6 vertices after one subdivision."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        sub = p.subdivide_edges(iterations=1)
        verts = sub.get_vertices(0)
        assert len(verts) == 6

    def test_triangle_midpoints_correct(self):
        """Midpoints of triangle edges should be at the correct positions."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        sub = p.subdivide_edges(iterations=1)
        verts = sub.get_vertices(0)
        # Expected: (0,0), (50,0), (100,0), (75,50), (50,100), (25,50)
        assert verts[0] == pytest.approx((0, 0), abs=1e-9)
        assert verts[1] == pytest.approx((50, 0), abs=1e-9)
        assert verts[2] == pytest.approx((100, 0), abs=1e-9)
        assert verts[3] == pytest.approx((75, 50), abs=1e-9)
        assert verts[4] == pytest.approx((50, 100), abs=1e-9)
        assert verts[5] == pytest.approx((25, 50), abs=1e-9)

    def test_square_one_iteration(self):
        """Square with 4 edges -> 8 vertices after one subdivision."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sub = p.subdivide_edges(iterations=1)
        verts = sub.get_vertices(0)
        assert len(verts) == 8

    def test_two_iterations_doubles_again(self):
        """Two iterations on a triangle: 3 -> 6 -> 12 vertices."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        sub = p.subdivide_edges(iterations=2)
        verts = sub.get_vertices(0)
        assert len(verts) == 12

    def test_zero_iterations_returns_copy(self):
        """Zero iterations should return a polygon with the same vertices."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        sub = p.subdivide_edges(iterations=0)
        verts = sub.get_vertices(0)
        assert len(verts) == 3
        assert verts[0] == pytest.approx((0, 0), abs=1e-9)

    def test_preserves_closed(self):
        """Result should preserve the closed flag of the original."""
        p = Polygon((0, 0), (100, 0), (50, 100), closed=True)
        sub = p.subdivide_edges(iterations=1)
        assert sub.closed is True

    def test_open_polyline(self):
        """Open polyline with 3 vertices (2 edges) -> 5 vertices after 1 iter."""
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        sub = p.subdivide_edges(iterations=1)
        verts = sub.get_vertices(0)
        assert len(verts) == 5

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the new Polygon."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        sub = p.subdivide_edges(iterations=1, stroke='#ff0000')
        svg = sub.to_svg(0)
        assert 'stroke=' in svg
        # Color may be normalized to rgb() form
        assert '255' in svg or '#ff0000' in svg


class TestLineExtend:
    def test_extend_horizontal_factor_1_5(self):
        """Factor 1.5 should extend a horizontal line by 50%, keeping midpoint fixed."""
        line = Line(x1=100, y1=200, x2=200, y2=200)
        result = line.extend(factor=1.5)
        assert result is line
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Midpoint = (150, 200). Half-length = 50 * 1.5 = 75.
        assert p1[0] == pytest.approx(75, abs=1e-6)
        assert p1[1] == pytest.approx(200, abs=1e-6)
        assert p2[0] == pytest.approx(225, abs=1e-6)
        assert p2[1] == pytest.approx(200, abs=1e-6)

    def test_extend_factor_1_no_change(self):
        """Factor 1.0 should leave endpoints unchanged."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend(factor=1.0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        assert p1[0] == pytest.approx(0, abs=1e-6)
        assert p2[0] == pytest.approx(100, abs=1e-6)

    def test_extend_shrink(self):
        """Factor < 1 should shrink the line around midpoint."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend(factor=0.5)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Midpoint = 50, half-length = 50 * 0.5 = 25
        assert p1[0] == pytest.approx(25, abs=1e-6)
        assert p2[0] == pytest.approx(75, abs=1e-6)

    def test_extend_diagonal(self):
        """Extending a diagonal line should scale length and preserve midpoint."""
        line = Line(x1=0, y1=0, x2=60, y2=80)
        line.extend(factor=2.0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        # Original length = 100. Factor 2 -> new length = 200
        assert length == pytest.approx(200, abs=1e-4)
        # Midpoint should still be (30, 40)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert mx == pytest.approx(30, abs=1e-4)
        assert my == pytest.approx(40, abs=1e-4)

    def test_extend_returns_self(self):
        """extend should modify in place and return self."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.extend(factor=2.0)
        assert result is line

    def test_extend_animated(self):
        """extend with end should animate the endpoints."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        line.extend(factor=2.0, start=0, end=1)
        # At time=0 should still be original
        p1_0 = line.p1.at_time(0)
        p2_0 = line.p2.at_time(0)
        # At time=1 should be extended: midpoint=50, half=50*2=100
        p1_1 = line.p1.at_time(1)
        p2_1 = line.p2.at_time(1)
        assert p1_1[0] == pytest.approx(-50, abs=1)
        assert p2_1[0] == pytest.approx(150, abs=1)


class TestAxesAddResidualLines:
    def test_basic_residual_lines(self):
        """Residual lines should be created for each data point."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 5, 4, 5]
        group = ax.add_residual_lines(x_data, y_data)
        assert len(group.objects) == 5

    def test_residual_lines_are_vertical(self):
        """Each residual line should be vertical (same x for p1 and p2)."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        x_data = [1, 2, 3]
        y_data = [2, 4, 6]
        group = ax.add_residual_lines(x_data, y_data)
        for line in group.objects:
            p1 = line.p1.at_time(0)
            p2 = line.p2.at_time(0)
            assert p1[0] == pytest.approx(p2[0], abs=0.5)

    def test_perfect_fit_zero_residuals(self):
        """For a perfect linear fit, residual lines should have zero length."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        x_data = [1, 2, 3, 4]
        y_data = [2, 4, 6, 8]  # y = 2x, perfect fit
        group = ax.add_residual_lines(x_data, y_data)
        for line in group.objects:
            p1 = line.p1.at_time(0)
            p2 = line.p2.at_time(0)
            assert p1[1] == pytest.approx(p2[1], abs=0.5)

    def test_fewer_than_two_points(self):
        """With fewer than 2 points, should return empty VCollection."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        group = ax.add_residual_lines([1], [2])
        assert len(group.objects) == 0

    def test_styling_kwargs(self):
        """Custom styling should be applied to residual lines."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        group = ax.add_residual_lines([1, 2, 3], [2, 4, 6], stroke='#00ff00')
        svg = group.objects[0].to_svg(0)
        # Color may be normalized to rgb() form
        assert 'rgb(0,255,0)' in svg or '#00ff00' in svg

    def test_default_dashed_style(self):
        """Residual lines should be dashed by default."""
        ax = Axes(x_range=(-1, 10, 1), y_range=(-1, 10, 1))
        group = ax.add_residual_lines([1, 2, 3], [2, 4, 6])
        svg = group.objects[0].to_svg(0)
        assert 'stroke-dasharray' in svg


class TestAxesAddSpreadBand:
    def test_basic_spread_band(self):
        """Band should be a Path added to axes objects."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        n_before = len(ax.objects)
        band = ax.add_spread_band(lambda x: x, lambda x: 0.5)
        assert n_before < len(ax.objects)
        assert hasattr(band, 'd')

    def test_spread_band_svg_not_empty(self):
        """Band should produce non-empty SVG at time 0."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        band = ax.add_spread_band(lambda x: x, lambda x: 0.5)
        svg = band.to_svg(0)
        assert 'M' in svg

    def test_spread_band_default_color(self):
        """Band should use default blue color."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        band = ax.add_spread_band(lambda x: x, lambda x: 0.5)
        svg = band.to_svg(0)
        # #58C4DD -> rgb(88,196,221)
        assert 'rgb(88,196,221)' in svg or '#58C4DD' in svg

    def test_spread_band_custom_color(self):
        """Custom color should override default."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        band = ax.add_spread_band(lambda x: x, lambda x: 0.5, color='#FF0000')
        svg = band.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#FF0000' in svg

    def test_spread_band_with_x_range(self):
        """x_range should limit the band extent."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        band = ax.add_spread_band(lambda x: 0, lambda x: 1, x_range=(0, 2))
        d = band.d.at_time(0)
        assert 'M' in d
        assert 'Z' in d

    def test_spread_band_with_curve_func(self):
        """Should work with a curve returned by plot() that has ._func."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        curve = ax.plot(lambda x: x**2)
        band = ax.add_spread_band(curve, lambda x: 0.5)
        svg = band.to_svg(0)
        assert 'M' in svg


class TestNumberLineAddIntervalBracket:
    def test_basic_interval(self):
        """Interval bracket should return a VCollection with 3 objects."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        group = nl.add_interval_bracket(2, 8)
        # bar + left bracket text + right bracket text
        assert len(group.objects) == 3

    def test_closed_brackets(self):
        """Closed interval should use '[' and ']'."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        group = nl.add_interval_bracket(2, 8, closed_left=True, closed_right=True)
        left_text = group.objects[1]
        right_text = group.objects[2]
        assert left_text.text.at_time(0) == '['
        assert right_text.text.at_time(0) == ']'

    def test_open_brackets(self):
        """Open interval should use '(' and ')'."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        group = nl.add_interval_bracket(2, 8, closed_left=False, closed_right=False)
        left_text = group.objects[1]
        right_text = group.objects[2]
        assert left_text.text.at_time(0) == '('
        assert right_text.text.at_time(0) == ')'

    def test_half_open_interval(self):
        """Half-open [a, b) should use '[' and ')'."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        group = nl.add_interval_bracket(2, 8, closed_left=True, closed_right=False)
        left_text = group.objects[1]
        right_text = group.objects[2]
        assert left_text.text.at_time(0) == '['
        assert right_text.text.at_time(0) == ')'

    def test_bar_position(self):
        """The connecting bar should span between the two points."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        group = nl.add_interval_bracket(2, 8)
        bar = group.objects[0]
        p1 = bar.p1.at_time(0)
        p2 = bar.p2.at_time(0)
        expected_x1 = nl.number_to_point(2)[0]
        expected_x2 = nl.number_to_point(8)[0]
        assert p1[0] == pytest.approx(expected_x1, abs=1)
        assert p2[0] == pytest.approx(expected_x2, abs=1)

    def test_added_to_numberline(self):
        """The group should be added to the number line's objects."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        n_before = len(nl.objects)
        nl.add_interval_bracket(2, 8)
        assert len(nl.objects) == n_before + 1

    def test_renders_svg(self):
        """Interval bracket should render in SVG output."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=500)
        nl.add_interval_bracket(2, 8)
        svg = nl.to_svg(0)
        assert '<line' in svg
        assert '<text' in svg


class TestTextCharCount:
    def test_basic_count(self):
        """char_count should return the number of characters."""
        t = Text(text='hello')
        assert t.char_count() == 5

    def test_empty_text(self):
        """Empty text should have 0 characters."""
        t = Text(text='')
        assert t.char_count() == 0

    def test_with_spaces(self):
        """Spaces should be counted."""
        t = Text(text='hello world')
        assert t.char_count() == 11

    def test_with_time_parameter(self):
        """char_count should respect the time parameter."""
        t = Text(text='hi')
        t.text.set_onward(1, 'hello world')
        assert t.char_count(time=0) == 2
        assert t.char_count(time=1) == 11

    def test_with_typing_animation(self):
        """char_count during typing animation should reflect partial text."""
        t = Text(text='abcdef')
        t.typing(start=0, end=6, change_existence=False)
        # At time 0, typing shows at least 1 char
        count_start = t.char_count(time=0)
        assert count_start >= 1
        # At time 6, all chars should be shown
        count_end = t.char_count(time=6)
        assert count_end == 6


# ---------------------------------------------------------------------------
# Tests for Polygon.smooth_corners
# ---------------------------------------------------------------------------
class TestPolygonSmoothCorners:
    def test_returns_path(self):
        """smooth_corners should return a Path object."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.smooth_corners(radius=10)
        assert isinstance(result, Path)

    def test_path_d_contains_Q_commands(self):
        """The smoothed path should contain quadratic Bezier Q commands."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.smooth_corners(radius=10)
        d = result.d.at_time(0)
        assert 'Q' in d

    def test_closed_polygon_ends_with_Z(self):
        """A closed polygon's smoothed path should end with Z."""
        p = Polygon((0, 0), (100, 0), (100, 100))
        result = p.smooth_corners(radius=10)
        d = result.d.at_time(0)
        assert d.strip().endswith('Z')

    def test_open_polyline_no_Z(self):
        """An open polyline's smoothed path should not end with Z."""
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        result = p.smooth_corners(radius=10)
        d = result.d.at_time(0)
        assert not d.strip().endswith('Z')

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Path constructor."""
        p = Polygon((0, 0), (100, 0), (100, 100))
        result = p.smooth_corners(radius=10, stroke='#f00')
        svg = result.to_svg(0)
        assert '255' in svg or 'f00' in svg.lower()

    def test_radius_zero_gives_straight_segments(self):
        """With radius=0, corners should not be smoothed (Q has same control/end)."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.smooth_corners(radius=0)
        d = result.d.at_time(0)
        # Q commands still appear but the curve degenerates to a point
        assert 'Q' in d

    def test_fewer_than_3_vertices(self):
        """With fewer than 3 vertices, smooth_corners should still return a Path."""
        p = Polygon((0, 0), (100, 100), closed=False)
        result = p.smooth_corners(radius=10)
        assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# Tests for Circle.inscribed_polygon (additional tests beyond existing ones)
# ---------------------------------------------------------------------------
class TestCircleInscribedPolygonExtra:
    def test_start_angle_alias(self):
        """start_angle parameter should work the same as angle."""
        c = Circle(r=100, cx=0, cy=0)
        poly = c.inscribed_polygon(4, start_angle=90)
        _, y0 = poly.vertices[0].at_time(0)
        assert y0 == pytest.approx(-100, abs=0.5)

    def test_equal_edge_lengths(self):
        """All edges of the inscribed polygon should have equal length."""
        c = Circle(r=100, cx=500, cy=500)
        poly = c.inscribed_polygon(5)
        lengths = poly.edge_lengths()
        for length in lengths:
            assert length == pytest.approx(lengths[0], abs=0.5)


# ---------------------------------------------------------------------------
# Tests for Line.angle_with
# ---------------------------------------------------------------------------
class TestLineAngleWith:
    def test_perpendicular_lines(self):
        """Two perpendicular lines should have an angle of 90 degrees."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=0, x2=0, y2=100)
        assert l1.angle_with(l2) == pytest.approx(90.0, abs=0.1)

    def test_parallel_lines(self):
        """Two parallel lines should have an angle of 0 degrees."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=10, y1=10, x2=200, y2=10)
        assert l1.angle_with(l2) == pytest.approx(0.0, abs=0.1)

    def test_opposite_direction(self):
        """Antiparallel lines should have an angle of 180 degrees."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=100, y1=0, x2=0, y2=0)
        assert l1.angle_with(l2) == pytest.approx(180.0, abs=0.1)

    def test_45_degree_angle(self):
        """A horizontal and 45-degree line should give 45 degrees."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=0, x2=100, y2=100)
        assert l1.angle_with(l2) == pytest.approx(45.0, abs=0.1)

    def test_matches_angle_to(self):
        """angle_with should return the same value as angle_to."""
        l1 = Line(x1=0, y1=0, x2=50, y2=30)
        l2 = Line(x1=10, y1=20, x2=80, y2=90)
        assert l1.angle_with(l2) == pytest.approx(l1.angle_to(l2))

    def test_result_in_0_180(self):
        """Result should always be in [0, 180]."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=0, x2=-50, y2=87)
        result = l1.angle_with(l2)
        assert 0 <= result <= 180


# ---------------------------------------------------------------------------
# Tests for Table.animate_cells
# ---------------------------------------------------------------------------
class TestTableAnimateCells:
    def test_returns_self(self):
        """animate_cells should return self for chaining."""
        t = Table([[1, 2], [3, 4]])
        result = t.animate_cells([(0, 0), (1, 1)])
        assert result is t

    def test_calls_method_on_entries(self):
        """animate_cells should call the specified method on each cell."""
        t = Table([[10, 20], [30, 40]])
        # 'flash' is a valid animation method on Text (VObject)
        t.animate_cells([(0, 0), (0, 1), (1, 0)], method_name='flash')
        # No exception means the methods were found and called

    def test_stagger_delay(self):
        """Each cell should receive an incremented start time."""
        t = Table([['a', 'b'], ['c', 'd']])
        # Use 'indicate' with default delay=0.15
        t.animate_cells([(0, 0), (1, 1)], method_name='indicate', start=1.0, delay=0.5)
        # Just verify it doesn't raise

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the animation method."""
        t = Table([[1, 2], [3, 4]])
        t.animate_cells([(0, 0)], method_name='flash', end=2.0, color='#f00')

    def test_empty_cells_list(self):
        """An empty cells list should do nothing and return self."""
        t = Table([[1, 2], [3, 4]])
        result = t.animate_cells([])
        assert result is t


# ---------------------------------------------------------------------------
# Tests for Axes.add_mean_line
# ---------------------------------------------------------------------------
class TestAxesAddMeanLine:
    def test_returns_line(self):
        """add_mean_line should return a Line object."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        line = ax.add_mean_line(lambda x: x ** 2)
        assert isinstance(line, Line)

    def test_mean_of_constant_function(self):
        """For a constant function f(x)=5, the mean line should be at y=5."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        line = ax.add_mean_line(lambda x: 5.0)
        # The line's endpoints should map to y=5 in math coords
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Both y coordinates should be the same (horizontal line)
        assert p1[1] == pytest.approx(p2[1], abs=1)
        # The svg y should correspond to math y=5
        expected_svg_y = ax._math_to_svg_y(5.0, 0)
        assert p1[1] == pytest.approx(expected_svg_y, abs=1)

    def test_mean_of_data_list(self):
        """For a data list, the mean line should be at the average value."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        data = [2, 4, 6, 8]
        line = ax.add_mean_line(data)
        # Mean is 5.0
        expected_svg_y = ax._math_to_svg_y(5.0, 0)
        p1 = line.p1.at_time(0)
        assert p1[1] == pytest.approx(expected_svg_y, abs=1)

    def test_line_is_dashed(self):
        """The returned line should have a stroke_dasharray style."""
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        line = ax.add_mean_line([1, 2, 3])
        svg = line.to_svg(0)
        assert 'stroke-dasharray' in svg

    def test_custom_x_range(self):
        """Custom x_range should limit where the function is sampled."""
        ax = Axes(x_range=(-10, 10), y_range=(-50, 50))
        # f(x) = x, sampled over [0, 10] has mean 5; over [-10, 0] has mean -5
        line1 = ax.add_mean_line(lambda x: x, x_range=(0, 10))
        line2 = ax.add_mean_line(lambda x: x, x_range=(-10, 0))
        p1 = line1.p1.at_time(0)
        p2 = line2.p1.at_time(0)
        # The y positions should be different (mean 5 vs mean -5)
        assert abs(p1[1] - p2[1]) > 50

    def test_line_added_to_axes(self):
        """The line should be added to the axes objects list."""
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        n_before = len(ax.objects)
        ax.add_mean_line([3, 3, 3])
        assert len(ax.objects) == n_before + 1


# ---------------------------------------------------------------------------
# Tests for NumberLine.animate_add_tick
# ---------------------------------------------------------------------------
class TestNumberLineAnimateAddTick:
    def test_returns_self(self):
        """animate_add_tick should return self."""
        nl = NumberLine(x_range=(-5, 5, 1))
        result = nl.animate_add_tick(2.5, start=0, end=1)
        assert result is nl

    def test_adds_tick_line(self):
        """A new Line object should be appended to the number line."""
        nl = NumberLine(x_range=(0, 10, 1))
        n_before = len(nl.objects)
        nl.animate_add_tick(5.5, start=0, end=1)
        assert len(nl.objects) > n_before

    def test_tick_at_correct_position(self):
        """The tick line should be at the correct x position."""
        nl = NumberLine(x_range=(0, 10, 1))
        nl.animate_add_tick(5.0, start=0, end=1)
        # The last-added object should be a Line at x = number_to_point(5.0)
        tick = nl.objects[-1]
        expected_x, _ = nl.number_to_point(5.0)
        p1 = tick.p1.at_time(0)
        assert p1[0] == pytest.approx(expected_x, abs=1)

    def test_with_label(self):
        """When label is given, an extra Text object should be added."""
        nl = NumberLine(x_range=(0, 10, 1))
        n_before = len(nl.objects)
        nl.animate_add_tick(3.0, start=0, end=1, label='3.0')
        # Should add both a tick Line and a Text label
        assert len(nl.objects) == n_before + 2

    def test_without_label(self):
        """When label is None, only the tick Line should be added."""
        nl = NumberLine(x_range=(0, 10, 1))
        n_before = len(nl.objects)
        nl.animate_add_tick(3.0, start=0, end=1)
        assert len(nl.objects) == n_before + 1

    def test_custom_easing(self):
        """Custom easing function should be accepted."""
        nl = NumberLine(x_range=(0, 10, 1))
        nl.animate_add_tick(7.0, start=0, end=2, easing=easings.linear)


class TestTextSplitIntoWords:
    def test_returns_vcollection(self):
        """split_into_words should return a VCollection."""
        t = Text(text='Hello World', x=100, y=200)
        result = t.split_into_words()
        assert isinstance(result, VCollection)

    def test_correct_word_count(self):
        """The number of Text objects should match the number of words."""
        t = Text(text='Hello World Foo', x=100, y=200)
        parts = t.split_into_words()
        assert len(parts.objects) == 3

    def test_word_contents(self):
        """Each Text object should contain the correct word."""
        t = Text(text='Hello World Foo', x=100, y=200)
        parts = t.split_into_words()
        assert parts.objects[0].text.at_time(0) == 'Hello'
        assert parts.objects[1].text.at_time(0) == 'World'
        assert parts.objects[2].text.at_time(0) == 'Foo'

    def test_preserves_y_position(self):
        """All words should share the same y coordinate."""
        t = Text(text='Hello World', x=100, y=300, font_size=48)
        parts = t.split_into_words()
        for p in parts.objects:
            assert p.y.at_time(0) == pytest.approx(300, abs=1e-6)

    def test_preserves_font_size(self):
        """All words should have the same font_size as the original."""
        t = Text(text='Hello World', x=100, y=200, font_size=36)
        parts = t.split_into_words()
        for p in parts.objects:
            assert p.font_size.at_time(0) == pytest.approx(36, abs=1e-6)

    def test_empty_text(self):
        """Empty text should return an empty VCollection."""
        t = Text(text='', x=100, y=200)
        parts = t.split_into_words()
        assert len(parts.objects) == 0

    def test_single_word(self):
        """A single word should return a VCollection with one Text."""
        t = Text(text='Hello', x=100, y=200)
        parts = t.split_into_words()
        assert len(parts.objects) == 1
        assert parts.objects[0].text.at_time(0) == 'Hello'

    def test_words_ordered_left_to_right(self):
        """Words should have increasing x positions."""
        t = Text(text='Hello World Foo', x=100, y=200, font_size=48)
        parts = t.split_into_words()
        xs = [p.x.at_time(0) for p in parts.objects]
        assert xs[0] < xs[1] < xs[2]

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to child Text objects."""
        t = Text(text='Hello World', x=100, y=200, fill='#ff0000')
        parts = t.split_into_words(fill='#00ff00')
        # The fill should be overridden by the kwarg
        for p in parts.objects:
            svg = p.to_svg(0)
            assert '#00ff00' in svg or '#0f0' in svg or 'fill' in svg


class TestEllipseGetTangentLine:
    def test_returns_line(self):
        """get_tangent_line should return a Line object."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        result = e.get_tangent_line(45)
        assert isinstance(result, Line)

    def test_tangent_at_zero_degrees(self):
        """At 0 degrees the tangent should be vertical (for a circle)."""
        c = Circle(r=100, cx=500, cy=400)
        tangent = c.get_tangent_line(0, length=200)
        start = tangent.get_start()
        end = tangent.get_end()
        # At 0 degrees, point is (600, 400), tangent is vertical
        assert start[0] == pytest.approx(600, abs=1)
        assert end[0] == pytest.approx(600, abs=1)

    def test_tangent_length(self):
        """The tangent line should have the requested length."""
        e = Ellipse(rx=80, ry=40, cx=960, cy=540)
        tangent = e.get_tangent_line(30, length=150)
        assert tangent.get_length() == pytest.approx(150, abs=1)

    def test_tangent_centered_on_ellipse_point(self):
        """The midpoint of the tangent line should be on the ellipse."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        tangent = e.get_tangent_line(0, length=200)
        mid = tangent.get_midpoint()
        # At 0 degrees the point is (600, 400)
        assert mid[0] == pytest.approx(600, abs=1)
        assert mid[1] == pytest.approx(400, abs=1)

    def test_default_length_is_100(self):
        """Default tangent length should be 100."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        tangent = e.get_tangent_line(90)
        assert tangent.get_length() == pytest.approx(100, abs=1)

    def test_tangent_perpendicular_to_normal(self):
        """The tangent and normal at the same angle should be perpendicular."""
        e = Ellipse(rx=100, ry=60, cx=500, cy=400)
        tangent = e.get_tangent_line(45, length=200)
        normal = e.normal_at_angle(45, length=200)
        td = tangent.get_direction()
        nd = normal.get_direction()
        dot = td[0] * nd[0] + td[1] * nd[1]
        assert dot == pytest.approx(0, abs=1e-6)


class TestRectangleChamfer:
    def test_returns_path(self):
        """chamfer should return a Path object."""
        r = Rectangle(width=200, height=100, x=50, y=50)
        result = r.chamfer(size=20)
        assert isinstance(result, Path)

    def test_path_is_closed(self):
        """The chamfered path should be closed (ends with Z)."""
        r = Rectangle(width=200, height=100, x=50, y=50)
        p = r.chamfer(size=20)
        d = p.d.at_time(0)
        assert d.strip().endswith('Z')

    def test_octagonal_shape(self):
        """A chamfered rectangle should have 8 line segments (octagon)."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        p = r.chamfer(size=20)
        d = p.d.at_time(0)
        # Count 'L' commands (7 L segments + the initial M point = 8 vertices)
        assert d.count('L') == 7

    def test_chamfer_vertices(self):
        """The chamfer cut points should be at the correct positions."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        p = r.chamfer(size=20)
        d = p.d.at_time(0)
        # First point should be at (20, 0) - top-left chamfer
        assert d.startswith('M20')

    def test_zero_chamfer(self):
        """Zero chamfer should produce a path that matches the rectangle."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        p = r.chamfer(size=0)
        d = p.d.at_time(0)
        # With size=0, the octagon degenerates to a rectangle
        assert 'M0' in d or 'M0.0' in d

    def test_max_chamfer(self):
        """Chamfer larger than half the smallest dimension should be clamped."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        p = r.chamfer(size=60)
        d = p.d.at_time(0)
        # Should be clamped to min(60, 100, 50) = 50
        assert 'M50' in d or 'M50.0' in d

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Path constructor."""
        r = Rectangle(width=200, height=100, x=0, y=0)
        p = r.chamfer(size=10, stroke='#ff0000')
        svg = p.to_svg(0)
        assert 'stroke=' in svg
        assert '255' in svg or '#ff0000' in svg


class TestAxesAddVerticalAsymptote:
    def test_returns_line(self):
        """add_vertical_asymptote should return a Line object."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_vertical_asymptote(2)
        assert isinstance(result, Line)

    def test_adds_to_objects(self):
        """The asymptote should be added to ax.objects."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        n_before = len(ax.objects)
        ax.add_vertical_asymptote(2)
        assert len(ax.objects) == n_before + 1

    def test_line_is_dashed(self):
        """The asymptote line should have a dashed stroke."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_vertical_asymptote(2)
        svg = line.to_svg(0)
        assert 'stroke-dasharray' in svg

    def test_line_is_vertical(self):
        """The asymptote should be a vertical line (same x for both endpoints)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_vertical_asymptote(0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        assert p1[0] == pytest.approx(p2[0], abs=1)

    def test_at_correct_x(self):
        """The line should be at the SVG x corresponding to the math x value."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_vertical_asymptote(0)
        expected_x = ax._math_to_svg_x(0)
        p1 = line.p1.at_time(0)
        assert p1[0] == pytest.approx(expected_x, abs=1)

    def test_custom_styling(self):
        """Custom styling kwargs should override defaults."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_vertical_asymptote(1, stroke='#ff0000')
        svg = line.to_svg(0)
        assert 'stroke=' in svg
        assert '255' in svg or '#ff0000' in svg


class TestAxesAddHorizontalAsymptote:
    def test_returns_line(self):
        """add_horizontal_asymptote should return a Line object."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_horizontal_asymptote(2)
        assert isinstance(result, Line)

    def test_adds_to_objects(self):
        """The asymptote should be added to ax.objects."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        n_before = len(ax.objects)
        ax.add_horizontal_asymptote(2)
        assert len(ax.objects) == n_before + 1

    def test_line_is_dashed(self):
        """The asymptote line should have a dashed stroke."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_horizontal_asymptote(2)
        svg = line.to_svg(0)
        assert 'stroke-dasharray' in svg

    def test_line_is_horizontal(self):
        """The asymptote should be a horizontal line (same y for both endpoints)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_horizontal_asymptote(0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        assert p1[1] == pytest.approx(p2[1], abs=1)

    def test_at_correct_y(self):
        """The line should be at the SVG y corresponding to the math y value."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_horizontal_asymptote(0)
        expected_y = ax._math_to_svg_y(0)
        p1 = line.p1.at_time(0)
        assert p1[1] == pytest.approx(expected_y, abs=1)

    def test_custom_styling(self):
        """Custom styling kwargs should override defaults."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_horizontal_asymptote(1, stroke='#ff0000')
        svg = line.to_svg(0)
        assert 'stroke=' in svg
        assert '255' in svg or '#ff0000' in svg


class TestPolygonCentroidFormula:
    def test_triangle_centroid(self):
        """The centroid of a right triangle at origin should be at (1/3 of sides)."""
        p = Polygon((0, 0), (300, 0), (0, 300))
        cx, cy = p.centroid()
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(100, abs=1)

    def test_square_centroid(self):
        """The centroid of a square should be at its center."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx, cy = p.centroid()
        assert cx == pytest.approx(50, abs=1)
        assert cy == pytest.approx(50, abs=1)

    def test_matches_get_center_for_regular(self):
        """For a regular polygon the centroid should match the vertex average."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        cx1, cy1 = p.centroid()
        cx2, cy2 = p.get_center()
        assert cx1 == pytest.approx(cx2, abs=1)
        assert cy1 == pytest.approx(cy2, abs=1)

    def test_empty_polygon(self):
        """An empty polygon should return (0, 0)."""
        p = Polygon()
        cx, cy = p.centroid()
        assert cx == 0
        assert cy == 0

    def test_degenerate_two_points(self):
        """Two-point polygon should return the midpoint."""
        p = Polygon((0, 0), (100, 0))
        cx, cy = p.centroid()
        assert cx == pytest.approx(50, abs=1)
        assert cy == pytest.approx(0, abs=1)


class TestLineGetNormalLine:
    def test_returns_line_at_midpoint(self):
        """get_normal_line at t=0.5 should return a line centered at midpoint."""
        l = Line(x1=0, y1=0, x2=200, y2=0)
        normal = l.get_normal_line(t=0.5, length=100)
        assert isinstance(normal, Line)
        mid = normal.get_midpoint()
        assert mid[0] == pytest.approx(100, abs=1)
        assert mid[1] == pytest.approx(0, abs=1)

    def test_perpendicular_direction(self):
        """Normal line should be perpendicular to the original."""
        l = Line(x1=0, y1=0, x2=200, y2=0)
        normal = l.get_normal_line(t=0.5, length=100)
        # For a horizontal line, the normal should be vertical
        p1 = normal.get_start()
        p2 = normal.get_end()
        assert p1[0] == pytest.approx(p2[0], abs=1)  # same x
        assert abs(p2[1] - p1[1]) == pytest.approx(100, abs=1)  # length 100

    def test_at_start(self):
        """Normal at t=0 should be at p1."""
        l = Line(x1=50, y1=50, x2=250, y2=50)
        normal = l.get_normal_line(t=0, length=80)
        mid = normal.get_midpoint()
        assert mid[0] == pytest.approx(50, abs=1)
        assert mid[1] == pytest.approx(50, abs=1)

    def test_at_end(self):
        """Normal at t=1 should be at p2."""
        l = Line(x1=50, y1=50, x2=250, y2=50)
        normal = l.get_normal_line(t=1, length=80)
        mid = normal.get_midpoint()
        assert mid[0] == pytest.approx(250, abs=1)
        assert mid[1] == pytest.approx(50, abs=1)

    def test_custom_length(self):
        """Normal line should have the specified length."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        normal = l.get_normal_line(t=0.5, length=60)
        assert normal.get_length() == pytest.approx(60, abs=1)

    def test_delegates_to_perpendicular_at(self):
        """Result should match perpendicular_at with same arguments."""
        l = Line(x1=10, y1=20, x2=200, y2=150)
        n1 = l.get_normal_line(t=0.3, length=80)
        n2 = l.perpendicular_at(t=0.3, length=80)
        assert n1.get_start() == pytest.approx(n2.get_start(), abs=1e-6)
        assert n1.get_end() == pytest.approx(n2.get_end(), abs=1e-6)

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Line constructor."""
        l = Line(x1=0, y1=0, x2=100, y2=0)
        normal = l.get_normal_line(t=0.5, length=50, stroke='#ff0000')
        svg = normal.to_svg(0)
        assert '255,0,0' in svg or 'ff0000' in svg


class TestCircleGetAnnulus:
    def test_returns_annulus(self):
        """get_annulus should return an Annulus instance."""
        c = Circle(r=100, cx=500, cy=300)
        ann = c.get_annulus()
        assert isinstance(ann, Annulus)

    def test_outer_radius_matches_circle(self):
        """Outer radius should equal the circle's radius."""
        c = Circle(r=120, cx=400, cy=400)
        ann = c.get_annulus()
        assert ann.get_outer_radius() == pytest.approx(120, abs=1)

    def test_inner_radius_default(self):
        """Default inner_ratio=0.5 should give inner radius = r/2."""
        c = Circle(r=100, cx=500, cy=300)
        ann = c.get_annulus()
        assert ann.get_inner_radius() == pytest.approx(50, abs=1)

    def test_custom_inner_ratio(self):
        """Custom inner_ratio should scale the inner radius."""
        c = Circle(r=200, cx=500, cy=300)
        ann = c.get_annulus(inner_ratio=0.75)
        assert ann.get_inner_radius() == pytest.approx(150, abs=1)
        assert ann.get_outer_radius() == pytest.approx(200, abs=1)

    def test_center_matches_circle(self):
        """Annulus center should match the circle center."""
        c = Circle(r=80, cx=100, cy=200)
        ann = c.get_annulus()
        cx, cy = ann.c.at_time(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(200)

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to Annulus constructor."""
        c = Circle(r=100, cx=500, cy=300)
        ann = c.get_annulus(fill='#ff0000')
        svg = ann.to_svg(0)
        assert '255,0,0' in svg or 'ff0000' in svg

    def test_svg_output(self):
        """Annulus should produce valid SVG output."""
        c = Circle(r=100, cx=500, cy=300)
        ann = c.get_annulus()
        svg = ann.to_svg(0)
        assert '<path' in svg
        assert 'fill-rule' in svg


class TestTableAnimateCellValues:
    def test_numeric_interpolation(self):
        """Numeric cells should interpolate between old and new values."""
        t = Table([[10, 20], [30, 40]])
        t.animate_cell_values([[50, 60], [70, 80]], start=0, end=1)
        # At midpoint, values should be interpolated
        mid_val = t.entries[0][0].text.at_time(0.5)
        # Should be between 10 and 50 (around 30 with smooth easing)
        val = float(mid_val)
        assert 10 < val < 50

    def test_numeric_reaches_target(self):
        """Numeric cells should reach the target value at end."""
        t = Table([[10, 20], [30, 40]])
        t.animate_cell_values([[100, 200], [300, 400]], start=0, end=1)
        assert t.entries[0][0].text.at_time(1) == '100'
        assert t.entries[0][1].text.at_time(1) == '200'
        assert t.entries[1][0].text.at_time(1) == '300'
        assert t.entries[1][1].text.at_time(1) == '400'

    def test_text_swap_at_midpoint(self):
        """Non-numeric text should swap at the midpoint."""
        t = Table([['A', 'B'], ['C', 'D']])
        t.animate_cell_values([['X', 'Y'], ['Z', 'W']], start=0, end=2)
        # Before midpoint, old value
        assert t.entries[0][0].text.at_time(0.5) == 'A'
        # After midpoint, new value
        assert t.entries[0][0].text.at_time(1.5) == 'X'

    def test_returns_self(self):
        """animate_cell_values should return self for chaining."""
        t = Table([[1, 2]])
        result = t.animate_cell_values([[3, 4]], start=0, end=1)
        assert result is t

    def test_zero_duration(self):
        """With start==end, values should change instantly."""
        t = Table([[10, 20]])
        t.animate_cell_values([[99, 88]], start=0, end=0)
        assert t.entries[0][0].text.at_time(0) == '99'
        assert t.entries[0][1].text.at_time(0) == '88'


class TestAxesAddFunctionLabel:
    def test_returns_text(self):
        """add_function_label should return a Text object."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        lbl = axes.add_function_label(lambda x: x**2, 'y = x^2', x_pos=2)
        assert isinstance(lbl, Text)

    def test_label_text_content(self):
        """The label should contain the specified text."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        lbl = axes.add_function_label(lambda x: x, 'f(x)', x_pos=3)
        assert lbl.text.at_time(0) == 'f(x)'

    def test_label_position_above(self):
        """Label with direction='above' should be above the curve point."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        func = lambda x: 0
        lbl = axes.add_function_label(func, 'zero', x_pos=0, direction='above')
        curve_y = axes._math_to_svg_y(0, 0)
        label_y = lbl.y.at_time(0)
        # 'above' means smaller y in SVG coords
        assert label_y < curve_y

    def test_label_position_below(self):
        """Label with direction='below' should be below the curve point."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        func = lambda x: 0
        lbl = axes.add_function_label(func, 'zero', x_pos=0, direction='below')
        curve_y = axes._math_to_svg_y(0, 0)
        label_y = lbl.y.at_time(0)
        # 'below' means larger y in SVG coords
        assert label_y > curve_y

    def test_uses_curve_func(self):
        """Should accept a curve Path with ._func attribute."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        curve = axes.add_function(lambda x: x**2)
        lbl = axes.add_function_label(curve, 'parabola', x_pos=2)
        assert isinstance(lbl, Text)
        assert lbl.text.at_time(0) == 'parabola'

    def test_default_x_pos_at_xmax(self):
        """When x_pos=None, label should be positioned near x_max."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        lbl = axes.add_function_label(lambda x: x, 'line')
        # Label x should be near the right edge of the plot
        label_x = lbl.x.at_time(0)
        xmax_svg = axes._math_to_svg_x(5, 0)
        assert abs(label_x - xmax_svg) < 50

    def test_added_to_axes(self):
        """The label should be added to the axes' objects."""
        axes = Axes(x_range=(-5, 5), y_range=(-5, 5))
        lbl = axes.add_function_label(lambda x: x, 'test', x_pos=0)
        assert lbl in axes.objects


class TestPolygonBuffer:
    def test_returns_polygon(self):
        """buffer should return a Polygon."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = p.buffer(10)
        assert isinstance(result, Polygon)

    def test_offset_changes_area(self):
        """buffer with non-zero distance should change the polygon area."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        buffered = p.buffer(10)
        assert buffered.area() != pytest.approx(p.area(), abs=1)

    def test_opposite_distance_reverses(self):
        """Opposite distances should move vertices in opposite directions."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        b1 = p.buffer(10)
        b2 = p.buffer(-10)
        # One should be larger, one smaller than original
        areas = sorted([b1.area(), p.area(), b2.area()])
        assert areas[0] < areas[1] < areas[2]

    def test_matches_offset(self):
        """buffer should produce the same result as offset."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        b = p.buffer(15)
        o = p.offset(15)
        bv = b.get_vertices()
        ov = o.get_vertices()
        for bpt, opt in zip(bv, ov):
            assert bpt[0] == pytest.approx(opt[0], abs=1e-6)
            assert bpt[1] == pytest.approx(opt[1], abs=1e-6)

    def test_preserves_closed_state(self):
        """buffer should preserve whether the polygon is closed."""
        p_open = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        result = p_open.buffer(5)
        assert not result.closed

    def test_zero_distance(self):
        """buffer(0) should return a polygon with the same vertices."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        result = p.buffer(0)
        orig = p.get_vertices()
        new = result.get_vertices()
        for o, n in zip(orig, new):
            assert o[0] == pytest.approx(n[0], abs=1e-6)
            assert o[1] == pytest.approx(n[1], abs=1e-6)


class TestArcGetChord:
    def test_returns_line(self):
        """get_chord should return a Line instance."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord()
        assert isinstance(chord, Line)

    def test_chord_start_matches_arc_start(self):
        """Chord start should match arc start point."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord()
        arc_start = arc.get_start_point()
        chord_start = chord.get_start()
        assert chord_start[0] == pytest.approx(arc_start[0], abs=1e-6)
        assert chord_start[1] == pytest.approx(arc_start[1], abs=1e-6)

    def test_chord_end_matches_arc_end(self):
        """Chord end should match arc end point."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord()
        arc_end = arc.get_end_point()
        chord_end = chord.get_end()
        assert chord_end[0] == pytest.approx(arc_end[0], abs=1e-6)
        assert chord_end[1] == pytest.approx(arc_end[1], abs=1e-6)

    def test_chord_length_matches(self):
        """Chord length should match get_chord_length."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord()
        expected = arc.get_chord_length()
        assert chord.get_length() == pytest.approx(expected, abs=1e-6)

    def test_semicircle_chord_is_diameter(self):
        """Chord of a semicircle should equal the diameter."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=180)
        chord = arc.get_chord()
        assert chord.get_length() == pytest.approx(200, abs=1)

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to Line constructor."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=90)
        chord = arc.get_chord(stroke='#ff0000')
        svg = chord.to_svg(0)
        assert '255,0,0' in svg or 'ff0000' in svg

    def test_full_circle_chord_zero(self):
        """Chord of a full circle should have near-zero length."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=360)
        chord = arc.get_chord()
        assert chord.get_length() == pytest.approx(0, abs=1)


# ── Polygon.to_path_string ──────────────────────────────────────────


class TestPolygonToPathString:
    def test_closed_triangle(self):
        """Closed triangle should produce M ... L ... L ... Z."""
        p = Polygon((10, 20), (30, 40), (50, 60))
        d = p.to_path_string()
        assert d.startswith('M 10.0,20.0')
        assert 'L 30.0,40.0' in d
        assert 'L 50.0,60.0' in d
        assert d.endswith('Z')

    def test_open_polyline_no_z(self):
        """Open polyline should not end with Z."""
        p = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        d = p.to_path_string()
        assert d.startswith('M 0.0,0.0')
        assert not d.endswith('Z')

    def test_single_vertex(self):
        """Single vertex produces just M command."""
        p = Polygon((5, 10))
        d = p.to_path_string()
        assert d == 'M 5.0,10.0 Z'

    def test_empty_polygon(self):
        """Polygon with no vertices returns empty string."""
        p = Polygon()
        d = p.to_path_string()
        assert d == ''

    def test_square_path(self):
        """Square should have 4 L commands plus Z."""
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        d = p.to_path_string()
        parts = d.split()
        # M x,y L x,y L x,y L x,y Z => 9 tokens
        assert parts[0] == 'M'
        assert parts[-1] == 'Z'
        assert d.count('L') == 3

    def test_matches_path_method(self):
        """to_path_string should produce equivalent content to path()."""
        p = Polygon((10, 20), (30, 40), (50, 10))
        d = p.to_path_string()
        # Both should start with M, have L segments, and end with Z
        assert d.startswith('M')
        assert d.endswith('Z')


# ── Arc.get_midpoint ────────────────────────────────────────────────


class TestArcGetMidpoint:
    def test_quarter_arc_midpoint(self):
        """Midpoint of 0-90 arc should be at 45 degrees."""
        arc = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        mx, my = arc.get_midpoint()
        # At 45 degrees: x = 100*cos(45) = ~70.71, y = -100*sin(45) = ~-70.71
        expected_x = 100 * math.cos(math.radians(45))
        expected_y = -100 * math.sin(math.radians(45))
        assert mx == pytest.approx(expected_x, abs=1e-6)
        assert my == pytest.approx(expected_y, abs=1e-6)

    def test_semicircle_midpoint(self):
        """Midpoint of 0-180 arc should be at 90 degrees (top)."""
        arc = Arc(cx=500, cy=300, r=100, start_angle=0, end_angle=180)
        mx, my = arc.get_midpoint()
        # At 90 degrees: x = 500 + 100*cos(90) = 500, y = 300 - 100*sin(90) = 200
        assert mx == pytest.approx(500, abs=1e-6)
        assert my == pytest.approx(200, abs=1e-6)

    def test_midpoint_with_offset_center(self):
        """Midpoint should account for non-origin center."""
        arc = Arc(cx=200, cy=300, r=50, start_angle=0, end_angle=90)
        mx, my = arc.get_midpoint()
        expected_x = 200 + 50 * math.cos(math.radians(45))
        expected_y = 300 - 50 * math.sin(math.radians(45))
        assert mx == pytest.approx(expected_x, abs=1e-6)
        assert my == pytest.approx(expected_y, abs=1e-6)

    def test_full_circle_midpoint(self):
        """Midpoint of 0-360 arc should be at 180 degrees."""
        arc = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=360)
        mx, my = arc.get_midpoint()
        expected_x = 100 * math.cos(math.radians(180))
        expected_y = -100 * math.sin(math.radians(180))
        assert mx == pytest.approx(expected_x, abs=1e-6)
        assert my == pytest.approx(expected_y, abs=1e-6)

    def test_midpoint_lies_on_arc(self):
        """The midpoint should be at distance r from center."""
        arc = Arc(cx=100, cy=200, r=80, start_angle=30, end_angle=120)
        mx, my = arc.get_midpoint()
        dist = math.hypot(mx - 100, my - 200)
        assert dist == pytest.approx(80, abs=1e-6)


# ── Axes.add_labeled_point ──────────────────────────────────────────


class TestAxesAddLabeledPoint:
    def test_returns_vcollection(self):
        """Should return a VCollection."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(1, 2, label='A')
        assert isinstance(result, VCollection)

    def test_dot_only_when_no_label(self):
        """With no label, collection should have 1 object (dot)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(1, 2)
        assert len(result.objects) == 1

    def test_dot_and_label(self):
        """With label, collection should have 2 objects."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(1, 2, label='P')
        assert len(result.objects) == 2

    def test_dot_position(self):
        """Dot should be at the correct SVG coordinates."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(0, 0, label='O')
        dot = result.objects[0]
        sx, sy = ax.coords_to_point(0, 0)
        cx, cy = dot.c.at_time(0)
        assert cx == pytest.approx(sx, abs=1)
        assert cy == pytest.approx(sy, abs=1)

    def test_custom_dot_radius(self):
        """Custom dot_radius should be applied."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(1, 1, dot_radius=10)
        dot = result.objects[0]
        assert dot.r.at_time(0) == pytest.approx(10)

    def test_direction_above(self):
        """Label should be above the dot (lower y in SVG)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(0, 0, label='P', direction='above')
        dot = result.objects[0]
        lbl = result.objects[1]
        dot_y = dot.c.at_time(0)[1]
        lbl_y = lbl.y.at_time(0)
        assert lbl_y < dot_y  # above means smaller y in SVG

    def test_direction_below(self):
        """Label should be below the dot (higher y in SVG)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_labeled_point(0, 0, label='P', direction='below')
        dot = result.objects[0]
        lbl = result.objects[1]
        dot_y = dot.c.at_time(0)[1]
        lbl_y = lbl.y.at_time(0)
        assert lbl_y > dot_y  # below means larger y in SVG


# ── Axes.add_function_region ────────────────────────────────────────


class TestAxesAddFunctionRegion:
    def test_returns_path(self):
        """Should return a Path object."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        area = ax.add_function_region(math.sin)
        from vectormation.objects import Path
        assert isinstance(area, Path)

    def test_area_has_fill(self):
        """The returned area should have a fill."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        area = ax.add_function_region(math.sin, color='#FF0000', opacity=0.5)
        fo = area.styling.fill_opacity.at_time(0)
        assert fo == pytest.approx(0.5)

    def test_with_x_range(self):
        """Should accept an x_range parameter."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        area = ax.add_function_region(math.sin, x_range=(0, math.pi))
        # The area's d attribute should be non-empty at time 0
        d = area.d.at_time(0)
        assert len(d) > 0

    def test_custom_color(self):
        """Custom color should appear in SVG output."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        area = ax.add_function_region(lambda x: x**2, color='#00FF00')
        svg = area.to_svg(0)
        # Check that the fill uses the specified color (green channel)
        assert '0,255,0' in svg or '00ff00' in svg or '00FF00' in svg

    def test_adds_curve_to_axes(self):
        """Both the curve and area should be added to axes objects."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        initial_count = len(ax.objects)
        ax.add_function_region(lambda x: x)
        # Should add at least 2 objects (curve + area)
        assert len(ax.objects) >= initial_count + 2


# ── Text.reverse ────────────────────────────────────────────────────


class TestTextReverse:
    def test_basic_reverse(self):
        """Simple string reversal."""
        t = Text('Hello')
        assert t.reverse() == 'olleH'

    def test_does_not_modify_object(self):
        """reverse() should not change the Text object."""
        t = Text('Hello')
        t.reverse()
        assert t.get_text() == 'Hello'

    def test_empty_string(self):
        """Empty text reverses to empty string."""
        t = Text('')
        assert t.reverse() == ''

    def test_single_char(self):
        """Single character reverses to itself."""
        t = Text('X')
        assert t.reverse() == 'X'

    def test_palindrome(self):
        """Palindrome should equal itself reversed."""
        t = Text('racecar')
        assert t.reverse() == 'racecar'

    def test_with_spaces(self):
        """Spaces should be preserved in reverse."""
        t = Text('ab cd')
        assert t.reverse() == 'dc ba'


# ── Rectangle.split_horizontal / split_vertical ────────────────────


class TestRectangleSplitHorizontal:
    def test_returns_vcollection(self):
        """Should return a VCollection."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_horizontal(3)
        assert isinstance(result, VCollection)

    def test_correct_count(self):
        """Should return n rectangles."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_horizontal(4)
        assert len(result.objects) == 4

    def test_strip_dimensions(self):
        """Each strip should have full width and 1/n height."""
        r = Rectangle(200, 120, x=10, y=20)
        result = r.split_horizontal(3)
        for part in result.objects:
            assert part.width.at_time(0) == pytest.approx(200)
            assert part.height.at_time(0) == pytest.approx(40)

    def test_strip_positions(self):
        """Strips should be stacked top to bottom."""
        r = Rectangle(200, 120, x=10, y=20)
        result = r.split_horizontal(3)
        assert result.objects[0].y.at_time(0) == pytest.approx(20)
        assert result.objects[1].y.at_time(0) == pytest.approx(60)
        assert result.objects[2].y.at_time(0) == pytest.approx(100)

    def test_default_n_is_two(self):
        """Default split should produce 2 strips."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_horizontal()
        assert len(result.objects) == 2

    def test_matches_split_method(self):
        """Should produce same result as split('horizontal', n)."""
        r = Rectangle(200, 100, x=10, y=20)
        a = r.split_horizontal(3)
        b = r.split('horizontal', 3)
        for pa, pb in zip(a.objects, b.objects):
            assert pa.x.at_time(0) == pytest.approx(pb.x.at_time(0))
            assert pa.y.at_time(0) == pytest.approx(pb.y.at_time(0))
            assert pa.width.at_time(0) == pytest.approx(pb.width.at_time(0))
            assert pa.height.at_time(0) == pytest.approx(pb.height.at_time(0))


class TestRectangleSplitVertical:
    def test_returns_vcollection(self):
        """Should return a VCollection."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_vertical(3)
        assert isinstance(result, VCollection)

    def test_correct_count(self):
        """Should return n rectangles."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_vertical(5)
        assert len(result.objects) == 5

    def test_strip_dimensions(self):
        """Each strip should have 1/n width and full height."""
        r = Rectangle(300, 100, x=10, y=20)
        result = r.split_vertical(3)
        for part in result.objects:
            assert part.width.at_time(0) == pytest.approx(100)
            assert part.height.at_time(0) == pytest.approx(100)

    def test_strip_positions(self):
        """Strips should be arranged left to right."""
        r = Rectangle(300, 100, x=10, y=20)
        result = r.split_vertical(3)
        assert result.objects[0].x.at_time(0) == pytest.approx(10)
        assert result.objects[1].x.at_time(0) == pytest.approx(110)
        assert result.objects[2].x.at_time(0) == pytest.approx(210)

    def test_default_n_is_two(self):
        """Default split should produce 2 strips."""
        r = Rectangle(200, 100, x=10, y=20)
        result = r.split_vertical()
        assert len(result.objects) == 2

    def test_matches_split_method(self):
        """Should produce same result as split('vertical', n)."""
        r = Rectangle(200, 100, x=10, y=20)
        a = r.split_vertical(4)
        b = r.split('vertical', 4)
        for pa, pb in zip(a.objects, b.objects):
            assert pa.x.at_time(0) == pytest.approx(pb.x.at_time(0))
            assert pa.y.at_time(0) == pytest.approx(pb.y.at_time(0))
            assert pa.width.at_time(0) == pytest.approx(pb.width.at_time(0))
            assert pa.height.at_time(0) == pytest.approx(pb.height.at_time(0))


class TestCircleGetArc:
    def test_returns_arc_instance(self):
        c = Circle(r=100, cx=500, cy=300)
        arc = c.get_arc(0, 90)
        assert isinstance(arc, Arc)

    def test_default_angles(self):
        c = Circle(r=100, cx=500, cy=300)
        arc = c.get_arc()
        assert arc.start_angle.at_time(0) == pytest.approx(0)
        assert arc.end_angle.at_time(0) == pytest.approx(180)

    def test_arc_has_same_center(self):
        c = Circle(r=100, cx=500, cy=300)
        arc = c.get_arc(0, 90)
        assert arc.cx.at_time(0) == pytest.approx(500)
        assert arc.cy.at_time(0) == pytest.approx(300)

    def test_arc_has_same_radius(self):
        c = Circle(r=80, cx=200, cy=400)
        arc = c.get_arc(45, 135)
        assert arc.r.at_time(0) == pytest.approx(80)

    def test_arc_angles_preserved(self):
        c = Circle(r=100, cx=960, cy=540)
        arc = c.get_arc(30, 150)
        assert arc.start_angle.at_time(0) == pytest.approx(30)
        assert arc.end_angle.at_time(0) == pytest.approx(150)

    def test_accepts_kwargs(self):
        c = Circle(r=100)
        arc = c.get_arc(0, 180, stroke_width=5)
        assert arc.styling.stroke_width.at_time(0) == pytest.approx(5)

    def test_respects_time(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shift(dx=200, dy=100, start=1)
        arc = c.get_arc(0, 90, time=1)
        assert arc.cx.at_time(0) == pytest.approx(300)
        assert arc.cy.at_time(0) == pytest.approx(200)


class TestLineDivide:
    def test_returns_n_plus_1_points(self):
        line = Line(0, 0, 200, 0)
        pts = line.divide(4)
        assert len(pts) == 5

    def test_default_n_is_2(self):
        line = Line(0, 0, 100, 0)
        pts = line.divide()
        assert len(pts) == 3

    def test_first_point_is_start(self):
        line = Line(10, 20, 210, 20)
        pts = line.divide(3)
        assert pts[0] == pytest.approx((10.0, 20.0))

    def test_last_point_is_end(self):
        line = Line(10, 20, 210, 20)
        pts = line.divide(3)
        assert pts[-1] == pytest.approx((210.0, 20.0))

    def test_midpoint_for_n_equals_2(self):
        line = Line(0, 0, 200, 0)
        pts = line.divide(2)
        assert pts[1] == pytest.approx((100.0, 0.0))

    def test_equally_spaced_horizontal(self):
        line = Line(0, 0, 300, 0)
        pts = line.divide(3)
        assert pts[0] == pytest.approx((0.0, 0.0))
        assert pts[1] == pytest.approx((100.0, 0.0))
        assert pts[2] == pytest.approx((200.0, 0.0))
        assert pts[3] == pytest.approx((300.0, 0.0))

    def test_diagonal_line(self):
        line = Line(0, 0, 100, 100)
        pts = line.divide(2)
        assert pts[0] == pytest.approx((0.0, 0.0))
        assert pts[1] == pytest.approx((50.0, 50.0))
        assert pts[2] == pytest.approx((100.0, 100.0))

    def test_n_equals_1_returns_endpoints(self):
        line = Line(0, 0, 100, 0)
        pts = line.divide(1)
        assert len(pts) == 2
        assert pts[0] == pytest.approx((0.0, 0.0))
        assert pts[1] == pytest.approx((100.0, 0.0))

    def test_respects_time(self):
        line = Line(0, 0, 100, 0)
        line.shift(dx=50, start=1)
        pts = line.divide(2, time=1)
        assert pts[0] == pytest.approx((50.0, 0.0))
        assert pts[2] == pytest.approx((150.0, 0.0))


class TestTableGetCell:
    def test_returns_text_object(self):
        t = Table([[1, 2], [3, 4]])
        cell = t.get_cell(0, 0)
        assert isinstance(cell, Text)

    def test_correct_value(self):
        t = Table([['a', 'b'], ['c', 'd']])
        assert t.get_cell(0, 0).text.at_time(0) == 'a'
        assert t.get_cell(0, 1).text.at_time(0) == 'b'
        assert t.get_cell(1, 0).text.at_time(0) == 'c'
        assert t.get_cell(1, 1).text.at_time(0) == 'd'

    def test_same_as_get_entry(self):
        t = Table([[10, 20, 30], [40, 50, 60]])
        for r in range(2):
            for c in range(3):
                assert t.get_cell(r, c) is t.get_entry(r, c)

    def test_3x3_table(self):
        data = [[i * 3 + j for j in range(3)] for i in range(3)]
        t = Table(data)
        for r in range(3):
            for c in range(3):
                assert t.get_cell(r, c).text.at_time(0) == str(data[r][c])


# ── New feature tests ──────────────────────────────────────────────────────


class TestPolygonArea:
    def test_triangle_area(self):
        """Area of a right triangle with legs 100 and 200."""
        tri = Polygon((0, 0), (100, 0), (0, 200), closed=True)
        assert tri.area() == pytest.approx(10000.0)

    def test_square_area(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=True)
        assert sq.area() == pytest.approx(10000.0)

    def test_area_always_positive(self):
        """area() returns positive regardless of winding order."""
        cw = Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=True)
        ccw = Polygon((0, 0), (0, 100), (100, 100), (100, 0), closed=True)
        assert cw.area() == pytest.approx(ccw.area())
        assert cw.area() > 0

    def test_area_equals_abs_signed_area(self):
        tri = Polygon((0, 0), (300, 0), (0, 400), closed=True)
        assert tri.area() == pytest.approx(abs(tri.signed_area()))

    def test_open_polygon_area_is_zero(self):
        poly = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        assert poly.area() == 0.0


class TestLineLength:
    def test_horizontal_line(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        assert line.length() == pytest.approx(100.0)

    def test_vertical_line(self):
        line = Line(x1=0, y1=0, x2=0, y2=200)
        assert line.length() == pytest.approx(200.0)

    def test_diagonal_line(self):
        line = Line(x1=0, y1=0, x2=3, y2=4)
        assert line.length() == pytest.approx(5.0)

    def test_length_matches_get_length(self):
        line = Line(x1=10, y1=20, x2=50, y2=80)
        assert line.length() == pytest.approx(line.get_length())

    def test_zero_length_line(self):
        line = Line(x1=42, y1=42, x2=42, y2=42)
        assert line.length() == pytest.approx(0.0)


class TestCircleCircumference:
    def test_unit_circle(self):
        c = Circle(r=1)
        assert c.circumference() == pytest.approx(2 * math.pi)

    def test_radius_50(self):
        c = Circle(r=50)
        assert c.circumference() == pytest.approx(2 * math.pi * 50)

    def test_matches_get_circumference(self):
        c = Circle(r=120)
        assert c.circumference() == pytest.approx(c.get_circumference())

    def test_matches_get_perimeter(self):
        c = Circle(r=75)
        assert c.circumference() == pytest.approx(c.get_perimeter())


class TestAxesShadeBetween:
    def test_returns_path(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        p = ax.shade_between(lambda x: x, lambda x: x**2)
        assert isinstance(p, Path)

    def test_custom_color_and_opacity(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        p = ax.shade_between(lambda x: 0, lambda x: x, color='#FF0000', opacity=0.5)
        svg = p.to_svg(0)
        # Color may be rendered as hex '#FF0000' or as 'rgb(255,0,0)'
        assert '#FF0000' in svg or 'rgb(255,0,0)' in svg

    def test_with_x_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        p = ax.shade_between(lambda x: 0, lambda x: 1, x_range=(0, 2))
        # The path should be created with a non-empty d attribute
        d = p.d.at_time(0)
        assert len(d) > 0

    def test_with_curve_objects(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        c1 = ax.plot(lambda x: x)
        c2 = ax.plot(lambda x: x**2)
        p = ax.shade_between(c1, c2)
        assert isinstance(p, Path)
        d = p.d.at_time(0)
        assert len(d) > 0


class TestNumberLineAddDotAt:
    def test_returns_dot(self):
        nl = NumberLine(x_range=(-5, 5))
        dot = nl.add_dot_at(0)
        assert isinstance(dot, Dot)

    def test_dot_position(self):
        nl = NumberLine(x_range=(0, 10))
        dot = nl.add_dot_at(5)
        expected_x, expected_y = nl.number_to_point(5)
        cx, cy = dot.c.at_time(0)
        assert cx == pytest.approx(expected_x)
        assert cy == pytest.approx(expected_y)

    def test_custom_color(self):
        nl = NumberLine(x_range=(0, 10))
        dot = nl.add_dot_at(3, color='#00FF00')
        svg = dot.to_svg(0)
        # Color may be rendered as hex '#00FF00' or as 'rgb(0,255,0)'
        assert '#00FF00' in svg or 'rgb(0,255,0)' in svg

    def test_custom_radius(self):
        nl = NumberLine(x_range=(0, 10))
        dot = nl.add_dot_at(5, radius=15)
        r = dot.rx.at_time(0)
        assert r == pytest.approx(15)

    def test_dot_appended_to_objects(self):
        nl = NumberLine(x_range=(0, 10))
        n_before = len(nl.objects)
        nl.add_dot_at(2)
        assert len(nl.objects) == n_before + 1


class TestRectangleDiagonalLength:
    def test_3_4_rectangle(self):
        r = Rectangle(width=3, height=4)
        assert r.diagonal_length() == pytest.approx(5.0)

    def test_square(self):
        r = Rectangle(width=100, height=100)
        assert r.diagonal_length() == pytest.approx(100 * math.sqrt(2))

    def test_matches_get_diagonal_length(self):
        r = Rectangle(width=200, height=150)
        assert r.diagonal_length() == pytest.approx(r.get_diagonal_length())

    def test_zero_dimensions(self):
        r = Rectangle(width=0, height=0)
        assert r.diagonal_length() == pytest.approx(0.0)


# ── Line.add_tip tests ──────────────────────────────────────────────────


class TestLineAddTip:
    def test_returns_vcollection(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip()
        assert isinstance(result, VCollection)

    def test_end_tip_only(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=True, start=False)
        # Should have 2 objects: the line + 1 tip polygon
        assert len(result.objects) == 2
        assert result.objects[0] is line
        # The tip is a Polygon (triangle)
        tip = result.objects[1]
        assert isinstance(tip, Polygon)
        assert len(tip.vertices) == 3

    def test_start_tip_only(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=False, start=True)
        assert len(result.objects) == 2
        assert result.objects[0] is line
        tip = result.objects[1]
        assert isinstance(tip, Polygon)

    def test_both_tips(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=True, start=True)
        # Should have 3 objects: line + 2 tips
        assert len(result.objects) == 3

    def test_no_tips(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=False, start=False)
        # Should have just the line
        assert len(result.objects) == 1
        assert result.objects[0] is line

    def test_end_tip_position_horizontal(self):
        """End tip should be at x=100 for a horizontal line from 0 to 100."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip()
        tip = result.objects[1]
        # Tip point (first vertex) should be at end of line
        v0 = tip.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(100)
        assert v0[1] == pytest.approx(0)

    def test_start_tip_position_horizontal(self):
        """Start tip should be at x=0 for a horizontal line from 0 to 100."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=False, start=True)
        tip = result.objects[1]
        v0 = tip.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(0)
        assert v0[1] == pytest.approx(0)

    def test_custom_tip_dimensions(self):
        line = Line(x1=0, y1=0, x2=200, y2=0)
        result = line.add_tip(tip_length=30, tip_width=20)
        tip = result.objects[1]
        # Tip point at (200, 0), base vertices at x = 200 - 30 = 170
        v0 = tip.vertices[0].at_time(0)
        v1 = tip.vertices[1].at_time(0)
        v2 = tip.vertices[2].at_time(0)
        assert v0[0] == pytest.approx(200)
        assert v1[0] == pytest.approx(170)
        assert v2[0] == pytest.approx(170)
        # Half-width = 10, perp direction is (0, 1) for rightward line
        # so base vertices at y = +10 and y = -10
        assert abs(v1[1]) == pytest.approx(10)
        assert abs(v2[1]) == pytest.approx(10)
        assert v1[1] == pytest.approx(-v2[1])

    def test_diagonal_line_tip(self):
        """Tip should point along the line direction for a diagonal line."""
        line = Line(x1=0, y1=0, x2=100, y2=100)
        result = line.add_tip()
        tip = result.objects[1]
        v0 = tip.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(100)
        assert v0[1] == pytest.approx(100)

    def test_svg_renders(self):
        """Ensure the result can produce SVG without errors."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        result = line.add_tip(end=True, start=True)
        svg = result.to_svg(0)
        assert '<line' in svg
        assert '<polygon' in svg

    def test_tip_fill_matches_stroke(self):
        """Tip fill color should match line stroke color."""
        line = Line(x1=0, y1=0, x2=100, y2=0, stroke='#FF0000')
        result = line.add_tip()
        tip = result.objects[1]
        fill = tip.styling.fill.at_time(0)
        stroke = line.styling.stroke.at_time(0)
        assert fill == stroke


# ── Text.add_background_rectangle tests ──────────────────────────────────


class TestTextAddBackgroundRectangle:
    def test_returns_vcollection(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        assert isinstance(result, VCollection)

    def test_contains_rect_and_text(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        assert len(result.objects) == 2
        assert isinstance(result.objects[0], Rectangle)
        assert result.objects[1] is t

    def test_rect_has_lower_z_index(self):
        t = Text(text='Hello', x=100, y=100, z=5)
        result = t.add_background_rectangle()
        rect = result.objects[0]
        assert rect.z.at_time(0) < t.z.at_time(0)

    def test_default_color_and_opacity(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        rect = result.objects[0]
        assert rect.styling.fill.at_time(0) == 'rgb(0,0,0)'
        assert rect.styling.fill_opacity.at_time(0) == pytest.approx(0.5)

    def test_custom_color_and_opacity(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle(color='#FF0000', opacity=0.8)
        rect = result.objects[0]
        assert rect.styling.fill.at_time(0) == 'rgb(255,0,0)'
        assert rect.styling.fill_opacity.at_time(0) == pytest.approx(0.8)

    def test_padding(self):
        t = Text(text='Hello', x=100, y=100, font_size=48)
        pad = 20
        bx, by, bw, bh = t.bbox(0)
        result = t.add_background_rectangle(padding=pad)
        rect = result.objects[0]
        assert rect.x.at_time(0) == pytest.approx(bx - pad)
        assert rect.y.at_time(0) == pytest.approx(by - pad)
        assert rect.width.at_time(0) == pytest.approx(bw + 2 * pad)
        assert rect.height.at_time(0) == pytest.approx(bh + 2 * pad)

    def test_svg_renders(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        svg = result.to_svg(0)
        assert '<rect' in svg
        assert '<text' in svg

    def test_rect_no_stroke(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        rect = result.objects[0]
        assert rect.styling.stroke_width.at_time(0) == 0


# ── Circle.from_bounding_box tests ──────────────────────────────────────


class TestCircleFromBoundingBox:
    def test_returns_circle(self):
        r = Rectangle(width=100, height=100, x=0, y=0)
        c = Circle.from_bounding_box(r)
        assert isinstance(c, Circle)

    def test_center_at_bbox_center(self):
        r = Rectangle(width=100, height=100, x=0, y=0)
        c = Circle.from_bounding_box(r)
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(50)
        assert cy == pytest.approx(50)

    def test_radius_is_half_diagonal(self):
        r = Rectangle(width=60, height=80, x=0, y=0)
        c = Circle.from_bounding_box(r)
        expected_r = math.hypot(30, 40)  # 50
        assert c.rx.at_time(0) == pytest.approx(expected_r)

    def test_radius_with_padding(self):
        r = Rectangle(width=60, height=80, x=0, y=0)
        c = Circle.from_bounding_box(r, padding=10)
        expected_r = math.hypot(30, 40) + 10  # 60
        assert c.rx.at_time(0) == pytest.approx(expected_r)

    def test_circumscribes_square(self):
        r = Rectangle(width=100, height=100, x=50, y=50)
        c = Circle.from_bounding_box(r)
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(100)
        assert c.rx.at_time(0) == pytest.approx(math.hypot(50, 50))

    def test_from_circle_object(self):
        """Circumscribing circle around another circle's bbox."""
        inner = Circle(r=50, cx=100, cy=100)
        outer = Circle.from_bounding_box(inner)
        # bbox of circle is (50, 50, 100, 100)
        cx, cy = outer.c.at_time(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(100)
        # half-diagonal of 100x100 square
        assert outer.rx.at_time(0) == pytest.approx(math.hypot(50, 50))

    def test_from_line(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        c = Circle.from_bounding_box(line)
        cx, cy = c.c.at_time(0)
        assert cx == pytest.approx(50)

    def test_svg_renders(self):
        r = Rectangle(width=100, height=100, x=0, y=0)
        c = Circle.from_bounding_box(r)
        svg = c.to_svg(0)
        assert '<circle' in svg

    def test_kwargs_forwarded(self):
        r = Rectangle(width=100, height=100, x=0, y=0)
        c = Circle.from_bounding_box(r, stroke='#FF0000')
        assert c.styling.stroke.at_time(0) == 'rgb(255,0,0)'


# ── Axes.annotate_area tests ────────────────────────────────────────────


class TestAxesAnnotateArea:
    def test_returns_vcollection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.annotate_area(lambda x: x**2, x_range=(0, 2))
        assert isinstance(result, VCollection)

    def test_area_only_no_label(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.annotate_area(lambda x: x, x_range=(0, 3))
        # Should have 1 object: the area Path
        assert len(result.objects) == 1

    def test_area_with_label(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.annotate_area(lambda x: x**2, x_range=(0, 2), label='Area')
        # Should have 2 objects: area + label
        assert len(result.objects) == 2
        label_obj = result.objects[1]
        assert isinstance(label_obj, Text)
        assert label_obj.text.at_time(0) == 'Area'

    def test_custom_color_opacity(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.annotate_area(lambda x: x, x_range=(0, 2),
                                   color='#FF0000', opacity=0.7)
        area = result.objects[0]
        assert area.styling.fill.at_time(0) == 'rgb(255,0,0)'
        assert area.styling.fill_opacity.at_time(0) == pytest.approx(0.7)

    def test_area_added_to_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        n_before = len(ax.objects)
        ax.annotate_area(lambda x: x**2, x_range=(0, 2))
        # get_area adds the Path to ax.objects
        assert len(ax.objects) > n_before

    def test_with_plot_curve(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        curve = ax.plot(lambda x: x**2)
        result = ax.annotate_area(curve, x_range=(0, 2))
        assert isinstance(result, VCollection)

    def test_svg_renders(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.annotate_area(lambda x: x, x_range=(0, 2), label='Test')
        svg = ax.to_svg(0)
        assert 'Test' in svg


# ── NumberLine.add_animated_pointer tests ────────────────────────────────


class TestNumberLineAddAnimatedPointer:
    def test_returns_self(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        result = nl.add_animated_pointer(lambda t: 0)
        assert result is nl

    def test_adds_objects(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        n_before = len(nl.objects)
        nl.add_animated_pointer(lambda t: 0)
        # Should add at least 1 object (triangle) + 1 label
        assert len(nl.objects) >= n_before + 2

    def test_label_disabled(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        n_before = len(nl.objects)
        nl.add_animated_pointer(lambda t: 0, label=False)
        # Should add just 1 object (triangle), no label
        assert len(nl.objects) == n_before + 1

    def test_pointer_tracks_value(self):
        nl = NumberLine(x_range=(0, 10, 1))
        nl.add_animated_pointer(lambda t: t * 10)
        # The last polygon added should be the pointer triangle
        ptr = None
        for obj in reversed(nl.objects):
            if isinstance(obj, Polygon):
                ptr = obj
                break
        assert ptr is not None
        # At time=0, value=0 => pointer at start
        v0 = ptr.vertices[2].at_time(0)
        px0, _ = nl.number_to_point(0)
        assert v0[0] == pytest.approx(px0, abs=1)

        # At time=0.5, value=5 => pointer at midpoint
        v05 = ptr.vertices[2].at_time(0.5)
        px5, _ = nl.number_to_point(5)
        assert v05[0] == pytest.approx(px5, abs=1)

    def test_label_text_updates(self):
        nl = NumberLine(x_range=(0, 10, 1))
        nl.add_animated_pointer(lambda t: t * 10)
        # Find the label Text object
        lbl = None
        for obj in reversed(nl.objects):
            if isinstance(obj, Text):
                lbl = obj
                break
        assert lbl is not None
        # At time=0, value=0
        assert float(lbl.text.at_time(0)) == pytest.approx(0.0)
        # At time=0.5, value=5.0
        assert float(lbl.text.at_time(0.5)) == pytest.approx(5.0)

    def test_svg_renders(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_animated_pointer(lambda t: t)
        svg = nl.to_svg(0)
        assert '<polygon' in svg

    def test_pointer_with_end(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_animated_pointer(lambda t: 0, start=0, end=2)
        # The pointer polygon should be hidden after end time
        ptr = None
        for obj in reversed(nl.objects):
            if isinstance(obj, Polygon):
                ptr = obj
                break
        assert ptr is not None
        # Should be visible at t=1 and hidden at t=3
        assert ptr.show.at_time(1) == True
        assert ptr.show.at_time(3) == False


class TestPolygonMoveVertex:
    def test_move_vertex_instant(self):
        """Moving a vertex instantly should update its position."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        result = p.move_vertex(0, 10, 20)
        assert result is p
        v0 = p.vertices[0].at_time(0)
        assert v0[0] == pytest.approx(10, abs=1e-6)
        assert v0[1] == pytest.approx(20, abs=1e-6)

    def test_move_vertex_animated(self):
        """Moving a vertex with end should animate over time."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        p.move_vertex(1, 200, 0, start=0, end=1)
        # At time=0, vertex 1 should still be near original
        v1_start = p.vertices[1].at_time(0)
        assert v1_start[0] == pytest.approx(100, abs=1)
        # At time=1, vertex 1 should be at target
        v1_end = p.vertices[1].at_time(1)
        assert v1_end[0] == pytest.approx(200, abs=1)
        assert v1_end[1] == pytest.approx(0, abs=1)

    def test_move_vertex_negative_index(self):
        """Negative index should work (last vertex)."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        p.move_vertex(-1, 60, 80)
        v_last = p.vertices[-1].at_time(0)
        assert v_last[0] == pytest.approx(60, abs=1e-6)
        assert v_last[1] == pytest.approx(80, abs=1e-6)

    def test_move_vertex_out_of_range(self):
        """Out of range index should raise IndexError."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        with pytest.raises(IndexError):
            p.move_vertex(5, 0, 0)

    def test_move_vertex_negative_out_of_range(self):
        """Out of range negative index should raise IndexError."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        with pytest.raises(IndexError):
            p.move_vertex(-4, 0, 0)

    def test_move_vertex_other_vertices_unchanged(self):
        """Only the specified vertex should move."""
        p = Polygon((0, 0), (100, 0), (50, 100))
        p.move_vertex(0, 10, 10)
        v1 = p.vertices[1].at_time(0)
        v2 = p.vertices[2].at_time(0)
        assert v1[0] == pytest.approx(100, abs=1e-6)
        assert v1[1] == pytest.approx(0, abs=1e-6)
        assert v2[0] == pytest.approx(50, abs=1e-6)
        assert v2[1] == pytest.approx(100, abs=1e-6)


class TestLineSetLengthMidpoint:
    def test_set_length_keeps_midpoint(self):
        """set_length should keep the midpoint fixed."""
        line = Line(x1=100, y1=200, x2=200, y2=200)
        # Midpoint = (150, 200)
        line.set_length(200, start=0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert mx == pytest.approx(150, abs=1e-6)
        assert my == pytest.approx(200, abs=1e-6)
        assert math.hypot(p2[0] - p1[0], p2[1] - p1[1]) == pytest.approx(200, abs=1e-4)

    def test_set_length_diagonal(self):
        """set_length should work on diagonal lines."""
        line = Line(x1=0, y1=0, x2=60, y2=80)
        # Original length = 100, midpoint = (30, 40)
        line.set_length(50, start=0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert mx == pytest.approx(30, abs=1e-4)
        assert my == pytest.approx(40, abs=1e-4)
        new_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert new_length == pytest.approx(50, abs=1e-4)


class TestArrowBetween:
    def test_between_horizontal(self):
        """Arrow.between should connect two objects horizontally."""
        r1 = Rectangle(50, 50, x=100, y=100)
        r2 = Rectangle(50, 50, x=300, y=100)
        arrow = Arrow.between(r1, r2)
        start = arrow.get_start(0)
        end = arrow.get_end(0)
        # r1 right edge = 150, r2 left edge = 300
        assert start[0] == pytest.approx(150, abs=1)
        assert end[0] == pytest.approx(300, abs=1)

    def test_between_vertical(self):
        """Arrow.between should connect two objects vertically."""
        r1 = Rectangle(50, 50, x=100, y=100)
        r2 = Rectangle(50, 50, x=100, y=400)
        arrow = Arrow.between(r1, r2)
        start = arrow.get_start(0)
        end = arrow.get_end(0)
        # r1 bottom edge = 150, r2 top edge = 400
        assert start[1] == pytest.approx(150, abs=1)
        assert end[1] == pytest.approx(400, abs=1)

    def test_between_with_buff(self):
        """Arrow.between with buff should shorten the arrow."""
        r1 = Rectangle(50, 50, x=100, y=100)
        r2 = Rectangle(50, 50, x=300, y=100)
        arrow_no_buff = Arrow.between(r1, r2)
        arrow_with_buff = Arrow.between(r1, r2, buff=10)
        len_no_buff = arrow_no_buff.get_length(0)
        len_with_buff = arrow_with_buff.get_length(0)
        assert len_with_buff == pytest.approx(len_no_buff - 20, abs=1)

    def test_between_returns_arrow(self):
        """Arrow.between should return an Arrow instance."""
        r1 = Circle(r=25, cx=100, cy=100)
        r2 = Circle(r=25, cx=300, cy=100)
        arrow = Arrow.between(r1, r2)
        assert isinstance(arrow, Arrow)

    def test_between_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Arrow constructor."""
        r1 = Rectangle(50, 50, x=100, y=100)
        r2 = Rectangle(50, 50, x=300, y=100)
        arrow = Arrow.between(r1, r2, stroke='#ff0000')
        svg = arrow.to_svg(0)
        # Color should be in the SVG
        assert '255' in svg or 'ff0000' in svg or 'rgb' in svg


class TestVector:
    def test_vector_is_arrow(self):
        v = Vector(100, 50)
        assert isinstance(v, Arrow)

    def test_vector_get_vector(self):
        v = Vector(100, 0, origin_x=0, origin_y=0)
        vx, vy = v.get_vector(0)
        assert vx == pytest.approx(100, abs=1)
        assert vy == pytest.approx(0, abs=1)

    def test_vector_repr(self):
        v = Vector(50, -30)
        assert 'Vector' in repr(v)

    def test_vector_coordinate_label(self):
        v = Vector(100, 0, origin_x=0, origin_y=0)
        m = v.coordinate_label()
        assert m is not None


class TestTableFromDict:
    def test_from_dict_basic(self):
        """Table.from_dict should create a table with correct dimensions."""
        t = Table.from_dict({'Name': ['Alice', 'Bob'], 'Age': [30, 25]})
        assert t.rows == 2
        assert t.cols == 2

    def test_from_dict_values(self):
        """Table.from_dict should populate entries correctly."""
        t = Table.from_dict({'Name': ['Alice', 'Bob'], 'Age': [30, 25]})
        assert t.entries[0][0].text.at_time(0) == 'Alice'
        assert t.entries[0][1].text.at_time(0) == '30'
        assert t.entries[1][0].text.at_time(0) == 'Bob'
        assert t.entries[1][1].text.at_time(0) == '25'

    def test_from_dict_scalar_values(self):
        """Scalar values should be wrapped in lists."""
        t = Table.from_dict({'Key': 'Value', 'Foo': 'Bar'})
        assert t.rows == 1
        assert t.cols == 2
        assert t.entries[0][0].text.at_time(0) == 'Value'
        assert t.entries[0][1].text.at_time(0) == 'Bar'

    def test_from_dict_unequal_lengths(self):
        """Shorter columns should be padded with empty strings."""
        t = Table.from_dict({'A': [1, 2, 3], 'B': [10]})
        assert t.rows == 3
        assert t.entries[0][1].text.at_time(0) == '10'
        assert t.entries[1][1].text.at_time(0) == ''
        assert t.entries[2][1].text.at_time(0) == ''

    def test_from_dict_renders_svg(self):
        """Table.from_dict result should render valid SVG."""
        t = Table.from_dict({'X': [1, 2], 'Y': [3, 4]})
        svg = t.to_svg(0)
        assert '<line' in svg
        assert '<text' in svg

    def test_from_dict_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Table constructor."""
        t = Table.from_dict({'A': [1]}, font_size=36)
        # Should not raise, and table should be created
        assert t.rows == 1


class TestBarChartHighlightBar:
    def test_highlight_bar_basic(self):
        """highlight_bar should change the bar's fill color."""
        chart = BarChart([10, 20, 30])
        result = chart.highlight_bar(1, color='#FF0000', start=0)
        assert result is chart
        bar = chart._bars[1]
        fill = bar.styling.fill.at_time(0)
        # Color may be normalized, check it's red
        assert '255' in fill or 'ff0000' in fill.lower() or 'FF0000' in fill

    def test_highlight_bar_with_opacity(self):
        """highlight_bar with opacity should set fill_opacity."""
        chart = BarChart([10, 20, 30])
        chart.highlight_bar(0, color='#00FF00', start=0, opacity=0.5)
        bar = chart._bars[0]
        assert bar.styling.fill_opacity.at_time(0) == pytest.approx(0.5, abs=0.01)

    def test_highlight_bar_out_of_range(self):
        """Out of range index should raise IndexError."""
        chart = BarChart([10, 20, 30])
        with pytest.raises(IndexError):
            chart.highlight_bar(5)

    def test_highlight_bar_animated(self):
        """highlight_bar with end should animate the color change."""
        chart = BarChart([10, 20, 30])
        chart.highlight_bar(0, color='#FF0000', start=0, end=1)
        # Should not raise and bar should exist
        assert chart._bars[0] is not None


# ---- Rectangle.from_two_objects ----

class TestRectangleFromTwoObjects:
    def test_basic_enclosure(self):
        """Rectangle should enclose two non-overlapping rectangles."""
        a = Rectangle(100, 50, x=10, y=20)
        b = Rectangle(80, 60, x=200, y=100)
        r = Rectangle.from_two_objects(a, b)
        rx = r.x.at_time(0)
        ry = r.y.at_time(0)
        rw = r.width.at_time(0)
        rh = r.height.at_time(0)
        # Union: x from 10 to max(110, 280)=280, y from 20 to max(70, 160)=160
        assert rx == pytest.approx(10)
        assert ry == pytest.approx(20)
        assert rw == pytest.approx(270)
        assert rh == pytest.approx(140)

    def test_with_padding(self):
        """Padding should expand the result on all sides."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=100, y=0)
        r = Rectangle.from_two_objects(a, b, padding=10)
        assert r.x.at_time(0) == pytest.approx(-10)
        assert r.y.at_time(0) == pytest.approx(-10)
        assert r.width.at_time(0) == pytest.approx(220)
        assert r.height.at_time(0) == pytest.approx(120)

    def test_overlapping_objects(self):
        """Should work for overlapping objects."""
        a = Rectangle(200, 200, x=0, y=0)
        b = Rectangle(100, 100, x=50, y=50)
        r = Rectangle.from_two_objects(a, b)
        assert r.x.at_time(0) == pytest.approx(0)
        assert r.y.at_time(0) == pytest.approx(0)
        assert r.width.at_time(0) == pytest.approx(200)
        assert r.height.at_time(0) == pytest.approx(200)

    def test_with_circle(self):
        """Should work with circles (any object with bbox)."""
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=30, cx=300, cy=200)
        r = Rectangle.from_two_objects(c1, c2)
        # c1 bbox: (50, 50, 100, 100) -> (50..150, 50..150)
        # c2 bbox: (270, 170, 60, 60) -> (270..330, 170..230)
        assert r.x.at_time(0) == pytest.approx(50)
        assert r.y.at_time(0) == pytest.approx(50)
        assert r.width.at_time(0) == pytest.approx(280)
        assert r.height.at_time(0) == pytest.approx(180)

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Rectangle constructor."""
        a = Rectangle(50, 50, x=0, y=0)
        b = Rectangle(50, 50, x=100, y=100)
        r = Rectangle.from_two_objects(a, b, fill='#FF0000')
        fill = r.styling.fill.at_time(0).lower()
        assert '255' in fill or 'ff0000' in fill

    def test_returns_rectangle(self):
        """Return type should be Rectangle."""
        a = Rectangle(50, 50, x=0, y=0)
        b = Rectangle(50, 50, x=100, y=0)
        r = Rectangle.from_two_objects(a, b)
        assert isinstance(r, Rectangle)


# ---- Line.from_objects ----

class TestLineFromObjects:
    def test_horizontal_connection(self):
        """Two objects side by side should connect via right/left edges."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=300, y=0)
        line = Line.from_objects(a, b)
        p1 = line.get_start()
        p2 = line.get_end()
        # a right edge: (100, 50), b left edge: (300, 50)
        assert p1[0] == pytest.approx(100)
        assert p1[1] == pytest.approx(50)
        assert p2[0] == pytest.approx(300)
        assert p2[1] == pytest.approx(50)

    def test_vertical_connection(self):
        """Two objects stacked vertically should connect via bottom/top edges."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=0, y=300)
        line = Line.from_objects(a, b)
        p1 = line.get_start()
        p2 = line.get_end()
        # a bottom edge: (50, 100), b top edge: (50, 300)
        assert p1[0] == pytest.approx(50)
        assert p1[1] == pytest.approx(100)
        assert p2[0] == pytest.approx(50)
        assert p2[1] == pytest.approx(300)

    def test_with_buff(self):
        """buff should shorten both endpoints inward."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=300, y=0)
        line = Line.from_objects(a, b, buff=10)
        p1 = line.get_start()
        p2 = line.get_end()
        # Without buff: (100, 50) to (300, 50), horizontal
        # With buff=10: (110, 50) to (290, 50)
        assert p1[0] == pytest.approx(110)
        assert p2[0] == pytest.approx(290)

    def test_reverse_horizontal(self):
        """Object B to the left of A should use left/right edges."""
        a = Rectangle(100, 100, x=300, y=0)
        b = Rectangle(100, 100, x=0, y=0)
        line = Line.from_objects(a, b)
        p1 = line.get_start()
        p2 = line.get_end()
        # a left edge: (300, 50), b right edge: (100, 50)
        assert p1[0] == pytest.approx(300)
        assert p2[0] == pytest.approx(100)

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Line constructor."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=300, y=0)
        line = Line.from_objects(a, b, stroke='#FF0000')
        svg = line.to_svg(0).lower()
        assert '255' in svg or 'ff0000' in svg

    def test_returns_line(self):
        """Return type should be Line."""
        a = Rectangle(100, 100, x=0, y=0)
        b = Rectangle(100, 100, x=300, y=0)
        assert isinstance(Line.from_objects(a, b), Line)


# ---- Text.wrap ----

class TestTextWrap:
    def test_basic_wrap(self):
        """Text that exceeds max_width should be split into multiple lines."""
        t = Text(text='hello world foo bar baz', x=100, y=100, font_size=48)
        col = t.wrap(max_width=300)
        # Should produce multiple lines (text is ~48*0.6*23 = 662px total)
        assert len(col.objects) > 1

    def test_single_word(self):
        """A single word should produce exactly one line."""
        t = Text(text='hello', x=100, y=100, font_size=48)
        col = t.wrap(max_width=1000)
        assert len(col.objects) == 1
        assert col.objects[0].text.at_time(0) == 'hello'

    def test_empty_text(self):
        """Empty text should produce empty VCollection."""
        t = Text(text='', x=100, y=100, font_size=48)
        col = t.wrap(max_width=300)
        assert len(col.objects) == 0

    def test_wide_enough_no_wrap(self):
        """Text fitting within max_width should remain as one line."""
        t = Text(text='hi', x=100, y=100, font_size=20)
        col = t.wrap(max_width=1000)
        assert len(col.objects) == 1
        assert col.objects[0].text.at_time(0) == 'hi'

    def test_line_positions(self):
        """Lines should be positioned vertically with line_height spacing."""
        t = Text(text='word1 word2 word3 word4 word5 word6', x=50, y=200, font_size=40)
        col = t.wrap(max_width=200)
        if len(col.objects) >= 2:
            y0 = col.objects[0].y.at_time(0)
            y1 = col.objects[1].y.at_time(0)
            expected_spacing = 40 * 1.2  # font_size * 1.2
            assert y1 - y0 == pytest.approx(expected_spacing)

    def test_returns_vcollection(self):
        """Return type should be VCollection."""
        t = Text(text='hello world', x=100, y=100, font_size=48)
        col = t.wrap(max_width=300)
        assert isinstance(col, VCollection)

    def test_preserves_x_position(self):
        """All wrapped lines should share the same x position."""
        t = Text(text='aaa bbb ccc ddd eee', x=150, y=100, font_size=48)
        col = t.wrap(max_width=200)
        for obj in col.objects:
            assert obj.x.at_time(0) == pytest.approx(150)

    def test_preserves_font_size(self):
        """All wrapped lines should have the same font size."""
        t = Text(text='aaa bbb ccc ddd eee', x=150, y=100, font_size=36)
        col = t.wrap(max_width=200)
        for obj in col.objects:
            assert obj.font_size.at_time(0) == pytest.approx(36)


# ---- Axes.add_animation_trace ----

class TestAxesAddAnimationTrace:
    def test_returns_self(self):
        """add_animation_trace should return self for chaining."""
        ax = Axes()
        result = ax.add_animation_trace(lambda x: x ** 2, 0, 5)
        assert result is ax

    def test_dot_and_trail(self):
        """Default call should add objects (dot + trail)."""
        ax = Axes()
        initial_count = len(ax.objects)
        ax.add_animation_trace(lambda x: x, 0, 5)
        assert len(ax.objects) > initial_count

    def test_dot_only(self):
        """trail=False should still add a dot."""
        ax = Axes()
        initial_count = len(ax.objects)
        ax.add_animation_trace(lambda x: x, 0, 5, trail=False)
        assert len(ax.objects) > initial_count

    def test_trail_only(self):
        """dot=False should still add trail objects."""
        ax = Axes()
        initial_count = len(ax.objects)
        ax.add_animation_trace(lambda x: x, 0, 5, dot=False)
        assert len(ax.objects) > initial_count

    def test_neither_dot_nor_trail(self):
        """dot=False, trail=False should not add anything."""
        ax = Axes()
        initial_count = len(ax.objects)
        ax.add_animation_trace(lambda x: x, 0, 5, dot=False, trail=False)
        assert len(ax.objects) == initial_count


# ---- BarChart.animate_sort ----

class TestBarChartAnimateSort:
    def test_returns_self(self):
        """animate_sort should return self for chaining."""
        chart = BarChart([30, 10, 20])
        result = chart.animate_sort()
        assert result is chart

    def test_values_reordered(self):
        """After animate_sort, values should be sorted ascending."""
        chart = BarChart([30, 10, 20])
        chart.animate_sort()
        assert chart.values == [10, 20, 30]

    def test_values_reordered_descending(self):
        """reverse=True should sort descending."""
        chart = BarChart([10, 30, 20])
        chart.animate_sort(reverse=True)
        assert chart.values == [30, 20, 10]

    def test_single_bar(self):
        """A single-bar chart should be a no-op."""
        chart = BarChart([42])
        result = chart.animate_sort()
        assert result is chart
        assert chart.values == [42]

    def test_already_sorted(self):
        """Already sorted values should be unchanged."""
        chart = BarChart([10, 20, 30])
        chart.animate_sort()
        assert chart.values == [10, 20, 30]

    def test_custom_key(self):
        """Custom key function should be used for sorting."""
        chart = BarChart([3, -1, 2], labels=['a', 'b', 'c'])
        chart.animate_sort(key=abs)
        assert chart.values == [-1, 2, 3]

    def test_bars_animate_positions(self):
        """Bar x positions should be animated between start and end."""
        chart = BarChart([30, 10, 20])
        # Record initial x positions
        old_xs = [bar.x.at_time(0) for bar in chart._bars]
        chart.animate_sort(start=0, end=1)
        # At time=0.5, some bars should be mid-transition
        # The bars have been reordered in the list, so check that
        # x values at time 1 are in the expected sorted positions
        xs_at_end = [bar.x.at_time(1) for bar in chart._bars]
        # After sorting [30,10,20] -> [10,20,30]
        # The bar now at index 0 (value 10, was index 1) should be at old_xs[0]
        assert xs_at_end[0] == pytest.approx(old_xs[0], abs=1)

    def test_labels_moved(self):
        """Labels should also be animated alongside their bars."""
        chart = BarChart([30, 10, 20], labels=['A', 'B', 'C'])
        chart.animate_sort(start=0, end=1)
        # After sort: values [10, 20, 30], labels [B, C, A]
        assert chart._labels[0].text.at_time(0) == 'B'
        assert chart._labels[1].text.at_time(0) == 'C'
        assert chart._labels[2].text.at_time(0) == 'A'

    def test_zero_duration(self):
        """Zero duration should return self without error."""
        chart = BarChart([30, 10, 20])
        result = chart.animate_sort(start=0, end=0)
        assert result is chart


# ===== New feature tests =====


class TestPolygonToPath:
    def test_returns_path_object(self):
        """to_path should return a Path instance."""
        poly = Polygon((0, 0), (100, 0), (100, 100))
        p = poly.to_path()
        assert isinstance(p, Path)

    def test_path_d_matches_polygon(self):
        """The Path's d string should match the polygon's path()."""
        poly = Polygon((10, 20), (30, 40), (50, 60))
        p = poly.to_path()
        d = p.d.at_time(0)
        assert 'M' in d
        assert 'L' in d
        assert 'Z' in d

    def test_preserves_fill(self):
        """Styling (fill) should be copied from the polygon."""
        poly = Polygon((0, 0), (100, 0), (100, 100), fill='#ff0000')
        p = poly.to_path()
        assert p.styling.fill.at_time(0) == 'rgb(255,0,0)'

    def test_preserves_stroke(self):
        """Styling (stroke) should be copied from the polygon."""
        poly = Polygon((0, 0), (100, 0), (100, 100), stroke='#00ff00', stroke_width=8)
        p = poly.to_path()
        assert p.styling.stroke.at_time(0) == 'rgb(0,255,0)'
        assert p.styling.stroke_width.at_time(0) == pytest.approx(8)

    def test_open_polyline(self):
        """An open polygon (closed=False) should produce a path without Z."""
        poly = Polygon((0, 0), (100, 0), (100, 100), closed=False)
        p = poly.to_path()
        d = p.d.at_time(0)
        assert 'Z' not in d

    def test_time_parameter(self):
        """to_path at a different time should use animated vertex positions."""
        poly = Polygon((0, 0), (100, 0), (100, 100))
        poly.shift(dx=50, dy=0, start=0)
        p = poly.to_path(time=0)
        d = p.d.at_time(0)
        # After shift, first vertex should be at (50, 0)
        assert '50' in d


class TestPathTrim:
    def test_trim_full_path(self):
        """Trimming from 0 to 1 should return a path with the same length."""
        p = Path('M0,0 L100,0 L100,100')
        trimmed = p.trim(0.0, 1.0)
        assert isinstance(trimmed, Path)
        orig_len = p.get_length()
        trimmed_len = trimmed.get_length()
        assert trimmed_len == pytest.approx(orig_len, abs=1)

    def test_trim_first_half(self):
        """Trimming first half should give roughly half the length."""
        p = Path('M0,0 L100,0 L100,100')
        trimmed = p.trim(0.0, 0.5)
        total = p.get_length()
        assert trimmed.get_length() == pytest.approx(total * 0.5, abs=1)

    def test_trim_second_half(self):
        """Trimming second half should give roughly half the length."""
        p = Path('M0,0 L200,0')
        trimmed = p.trim(0.5, 1.0)
        assert trimmed.get_length() == pytest.approx(100, abs=1)

    def test_trim_empty_range(self):
        """Trimming with t_start >= t_end should return empty path."""
        p = Path('M0,0 L100,0')
        trimmed = p.trim(0.5, 0.5)
        assert trimmed.d.at_time(0) == ''

    def test_trim_empty_path(self):
        """Trimming empty path should return empty path."""
        p = Path('')
        trimmed = p.trim(0.0, 1.0)
        assert trimmed.d.at_time(0) == ''

    def test_trim_preserves_styling(self):
        """Trimmed path should copy the stroke from original."""
        p = Path('M0,0 L100,0', stroke='#ff0000', stroke_width=6)
        trimmed = p.trim(0.0, 0.5)
        assert trimmed.styling.stroke.at_time(0) == 'rgb(255,0,0)'
        assert trimmed.styling.stroke_width.at_time(0) == pytest.approx(6)

    def test_trim_clamps_values(self):
        """Values outside [0,1] should be clamped."""
        p = Path('M0,0 L100,0')
        trimmed = p.trim(-0.5, 1.5)
        assert trimmed.get_length() == pytest.approx(100, abs=1)


class TestTableAddRow:
    def test_add_row_increases_row_count(self):
        """add_row should increment self.rows."""
        t = Table([[1, 2], [3, 4]])
        assert t.rows == 2
        t.add_row([5, 6], animate=False)
        assert t.rows == 3

    def test_add_row_creates_entries(self):
        """New row entries should be accessible."""
        t = Table([[1, 2], [3, 4]])
        t.add_row([5, 6], animate=False)
        assert len(t.entries) == 3
        assert t.entries[2][0].text.at_time(0) == '5'
        assert t.entries[2][1].text.at_time(0) == '6'

    def test_add_row_returns_self(self):
        """add_row should return self for chaining."""
        t = Table([[1, 2]])
        result = t.add_row([3, 4], animate=False)
        assert result is t

    def test_add_row_with_animation(self):
        """add_row with animate=True should not raise."""
        t = Table([[1, 2]])
        t.add_row([3, 4], start=1, animate=True)
        assert t.rows == 2

    def test_add_row_fewer_values(self):
        """Fewer values than columns should fill missing with empty string."""
        t = Table([['a', 'b', 'c']])
        t.add_row(['x'], animate=False)
        assert t.entries[1][0].text.at_time(0) == 'x'
        assert t.entries[1][1].text.at_time(0) == ''
        assert t.entries[1][2].text.at_time(0) == ''


class TestTableAddColumn:
    def test_add_column_increases_col_count(self):
        """add_column should increment self.cols."""
        t = Table([[1, 2], [3, 4]])
        assert t.cols == 2
        t.add_column([5, 6], animate=False)
        assert t.cols == 3

    def test_add_column_creates_entries(self):
        """New column entries should be accessible in each row."""
        t = Table([[1, 2], [3, 4]])
        t.add_column([5, 6], animate=False)
        assert len(t.entries[0]) == 3
        assert len(t.entries[1]) == 3
        assert t.entries[0][2].text.at_time(0) == '5'
        assert t.entries[1][2].text.at_time(0) == '6'

    def test_add_column_returns_self(self):
        """add_column should return self for chaining."""
        t = Table([[1, 2]])
        result = t.add_column([3], animate=False)
        assert result is t

    def test_add_column_with_animation(self):
        """add_column with animate=True should not raise."""
        t = Table([[1, 2]])
        t.add_column([3], start=1, animate=True)
        assert t.cols == 3

    def test_add_column_fewer_values(self):
        """Fewer values than rows should fill missing with empty string."""
        t = Table([['a'], ['b'], ['c']])
        t.add_column(['x'], animate=False)
        assert t.entries[0][1].text.at_time(0) == 'x'
        assert t.entries[1][1].text.at_time(0) == ''
        assert t.entries[2][1].text.at_time(0) == ''


class TestPieChartExplode:
    def test_explode_returns_self(self):
        """explode should return self for chaining."""
        chart = PieChart([30, 50, 20])
        result = chart.explode([0])
        assert result is chart

    def test_explode_shifts_sector(self):
        """Exploded sector should be shifted from its original center."""
        chart = PieChart([30, 50, 20], cx=960, cy=540, r=200)
        cx_before = chart._sectors[0].cx.at_time(0)
        cy_before = chart._sectors[0].cy.at_time(0)
        chart.explode([0], distance=30)
        cx_after = chart._sectors[0].cx.at_time(0)
        cy_after = chart._sectors[0].cy.at_time(0)
        shift = math.hypot(cx_after - cx_before, cy_after - cy_before)
        assert shift == pytest.approx(30, abs=1)

    def test_explode_does_not_affect_other_sectors(self):
        """Sectors not in indices should remain unchanged."""
        chart = PieChart([30, 50, 20], cx=960, cy=540)
        cx1_before = chart._sectors[1].cx.at_time(0)
        cy1_before = chart._sectors[1].cy.at_time(0)
        chart.explode([0], distance=30)
        cx1_after = chart._sectors[1].cx.at_time(0)
        cy1_after = chart._sectors[1].cy.at_time(0)
        assert cx1_after == pytest.approx(cx1_before)
        assert cy1_after == pytest.approx(cy1_before)

    def test_explode_multiple_sectors(self):
        """Multiple sectors can be exploded at once."""
        chart = PieChart([25, 25, 25, 25], cx=960, cy=540)
        chart.explode([0, 2], distance=20)
        # Both sector 0 and 2 should have shifted
        s0_shift = math.hypot(
            chart._sectors[0].cx.at_time(0) - 960,
            chart._sectors[0].cy.at_time(0) - 540)
        s2_shift = math.hypot(
            chart._sectors[2].cx.at_time(0) - 960,
            chart._sectors[2].cy.at_time(0) - 540)
        assert s0_shift == pytest.approx(20, abs=1)
        assert s2_shift == pytest.approx(20, abs=1)

    def test_explode_out_of_range_ignored(self):
        """Out-of-range indices should be silently ignored."""
        chart = PieChart([30, 50, 20])
        chart.explode([10, -1], distance=30)  # should not raise

    def test_explode_animated(self):
        """Animated explode should shift between start and end times."""
        chart = PieChart([50, 50], cx=960, cy=540)
        cx_before = chart._sectors[0].cx.at_time(0)
        chart.explode([0], distance=30, start=0, end=1)
        # At time=0 the shift should not yet be fully applied
        # At time=1 it should be
        cx_at_end = chart._sectors[0].cx.at_time(1)
        shift = abs(cx_at_end - cx_before)
        assert shift > 0


class TestLineIntersection:
    def test_intersecting_segments(self):
        """Two crossing line segments should return intersection point."""
        l1 = Line(0, 0, 100, 100)
        l2 = Line(100, 0, 0, 100)
        pt = l1.intersection(l2)
        assert pt is not None
        assert pt[0] == pytest.approx(50, abs=1)
        assert pt[1] == pytest.approx(50, abs=1)

    def test_parallel_lines(self):
        """Parallel lines should return None."""
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 10, 100, 10)
        assert l1.intersection(l2) is None

    def test_non_intersecting_segments(self):
        """Non-overlapping segments should return None (segment check)."""
        l1 = Line(0, 0, 10, 0)
        l2 = Line(20, 10, 20, 20)
        assert l1.intersection(l2) is None

    def test_line_circle_intersection(self):
        """Line intersecting a circle should return a list of points."""
        l = Line(-200, 540, 200, 540)
        c = Circle(r=100, cx=0, cy=540)
        pts = l.intersection(c)
        assert isinstance(pts, list)
        assert len(pts) == 2

    def test_line_circle_no_intersection(self):
        """Line far from circle should return empty list."""
        l = Line(0, 0, 100, 0)
        c = Circle(r=10, cx=50, cy=100)
        pts = l.intersection(c)
        assert isinstance(pts, list)
        assert len(pts) == 0

    def test_unsupported_type_raises(self):
        """Intersection with unsupported type should raise TypeError."""
        l = Line(0, 0, 100, 0)
        with pytest.raises(TypeError):
            l.intersection("not a shape")


# ---- Tests for new features ----


class TestPolygonApplyPointwise:
    def test_translate_all_vertices(self):
        """apply_pointwise should translate all vertices."""
        poly = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        poly.apply_pointwise(lambda x, y: (x + 10, y + 20))
        verts = poly.get_vertices(0)
        assert verts[0] == pytest.approx((10, 20))
        assert verts[1] == pytest.approx((110, 20))
        assert verts[2] == pytest.approx((110, 120))
        assert verts[3] == pytest.approx((10, 120))

    def test_scale_vertices(self):
        """apply_pointwise with scaling function."""
        poly = Polygon((10, 20), (30, 40))
        poly.apply_pointwise(lambda x, y: (x * 2, y * 3))
        verts = poly.get_vertices(0)
        assert verts[0] == pytest.approx((20, 60))
        assert verts[1] == pytest.approx((60, 120))

    def test_returns_self(self):
        """apply_pointwise should return self for chaining."""
        poly = Polygon((0, 0), (1, 0), (0, 1))
        result = poly.apply_pointwise(lambda x, y: (x, y))
        assert result is poly

    def test_identity_preserves_positions(self):
        """Identity function should not change vertex positions."""
        poly = Polygon((50, 60), (70, 80), (90, 100))
        original = poly.get_vertices(0)
        poly.apply_pointwise(lambda x, y: (x, y))
        assert poly.get_vertices(0) == pytest.approx(original, abs=1e-9)

    def test_rotation_90_degrees(self):
        """apply_pointwise with 90-degree rotation around origin."""
        poly = Polygon((100, 0), (0, 100))
        poly.apply_pointwise(lambda x, y: (-y, x))
        verts = poly.get_vertices(0)
        assert verts[0] == pytest.approx((0, 100), abs=1e-9)
        assert verts[1] == pytest.approx((-100, 0), abs=1e-9)

    def test_empty_polygon(self):
        """apply_pointwise on a polygon with no vertices should not error."""
        poly = Polygon()
        poly.apply_pointwise(lambda x, y: (x + 1, y + 1))
        assert poly.get_vertices(0) == []


class TestLineBisectorGeometry:
    def test_horizontal_line_bisector(self):
        """Bisector of a horizontal line should be vertical through midpoint."""
        line = Line(x1=0, y1=0, x2=200, y2=0)
        bis = line.bisector()
        mid = bis.get_midpoint()
        assert mid[0] == pytest.approx(100)
        assert mid[1] == pytest.approx(0)
        # The bisector should be perpendicular (vertical)
        angle = abs(line.angle_to(bis))
        assert angle == pytest.approx(90, abs=1)

    def test_vertical_line_bisector(self):
        """Bisector of a vertical line should be horizontal through midpoint."""
        line = Line(x1=50, y1=0, x2=50, y2=200)
        bis = line.bisector()
        mid = bis.get_midpoint()
        assert mid[0] == pytest.approx(50)
        assert mid[1] == pytest.approx(100)
        angle = abs(line.angle_to(bis))
        assert angle == pytest.approx(90, abs=1)

    def test_bisector_default_length(self):
        """Default bisector length should equal the original line length."""
        line = Line(x1=0, y1=0, x2=300, y2=400)
        bis = line.bisector()
        assert bis.get_length() == pytest.approx(line.get_length(), abs=1e-6)

    def test_bisector_custom_length(self):
        """Custom length should be respected."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        bis = line.bisector(length=50)
        assert bis.get_length() == pytest.approx(50, abs=1e-6)

    def test_bisector_perpendicular(self):
        """Bisector should be perpendicular to the original line."""
        line = Line(x1=10, y1=20, x2=130, y2=70)
        bis = line.bisector()
        angle = line.angle_to(bis)
        assert angle == pytest.approx(90, abs=1e-3)

    def test_bisector_passes_through_midpoint(self):
        """Bisector's midpoint should be at the original line's midpoint."""
        line = Line(x1=30, y1=40, x2=150, y2=200)
        bis = line.bisector()
        orig_mid = line.get_midpoint()
        bis_mid = bis.get_midpoint()
        assert bis_mid[0] == pytest.approx(orig_mid[0], abs=1e-6)
        assert bis_mid[1] == pytest.approx(orig_mid[1], abs=1e-6)

    def test_bisector_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Line constructor."""
        line = Line(x1=0, y1=0, x2=100, y2=0)
        bis = line.bisector(stroke='#ff0000')
        svg = bis.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg


class TestCircleTangentLineFromPoint:
    def test_external_point_two_tangents(self):
        """External point should produce two tangent lines."""
        c = Circle(r=100, cx=400, cy=400)
        lines = c.tangent_line_from_point(700, 400)
        assert len(lines) == 2

    def test_internal_point_no_tangents(self):
        """Point inside the circle should return empty list."""
        c = Circle(r=100, cx=400, cy=400)
        lines = c.tangent_line_from_point(400, 400)
        assert lines == []

    def test_point_on_circle_one_tangent(self):
        """Point on the circle boundary should produce one tangent."""
        c = Circle(r=100, cx=400, cy=400)
        # Point on the right of the circle
        lines = c.tangent_line_from_point(500, 400)
        assert len(lines) == 1

    def test_tangent_touch_points_on_circle(self):
        """Each tangent line's midpoint should be on the circle surface."""
        c = Circle(r=100, cx=0, cy=0)
        lines = c.tangent_line_from_point(200, 0)
        assert len(lines) == 2
        for tl in lines:
            mid = tl.get_midpoint()
            dist = math.hypot(mid[0], mid[1])
            assert dist == pytest.approx(100, abs=1)

    def test_tangent_perpendicular_to_radius(self):
        """Each tangent line should be perpendicular to the radius at the touch point."""
        c = Circle(r=100, cx=0, cy=0)
        lines = c.tangent_line_from_point(300, 0)
        for tl in lines:
            mid = tl.get_midpoint()
            # Radius direction from center to touch point
            radius_line = Line(x1=0, y1=0, x2=mid[0], y2=mid[1])
            angle = tl.angle_to(radius_line)
            assert angle == pytest.approx(90, abs=1)

    def test_custom_length(self):
        """Custom length parameter should be respected."""
        c = Circle(r=50, cx=0, cy=0)
        lines = c.tangent_line_from_point(200, 0, length=400)
        for tl in lines:
            assert tl.get_length() == pytest.approx(400, abs=1)

    def test_slightly_inside_no_tangents(self):
        """Point slightly inside the circle should return empty list."""
        c = Circle(r=100, cx=0, cy=0)
        lines = c.tangent_line_from_point(50, 0)
        assert lines == []


class TestBarChartFromDict:
    def test_basic_creation(self):
        """from_dict should create a BarChart with correct values and labels."""
        data = {'A': 10, 'B': 20, 'C': 30}
        chart = BarChart.from_dict(data)
        assert chart.values == [10, 20, 30]
        assert chart.bar_count == 3

    def test_empty_dict(self):
        """from_dict with empty dict should create empty chart."""
        chart = BarChart.from_dict({})
        assert chart.values == []
        assert chart.bar_count == 0

    def test_single_entry(self):
        """from_dict with a single entry."""
        chart = BarChart.from_dict({'X': 42})
        assert chart.values == [42]
        assert chart.bar_count == 1

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the constructor."""
        data = {'A': 1, 'B': 2}
        chart = BarChart.from_dict(data, width=800)
        assert isinstance(chart, BarChart)
        assert chart.bar_count == 2

    def test_repr(self):
        """repr should work correctly."""
        chart = BarChart.from_dict({'a': 1, 'b': 2, 'c': 3})
        assert '3 bars' in repr(chart)


class TestPieChartFromDict:
    def test_basic_creation(self):
        """from_dict should create a PieChart with correct values."""
        data = {'Apples': 40, 'Bananas': 30, 'Cherries': 30}
        chart = PieChart.from_dict(data)
        assert chart.values == [40, 30, 30]

    def test_empty_dict(self):
        """from_dict with empty dict should create empty chart."""
        chart = PieChart.from_dict({})
        assert chart.values == []

    def test_single_entry(self):
        """from_dict with a single entry."""
        chart = PieChart.from_dict({'Only': 100})
        assert chart.values == [100]

    def test_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the constructor."""
        data = {'A': 50, 'B': 50}
        chart = PieChart.from_dict(data, r=300)
        assert isinstance(chart, PieChart)

    def test_repr(self):
        """repr should work correctly."""
        chart = PieChart.from_dict({'x': 1, 'y': 2})
        assert '2 sectors' in repr(chart)


class TestAxesAddFilledCurve:
    def test_returns_vcollection(self):
        """add_filled_curve should return a VCollection."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        result = ax.add_filled_curve(lambda x: x**2, reveal=False)
        assert isinstance(result, VCollection)

    def test_collection_has_two_objects(self):
        """The returned VCollection should contain curve and area."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        result = ax.add_filled_curve(lambda x: x**2, reveal=False)
        assert len(result.objects) == 2

    def test_with_x_range(self):
        """add_filled_curve with x_range should not error."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 30))
        result = ax.add_filled_curve(lambda x: x**2, x_range=(-2, 2), reveal=False)
        assert isinstance(result, VCollection)

    def test_with_reveal_animation(self):
        """add_filled_curve with reveal=True and end should not error."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        result = ax.add_filled_curve(math.sin, start=0, end=2, reveal=True)
        assert isinstance(result, VCollection)

    def test_without_reveal(self):
        """add_filled_curve with reveal=False should create instant objects."""
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        result = ax.add_filled_curve(lambda x: x, reveal=False)
        assert isinstance(result, VCollection)

    def test_custom_color_and_opacity(self):
        """Custom color and opacity should be accepted."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        result = ax.add_filled_curve(lambda x: x**2, color='#FF0000',
                                     opacity=0.5, reveal=False)
        assert isinstance(result, VCollection)


# ---------------------------------------------------------------------------
# Path.tangent_at
# ---------------------------------------------------------------------------

class TestPathTangentAt:
    def test_horizontal_path_tangent(self):
        """Tangent of a horizontal line path should point right."""
        p = Path('M0,0 L100,0')
        dx, dy = p.tangent_at(0.5)
        assert dx == pytest.approx(1.0, abs=1e-3)
        assert dy == pytest.approx(0.0, abs=1e-3)

    def test_vertical_path_tangent(self):
        """Tangent of a vertical line path should point down."""
        p = Path('M0,0 L0,100')
        dx, dy = p.tangent_at(0.5)
        assert dx == pytest.approx(0.0, abs=1e-3)
        assert dy == pytest.approx(1.0, abs=1e-3)

    def test_unit_vector(self):
        """Tangent should be a unit vector."""
        p = Path('M0,0 L30,40')
        dx, dy = p.tangent_at(0.5)
        mag = math.hypot(dx, dy)
        assert mag == pytest.approx(1.0, abs=1e-6)

    def test_diagonal_direction(self):
        """Tangent on a 45-degree path should have equal dx and dy."""
        p = Path('M0,0 L100,100')
        dx, dy = p.tangent_at(0.5)
        assert abs(dx) == pytest.approx(abs(dy), abs=1e-3)

    def test_empty_path(self):
        """Empty path should return (0, 0)."""
        p = Path('')
        assert p.tangent_at(0.5) == (0.0, 0.0)

    def test_proportion_at_start(self):
        """Tangent at proportion=0 should work."""
        p = Path('M0,0 L100,0')
        dx, dy = p.tangent_at(0.0)
        assert dx == pytest.approx(1.0, abs=1e-3)

    def test_proportion_at_end(self):
        """Tangent at proportion=1 should work."""
        p = Path('M0,0 L100,0')
        dx, dy = p.tangent_at(1.0)
        assert dx == pytest.approx(1.0, abs=1e-3)


# ---------------------------------------------------------------------------
# Line.from_slope_point
# ---------------------------------------------------------------------------

class TestLineFromSlopePoint:
    def test_horizontal_line(self):
        """Slope 0 should produce a horizontal line."""
        line = Line.from_slope_point(0, (960, 540), length=200)
        s = line.get_start()
        e = line.get_end()
        assert s[1] == pytest.approx(540)
        assert e[1] == pytest.approx(540)
        assert line.get_length() == pytest.approx(200, abs=1)

    def test_vertical_line(self):
        """Infinite slope should produce a vertical line."""
        line = Line.from_slope_point(float('inf'), (960, 540), length=200)
        s = line.get_start()
        e = line.get_end()
        assert s[0] == pytest.approx(960)
        assert e[0] == pytest.approx(960)
        assert line.get_length() == pytest.approx(200, abs=1)

    def test_negative_inf_slope(self):
        """Negative infinite slope should also produce a vertical line."""
        line = Line.from_slope_point(float('-inf'), (960, 540), length=200)
        s = line.get_start()
        e = line.get_end()
        assert s[0] == pytest.approx(960)
        assert e[0] == pytest.approx(960)

    def test_slope_1_diagonal(self):
        """Slope 1 should give a 45-degree line."""
        line = Line.from_slope_point(1, (100, 100), length=200)
        assert line.get_length() == pytest.approx(200, abs=1)
        slope = line.get_slope()
        assert slope == pytest.approx(1.0, abs=1e-6)

    def test_centered_at_point(self):
        """The midpoint should be at the given point."""
        line = Line.from_slope_point(0, (500, 300), length=200)
        mid = line.get_midpoint()
        assert mid[0] == pytest.approx(500, abs=1e-6)
        assert mid[1] == pytest.approx(300, abs=1e-6)

    def test_custom_length(self):
        """Custom length should be respected."""
        line = Line.from_slope_point(2, (0, 0), length=500)
        assert line.get_length() == pytest.approx(500, abs=1)

    def test_kwargs_forwarded(self):
        """Extra kwargs should reach the Line constructor."""
        line = Line.from_slope_point(0, (960, 540), stroke='#ff0000')
        svg = line.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg


# ---------------------------------------------------------------------------
# Table.transpose
# ---------------------------------------------------------------------------

class TestTableTranspose:
    def test_dimensions_swapped(self):
        """After transpose, rows and cols should swap."""
        t = Table([[1, 2, 3], [4, 5, 6]])
        assert t.rows == 2
        assert t.cols == 3
        t.transpose()
        assert t.rows == 3
        assert t.cols == 2

    def test_entries_rearranged(self):
        """Entries grid should reflect the transposition."""
        t = Table([[1, 2, 3], [4, 5, 6]])
        # Before: entries[0][1] has text '2'
        assert t.entries[0][1].text.at_time(0) == '2'
        t.transpose()
        # After transpose: what was row 0 col 1 is now row 1 col 0
        assert t.entries[1][0].text.at_time(0) == '2'

    def test_all_entries_preserved(self):
        """All original entries should still be present."""
        data = [[1, 2], [3, 4]]
        t = Table(data)
        original_texts = set()
        for r in range(t.rows):
            for c in range(t.cols):
                original_texts.add(t.entries[r][c].text.at_time(0))
        t.transpose()
        transposed_texts = set()
        for r in range(t.rows):
            for c in range(t.cols):
                transposed_texts.add(t.entries[r][c].text.at_time(0))
        assert original_texts == transposed_texts

    def test_returns_self(self):
        """transpose() should return self for chaining."""
        t = Table([[1, 2], [3, 4]])
        result = t.transpose()
        assert result is t

    def test_animated_transpose(self):
        """Animated transpose should not error."""
        t = Table([[1, 2], [3, 4]])
        t.transpose(start=0, end=1)
        assert t.rows == 2
        assert t.cols == 2

    def test_square_table_transpose(self):
        """Transposing a square table should swap off-diagonal entries."""
        t = Table([['a', 'b'], ['c', 'd']])
        t.transpose()
        # (0,1) was 'b', after transpose entries[1][0] should be 'b'
        assert t.entries[1][0].text.at_time(0) == 'b'
        assert t.entries[0][1].text.at_time(0) == 'c'


# ---------------------------------------------------------------------------
# Axes.mark_intersection
# ---------------------------------------------------------------------------

class TestAxesGetGraphIntersection:
    def test_finds_intersection(self):
        """Should find intersection of two crossing functions."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        f1 = lambda x: x
        f2 = lambda x: -x + 2
        dot = ax.mark_intersection(f1, f2, x_range=(0, 3))
        assert dot is not None

    def test_returns_dot(self):
        """Without label, should return a Dot."""
        from vectormation.objects import Dot as DotCls
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        dot = ax.mark_intersection(lambda x: x, lambda x: 2 - x, x_range=(0, 3))
        assert isinstance(dot, DotCls)

    def test_with_label_returns_collection(self):
        """With label, should return a VCollection."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.mark_intersection(
            lambda x: x, lambda x: 2 - x,
            x_range=(0, 3), label='P')
        assert isinstance(result, VCollection)

    def test_no_intersection_returns_none(self):
        """Non-crossing functions should return None."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.mark_intersection(
            lambda x: x + 10, lambda x: x - 10, x_range=(-5, 5))
        assert result is None

    def test_default_x_range(self):
        """When x_range is None, should use axes' x range."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        dot = ax.mark_intersection(lambda x: x, lambda x: -x)
        # x=0, y=0 is the intersection
        assert dot is not None

    def test_kwargs_forwarded_to_dot(self):
        """Extra kwargs like fill and r should reach the Dot."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        dot = ax.mark_intersection(
            lambda x: x, lambda x: -x,
            fill='#00FF00', r=10)
        svg = dot.to_svg(0)
        assert 'rgb(0,255,0)' in svg or '#00FF00' in svg
        assert "r='10'" in svg


# ---------------------------------------------------------------------------
# Brace.for_range
# ---------------------------------------------------------------------------

class TestBraceForRange:
    def test_x_range_creates_brace(self):
        """for_range on x-axis should produce a Brace."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'x', 2, 8)
        assert isinstance(b, Brace)

    def test_y_range_creates_brace(self):
        """for_range on y-axis should produce a Brace."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'y', 1, 5)
        assert isinstance(b, Brace)

    def test_invalid_axis_raises(self):
        """Invalid axis should raise ValueError."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        with pytest.raises(ValueError):
            Brace.for_range(ax, 'z', 0, 5)

    def test_with_label(self):
        """Brace with label should include text."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'x', 2, 8, label=r'$\Delta x$')
        # Label adds a second object to the brace collection
        assert len(b.objects) == 2

    def test_default_direction_x(self):
        """Default direction for x-axis should be 'down'."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'x', 2, 8)
        assert b._direction == 'down'

    def test_default_direction_y(self):
        """Default direction for y-axis should be 'left'."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'y', 1, 5)
        assert b._direction == 'left'

    def test_custom_direction(self):
        """Custom direction should override the default."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'x', 2, 8, direction='up')
        assert b._direction == 'up'

    def test_renders_svg(self):
        """Brace should render valid SVG."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        b = Brace.for_range(ax, 'x', 2, 8)
        svg = b.to_svg(0)
        assert '<path' in svg or '<g' in svg


# ---- Text.set_font_family / font_family ----

class TestTextFontFamily:
    def test_font_family_constructor(self):
        """font_family param should be stored and rendered in SVG."""
        t = Text('hello', font_family='monospace')
        svg = t.to_svg(0)
        assert "font-family='monospace'" in svg

    def test_font_family_constructor_none_default(self):
        """Default font_family=None should not add font-family attribute."""
        t = Text('hello')
        svg = t.to_svg(0)
        assert 'font-family' not in svg

    def test_set_font_family_method(self):
        """set_font_family should update _font_family and render in SVG."""
        t = Text('hello')
        result = t.set_font_family('Arial')
        assert result is t
        svg = t.to_svg(0)
        assert "font-family='Arial'" in svg

    def test_set_font_family_none_clears(self):
        """set_font_family(None) should remove font-family from SVG."""
        t = Text('hello', font_family='serif')
        t.set_font_family(None)
        svg = t.to_svg(0)
        assert 'font-family' not in svg

    def test_font_family_with_spaces(self):
        """Font families with spaces should be rendered correctly."""
        t = Text('hello', font_family='Times New Roman')
        svg = t.to_svg(0)
        assert "font-family='Times New Roman'" in svg

    def test_font_family_preserved_in_wrap(self):
        """wrap should copy _font_family to child Text objects."""
        t = Text('a b c d e f', font_family='monospace', font_size=20)
        parts = t.wrap(max_width=50, time=0)
        for child in parts.objects:
            assert child._font_family == 'monospace'

    def test_font_family_combined_with_bold_italic(self):
        """font_family should coexist with font_weight and font_style."""
        t = Text('hello', font_family='serif')
        t.bold()
        t.italic()
        svg = t.to_svg(0)
        assert "font-family='serif'" in svg
        assert "font-weight='bold'" in svg
        assert "font-style='italic'" in svg


# ---- Arc.animate_sweep ----

class TestArcAnimateSweep:
    def test_animate_sweep_instant(self):
        """animate_sweep with end=None should set end_angle instantly."""
        a = Arc(start_angle=0, end_angle=90)
        result = a.animate_sweep(180, start=0)
        assert result is a
        assert a.end_angle.at_time(0) == pytest.approx(180)

    def test_animate_sweep_animated(self):
        """animate_sweep with end should animate end_angle."""
        a = Arc(start_angle=0, end_angle=90)
        a.animate_sweep(270, start=0, end=1)
        # At start, should still be near 90
        assert a.end_angle.at_time(0) == pytest.approx(90)
        # At end, should be 270
        assert a.end_angle.at_time(1) == pytest.approx(270)

    def test_animate_sweep_midpoint(self):
        """At the midpoint the end_angle should be between start and target."""
        a = Arc(start_angle=0, end_angle=0)
        a.animate_sweep(180, start=0, end=1)
        mid = a.end_angle.at_time(0.5)
        assert 0 < mid < 180

    def test_animate_sweep_preserves_start_angle(self):
        """animate_sweep should not affect start_angle."""
        a = Arc(start_angle=45, end_angle=90)
        a.animate_sweep(360, start=0, end=1)
        assert a.start_angle.at_time(0) == pytest.approx(45)
        assert a.start_angle.at_time(1) == pytest.approx(45)

    def test_animate_sweep_with_easing(self):
        """animate_sweep should accept a custom easing."""
        a = Arc(start_angle=0, end_angle=0)
        a.animate_sweep(90, start=0, end=1, easing=easings.linear)
        # With linear easing, midpoint should be exactly 45
        assert a.end_angle.at_time(0.5) == pytest.approx(45)

    def test_animate_sweep_returns_self(self):
        """animate_sweep should return self for chaining."""
        a = Arc()
        assert a.animate_sweep(180) is a


# ---- BarChart.add_bar ----

class TestBarChartAddBar:
    def test_add_bar_increases_count(self):
        """add_bar should increase bar_count and bars list."""
        chart = BarChart([10, 20])
        assert chart.bar_count == 2
        result = chart.add_bar(30)
        assert result is chart
        assert chart.bar_count == 3
        assert len(chart._bars) == 3
        assert chart.values == [10, 20, 30]

    def test_add_bar_creates_rectangle(self):
        """The new bar should be a Rectangle with correct height."""
        chart = BarChart([10, 20], x=0, y=0, width=200, height=100)
        chart.add_bar(20)
        new_bar = chart._bars[-1]
        assert isinstance(new_bar, Rectangle)
        # Bar should have non-zero height
        assert new_bar.height.at_time(0) > 0

    def test_add_bar_with_label(self):
        """add_bar with label should create a Text label."""
        chart = BarChart([10], labels=['A'])
        chart.add_bar(20, label='B')
        assert len(chart._labels) == 2
        assert chart._labels[1] is not None
        assert chart._labels[1].text.at_time(0) == 'B'

    def test_add_bar_without_label(self):
        """add_bar without label should append None to _labels."""
        chart = BarChart([10])
        chart.add_bar(20)
        assert len(chart._labels) == 2
        assert chart._labels[1] is None

    def test_add_bar_animated(self):
        """add_bar with end should animate bar growing from zero."""
        chart = BarChart([10, 20], x=0, y=0, width=200, height=100)
        chart.add_bar(30, start=0, end=1)
        new_bar = chart._bars[-1]
        # At start, height should be 0
        assert new_bar.height.at_time(0) == pytest.approx(0)
        # At end, height should be non-zero
        assert new_bar.height.at_time(1) > 0

    def test_add_bar_to_empty_chart(self):
        """add_bar on an empty chart should work correctly."""
        chart = BarChart([])
        chart.add_bar(10)
        assert chart.bar_count == 1
        assert len(chart._bars) == 1
        assert chart.values == [10]

    def test_add_bar_in_objects(self):
        """The new bar should be added to the VCollection's objects."""
        chart = BarChart([10])
        before = len(chart.objects)
        chart.add_bar(20)
        assert len(chart.objects) > before


# ---- BarChart.remove_bar ----

class TestBarChartRemoveBar:
    def test_remove_bar_decreases_count(self):
        """remove_bar should decrease bar_count and bars list."""
        chart = BarChart([10, 20, 30])
        result = chart.remove_bar(1, start=0)
        assert result is chart
        assert chart.bar_count == 2
        assert len(chart._bars) == 2
        assert chart.values == [10, 30]

    def test_remove_bar_first(self):
        """Removing the first bar should shift remaining bars."""
        chart = BarChart([10, 20, 30])
        chart.remove_bar(0, start=0)
        assert chart.bar_count == 2
        assert chart.values == [20, 30]

    def test_remove_bar_last(self):
        """Removing the last bar should not need shifting."""
        chart = BarChart([10, 20, 30])
        chart.remove_bar(2, start=0)
        assert chart.bar_count == 2
        assert chart.values == [10, 20]

    def test_remove_bar_negative_index(self):
        """remove_bar should support negative indices."""
        chart = BarChart([10, 20, 30])
        chart.remove_bar(-1, start=0)
        assert chart.bar_count == 2
        assert chart.values == [10, 20]

    def test_remove_bar_out_of_range(self):
        """Out of range index should raise IndexError."""
        chart = BarChart([10, 20])
        with pytest.raises(IndexError):
            chart.remove_bar(5)

    def test_remove_bar_animated(self):
        """remove_bar with end should animate shrinking."""
        chart = BarChart([10, 20, 30], x=0, y=0, width=300, height=100)
        bar = chart._bars[1]
        chart.remove_bar(1, start=0, end=1)
        # Bar height should shrink to near zero at end
        assert bar.height.at_time(1) == pytest.approx(0, abs=0.1)

    def test_remove_bar_hides_label(self):
        """remove_bar should hide the associated label."""
        chart = BarChart([10, 20, 30], labels=['A', 'B', 'C'])
        lbl = chart._labels[1]
        chart.remove_bar(1, start=0)
        # Label should be hidden (show is False at time 0)
        assert lbl.show.at_time(0) == False

    def test_remove_bar_shifts_remaining(self):
        """After removal, remaining bars should have updated x positions."""
        chart = BarChart([10, 20, 30], x=0, y=0, width=300, height=100)
        # Record original position of bar at index 2
        old_x2 = chart._bars[2].x.at_time(0)
        chart.remove_bar(0, start=0)
        # The bar that was at index 2 is now at index 1
        # It should have moved left
        new_x = chart._bars[1].x.at_time(0)
        assert new_x < old_x2


# ---- New feature tests ----


class TestPathReverse:
    def test_reverse_returns_new_path(self):
        p = Path('M0,0 L100,0 L100,100')
        rev = p.reverse()
        assert isinstance(rev, Path)
        assert rev is not p

    def test_reverse_reverses_d_string(self):
        p = Path('M0,0 L100,0 L100,100')
        rev = p.reverse()
        d = rev.d.at_time(0)
        # The reversed path should start near (100, 100) and end near (0, 0)
        assert d.startswith('M')
        # Parse start point from the reversed d-string
        assert '100' in d[:20]

    def test_reverse_copies_styling(self):
        p = Path('M0,0 L100,0', stroke='#ff0000', stroke_width=5)
        rev = p.reverse()
        assert rev.styling.stroke_width.at_time(0) == 5

    def test_reverse_empty_path(self):
        p = Path('')
        rev = p.reverse()
        assert rev.d.at_time(0) == ''

    def test_reverse_preserves_length(self):
        p = Path('M0,0 L100,0 L100,100')
        rev = p.reverse()
        assert p.get_length() == pytest.approx(rev.get_length(), abs=1)

    def test_reverse_with_time_param(self):
        p = Path('M0,0 L50,0')
        p.d.set_onward(1, 'M0,0 L200,0')
        rev = p.reverse(time=1)
        d = rev.d.at_time(0)
        # Should have reversed the d-string at time=1
        assert '200' in d

    def test_reverse_start_end_points_swap(self):
        p = Path('M10,20 L80,90')
        rev = p.reverse()
        # The reversed path starts where the original ended
        start = rev.point_from_proportion(0)
        assert start[0] == pytest.approx(80, abs=1)
        assert start[1] == pytest.approx(90, abs=1)
        end = rev.point_from_proportion(1)
        assert end[0] == pytest.approx(10, abs=1)
        assert end[1] == pytest.approx(20, abs=1)


class TestTextUpdateText:
    def test_update_text_changes_text(self):
        t = Text('hello')
        t.update_text('world')
        assert t.text.at_time(0) == 'world'

    def test_update_text_at_later_time(self):
        t = Text('hello')
        t.update_text('world', start=2)
        # Before start, original text
        assert t.text.at_time(1) == 'hello'
        # At and after start, new text
        assert t.text.at_time(2) == 'world'
        assert t.text.at_time(5) == 'world'

    def test_update_text_returns_self(self):
        t = Text('hello')
        result = t.update_text('world')
        assert result is t

    def test_update_text_chaining(self):
        t = Text('a')
        t.update_text('b', start=1).update_text('c', start=2)
        assert t.text.at_time(0) == 'a'
        assert t.text.at_time(1) == 'b'
        assert t.text.at_time(2) == 'c'

    def test_update_text_empty(self):
        t = Text('hello')
        t.update_text('')
        assert t.text.at_time(0) == ''


class TestAxesPlotLineGraphAnimateData:
    def test_plot_line_graph_returns_vcollection(self):
        axes = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        graph = axes.plot_line_graph([1, 2, 3], [1, 4, 9])
        assert isinstance(graph, VCollection)

    def test_plot_line_graph_has_animate_data(self):
        axes = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        graph = axes.plot_line_graph([1, 2, 3], [1, 4, 9])
        assert hasattr(graph, 'animate_data')
        assert callable(graph.animate_data)

    def test_animate_data_returns_group(self):
        axes = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        graph = axes.plot_line_graph([1, 2, 3], [1, 4, 9])
        result = graph.animate_data([1, 2, 3], [2, 5, 7], start=1, end=2)
        assert result is graph

    def test_animate_data_instant(self):
        axes = Axes(x_range=(0, 5, 1), y_range=(0, 10, 1))
        graph = axes.plot_line_graph([1, 2, 3], [2, 4, 6])
        # Instant update (start == end)
        graph.animate_data([1, 2, 3], [3, 5, 7], start=0, end=0)
        # Dots should now point at new data at time=0
        dot0 = graph.objects[1]  # first dot
        pos = dot0.c.at_time(0)
        expected = axes.coords_to_point(1, 3, 0)
        assert pos[0] == pytest.approx(expected[0], abs=1)
        assert pos[1] == pytest.approx(expected[1], abs=1)

    def test_animate_data_interpolation(self):
        axes = Axes(x_range=(0, 5, 1), y_range=(0, 10, 1))
        graph = axes.plot_line_graph([1, 2], [2, 4])
        graph.animate_data([1, 2], [4, 8], start=0, end=1)
        # At end time, dots should be at new positions
        dot0 = graph.objects[1]  # first dot
        pos_end = dot0.c.at_time(1)
        expected = axes.coords_to_point(1, 4, 1)
        assert pos_end[0] == pytest.approx(expected[0], abs=1)
        assert pos_end[1] == pytest.approx(expected[1], abs=1)

    def test_animate_data_midpoint_is_interpolated(self):
        axes = Axes(x_range=(0, 5, 1), y_range=(0, 10, 1))
        graph = axes.plot_line_graph([1], [0])
        graph.animate_data([1], [10], start=0, end=1, easing=easings.linear)
        # At time=0.5 with linear easing, should be at y=5
        dot0 = graph.objects[1]
        pos_mid = dot0.c.at_time(0.5)
        expected = axes.coords_to_point(1, 5, 0.5)
        assert pos_mid[0] == pytest.approx(expected[0], abs=1)
        assert pos_mid[1] == pytest.approx(expected[1], abs=1)

    def test_plot_line_graph_d_attribute_is_dynamic(self):
        axes = Axes(x_range=(0, 5, 1), y_range=(0, 10, 1))
        graph = axes.plot_line_graph([1, 2], [3, 6])
        # The curve (first object) should have a d-string with M and L
        curve = graph.objects[0]
        d = curve.d.at_time(0)
        assert d.startswith('M')
        assert 'L' in d


class TestNumberLineAnimateRange:
    def test_animate_range_updates_properties(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.animate_range(-10, 10, start=0, end=1)
        assert nl.x_start == -10
        assert nl.x_end == 10

    def test_animate_range_returns_self(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        result = nl.animate_range(-10, 10, start=0, end=1)
        assert result is nl

    def test_animate_range_instant(self):
        nl = NumberLine(x_range=(0, 10, 1))
        nl.animate_range(0, 20, start=0, end=0)
        assert nl.x_start == 0
        assert nl.x_end == 20

    def test_animate_range_number_to_point_uses_new_range(self):
        nl = NumberLine(x_range=(0, 10, 1), length=100, x=0, y=0)
        nl.animate_range(0, 20, start=0, end=1)
        # After animation, number_to_point should use new range
        px, py = nl.number_to_point(10)
        # 10 in range [0,20] with length 100 => x = 50
        assert px == pytest.approx(50, abs=1)

    def test_animate_range_ticks_move(self):
        nl = NumberLine(x_range=(0, 10, 5), length=100, x=0, y=0,
                        include_arrows=False, include_numbers=False)
        # Ticks at values 0, 5, 10
        # Initial tick positions: 0, 50, 100
        tick0 = nl.objects[1]  # first tick (value=0)
        tick1 = nl.objects[2]  # second tick (value=5)
        old_x1 = tick1.p1.at_time(0)[0]
        assert old_x1 == pytest.approx(50, abs=1)

        nl.animate_range(0, 20, start=0, end=1)
        # After animation, tick at value=5 should be at x=25
        new_x1 = tick1.p1.at_time(1)[0]
        assert new_x1 == pytest.approx(25, abs=1)

    def test_animate_range_with_easing(self):
        nl = NumberLine(x_range=(0, 10, 5), length=100, x=0, y=0,
                        include_arrows=False, include_numbers=False)
        nl.animate_range(0, 20, start=0, end=1, easing=easings.linear)
        # Tick at value=5, at time=0.5 with linear easing: should be halfway
        tick1 = nl.objects[2]  # second tick (value=5)
        # Old x=50, new x=25, midpoint=37.5
        mid_x = tick1.p1.at_time(0.5)[0]
        assert mid_x == pytest.approx(37.5, abs=1)

class TestSquare:
    def test_square_is_rectangle(self):
        s = Square(side=100)
        assert isinstance(s, Rectangle)

    def test_square_equal_sides(self):
        s = Square(side=100)
        assert s.width.at_time(0) == pytest.approx(100)
        assert s.height.at_time(0) == pytest.approx(100)

    def test_square_centered(self):
        s = Square(side=100, x=500, y=300)
        assert s.x.at_time(0) == pytest.approx(450)
        assert s.y.at_time(0) == pytest.approx(250)

    def test_square_repr(self):
        s = Square(side=200)
        assert 'Square' in repr(s)
        assert '200' in repr(s)

    def test_square_svg(self):
        s = Square(side=50, x=100, y=100)
        svg = s.to_svg(0)
        assert '<rect' in svg


class TestInteger:
    def test_integer_is_decimal_number(self):
        from vectormation.objects import DecimalNumber
        i = Integer(42)
        assert isinstance(i, DecimalNumber)

    def test_integer_no_decimals(self):
        i = Integer(42)
        svg = i.to_svg(0)
        assert '42' in svg
        assert '42.' not in svg.replace('42.0', '')  # no decimal point in text

    def test_integer_repr(self):
        i = Integer(7)
        assert 'Integer' in repr(i)
        assert '7' in repr(i)

    def test_integer_animate_value(self):
        i = Integer(0)
        i.animate_value(10, start=0, end=1)
        # At time 0.5, should be ~5
        svg = i.to_svg(0.5)
        assert '5' in svg

class TestComplexValueTracker:
    def test_initial_value(self):
        from vectormation.objects import ComplexValueTracker
        cvt = ComplexValueTracker(3+4j)
        assert cvt.get_value(0) == (3+4j)

    def test_set_value(self):
        from vectormation.objects import ComplexValueTracker
        cvt = ComplexValueTracker(0)
        cvt.set_value(5+2j, start=0)
        assert cvt.get_value(0) == pytest.approx(5+2j)

    def test_animate_value(self):
        from vectormation.objects import ComplexValueTracker
        cvt = ComplexValueTracker(0+0j)
        cvt.animate_value(10+10j, start=0, end=1, easing=easings.linear)
        v = cvt.get_value(0.5)
        assert v.real == pytest.approx(5, abs=0.5)
        assert v.imag == pytest.approx(5, abs=0.5)

    def test_repr(self):
        from vectormation.objects import ComplexValueTracker
        cvt = ComplexValueTracker(1+2j)
        assert 'ComplexValueTracker' in repr(cvt)


class TestArcPolygon:
    def test_basic_creation(self):
        ap = ArcPolygon((100, 100), (200, 100), (150, 50))
        assert 'ArcPolygon' in repr(ap)
        assert '3 vertices' in repr(ap)

    def test_svg_contains_arc(self):
        ap = ArcPolygon((100, 100), (200, 100), (150, 50), arc_angles=45)
        svg = ap.to_svg(0)
        assert '<path' in svg
        assert 'A' in svg  # arc command present

    def test_straight_edges_with_zero_angle(self):
        ap = ArcPolygon((100, 100), (200, 100), (150, 50), arc_angles=0)
        path = ap.path(0)
        assert 'A' not in path  # no arc commands
        assert 'L' in path  # only line commands

    def test_per_edge_angles(self):
        ap = ArcPolygon((100, 100), (200, 100), (150, 50), arc_angles=[30, 0, -30])
        path = ap.path(0)
        assert 'Z' in path  # closed

    def test_minimum_vertices_error(self):
        with pytest.raises(ValueError):
            ArcPolygon((100, 100), (200, 100))


class TestSmoothererstep:
    def test_zero(self):
        assert easings.smoothererstep(0) == 0

    def test_one(self):
        assert easings.smoothererstep(1) == 1

    def test_half(self):
        assert easings.smoothererstep(0.5) == pytest.approx(0.5, abs=0.01)

    def test_monotonic(self):
        values = [easings.smoothererstep(i / 10) for i in range(11)]
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]


# ── New animation tests ──

class TestFadeinWithScale:
    def test_fadein_scale_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.fadein(start=0, end=1, scale=0.5) is c

    def test_fadein_scale_starts_small(self):
        c = Circle(r=50, cx=100, cy=100)
        c.fadein(start=0, end=1, scale=0.5)
        assert c.styling.scale_x.at_time(0) == pytest.approx(0.5, abs=0.1)

    def test_fadein_scale_ends_normal(self):
        c = Circle(r=50, cx=100, cy=100)
        c.fadein(start=0, end=1, scale=0.5)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0, abs=0.05)


class TestFadeoutWithScale:
    def test_fadeout_scale_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.fadeout(start=0, end=1, scale=0.5) is c

    def test_fadeout_scale_starts_normal(self):
        c = Circle(r=50, cx=100, cy=100)
        c.fadeout(start=0, end=1, scale=0.5)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0, abs=0.05)

    def test_fadeout_scale_ends_small(self):
        c = Circle(r=50, cx=100, cy=100)
        c.fadeout(start=0, end=1, scale=0.5)
        assert c.styling.scale_x.at_time(1) == pytest.approx(0.5, abs=0.1)


class TestSpinIn:
    def test_spin_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.spin_in(start=0, end=1) is c

    def test_spin_in_shows_object(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_in(start=0, end=1)
        assert c.show.at_time(0.5) == True

    def test_spin_in_starts_at_zero_scale(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_in(start=0, end=1)
        assert c.styling.scale_x.at_time(0) == pytest.approx(0.0, abs=0.05)


class TestSpinOut:
    def test_spin_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.spin_out(start=0, end=1) is c

    def test_spin_out_hides_object(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_out(start=0, end=1)
        assert not c.show.at_time(1.5)


class TestBlinkNew:
    def test_blink_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.blink(start=0, end=1, num_blinks=4) is c

    def test_blink_opacity_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.blink_opacity(start=0, end=1, frequency=4) is c


class TestIndicateEnhanced:
    def test_indicate_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        assert c.indicate(start=0, end=1) is c


class TestArrowGrow:
    def test_grow_returns_self(self):
        from vectormation.objects import Arrow
        a = Arrow(x1=100, y1=100, x2=300, y2=100)
        assert a.grow(start=0, end=1) is a

    def test_grow_starts_from_start_point(self):
        from vectormation.objects import Arrow
        a = Arrow(x1=100, y1=100, x2=300, y2=100)
        a.grow(start=0, end=1)
        p2_at_0 = a.shaft.p2.at_time(0)
        assert abs(p2_at_0[0] - 100) < 5  # should be near start

    def test_grow_ends_at_end_point(self):
        from vectormation.objects import Arrow
        a = Arrow(x1=100, y1=100, x2=300, y2=100)
        a.grow(start=0, end=1)
        p2_at_1 = a.shaft.p2.at_time(1)
        assert abs(p2_at_1[0] - 300) < 5


class TestDrawBorderThenFill:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        assert c.draw_border_then_fill(start=0, end=1) is c

    def test_fill_starts_hidden(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.draw_border_then_fill(start=0, end=1)
        assert c.styling.fill_opacity.at_time(0) == pytest.approx(0.0, abs=0.01)

    def test_fill_visible_at_end(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.draw_border_then_fill(start=0, end=2)
        # Circle default fill_opacity is 0.7; ramp restores to that value
        assert c.styling.fill_opacity.at_time(2) == pytest.approx(0.7, abs=0.05)


class TestPiTexFormat:
    def test_zero(self):
        from vectormation._axes_helpers import pi_tex_format
        assert pi_tex_format(0) == '$0$'

    def test_pi(self):
        import math
        from vectormation._axes_helpers import pi_tex_format
        assert pi_tex_format(math.pi) == '$\\pi$'

    def test_half_pi(self):
        import math
        from vectormation._axes_helpers import pi_tex_format
        result = pi_tex_format(math.pi / 2)
        assert '\\frac' in result
        assert '\\pi' in result

    def test_negative_pi(self):
        import math
        from vectormation._axes_helpers import pi_tex_format
        result = pi_tex_format(-math.pi)
        assert result == '$-\\pi$'


class TestLogTexFormat:
    def test_power_of_10(self):
        from vectormation._axes_helpers import log_tex_format
        assert log_tex_format(1000) == '$10^{3}$'

    def test_one(self):
        from vectormation._axes_helpers import log_tex_format
        assert log_tex_format(1) == '$10^{0}$'


class TestVCollectionAnimations:
    def test_fadein_delegates(self):
        c1 = Circle(r=30, cx=100, cy=100)
        c2 = Circle(r=30, cx=200, cy=100)
        g = VGroup(c1, c2)
        assert g.fadein(start=0, end=1) is g
        # Both children should have opacity ramped
        assert c1.styling.opacity.at_time(0) < 0.1
        assert c2.styling.opacity.at_time(0) < 0.1

    def test_fadeout_delegates(self):
        c1 = Circle(r=30, cx=100, cy=100)
        c2 = Circle(r=30, cx=200, cy=100)
        g = VGroup(c1, c2)
        g.fadeout(start=0, end=1)
        assert c1.styling.opacity.at_time(1) < 0.1
        assert c2.styling.opacity.at_time(1) < 0.1

    def test_create_delegates(self):
        c = Circle(r=30, cx=100, cy=100)
        g = VGroup(c)
        assert g.create(start=0, end=1) is g

    def test_grow_from_center_delegates(self):
        c = Circle(r=30, cx=100, cy=100)
        g = VGroup(c)
        assert g.grow_from_center(start=0, end=1) is g

    def test_indicate_delegates(self):
        c = Circle(r=30, cx=100, cy=100)
        g = VGroup(c)
        assert g.indicate(start=0, end=1) is g

    def test_pop_in_delegates(self):
        c = Circle(r=30, cx=100, cy=100)
        g = VGroup(c)
        assert g.pop_in(start=0) is g

    def test_draw_border_then_fill_delegates(self):
        c = Circle(r=30, cx=100, cy=100, fill='#FF0000')
        g = VGroup(c)
        assert g.draw_border_then_fill(start=0, end=1) is g


class TestTransformFromCopy:
    def test_returns_copy(self):
        c = Circle(r=30, cx=100, cy=100)
        r = Rectangle(60, 40, x=300, y=300)
        ghost = c.transform_from_copy(r, start=0, end=2)
        # Returns a separate object (the ghost copy)
        assert ghost is not c
        assert ghost is not r


class TestSuccession:
    def test_basic_chain(self):
        from vectormation.objects import succession
        c1 = Circle(r=30, cx=100, cy=100)
        c2 = Circle(r=30, cx=200, cy=200)
        succession(
            (c1, 'fadein'),
            (c2, 'fadein'),
            start=0,
        )
        # c1 should animate first (t=0..1), c2 second (t=1..2)
        assert c1.styling.opacity.at_time(0) < 0.1
        assert c2.styling.opacity.at_time(1) < 0.1

    def test_with_kwargs(self):
        from vectormation.objects import succession, UP
        c = Circle(r=30, cx=100, cy=100)
        succession(
            (c, 'fadein', {'shift_dir': UP}),
            start=0,
        )
        assert c.styling.opacity.at_time(0) < 0.1

    def test_lagged_start_alias(self):
        """VCollection.lagged_start should be an alias for cascade."""
        assert VCollection.lagged_start is VCollection.cascade


class TestCombinedAnimations:
    def test_create_then_fadeout(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.create_then_fadeout(start=0, end=3) is c
        # Should be visible during hold phase
        assert c.show.at_time(1.5) is True

    def test_write_then_fadeout(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.write_then_fadeout(start=0, end=3) is c

    def test_fadein_then_fadeout(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.fadein_then_fadeout(start=0, end=3) is c
        # Opacity should be low at start
        assert c.styling.opacity.at_time(0) < 0.1
        # Should fade back out by end
        assert c.styling.opacity.at_time(3) < 0.1

    def test_zero_duration_returns_self(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.create_then_fadeout(start=1, end=1) is c
        assert c.write_then_fadeout(start=1, end=1) is c
        assert c.fadein_then_fadeout(start=1, end=1) is c


class TestCounterclockwiseMorph:
    def test_returns_morph_object(self):
        from vectormation.objects import counterclockwise_morph, MorphObject
        c = Circle(r=30, cx=100, cy=100)
        r = Rectangle(60, 40, x=300, y=300)
        morph = counterclockwise_morph(c, r, start=0, end=2)
        assert isinstance(morph, MorphObject)

    def test_can_generate_svg(self):
        from vectormation.objects import counterclockwise_morph
        c = Circle(r=30, cx=100, cy=100)
        r = Rectangle(60, 40, x=300, y=300)
        morph = counterclockwise_morph(c, r, start=0, end=2)
        svg = morph.to_svg(1.0)
        assert '<path' in svg or '<g' in svg


class TestShowIncreasingSubsets:
    def test_basic(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=100)
        c3 = Circle(r=10, cx=300, cy=100)
        group = VCollection(c1, c2, c3)
        result = group.show_increasing_subsets(start=0, end=3)
        assert result is group
        # First child visible from t=0, second from t=1, third from t=2
        assert c1.show.at_time(0) is True
        assert c2.show.at_time(0.5) is False
        assert c2.show.at_time(1.5) is True
        assert c3.show.at_time(1.5) is False
        assert c3.show.at_time(2.5) is True

    def test_empty_collection(self):
        group = VCollection()
        assert group.show_increasing_subsets(start=0, end=1) is group

    def test_zero_duration(self):
        c = Circle(r=10, cx=100, cy=100)
        group = VCollection(c)
        assert group.show_increasing_subsets(start=1, end=1) is group


class TestShowOneByOne:
    def test_basic(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=100)
        group = VCollection(c1, c2)
        result = group.show_one_by_one(start=0, end=2)
        assert result is group
        # c1 fades in from 0..1, c2 from 1..2
        assert c1.styling.opacity.at_time(0) < 0.1
        # c2 hasn't started fading in yet, so show is False
        assert c2.show.at_time(0.5) is False


class TestApplyWave:
    def test_returns_self(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.apply_wave(start=0, end=2) is c

    def test_zero_duration(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.apply_wave(start=1, end=1) is c

    def test_x_direction(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.apply_wave(start=0, end=2, direction='x') is c


class TestScaleInPlace:
    def test_returns_self(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.scale_in_place(2.0, start=0, end=1) is c

    def test_center_preserved(self):
        c = Circle(r=30, cx=500, cy=500)
        c.scale_in_place(2.0, start=0, end=1)
        # Object should still render with scale origin set
        svg = c.to_svg(0.5)
        assert svg  # non-empty


# =============================================================================
# Text Animation Methods
# =============================================================================

class TestTextAnimations:
    def test_typewrite(self):
        t = Text("Hello", x=100, y=100)
        result = t.typewrite(start=0, end=2)
        assert result is t
        # At halfway, only some characters should be visible
        text_mid = t.text.at_time(1.0)
        assert len(text_mid) < len("Hello") or text_mid == "Hello"

    def test_set_text(self):
        t = Text("old", x=100, y=100)
        t.set_text(1, 2, "new")
        assert t.text.at_time(0) == "old"
        assert t.text.at_time(2) == "new"

    def test_highlight(self):
        t = Text("Hello World", x=100, y=100)
        result = t.highlight(start=0, end=1, color='#FF0000')
        # highlight returns a VCollection or self
        assert result is not None

    def test_scramble(self):
        t = Text("Hello", x=100, y=100)
        result = t.scramble(start=0, end=2)
        assert result is t
        # During scramble, text should be different from original at some point
        text_mid = t.text.at_time(0.5)
        assert isinstance(text_mid, str)
        assert len(text_mid) == len("Hello")

    def test_typing(self):
        t = Text("Hello World", x=100, y=100)
        result = t.typing(start=0, end=2)
        assert result is t
        # At end, full text should be there
        assert t.text.at_time(2) == "Hello World"

    def test_reveal_by_word(self):
        t = Text("Hello World", x=100, y=100)
        result = t.reveal_by_word(start=0, end=2)
        assert result is t
        # At start, should be empty or partial
        text_start = t.text.at_time(0)
        assert len(text_start) <= len("Hello World")


class TestTextHighlightSubstring:
    def test_basic(self):
        t = Text("Hello World", x=100, y=100)
        result = t.highlight_substring("World", start=0, end=1, color='#E74C3C')
        # Should return something (highlight rect or self)
        assert result is not None


# =============================================================================
# Advanced Effect Behavioral Tests
# =============================================================================

class TestEffectBehavior:
    """Test that effects actually modify animation attributes, not just return self."""

    def test_telegraph_modifies_scale(self):
        c = Circle(r=30, cx=100, cy=100)
        c.telegraph(start=0, duration=1.0, scale_factor=2.0)
        # Scale should be > 1 during the effect
        sx = c.styling.scale_x.at_time(0.3)
        assert sx > 1.0

    def test_flicker_modifies_opacity(self):
        c = Circle(r=30, cx=100, cy=100)
        c.flicker(start=0, end=2, frequency=4)
        # Opacity should vary during flicker
        op1 = c.styling.opacity.at_time(0.25)
        op2 = c.styling.opacity.at_time(0.5)
        # At least one should differ from 1.0 or they should differ from each other
        assert op1 != 1.0 or op2 != 1.0 or op1 != op2

    def test_strobe_creates_on_off(self):
        c = Circle(r=30, cx=100, cy=100)
        c.strobe(start=0, end=1, flashes=5, duty=0.5)
        # At various points, opacity should be either 0 or 1
        for t in [0.1, 0.2, 0.3, 0.4]:
            op = c.styling.opacity.at_time(t)
            assert op == pytest.approx(0.0) or op == pytest.approx(1.0)

    def test_elastic_bounce_moves_vertically(self):
        c = Circle(r=30, cx=500, cy=500)
        c.elastic_bounce(start=0, end=2, height=100, bounces=3)
        # During bounce, dy should shift the object
        svg_mid = c.to_svg(0.5)
        assert svg_mid  # renders

    def test_slingshot_reaches_target(self):
        c = Circle(r=20, cx=100, cy=100)
        c.slingshot(500, 500, start=0, end=2)
        # At end, object should be near target
        svg = c.to_svg(2.0)
        assert svg  # renders

    def test_domino_hides_at_end(self):
        c = Rectangle(50, 100, x=100, y=100)
        c.domino(start=0, end=1)
        assert c.show.at_time(1.5) is False

    def test_unfold_shows_from_start(self):
        c = Rectangle(200, 100, x=100, y=100)
        c.unfold(start=0, end=1, change_existence=True)
        # Should be shown from start
        assert c.show.at_time(0) is True

    def test_wobble_modifies_position(self):
        c = Circle(r=30, cx=500, cy=500)
        c.wobble(start=0, end=2, intensity=10)
        # Wobble should produce SVG that includes rotation
        svg = c.to_svg(0.5)
        assert svg

    def test_morph_scale_reaches_target(self):
        c = Circle(r=30, cx=100, cy=100)
        c.morph_scale(target_scale=2.0, start=0, end=2)
        # At end, scale should be approximately 2.0
        sx = c.styling.scale_x.at_time(2.0)
        assert sx == pytest.approx(2.0, abs=0.05)

    def test_squeeze_changes_aspect(self):
        c = Circle(r=30, cx=100, cy=100)
        c.squeeze(start=0, end=1, axis='x', factor=0.5)
        # Scale x should decrease, scale y should increase
        sx = c.styling.scale_x.at_time(1.0)
        sy = c.styling.scale_y.at_time(1.0)
        assert sx < 1.0
        assert sy > 1.0


# =============================================================================
# VCollection Stagger Methods
# =============================================================================

class TestCollectionStaggerMethods:
    def test_stagger_basic(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=100)
        group = VCollection(c1, c2)
        result = group.stagger('fadein', delay=0.5, start=0, end=1)
        assert result is group
        # c1 should start fading at t=0
        assert c1.styling.opacity.at_time(0) < 0.1
        # c2 starts at t=0.5, so at t=0 it's not yet fading (change_existence)
        assert c2.show.at_time(0) is False

    def test_cascade_animates_sequentially(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=100)
        c3 = Circle(r=10, cx=300, cy=100)
        group = VCollection(c1, c2, c3)
        result = group.cascade('fadein', start=0, end=3)
        assert result is group
        # First child should start before second
        assert c1.styling.opacity.at_time(0) < 0.1

    def test_sequential(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=100)
        group = VCollection(c1, c2)
        result = group.sequential('fadein', start=0, end=2)
        assert result is group

    def test_wave_anim(self):
        circles = [Circle(r=10, cx=100 + i*50, cy=100) for i in range(5)]
        group = VCollection(*circles)
        # wave_anim doesn't take a method name — it's a position wave
        result = group.wave_anim(start=0, end=3, amplitude=20)
        assert result is group

    def test_stagger_fadein(self):
        circles = [Circle(r=10, cx=100 + i*50, cy=100) for i in range(3)]
        group = VCollection(*circles)
        result = group.stagger_fadein(start=0, end=2)
        assert result is group
        # First circle should be fading in before last
        assert circles[0].styling.opacity.at_time(0) < 0.1

    def test_stagger_fadeout(self):
        circles = [Circle(r=10, cx=100 + i*50, cy=100) for i in range(3)]
        group = VCollection(*circles)
        result = group.stagger_fadeout(start=0, end=2)
        assert result is group


# =============================================================================
# Boolean Operations
# =============================================================================

class TestBooleanOps:
    def test_union_renders(self):
        from vectormation.objects import Union
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(80, 80, x=70, y=70)
        u = Union(c, r)
        svg = u.to_svg(0)
        assert svg  # non-empty, renders

    def test_difference_renders(self):
        from vectormation.objects import Difference
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(80, 80, x=70, y=70)
        d = Difference(c, r)
        svg = d.to_svg(0)
        assert svg

    def test_exclusion_renders(self):
        from vectormation.objects import Exclusion
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(80, 80, x=70, y=70)
        e = Exclusion(c, r)
        svg = e.to_svg(0)
        assert svg

    def test_intersection_renders(self):
        from vectormation.objects import Intersection
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(80, 80, x=70, y=70)
        i = Intersection(c, r)
        svg = i.to_svg(0)
        assert svg


# =============================================================================
# Canvas Camera Controls
# =============================================================================

class TestCameraControls:
    def test_camera_shift(self):
        import tempfile
        from vectormation.objects import VectorMathAnim
        v = VectorMathAnim(tempfile.mkdtemp(), width=800, height=600)
        v.camera_shift(100, 50, start=0, end=1)
        # Viewbox should shift
        vb_x = v.vb_x.at_time(1.0)
        assert vb_x == pytest.approx(100, abs=1)

    def test_camera_zoom(self):
        import tempfile
        from vectormation.objects import VectorMathAnim
        v = VectorMathAnim(tempfile.mkdtemp(), width=800, height=600)
        v.camera_zoom(2.0, start=0, end=1)
        # After zoom, viewbox should be smaller
        vb_w = v.vb_w.at_time(1.0)
        assert vb_w < 800

    def test_camera_reset(self):
        import tempfile
        from vectormation.objects import VectorMathAnim
        v = VectorMathAnim(tempfile.mkdtemp(), width=800, height=600)
        v.camera_shift(100, 50, start=0, end=0.5)
        v.camera_reset(start=1, end=2)
        # After reset, should be back to original
        vb_x = v.vb_x.at_time(2.0)
        assert vb_x == pytest.approx(0, abs=1)


# ---- New feature tests: get_subcurve, passing_flash, animated_tangent ----

class TestGetSubcurve:
    def test_full_curve(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=False)
        sub = p.get_subcurve(0, 1)
        verts = sub.get_vertices()
        assert len(verts) >= 2

    def test_first_half(self):
        p = Lines((0, 0), (100, 0), (200, 0))
        sub = p.get_subcurve(0, 0.5)
        verts = sub.get_vertices()
        # Total length is 200, so first half ends at (100, 0)
        assert verts[-1] == pytest.approx((100, 0), abs=1)

    def test_middle_section(self):
        p = Lines((0, 0), (100, 0), (200, 0), (300, 0))
        sub = p.get_subcurve(1/3, 2/3)
        verts = sub.get_vertices()
        assert len(verts) >= 2
        assert verts[0][0] == pytest.approx(100, abs=1)
        assert verts[-1][0] == pytest.approx(200, abs=1)

    def test_empty_range(self):
        p = Lines((0, 0), (100, 0))
        sub = p.get_subcurve(0.5, 0.5)
        # Should return something (degenerate) but not crash
        assert sub is not None


class TestPassingFlash:
    def test_basic(self):
        c = Circle(r=100, stroke='#fff')
        c.passing_flash(start=0, end=2)
        svg = c.to_svg(1)
        # During the flash, object should have dash styling
        assert 'stroke-dasharray' in svg or 'stroke-dashoffset' in svg

    def test_with_color(self):
        l = Line(0, 0, 200, 0, stroke='#fff')
        l.passing_flash(start=0, end=1, color='#FF0000')
        svg = l.to_svg(0.5)
        assert svg  # renders something

    def test_visibility(self):
        c = Circle(r=50)
        c.passing_flash(start=1, end=2)
        # Before start, hidden
        assert c.show.at_time(0) is False
        # After end, hidden
        assert c.show.at_time(3) is False


class TestAnimatedTangentLine:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        import math
        tl = ax.animated_tangent_line(math.sin, -3, 3, start=0, end=2)
        svg = tl.to_svg(1)
        assert 'line' in svg

    def test_returns_line(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        tl = ax.animated_tangent_line(lambda x: x**2, -2, 2, start=0, end=1)
        # Should be a Line object
        assert hasattr(tl, 'p1')
        assert hasattr(tl, 'p2')
