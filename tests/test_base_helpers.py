"""Tests for vectormation._base_helpers: interpolation, direction normalization, clipping."""
import pytest
import vectormation.easings as easings
from vectormation._base_helpers import (
    _clamp01, _lerp, _ramp, _ramp_down, _lerp_point,
    _clip_reveal, _clip_hide,
    _norm_dir, _norm_edge, _coords_of, _set_attr,
)
from vectormation._constants import UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR


class TestClamp01:
    def test_in_range(self):
        assert _clamp01(0.5) == 0.5

    def test_below(self):
        assert _clamp01(-0.5) == 0.0

    def test_above(self):
        assert _clamp01(1.5) == 1.0

    def test_at_zero(self):
        assert _clamp01(0.0) == 0.0

    def test_at_one(self):
        assert _clamp01(1.0) == 1.0


class TestLerp:
    def test_start(self):
        f = _lerp(0, 1, 10, 20, easings.linear)
        assert f(0) == pytest.approx(10)

    def test_end(self):
        f = _lerp(0, 1, 10, 20, easings.linear)
        assert f(1) == pytest.approx(20)

    def test_midpoint(self):
        f = _lerp(0, 1, 0, 100, easings.linear)
        assert f(0.5) == pytest.approx(50)

    def test_offset_start(self):
        f = _lerp(2, 1, 0, 100, easings.linear)
        assert f(2) == pytest.approx(0)
        assert f(3) == pytest.approx(100)

    def test_negative_values(self):
        f = _lerp(0, 1, -50, 50, easings.linear)
        assert f(0.5) == pytest.approx(0)


class TestRamp:
    def test_start(self):
        f = _ramp(0, 1, 100, easings.linear)
        assert f(0) == pytest.approx(0)

    def test_end(self):
        f = _ramp(0, 1, 100, easings.linear)
        assert f(1) == pytest.approx(100)

    def test_midpoint(self):
        f = _ramp(0, 1, 50, easings.linear)
        assert f(0.5) == pytest.approx(25)


class TestRampDown:
    def test_start(self):
        f = _ramp_down(0, 1, 100, easings.linear)
        assert f(0) == pytest.approx(100)

    def test_end(self):
        f = _ramp_down(0, 1, 100, easings.linear)
        assert f(1) == pytest.approx(0)

    def test_midpoint(self):
        f = _ramp_down(0, 1, 50, easings.linear)
        assert f(0.5) == pytest.approx(25)


class TestLerpPoint:
    def test_start(self):
        f = _lerp_point(0, 1, (0, 0), (100, 200), easings.linear)
        x, y = f(0)
        assert x == pytest.approx(0)
        assert y == pytest.approx(0)

    def test_end(self):
        f = _lerp_point(0, 1, (0, 0), (100, 200), easings.linear)
        x, y = f(1)
        assert x == pytest.approx(100)
        assert y == pytest.approx(200)

    def test_midpoint(self):
        f = _lerp_point(0, 1, (10, 20), (30, 40), easings.linear)
        x, y = f(0.5)
        assert x == pytest.approx(20)
        assert y == pytest.approx(30)


class TestClipRevealHide:
    def test_reveal_start_is_clipped(self):
        tmpl = lambda pct: f'inset({pct}%)'
        f = _clip_reveal(tmpl, 0, 1, easings.linear)
        result = f(0)
        assert '100' in result

    def test_reveal_end_is_visible(self):
        tmpl = lambda pct: f'inset({pct}%)'
        f = _clip_reveal(tmpl, 0, 1, easings.linear)
        result = f(1)
        assert '0' in result

    def test_hide_start_is_visible(self):
        tmpl = lambda pct: f'inset({pct}%)'
        f = _clip_hide(tmpl, 0, 1, easings.linear)
        result = f(0)
        assert '0' in result

    def test_hide_end_is_clipped(self):
        tmpl = lambda pct: f'inset({pct}%)'
        f = _clip_hide(tmpl, 0, 1, easings.linear)
        result = f(1)
        assert '100' in result


class TestNormDir:
    def test_tuple_to_string(self):
        assert _norm_dir(RIGHT) == 'right'
        assert _norm_dir(LEFT) == 'left'
        assert _norm_dir(UP) == 'up'
        assert _norm_dir(DOWN) == 'down'

    def test_diagonal(self):
        # Diagonals map to primary direction
        assert _norm_dir(UL) == 'left'
        assert _norm_dir(UR) == 'right'
        assert _norm_dir(DL) == 'down'
        assert _norm_dir(DR) == 'down'

    def test_string_passthrough(self):
        assert _norm_dir('right') == 'right'
        assert _norm_dir('custom') == 'custom'

    def test_unknown_tuple_default(self):
        assert _norm_dir((99, 99)) == 'right'


class TestNormEdge:
    def test_tuple_to_string(self):
        assert _norm_edge(DOWN) == 'bottom'
        assert _norm_edge(UP) == 'top'
        assert _norm_edge(LEFT) == 'left'
        assert _norm_edge(RIGHT) == 'right'

    def test_string_passthrough(self):
        assert _norm_edge('bottom') == 'bottom'

    def test_unknown_tuple_default(self):
        assert _norm_edge((99, 99)) == 'bottom'


class TestCoordsOf:
    def test_raw_tuple(self):
        x, y = _coords_of((100, 200))
        assert x == 100
        assert y == 200

    def test_object_with_center(self):
        from vectormation.objects import Circle
        c = Circle(r=50, cx=100, cy=200)
        x, y = _coords_of(c, time=0)
        assert x == pytest.approx(100)
        assert y == pytest.approx(200)


class TestSetAttr:
    def test_instant(self):
        from vectormation.attributes import Real
        attr = Real(0, 10)
        _set_attr(attr, 1, None, 20, easings.smooth)
        assert attr.at_time(1) == pytest.approx(20)

    def test_animated(self):
        from vectormation.attributes import Real
        attr = Real(0, 10)
        _set_attr(attr, 0, 1, 20, easings.linear)
        assert attr.at_time(0) == pytest.approx(10)
        assert attr.at_time(1) == pytest.approx(20)
