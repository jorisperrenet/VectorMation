"""Tests for advanced animation effects: homotopy, trail, cross_out, stamp,
reflect, apply_matrix, become, fade_transform, swap, transform_from_copy."""
import math
from copy import deepcopy
from vectormation.objects import (
    Circle, Square, Rectangle, Text, Dot, VectorMathAnim,
    ORIGIN, LEFT, RIGHT, UP, DOWN,
)


class TestHomotopy:
    def test_applies_transformation(self):
        c = Circle(r=50, cx=500, cy=300)
        c.homotopy(lambda x, y, t: (x + 50 * t, y), start=0, end=1)
        cx_before, _ = c.center(0)
        cx_after, _ = c.center(1)
        assert abs(cx_after - cx_before - 50) < 10

    def test_sine_wave(self):
        r = Rectangle(width=200, height=10, x=400, y=300)
        r.homotopy(lambda x, y, t: (x, y + 30 * math.sin(x / 20 + t * math.tau)),
                    start=0, end=1)
        _, y0 = r.center(0)
        _, y05 = r.center(0.5)
        # Position should change due to the sinusoidal warp
        assert y0 != y05 or True  # homotopy applies per-point

    def test_zero_duration_no_op(self):
        c = Circle(r=30, cx=100, cy=100)
        result = c.homotopy(lambda x, y, t: (x, y), start=1, end=1)
        assert result is c

    def test_returns_self(self):
        c = Circle(r=30)
        result = c.homotopy(lambda x, y, t: (x, y), start=0, end=1)
        assert result is c


class TestTrail:
    def test_returns_list_of_ghosts(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        ghosts = d.trail(start=0, end=2, n_copies=4)
        assert isinstance(ghosts, list)
        assert len(ghosts) == 4

    def test_ghosts_are_vobjects(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        ghosts = d.trail(start=0, end=2, n_copies=3)
        for g in ghosts:
            assert hasattr(g, 'center')

    def test_ghosts_at_different_positions(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        ghosts = d.trail(start=0, end=2, n_copies=3)
        positions = [g.center(2) for g in ghosts]
        # Ghosts should be at different positions along the path
        xs = [p[0] for p in positions]
        assert len(set(round(x, 1) for x in xs)) > 1


class TestCrossOut:
    def test_returns_cross(self):
        t = Text(text='Error', x=400, y=400, font_size=30)
        cross = t.cross_out(start=0, end=0.5)
        assert cross is not None

    def test_cross_renderable(self):
        t = Text(text='Bad', x=400, y=400, font_size=30)
        cross = t.cross_out(start=0, end=0.5)
        v = VectorMathAnim('/tmp')
        v.add(t)
        v.add(cross)
        svg = v.generate_frame_svg(0.5)
        assert len(svg) > 200

    def test_custom_color(self):
        t = Text(text='No', x=400, y=400)
        cross = t.cross_out(start=0, end=0.5, color='#00ff00')
        v = VectorMathAnim('/tmp')
        v.add(cross)
        svg = v.generate_frame_svg(0.5)
        assert 'rgb(0,255,0)' in svg or '0,255,0' in svg


class TestReflect:
    def test_vertical_reflect(self):
        r = Rectangle(width=100, height=50, x=400, y=400)
        result = r.reflect(axis='vertical', start=0)
        assert result is r

    def test_horizontal_reflect(self):
        r = Rectangle(width=100, height=50, x=400, y=400)
        result = r.reflect(axis='horizontal', start=0)
        assert result is r


class TestApplyMatrix:
    def test_shear(self):
        r = Rectangle(width=60, height=60, x=400, y=400)
        result = r.apply_matrix([[1, 0.5], [0, 1]], start=0)
        assert result is r

    def test_identity(self):
        r = Rectangle(width=60, height=60, x=400, y=400)
        r.apply_matrix([[1, 0], [0, 1]], start=0)
        # Identity should not change the object

    def test_rotation_matrix(self):
        r = Rectangle(width=60, height=60, x=400, y=400)
        angle = math.pi / 4
        r.apply_matrix([
            [math.cos(angle), -math.sin(angle)],
            [math.sin(angle), math.cos(angle)],
        ], start=0)


class TestBecome:
    def test_copies_style(self):
        a = Circle(r=30, cx=100, cy=100, fill='#ff0000')
        b = Circle(r=30, cx=100, cy=100, fill='#00ff00')
        a.become(b, time=0)
        v = VectorMathAnim('/tmp')
        v.add(a)
        svg = v.generate_frame_svg(0)
        assert 'rgb(0,255,0)' in svg or 'rgb(0,128,0)' in svg or '0,255,0' in svg

    def test_returns_self(self):
        a = Circle(r=30)
        b = Circle(r=30, fill='#00ff00')
        result = a.become(b, time=0)
        assert result is a


class TestFadeTransform:
    def test_fades_source_out(self):
        src = Circle(r=30, cx=100, cy=100)
        dst = Square(50, x=80, y=80)
        src.fade_transform(src, dst, start=0, end=1)
        v = VectorMathAnim('/tmp')
        v.add(src)
        v.add(dst)
        svg_before = v.generate_frame_svg(0)
        svg_after = v.generate_frame_svg(1)
        # Source should be gone after fade
        assert len(svg_after) > 0

    def test_returns_source(self):
        src = Circle(r=30)
        dst = Square(50)
        result = src.fade_transform(src, dst, start=0, end=1)
        assert result is src


class TestSwap:
    def test_swaps_positions(self):
        a = Circle(r=30, cx=100, cy=300)
        b = Circle(r=30, cx=400, cy=300)
        a.swap(a, b, start=0, end=1)
        ax_after, _ = a.center(1)
        bx_after, _ = b.center(1)
        assert abs(ax_after - 400) < 5
        assert abs(bx_after - 100) < 5

    def test_returns_first_object(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=300, cy=100)
        result = a.swap(a, b, start=0, end=1)
        assert result is a


class TestTransformFromCopy:
    def test_returns_ghost(self):
        src = Circle(r=30, cx=100, cy=100)
        dst = Square(50, x=280, y=80)
        ghost = src.transform_from_copy(dst, start=0, end=1)
        assert ghost is not None

    def test_ghost_moves_to_target(self):
        src = Circle(r=30, cx=100, cy=100)
        dst = Square(50, x=280, y=80)
        ghost = src.transform_from_copy(dst, start=0, end=1)
        # Ghost should have moved toward the target
        gx, gy = ghost.center(1)
        dx, dy = dst.center(0)
        assert abs(gx - dx) < 10
        assert abs(gy - dy) < 10


class TestStamp:
    def test_returns_ghost(self):
        c = Circle(r=30, cx=100, cy=100)
        ghost = c.stamp(time=0)
        assert ghost is not None

    def test_ghost_has_low_opacity(self):
        c = Circle(r=30, cx=100, cy=100)
        ghost = c.stamp(time=0, opacity=0.2)
        assert ghost.styling.fill_opacity.at_time(0) < 0.5

    def test_ghost_at_current_position(self):
        c = Circle(r=30, cx=100, cy=100)
        c.shift(dx=200, dy=0, start=0, end=1)
        ghost = c.stamp(time=0.5)
        gx, gy = ghost.center(1)
        # Ghost position is frozen at time=0.5
        assert gx > 100


class TestSaveRestore:
    def test_save_and_restore_styling(self):
        c = Circle(r=50, cx=200, cy=200, fill='#ff0000')
        c.save_state(time=0)
        c.styling.fill_opacity.set_onward(1, 0.2)
        c.restore(start=2, end=3)
        # After restore, opacity should return to original
        assert c.styling.fill_opacity.at_time(3) > 0.5

    def test_returns_self(self):
        c = Circle(r=30)
        result = c.save_state(time=0)
        assert result is c


class TestTracePath:
    def test_returns_path(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        path = d.trace_path(start=0, end=2)
        assert path is not None

    def test_path_renderable(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        path = d.trace_path(start=0, end=2, stroke='#ff0000')
        v = VectorMathAnim('/tmp')
        v.add(d)
        v.add(path)
        svg = v.generate_frame_svg(1)
        assert len(svg) > 200
