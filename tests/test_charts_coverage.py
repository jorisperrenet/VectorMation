"""Tests for chart classes with weak or missing coverage: PolarAxes, Legend, BarChart methods."""
from vectormation.objects import BarChart, PolarAxes, Legend


# -- PolarAxes -----------------------------------------------------------------

class TestPolarAxes:
    def test_polar_to_point_at_angle(self):
        pa = PolarAxes(r_range=(0, 5))
        p0 = pa.polar_to_point(3, 0)
        p90 = pa.polar_to_point(3, 90)
        # Different angles should give different points
        assert p0 != p90


# -- Legend --------------------------------------------------------------------

class TestLegend:
    def test_single_item(self):
        lg = Legend([('#58C4DD', 'Data')])
        svg = lg.to_svg(0)
        assert 'Data' in svg


# -- BarChart untested methods -------------------------------------------------

class TestBarChartMethods:
    def _make_chart(self):
        return BarChart(values=[3, 7, 2, 5], labels=['A', 'B', 'C', 'D'])

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
