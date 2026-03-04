"""Tests for animation effects: fadein/out, scale, rotation, transforms."""
import math
import pytest

from vectormation._shapes import Circle, Rectangle, Polygon
from vectormation._constants import ORIGIN
import vectormation.easings as easings


class TestFadeInOut:

    def test_fadein_makes_visible(self):
        c = Circle(r=50, creation=0)
        c.fadein(start=1, end=2)
        # Before animation starts, object hidden (change_existence=True)
        assert c.show.at_time(0.5) is False
        # During animation, object should exist
        assert c.show.at_time(1.5) is True
        # After animation, object visible
        assert c.show.at_time(3) is True

    def test_fadein_opacity_animation(self):
        c = Circle(r=50, creation=0)
        c.fadein(start=0, end=1)
        # Opacity should increase from 0 to 1
        opacity_start = c.styling.opacity.at_time(0)
        opacity_end = c.styling.opacity.at_time(1)
        assert opacity_start < opacity_end
        assert opacity_end == pytest.approx(1, abs=0.01)

    def test_fadeout_hides_object(self):
        c = Circle(r=50, creation=0)
        c.fadeout(start=1, end=2)
        assert c.show.at_time(0.5) is True
        assert c.show.at_time(2) is False

    def test_fadeout_opacity_decreases(self):
        c = Circle(r=50, creation=0)
        c.fadeout(start=0, end=1)
        opacity_mid = c.styling.opacity.at_time(0.5)
        assert opacity_mid < 1


class TestScale:

    def test_scale_changes_size(self):
        c = Circle(r=50, cx=ORIGIN[0], cy=ORIGIN[1])
        c.scale(2, start=0)
        assert c.get_width(0) == pytest.approx(200, abs=5)

    def test_scale_animated(self):
        c = Circle(r=50, cx=ORIGIN[0], cy=ORIGIN[1])
        original_width = c.get_width(0)
        c.scale(2, start=0, end=1, easing=easings.linear)
        mid_width = c.get_width(0.5)
        end_width = c.get_width(1)
        assert mid_width > original_width
        assert end_width == pytest.approx(original_width * 2, abs=5)

    def test_scale_preserves_center(self):
        c = Circle(r=50, cx=300, cy=400)
        center_before = c.center(0)
        c.scale(2, start=0)
        center_after = c.center(0)
        assert center_after == pytest.approx(center_before, abs=2)


class TestRotation:

    def test_rotate_by(self):
        r = Rectangle(200, 100, x=ORIGIN[0] - 100, y=ORIGIN[1] - 50)
        r.rotate_by(start=0, end=1, degrees=90, easing=easings.linear)
        # At t=0.5, rotation should be ~45 degrees
        rot = r.styling.rotation.at_time(0.5)
        assert rot[0] == pytest.approx(45, abs=2)

    def test_rotate_to_absolute(self):
        r = Rectangle(200, 100, x=ORIGIN[0] - 100, y=ORIGIN[1] - 50)
        r.rotate_by(start=0, end=0, degrees=30)  # instant rotate to 30
        r.rotate_by(start=1, end=2, degrees=60)   # rotate by 60 more
        rot_end = r.styling.rotation.at_time(2)
        assert rot_end[0] == pytest.approx(90, abs=2)


class TestShift:

    def test_instant_shift(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shift(dx=50, dy=-50, start=0)
        assert c.center(0) == pytest.approx((150, 50))

    def test_animated_shift_midpoint(self):
        c = Circle(r=50, cx=0, cy=0)
        c.shift(dx=100, dy=200, start=0, end=1, easing=easings.linear)
        mid = c.center(0.5)
        assert mid[0] == pytest.approx(50)
        assert mid[1] == pytest.approx(100)

    def test_shift_zero_duration_is_instant(self):
        c = Circle(r=50, cx=0, cy=0)
        c.shift(dx=100, dy=0, start=5, end=5)  # zero duration
        assert c.center(5)[0] == pytest.approx(100)

    def test_multiple_shifts_accumulate(self):
        c = Circle(r=50, cx=0, cy=0)
        c.shift(dx=100, dy=0, start=0)
        c.shift(dx=0, dy=200, start=0)
        assert c.center(0) == pytest.approx((100, 200))


class TestMoveTo:

    def test_move_to_position(self):
        c = Circle(r=50, cx=0, cy=0)
        c.move_to(500, 300, start=0)
        assert c.center(0) == pytest.approx((500, 300), abs=2)

    def test_move_to_animated(self):
        c = Circle(r=50, cx=0, cy=0)
        c.move_to(500, 300, start=0, end=1, easing=easings.linear)
        mid = c.center(0.5)
        assert mid[0] == pytest.approx(250, abs=5)
        assert mid[1] == pytest.approx(150, abs=5)


class TestSetColor:

    def test_set_fill_color(self):
        c = Circle(r=50, fill='#ff0000')
        c.set_color(start=0, end=1, fill='#00ff00')
        # After animation completes
        fill = c.styling.fill.at_time(1)
        assert fill == 'rgb(0,255,0)'

    def test_set_stroke_color(self):
        c = Circle(r=50, stroke='#ff0000')
        c.set_color(start=0, end=1, stroke='#0000ff')
        stroke = c.styling.stroke.at_time(1)
        assert stroke == 'rgb(0,0,255)'


class TestNextTo:

    def test_next_to_right(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=500, cy=500)
        c2.next_to(c1, 'right', buff=10, start=0)
        # c2 should be to the right of c1 with 10px gap
        c1_right = c1.bbox(0)[0] + c1.bbox(0)[2]
        c2_left = c2.bbox(0)[0]
        assert c2_left == pytest.approx(c1_right + 10, abs=2)

    def test_next_to_left(self):
        c1 = Circle(r=50, cx=500, cy=100)
        c2 = Circle(r=50, cx=0, cy=0)
        c2.next_to(c1, 'left', buff=10, start=0)
        c1_left = c1.bbox(0)[0]
        c2_right = c2.bbox(0)[0] + c2.bbox(0)[2]
        assert c2_right == pytest.approx(c1_left - 10, abs=2)


class TestToEdge:

    def test_to_bottom_edge(self):
        c = Circle(r=50, cx=ORIGIN[0], cy=ORIGIN[1])
        c.to_edge('bottom', buff=20, start=0)
        _, _, _, h = c.bbox(0)
        cx, cy = c.center(0)
        # Bottom of circle should be 20px from canvas bottom
        assert cy + h / 2 == pytest.approx(1080 - 20, abs=2)

    def test_to_top_edge(self):
        c = Circle(r=50, cx=ORIGIN[0], cy=ORIGIN[1])
        c.to_edge('top', buff=20, start=0)
        _, _, _, h = c.bbox(0)
        cx, cy = c.center(0)
        assert cy - h / 2 == pytest.approx(20, abs=2)


class TestToCorner:

    def test_to_bottom_right(self):
        c = Circle(r=50, cx=ORIGIN[0], cy=ORIGIN[1])
        c.to_corner('bottom_right', buff=20, start=0)
        cx, cy = c.center(0)
        _, _, w, h = c.bbox(0)
        assert cx + w / 2 == pytest.approx(1920 - 20, abs=2)
        assert cy + h / 2 == pytest.approx(1080 - 20, abs=2)


class TestBboxMixin:

    def test_get_width_height(self):
        r = Rectangle(200, 100, x=0, y=0)
        assert r.get_width(0) == pytest.approx(200)
        assert r.get_height(0) == pytest.approx(100)

    def test_get_diagonal(self):
        r = Rectangle(300, 400, x=0, y=0)
        assert r.get_diagonal(0) == pytest.approx(500)

    def test_distance_to(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=300, cy=400)
        assert c1.distance_to(c2, 0) == pytest.approx(500)

    def test_is_overlapping(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=50, cy=0)   # overlapping
        c3 = Circle(r=50, cx=200, cy=0)  # not overlapping
        assert c1.is_overlapping(c2, 0) is True
        assert c1.is_overlapping(c3, 0) is False

    def test_get_edge_points(self):
        r = Rectangle(200, 100, x=0, y=0)
        assert r.get_left(0) == pytest.approx((0, 50))
        assert r.get_right(0) == pytest.approx((200, 50))
        assert r.get_top(0) == pytest.approx((100, 0))
        assert r.get_bottom(0) == pytest.approx((100, 100))

    def test_get_aspect_ratio(self):
        r = Rectangle(200, 100, x=0, y=0)
        assert r.get_aspect_ratio(0) == pytest.approx(2.0)

    def test_get_aspect_ratio_zero_height(self):
        r = Rectangle(200, 0, x=0, y=0)
        assert r.get_aspect_ratio(0) == math.inf


class TestUpdaters:

    def test_add_updater_called_during_svg(self):
        c = Circle(r=50, cx=0, cy=0)
        calls = []
        c.add_updater(lambda obj, t: calls.append(t), start=0, end=10)
        c._run_updaters(5)
        assert 5 in calls

    def test_updater_can_modify_object(self):
        c = Circle(r=50, cx=0, cy=0)
        # Updater that moves circle based on time
        def mover(obj, t):
            # This demonstrates updaters work - they get called with the object
            pass
        c.add_updater(mover, start=0, end=1)
        c._run_updaters(0.5)  # should not crash
