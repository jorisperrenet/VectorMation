"""Tests for shape classes in vectormation.objects."""
import pytest
from vectormation.objects import (
    Circle, Rectangle, Polygon, Line, Lines, RegularPolygon, Arc, Ellipse,
    Path, Trace, Text, Dot, Wedge, Sector, Star, RoundedRectangle, DashedLine,
    NumberLine, EquilateralTriangle, Arrow, CurvedArrow, VObject, VCollection,
    from_svg, CountAnimation, Annulus, DoubleArrow, FunctionGraph,
    AnnularSector, PieChart, DonutChart, Axes,
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
        c.shift(dx=10, dy=20, start_time=0)
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
        r.shift(dx=5, dy=10, start_time=0)
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
        p.shift(dx=10, dy=20, start_time=0)
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
        l.shift(dx=10, dy=20, start_time=0)
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
        c2.shift(dx=50, start_time=0)
        # Original should be unchanged
        assert c.c.at_time(0)[0] == pytest.approx(100)
        assert c2.c.at_time(0)[0] == pytest.approx(150)

    def test_rect_copy(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        r2 = r.copy()
        r2.shift(dx=100, start_time=0)
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
        coll.arrange(direction='right', buff=10, start_time=0)
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
        from vectormation.objects import _parse_inline_style
        result = _parse_inline_style('fill:#ff0; stroke-width:2; opacity:0.5')
        assert result == {'fill': '#ff0', 'stroke-width': '2', 'opacity': '0.5'}

    def test_parse_inline_style_empty(self):
        from vectormation.objects import _parse_inline_style
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


class TestCountAnimation:
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


class TestDrawAlong:
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


class TestArcBbox:
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
        group.arrange(direction='right', buff=10, start_time=0)
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
        c.shift(dx=50, dy=-30, start_time=0)
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
        p2 = line.p2.at_time(0)
        assert abs(p2[0] - 200) < 0.01
        assert abs(p2[1]) < 0.01

    def test_line_set_length_animated(self):
        line = Line(0, 0, 100, 0)
        line.set_length(200, start=0, end=1)
        p2_mid = line.p2.at_time(0.5)
        assert 100 < p2_mid[0] < 200

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
        assert abs(an.get_area() - expected) < 0.01

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
        assert abs(mx - 0) < 0.01
        assert abs(my - (-100)) < 0.01  # y is inverted in SVG

    def test_wedge_get_area(self):
        import math
        w = Wedge(r=100, start_angle=0, end_angle=90)
        expected = 0.5 * 100**2 * math.radians(90)
        assert abs(w.get_area() - expected) < 0.01

    def test_cubicbezier_point_at(self):
        from vectormation.objects import CubicBezier
        b = CubicBezier(p0=(0, 0), p1=(100, 0), p2=(100, 100), p3=(200, 100))
        start = b.point_at(0)
        end = b.point_at(1)
        assert abs(start[0] - 0) < 0.01 and abs(start[1] - 0) < 0.01
        assert abs(end[0] - 200) < 0.01 and abs(end[1] - 100) < 0.01
        mid = b.point_at(0.5)
        assert 50 < mid[0] < 150  # somewhere in the middle

    def test_cubicbezier_tangent_at(self):
        import math
        from vectormation.objects import CubicBezier
        b = CubicBezier(p0=(0, 0), p1=(100, 0), p2=(100, 0), p3=(200, 0))
        dx, dy = b.tangent_at(0.5)
        # Horizontal line, tangent should point right
        assert abs(dx - 1.0) < 0.1
        assert abs(dy) < 0.1
        # Unit vector
        assert abs(math.hypot(dx, dy) - 1.0) < 0.01

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
        assert abs(e.get_perimeter() - expected) < 0.1

    def test_ellipse_get_perimeter_ellipse(self):
        e = Ellipse(rx=100, ry=50)
        p = e.get_perimeter()
        # Perimeter should be between 2*pi*50 and 2*pi*100
        import math
        assert 2 * math.pi * 50 < p < 2 * math.pi * 100

    def test_line_angle_horizontal(self):
        line = Line(0, 0, 100, 0)
        assert abs(line.angle() - 0) < 0.01

    def test_line_angle_up(self):
        line = Line(0, 100, 0, 0)  # points up in SVG (y decreases)
        assert abs(line.angle() - 90) < 0.01

    def test_line_angle_down(self):
        line = Line(0, 0, 0, 100)  # points down in SVG
        assert abs(line.angle() - (-90)) < 0.01


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

    def test_donutchart_highlight_sector_out_of_range_no_error(self):
        dc = DonutChart([1, 2, 3])
        # Out-of-range index returns self without raising
        result = dc.highlight_sector(10, start=0, end=1)
        assert result is dc

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
