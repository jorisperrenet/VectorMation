"""Comprehensive tests targeting untested areas and potential bugs."""
import math
import pytest
import tempfile

from vectormation._shapes import (
    Polygon, Circle, Ellipse, Rectangle, Dot, Lines, RoundedRectangle,
    Line, Text, Path, Arc, RegularPolygon, Star, Wedge,
)
from vectormation._base import VObject
from vectormation._collection import VCollection
from vectormation._composites import (
    Table, NumberLine, DynamicObject, Matrix, _det,
)
from vectormation._canvas import VectorMathAnim
from vectormation._constants import ORIGIN, UP, DOWN, LEFT, RIGHT, UNIT
from vectormation._base_helpers import _ramp, _ramp_down, _norm_dir, _norm_edge
import vectormation.easings as easings
import vectormation.attributes as attributes


def _make_canvas():
    return VectorMathAnim(tempfile.mkdtemp())


# ===========================================================================
# BUG: Ellipse.get_point_at_parameter uses wrong y-sign (+ instead of -)
# ===========================================================================

class TestEllipseGetPointAtParameter:

    def test_point_at_parameter_matches_point_at_angle(self):
        """get_point_at_parameter(0.25) should match point_at_angle(90)."""
        e = Ellipse(rx=100, ry=50, cx=200, cy=300)
        pp = e.get_point_at_parameter(0.25, time=0)
        pa = e.point_at_angle(90, time=0)
        assert pp[0] == pytest.approx(pa[0], abs=1e-6)
        assert pp[1] == pytest.approx(pa[1], abs=1e-6)

    def test_point_at_parameter_zero_matches_angle_zero(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=300)
        pp = e.get_point_at_parameter(0, time=0)
        pa = e.point_at_angle(0, time=0)
        assert pp[0] == pytest.approx(pa[0], abs=1e-6)
        assert pp[1] == pytest.approx(pa[1], abs=1e-6)

    def test_point_at_parameter_half_matches_angle_180(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=300)
        pp = e.get_point_at_parameter(0.5, time=0)
        pa = e.point_at_angle(180, time=0)
        assert pp[0] == pytest.approx(pa[0], abs=1e-6)
        assert pp[1] == pytest.approx(pa[1], abs=1e-6)

    def test_point_at_parameter_three_quarters_matches_270(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=300)
        pp = e.get_point_at_parameter(0.75, time=0)
        pa = e.point_at_angle(270, time=0)
        assert pp[0] == pytest.approx(pa[0], abs=1e-6)
        assert pp[1] == pytest.approx(pa[1], abs=1e-6)


# ===========================================================================
# BUG: Polygon.offset direction depends on winding order
# ===========================================================================

class TestPolygonOffset:

    def test_offset_positive_expands_cw(self):
        """Positive offset on CW polygon should expand outward."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.is_clockwise() is True
        expanded = sq.offset(10)
        assert expanded.area(0) > sq.area(0)

    def test_offset_negative_contracts_cw(self):
        """Negative offset on CW polygon should shrink inward."""
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        contracted = sq.offset(-10)
        assert contracted.area(0) < sq.area(0)

    def test_offset_zero_unchanged(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        same = sq.offset(0)
        verts_orig = sq.get_vertices(0)
        verts_new = same.get_vertices(0)
        for (x1, y1), (x2, y2) in zip(verts_orig, verts_new):
            assert x1 == pytest.approx(x2, abs=1e-6)
            assert y1 == pytest.approx(y2, abs=1e-6)


# ===========================================================================
# Polygon.triangulate signed area formula inconsistency
# ===========================================================================

class TestTriangulateSignedArea:

    def test_triangulate_simple_triangle(self):
        tri = Polygon((0, 0), (100, 0), (50, 80))
        triangles = tri.triangulate()
        assert len(triangles) == 1

    def test_triangulate_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        triangles = sq.triangulate()
        assert len(triangles) == 2
        total = sum(t.area(0) for t in triangles)
        assert total == pytest.approx(sq.area(0), rel=1e-6)

    def test_triangulate_ccw_polygon(self):
        ccw = Polygon((0, 0), (0, 100), (100, 100), (100, 0))
        triangles = ccw.triangulate()
        assert len(triangles) == 2
        total = sum(t.area(0) for t in triangles)
        assert total == pytest.approx(ccw.area(0), rel=1e-6)

    def test_triangulate_concave_l_shape(self):
        L = Polygon((0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100))
        triangles = L.triangulate()
        assert len(triangles) == 4
        total = sum(t.area(0) for t in triangles)
        assert total == pytest.approx(L.area(0), rel=1e-6)

    def test_triangulate_requires_closed(self):
        with pytest.raises(ValueError, match="closed"):
            Polygon((0, 0), (100, 0), (50, 80), closed=False).triangulate()

    def test_triangulate_requires_3_vertices(self):
        with pytest.raises(ValueError, match="at least 3"):
            Polygon((0, 0), (100, 0)).triangulate()


# ===========================================================================
# Polygon.contains_point
# ===========================================================================

class TestPolygonContainsPoint:

    def test_center_inside(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.contains_point(50, 50) is True

    def test_outside(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.contains_point(150, 50) is False

    def test_near_horizontal_edge(self):
        """Test stability with nearly-horizontal edges."""
        poly = Polygon((0, 0), (100, 1e-12), (100, 100), (0, 100))
        assert poly.contains_point(50, 50) is True

    def test_on_vertex_no_crash(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.contains_point(0, 0)
        assert isinstance(result, bool)


# ===========================================================================
# Polygon geometry methods
# ===========================================================================

class TestPolygonGeometry:

    def test_diagonals_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert len(sq.get_diagonals()) == 2

    def test_diagonals_pentagon(self):
        pts = [(math.cos(2*math.pi*i/5)*100, math.sin(2*math.pi*i/5)*100) for i in range(5)]
        assert len(Polygon(*pts).get_diagonals()) == 5

    def test_diagonals_triangle_empty(self):
        assert Polygon((0, 0), (100, 0), (50, 80)).get_diagonals() == []

    def test_diagonals_open_empty(self):
        assert Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=False).get_diagonals() == []

    def test_edge_midpoints_square(self):
        mids = Polygon((0, 0), (100, 0), (100, 100), (0, 100)).get_edge_midpoints()
        assert len(mids) == 4
        assert mids[0] == pytest.approx((50, 0))
        assert mids[1] == pytest.approx((100, 50))

    def test_edge_midpoints_open(self):
        assert len(Polygon((0, 0), (100, 0), (100, 100), closed=False).get_edge_midpoints()) == 2

    def test_edges_closed(self):
        assert len(Polygon((0, 0), (100, 0), (100, 100), (0, 100)).get_edges()) == 4

    def test_edges_open(self):
        assert len(Polygon((0, 0), (100, 0), (100, 100), closed=False).get_edges()) == 2

    def test_bounding_circle_contains_all_vertices(self):
        pts_list = [(0, 0), (100, 0), (100, 100), (0, 100)]
        sq = Polygon(*pts_list)
        bc = sq.bounding_circle()
        cx, cy = bc.c.at_time(0)
        r = bc.r.at_time(0)
        for px, py in pts_list:
            assert math.hypot(px - cx, py - cy) <= r + 1e-6

    def test_is_convex_square(self):
        assert Polygon((0, 0), (100, 0), (100, 100), (0, 100)).is_convex() is True

    def test_is_not_convex_l_shape(self):
        L = Polygon((0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100))
        assert L.is_convex() is False

    def test_interior_angles_square(self):
        angles = Polygon((0, 0), (100, 0), (100, 100), (0, 100)).interior_angles()
        assert len(angles) == 4
        for a in angles:
            assert a == pytest.approx(90, abs=1)

    def test_interior_angles_equilateral_triangle(self):
        h = 100 * math.sqrt(3) / 2
        for a in Polygon((0, 0), (100, 0), (50, h)).interior_angles():
            assert a == pytest.approx(60, abs=1)

    def test_is_clockwise(self):
        assert Polygon((0, 0), (100, 0), (100, 100), (0, 100)).is_clockwise() is True
        assert Polygon((0, 0), (0, 100), (100, 100), (100, 0)).is_clockwise() is False

    def test_translate(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sq.translate(50, 25)
        v = sq.get_vertices(0)
        assert v[0] == pytest.approx((50, 25))
        assert v[2] == pytest.approx((150, 125))

    def test_scale_vertices(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sq.scale_vertices(2)
        assert sq.area(0) == pytest.approx(4 * 10000, rel=0.01)

    def test_mirror_x(self):
        tri = Polygon((10, 0), (110, 0), (60, 50))
        tri.mirror_x(60)
        v = tri.get_vertices(0)
        assert v[0][0] == pytest.approx(110)
        assert v[1][0] == pytest.approx(10)

    def test_mirror_y(self):
        tri = Polygon((0, 10), (100, 10), (50, 60))
        tri.mirror_y(35)
        v = tri.get_vertices(0)
        assert v[0][1] == pytest.approx(60)
        assert v[2][1] == pytest.approx(10)

    def test_apply_pointwise(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sq.apply_pointwise(lambda x, y: (x + 10, y + 20))
        v = sq.get_vertices(0)
        assert v[0] == pytest.approx((10, 20))
        assert v[2] == pytest.approx((110, 120))

    def test_is_regular_hexagon(self):
        pts = [(math.cos(2*math.pi*i/6)*100, math.sin(2*math.pi*i/6)*100) for i in range(6)]
        assert Polygon(*pts).is_regular() is True

    def test_is_not_regular_rectangle(self):
        assert Polygon((0, 0), (200, 0), (200, 100), (0, 100)).is_regular() is False


# ===========================================================================
# Smooth corners
# ===========================================================================

class TestSmoothCorners:

    def test_returns_path(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100)).smooth_corners(radius=10)
        assert isinstance(p, Path)

    def test_contains_bezier(self):
        d = Polygon((0, 0), (100, 0), (100, 100), (0, 100)).smooth_corners(radius=10).d.at_time(0)
        assert 'Q' in d

    def test_closed_has_Z(self):
        d = Polygon((0, 0), (100, 0), (100, 100), (0, 100)).smooth_corners(radius=10).d.at_time(0)
        assert 'Z' in d

    def test_open_no_Z(self):
        d = Polygon((0, 0), (100, 0), (100, 100), closed=False).smooth_corners(radius=10).d.at_time(0)
        assert 'Z' not in d


# ===========================================================================
# Ellipse / Circle contains_point edge cases
# ===========================================================================

class TestEllipseContainsPoint:

    def test_center_inside(self):
        assert Ellipse(rx=100, ry=50, cx=200, cy=300).contains_point(200, 300) is True

    def test_on_boundary(self):
        assert Ellipse(rx=100, ry=50, cx=200, cy=300).contains_point(300, 300) is True

    def test_outside(self):
        assert Ellipse(rx=100, ry=50, cx=200, cy=300).contains_point(400, 300) is False

    def test_zero_rx(self):
        assert Ellipse(rx=0, ry=50, cx=200, cy=300).contains_point(200, 300) is False

    def test_circle_and_ellipse_zero_radius_consistent(self):
        """Both Circle r=0 and Ellipse rx=ry=0 should return False."""
        c = Circle(r=0, cx=100, cy=100)
        e = Ellipse(rx=0, ry=0, cx=100, cy=100)
        assert c.contains_point(100, 100) is False
        assert e.contains_point(100, 100) is False


# ===========================================================================
# Rectangle extra
# ===========================================================================

class TestRectangleExtended:

    def test_contains_point(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.contains_point(60, 45) is True
        assert r.contains_point(0, 0) is False

    def test_round_corners(self):
        assert isinstance(Rectangle(100, 50, x=10, y=20).round_corners(radius=5), RoundedRectangle)

    def test_grow_width(self):
        r = Rectangle(100, 50, x=10, y=20)
        r.grow_width(20, start=0, end=1)
        assert r.width.at_time(1) == pytest.approx(120)

    def test_grow_height(self):
        r = Rectangle(100, 50, x=10, y=20)
        r.grow_height(30, start=0, end=1)
        assert r.height.at_time(1) == pytest.approx(80)


# ===========================================================================
# VCollection arrange
# ===========================================================================

class TestCollectionArrange:

    def test_arrange_right_no_overlap(self):
        items = [Circle(r=50, cx=0, cy=0) for _ in range(3)]
        coll = VCollection(*items)
        coll.arrange('right', buff=10, start=0)
        bboxes = [obj.bbox(0) for obj in coll.objects]
        for i in range(len(bboxes) - 1):
            right = bboxes[i][0] + bboxes[i][2]
            left = bboxes[i+1][0]
            assert right <= left + 1

    def test_arrange_down(self):
        items = [Rectangle(50, 30) for _ in range(2)]
        coll = VCollection(*items)
        coll.arrange('down', buff=10, start=0)
        bboxes = [o.bbox(0) for o in coll.objects]
        assert bboxes[0][1] + bboxes[0][3] <= bboxes[1][1] + 1

    def test_arrange_left(self):
        items = [Rectangle(50, 30, x=0, y=0) for _ in range(2)]
        coll = VCollection(*items)
        coll.arrange('left', buff=10, start=0)
        bboxes = [o.bbox(0) for o in coll.objects]
        # In left arrangement, first object is to the right
        assert bboxes[1][0] + bboxes[1][2] <= bboxes[0][0] + 1

    def test_arrange_empty(self):
        VCollection().arrange('right', buff=10)

    def test_arrange_single(self):
        c = Circle(r=50)
        coll = VCollection(c)
        old = coll.center(0)
        coll.arrange('right', buff=10)
        new = coll.center(0)
        assert new[0] == pytest.approx(old[0], abs=5)

    def test_arrange_in_grid(self):
        items = [Rectangle(40, 30) for _ in range(6)]
        coll = VCollection(*items)
        coll.arrange_in_grid(rows=2, cols=3, buff=5, start=0)
        bboxes = [o.bbox(0) for o in coll.objects]
        # Top row y values should be similar
        assert bboxes[0][1] == pytest.approx(bboxes[1][1], abs=5)
        # Top row above bottom row
        assert bboxes[0][1] < bboxes[3][1]


# ===========================================================================
# Table tests
# ===========================================================================

class TestTable:

    def test_basic(self):
        t = Table([['A', 'B'], ['C', 'D']])
        assert t.rows == 2 and t.cols == 2

    def test_entries_accessible(self):
        t = Table([['X', 'Y'], ['Z', 'W']])
        assert len(t.entries) == 2 and len(t.entries[0]) == 2

    def test_with_labels(self):
        t = Table([['1', '2'], ['3', '4']],
                  col_labels=['A', 'B'], row_labels=['R1', 'R2'])
        assert len(t.to_svg(0)) > 0

    def test_empty_data_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            Table([])

    def test_jagged_rows_raises(self):
        with pytest.raises(ValueError, match="same number"):
            Table([['A', 'B'], ['C']])

    def test_line_count_no_labels(self):
        """2 rows, 3 cols => 3 horizontal + 4 vertical = 7 lines."""
        t = Table([['1', '2', '3'], ['4', '5', '6']])
        lines = [o for o in t.objects if isinstance(o, Line)]
        assert len(lines) == 7

    def test_line_count_with_col_labels_includes_top_line(self):
        """With col_labels, should have rows+2 horizontal lines (including top of header)."""
        t = Table([['1', '2'], ['3', '4']], col_labels=['A', 'B'])
        lines = [o for o in t.objects if isinstance(o, Line)]
        h_lines = [l for l in lines if l.p1.at_time(0)[1] == l.p2.at_time(0)[1]]
        # 4 lines: top of header, bottom of header, between rows, bottom
        assert len(h_lines) == 4


# ===========================================================================
# Matrix and _det
# ===========================================================================

class TestMatrix:

    def test_det_1x1(self):
        assert _det([[5]]) == 5

    def test_det_2x2(self):
        assert _det([[1, 2], [3, 4]]) == pytest.approx(-2)

    def test_det_3x3(self):
        assert _det([[1, 2, 3], [4, 5, 6], [7, 8, 10]]) == pytest.approx(-3)

    def test_det_identity(self):
        assert _det([[1, 0], [0, 1]]) == pytest.approx(1)

    def test_det_singular(self):
        assert _det([[1, 2], [2, 4]]) == pytest.approx(0)


# ===========================================================================
# DynamicObject
# ===========================================================================

class TestDynamicObject:

    def test_basic(self):
        d = DynamicObject(lambda t: Circle(r=50+t*10, cx=100, cy=100))
        assert len(d.to_svg(0)) > 0

    def test_caching(self):
        calls = [0]
        def f(t):
            calls[0] += 1
            return Rectangle(100, 50)
        d = DynamicObject(f)
        d.to_svg(0); d.to_svg(0)
        assert calls[0] == 1

    def test_none_returns_empty(self):
        d = DynamicObject(lambda t: None)
        assert d.to_svg(0) == ''
        assert d.bbox(0) == (0, 0, 0, 0)
        assert d.path(0) == ''


# ===========================================================================
# Canvas
# ===========================================================================

class TestCanvas:

    def test_empty_canvas_svg(self):
        svg = _make_canvas().generate_frame_svg(0)
        assert '<svg' in svg and '</svg>' in svg

    def test_add_and_render(self):
        c = _make_canvas()
        c.add(Rectangle(100, 50, x=10, y=20))
        assert 'rect' in c.generate_frame_svg(0)

    def test_frame_times(self):
        times = list(_make_canvas()._frame_times(0, 1, 10))
        assert len(times) == 11
        assert times[0] == pytest.approx(0.0)
        assert times[-1] == pytest.approx(1.0)

    def test_count_frames(self):
        assert VectorMathAnim._count_frames(0, 1, 10) == 11

    def test_resolve_end_explicit(self):
        assert _make_canvas()._resolve_end(5.0) == 5.0

    def test_resolve_end_auto(self):
        c = _make_canvas()
        r = Rectangle(100, 50)
        r.shift(dx=50, start=0, end=3)
        c.add(r)
        assert c._resolve_end(None) >= 3.0

    def test_camera_shift(self):
        c = _make_canvas()
        c.camera_shift(dx=100, dy=50, start=0, end=1)
        assert c.vb_x.at_time(1) == pytest.approx(100, abs=5)
        assert c.vb_y.at_time(1) == pytest.approx(50, abs=5)

    def test_camera_zoom(self):
        c = _make_canvas()
        c.camera_zoom(factor=2, start=0, end=1)
        assert c.vb_w.at_time(1) < 1920

    def test_svg_viewbox(self):
        svg = _make_canvas().generate_frame_svg(0)
        assert 'viewBox' in svg

    def test_svg_default_dimensions(self):
        svg = _make_canvas().generate_frame_svg(0)
        assert '1920' in svg and '1080' in svg

    def test_multiple_objects(self):
        c = _make_canvas()
        c.add(Circle(r=50, cx=100, cy=100))
        c.add(Rectangle(80, 40, x=200, y=200))
        svg = c.generate_frame_svg(0)
        assert 'rect' in svg


# ===========================================================================
# Line
# ===========================================================================

class TestLine:

    def test_length(self):
        assert Line(x1=0, y1=0, x2=100, y2=0).get_length(0) == pytest.approx(100)

    def test_diagonal_length(self):
        assert Line(x1=0, y1=0, x2=30, y2=40).get_length(0) == pytest.approx(50)

    def test_midpoint(self):
        mx, my = Line(x1=0, y1=0, x2=100, y2=100).get_midpoint(0)
        assert mx == pytest.approx(50) and my == pytest.approx(50)


# ===========================================================================
# Arc / Wedge
# ===========================================================================

class TestArc:

    def test_arc_renders(self):
        assert len(Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=90).to_svg(0)) > 0

    def test_wedge_renders(self):
        assert len(Wedge(cx=100, cy=100, r=50, start_angle=0, end_angle=90).to_svg(0)) > 0


# ===========================================================================
# RegularPolygon / Star
# ===========================================================================

class TestRegularPolygon:

    def test_vertex_count(self):
        assert len(RegularPolygon(6, radius=100).get_vertices(0)) == 6

    def test_is_regular(self):
        assert RegularPolygon(3, radius=100).is_regular() is True

    def test_star_vertex_count(self):
        assert len(Star(5, outer_radius=100, inner_radius=50).get_vertices(0)) == 10


# ===========================================================================
# VObject animation effects
# ===========================================================================

class TestVObjectEffects:

    def test_shift(self):
        r = Rectangle(100, 50, x=10, y=20)
        r.shift(dx=100, dy=50, start=0, end=1)
        bx, by, _, _ = r.bbox(1)
        assert bx == pytest.approx(110) and by == pytest.approx(70)

    def test_move_to(self):
        c = Circle(r=50, cx=0, cy=0)
        c.move_to(x=200, y=300, start=0, end=1)
        cx, cy = c.get_center(1)
        assert cx == pytest.approx(200, abs=5) and cy == pytest.approx(300, abs=5)

    def test_set_opacity(self):
        r = Rectangle(100, 50)
        r.set_opacity(0.5, start=0)
        assert r.styling.opacity.at_time(0) == pytest.approx(0.5)

    def test_set_fill_color(self):
        r = Rectangle(100, 50)
        r.set_fill(color='#ff0000', start=0)
        fill = r.styling.fill.time_func(0)
        assert fill[0] == pytest.approx(255, abs=1)

    def test_fadein_opacity(self):
        r = Rectangle(100, 50)
        r.fadein(start=0, end=1, change_existence=False)
        assert r.styling.opacity.at_time(0) == pytest.approx(0, abs=0.05)
        assert r.styling.opacity.at_time(1) == pytest.approx(1, abs=0.05)

    def test_fadeout_opacity(self):
        r = Rectangle(100, 50)
        r.fadeout(start=0, end=1)
        assert r.styling.opacity.at_time(1) == pytest.approx(0, abs=0.05)

    def test_scale(self):
        r = Rectangle(100, 50)
        r.scale(factor=2, start=0, end=1)
        assert r.styling.scale_x.at_time(1) == pytest.approx(2, abs=0.1)

    def test_rotate_to(self):
        r = Rectangle(100, 50)
        r.rotate_to(start=0, end=1, degrees=90)
        rot = r.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(90, abs=1)

    def test_rotate_by(self):
        r = Rectangle(100, 50)
        r.rotate_by(start=0, end=1, degrees=45)
        rot = r.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(45, abs=1)


# ===========================================================================
# Base effects: look_at, typewriter, stamp_trail, unfold, etc.
# ===========================================================================

class TestBaseEffects:

    def test_look_at_with_end_none_is_instant(self):
        """look_at with end=None: end or start => 0, so rotate_to(0, 0, ...) = instant."""
        r = Rectangle(100, 50, x=0, y=0)
        r.look_at((500, 500), start=0, end=None)
        rot = r.styling.rotation.at_time(0)
        assert isinstance(rot[0], (int, float))

    def test_look_at_animated(self):
        r = Rectangle(100, 50, x=0, y=0)
        r.look_at((500, 500), start=0, end=1)
        rot = r.styling.rotation.at_time(1)
        assert rot[0] != pytest.approx(0, abs=1)

    def test_typewriter_reveals_text(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello', start=0, end=1)
        assert t.text.at_time(1) == 'Hello'
        assert len(t.text.at_time(0.5)) < len('Hello')

    def test_typewriter_empty_noop(self):
        t = Text(text='', x=100, y=100)
        assert t.typewriter_effect('', start=0, end=1) is t

    def test_stamp_trail(self):
        r = Rectangle(100, 50)
        r.shift(dx=200, start=0, end=1)
        assert len(r.stamp_trail(start=0, end=1, count=5)) == 5

    def test_stamp_trail_zero(self):
        assert Rectangle(100, 50).stamp_trail(start=0, end=1, count=0) == []

    def test_stamp_trail_negative_duration(self):
        assert Rectangle(100, 50).stamp_trail(start=1, end=0, count=5) == []

    def test_unfold_horizontal(self):
        r = Rectangle(100, 50, x=0, y=0)
        r.unfold(start=0, end=1, direction='right')
        assert r.styling.scale_x.at_time(0) == pytest.approx(0, abs=0.05)
        assert r.styling.scale_x.at_time(1) == pytest.approx(1, abs=0.05)

    def test_unfold_vertical(self):
        r = Rectangle(100, 50, x=0, y=0)
        r.unfold(start=0, end=1, direction='down')
        assert r.styling.scale_y.at_time(0) == pytest.approx(0, abs=0.05)
        assert r.styling.scale_y.at_time(1) == pytest.approx(1, abs=0.05)

    def test_glitch_shift_deterministic(self):
        r1, r2 = Rectangle(100, 50), Rectangle(100, 50)
        r1.glitch_shift(start=0, end=1, seed=42)
        r2.glitch_shift(start=0, end=1, seed=42)
        assert r1.styling.dx.at_time(0.5) == pytest.approx(r2.styling.dx.at_time(0.5))

    def test_show_if_basic(self):
        r = Rectangle(100, 50)
        r.show_if(lambda t: t < 0.5, start=0)
        assert r.styling.opacity.at_time(0.25) == pytest.approx(1)
        assert r.styling.opacity.at_time(0.75) == pytest.approx(0)

    def test_cycle_colors(self):
        r = Rectangle(100, 50)
        r.cycle_colors(['#ff0000', '#00ff00', '#0000ff'], start=0, end=1)
        f0 = r.styling.fill.time_func(0)
        f1 = r.styling.fill.time_func(1)
        assert f0[0] > 200  # red at start
        assert f1[2] > 200  # blue at end

    def test_cycle_colors_single_noop(self):
        r = Rectangle(100, 50)
        assert r.cycle_colors(['#ff0000'], start=0, end=1) is r


# ===========================================================================
# show_passing_flash
# ===========================================================================

class TestShowPassingFlash:

    def test_basic(self):
        flash = Path('M 0 0 L 100 0 L 100 100').show_passing_flash(start=0, end=1)
        assert isinstance(flash, Path)

    def test_zero_duration_returns_empty(self):
        """dur=0 returns an empty path instead of mismatched timing."""
        flash = Path('M 0 0 L 100 0').show_passing_flash(start=1, end=1)
        assert isinstance(flash, Path)

    def test_empty_path(self):
        flash = Path('').show_passing_flash(start=0, end=1)
        assert isinstance(flash, Path)


# ===========================================================================
# Flicker effect (BUG: inverted max(0, -flicker))
# ===========================================================================

class TestFlickerEffect:

    def test_flicker_varies_opacity(self):
        """The flicker effect should cause opacity to vary over time."""
        r = Rectangle(100, 50)
        r.flicker(start=0, end=1, frequency=10, min_opacity=0.2)
        opacities = [r.styling.opacity.at_time(t / 100) for t in range(101)]
        assert all(0 <= op <= 1.01 for op in opacities)
        assert min(opacities) < 1.0  # should actually flicker

    def test_flicker_uses_abs_value(self):
        """abs(flicker) means the effect triggers for both positive and negative sine waves."""
        r = Rectangle(100, 50)
        r.flicker(start=0, end=1, frequency=5, min_opacity=0.0)
        below_one = sum(1 for t in range(101)
                        if r.styling.opacity.at_time(t / 100) < 0.99)
        # With abs(flicker), dimming should happen more frequently
        assert below_one > 10


# ===========================================================================
# Helpers
# ===========================================================================

class TestHelpers:

    def test_norm_dir_strings(self):
        assert _norm_dir('right') == 'right'
        assert _norm_dir('left') == 'left'
        assert _norm_dir('up') == 'up'
        assert _norm_dir('down') == 'down'

    def test_norm_dir_tuples(self):
        assert _norm_dir(RIGHT) == 'right'
        assert _norm_dir(LEFT) == 'left'
        assert _norm_dir(UP) == 'up'
        assert _norm_dir(DOWN) == 'down'

    def test_norm_edge_string(self):
        assert _norm_edge('right') == 'right'

    def test_norm_edge_tuple(self):
        assert _norm_edge(RIGHT) == 'right'


# ===========================================================================
# Easings (extended)
# ===========================================================================

class TestEasingsExtended:

    def test_all_easings_endpoints(self):
        fns = [
            easings.linear, easings.smooth, easings.rush_into, easings.rush_from,
            easings.ease_in_out_quad, easings.ease_in_quad, easings.ease_out_quad,
            easings.ease_in_cubic, easings.ease_out_cubic, easings.ease_in_out_cubic,
            easings.ease_in_sine, easings.ease_out_sine, easings.ease_in_out_sine,
            easings.ease_in_expo, easings.ease_out_expo, easings.ease_in_out_expo,
            easings.ease_in_circ, easings.ease_out_circ, easings.ease_in_out_circ,
        ]
        for fn in fns:
            assert fn(0) == pytest.approx(0, abs=1e-6), f"{fn.__name__}(0) != 0"
            assert fn(1) == pytest.approx(1, abs=1e-6), f"{fn.__name__}(1) != 1"

    def test_monotonic(self):
        for fn in [easings.linear, easings.smooth,
                   easings.ease_in_quad, easings.ease_out_quad,
                   easings.ease_in_cubic, easings.ease_out_cubic]:
            prev = fn(0)
            for i in range(1, 101):
                curr = fn(i / 100)
                assert curr >= prev - 1e-6, f"{fn.__name__} not monotonic at t={i/100}"
                prev = curr

    def test_smooth_midpoint(self):
        assert easings.smooth(0.5) == pytest.approx(0.5, abs=0.01)

    def test_linear_identity(self):
        for t in [0, 0.25, 0.5, 0.75, 1.0]:
            assert easings.linear(t) == pytest.approx(t)


# ===========================================================================
# Attributes
# ===========================================================================

class TestAttributesExtended:

    def test_real_basic(self):
        r = attributes.Real(0, 100)
        assert r.at_time(0) == 100

    def test_real_animation(self):
        r = attributes.Real(0, 0)
        r.move_to(0, 1, 100)
        assert r.at_time(0) == pytest.approx(0)
        assert r.at_time(1) == pytest.approx(100)
        assert 0 < r.at_time(0.5) < 100

    def test_real_set_onward(self):
        r = attributes.Real(0, 10)
        r.set_onward(2, 50)
        assert r.at_time(1) == 10
        assert r.at_time(2) == 50 and r.at_time(3) == 50

    def test_real_add_onward(self):
        r = attributes.Real(0, 10)
        r.add_onward(0, lambda t: t * 5)
        assert r.at_time(0) == pytest.approx(10)
        assert r.at_time(1) == pytest.approx(15)

    def test_last_change_tracking(self):
        r = attributes.Real(0, 0)
        assert r.last_change == 0
        r.move_to(1, 3, 100)
        assert r.last_change >= 3


# ===========================================================================
# NumberLine
# ===========================================================================

class TestNumberLine:

    def test_basic(self):
        assert len(NumberLine(x_range=(0, 10, 1), length=500).to_svg(0)) > 0

    def test_with_numbers(self):
        assert len(NumberLine(x_range=(0, 5, 1), length=500, include_numbers=True).to_svg(0)) > 0


# ===========================================================================
# VCollection operations
# ===========================================================================

class TestCollectionOps:

    def test_filter(self):
        items = [Circle(r=r) for r in [10, 50, 100]]
        big = VCollection(*items).filter(lambda obj: obj.r.at_time(0) > 30)
        assert len(big.objects) == 2

    def test_select(self):
        items = [Rectangle(10, 10) for _ in range(5)]
        assert len(VCollection(*items).select(1, 3).objects) == 2

    def test_for_each(self):
        items = [Circle(r=10) for _ in range(3)]
        coll = VCollection(*items)
        # for_each takes a method name string, not a lambda
        coll.for_each('set_opacity', value=0.5, start=0)
        for obj in coll.objects:
            assert obj.styling.opacity.at_time(0) == pytest.approx(0.5)

    def test_sort_objects(self):
        items = [Circle(r=10, cx=x, cy=0) for x in [300, 100, 200]]
        coll = VCollection(*items)
        coll.sort_objects(key=lambda obj: obj.c.at_time(0)[0])
        xs = [obj.c.at_time(0)[0] for obj in coll.objects]
        assert xs == sorted(xs)

    def test_distribute(self):
        items = [Circle(r=10) for _ in range(4)]
        coll = VCollection(*items)
        coll.distribute(direction='right', start=0)
        xs = [o.bbox(0)[0] for o in coll.objects]
        for i in range(len(xs) - 1):
            assert xs[i] <= xs[i+1] + 1


# ===========================================================================
# Bbox-derived methods
# ===========================================================================

class TestBboxMethods:

    def test_get_center(self):
        cx, cy = Rectangle(100, 50, x=10, y=20).get_center(0)
        assert cx == pytest.approx(60) and cy == pytest.approx(45)

    def test_get_width(self):
        assert Rectangle(100, 50, x=10, y=20).get_width(0) == pytest.approx(100)

    def test_get_height(self):
        assert Rectangle(100, 50, x=10, y=20).get_height(0) == pytest.approx(50)

    def test_get_edge_right(self):
        ex, ey = Rectangle(100, 50, x=10, y=20).get_edge('right', time=0)
        assert ex == pytest.approx(110) and ey == pytest.approx(45)

    def test_get_edge_left(self):
        ex, ey = Rectangle(100, 50, x=10, y=20).get_edge('left', time=0)
        assert ex == pytest.approx(10) and ey == pytest.approx(45)

    def test_get_edge_top(self):
        ex, ey = Rectangle(100, 50, x=10, y=20).get_edge('top', time=0)
        assert ex == pytest.approx(60) and ey == pytest.approx(20)

    def test_get_edge_bottom(self):
        ex, ey = Rectangle(100, 50, x=10, y=20).get_edge('bottom', time=0)
        assert ex == pytest.approx(60) and ey == pytest.approx(70)

    def test_get_x_y(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.get_x(0) == pytest.approx(60)
        assert r.get_y(0) == pytest.approx(45)

    def test_distance_to(self):
        r1 = Rectangle(10, 10, x=0, y=0)
        r2 = Rectangle(10, 10, x=100, y=0)
        assert r1.distance_to(r2, time=0) == pytest.approx(100, abs=15)


# ===========================================================================
# Visibility
# ===========================================================================

class TestVisibility:

    def test_show_hide(self):
        r = Rectangle(100, 50)
        r.show.set_onward(0, True)
        r.show.set_onward(1, False)
        assert r.show.at_time(0) is True and r.show.at_time(1) is False

    def test_visibility_toggle(self):
        r = Rectangle(100, 50)
        r.visibility_toggle(1, 2, 3)
        assert r.show.at_time(0.5) is False  # before first toggle
        assert r.show.at_time(1) is True      # after first toggle
        assert r.show.at_time(2) is False      # after second toggle
        assert r.show.at_time(3) is True       # after third toggle


# ===========================================================================
# to_svg rendering
# ===========================================================================

class TestToSvg:

    def test_circle(self):
        assert 'circle' in Circle(r=50, cx=100, cy=100).to_svg(0)

    def test_rectangle(self):
        assert 'rect' in Rectangle(100, 50, x=10, y=20).to_svg(0)

    def test_line(self):
        assert 'line' in Line(x1=0, y1=0, x2=100, y2=100).to_svg(0)

    def test_polygon(self):
        svg = Polygon((0, 0), (100, 0), (50, 80)).to_svg(0)
        assert 'polygon' in svg or 'path' in svg

    def test_dot(self):
        assert len(Dot(cx=100, cy=200).to_svg(0)) > 0

    def test_text(self):
        assert 'Hello' in Text(text='Hello', x=100, y=100).to_svg(0)

    def test_path(self):
        assert 'path' in Path('M 0 0 L 100 100').to_svg(0)

    def test_rounded_rectangle(self):
        svg = RoundedRectangle(100, 50, corner_radius=10).to_svg(0)
        assert 'rect' in svg


# ===========================================================================
# Stagger
# ===========================================================================

class TestStagger:

    def test_stagger_creates_animation(self):
        items = [Rectangle(40, 30) for _ in range(3)]
        coll = VCollection(*items)
        coll.stagger('fadein', start=0, end=3, overlap=0.5)
        # Each object should have its opacity modified
        # The last object finishes last; check at time 3
        last = coll.objects[-1]
        assert last.styling.opacity.at_time(3) == pytest.approx(1, abs=0.15)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:

    def test_origin(self):
        assert ORIGIN == (960, 540)

    def test_unit(self):
        assert UNIT == 135

    def test_directions(self):
        assert UP == (0, -1)
        assert DOWN == (0, 1)
        assert LEFT == (-1, 0)
        assert RIGHT == (1, 0)


# ===========================================================================
# Path
# ===========================================================================

class TestPath:

    def test_create(self):
        assert 'path' in Path('M 0 0 L 100 0 L 100 100 Z').to_svg(0)

    def test_empty(self):
        Path('').to_svg(0)  # should not crash
