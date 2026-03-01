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
    easings.smoothstep, easings.smootherstep, easings.smoothererstep,
    easings.running_start, easings.exponential_decay,
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

    def test_compose_empty(self):
        f = easings.compose()
        assert f(0.5) == pytest.approx(0.5, abs=0.01)

    def test_compose_single(self):
        f = easings.compose(easings.linear)
        assert f is easings.linear

    def test_compose_midpoint(self):
        f = easings.compose(easings.linear, easings.linear)
        assert f(0.5) == pytest.approx(0.5, abs=0.02)


class TestReverseEasing:
    def test_reverse_at_zero(self):
        f = easings.reverse(easings.linear)
        assert f(0.0) == pytest.approx(0, abs=0.01)

    def test_reverse_at_one(self):
        f = easings.reverse(easings.linear)
        assert f(1.0) == pytest.approx(1, abs=0.01)

    def test_reverse_midpoint(self):
        f = easings.reverse(easings.linear)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)

    def test_reverse_asymmetric(self):
        # ease_in_quad(0.25) = 0.0625, so reverse should give 1 - ease_in_quad(0.75)
        f = easings.reverse(easings.ease_in_quad)
        val = f(0.25)
        expected = 1 - easings.ease_in_quad(0.75)
        assert val == pytest.approx(expected, abs=0.01)


class TestRepeatEasing:
    def test_repeat_boundaries(self):
        f = easings.repeat(easings.linear, 2)
        assert f(0.0) == pytest.approx(0, abs=0.01)
        assert f(1.0) == pytest.approx(1, abs=0.01)

    def test_repeat_two_midpoint(self):
        f = easings.repeat(easings.linear, 2)
        # At t=0.25, we're halfway through first repetition
        assert f(0.25) == pytest.approx(0.5, abs=0.02)

    def test_repeat_count_one(self):
        f = easings.repeat(easings.linear, 1)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)


class TestOscillateEasing:
    def test_oscillate_boundaries(self):
        f = easings.oscillate(easings.linear, 1)
        assert f(0.0) == pytest.approx(0, abs=0.01)
        # oscillate(linear, 1) = forward then backward = ends at 0
        assert f(1.0) == pytest.approx(0, abs=0.01)

    def test_oscillate_peak(self):
        f = easings.oscillate(easings.linear, 1)
        # At t=0.5, first forward half finishes -> value at 1.0
        assert f(0.5) == pytest.approx(1, abs=0.02)

    def test_oscillate_count_two(self):
        f = easings.oscillate(easings.linear, 2)
        # 2 full oscillations = 4 segments
        assert f(0.0) == pytest.approx(0, abs=0.01)
        assert f(1.0) == pytest.approx(0, abs=0.01)


class TestClampEasing:
    def test_clamp_before_start(self):
        f = easings.clamp(easings.linear, 0.3, 0.7)
        assert f(0.1) == pytest.approx(0, abs=0.01)

    def test_clamp_after_end(self):
        f = easings.clamp(easings.linear, 0.3, 0.7)
        assert f(0.9) == pytest.approx(1, abs=0.01)

    def test_clamp_midpoint(self):
        f = easings.clamp(easings.linear, 0.0, 1.0)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)

    def test_clamp_equal_boundaries(self):
        f = easings.clamp(easings.linear, 0.5, 0.5)
        assert f(0.3) == pytest.approx(0, abs=0.01)
        assert f(0.7) == pytest.approx(1, abs=0.01)


class TestBlendEasing:
    def test_blend_equal_weight(self):
        f = easings.blend(easings.linear, easings.linear, 0.5)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)

    def test_blend_weight_zero(self):
        # weight=0 means 100% easing_a
        f = easings.blend(easings.linear, easings.ease_in_quad, 0.0)
        assert f(0.5) == pytest.approx(0.5, abs=0.01)

    def test_blend_weight_one(self):
        # weight=1 means 100% easing_b
        f = easings.blend(easings.linear, easings.ease_in_quad, 1.0)
        assert f(0.5) == pytest.approx(easings.ease_in_quad(0.5), abs=0.01)

    def test_blend_boundaries(self):
        f = easings.blend(easings.linear, easings.smooth, 0.5)
        assert f(0.0) == pytest.approx(0, abs=0.01)
        assert f(1.0) == pytest.approx(1, abs=0.01)


class TestSmoothstepEasings:
    def test_smoothstep_boundaries(self):
        assert easings.smoothstep(0) == pytest.approx(0, abs=0.01)
        assert easings.smoothstep(1) == pytest.approx(1, abs=0.01)

    def test_smoothstep_midpoint(self):
        assert easings.smoothstep(0.5) == pytest.approx(0.5, abs=0.01)

    def test_smootherstep_boundaries(self):
        assert easings.smootherstep(0) == pytest.approx(0, abs=0.01)
        assert easings.smootherstep(1) == pytest.approx(1, abs=0.01)

    def test_smoothererstep_boundaries(self):
        assert easings.smoothererstep(0) == pytest.approx(0, abs=0.01)
        assert easings.smoothererstep(1) == pytest.approx(1, abs=0.01)


class TestRunningStartEasing:
    def test_running_start_boundaries(self):
        assert easings.running_start(0) == pytest.approx(0, abs=0.01)
        assert easings.running_start(1) == pytest.approx(1, abs=0.01)

    def test_running_start_pulls_back(self):
        # With negative pull_factor, early values should be negative
        val = easings.running_start(0.1, pull_factor=-0.5)
        assert val < 0.1  # pulls back relative to linear


class TestThereAndBackWithPause:
    def test_boundaries(self):
        assert easings.there_and_back_with_pause(0) == pytest.approx(0, abs=0.01)
        assert easings.there_and_back_with_pause(1) == pytest.approx(0, abs=0.01)

    def test_pause_at_middle(self):
        assert easings.there_and_back_with_pause(0.5) == pytest.approx(1, abs=0.01)


class TestNotQuiteThereEasing:
    def test_not_quite_there(self):
        f = easings.not_quite_there(easings.linear, 0.7)
        assert f(0) == pytest.approx(0, abs=0.01)
        assert f(1) == pytest.approx(0.7, abs=0.01)

    def test_not_quite_there_midpoint(self):
        f = easings.not_quite_there(easings.linear, 0.5)
        assert f(0.5) == pytest.approx(0.25, abs=0.01)
