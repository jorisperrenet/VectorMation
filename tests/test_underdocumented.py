"""Tests for previously underdocumented classes: SampleSpace, Stamp, RoundedCornerPolygon, Wall."""
import math
import pytest
from vectormation.objects import (
    Circle, Star, Rectangle, Dot,
    SampleSpace, Stamp, RoundedCornerPolygon,
)
from vectormation._physics import Wall, Body, PhysicsSpace


# ── SampleSpace ─────────────────────────────────────────────────────────

class TestSampleSpace:
    def test_creation(self):
        ss = SampleSpace()
        svg = ss.to_svg(0)
        assert svg is not None

    def test_custom_size(self):
        ss = SampleSpace(width=300, height=200, x=100, y=100)
        svg = ss.to_svg(0)
        assert svg is not None

    def test_divide_horizontally(self):
        ss = SampleSpace()
        ss.divide_horizontally(0.5)
        svg = ss.to_svg(0)
        assert svg is not None

    def test_divide_horizontally_with_labels(self):
        ss = SampleSpace()
        ss.divide_horizontally(0.7, labels=('A', 'B'))
        svg = ss.to_svg(0)
        assert 'A' in svg
        assert 'B' in svg

    def test_divide_vertically(self):
        ss = SampleSpace()
        ss.divide_vertically(0.4)
        svg = ss.to_svg(0)
        assert svg is not None

    def test_divide_vertically_with_labels(self):
        ss = SampleSpace()
        ss.divide_vertically(0.3, labels=('Top', 'Bottom'))
        svg = ss.to_svg(0)
        assert svg is not None

    def test_divide_extreme_proportion_zero(self):
        ss = SampleSpace()
        ss.divide_horizontally(0.0)
        svg = ss.to_svg(0)
        assert svg is not None

    def test_divide_extreme_proportion_one(self):
        ss = SampleSpace()
        ss.divide_horizontally(1.0)
        svg = ss.to_svg(0)
        assert svg is not None

    def test_custom_colors(self):
        ss = SampleSpace()
        ss.divide_horizontally(0.5, colors=('#FF0000', '#0000FF'))
        svg = ss.to_svg(0)
        assert svg is not None

    def test_repr(self):
        ss = SampleSpace()
        assert 'SampleSpace' in repr(ss)

    def test_custom_styling(self):
        ss = SampleSpace(fill='#FF0000', stroke='#00FF00')
        svg = ss.to_svg(0)
        assert svg is not None


# ── Stamp ───────────────────────────────────────────────────────────────

class TestStamp:
    def test_basic(self):
        template = Circle(r=20, cx=0, cy=0, fill='#FF0000')
        pts = [(100, 100), (200, 200), (300, 300)]
        s = Stamp(template, pts)
        svg = s.to_svg(0)
        assert svg is not None

    def test_single_point(self):
        template = Dot(cx=0, cy=0, r=5)
        s = Stamp(template, [(500, 500)])
        svg = s.to_svg(0)
        assert svg is not None

    def test_many_points(self):
        template = Rectangle(width=20, height=20, x=-10, y=-10, fill='#58C4DD')
        pts = [(i * 50, i * 30) for i in range(10)]
        s = Stamp(template, pts)
        svg = s.to_svg(0)
        assert svg is not None

    def test_repr(self):
        template = Circle(r=10, cx=0, cy=0)
        s = Stamp(template, [(0, 0), (10, 10)])
        assert '2 copies' in repr(s)

    def test_with_star_template(self):
        template = Star(n=5, outer_radius=15, cx=0, cy=0, fill='#FFFF00')
        pts = [(100, 200), (300, 400)]
        s = Stamp(template, pts)
        svg = s.to_svg(0)
        assert svg is not None

    def test_fadein(self):
        template = Circle(r=10, cx=0, cy=0)
        s = Stamp(template, [(100, 100), (200, 200)])
        s.stagger_fadein(start=0, end=1)
        svg = s.to_svg(0.5)
        assert svg is not None

    def test_creation_time(self):
        template = Dot(cx=0, cy=0)
        s = Stamp(template, [(100, 100)], creation=5)
        svg = s.to_svg(0)
        # Before creation time, should still render (might be empty/invisible)
        assert svg is not None


# ── RoundedCornerPolygon ────────────────────────────────────────────────

class TestRoundedCornerPolygon:
    def test_triangle(self):
        p = RoundedCornerPolygon((100, 300), (300, 300), (200, 100), radius=20)
        svg = p.to_svg(0)
        assert svg is not None

    def test_square(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=15)
        svg = p.to_svg(0)
        assert svg is not None

    def test_pentagon(self):
        pts = [(200 + 80 * math.cos(math.radians(90 + i * 72)),
                200 + 80 * math.sin(math.radians(90 + i * 72))) for i in range(5)]
        p = RoundedCornerPolygon(*pts, radius=10)
        svg = p.to_svg(0)
        assert svg is not None

    def test_zero_radius(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=0)
        svg = p.to_svg(0)
        assert svg is not None

    def test_large_radius(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=100)
        svg = p.to_svg(0)
        assert svg is not None

    def test_custom_styling(self):
        p = RoundedCornerPolygon(
            (100, 100), (200, 50), (300, 100),
            radius=10, fill='#FF0000', stroke='#00FF00', stroke_width=5)
        svg = p.to_svg(0)
        assert svg is not None

    def test_two_points_degenerate(self):
        p = RoundedCornerPolygon((100, 100), (200, 200), radius=10)
        svg = p.to_svg(0)
        # Less than 3 points yields empty path
        assert svg is not None

    def test_fadein(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=15)
        p.fadein(0, 1)
        svg = p.to_svg(0.5)
        assert svg is not None

    def test_bbox(self):
        p = RoundedCornerPolygon(
            (100, 100), (300, 100), (300, 300), (100, 300),
            radius=15)
        x, y, w, h = p.bbox(0)
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

    def test_wall_collision(self):
        space = PhysicsSpace()
        ball = Circle(r=10, cx=50, cy=500, fill='#FF0000')
        b = Body(ball, vx=100, vy=0, mass=1)
        space.add(b)
        space.add_wall(x=200, restitution=0.8)
        space.simulate(duration=5)
        # Body's VObject should have been moved by simulation
        svg = ball.to_svg(3)
        assert svg is not None

    def test_wall_floor(self):
        space = PhysicsSpace(gravity=(0, 200))
        ball = Circle(r=15, cx=960, cy=100, fill='#00FF00')
        b = Body(ball, mass=1)
        space.add(b)
        space.add_wall(y=800)
        space.simulate(duration=3)
        svg = ball.to_svg(2)
        assert svg is not None

    def test_add_wall_with_wall_object(self):
        space = PhysicsSpace()
        w = Wall(x=500)
        returned = space.add_wall(w)
        assert returned is w
        assert w in space.walls
        assert len(space.walls) == 1
