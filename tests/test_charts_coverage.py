"""Tests for chart classes with weak or missing coverage: PolarAxes, Legend, BarChart methods."""
import math
from vectormation.objects import (
    BarChart, PolarAxes, PieChart,
)
from vectormation.objects import Legend


# ── PolarAxes ───────────────────────────────────────────────────────────

class TestPolarAxes:
    def test_creation(self):
        pa = PolarAxes()
        svg = pa.to_svg(0)
        assert svg is not None

    def test_custom_params(self):
        pa = PolarAxes(max_radius=300, r_range=(0, 10), n_rings=3, n_sectors=6)
        svg = pa.to_svg(0)
        assert svg is not None

    def test_polar_to_point(self):
        pa = PolarAxes(r_range=(0, 5))
        x, y = pa.polar_to_point(0, 0)
        assert math.isfinite(x) and math.isfinite(y)

    def test_polar_to_point_at_angle(self):
        pa = PolarAxes(r_range=(0, 5))
        p0 = pa.polar_to_point(3, 0)
        p90 = pa.polar_to_point(3, 90)
        # Different angles should give different points
        assert p0 != p90

    def test_polar_to_point_zero_radius(self):
        pa = PolarAxes(r_range=(0, 5))
        x, y = pa.polar_to_point(0, 45)
        # At r=0, should be at center
        assert math.isfinite(x) and math.isfinite(y)

    def test_plot_polar_constant(self):
        pa = PolarAxes(r_range=(0, 5))
        pa.plot_polar(lambda theta: 3)
        svg = pa.to_svg(0)
        assert svg is not None

    def test_plot_polar_cardioid(self):
        pa = PolarAxes(r_range=(0, 3))
        pa.plot_polar(lambda theta: 1 + math.cos(math.radians(theta)))
        svg = pa.to_svg(0)
        assert svg is not None

    def test_plot_polar_custom_range(self):
        pa = PolarAxes(r_range=(0, 5))
        pa.plot_polar(lambda theta: 2, theta_range=(0, 180))
        svg = pa.to_svg(0)
        assert svg is not None

    def test_plot_polar_few_points(self):
        pa = PolarAxes(r_range=(0, 5))
        pa.plot_polar(lambda theta: 1, num_points=5)
        svg = pa.to_svg(0)
        assert svg is not None

    def test_repr(self):
        pa = PolarAxes()
        r = repr(pa)
        assert r is not None


# ── Legend ──────────────────────────────────────────────────────────────

class TestLegend:
    def test_creation(self):
        lg = Legend([('#FF0000', 'Red'), ('#00FF00', 'Green')])
        svg = lg.to_svg(0)
        assert svg is not None

    def test_single_item(self):
        lg = Legend([('#58C4DD', 'Data')])
        svg = lg.to_svg(0)
        assert 'Data' in svg

    def test_many_items(self):
        items = [(f'#{i:02x}{i:02x}{i:02x}', f'Item {i}') for i in range(5)]
        lg = Legend(items)
        svg = lg.to_svg(0)
        assert svg is not None

    def test_horizontal_direction(self):
        lg = Legend([('#FF0000', 'A'), ('#00FF00', 'B')], direction='right')
        svg = lg.to_svg(0)
        assert svg is not None

    def test_custom_position(self):
        lg = Legend([('#FF0000', 'Test')], x=500, y=300)
        svg = lg.to_svg(0)
        assert svg is not None

    def test_custom_font_size(self):
        lg = Legend([('#FF0000', 'Big')], font_size=24)
        svg = lg.to_svg(0)
        assert svg is not None

    def test_custom_swatch_size(self):
        lg = Legend([('#FF0000', 'Test')], swatch_size=24, spacing=12)
        svg = lg.to_svg(0)
        assert svg is not None


# ── BarChart untested methods ───────────────────────────────────────────

class TestBarChartMethods:
    def _make_chart(self):
        return BarChart(values=[3, 7, 2, 5], labels=['A', 'B', 'C', 'D'])

    def test_set_bar_color(self):
        bc = self._make_chart()
        bc.set_bar_color(0, '#FF0000')
        svg = bc.to_svg(0)
        assert svg is not None

    def test_set_bar_color_negative_index(self):
        bc = self._make_chart()
        bc.set_bar_color(-1, '#00FF00')
        svg = bc.to_svg(0)
        assert svg is not None

    def test_set_bar_color_animated(self):
        bc = self._make_chart()
        bc.set_bar_color(1, '#0000FF', start=0, end=1)
        svg0 = bc.to_svg(0)
        svg1 = bc.to_svg(1)
        assert svg0 is not None
        assert svg1 is not None

    def test_set_bar_colors(self):
        bc = self._make_chart()
        bc.set_bar_colors(['#FF0000', '#00FF00', '#0000FF', '#FFFF00'])
        svg = bc.to_svg(0)
        assert svg is not None

    def test_set_bar_colors_fewer(self):
        bc = self._make_chart()
        bc.set_bar_colors(['#FF0000', '#00FF00'])  # fewer than bars
        svg = bc.to_svg(0)
        assert svg is not None

    def test_get_bar(self):
        bc = self._make_chart()
        bar = bc.get_bar(0)
        assert bar is not None

    def test_get_bar_last(self):
        bc = self._make_chart()
        bar = bc.get_bar(-1)
        assert bar is not None

    def test_get_bars_all(self):
        bc = self._make_chart()
        bars = bc.get_bars()
        assert len(bars.objects) == 4

    def test_get_bars_slice(self):
        bc = self._make_chart()
        bars = bc.get_bars(1, 3)
        assert len(bars.objects) == 2

    def test_get_bar_by_label(self):
        bc = self._make_chart()
        bar = bc.get_bar_by_label('B')
        assert bar is not None

    def test_get_bar_by_label_missing(self):
        bc = self._make_chart()
        bar = bc.get_bar_by_label('Z')
        assert bar is None

    def test_grow_from_zero(self):
        bc = self._make_chart()
        bc.grow_from_zero(start=0, end=2)
        svg = bc.to_svg(1)
        assert svg is not None

    def test_grow_from_zero_no_stagger(self):
        bc = self._make_chart()
        bc.grow_from_zero(start=0, end=1, stagger=False)
        svg = bc.to_svg(0.5)
        assert svg is not None

    def test_get_max_bar(self):
        bc = self._make_chart()
        bar = bc.get_max_bar()
        assert bar is not None

    def test_get_min_bar(self):
        bc = self._make_chart()
        bar = bc.get_min_bar()
        assert bar is not None

    def test_get_max_bar_empty(self):
        bc = BarChart(values=[])
        bar = bc.get_max_bar()
        assert bar is None

    def test_animate_sort(self):
        bc = self._make_chart()
        bc.animate_sort(start=0, end=2)
        svg = bc.to_svg(1)
        assert svg is not None

    def test_animate_sort_reverse(self):
        bc = self._make_chart()
        bc.animate_sort(reverse=True, start=0, end=1)
        svg = bc.to_svg(0.5)
        assert svg is not None

    def test_animate_sort_custom_key(self):
        bc = self._make_chart()
        bc.animate_sort(key=lambda v: -v, start=0, end=1)
        svg = bc.to_svg(1)
        assert svg is not None


# ── PieChart untested methods ───────────────────────────────────────────

class TestPieChartMethods:
    def test_sweep_in(self):
        pc = PieChart(values=[3, 5, 2], labels=['A', 'B', 'C'])
        pc.sweep_in(start=0, end=2)
        svg = pc.to_svg(1)
        assert svg is not None

    def test_add_percentage_labels(self):
        pc = PieChart(values=[30, 50, 20], labels=['A', 'B', 'C'])
        pc.add_percentage_labels()
        svg = pc.to_svg(0)
        assert svg is not None
