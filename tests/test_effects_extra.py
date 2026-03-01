"""Tests for effects with zero or minimal test coverage."""
from vectormation.objects import (
    Circle, Rectangle, Dot, VectorMathAnim,
)


class TestFloatAnim:
    def test_returns_self(self):
        c = Circle(r=30, creation=0)
        assert c.float_anim(0, 2) is c

    def test_zero_duration_noop(self):
        c = Circle(r=30, cx=100, cy=100, creation=0)
        cy_before = c.center(0)[1]
        c.float_anim(0, 0)
        assert c.center(0)[1] == cy_before

    def test_oscillates_vertically(self):
        c = Circle(r=30, cx=100, cy=100, creation=0)
        c.float_anim(0, 2, amplitude=20, speed=1)
        # At t=0.25 (quarter period), should have moved
        _, cy1 = c.center(0.25)
        assert cy1 != 100

    def test_returns_to_start(self):
        c = Circle(r=30, cx=100, cy=100, creation=0)
        c.float_anim(0, 1, amplitude=20, speed=1)
        _, cy_end = c.center(1.0)
        assert abs(cy_end - 100) < 1


class TestHighlightBorder:
    def test_returns_self(self):
        r = Rectangle(100, 50, creation=0)
        assert r.highlight_border(0, 1) is r

    def test_zero_duration_noop(self):
        r = Rectangle(100, 50, creation=0)
        r.highlight_border(0, 0)

    def test_changes_stroke(self):
        r = Rectangle(100, 50, creation=0)
        r.highlight_border(0, 1, color='#FF0000', width=8)
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(r)
        svg = v.generate_frame_svg(time=0.25)
        assert 'stroke' in svg


class TestSpiralOut:
    def test_returns_self(self):
        c = Circle(r=30, creation=0)
        assert c.spiral_out(0, 1) is c

    def test_hides_at_end(self):
        c = Circle(r=30, creation=0)
        c.spiral_out(0, 1, change_existence=True)
        assert not c.show.at_time(1.5)

    def test_zero_duration_noop(self):
        c = Circle(r=30, creation=0)
        c.spiral_out(0, 0)


class TestWipe:
    def test_wipe_right_shows_object(self):
        r = Rectangle(100, 50, creation=0)
        r.wipe('right', 0, 1)
        assert r.show.at_time(0.5)

    def test_wipe_reverse_hides(self):
        r = Rectangle(100, 50, creation=0)
        r.wipe('left', 0, 1, reverse=True)
        assert not r.show.at_time(1.5)


class TestAnimateDash:
    def test_returns_self(self):
        r = Rectangle(100, 50, creation=0)
        assert r.animate_dash(0, 1) is r

    def test_sets_dasharray(self):
        r = Rectangle(100, 50, creation=0)
        r.animate_dash(0, 1, dash_length=15, gap=10)
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(r)
        svg = v.generate_frame_svg(time=0.5)
        assert 'stroke-dasharray' in svg

    def test_zero_duration_noop(self):
        r = Rectangle(100, 50, creation=0)
        r.animate_dash(0, 0)


class TestRipple:
    def test_returns_vcollection(self):
        d = Dot(cx=100, cy=100, creation=0)
        rings = d.ripple(0, 1)
        assert len(rings.objects) > 0

    def test_custom_count(self):
        d = Dot(cx=100, cy=100, creation=0)
        rings = d.ripple(0, 1, count=5)
        assert len(rings.objects) == 5


class TestSwirl:
    def test_returns_self(self):
        c = Circle(r=30, creation=0)
        assert c.swirl(0, 1) is c

    def test_renders_with_rotation(self):
        c = Circle(r=30, cx=100, cy=100, creation=0)
        c.swirl(0, 1, turns=2)
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(c)
        svg = v.generate_frame_svg(time=0.5)
        assert 'transform' in svg or 'rotate' in svg

    def test_zero_duration_noop(self):
        c = Circle(r=30, creation=0)
        c.swirl(0, 0)


class TestWarp:
    def test_returns_self(self):
        r = Rectangle(100, 50, creation=0)
        assert r.warp(0, 1) is r

    def test_renders_during_animation(self):
        r = Rectangle(100, 50, creation=0)
        r.warp(0, 1, amplitude=0.3)
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(r)
        svg = v.generate_frame_svg(time=0.5)
        assert 'transform' in svg

    def test_zero_duration_noop(self):
        r = Rectangle(100, 50, creation=0)
        r.warp(0, 0)


class TestHomotopy:
    def test_returns_self(self):
        r = Rectangle(100, 50, creation=0)
        assert r.homotopy(lambda x, y, t: (x, y + 10 * t), 0, 1) is r

    def test_vertices_move(self):
        r = Rectangle(100, 50, x=100, y=100, creation=0)
        r.homotopy(lambda x, y, t: (x, y + 50 * t), 0, 1)
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(r)
        svg = v.generate_frame_svg(time=1)
        assert svg


class TestSlideOut:
    def test_returns_self(self):
        c = Circle(r=30, creation=0)
        assert c.slide_out('down', 0, 1) is c

    def test_hides_after(self):
        c = Circle(r=30, creation=0)
        c.slide_out('down', start=0, end=1, change_existence=True)
        assert not c.show.at_time(1.5)


class TestBroadcast:
    def test_returns_vcollection(self):
        d = Dot(cx=100, cy=100, creation=0)
        copies = d.broadcast(0, 1, n_copies=3)
        assert len(copies.objects) == 3

    def test_custom_count(self):
        d = Dot(cx=100, cy=100, creation=0)
        copies = d.broadcast(0, 1, n_copies=5)
        assert len(copies.objects) == 5


class TestFlashHighlight:
    def test_returns_rectangle(self):
        c = Circle(r=30, creation=0)
        rect = c.flash_highlight(0, 1)
        assert rect is not None

    def test_custom_color(self):
        c = Circle(r=30, creation=0)
        rect = c.flash_highlight(0, 1, color='#FF0000')
        v = VectorMathAnim(save_dir='/tmp/test_effects')
        v.add(rect)
        svg = v.generate_frame_svg(time=0.5)
        assert svg
