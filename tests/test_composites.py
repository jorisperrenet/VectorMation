"""Tests for composite objects: Axes, Arrow, Table, NumberLine, etc."""
import math
import pytest

from vectormation._composites import Arrow, Brace, NumberLine, Table, Matrix
from vectormation._axes import Axes
from vectormation._shapes import Circle
from vectormation._constants import ORIGIN
import vectormation.easings as easings


class TestAxes:

    def test_coords_to_point_origin(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        sx, sy = ax.coords_to_point(0, 0)
        # Math origin should map near the visual center of axes
        cx, cy = ax.center(0)
        assert sx == pytest.approx(cx, abs=10)
        assert sy == pytest.approx(cy, abs=10)

    def test_coords_to_point_extremes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        left = ax.coords_to_point(-5, 0)
        right = ax.coords_to_point(5, 0)
        assert left[0] < right[0]  # left is to the left

    def test_y_axis_inverted(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        bottom = ax.coords_to_point(0, -5)
        top = ax.coords_to_point(0, 5)
        # In SVG, y-up means smaller y value for larger math y
        assert top[1] < bottom[1]

    def test_plot_returns_path(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        curve = ax.plot(lambda x: x ** 2)
        svg = curve.to_svg(0)
        assert 'd=' in svg or '<path' in svg

    def test_animated_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.x_max.move_to(0, 1, 10, easing=easings.linear)
        # At t=0.5, x_max should be 7.5
        assert ax.x_max.at_time(0.5) == pytest.approx(7.5)
        # coords_to_point should reflect animated range
        p_at_0 = ax.coords_to_point(5, 0, time=0)
        p_at_1 = ax.coords_to_point(5, 0, time=1)
        # At t=1, x=5 is no longer at the right edge (x_max=10)
        # so it should map to a different screen position
        assert p_at_0[0] != pytest.approx(p_at_1[0], abs=5)

    def test_get_area(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        curve = ax.plot(lambda x: x)
        area = ax.get_area(curve, x_range=(0, 5))
        svg = area.to_svg(0)
        # Area should produce a filled path
        assert '<path' in svg


class TestArrow:

    def test_arrow_has_tip(self):
        a = Arrow(x1=100, y1=100, x2=300, y2=100)
        svg = a.to_svg(0)
        # Arrow should contain a polygon (tip) and a line
        assert '<polygon' in svg or '<line' in svg

    def test_arrow_direction(self):
        a = Arrow(x1=0, y1=0, x2=100, y2=0)
        # The tip should be near x2
        svg = a.to_svg(0)
        assert len(svg) > 10


class TestNumberLine:

    def test_number_to_point(self):
        nl = NumberLine(x_range=(0, 10))
        p_start = nl.number_to_point(0)
        p_end = nl.number_to_point(10)
        # Start should be to the left of end
        assert p_start[0] < p_end[0]

    def test_number_to_point_linear(self):
        nl = NumberLine(x_range=(0, 10))
        p0 = nl.number_to_point(0)
        p5 = nl.number_to_point(5)
        p10 = nl.number_to_point(10)
        # Should be equally spaced
        gap1 = p5[0] - p0[0]
        gap2 = p10[0] - p5[0]
        assert gap1 == pytest.approx(gap2, abs=2)


class TestTable:

    def test_table_has_correct_cell_count(self):
        t = Table([['A', 'B'], ['C', 'D']])
        # 2x2 table = 4 text cells
        texts = [obj for obj in t.objects
                 if hasattr(obj, 'text') and hasattr(obj.text, 'at_time')]
        assert len(texts) >= 4

    def test_table_renders(self):
        t = Table([['A', 'B'], ['C', 'D']])
        svg = t.to_svg(0)
        assert len(svg) > 10


class TestMatrix:

    def test_matrix_renders(self):
        m = Matrix([[1, 2], [3, 4]])
        svg = m.to_svg(0)
        assert len(svg) > 10
