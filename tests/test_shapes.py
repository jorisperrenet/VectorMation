"""Tests for shape classes in vectormation.objects."""
import pytest
from vectormation.objects import (
    Circle, Rectangle, Polygon, Line, Lines, RegularPolygon, Arc, Ellipse,
    Path, Trace, Text, Dot, Wedge, Sector, Star, RoundedRectangle, DashedLine,
    NumberLine, EquilateralTriangle, Arrow, CurvedArrow, VObject, VCollection,
    from_svg, CountAnimation, Annulus, DoubleArrow, FunctionGraph,
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
        bx, by, bw, bh = t.bbox(0)
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
        assert isinstance(obj, Path)

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
        x, y, w, h = a.bbox(0)
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
