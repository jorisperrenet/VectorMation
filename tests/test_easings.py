"""Tests for easing functions: boundary conditions, mathematical properties, combinators."""
import math
import pytest

import vectormation.easings as easings


# All basic easings that should satisfy f(0)≈0, f(1)≈1
STANDARD_EASINGS = [
    easings.linear,
    easings.smooth,
    easings.rush_into,
    easings.rush_from,
    easings.slow_into,
    easings.double_smooth,
    easings.ease_in_sine, easings.ease_out_sine, easings.ease_in_out_sine,
    easings.ease_in_quad, easings.ease_out_quad, easings.ease_in_out_quad,
    easings.ease_in_cubic, easings.ease_out_cubic, easings.ease_in_out_cubic,
    easings.ease_in_quart, easings.ease_out_quart, easings.ease_in_out_quart,
    easings.ease_in_quint, easings.ease_out_quint, easings.ease_in_out_quint,
    easings.ease_in_expo, easings.ease_out_expo, easings.ease_in_out_expo,
    easings.ease_in_circ, easings.ease_out_circ, easings.ease_in_out_circ,
    easings.ease_in_bounce, easings.ease_out_bounce, easings.ease_in_out_bounce,
    easings.smoothstep, easings.smootherstep, easings.smoothererstep,
    easings.lingering,
]

# Easings that overshoot (go outside [0, 1] range) but still start at 0 and end at 1
OVERSHOOTING_EASINGS = [
    easings.ease_in_back, easings.ease_out_back, easings.ease_in_out_back,
    easings.ease_in_elastic, easings.ease_out_elastic, easings.ease_in_out_elastic,
]


class TestBoundaryConditions:
    """Every standard easing must start near 0 and end near 1."""

    @pytest.mark.parametrize("easing", STANDARD_EASINGS + OVERSHOOTING_EASINGS,
                             ids=lambda e: e.__name__)
    def test_f0_is_zero(self, easing):
        assert easing(0) == pytest.approx(0, abs=1e-6)

    @pytest.mark.parametrize("easing", STANDARD_EASINGS + OVERSHOOTING_EASINGS,
                             ids=lambda e: e.__name__)
    def test_f1_is_one(self, easing):
        assert easing(1) == pytest.approx(1, abs=1e-6)


class TestUnitIntervalDecorator:
    """Easings with @unit_interval should clamp outside [0, 1]."""

    @pytest.mark.parametrize("easing", STANDARD_EASINGS + OVERSHOOTING_EASINGS,
                             ids=lambda e: e.__name__)
    def test_below_zero_returns_zero(self, easing):
        assert easing(-0.5) == 0

    @pytest.mark.parametrize("easing", STANDARD_EASINGS + OVERSHOOTING_EASINGS,
                             ids=lambda e: e.__name__)
    def test_above_one_returns_one(self, easing):
        assert easing(1.5) == 1


class TestZeroDecorator:
    """Easings with @zero return 0 outside [0, 1]."""

    @pytest.mark.parametrize("easing", [easings.there_and_back, easings.wiggle])
    def test_returns_zero_outside(self, easing):
        assert easing(-0.1) == 0
        assert easing(1.1) == 0


class TestStandardEasingRange:
    """Standard (non-overshooting) easings should stay in [0, 1]."""

    @pytest.mark.parametrize("easing", STANDARD_EASINGS, ids=lambda e: e.__name__)
    def test_stays_in_01_range(self, easing):
        for i in range(101):
            t = i / 100
            val = easing(t)
            assert -1e-6 <= val <= 1 + 1e-6, f"{easing.__name__}({t}) = {val}"


class TestOvershootingEasings:
    """Back and elastic easings should overshoot but still hit endpoints."""

    def test_ease_in_back_goes_negative(self):
        # ease_in_back dips below 0 near t=0
        vals = [easings.ease_in_back(i / 100) for i in range(30)]
        assert any(v < -0.01 for v in vals)

    def test_ease_out_back_exceeds_one(self):
        vals = [easings.ease_out_back(i / 100) for i in range(70, 101)]
        assert any(v > 1.01 for v in vals)

    def test_ease_in_elastic_oscillates(self):
        vals = [easings.ease_in_elastic(i / 100) for i in range(100)]
        # Should have negative values (oscillation/overshoot)
        has_negative = any(v < 0 for v in vals)
        assert has_negative


class TestMonotonicity:
    """Linear and basic power easings should be monotonically non-decreasing."""

    @pytest.mark.parametrize("easing", [
        easings.linear, easings.ease_in_quad, easings.ease_out_quad,
        easings.ease_in_cubic, easings.ease_out_cubic,
        easings.ease_in_sine, easings.ease_out_sine,
    ], ids=lambda e: e.__name__)
    def test_monotonic(self, easing):
        prev = easing(0)
        for i in range(1, 101):
            curr = easing(i / 100)
            assert curr >= prev - 1e-9, f"{easing.__name__} not monotonic at {i/100}"
            prev = curr


class TestThereAndBack:
    """there_and_back should be symmetric: f(t) == f(1-t)."""

    def test_symmetric(self):
        for i in range(51):
            t = i / 100
            assert easings.there_and_back(t) == pytest.approx(
                easings.there_and_back(1 - t), abs=1e-6)

    def test_peak_at_half(self):
        assert easings.there_and_back(0.5) == pytest.approx(1, abs=0.01)


class TestSpecificValues:
    """Test known mathematical identities for specific easings."""

    def test_linear_is_identity(self):
        for t in [0, 0.25, 0.5, 0.75, 1]:
            assert easings.linear(t) == pytest.approx(t)

    def test_smoothstep_hermite(self):
        # smoothstep(t) = 3t² - 2t³
        for t in [0, 0.25, 0.5, 0.75, 1]:
            expected = t * t * (3 - 2 * t)
            assert easings.smoothstep(t) == pytest.approx(expected)

    def test_ease_in_quad_is_t_squared(self):
        for t in [0, 0.25, 0.5, 0.75, 1]:
            assert easings.ease_in_quad(t) == pytest.approx(t ** 2)

    def test_ease_out_quad_formula(self):
        for t in [0, 0.25, 0.5, 0.75, 1]:
            assert easings.ease_out_quad(t) == pytest.approx(1 - (1 - t) ** 2)

    def test_ease_in_out_sine_formula(self):
        for t in [0, 0.25, 0.5, 0.75, 1]:
            expected = -(math.cos(math.pi * t) - 1) / 2
            assert easings.ease_in_out_sine(t) == pytest.approx(expected)


class TestCombinators:

    def test_reverse(self):
        rev = easings.reverse(easings.linear)
        assert rev(0) == pytest.approx(0)
        assert rev(1) == pytest.approx(1)
        # For linear, reverse is same as linear (1-(1-t) = t)
        for t in [0, 0.25, 0.5, 0.75, 1]:
            assert rev(t) == pytest.approx(t)

    def test_reverse_nonlinear(self):
        rev = easings.reverse(easings.ease_in_quad)
        # reverse(ease_in)(t) = 1 - ease_in(1-t) = 1 - (1-t)^2 = ease_out
        for t in [0, 0.25, 0.5, 0.75, 1]:
            assert rev(t) == pytest.approx(easings.ease_out_quad(t), abs=1e-6)

    def test_compose_two_easings(self):
        c = easings.compose(easings.linear, easings.linear)
        assert c(0) == pytest.approx(0)
        assert c(1) == pytest.approx(1)
        # At midpoint, first easing finishes at 0.5
        assert c(0.5) == pytest.approx(0.5)

    def test_compose_empty_returns_linear(self):
        c = easings.compose()
        assert c(0.5) == pytest.approx(0.5)

    def test_repeat_count_2(self):
        r = easings.repeat(easings.linear, 2)
        assert r(0) == pytest.approx(0)
        assert r(0.25) == pytest.approx(0.5)  # halfway through first rep
        assert r(0.5) == pytest.approx(0)     # start of second rep
        assert r(0.75) == pytest.approx(0.5)  # halfway through second
        assert r(1) == pytest.approx(1)       # end

    def test_oscillate(self):
        o = easings.oscillate(easings.linear, 1)
        # 1 oscillation = 2 segments: forward [0,0.5], backward [0.5,1]
        assert o(0) == pytest.approx(0)
        assert o(0.25) == pytest.approx(0.5)   # halfway forward
        assert o(0.5) == pytest.approx(1)       # peak (start of backward)
        assert o(0.75) == pytest.approx(0.5)    # halfway backward
        # At t=1: 2 segments is even, so ends at easing(0) = 0
        assert o(1) == pytest.approx(0)

    def test_clamp(self):
        c = easings.clamp(easings.linear, 0.25, 0.75)
        assert c(0) == pytest.approx(0)       # before start_t
        assert c(0.25) == pytest.approx(0)    # at start_t
        assert c(0.5) == pytest.approx(0.5)   # midpoint
        assert c(0.75) == pytest.approx(1)    # at end_t
        assert c(1) == pytest.approx(1)       # after end_t

    def test_clamp_degenerate(self):
        # start_t >= end_t: step function
        c = easings.clamp(easings.linear, 0.5, 0.5)
        assert c(0.4) == pytest.approx(0)
        assert c(0.5) == pytest.approx(1)

    def test_blend(self):
        b = easings.blend(easings.linear, easings.ease_in_quad, weight=0.5)
        # blend = 0.5*t + 0.5*t^2
        for t in [0, 0.5, 1]:
            assert b(t) == pytest.approx(0.5 * t + 0.5 * t ** 2)

    def test_step(self):
        s = easings.step(4)
        assert s(0) == pytest.approx(0)
        assert s(0.1) == pytest.approx(0)        # first step
        assert s(0.26) == pytest.approx(1/3)      # second step
        assert s(1) == pytest.approx(1)

    def test_step_single(self):
        s = easings.step(1)
        assert s(0) == pytest.approx(0)
        assert s(0.99) == pytest.approx(0)
        assert s(1) == pytest.approx(1)
