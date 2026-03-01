"""Edge case tests for _axes.py and _axes_ext.py."""
import math
from vectormation._composites import NumberLine
from vectormation.objects import Axes


# ── Axes construction edge cases ──────────────────────────────────────────

class TestAxesConstruction:
    def test_default_axes(self):
        ax = Axes()
        svg = ax.to_svg(0)
        assert svg is not None

    def test_custom_range(self):
        ax = Axes(x_range=(-10, 10, 2), y_range=(-5, 5, 1))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_zero_step(self):
        """Axes with step=0 in range should not crash."""
        ax = Axes(x_range=(-5, 5, 0))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_negative_step(self):
        ax = Axes(x_range=(0, 10, -1))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_equal_range(self):
        """x_min == x_max."""
        ax = Axes(x_range=(5, 5, 1))
        svg = ax.to_svg(0)
        assert svg is not None


# ── coords_to_point / input_to_graph_point ───────────────────────────────

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


# ── plot / add_function ───────────────────────────────────────────────────

class TestAxesPlot:
    def test_linear(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        curve = ax.plot(lambda x: x)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_constant(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.plot(lambda x: 3)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_quadratic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.plot(lambda x: x**2)
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_histogram edge cases ────────────────────────────────────────────

class TestPlotHistogram:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_histogram([1, 2, 2, 3, 3, 3, 4, 5, 6, 7])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_histogram([5])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_identical_values(self):
        """All values the same — lo == hi edge case."""
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_histogram([3, 3, 3, 3])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_bins_zero_clamped(self):
        """bins=0 should be clamped to 1."""
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_histogram([1, 2, 3, 4], bins=0)
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_parametric_plot ───────────────────────────────────────────────────

class TestParametricPlot:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_parametric_plot(
            lambda t: math.cos(t * math.tau),
            lambda t: math.sin(t * math.tau),
            t_range=(0, 1),
        )
        svg = ax.to_svg(0)
        assert svg is not None

    def test_num_points_zero_clamped(self):
        """num_points=0 should be clamped to 1."""
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_parametric_plot(
            lambda t: t,
            lambda t: t,
            t_range=(0, 1),
            num_points=0,
        )

    def test_few_points(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_parametric_plot(
            lambda t: math.cos(t),
            lambda t: math.sin(t),
            t_range=(0, math.tau),
            num_points=3,
        )
        svg = ax.to_svg(0)
        assert svg is not None


# ── get_area ──────────────────────────────────────────────────────────────

class TestGetArea:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        curve = ax.plot(lambda x: x)
        area = ax.get_area(curve, x_range=(0, 5))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_function_area(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        area = ax.get_area(lambda x: x, x_range=(0, 5))
        svg = ax.to_svg(0)
        assert svg is not None


# ── get_vertical_line / get_horizontal_line ───────────────────────────────

class TestAxesLines:
    def test_vertical_line(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.plot(lambda x: x**2)
        ax.get_vertical_line(2, y_val=4)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_horizontal_line(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.plot(lambda x: x)
        ax.get_horizontal_line(3, 3)
        svg = ax.to_svg(0)
        assert svg is not None


# ── Axes animated range ──────────────────────────────────────────────────

class TestAxesAnimatedRange:
    def test_x_range_animation(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.x_min.move_to(0, 1, -10)
        ax.x_max.move_to(0, 1, 10)
        svg0 = ax.to_svg(0)
        svg1 = ax.to_svg(1)
        assert svg0 is not None
        assert svg1 is not None

    def test_y_range_animation(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.y_min.move_to(0, 1, -10)
        ax.y_max.move_to(0, 1, 10)
        svg = ax.to_svg(0.5)
        assert svg is not None


# ── add_coordinates / add_grid ────────────────────────────────────────────

class TestAxesDecorations:
    def test_add_grid(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_grid()
        svg = ax.to_svg(0)
        assert svg is not None

    def test_add_title(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_title('Test Title')
        svg = ax.to_svg(0)
        assert svg is not None

    def test_add_legend(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        c1 = ax.plot(lambda x: x, stroke='#f00')
        c2 = ax.plot(lambda x: -x, stroke='#00f')
        ax.add_legend([('f(x)', '#f00'), ('g(x)', '#00f')])
        svg = ax.to_svg(0)
        assert svg is not None


# ── NumberLine roundtrip tests ───────────────────────────────────────────

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

    def test_two_element_range(self):
        """Range with only (start, end), no step."""
        nl = NumberLine(x_range=(-3, 3))
        svg = nl.to_svg(0)
        assert svg is not None
