"""Extended tests for chart classes with minimal coverage."""
import pytest
from vectormation.objects import (
    DonutChart, SparkLine, KPICard, BulletChart,
    CalendarHeatmap, WaffleChart, CircularProgressBar,
    Scoreboard, MatrixHeatmap, BoxPlot,
    FunnelChart, TreeMap, GanttChart,
)


class TestDonutChart:
    def test_renders_paths(self):
        d = DonutChart([30, 50, 20])
        svg = d.to_svg(0)
        assert 'path' in svg.lower()

    def test_with_labels(self):
        d = DonutChart([30, 50, 20], labels=['A', 'B', 'C'])
        svg = d.to_svg(0)
        assert 'A' in svg

    def test_center_text(self):
        d = DonutChart([60, 40], center_text='Total')
        svg = d.to_svg(0)
        assert 'Total' in svg

    def test_animate_values_wrong_length(self):
        d = DonutChart([30, 50, 20])
        with pytest.raises(ValueError, match="expects 3 values"):
            d.animate_values([40, 60])


class TestSparkLine:
    def test_renders_path(self):
        s = SparkLine([1, 3, 2, 5, 4])
        svg = s.to_svg(0)
        assert 'path' in svg.lower()

    def test_show_endpoint(self):
        s = SparkLine([1, 2, 3], show_endpoint=True)
        svg = s.to_svg(0)
        assert 'circle' in svg.lower()

    def test_snap_points(self):
        s = SparkLine([1, 2, 3], x=100, y=100, width=120, height=30)
        pts = s.snap_points(0)
        assert len(pts) >= 2


class TestKPICard:
    def test_basic(self):
        k = KPICard(title='Revenue', value=42000)
        svg = k.to_svg(0)
        assert 'Revenue' in svg
        assert '42000' in svg

    def test_with_subtitle(self):
        k = KPICard(title='Users', value=1200, subtitle='Active')
        svg = k.to_svg(0)
        assert 'Active' in svg


class TestBulletChart:
    def test_renders_rects(self):
        b = BulletChart(actual=75, target=90)
        svg = b.to_svg(0)
        assert 'rect' in svg

    def test_with_label(self):
        b = BulletChart(actual=50, target=80, label='Performance')
        svg = b.to_svg(0)
        assert 'Performance' in svg


class TestCalendarHeatmap:
    def test_renders_rects(self):
        data = list(range(100))
        ch = CalendarHeatmap(data, rows=7, cols=15)
        svg = ch.to_svg(0)
        assert 'rect' in svg

    def test_dict_data(self):
        data = {(0, 0): 1, (1, 1): 5, (2, 2): 10}
        ch = CalendarHeatmap(data)
        svg = ch.to_svg(0)
        assert 'rect' in svg

    def test_empty_data(self):
        ch = CalendarHeatmap({})
        assert len(ch) == 0


class TestWaffleChart:
    def test_renders_with_labels(self):
        cats = [('A', 30, '#3498DB'), ('B', 70, '#E74C3C')]
        wc = WaffleChart(cats)
        svg = wc.to_svg(0)
        assert 'rect' in svg
        assert 'A' in svg


class TestCircularProgressBar:
    def test_percentage_text(self):
        cp = CircularProgressBar(75)
        svg = cp.to_svg(0)
        assert '75%' in svg

    def test_zero(self):
        cp = CircularProgressBar(0)
        svg = cp.to_svg(0)
        assert '0%' in svg

    def test_full(self):
        cp = CircularProgressBar(100)
        svg = cp.to_svg(0)
        assert '100%' in svg

    def test_clamped_over_100(self):
        cp = CircularProgressBar(150)
        svg = cp.to_svg(0)
        assert '100%' in svg

    def test_clamped_negative(self):
        cp = CircularProgressBar(-10)
        svg = cp.to_svg(0)
        assert '0%' in svg

    def test_no_text(self):
        cp = CircularProgressBar(50, show_text=False)
        svg = cp.to_svg(0)
        assert '50%' not in svg


class TestScoreboard:
    def test_basic(self):
        s = Scoreboard([('Score', 100), ('Level', 5)])
        svg = s.to_svg(0)
        assert '100' in svg
        assert 'Score' in svg

    def test_empty(self):
        s = Scoreboard([])
        assert len(s) == 0

    def test_single_entry(self):
        s = Scoreboard([('Only', 42)])
        svg = s.to_svg(0)
        assert '42' in svg


class TestMatrixHeatmap:
    def test_renders_rects(self):
        mh = MatrixHeatmap([[1, 2], [3, 4]])
        svg = mh.to_svg(0)
        assert 'rect' in svg

    def test_with_labels(self):
        mh = MatrixHeatmap([[1, 2], [3, 4]],
                           row_labels=['R1', 'R2'], col_labels=['C1', 'C2'])
        svg = mh.to_svg(0)
        assert 'R1' in svg
        assert 'C1' in svg

    def test_empty_data(self):
        mh = MatrixHeatmap([])
        assert len(mh) == 0


class TestBoxPlot:
    def test_empty_data(self):
        bp = BoxPlot([])
        assert len(bp) == 0


class TestFunnelChartFromDict:
    def test_labels_visible(self):
        fc = FunnelChart.from_dict({'Visits': 1000, 'Signups': 400, 'Purchases': 100})
        svg = fc.to_svg(0)
        assert 'Visits' in svg
        assert 'Signups' in svg
        assert 'Purchases' in svg

    def test_single_entry(self):
        fc = FunnelChart.from_dict({'Only': 50})
        svg = fc.to_svg(0)
        assert 'Only' in svg


class TestTreeMapFromDict:
    def test_labels_visible(self):
        tm = TreeMap.from_dict({'BigItem': 90, 'SmallItem': 10})
        svg = tm.to_svg(0)
        assert 'BigItem' in svg


class TestGanttChartExtended:
    def test_single_task(self):
        gc = GanttChart([('Task A', 0, 5)])
        svg = gc.to_svg(0)
        assert 'Task A' in svg

    def test_overlapping_tasks(self):
        gc = GanttChart([('Task A', 0, 5), ('Task B', 3, 8)])
        svg = gc.to_svg(0)
        assert 'Task A' in svg
        assert 'Task B' in svg
