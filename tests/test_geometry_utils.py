"""Tests for under-tested geometry utilities and shape helpers."""
import math
import pytest
from vectormation.objects import (
    AnnotationDot, BackgroundRectangle, ScreenRectangle, SurroundingCircle,
    Elbow, RightAngle, Countdown, LabeledDot,
    Circle, Rectangle, Square, Text, Dot, Star, RegularPolygon,
    VectorMathAnim, ORIGIN,
)


class TestAnnotationDot:
    def test_default_creation(self):
        d = AnnotationDot()
        assert d is not None

    def test_default_position_at_origin(self):
        d = AnnotationDot()
        cx, cy = d.center(0)
        assert abs(cx - ORIGIN[0]) < 1
        assert abs(cy - ORIGIN[1]) < 1

    def test_custom_position(self):
        d = AnnotationDot(cx=100, cy=200)
        cx, cy = d.center(0)
        assert abs(cx - 100) < 1
        assert abs(cy - 200) < 1

    def test_stroke_defaults(self):
        d = AnnotationDot()
        v = VectorMathAnim('/tmp')
        v.add(d)
        out = v.generate_frame_svg(0)
        assert 'stroke-width' in out

    def test_custom_radius(self):
        d = AnnotationDot(r=30)
        assert d.rx.at_time(0) == pytest.approx(30, abs=1)

    def test_repr(self):
        d = AnnotationDot(cx=100, cy=200)
        r = repr(d)
        assert 'AnnotationDot' in r

    def test_inherits_from_dot(self):
        d = AnnotationDot()
        assert isinstance(d, Dot)


class TestBackgroundRectangle:
    def test_surrounds_target(self):
        target = Circle(r=50, cx=500, cy=300)
        bg = BackgroundRectangle(target)
        bx, by, bw, bh = bg.bbox(0)
        tx, ty, tw, th = target.bbox(0)
        assert bw >= tw
        assert bh >= th

    def test_default_z_behind(self):
        target = Square(50)
        bg = BackgroundRectangle(target)
        assert bg.z.at_time(0) <= 0

    def test_custom_buff(self):
        target = Square(50, x=400, y=400)
        bg1 = BackgroundRectangle(target, buff=5)
        bg2 = BackgroundRectangle(target, buff=50)
        assert bg2.get_width(0) > bg1.get_width(0)

    def test_custom_fill(self):
        target = Circle(r=30)
        bg = BackgroundRectangle(target, fill='#ff0000')
        svg = VectorMathAnim('/tmp')
        svg.add(bg)
        out = svg.generate_frame_svg(0)
        assert 'rgb(255,0,0)' in out or '255, 0, 0' in out

    def test_repr(self):
        bg = BackgroundRectangle(Circle(r=30))
        assert 'BackgroundRectangle' in repr(bg)


class TestScreenRectangle:
    def test_default_aspect_ratio(self):
        sr = ScreenRectangle()
        w = sr.get_width(0)
        h = sr.get_height(0)
        assert abs(w / h - 16 / 9) < 0.1

    def test_custom_width(self):
        sr = ScreenRectangle(width=800)
        w = sr.get_width(0)
        assert abs(w - 800) < 1

    def test_height_derived_from_width(self):
        sr = ScreenRectangle(width=640)
        h = sr.get_height(0)
        assert abs(h - 640 * 9 / 16) < 1

    def test_repr(self):
        sr = ScreenRectangle()
        assert 'ScreenRectangle' in repr(sr)

    def test_is_rectangle(self):
        sr = ScreenRectangle()
        assert isinstance(sr, Rectangle)


class TestSurroundingCircle:
    def test_encloses_target(self):
        target = Square(60, x=400, y=400)
        sc = SurroundingCircle(target)
        r = sc.rx.at_time(0)
        _, _, tw, th = target.bbox(0)
        min_r = math.hypot(tw, th) / 2
        assert r >= min_r

    def test_centered_on_target(self):
        target = Circle(r=40, cx=500, cy=300)
        sc = SurroundingCircle(target)
        scx, scy = sc.center(0)
        tcx, tcy = target.center(0)
        assert abs(scx - tcx) < 2
        assert abs(scy - tcy) < 2

    def test_follows_target(self):
        target = Circle(r=30, cx=200, cy=200)
        sc = SurroundingCircle(target, follow=True)
        target.shift(dx=100, dy=0, start=0, end=1)
        scx_before, _ = sc.center(0)
        scx_after, _ = sc.center(1)
        assert abs(scx_after - scx_before - 100) < 5

    def test_no_follow(self):
        target = Circle(r=30, cx=200, cy=200)
        sc = SurroundingCircle(target, follow=False)
        target.shift(dx=100, dy=0, start=0, end=1)
        scx_before, _ = sc.center(0)
        scx_after, _ = sc.center(1)
        assert abs(scx_after - scx_before) < 5

    def test_custom_buff(self):
        target = Circle(r=30, cx=200, cy=200)
        sc1 = SurroundingCircle(target, buff=5)
        sc2 = SurroundingCircle(target, buff=50)
        assert sc2.rx.at_time(0) > sc1.rx.at_time(0)

    def test_repr(self):
        sc = SurroundingCircle(Circle(r=20))
        assert 'SurroundingCircle' in repr(sc)


class TestElbow:
    def test_creation(self):
        e = Elbow()
        assert e is not None

    def test_custom_size(self):
        e = Elbow(width=60, height=80)
        _, _, w, h = e.bbox(0)
        assert w > 0
        assert h > 0

    def test_custom_position(self):
        e = Elbow(cx=100, cy=200)
        svg = VectorMathAnim('/tmp')
        svg.add(e)
        out = svg.generate_frame_svg(0)
        assert '100' in out

    def test_repr(self):
        e = Elbow()
        assert 'Elbow' in repr(e)

    def test_renders_svg(self):
        e = Elbow()
        v = VectorMathAnim('/tmp')
        v.add(e)
        svg = v.generate_frame_svg(0)
        assert '<polyline' in svg or '<path' in svg


class TestRightAngle:
    def test_creation(self):
        ra = RightAngle(vertex=(0, 0), p1=(1, 0), p2=(0, 1))
        assert ra is not None

    def test_renders(self):
        ra = RightAngle(vertex=(100, 100), p1=(200, 100), p2=(100, 200))
        v = VectorMathAnim('/tmp')
        v.add(ra)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100

    def test_custom_size(self):
        ra = RightAngle(vertex=(0, 0), p1=(1, 0), p2=(0, 1), size=30)
        assert ra is not None

    def test_custom_style(self):
        ra = RightAngle(vertex=(0, 0), p1=(1, 0), p2=(0, 1), stroke='#ff0000')
        v = VectorMathAnim('/tmp')
        v.add(ra)
        svg = v.generate_frame_svg(0)
        assert 'rgb(255,0,0)' in svg or '255, 0, 0' in svg

    def test_45_degree_angle(self):
        ra = RightAngle(vertex=(100, 100), p1=(200, 0), p2=(0, 200))
        v = VectorMathAnim('/tmp')
        v.add(ra)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 50


class TestCountdown:
    def test_creation(self):
        cd = Countdown(start_value=5, end_value=0, start=0, end=5)
        assert cd is not None

    def test_renders_initial_value(self):
        cd = Countdown(start_value=10, end_value=0, start=0, end=10)
        v = VectorMathAnim('/tmp')
        v.add(cd)
        svg = v.generate_frame_svg(0)
        assert '10' in svg

    def test_value_changes_over_time(self):
        cd = Countdown(start_value=10, end_value=0, start=0, end=10)
        v = VectorMathAnim('/tmp')
        v.add(cd)
        svg5 = v.generate_frame_svg(5)
        assert '5' in svg5

    def test_counts_up(self):
        cd = Countdown(start_value=0, end_value=10, start=0, end=10)
        v = VectorMathAnim('/tmp')
        v.add(cd)
        svg = v.generate_frame_svg(10)
        assert '10' in svg

    def test_custom_position(self):
        cd = Countdown(start_value=5, end_value=0, x=100, y=200, start=0, end=5)
        v = VectorMathAnim('/tmp')
        v.add(cd)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 50


class TestLabeledDot:
    def test_creation(self):
        from vectormation.objects import LabeledDot
        ld = LabeledDot('A')
        assert ld is not None

    def test_renders_label(self):
        from vectormation.objects import LabeledDot
        ld = LabeledDot('X', cx=300, cy=300)
        v = VectorMathAnim('/tmp')
        v.add(ld)
        svg = v.generate_frame_svg(0)
        assert 'X' in svg

    def test_custom_position(self):
        from vectormation.objects import LabeledDot
        ld = LabeledDot('Z', cx=100, cy=200)
        cx, cy = ld.center(0)
        assert abs(cx - 100) < 50
        assert abs(cy - 200) < 50

    def test_custom_radius(self):
        from vectormation.objects import LabeledDot
        ld = LabeledDot('B', r=40)
        assert ld is not None


class TestStar:
    def test_default_creation(self):
        s = Star()
        assert s is not None

    def test_custom_points(self):
        s3 = Star(n=3)
        s8 = Star(n=8)
        assert s3 is not None
        assert s8 is not None

    def test_custom_radii(self):
        s = Star(outer_radius=100, inner_radius=40)
        assert s._outer_radius == 100
        assert s._inner_radius == 40

    def test_renders_svg(self):
        s = Star(n=5, cx=500, cy=400)
        v = VectorMathAnim('/tmp')
        v.add(s)
        svg = v.generate_frame_svg(0)
        assert '<polygon' in svg or '<path' in svg

    def test_auto_inner_radius(self):
        s = Star(n=5, outer_radius=100)
        assert abs(s._inner_radius - 40) < 1


class TestRegularPolygon:
    def test_triangle(self):
        p = RegularPolygon(3)
        assert p is not None

    def test_hexagon(self):
        p = RegularPolygon(6, radius=100)
        assert p is not None

    def test_side_length(self):
        p = RegularPolygon(4, radius=100)
        expected = 2 * 100 * math.sin(math.pi / 4)
        assert abs(p.get_side_length() - expected) < 0.1

    def test_inradius(self):
        p = RegularPolygon(6, radius=100)
        expected = 100 * math.cos(math.pi / 6)
        assert abs(p.get_inradius() - expected) < 0.1

    def test_apothem_alias(self):
        p = RegularPolygon(5, radius=80)
        assert abs(p.get_apothem() - p.get_inradius()) < 0.01

    def test_custom_position(self):
        p = RegularPolygon(4, cx=100, cy=200)
        cx, cy = p.center(0)
        assert abs(cx - 100) < 5
        assert abs(cy - 200) < 5

    def test_rotation_angle(self):
        p1 = RegularPolygon(4, angle=0)
        p2 = RegularPolygon(4, angle=45)
        b1 = p1.bbox(0)
        b2 = p2.bbox(0)
        # Different angle should give different bbox shape
        assert abs(b1[2] - b2[2]) > 1 or abs(b1[3] - b2[3]) > 1
