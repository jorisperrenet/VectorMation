"""Tests for Axes plotting methods: scatter, step, polar, implicit, histogram."""
import math
from vectormation.objects import Axes


class TestPlotScatter:
    def test_point_count(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.plot_scatter([1, 2, 3], [1, 4, 9])
        assert len(result) == 3

    def test_single_point(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_scatter([5], [5])
        assert len(result) == 1

    def test_renders_circles(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_scatter([1, 2, 3], [3, 2, 1])
        svg = ax.to_svg(0)
        assert 'circle' in svg


class TestPlotStep:
    def test_renders(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        ax.plot_step([0, 1, 2, 3], [1, 3, 2, 4])
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()


class TestPlotPolar:
    def test_renders(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_polar(lambda theta: 2)
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()


class TestPlotImplicit:
    def test_renders(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_implicit(lambda x, y: x**2 + y**2 - 4, num_points=20)
        svg = ax.to_svg(0)
        assert 'path' in svg.lower()


class TestPlotHistogram:
    def test_empty_data(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_histogram([], bins=5)
        assert len(result) == 0

    def test_renders_rects(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_histogram([1, 2, 3, 4, 5, 6, 7, 8, 9], bins=3)
        svg = ax.to_svg(0)
        assert 'rect' in svg.lower()


class TestPlotColorShorthand:
    def test_color_maps_to_stroke(self):
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        ax.plot(math.sin, color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_stroke_takes_precedence(self):
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        ax.plot(math.sin, color='#FF0000', stroke='#00FF00')
        svg = ax.to_svg(0)
        assert 'rgb(0,255,0)' in svg or 'rgb(0, 255, 0)' in svg

    def test_parametric_color(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_parametric(lambda t: (math.cos(t), math.sin(t)),
                           t_range=(0, math.tau), color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_polar_color(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_polar(lambda theta: 2, color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_implicit_color(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        ax.plot_implicit(lambda x, y: x**2 + y**2 - 1, color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_step_color(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        ax.plot_step([0, 1, 2], [1, 3, 2], color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_scatter_color_maps_to_fill(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_scatter([1, 2], [3, 4], color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_histogram_color(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot_histogram([1, 2, 3, 4, 5], bins=3, color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_line_graph_color(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        ax.plot_line_graph([0, 1, 2], [1, 3, 2], color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg

    def test_filled_step_color(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        ax.plot_filled_step([0, 1, 2], [1, 3, 2], color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'rgb(255, 0, 0)' in svg
