"""Tests for previously untested _axes_ext.py methods."""
import math
from vectormation.objects import Axes


# ── add_function_label ──────────────────────────────────────────────────

class TestAddFunctionLabel:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        curve = ax.plot(lambda x: x)
        ax.add_function_label(curve, 'f(x)=x')
        svg = ax.to_svg(0)
        assert 'f(x)=x' in svg

    def test_with_x_pos(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_function_label(lambda x: x**2, 'x²', x_pos=2)
        svg = ax.to_svg(0)
        assert 'x²' in svg

    def test_direction_below(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_function_label(lambda x: x, 'below', direction='below')
        svg = ax.to_svg(0)
        assert 'below' in svg


# ── add_mean_line ───────────────────────────────────────────────────────

class TestAddMeanLine:
    def test_from_function(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_mean_line(lambda x: 5)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_from_data(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_mean_line([1, 2, 3, 4, 5])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_with_x_range(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_mean_line(lambda x: x, x_range=(2, 8))
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_residual_lines ──────────────────────────────────────────────────

class TestAddResidualLines:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        result = ax.add_residual_lines([1, 2, 3, 4], [2, 4, 5, 8])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_point(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        result = ax.add_residual_lines([5], [5])
        assert result is not None


# ── add_spread_band ─────────────────────────────────────────────────────

class TestAddSpreadBand:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_spread_band(lambda x: x, lambda x: 0.5)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_varying_spread(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(-5, 15, 1))
        ax.add_spread_band(lambda x: x, lambda x: abs(x) * 0.1)
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_tangent_at ──────────────────────────────────────────────────────

class TestAddTangentAt:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.add_tangent_at(lambda x: x**2, 2)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_at_zero(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_tangent_at(lambda x: math.sin(x), 0)
        svg = ax.to_svg(0)
        assert svg is not None


# ── animated_tangent_line ───────────────────────────────────────────────

class TestAnimatedTangentLine:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.animated_tangent_line(lambda x: x**2, -3, 3, start=0, end=2)
        svg0 = ax.to_svg(0)
        svg1 = ax.to_svg(1)
        assert svg0 is not None
        assert svg1 is not None

    def test_short_range(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.animated_tangent_line(lambda x: x, 0, 1, start=0, end=1)
        svg = ax.to_svg(0.5)
        assert svg is not None


# ── annotate_area ───────────────────────────────────────────────────────

class TestAnnotateArea:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.annotate_area(lambda x: x, x_range=(0, 3))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_with_label(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.annotate_area(lambda x: x**2, x_range=(1, 3), label='A')
        svg = ax.to_svg(0)
        assert 'A' in svg


# ── get_intersection_point ──────────────────────────────────────────────

class TestGetIntersectionPoint:
    def test_linear_intersection(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.get_intersection_point(lambda x: x, lambda x: -x + 2, (-5, 5))
        assert result is not None
        ix, iy = result
        assert abs(ix - 1) < 0.1
        assert abs(iy - 1) < 0.1

    def test_no_intersection(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.get_intersection_point(lambda x: 1, lambda x: 2, (-5, 5))
        assert result is None

    def test_quadratic_linear(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 25, 5))
        result = ax.get_intersection_point(lambda x: x**2, lambda x: 4, (0, 5))
        assert result is not None
        assert abs(result[0] - 2) < 0.1


# ── mark_intersection ──────────────────────────────────────────────────

class TestMarkIntersection:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.mark_intersection(lambda x: x, lambda x: -x + 2)
        assert result is not None

    def test_no_crossing(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.mark_intersection(lambda x: 1, lambda x: 2)
        assert result is None

    def test_with_label(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.mark_intersection(lambda x: x, lambda x: 2, label='P')
        assert result is not None


# ── get_trapezoidal_rule ────────────────────────────────────────────────

class TestGetTrapezoidalRule:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        result = ax.get_trapezoidal_rule(lambda x: x, x_range=(0, 4), dx=1)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_small_dx(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 25, 5))
        ax.get_trapezoidal_rule(lambda x: x**2, x_range=(0, 3), dx=0.5)
        svg = ax.to_svg(0)
        assert svg is not None


# ── get_x_axis_line / get_y_axis_line ───────────────────────────────────

class TestAxisLines:
    def test_x_axis_line(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        line = ax.get_x_axis_line()
        svg = line.to_svg(0)
        assert svg is not None

    def test_y_axis_line(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        line = ax.get_y_axis_line()
        svg = line.to_svg(0)
        assert svg is not None

    def test_y_axis_line_no_zero(self):
        ax = Axes(x_range=(1, 10, 1), y_range=(0, 10, 1))
        line = ax.get_y_axis_line()
        svg = line.to_svg(0)
        assert svg is not None


# ── add_crosshair ──────────────────────────────────────────────────────

class TestAddCrosshair:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        result = ax.add_crosshair(lambda x: x, -3, 3, start=0, end=2)
        svg = ax.to_svg(1)
        assert svg is not None

    def test_quadratic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.add_crosshair(lambda x: x**2, 0, 4, start=0, end=1)
        svg = ax.to_svg(0.5)
        assert svg is not None


# ── plot_stacked_area ───────────────────────────────────────────────────

class TestPlotStackedArea:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 20, 5))
        data = [[1, 2, 3, 4, 5], [2, 3, 1, 4, 2]]
        ax.plot_stacked_area(data)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_empty_data(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 1))
        result = ax.plot_stacked_area([])
        assert result is not None

    def test_single_series(self):
        ax = Axes(x_range=(0, 3, 1), y_range=(0, 10, 1))
        ax.plot_stacked_area([[1, 2, 3]])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_candlestick ────────────────────────────────────────────────────

class TestPlotCandlestick:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 20, 5))
        data = [
            (1, 10, 15, 8, 12),   # up
            (2, 12, 14, 9, 10),   # down
            (3, 10, 16, 10, 15),  # up
        ]
        ax.plot_candlestick(data)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_candle(self):
        ax = Axes(x_range=(0, 3, 1), y_range=(0, 20, 5))
        ax.plot_candlestick([(1, 10, 15, 8, 12)])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_dumbbell ───────────────────────────────────────────────────────

class TestPlotDumbbell:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_dumbbell([1, 2, 3], [2, 3, 1], [8, 7, 6])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_row(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 3, 1))
        ax.plot_dumbbell([1], [2], [8])
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_parametric_area ─────────────────────────────────────────────────

class TestAddParametricArea:
    def test_circle(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_parametric_area(
            lambda t: 2 * math.cos(t * math.tau),
            lambda t: 2 * math.sin(t * math.tau),
            t_range=(0, 1),
        )
        svg = ax.to_svg(0)
        assert svg is not None

    def test_few_samples(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_parametric_area(lambda t: t, lambda t: t, t_range=(0, 1), samples=10)
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_threshold_line ──────────────────────────────────────────────────

class TestAddThresholdLine:
    def test_horizontal(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_threshold_line(3)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_vertical(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_threshold_line(2, direction='vertical')
        svg = ax.to_svg(0)
        assert svg is not None

    def test_with_label(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_threshold_line(0, label='Threshold')
        svg = ax.to_svg(0)
        assert 'Threshold' in svg


# ── add_data_labels ─────────────────────────────────────────────────────

class TestAddDataLabels:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.add_data_labels([1, 2, 3], [2, 4, 6])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_custom_format(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.add_data_labels([1, 2], [3.14, 2.71], fmt='{:.2f}')
        svg = ax.to_svg(0)
        assert '3.14' in svg


# ── plot_lollipop ───────────────────────────────────────────────────────

class TestPlotLollipop:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_lollipop([1, 2, 3], [5, 8, 3])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_with_baseline(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_lollipop([1, 2], [5, 7], baseline=2)
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_moving_label ────────────────────────────────────────────────────

class TestAddMovingLabel:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_moving_label(lambda x: x, 'pt', -3, 3, start=0, end=2)
        svg = ax.to_svg(1)
        assert svg is not None

    def test_quadratic(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 25, 5))
        ax.add_moving_label(lambda x: x**2, 'max', 0, 4)
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_density ────────────────────────────────────────────────────────

class TestPlotDensity:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 1, 0.2))
        ax.plot_density([1, 2, 2, 3, 3, 3, 4, 5])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_empty(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 1, 0.2))
        ax.plot_density([])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 1, 0.2))
        ax.plot_density([5])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_population_pyramid ─────────────────────────────────────────────

class TestPlotPopulationPyramid:
    def test_basic(self):
        ax = Axes(x_range=(-10, 10, 2), y_range=(0, 5, 1))
        ax.plot_population_pyramid([1, 2, 3, 4], [5, 4, 3, 2], [4, 5, 6, 3])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_category(self):
        ax = Axes(x_range=(-10, 10, 2), y_range=(0, 3, 1))
        ax.plot_population_pyramid([1], [5], [3])
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_data_table ──────────────────────────────────────────────────────

class TestAddDataTable:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 5, 1))
        ax.add_data_table(['x', 'y'], [[1, 2], [3, 4]])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_row(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 5, 1))
        ax.add_data_table(['a', 'b', 'c'], [[10, 20, 30]])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_ribbon ─────────────────────────────────────────────────────────

class TestPlotRibbon:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_ribbon([0, 1, 2, 3, 4], [1, 2, 1, 2, 1], [5, 6, 5, 6, 5])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_narrow_band(self):
        ax = Axes(x_range=(0, 3, 1), y_range=(0, 5, 1))
        ax.plot_ribbon([0, 1, 2], [2, 2, 2], [3, 3, 3])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_swarm ──────────────────────────────────────────────────────────

class TestPlotSwarm:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_swarm([1, 2, 3], [[2, 3, 4], [5, 6], [1, 2, 3, 4]])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_group(self):
        ax = Axes(x_range=(0, 3, 1), y_range=(0, 10, 2))
        ax.plot_swarm([1], [[3, 5, 7]])
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_axis_break ──────────────────────────────────────────────────────

class TestAddAxisBreak:
    def test_y_axis(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 100, 10))
        ax.add_axis_break(50, axis='y')
        svg = ax.to_svg(0)
        assert svg is not None

    def test_x_axis(self):
        ax = Axes(x_range=(0, 100, 10), y_range=(0, 10, 1))
        ax.add_axis_break(50, axis='x')
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_error_bar ──────────────────────────────────────────────────────

class TestPlotErrorBar:
    def test_symmetric_errors(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_error_bar([1, 2, 3], [3, 5, 7], [0.5, 0.8, 0.3])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_asymmetric_errors(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_error_bar([1, 2, 3], [3, 5, 7], [(0.5, 1), (0.3, 0.8), (0.2, 0.4)])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_contour ────────────────────────────────────────────────────────

class TestPlotContour:
    def test_basic(self):
        ax = Axes(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        ax.plot_contour(lambda x, y: x**2 + y**2, levels=4)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_explicit_levels(self):
        ax = Axes(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        ax.plot_contour(lambda x, y: x**2 + y**2, levels=[1, 4, 9])
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_quiver ─────────────────────────────────────────────────────────

class TestPlotQuiver:
    def test_basic(self):
        ax = Axes(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        ax.plot_quiver(lambda x, y: (y, -x), x_step=1, y_step=1)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_constant_field(self):
        ax = Axes(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        ax.plot_quiver(lambda x, y: (1, 0), x_step=2, y_step=2)
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_area ───────────────────────────────────────────────────────────

class TestPlotArea:
    def test_basic(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_area(lambda x: x)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_with_baseline(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 10, 2))
        ax.plot_area(lambda x: x**2, x_range=(0, 3), baseline=2)
        svg = ax.to_svg(0)
        assert svg is not None


# ── plot_dot_plot ───────────────────────────────────────────────────────

class TestPlotDotPlot:
    def test_basic(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1))
        ax.plot_dot_plot([1, 2, 2, 3, 3, 3, 4])
        svg = ax.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 3, 1))
        ax.plot_dot_plot([5])
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_reference_band ──────────────────────────────────────────────────

class TestAddReferenceBand:
    def test_y_band(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_reference_band(1, 3, axis='y')
        svg = ax.to_svg(0)
        assert svg is not None

    def test_x_band(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        ax.add_reference_band(-2, 2, axis='x')
        svg = ax.to_svg(0)
        assert svg is not None


# ── add_color_bar ───────────────────────────────────────────────────────

class TestAddColorBar:
    def test_default(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_color_bar()
        svg = ax.to_svg(0)
        assert svg is not None

    def test_custom_colormap(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_color_bar(colormap=[(0, '#000'), (1, '#fff')], label='Value')
        svg = ax.to_svg(0)
        assert svg is not None

    def test_left_side(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_color_bar(side='left')
        svg = ax.to_svg(0)
        assert svg is not None
