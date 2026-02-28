"""Tests for vectormation.easings: boundary values and clamping."""
import pytest
import vectormation.easings as easings


# All unit_interval-decorated easings should satisfy f(0)~=0 and f(1)~=1
UNIT_INTERVAL_EASINGS = [
    easings.linear, easings.smooth, easings.rush_into, easings.rush_from,
    easings.slow_into, easings.double_smooth, easings.lingering,
    easings.ease_in_sine, easings.ease_out_sine, easings.ease_in_out_sine,
    easings.ease_in_quad, easings.ease_out_quad, easings.ease_in_out_quad,
    easings.ease_in_cubic, easings.ease_out_cubic, easings.ease_in_out_cubic,
    easings.ease_in_quart, easings.ease_out_quart, easings.ease_in_out_quart,
    easings.ease_in_quint, easings.ease_out_quint, easings.ease_in_out_quint,
    easings.ease_in_expo, easings.ease_out_expo, easings.ease_in_out_expo,
    easings.ease_in_circ, easings.ease_out_circ, easings.ease_in_out_circ,
    easings.ease_in_back, easings.ease_out_back, easings.ease_in_out_back,
    easings.ease_in_elastic, easings.ease_out_elastic, easings.ease_in_out_elastic,
    easings.ease_in_bounce, easings.ease_out_bounce, easings.ease_in_out_bounce,
]


@pytest.mark.parametrize('easing', UNIT_INTERVAL_EASINGS,
                         ids=[f.__name__ for f in UNIT_INTERVAL_EASINGS])
class TestUnitIntervalEasings:
    def test_at_zero(self, easing):
        assert easing(0) == pytest.approx(0, abs=0.01)

    def test_at_one(self, easing):
        assert easing(1) == pytest.approx(1, abs=0.01)

    def test_clamped_below(self, easing):
        val = easing(-0.5)
        assert val == pytest.approx(0, abs=0.01)

    def test_clamped_above(self, easing):
        val = easing(1.5)
        assert val == pytest.approx(1, abs=0.01)


# Zero-decorated easings: return 0 outside [0,1]
ZERO_EASINGS = [easings.there_and_back, easings.wiggle]


@pytest.mark.parametrize('easing', ZERO_EASINGS,
                         ids=[f.__name__ for f in ZERO_EASINGS])
class TestZeroEasings:
    def test_at_zero(self, easing):
        assert easing(0) == pytest.approx(0, abs=0.01)

    def test_at_one(self, easing):
        assert easing(1) == pytest.approx(0, abs=0.01)

    def test_outside_returns_zero(self, easing):
        assert easing(-1) == pytest.approx(0, abs=0.01)
        assert easing(2) == pytest.approx(0, abs=0.01)


class TestSquishRateFunc:
    def test_returns_callable(self):
        result = easings.squish_rate_func(easings.linear, 0.2, 0.8)
        assert callable(result)

    def test_equal_a_b_returns_callable(self):
        """squish_rate_func with a==b should return a callable, not a number."""
        result = easings.squish_rate_func(easings.linear, 0.5, 0.5)
        assert callable(result)
        assert result(0.5) == pytest.approx(0, abs=0.01)

    def test_before_a(self):
        f = easings.squish_rate_func(easings.linear, 0.2, 0.8)
        assert f(0.1) == pytest.approx(0, abs=0.01)

    def test_after_b(self):
        f = easings.squish_rate_func(easings.linear, 0.2, 0.8)
        assert f(0.9) == pytest.approx(1, abs=0.01)

    def test_midpoint(self):
        f = easings.squish_rate_func(easings.linear, 0.0, 1.0)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)


class TestStepEasing:
    def test_step_3(self):
        f = easings.step(3)
        assert f(0.0) == pytest.approx(0, abs=0.01)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)
        assert f(1.0) == pytest.approx(1, abs=0.01)


class TestComposeEasing:
    def test_compose_two(self):
        f = easings.compose(easings.linear, easings.linear)
        assert f(0.0) == pytest.approx(0, abs=0.01)
        assert f(1.0) == pytest.approx(1, abs=0.01)
