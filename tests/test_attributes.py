"""Tests for the time-varying attribute system (Real, Coor, Color, etc.)."""
import math
import pytest

from vectormation.attributes import Real, Coor, Color, String, Tup, _wrap
import vectormation.easings as easings


class TestWrap:
    """Test the _wrap helper that builds interval-gated time functions."""

    def test_wrap_half_open_interval(self):
        outer = lambda t: 0
        inner = lambda t: 42
        f = _wrap(outer, inner, start=5)
        assert f(4) == 0
        assert f(5) == 42
        assert f(100) == 42

    def test_wrap_closed_interval_with_stay(self):
        outer = lambda t: -1
        inner = lambda t: t * 10
        f = _wrap(outer, inner, start=1, end=3, stay=True)
        assert f(0.5) == -1      # before interval
        assert f(1) == 10        # at start
        assert f(2) == 20        # midpoint
        assert f(3) == 30        # at end
        assert f(4) == 30        # after end, stays at f(end)

    def test_wrap_closed_interval_without_stay(self):
        outer = lambda t: -1
        inner = lambda t: t * 10
        f = _wrap(outer, inner, start=1, end=3, stay=False)
        assert f(4) == -1        # after end, reverts to outer

    def test_wrap_lincl_false(self):
        outer = lambda t: 0
        inner = lambda t: 1
        f = _wrap(outer, inner, start=5, lincl=False)
        assert f(5) == 0         # start excluded
        assert f(5.001) == 1

    def test_wrap_rincl_false(self):
        outer = lambda t: 0
        inner = lambda t: 1
        f = _wrap(outer, inner, start=1, end=3, rincl=False)
        assert f(2) == 1         # inside
        assert f(3) == 0         # end excluded


class TestReal:

    def test_initial_value(self):
        r = Real(0, 5)
        assert r.at_time(0) == 5
        assert r.at_time(10) == 5

    def test_before_creation_is_zero(self):
        r = Real(2, 5)
        assert r.at_time(0) == 0
        assert r.at_time(1.9) == 0
        assert r.at_time(2) == 5

    def test_set_overrides_on_interval(self):
        r = Real(0, 10)
        r.set(1, 3, lambda t: t * 100, stay=False)
        assert r.at_time(0.5) == 10      # before interval
        assert r.at_time(2) == 200        # inside interval
        assert r.at_time(4) == 10         # after interval (no stay)

    def test_set_with_stay(self):
        r = Real(0, 10)
        r.set(1, 3, lambda t: t * 100, stay=True)
        assert r.at_time(4) == 300        # stays at f(3)

    def test_add_accumulates(self):
        r = Real(0, 10)
        r.add(1, 3, lambda t: 5)
        assert r.at_time(0.5) == 10       # before: original
        assert r.at_time(2) == 15         # during: 10 + 5

    def test_set_onward_permanent(self):
        r = Real(0, 10)
        r.set_onward(5, 42)
        assert r.at_time(3) == 10
        assert r.at_time(5) == 42
        assert r.at_time(100) == 42

    def test_set_onward_with_function(self):
        r = Real(0, 0)
        r.set_onward(0, lambda t: t ** 2)
        assert r.at_time(3) == 9

    def test_add_onward(self):
        r = Real(0, 10)
        r.add_onward(2, 5)
        assert r.at_time(1) == 10
        assert r.at_time(3) == 15

    def test_set_at_point(self):
        r = Real(0, 0)
        r.set_at(5, 99)
        assert r.at_time(5) == 99
        assert r.at_time(5 + 1e-10) == pytest.approx(99)  # within eps
        assert r.at_time(6) == 0          # outside eps

    def test_move_to_interpolation(self):
        r = Real(0, 0)
        r.move_to(0, 1, 100, easing=easings.linear)
        assert r.at_time(0) == pytest.approx(0)
        assert r.at_time(0.5) == pytest.approx(50)
        assert r.at_time(1) == pytest.approx(100)

    def test_move_to_stays_after_end(self):
        r = Real(0, 0)
        r.move_to(0, 1, 100, stay=True, easing=easings.linear)
        assert r.at_time(5) == pytest.approx(100)

    def test_move_to_zero_duration_is_instant(self):
        r = Real(0, 0)
        r.move_to(2, 2, 100)  # dur=0
        assert r.at_time(1) == 0
        assert r.at_time(2) == 100

    def test_multiple_set_operations_last_wins(self):
        r = Real(0, 0)
        r.set_onward(0, 10)
        r.set_onward(5, 20)
        assert r.at_time(3) == 10
        assert r.at_time(5) == 20

    def test_interpolate_linear(self):
        a = Real(0, 0)
        b = Real(0, 100)
        c = a.interpolate(b, 0, 1, easing=easings.linear)
        assert c.at_time(0) == pytest.approx(0)
        assert c.at_time(0.5) == pytest.approx(50)
        assert c.at_time(1) == pytest.approx(100)

    def test_apply_transforms_value(self):
        r = Real(0, 5)
        doubled = r.apply(lambda x: x * 2)
        assert doubled.at_time(0) == 10

    def test_set_to_copies(self):
        a = Real(0, 42)
        b = Real(0, 0)
        b.set_to(a)
        assert b.at_time(0) == 42

    def test_last_change_tracks_operations(self):
        r = Real(0, 0)
        assert r.last_change == 0
        r.move_to(0, 5, 100)
        assert r.last_change == 5
        r.set_onward(10, 0)
        assert r.last_change == 10


class TestCoor:

    def test_initial_position(self):
        c = Coor(0, (100, 200))
        assert c.at_time(0) == (100, 200)

    def test_before_creation_is_origin(self):
        c = Coor(2, (100, 200))
        assert c.at_time(0) == (0, 0)
        assert c.at_time(2) == (100, 200)

    def test_add_onward_with_tuple(self):
        c = Coor(0, (10, 20))
        c.add_onward(1, (5, -5))
        assert c.at_time(0) == (10, 20)
        assert c.at_time(1) == (15, 15)

    def test_add_onward_with_function(self):
        c = Coor(0, (0, 0))
        c.add_onward(0, lambda t: (t, t * 2))
        assert c.at_time(3) == (3, 6)

    def test_move_to_interpolation(self):
        c = Coor(0, (0, 0))
        c.move_to(0, 1, (100, 200), easing=easings.linear)
        x, y = c.at_time(0.5)
        assert x == pytest.approx(50)
        assert y == pytest.approx(100)

    def test_move_to_zero_duration(self):
        c = Coor(0, (0, 0))
        c.move_to(1, 1, (50, 50))  # instant
        assert c.at_time(0) == (0, 0)
        assert c.at_time(1) == (50, 50)

    def test_rotate_around_90_degrees(self):
        # Point at (100, 0) rotated 90° CCW around origin
        # base_angle = atan2(0, 100) = 0
        # phi = 0 + radians(90) = pi/2
        # result = (100*cos(pi/2), 100*sin(pi/2)) = (0, 100)
        c = Coor(0, (100, 0))
        c.rotate_around(0, 1, (0, 0), 90, clockwise=False)
        x, y = c.at_time(1)
        assert x == pytest.approx(0, abs=1e-6)
        assert y == pytest.approx(100, abs=1e-6)

    def test_rotate_around_zero_duration_does_nothing(self):
        c = Coor(0, (100, 0))
        c.rotate_around(5, 5, (0, 0), 90)  # dur=0
        assert c.at_time(5) == (100, 0)

    def test_add_on_interval(self):
        c = Coor(0, (10, 10))
        c.add(1, 3, lambda t: (5, 5))
        assert c.at_time(0) == (10, 10)
        assert c.at_time(2) == (15, 15)
        # After interval, reverts
        assert c.at_time(4) == (10, 10)


class TestColor:

    def test_parse_hex_short(self):
        c = Color(0, '#fff')
        assert c.at_time(0) == 'rgb(255,255,255)'

    def test_parse_hex_6digit(self):
        c = Color(0, '#ff0000')
        assert c.at_time(0) == 'rgb(255,0,0)'

    def test_parse_hex_8digit_rgba(self):
        c = Color(0, '#ff000080')
        assert c.at_time(0) == 'rgba(255,0,0,128)'

    def test_parse_tuple_rgb(self):
        c = Color(0, (100, 200, 50))
        assert c.at_time(0) == 'rgb(100,200,50)'

    def test_parse_named_color(self):
        c = Color(0, 'red')
        val = c.at_time(0)
        assert 'rgb' in val

    def test_interpolate_rgb(self):
        red = Color(0, '#ff0000')
        blue = Color(0, '#0000ff')
        mid = red.interpolate(blue, 0, 1, easing=easings.linear)
        val = mid.time_func(0.5)
        # At midpoint: R=127.5, G=0, B=127.5
        assert val[0] == pytest.approx(127.5)
        assert val[1] == pytest.approx(0)
        assert val[2] == pytest.approx(127.5)

    def test_interpolate_endpoints(self):
        red = Color(0, '#ff0000')
        blue = Color(0, '#0000ff')
        mid = red.interpolate(blue, 0, 1, easing=easings.linear)
        start = mid.time_func(0)
        end = mid.time_func(1)
        assert start == pytest.approx((255, 0, 0))
        assert end == pytest.approx((0, 0, 255))

    def test_interpolate_hsl_goes_through_hue(self):
        red = Color(0, '#ff0000')
        blue = Color(0, '#0000ff')
        mid = red.interpolate(blue, 0, 1, color_space='hsl')
        # HSL interpolation should produce different midpoint than RGB
        hsl_mid = mid.time_func(0.5)
        rgb_only = red.interpolate(blue, 0, 1, easing=easings.linear)
        rgb_mid = rgb_only.time_func(0.5)
        # The two midpoints should differ (HSL goes through hue wheel)
        assert hsl_mid != pytest.approx(rgb_mid, abs=1)

    def test_set_onward_changes_color(self):
        c = Color(0, '#ff0000')
        c.set_onward(1, '#00ff00')
        assert c.at_time(0) == 'rgb(255,0,0)'
        assert c.at_time(1) == 'rgb(0,255,0)'

    def test_creation_must_be_number(self):
        with pytest.raises(TypeError):
            Color('not_a_number', '#000')

    def test_invalid_hex_length_raises(self):
        with pytest.raises(ValueError):
            Color(0, '#12345')  # 5 hex digits

    def test_invalid_tuple_length_raises(self):
        with pytest.raises(ValueError):
            Color(0, (1, 2))  # not 3 or 4

    def test_apply_transforms_color(self):
        c = Color(0, '#ff0000')
        inverted = c.apply(lambda rgb: (255 - rgb[0], 255 - rgb[1], 255 - rgb[2]))
        val = inverted.time_func(0)
        assert val == (0, 255, 255)


class TestString:

    def test_initial_value(self):
        s = String(0, 'hello')
        assert s.at_time(0) == 'hello'

    def test_before_creation_is_empty(self):
        s = String(2, 'hello')
        assert s.at_time(0) == ''
        assert s.at_time(2) == 'hello'

    def test_set_onward(self):
        s = String(0, 'hello')
        s.set_onward(1, 'world')
        assert s.at_time(0) == 'hello'
        assert s.at_time(1) == 'world'


class TestTup:

    def test_initial_value(self):
        t = Tup(0, (1, 2, 3))
        assert t.at_time(0) == (1, 2, 3)

    def test_before_creation_is_zeros(self):
        t = Tup(2, (10, 20, 30))
        assert t.at_time(0) == (0, 0, 0)

    def test_add_element_wise(self):
        t = Tup(0, (10, 20, 30))
        t.add(0, 1, (1, 2, 3))
        assert t.at_time(0.5) == pytest.approx((11, 22, 33))

    def test_interpolate(self):
        a = Tup(0, (0, 0, 0))
        b = Tup(0, (10, 20, 30))
        c = a.interpolate(b, 0, 1, easing=easings.linear)
        assert c.at_time(0.5) == pytest.approx((5, 10, 15))
