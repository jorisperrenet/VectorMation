"""Tests for Axes analytical methods: extrema, zeros, integrals, derivatives, etc."""
import math
import pytest
from vectormation.objects import Axes, VectorMathAnim


@pytest.fixture
def ax():
    return Axes(x_range=(-5, 5), y_range=(-5, 5))


@pytest.fixture
def canvas():
    return VectorMathAnim('/tmp')


# -- get_function_max / get_function_min --

class TestFunctionExtrema:
    def test_max_of_quadratic(self, ax):
        """f(x) = -(x-1)^2 + 4 has max at x=1, y=4."""
        x, y = ax.get_function_max(lambda x: -(x - 1)**2 + 4, -5, 5)
        assert abs(x - 1.0) < 0.1
        assert abs(y - 4.0) < 0.1

    def test_min_of_quadratic(self, ax):
        """f(x) = (x+2)^2 - 3 has min at x=-2, y=-3."""
        x, y = ax.get_function_min(lambda x: (x + 2)**2 - 3, -5, 5)
        assert abs(x - (-2.0)) < 0.1
        assert abs(y - (-3.0)) < 0.1

    def test_max_of_sine(self, ax):
        x, y = ax.get_function_max(math.sin, -math.pi, math.pi)
        assert abs(x - math.pi / 2) < 0.1
        assert abs(y - 1.0) < 0.01

    def test_min_of_sine(self, ax):
        x, y = ax.get_function_min(math.sin, -math.pi, math.pi)
        assert abs(x - (-math.pi / 2)) < 0.1
        assert abs(y - (-1.0)) < 0.01

    def test_linear_max_at_endpoint(self, ax):
        """For f(x) = x, max is at x=5."""
        x, y = ax.get_function_max(lambda x: x, -5, 5)
        assert abs(x - 5.0) < 0.1
        assert abs(y - 5.0) < 0.1

    def test_no_finite_values_raises(self, ax):
        """If all values are NaN/inf, raise ValueError."""
        with pytest.raises(ValueError, match="No finite"):
            ax.get_function_max(lambda x: float('nan'), 0, 1)


# -- get_zeros --

class TestGetZeros:
    def test_linear_zero(self, ax):
        """f(x) = x has a zero at x=0."""
        zeros = ax.get_zeros(lambda x: x, -5, 5)
        assert any(abs(z[0]) < 0.1 for z in zeros)

    def test_quadratic_zeros(self, ax):
        """f(x) = x^2 - 4 has zeros at x=-2 and x=2."""
        zeros = ax.get_zeros(lambda x: x**2 - 4, -5, 5)
        assert len(zeros) >= 2
        x_vals = sorted(z[0] for z in zeros)
        assert abs(x_vals[0] - (-2.0)) < 0.1
        assert abs(x_vals[-1] - 2.0) < 0.1

    def test_sine_zeros(self, ax):
        """sin(x) has zeros at 0, pi, -pi, etc."""
        zeros = ax.get_zeros(math.sin, -4, 4)
        assert len(zeros) >= 2  # at least 0 and pi

    def test_exact_zero_at_endpoint(self, ax):
        """f(x) = x has exact zero at x=0 which is an interior point."""
        zeros = ax.get_zeros(lambda x: x, -1, 1)
        assert any(abs(z[0]) < 0.05 for z in zeros)


# -- get_x_intercept / get_y_intercept --

class TestIntercepts:
    def test_x_intercept_linear(self, ax):
        """f(x) = 2x - 4 has x-intercept at x=2."""
        xi = ax.get_x_intercept(lambda x: 2 * x - 4)
        assert xi is not None
        assert abs(xi - 2.0) < 0.1

    def test_x_intercept_none(self, ax):
        """f(x) = x^2 + 1 has no x-intercept."""
        xi = ax.get_x_intercept(lambda x: x**2 + 1)
        assert xi is None

    def test_y_intercept(self, ax):
        """f(x) = 3x + 7 has y-intercept at 7."""
        yi = ax.get_y_intercept(lambda x: 3 * x + 7)
        assert yi == 7

    def test_y_intercept_quadratic(self, ax):
        """f(x) = x^2 - 5 has y-intercept at -5."""
        yi = ax.get_y_intercept(lambda x: x**2 - 5)
        assert yi == -5

    def test_y_intercept_error_returns_none(self, ax):
        """If func(0) raises, return None."""
        def bad_func(x):
            raise ZeroDivisionError
        yi = ax.get_y_intercept(bad_func)
        assert yi is None


# -- get_derivative / get_secant_slope --

class TestDerivatives:
    def test_derivative_of_x_squared(self, ax):
        """d/dx(x^2) = 2x at x=3 gives ~6."""
        d = ax.get_derivative(lambda x: x**2, 3)
        assert abs(d - 6.0) < 0.01

    def test_derivative_of_sin(self, ax):
        """d/dx(sin(x)) = cos(x) at x=0 gives ~1."""
        d = ax.get_derivative(math.sin, 0)
        assert abs(d - 1.0) < 0.01

    def test_get_slope_is_alias(self, ax):
        """get_slope should produce the same result as get_derivative."""
        assert ax.get_slope(lambda x: x**2, 3) == ax.get_derivative(lambda x: x**2, 3)

    def test_secant_slope(self, ax):
        """Secant slope of x^2 from x=1 to x=3 is (9-1)/2 = 4."""
        s = ax.get_secant_slope(lambda x: x**2, 1, 2)
        assert abs(s - 4.0) < 0.01

    def test_secant_slope_zero_dx_raises(self, ax):
        with pytest.raises(ValueError, match="dx must not be zero"):
            ax.get_secant_slope(lambda x: x, 1, 0)

    def test_secant_slope_small_dx_approaches_derivative(self, ax):
        """With small dx, secant slope approximates derivative."""
        f = lambda x: x**3
        secant = ax.get_secant_slope(f, 2, 0.001)
        deriv = ax.get_derivative(f, 2)
        assert abs(secant - deriv) < 0.1


# -- get_area_value / get_integral --

class TestAreaValue:
    def test_area_of_constant(self, ax):
        """Integral of f(x)=3 from 0 to 4 is 12."""
        area = ax.get_area_value(lambda x: 3, 0, 4)
        assert abs(area - 12.0) < 0.01

    def test_area_of_linear(self, ax):
        """Integral of f(x)=x from 0 to 4 is 8."""
        area = ax.get_area_value(lambda x: x, 0, 4)
        assert abs(area - 8.0) < 0.1

    def test_area_of_quadratic(self, ax):
        """Integral of f(x)=x^2 from 0 to 3 is 9."""
        area = ax.get_area_value(lambda x: x**2, 0, 3)
        assert abs(area - 9.0) < 0.2

    def test_negative_area(self, ax):
        """Integral of f(x)=-1 from 0 to 5 is -5."""
        area = ax.get_area_value(lambda x: -1, 0, 5)
        assert abs(area - (-5.0)) < 0.01

    def test_get_integral_is_alias(self, ax):
        """get_integral should produce the same result as get_area_value."""
        assert ax.get_integral(lambda x: x, 0, 4) == ax.get_area_value(lambda x: x, 0, 4)

    def test_sine_integral(self, ax):
        """Integral of sin from 0 to pi is 2."""
        area = ax.get_area_value(math.sin, 0, math.pi)
        assert abs(area - 2.0) < 0.05


# -- get_average --

class TestGetAverage:
    def test_average_of_linear(self, ax):
        """Average of f(x)=x over [0,4] is 2."""
        avg = ax.get_average(lambda x: x, 0, 4)
        assert abs(avg - 2.0) < 0.1


# -- get_graph_length --

class TestGraphLength:
    def test_horizontal_line_length(self, ax):
        """f(x) = 0 from -5 to 5 has length = plot_width."""
        length = ax.get_graph_length(lambda x: 0, -5, 5)
        assert abs(length - ax.plot_width) < 5

    def test_increasing_length(self, ax):
        """Curved function has longer arc than a straight line between same endpoints."""
        straight = ax.get_graph_length(lambda x: x, 0, 3)
        curved = ax.get_graph_length(lambda x: math.sin(x * 2) + x, 0, 3)
        assert curved > straight * 0.9  # curved should be at least as long


# -- get_point_on_graph --

class TestGetPointOnGraph:
    def test_error_returns_none(self, ax):
        def bad(x):
            raise ValueError("boom")
        assert ax.get_point_on_graph(bad, 0) is None

    def test_matches_coords_to_point(self, ax):
        f = lambda x: x + 1
        pt = ax.get_point_on_graph(f, 2)
        expected = ax.coords_to_point(2, 3)
        assert abs(pt[0] - expected[0]) < 1
        assert abs(pt[1] - expected[1]) < 1


# -- get_vertical_line / get_line_from_to --

class TestLineHelpers:
    def test_get_vertical_line(self, ax, canvas):
        canvas.add(ax)
        ax.get_vertical_line(2)
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_get_line_from_to(self, ax, canvas):
        canvas.add(ax)
        ax.get_line_from_to(0, 0, 3, 4)
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg


# -- highlight_x_range / highlight_y_range --

class TestHighlightRanges:
    def test_highlight_x_range(self, ax, canvas):
        canvas.add(ax)
        ax.highlight_x_range(1, 3)
        svg = canvas.generate_frame_svg(time=0)
        assert '<rect' in svg

    def test_highlight_y_range(self, ax, canvas):
        canvas.add(ax)
        ax.highlight_y_range(-2, 2)
        svg = canvas.generate_frame_svg(time=0)
        assert '<rect' in svg


# -- add_dot_label --

class TestAddDotLabel:
    def test_no_label_text(self, ax, canvas):
        canvas.add(ax)
        _, lbl = ax.add_dot_label(1, 1)
        assert lbl is None

    def test_renders_in_svg(self, ax, canvas):
        canvas.add(ax)
        ax.add_dot_label(0, 0, label='Origin')
        svg = canvas.generate_frame_svg(time=0)
        assert 'Origin' in svg


# -- add_legend --

class TestAddLegend:
    def test_basic_legend(self, ax, canvas):
        canvas.add(ax)
        ax.add_legend([('sin', '#FF0000'), ('cos', '#0000FF')])
        svg = canvas.generate_frame_svg(time=0)
        assert 'sin' in svg
        assert 'cos' in svg


# -- add_coordinates / add_grid --

class TestAxesDecorations:
    def test_add_coordinates(self, ax, canvas):
        canvas.add(ax)
        ax.add_coordinates()
        svg = canvas.generate_frame_svg(time=0)
        assert '<text' in svg

    def test_add_grid(self, ax, canvas):
        canvas.add(ax)
        ax.add_grid()
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg


# -- get_area (visual) --

class TestGetAreaVisual:
    def test_get_area_returns_path(self, ax, canvas):
        canvas.add(ax)
        curve = ax.plot(lambda x: x**2)
        ax.get_area(curve)
        svg = canvas.generate_frame_svg(time=0)
        assert '<path' in svg

    def test_get_area_between(self, ax, canvas):
        canvas.add(ax)
        ax.get_area_between(lambda x: x, lambda x: x**2, x_range=(0, 1))
        svg = canvas.generate_frame_svg(time=0)
        assert '<path' in svg
