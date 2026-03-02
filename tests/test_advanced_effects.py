"""Tests for advanced animation effects: homotopy, trail, cross_out, stamp,
reflect, apply_matrix, become, fade_transform, swap, transform_from_copy."""
from vectormation.objects import (
    Circle, Square, Text, Dot, VectorMathAnim,
)


class TestHomotopy:
    def test_applies_transformation(self):
        c = Circle(r=50, cx=500, cy=300)
        c.homotopy(lambda x, y, t: (x + 50 * t, y), start=0, end=1)
        cx_before, _ = c.center(0)
        cx_after, _ = c.center(1)
        assert abs(cx_after - cx_before - 50) < 10


class TestTrail:
    def test_correct_number_of_ghosts(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        ghosts = d.trail(start=0, end=2, n_copies=4)
        assert len(ghosts) == 4

    def test_ghosts_at_different_positions(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, dy=0, start=0, end=2)
        ghosts = d.trail(start=0, end=2, n_copies=3)
        positions = [g.center(2) for g in ghosts]
        # Ghosts should be at different positions along the path
        xs = [p[0] for p in positions]
        assert len(set(round(x, 1) for x in xs)) > 1


class TestCrossOut:
    def test_custom_color(self):
        t = Text(text='No', x=400, y=400)
        cross = t.cross_out(start=0, end=0.5, color='#00ff00')
        v = VectorMathAnim('/tmp')
        v.add(cross)
        svg = v.generate_frame_svg(0.5)
        assert 'rgb(0,255,0)' in svg or '0,255,0' in svg


class TestBecome:
    def test_copies_style(self):
        a = Circle(r=30, cx=100, cy=100, fill='#ff0000')
        b = Circle(r=30, cx=100, cy=100, fill='#00ff00')
        a.become(b, time=0)
        v = VectorMathAnim('/tmp')
        v.add(a)
        svg = v.generate_frame_svg(0)
        assert 'rgb(0,255,0)' in svg or 'rgb(0,128,0)' in svg or '0,255,0' in svg


class TestSwap:
    def test_swaps_positions(self):
        a = Circle(r=30, cx=100, cy=300)
        b = Circle(r=30, cx=400, cy=300)
        a.swap(a, b, start=0, end=1)
        ax_after, _ = a.center(1)
        bx_after, _ = b.center(1)
        assert abs(ax_after - 400) < 5
        assert abs(bx_after - 100) < 5


class TestTransformFromCopy:
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
    def test_ghost_has_low_opacity(self):
        c = Circle(r=30, cx=100, cy=100)
        ghost = c.stamp(time=0, opacity=0.2)
        assert ghost.styling.fill_opacity.at_time(0) < 0.5

    def test_ghost_at_current_position(self):
        c = Circle(r=30, cx=100, cy=100)
        c.shift(dx=200, dy=0, start=0, end=1)
        ghost = c.stamp(time=0.5)
        gx, _ = ghost.center(1)
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
