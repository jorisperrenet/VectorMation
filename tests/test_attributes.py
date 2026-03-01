"""Tests for vectormation.attributes: Real, Coor, Color, Tup, String."""
import pytest
from vectormation.attributes import Real, Coor, Color, Tup, String
import vectormation.easings as easings


class TestReal:
    def test_constant_value(self):
        r = Real(0, start_val=5)
        assert r.at_time(0) == 5
        assert r.at_time(10) == 5

    def test_before_creation_is_zero(self):
        r = Real(1, start_val=5)
        assert r.at_time(0) == 0
        assert r.at_time(1) == 5

    def test_set(self):
        r = Real(0, start_val=0)
        r.set(1, 2, lambda t: t * 10)
        assert r.at_time(0) == 0
        assert r.at_time(1.5) == 15
        assert r.at_time(3) == 0  # After set range, returns to original

    def test_set_stay(self):
        r = Real(0, start_val=0)
        r.set(1, 2, lambda t: t * 10, stay=True)
        assert r.at_time(3) == 20  # Stays at end value

    def test_add_onward(self):
        r = Real(0, start_val=10)
        r.add_onward(1, 5)
        assert r.at_time(0) == 10
        assert r.at_time(1) == 15
        assert r.at_time(5) == 15

    def test_move_to(self):
        r = Real(0, start_val=0)
        r.move_to(0, 1, 100, easing=easings.linear)
        assert r.at_time(0) == pytest.approx(0, abs=1)
        assert r.at_time(0.5) == pytest.approx(50, abs=1)
        assert r.at_time(1) == pytest.approx(100, abs=1)
        # stay=True by default
        assert r.at_time(2) == pytest.approx(100, abs=1)

    def test_last_change(self):
        r = Real(0, start_val=5)
        assert r.last_change == 0
        r.move_to(1, 3, 10)
        assert r.last_change == 3

    def test_interpolate(self):
        a = Real(0, start_val=0)
        b = Real(0, start_val=100)
        result = a.interpolate(b, 0, 1, easing=easings.linear)
        assert result.at_time(0) == pytest.approx(0)
        assert result.at_time(0.5) == pytest.approx(50)
        assert result.at_time(1) == pytest.approx(100)

    def test_set_onward(self):
        r = Real(0, start_val=5)
        r.set_onward(2, 20)
        assert r.at_time(1) == 5
        assert r.at_time(2) == 20
        assert r.at_time(10) == 20


class TestCoor:
    def test_constant(self):
        c = Coor(0, (100, 200))
        assert c.at_time(0) == (100, 200)

    def test_move_to(self):
        c = Coor(0, (0, 0))
        c.move_to(0, 1, (100, 200), easing=easings.linear)
        pos = c.at_time(0.5)
        assert pos[0] == pytest.approx(50, abs=1)
        assert pos[1] == pytest.approx(100, abs=1)
        end = c.at_time(1)
        assert end[0] == pytest.approx(100, abs=1)
        assert end[1] == pytest.approx(200, abs=1)

    def test_add_onward(self):
        c = Coor(0, (10, 20))
        c.add_onward(1, (5, 10))
        assert c.at_time(0) == (10, 20)
        pos = c.at_time(1)
        assert pos[0] == pytest.approx(15)
        assert pos[1] == pytest.approx(30)

    def test_along_path(self):
        """Test that along_path moves the coordinate along a simple line path."""
        c = Coor(0, (0, 0))
        # A straight horizontal line from (0,0) to (100,0)
        c.along_path(0, 1, 'M 0,0 L 100,0', easing=easings.linear)
        start = c.at_time(0)
        assert start[0] == pytest.approx(0, abs=1)
        assert start[1] == pytest.approx(0, abs=1)
        end = c.at_time(1)
        assert end[0] == pytest.approx(100, abs=1)
        assert end[1] == pytest.approx(0, abs=1)


class TestColor:
    def test_hex_color(self):
        c = Color(0, '#ff0000')
        assert c.at_time(0) == 'rgb(255,0,0)'

    def test_short_hex_color(self):
        c = Color(0, '#f00')
        assert c.at_time(0) == 'rgb(255,0,0)'

    def test_color_name(self):
        c = Color(0, 'white')
        assert c.at_time(0) == 'rgb(255,255,255)'

    def test_rgb_tuple(self):
        c = Color(0, (128, 64, 32))
        assert c.at_time(0) == 'rgb(128,64,32)'

    def test_interpolate_rgb(self):
        a = Color(0, '#000000')
        b = Color(0, '#ffffff')
        result = a.interpolate(b, 0, 1, easing=easings.linear)
        mid = result.time_func(0.5)
        # Should be approximately (127.5, 127.5, 127.5)
        assert mid[0] == pytest.approx(127.5, abs=1)
        assert mid[1] == pytest.approx(127.5, abs=1)
        assert mid[2] == pytest.approx(127.5, abs=1)

    def test_interpolate_hsl(self):
        a = Color(0, '#ff0000')  # Red
        b = Color(0, '#00ff00')  # Green
        result = a.interpolate(b, 0, 1, easing=easings.linear, color_space='hsl')
        # The midpoint in HSL should produce a valid color
        mid = result.time_func(0.5)
        assert len(mid) == 3
        assert all(0 <= v <= 255 for v in mid)

    def test_interpolate_hsl_endpoints(self):
        a = Color(0, '#ff0000')
        b = Color(0, '#0000ff')
        result = a.interpolate_hsl(b, 0, 1, easing=easings.linear)
        start = result.time_func(0)
        assert start[0] == pytest.approx(255, abs=1)
        assert start[1] == pytest.approx(0, abs=1)
        assert start[2] == pytest.approx(0, abs=1)
        end = result.time_func(1)
        assert end[0] == pytest.approx(0, abs=1)
        assert end[1] == pytest.approx(0, abs=1)
        assert end[2] == pytest.approx(255, abs=1)


class TestRealAddAt:
    def test_add_at_increments(self):
        r = Real(0, start_val=10)
        r.add_at(1, 5)
        assert r.at_time(1) == 15
        assert r.at_time(0) == 10  # Unchanged elsewhere

    def test_add_at_negative(self):
        r = Real(0, start_val=10)
        r.add_at(1, -3)
        assert r.at_time(1) == 7


class TestRealSetAtEpsilon:
    def test_set_at_exact(self):
        r = Real(0, start_val=0)
        r.set_at(1, 42)
        assert r.at_time(1) == 42

    def test_set_at_epsilon_match(self):
        r = Real(0, start_val=0)
        r.set_at(1, 42, eps=1e-6)
        assert r.at_time(1 + 1e-7) == 42

    def test_set_at_outside_epsilon(self):
        r = Real(0, start_val=5)
        r.set_at(1, 42, eps=1e-9)
        assert r.at_time(1 + 1e-6) == 5


class TestRealSetTo:
    def test_set_to_follows_other(self):
        a = Real(0, start_val=10)
        b = Real(0, start_val=0)
        b.set_to(a)
        assert b.at_time(0) == 10
        a.set_onward(1, 20)
        assert b.at_time(1) == 20


class TestTup:
    def test_constant_value(self):
        t = Tup(0, (1, 2, 3))
        assert t.at_time(0) == (1, 2, 3)

    def test_set(self):
        t = Tup(0, (0, 0))
        t.set(1, 2, lambda x: (x * 10, x * 20))
        assert t.at_time(1.5) == (15, 30)

    def test_add(self):
        t = Tup(0, (10, 20))
        t.add(1, 2, (5, 10))
        result = t.at_time(1)
        assert result[0] == pytest.approx(15)
        assert result[1] == pytest.approx(30)

    def test_interpolate(self):
        a = Tup(0, (0, 0))
        b = Tup(0, (100, 200))
        result = a.interpolate(b, 0, 1, easing=easings.linear)
        mid = result.at_time(0.5)
        assert mid[0] == pytest.approx(50)
        assert mid[1] == pytest.approx(100)


class TestString:
    def test_constant_value(self):
        s = String(0, 'hello')
        assert s.at_time(0) == 'hello'

    def test_before_creation_is_empty(self):
        s = String(1, 'hello')
        assert s.at_time(0) == ''

    def test_set_onward(self):
        s = String(0, 'hello')
        s.set_onward(1, 'world')
        assert s.at_time(0) == 'hello'
        assert s.at_time(1) == 'world'


class TestColorEdgeCases:
    def test_rgba_tuple(self):
        c = Color(0, (128, 64, 32, 200))
        assert c.at_time(0) == 'rgba(128,64,32,200)'

    def test_hex_rgba(self):
        c = Color(0, '#ff000080')
        assert c.use == 'rgba'
        result = c.at_time(0)
        assert 'rgba' in result

    def test_url_color(self):
        c = Color(0, 'url(#gradient1)')
        assert c.at_time(0) == 'url(#gradient1)'

    def test_invalid_color_raises(self):
        with pytest.raises(ValueError):
            Color(0, '#xyz')

    def test_color_set_onward(self):
        c = Color(0, '#ff0000')
        c.set_onward(1, '#00ff00')
        assert c.at_time(0) == 'rgb(255,0,0)'
        assert c.at_time(1) == 'rgb(0,255,0)'

    def test_color_set(self):
        c = Color(0, '#ff0000')
        c.set(1, 2, lambda t: (0, 255, 0))
        assert c.at_time(0) == 'rgb(255,0,0)'
        mid = c.time_func(1.5)
        assert mid == (0, 255, 0)


class TestRepr:
    """Test __repr__ for all attribute types."""
    def test_real_repr(self):
        r = Real(0, 42)
        s = repr(r)
        assert 'Real' in s
        assert '42' in s

    def test_real_repr_float(self):
        r = Real(0, 3.14)
        s = repr(r)
        assert 'Real' in s
        assert '3.14' in s

    def test_tup_repr(self):
        t = Tup(0, (1, 2, 3))
        s = repr(t)
        assert 'Tup' in s
        assert '(1, 2, 3)' in s

    def test_coor_repr(self):
        c = Coor(0, (100.0, 200.0))
        s = repr(c)
        assert 'Coor' in s
        assert '100.0' in s
        assert '200.0' in s

    def test_string_repr(self):
        s = String(0, 'hello')
        r = repr(s)
        assert 'String' in r
        assert 'hello' in r

    def test_string_repr_empty(self):
        s = String(0, '')
        r = repr(s)
        assert 'String' in r

    def test_color_repr_hex(self):
        c = Color(0, '#ff0000')
        r = repr(c)
        assert 'Color' in r
        assert '255' in r

    def test_color_repr_tuple(self):
        c = Color(0, (0, 128, 255))
        r = repr(c)
        assert 'Color' in r
        assert '128' in r

    def test_real_repr_after_change(self):
        """Repr should reflect the latest value."""
        r = Real(0, 10)
        r.set_onward(1, 99)
        s = repr(r)
        assert '99' in s
