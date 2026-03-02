"""Edge case tests for _axes.py and _axes_ext.py."""
import math
import pytest
from vectormation.objects import NumberLine, Axes


# -- coords_to_point / input_to_graph_point -----------------------------------

class TestCoordsToPoint:
    def test_origin(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        px, py = ax.coords_to_point(0, 0)
        assert math.isfinite(px) and math.isfinite(py)

    def test_extremes(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        p1 = ax.coords_to_point(0, 0)
        p2 = ax.coords_to_point(10, 10)
        assert p1 != p2

    def test_time_param(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        pt = ax.coords_to_point(1, 2, time=0)
        assert len(pt) == 2


# -- NumberLine roundtrip tests ------------------------------------------------

class TestNumberLineRoundtrip:
    def test_roundtrip_integers(self):
        nl = NumberLine(x_range=(0, 10, 1))
        for v in range(11):
            px, _ = nl.number_to_point(v)
            result = nl.point_to_number(px)
            assert abs(result - v) < 0.5

    def test_roundtrip_negatives(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        for v in range(-5, 6):
            px, _ = nl.number_to_point(v)
            result = nl.point_to_number(px)
            assert abs(result - v) < 0.5


class TestPlotLengthValidation:
    def test_scatter_mismatched_lengths(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        with pytest.raises(ValueError, match='equal length'):
            ax.plot_scatter([1, 2, 3], [1, 2])

    def test_step_mismatched_lengths(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        with pytest.raises(ValueError, match='equal length'):
            ax.plot_step([1, 2], [1])

    def test_bar_mismatched_lengths(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        with pytest.raises(ValueError, match='equal length'):
            ax.plot_bar([1, 2, 3], [1])

    def test_filled_step_mismatched_lengths(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        with pytest.raises(ValueError, match='equal length'):
            ax.plot_filled_step([1], [1, 2])

    def test_grouped_bar_jagged(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        with pytest.raises(ValueError, match='equal length'):
            ax.plot_grouped_bar([[1, 2, 3], [4, 5]])


class TestTickHelpers:
    def test_nice_ticks_zero_count(self):
        from vectormation._axes_helpers import _nice_ticks
        assert _nice_ticks(0, 10, target_count=0) == []

    def test_nice_ticks_negative_count(self):
        from vectormation._axes_helpers import _nice_ticks
        assert _nice_ticks(0, 10, target_count=-5) == []

    def test_pi_ticks_zero_step(self):
        from vectormation._axes_helpers import pi_ticks
        assert pi_ticks(0, 10, step=0) == []

    def test_pi_ticks_negative_step(self):
        from vectormation._axes_helpers import pi_ticks
        assert pi_ticks(0, 10, step=-1) == []
