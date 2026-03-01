"""Tests for Axes plotting methods: scatter, step, polar, implicit, histogram."""
import math
from vectormation.objects import Axes, VCollection, Path


class TestPlotScatter:
    def test_basic(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.plot_scatter([1, 2, 3], [1, 4, 9])
        assert isinstance(result, VCollection)
        assert len(result) == 3

    def test_single_point(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_scatter([5], [5])
        assert len(result) == 1

    def test_custom_radius(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_scatter([1, 2], [3, 4], r=10)
        assert len(result) == 2

    def test_renders(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_scatter([1, 2, 3], [3, 2, 1])
        svg = ax.to_svg(0)
        assert 'circle' in svg


class TestPlotStep:
    def test_basic(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        result = ax.plot_step([0, 1, 2, 3, 4], [2, 5, 3, 8, 1])
        assert isinstance(result, Path)

    def test_renders(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        ax.plot_step([0, 1, 2, 3], [1, 3, 2, 4])
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()

    def test_single_point(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        result = ax.plot_step([2], [3])
        assert isinstance(result, Path)


class TestPlotFilledStep:
    def test_basic(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        result = ax.plot_filled_step([0, 1, 2, 3], [2, 5, 3, 8])
        assert isinstance(result, Path)

    def test_custom_baseline(self):
        ax = Axes(x_range=(0, 5), y_range=(-5, 5))
        result = ax.plot_filled_step([0, 1, 2], [1, 3, 2], baseline=-1)
        assert isinstance(result, Path)


class TestPlotPolar:
    def test_circle(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        result = ax.plot_polar(lambda theta: 2)
        assert isinstance(result, Path)

    def test_cardioid(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        result = ax.plot_polar(lambda theta: 1 + math.cos(theta))
        assert isinstance(result, Path)

    def test_renders(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_polar(lambda theta: 2)
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()


class TestPlotImplicit:
    def test_circle(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        result = ax.plot_implicit(lambda x, y: x**2 + y**2 - 1)
        assert isinstance(result, Path)

    def test_renders(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_implicit(lambda x, y: x**2 + y**2 - 4, num_points=20)
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()


class TestPlotHistogram:
    def test_basic(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        data = [1, 2, 2, 3, 3, 3, 4, 5, 5, 6, 7, 8, 9]
        result = ax.plot_histogram(data, bins=5)
        assert isinstance(result, VCollection)

    def test_empty_data(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_histogram([], bins=5)
        assert isinstance(result, VCollection)
        assert len(result) == 0

    def test_single_value(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 5))
        result = ax.plot_histogram([5, 5, 5], bins=3)
        assert isinstance(result, VCollection)

    def test_renders(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_histogram([1, 2, 3, 4, 5, 6, 7, 8, 9], bins=3)
        svg = ax.to_svg(0)
        assert 'rect' in svg.lower()


class TestPlotColorShorthand:
    def test_color_maps_to_stroke(self):
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        import math
        curve = ax.plot(math.sin, color='#FF0000')
        assert isinstance(curve, Path)
        svg = ax.to_svg(0)
        # Color is rendered as rgb(255,0,0) by the styling system
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_stroke_takes_precedence(self):
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        import math
        ax.plot(math.sin, color='#FF0000', stroke='#00FF00')
        svg = ax.to_svg(0)
        # stroke= should win over color=
        assert 'rgb(0,255,0)' in svg or 'rgb(0, 255, 0)' in svg
