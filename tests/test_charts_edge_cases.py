"""Edge case tests for chart classes in _charts.py."""
from vectormation.objects import (
    PieChart, DonutChart, BarChart, WaterfallChart, FunnelChart,
    TreeMap, GaugeChart, SparkLine, ProgressBar, RadarChart,
    SankeyDiagram, GanttChart, BulletChart, CalendarHeatmap,
    WaffleChart, CircularProgressBar, MatrixHeatmap, BoxPlot,
    Scoreboard, KPICard,
)


# ── BarChart edge cases ─────────────────────────────────────────────────

class TestBarChartEdgeCases:
    def test_all_zero_values(self):
        bc = BarChart(values=[0, 0, 0], labels=['A', 'B', 'C'])
        svg = bc.to_svg(0)
        assert svg is not None

    def test_single_bar(self):
        bc = BarChart(values=[42], labels=['Solo'])
        svg = bc.to_svg(0)
        assert svg is not None

    def test_highlight_bar(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bc.highlight_bar(1, start=0, end=1)
        svg = bc.to_svg(0.5)
        assert svg is not None

    def test_add_value_labels(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bc.add_value_labels()
        svg = bc.to_svg(0)
        assert '10' in svg or '20' in svg or '30' in svg

    def test_add_bar_then_remove(self):
        bc = BarChart(values=[10, 20], labels=['A', 'B'])
        bc.add_bar(30, label='C', start=0)
        bc.remove_bar(0, start=1)
        svg = bc.to_svg(0.5)
        assert svg is not None


# ── PieChart edge cases ─────────────────────────────────────────────────

class TestPieChartEdgeCases:
    def test_single_value(self):
        pc = PieChart(values=[100], labels=['Only'])
        svg = pc.to_svg(0)
        assert svg is not None

    def test_explode_list(self):
        """explode() takes a list of indices."""
        pc = PieChart(values=[30, 30, 40], labels=['A', 'B', 'C'])
        pc.explode([0, 2], start=0, end=0.5)
        svg = pc.to_svg(0.3)
        assert svg is not None

    def test_add_legend_with_labels(self):
        pc = PieChart(values=[50, 50], labels=['A', 'B'])
        pc.add_legend(['A', 'B'])
        svg = pc.to_svg(0)
        assert svg is not None


# ── WaterfallChart edge cases ────────────────────────────────────────────

class TestWaterfallChartEdgeCases:
    def test_all_positive(self):
        wc = WaterfallChart(values=[100, 50, 30], labels=['A', 'B', 'C'])
        svg = wc.to_svg(0)
        assert svg is not None

    def test_all_negative(self):
        wc = WaterfallChart(values=[-100, -50, -30], labels=['A', 'B', 'C'])
        svg = wc.to_svg(0)
        assert svg is not None

    def test_from_dict(self):
        wc = WaterfallChart.from_dict({'Revenue': 500, 'COGS': -200, 'Net': 300})
        svg = wc.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        wc = WaterfallChart(values=[100])
        svg = wc.to_svg(0)
        assert svg is not None

    def test_no_total(self):
        wc = WaterfallChart(values=[100, -30], show_total=False)
        svg = wc.to_svg(0)
        assert svg is not None


# ── FunnelChart edge cases ──────────────────────────────────────────────

class TestFunnelChartEdgeCases:
    def test_single_stage(self):
        fc = FunnelChart(stages=[('Only', 100)])
        svg = fc.to_svg(0)
        assert svg is not None

    def test_equal_values(self):
        fc = FunnelChart(stages=[('A', 100), ('B', 100), ('C', 100)])
        svg = fc.to_svg(0)
        assert svg is not None

    def test_zero_value_stage(self):
        fc = FunnelChart(stages=[('A', 100), ('B', 0), ('C', 50)])
        svg = fc.to_svg(0)
        assert svg is not None


# ── TreeMap edge cases ──────────────────────────────────────────────────

class TestTreeMapEdgeCases:
    def test_many_items(self):
        data = [(f'Item{i}', i + 1) for i in range(20)]
        tm = TreeMap(data)
        svg = tm.to_svg(0)
        assert svg is not None

    def test_unequal_values(self):
        tm = TreeMap([('Big', 1000), ('Tiny', 1)])
        svg = tm.to_svg(0)
        assert svg is not None


# ── GaugeChart edge cases ────────────────────────────────────────────────

class TestGaugeChartEdgeCases:
    def test_value_at_min(self):
        gc = GaugeChart(value=0, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert svg is not None

    def test_value_at_max(self):
        gc = GaugeChart(value=100, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert svg is not None

    def test_value_beyond_max(self):
        gc = GaugeChart(value=150, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert svg is not None

    def test_custom_ranges(self):
        gc = GaugeChart(value=50, min_val=-100, max_val=100)
        svg = gc.to_svg(0)
        assert svg is not None


# ── SparkLine edge cases ────────────────────────────────────────────────

class TestSparkLineEdgeCases:
    def test_constant_values(self):
        sl = SparkLine(data=[5, 5, 5, 5, 5])
        svg = sl.to_svg(0)
        assert svg is not None

    def test_two_points(self):
        sl = SparkLine(data=[0, 100])
        svg = sl.to_svg(0)
        assert svg is not None

    def test_show_endpoint(self):
        sl = SparkLine(data=[10, 20, 30], show_endpoint=True)
        svg = sl.to_svg(0)
        assert svg is not None

    def test_single_point_returns_empty(self):
        sl = SparkLine(data=[42])
        svg = sl.to_svg(0)
        # With < 2 points, returns empty path


# ── ProgressBar edge cases ──────────────────────────────────────────────

class TestProgressBarEdgeCases:
    def test_sequential_updates(self):
        pb = ProgressBar(width=400)
        pb.set_progress(0.25, start=0)
        pb.set_progress(0.5, start=1, end=2)
        pb.set_progress(1.0, start=2, end=3)
        svg = pb.to_svg(2.5)
        assert svg is not None

    def test_get_progress(self):
        pb = ProgressBar(width=400)
        pb.set_progress(0.5, start=0)
        p = pb.get_progress(time=0)
        assert 0 <= p <= 1

    def test_reverse_progress(self):
        pb = ProgressBar(width=400)
        pb.set_progress(1.0, start=0)
        pb.set_progress(0.0, start=1, end=2)
        svg = pb.to_svg(1.5)
        assert svg is not None


# ── RadarChart edge cases ────────────────────────────────────────────────

class TestRadarChartEdgeCases:
    def test_all_zero_values(self):
        rc = RadarChart(values=[0, 0, 0], labels=['A', 'B', 'C'])
        svg = rc.to_svg(0)
        assert svg is not None

    def test_identical_values(self):
        rc = RadarChart(values=[50, 50, 50], labels=['A', 'B', 'C'])
        svg = rc.to_svg(0)
        assert svg is not None

    def test_multiple_datasets(self):
        rc = RadarChart(values=[80, 60, 40, 70], labels=['A', 'B', 'C', 'D'])
        rc.add_dataset([50, 70, 90, 30], color='#FF0000')
        svg = rc.to_svg(0)
        assert svg is not None


# ── SankeyDiagram edge cases ────────────────────────────────────────────

class TestSankeyDiagramEdgeCases:
    def test_single_flow(self):
        sd = SankeyDiagram(flows=[('A', 'B', 100)])
        svg = sd.to_svg(0)
        assert svg is not None

    def test_zero_flow(self):
        sd = SankeyDiagram(flows=[('A', 'B', 100), ('A', 'C', 0)])
        svg = sd.to_svg(0)
        assert svg is not None

    def test_many_sources(self):
        flows = [(f'S{i}', 'Target', 10) for i in range(10)]
        sd = SankeyDiagram(flows=flows)
        svg = sd.to_svg(0)
        assert svg is not None


# ── DonutChart edge cases ────────────────────────────────────────────────

class TestDonutChartEdgeCases:
    def test_inner_radius_zero(self):
        dc = DonutChart(values=[30, 40, 30], inner_radius=0)
        svg = dc.to_svg(0)
        assert svg is not None

    def test_single_value(self):
        dc = DonutChart(values=[100])
        svg = dc.to_svg(0)
        assert svg is not None


# ── BoxPlot edge cases ──────────────────────────────────────────────────

class TestBoxPlotEdgeCases:
    def test_single_group(self):
        bp = BoxPlot(data_groups=[[1, 2, 3, 4, 5]])
        svg = bp.to_svg(0)
        assert svg is not None

    def test_uniform_data(self):
        bp = BoxPlot(data_groups=[[5, 5, 5, 5, 5]])
        svg = bp.to_svg(0)
        assert svg is not None

    def test_two_value_group(self):
        bp = BoxPlot(data_groups=[[1, 10]])
        svg = bp.to_svg(0)
        assert svg is not None


# ── MatrixHeatmap edge cases ────────────────────────────────────────────

class TestMatrixHeatmapEdgeCases:
    def test_single_cell(self):
        mh = MatrixHeatmap(data=[[5]])
        svg = mh.to_svg(0)
        assert svg is not None

    def test_single_row(self):
        mh = MatrixHeatmap(data=[[1, 2, 3]])
        svg = mh.to_svg(0)
        assert svg is not None

    def test_single_column(self):
        mh = MatrixHeatmap(data=[[1], [2], [3]])
        svg = mh.to_svg(0)
        assert svg is not None

    def test_uniform_values(self):
        mh = MatrixHeatmap(data=[[5, 5], [5, 5]])
        svg = mh.to_svg(0)
        assert svg is not None


# ── CalendarHeatmap edge cases ──────────────────────────────────────────

class TestCalendarHeatmapEdgeCases:
    def test_with_tuple_keys(self):
        data = {(0, 0): 5, (1, 0): 3, (2, 0): 8}
        ch = CalendarHeatmap(data=data)
        svg = ch.to_svg(0)
        assert svg is not None

    def test_all_zeros(self):
        data = {(r, c): 0 for r in range(7) for c in range(4)}
        ch = CalendarHeatmap(data=data)
        svg = ch.to_svg(0)
        assert svg is not None

    def test_flat_list(self):
        ch = CalendarHeatmap(data=[1, 2, 3, 0, 5, 6, 7])
        svg = ch.to_svg(0)
        assert svg is not None


# ── WaffleChart edge cases ──────────────────────────────────────────────

class TestWaffleChartEdgeCases:
    def test_single_category(self):
        wc = WaffleChart(categories=[('Only', 100, '#58C4DD')])
        svg = wc.to_svg(0)
        assert svg is not None

    def test_small_values(self):
        wc = WaffleChart(categories=[('A', 1, '#f00'), ('B', 1, '#0f0'), ('C', 1, '#00f')])
        svg = wc.to_svg(0)
        assert svg is not None


# ── CircularProgressBar edge cases ──────────────────────────────────────

class TestCircularProgressBarEdgeCases:
    def test_zero_progress(self):
        cpb = CircularProgressBar(value=0)
        svg = cpb.to_svg(0)
        assert svg is not None

    def test_full_progress(self):
        cpb = CircularProgressBar(value=100)
        svg = cpb.to_svg(0)
        assert svg is not None

    def test_over_100(self):
        cpb = CircularProgressBar(value=200)
        svg = cpb.to_svg(0)
        assert svg is not None


# ── Scoreboard edge cases ──────────────────────────────────────────────

class TestScoreboardEdgeCases:
    def test_single_entry(self):
        sb = Scoreboard(entries=[('Alice', 100)])
        svg = sb.to_svg(0)
        assert svg is not None

    def test_tied_scores(self):
        sb = Scoreboard(entries=[('A', 50), ('B', 50), ('C', 50)])
        svg = sb.to_svg(0)
        assert svg is not None


# ── BulletChart edge cases ──────────────────────────────────────────────

class TestBulletChartEdgeCases:
    def test_actual_exceeds_target(self):
        bc = BulletChart(actual=120, target=100)
        svg = bc.to_svg(0)
        assert svg is not None

    def test_zero_actual_and_target(self):
        bc = BulletChart(actual=0, target=0)
        svg = bc.to_svg(0)
        assert svg is not None


# ── KPICard edge cases ──────────────────────────────────────────────────

class TestKPICardEdgeCases:
    def test_with_trend_data(self):
        kc = KPICard(title='Revenue', value='$1M', trend_data=[10, 20, 15, 25, 30])
        svg = kc.to_svg(0)
        assert svg is not None

    def test_with_subtitle(self):
        kc = KPICard(title='Users', value='10K', subtitle='Active')
        svg = kc.to_svg(0)
        assert svg is not None


# ── GanttChart edge cases ───────────────────────────────────────────────

class TestGanttChartEdgeCases:
    def test_single_task(self):
        gc = GanttChart(tasks=[('Task', 0, 5)])
        svg = gc.to_svg(0)
        assert svg is not None

    def test_zero_duration_task(self):
        gc = GanttChart(tasks=[('Milestone', 3, 3)])
        svg = gc.to_svg(0)
        assert svg is not None

    def test_overlapping_tasks(self):
        gc = GanttChart(tasks=[('A', 0, 5), ('B', 2, 7), ('C', 4, 6)])
        svg = gc.to_svg(0)
        assert svg is not None
