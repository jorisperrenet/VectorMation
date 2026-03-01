"""Extended tests for chart classes with minimal coverage."""
from vectormation.objects import (
    DonutChart, SparkLine, KPICard, BulletChart,
    CalendarHeatmap, WaffleChart, CircularProgressBar,
    Scoreboard, MatrixHeatmap, BoxPlot,
    FunnelChart, TreeMap, SankeyDiagram, GanttChart,
)


class TestDonutChart:
    def test_basic(self):
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

    def test_custom_radii(self):
        d = DonutChart([50, 50], r=200, inner_radius=80)
        svg = d.to_svg(0)
        assert svg is not None

    def test_get_sector(self):
        d = DonutChart([30, 50, 20])
        s = d.get_sector(0)
        assert s is not None

    def test_highlight_sector(self):
        d = DonutChart([30, 50, 20])
        result = d.highlight_sector(0, start=0, end=1)
        assert result is d

    def test_animate_values(self):
        d = DonutChart([30, 50, 20])
        result = d.animate_values([40, 40, 20], start=0, end=1)
        assert result is d

    def test_animate_values_wrong_length(self):
        d = DonutChart([30, 50, 20])
        import pytest
        with pytest.raises(ValueError, match="expects 3 values"):
            d.animate_values([40, 60])

    def test_from_dict(self):
        d = DonutChart.from_dict({'A': 30, 'B': 50, 'C': 20})
        svg = d.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        d = DonutChart([100])
        svg = d.to_svg(0)
        assert svg is not None

    def test_all_zeros(self):
        d = DonutChart([0, 0, 0])
        svg = d.to_svg(0)
        assert svg is not None


class TestSparkLine:
    def test_basic(self):
        s = SparkLine([1, 3, 2, 5, 4])
        svg = s.to_svg(0)
        assert 'path' in svg.lower()

    def test_show_endpoint(self):
        s = SparkLine([1, 2, 3], show_endpoint=True)
        svg = s.to_svg(0)
        assert 'circle' in svg.lower()

    def test_custom_size(self):
        s = SparkLine([10, 20, 30], width=200, height=50)
        svg = s.to_svg(0)
        assert svg is not None

    def test_two_points(self):
        s = SparkLine([0, 10])
        svg = s.to_svg(0)
        assert svg is not None

    def test_constant_values(self):
        s = SparkLine([5, 5, 5, 5])
        svg = s.to_svg(0)
        assert svg is not None

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

    def test_with_trend(self):
        k = KPICard(title='Sales', value=500, trend_data=[10, 20, 15, 30, 25])
        svg = k.to_svg(0)
        assert svg is not None

    def test_custom_colors(self):
        k = KPICard(title='T', value=1, bg_color='#333', value_color='#0F0')
        svg = k.to_svg(0)
        assert svg is not None


class TestBulletChart:
    def test_basic(self):
        b = BulletChart(actual=75, target=90)
        svg = b.to_svg(0)
        assert 'rect' in svg

    def test_with_label(self):
        b = BulletChart(actual=50, target=80, label='Performance')
        svg = b.to_svg(0)
        assert 'Performance' in svg

    def test_custom_ranges(self):
        b = BulletChart(actual=60, target=80,
                        ranges=[(30, '#d32f2f'), (60, '#ffa726'), (100, '#66bb6a')])
        svg = b.to_svg(0)
        assert svg is not None

    def test_exceeds_target(self):
        b = BulletChart(actual=100, target=80)
        svg = b.to_svg(0)
        assert svg is not None

    def test_zero_actual(self):
        b = BulletChart(actual=0, target=50)
        svg = b.to_svg(0)
        assert svg is not None

    def test_custom_max(self):
        b = BulletChart(actual=150, target=200, max_val=300)
        svg = b.to_svg(0)
        assert svg is not None


class TestCalendarHeatmap:
    def test_basic_list(self):
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

    def test_single_value(self):
        ch = CalendarHeatmap({(0, 0): 5})
        svg = ch.to_svg(0)
        assert svg is not None

    def test_custom_colormap(self):
        ch = CalendarHeatmap(list(range(50)), rows=5, cols=10,
                             colormap=['#eee', '#bbb', '#888', '#444', '#000'])
        svg = ch.to_svg(0)
        assert svg is not None

    def test_custom_cell_size(self):
        ch = CalendarHeatmap(list(range(20)), rows=4, cols=5, cell_size=20, gap=3)
        svg = ch.to_svg(0)
        assert svg is not None


class TestWaffleChart:
    def test_basic(self):
        cats = [('A', 30, '#3498DB'), ('B', 70, '#E74C3C')]
        wc = WaffleChart(cats)
        svg = wc.to_svg(0)
        assert 'rect' in svg
        assert 'A' in svg

    def test_three_categories(self):
        cats = [('X', 20, '#ff0000'), ('Y', 30, '#00ff00'), ('Z', 50, '#0000ff')]
        wc = WaffleChart(cats)
        svg = wc.to_svg(0)
        assert svg is not None

    def test_custom_grid_size(self):
        cats = [('A', 50, '#fff')]
        wc = WaffleChart(cats, grid_size=5)
        svg = wc.to_svg(0)
        assert svg is not None

    def test_single_category_100pct(self):
        cats = [('All', 100, '#58C4DD')]
        wc = WaffleChart(cats)
        svg = wc.to_svg(0)
        assert svg is not None


class TestCircularProgressBar:
    def test_basic(self):
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

    def test_custom_colors(self):
        cp = CircularProgressBar(50, track_color='#000', bar_color='#f00')
        svg = cp.to_svg(0)
        assert svg is not None


class TestScoreboard:
    def test_basic(self):
        s = Scoreboard([('Score', 100), ('Level', 5)])
        svg = s.to_svg(0)
        assert '100' in svg
        assert 'Score' in svg

    def test_many_entries(self):
        entries = [(f'Metric{i}', i * 10) for i in range(8)]
        s = Scoreboard(entries)
        svg = s.to_svg(0)
        assert svg is not None

    def test_custom_cols(self):
        s = Scoreboard([('A', 1), ('B', 2), ('C', 3)], cols=3)
        svg = s.to_svg(0)
        assert svg is not None

    def test_empty(self):
        s = Scoreboard([])
        assert len(s) == 0

    def test_single_entry(self):
        s = Scoreboard([('Only', 42)])
        svg = s.to_svg(0)
        assert '42' in svg


class TestMatrixHeatmap:
    def test_basic(self):
        mh = MatrixHeatmap([[1, 2], [3, 4]])
        svg = mh.to_svg(0)
        assert 'rect' in svg

    def test_with_labels(self):
        mh = MatrixHeatmap([[1, 2], [3, 4]],
                           row_labels=['R1', 'R2'], col_labels=['C1', 'C2'])
        svg = mh.to_svg(0)
        assert 'R1' in svg
        assert 'C1' in svg

    def test_no_values(self):
        mh = MatrixHeatmap([[1, 2], [3, 4]], show_values=False)
        svg = mh.to_svg(0)
        assert svg is not None

    def test_uniform_data(self):
        mh = MatrixHeatmap([[5, 5], [5, 5]])
        svg = mh.to_svg(0)
        assert svg is not None

    def test_single_cell(self):
        mh = MatrixHeatmap([[42]])
        svg = mh.to_svg(0)
        assert svg is not None

    def test_empty_data(self):
        mh = MatrixHeatmap([])
        assert len(mh) == 0


class TestBoxPlot:
    def test_basic(self):
        bp = BoxPlot([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        svg = bp.to_svg(0)
        assert svg is not None

    def test_multiple_groups(self):
        data = [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50], [5, 10, 15, 20, 25]]
        bp = BoxPlot(data)
        svg = bp.to_svg(0)
        assert svg is not None

    def test_custom_positions(self):
        bp = BoxPlot([[1, 2, 3, 4, 5]], positions=[3])
        svg = bp.to_svg(0)
        assert svg is not None

    def test_empty_data(self):
        bp = BoxPlot([])
        assert len(bp) == 0

    def test_identical_values(self):
        bp = BoxPlot([[5, 5, 5, 5, 5]])
        svg = bp.to_svg(0)
        assert svg is not None

    def test_custom_colors(self):
        bp = BoxPlot([[1, 2, 3, 4, 5]], box_color='#ff0000', median_color='#00ff00')
        svg = bp.to_svg(0)
        assert svg is not None


class TestFunnelChartFromDict:
    def test_basic(self):
        fc = FunnelChart.from_dict({'Visits': 1000, 'Signups': 400, 'Purchases': 100})
        svg = fc.to_svg(0)
        assert 'Visits' in svg
        assert 'Signups' in svg
        assert 'Purchases' in svg

    def test_empty(self):
        fc = FunnelChart.from_dict({})
        svg = fc.to_svg(0)
        assert svg is not None

    def test_single_entry(self):
        fc = FunnelChart.from_dict({'Only': 50})
        svg = fc.to_svg(0)
        assert 'Only' in svg

    def test_kwargs_forwarded(self):
        fc = FunnelChart.from_dict({'A': 10, 'B': 5}, width=400, gap=8)
        svg = fc.to_svg(0)
        assert svg is not None


class TestTreeMapFromDict:
    def test_basic(self):
        tm = TreeMap.from_dict({'Cats': 40, 'Dogs': 30, 'Birds': 20, 'Fish': 10})
        svg = tm.to_svg(0)
        assert svg is not None

    def test_empty(self):
        tm = TreeMap.from_dict({})
        svg = tm.to_svg(0)
        assert svg is not None

    def test_single_entry(self):
        tm = TreeMap.from_dict({'Only': 100})
        svg = tm.to_svg(0)
        assert svg is not None

    def test_kwargs_forwarded(self):
        tm = TreeMap.from_dict({'A': 50, 'B': 30}, width=600, height=400)
        svg = tm.to_svg(0)
        assert svg is not None

    def test_labels_visible(self):
        tm = TreeMap.from_dict({'BigItem': 90, 'SmallItem': 10})
        svg = tm.to_svg(0)
        # The big item should get a label if it has enough space
        assert 'BigItem' in svg


class TestGanttChartExtended:
    def test_empty_tasks(self):
        gc = GanttChart([])
        svg = gc.to_svg(0)
        assert svg is not None

    def test_single_task(self):
        gc = GanttChart([('Task A', 0, 5)])
        svg = gc.to_svg(0)
        assert 'Task A' in svg

    def test_overlapping_tasks(self):
        gc = GanttChart([('Task A', 0, 5), ('Task B', 3, 8)])
        svg = gc.to_svg(0)
        assert 'Task A' in svg
        assert 'Task B' in svg


class TestSankeyDiagramExtended:
    def test_empty_flows(self):
        sd = SankeyDiagram([])
        svg = sd.to_svg(0)
        assert svg is not None

    def test_single_flow(self):
        sd = SankeyDiagram([('A', 'B', 100)])
        svg = sd.to_svg(0)
        assert svg is not None

    def test_multiple_flows(self):
        sd = SankeyDiagram([('A', 'B', 50), ('A', 'C', 30), ('B', 'D', 40)])
        svg = sd.to_svg(0)
        assert svg is not None
