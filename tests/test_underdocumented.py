"""Tests for previously underdocumented classes: SampleSpace, Stamp, RoundedCornerPolygon, Wall."""
import pytest
from vectormation.objects import (
    Circle,
    SampleSpace, Stamp, RoundedCornerPolygon,
)
from vectormation._physics import Wall, Body, PhysicsSpace


# ── SampleSpace ─────────────────────────────────────────────────────────

class TestSampleSpace:
    def test_divide_horizontally_with_labels(self):
        ss = SampleSpace()
        ss.divide_horizontally(0.7, labels=('A', 'B'))
        svg = ss.to_svg(0)
        assert 'A' in svg
        assert 'B' in svg


# ── Stamp ───────────────────────────────────────────────────────────────

class TestStamp:
    def test_repr(self):
        template = Circle(r=10, cx=0, cy=0)
        s = Stamp(template, [(0, 0), (10, 10)])
        assert '2 copies' in repr(s)


# ── RoundedCornerPolygon ────────────────────────────────────────────────

class TestRoundedCornerPolygon:
    def test_bbox(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=15)
        _, _, w, h = p.bbox(0)
        assert w > 0 and h > 0


# ── Wall (physics) ──────────────────────────────────────────────────────

class TestWall:
    def test_vertical_wall(self):
        w = Wall(x=100)
        assert w.x == 100
        assert w.y is None

    def test_horizontal_wall(self):
        w = Wall(y=500)
        assert w.y == 500
        assert w.x is None

    def test_both_axes(self):
        w = Wall(x=100, y=200)
        assert w.x == 100
        assert w.y == 200

    def test_no_axes_raises(self):
        with pytest.raises(ValueError):
            Wall()

    def test_repr_vertical(self):
        w = Wall(x=50)
        assert 'x=50' in repr(w)

    def test_repr_horizontal(self):
        w = Wall(y=300)
        assert 'y=300' in repr(w)

    def test_custom_restitution(self):
        w = Wall(x=100, restitution=0.5)
        assert w.restitution == 0.5

    def test_wall_collision_reverses_velocity(self):
        space = PhysicsSpace()
        ball = Circle(r=10, cx=50, cy=500, fill='#FF0000')
        b = Body(ball, vx=100, vy=0, mass=1)
        space.add(b)
        space.add_wall(x=200, restitution=0.8)
        space.simulate(duration=5)
        # Ball should have bounced back from wall at x=200
        cx, _ = ball.center(3)
        assert cx < 200

    def test_wall_floor_prevents_falling_through(self):
        space = PhysicsSpace(gravity=(0, 200))
        ball = Circle(r=15, cx=960, cy=100, fill='#00FF00')
        b = Body(ball, mass=1)
        space.add(b)
        space.add_wall(y=800)
        space.simulate(duration=3)
        # Ball should not have fallen past the wall at y=800
        _, cy = ball.center(2)
        assert cy <= 800

    def test_add_wall_with_wall_object(self):
        space = PhysicsSpace()
        w = Wall(x=500)
        space.add_wall(w)
        assert space._wall_count == 1
