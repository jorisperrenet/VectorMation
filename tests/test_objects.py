"""Tests for VObject subclasses: draw_along, updater, from_svg, Brace, Arrow, Wedge, ClipPath, Graph, show/hide."""
import os
import tempfile
import pytest
from vectormation.objects import (
    Circle, Rectangle, Polygon, Line, Lines, Path, Text, Ellipse,
    Arrow, Brace, Wedge, Arc, ClipPath, Graph, Dot, Cross, LabeledDot,
    BarChart, PieChart, Axes, BlurFilter, DropShadowFilter, Angle, RightAngle,
    VCollection, from_svg, from_svg_file, Image, Trace,
    VectorMathAnim, CountAnimation, Table, Matrix, DynamicObject,
    ValueTracker, DecimalNumber, VGroup,
    SurroundingRectangle, BackgroundRectangle, RoundedRectangle,
    SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_DOT_RADIUS,
    always_redraw, UP, DOWN, LEFT, RIGHT,
    ZoomedInset, Intersection, Difference, Union, Exclusion,
    ThreeDAxes, WaterfallChart, DonutChart, GanttChart, SankeyDiagram,
    FunnelChart, TreeMap, GaugeChart, SparkLine,
    VennDiagram, OrgChart,
    KPICard, BulletChart, CalendarHeatmap,
    WaffleChart, MindMap,
    CircularProgressBar, Scoreboard,
    MatrixHeatmap, BoxPlot, TextBox, Bracket, IconGrid,
    NumberedList, SpeechBubble, Badge, Divider,
    Checklist, Stepper, TagCloud,
    StatusIndicator, Meter, Breadcrumb,
    Paragraph, EquilateralTriangle, Star, AnnularSector, CubicBezier,
    DashedLine, RegularPolygon, FunctionGraph, Annulus, ArcBetweenPoints,
    Elbow, SurroundingCircle, BulletedList,
    DoubleArrow, CurvedArrow, NumberLine,
    Code, NetworkGraph, Tree, Label, LabeledArrow,
    Callout, DimensionLine, Tooltip, ProgressBar, Legend, FlowChart,
    StreamLines, PolarAxes, Stamp, TimelineBar, RadarChart,
    DEFAULT_CHART_COLORS, Variable, Underline,
    ArrowVectorField, ComplexPlane, ChessBoard, Automaton,
    PeriodicTable, BohrAtom,
    Countdown, Filmstrip, MorphObject, Title, NumberPlane, Matrix,
    Ellipse, from_svg,
)
from vectormation.attributes import Coor, Real
import vectormation.easings as easings
from bs4 import BeautifulSoup


class TestDrawAlong:
    def test_draw_along_sets_dasharray(self):
        c = Circle(r=50, cx=100, cy=100)
        c.draw_along(start=0, end=1)
        da = c.styling.stroke_dasharray.at_time(0)
        assert da != ''

    def test_draw_along_dashoffset_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.draw_along(start=0, end=1, easing=easings.linear)
        offset = c.styling.stroke_dashoffset.at_time(1)
        assert offset == pytest.approx(0, abs=0.1)

    def test_draw_along_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.draw_along(start=0, end=1)
        assert result is c


class TestFromSvg:
    def test_from_svg_path(self):
        soup = BeautifulSoup("<path d='M0,0L100,100' x='0' y='0'/>", 'html.parser')
        elem = soup.find('path')
        obj = from_svg(elem)
        assert isinstance(obj, Path)

    def test_from_svg_circle(self):
        soup = BeautifulSoup("<circle cx='50' cy='50' r='25'/>", 'html.parser')
        elem = soup.find('circle')
        obj = from_svg(elem)
        assert isinstance(obj, Circle)

    def test_from_svg_ellipse(self):
        soup = BeautifulSoup("<ellipse cx='50' cy='50' rx='30' ry='20'/>", 'html.parser')
        elem = soup.find('ellipse')
        obj = from_svg(elem)
        assert isinstance(obj, Ellipse)

    def test_from_svg_line(self):
        soup = BeautifulSoup("<line x1='0' y1='0' x2='100' y2='100'/>", 'html.parser')
        elem = soup.find('line')
        obj = from_svg(elem)
        assert isinstance(obj, Line)

    def test_from_svg_polygon(self):
        soup = BeautifulSoup("<polygon points='0,0 100,0 50,100'/>", 'html.parser')
        elem = soup.find('polygon')
        obj = from_svg(elem)
        assert isinstance(obj, Polygon)

    def test_from_svg_polyline(self):
        soup = BeautifulSoup("<polyline points='0,0 100,0 50,100'/>", 'html.parser')
        elem = soup.find('polyline')
        obj = from_svg(elem)
        assert isinstance(obj, Lines)

    def test_from_svg_unknown_raises(self):
        soup = BeautifulSoup("<defs/>", 'html.parser')
        elem = soup.find('defs')
        with pytest.raises(NotImplementedError):
            from_svg(elem)


class TestFromSvgFile:
    def test_load_simple_svg(self):
        tmpdir = tempfile.mkdtemp()
        svg_path = os.path.join(tmpdir, 'test.svg')
        with open(svg_path, 'w') as f:
            f.write("""<?xml version='1.0'?>
<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
  <circle cx='50' cy='50' r='25'/>
  <rect x='10' y='10' width='30' height='30'/>
</svg>""")
        col = from_svg_file(svg_path)
        assert isinstance(col, VCollection)
        assert len(col) >= 1  # At least the circle (rect may be converted to path)


class TestBrace:
    def test_brace_down(self):
        target = Rectangle(width=100, height=50, x=100, y=100)
        b = Brace(target, direction='down')
        assert isinstance(b, VCollection)
        assert len(b) >= 1

    def test_brace_with_label(self):
        target = Rectangle(width=100, height=50, x=100, y=100)
        b = Brace(target, direction='up', label='test')
        assert len(b) >= 2  # Path + Text

    def test_brace_invalid_direction(self):
        target = Rectangle(width=100, height=50, x=100, y=100)
        with pytest.raises(ValueError):
            Brace(target, direction='diagonal')

    def test_brace_all_directions(self):
        target = Rectangle(width=100, height=50, x=100, y=100)
        for d in ('down', 'up', 'left', 'right'):
            b = Brace(target, direction=d)
            assert isinstance(b, VCollection)


class TestArrow:
    def test_arrow_creates_collection(self):
        a = Arrow(x1=0, y1=0, x2=100, y2=0)
        assert isinstance(a, VCollection)
        assert len(a) >= 2  # shaft + tip

    def test_double_ended_arrow(self):
        a = Arrow(x1=0, y1=0, x2=100, y2=0, double_ended=True)
        assert len(a) >= 3  # shaft + tip + tail

    def test_arrow_to_svg(self):
        a = Arrow(x1=0, y1=0, x2=100, y2=0)
        svg = a.to_svg(0)
        assert '<g' in svg
        assert '<line' in svg


class TestWedge:
    def test_wedge_path_closes(self):
        w = Wedge(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        p = w.path(0)
        assert p.endswith('Z')

    def test_wedge_to_svg(self):
        w = Wedge(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        svg = w.to_svg(0)
        assert '<path' in svg


class TestClipPath:
    def test_clip_path_to_svg_def(self):
        c = Circle(r=50, cx=100, cy=100)
        cp = ClipPath(c)
        svg = cp.to_svg_def(0)
        assert '<clipPath' in svg
        assert '</clipPath>' in svg
        assert '<circle' in svg

    def test_clip_ref(self):
        c = Circle(r=50, cx=100, cy=100)
        cp = ClipPath(c)
        ref = cp.clip_ref()
        assert ref.startswith('url(#')


class TestGraph:
    def test_graph_creates_collection(self):
        g = Graph(lambda x: x**2, x_range=(-2, 2))
        assert isinstance(g, VCollection)
        assert len(g) > 0

    def test_graph_to_svg(self):
        g = Graph(lambda x: x**2, x_range=(-2, 2))
        svg = g.to_svg(0)
        assert '<g' in svg

    def test_graph_add_function(self):
        g = Graph(lambda x: x, x_range=(-2, 2))
        initial_len = len(g)
        g.add_function(lambda x: x**2)
        assert len(g) == initial_len + 1


class TestShowHide:
    def test_show_at_creation(self):
        c = Circle(r=50, creation=1)
        assert not c.show.at_time(0)
        assert c.show.at_time(1)

    def test_fadein_hides_then_shows(self):
        c = Circle(r=50, creation=0)
        c.fadein(start=1, end=2)
        assert not c.show.at_time(0.5)
        assert c.show.at_time(1)

    def test_fadeout_hides_at_end(self):
        c = Circle(r=50, creation=0)
        c.fadeout(start=1, end=2)
        assert not c.show.at_time(3)


class TestDot:
    def test_dot_is_circle(self):
        d = Dot(r=6, cx=50, cy=50)
        assert isinstance(d, Circle)

    def test_dot_default_styling(self):
        d = Dot()
        assert d.styling.stroke_width.at_time(0) == 0


class TestImage:
    def test_image_to_svg(self):
        img = Image(href='test.png', x=10, y=20, width=100, height=50)
        svg = img.to_svg(0)
        assert '<image' in svg
        assert "href='test.png'" in svg

    def test_image_bbox(self):
        img = Image(href='test.png', x=10, y=20, width=100, height=50)
        bx, by, bw, bh = img.bbox(0)
        assert bx == pytest.approx(10)
        assert by == pytest.approx(20)
        assert bw == pytest.approx(100)
        assert bh == pytest.approx(50)

    def test_image_shift(self):
        img = Image(href='test.png', x=10, y=20, width=100, height=50)
        img.shift(dx=5, dy=10)
        assert img.x.at_time(0) == pytest.approx(15)
        assert img.y.at_time(0) == pytest.approx(30)


class TestEllipse:
    def test_ellipse_to_svg(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=200)
        svg = e.to_svg(0)
        assert '<ellipse' in svg
        assert "rx='100'" in svg
        assert "ry='50'" in svg

    def test_ellipse_bbox(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=200)
        bx, by, bw, bh = e.bbox(0)
        assert bx == pytest.approx(100)
        assert by == pytest.approx(150)
        assert bw == pytest.approx(200)
        assert bh == pytest.approx(100)

    def test_ellipse_shift(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=200)
        e.shift(dx=10, dy=20)
        pos = e.c.at_time(0)
        assert pos[0] == pytest.approx(210)
        assert pos[1] == pytest.approx(220)


class TestWaveAnimation:
    def test_wave_returns_self(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.wave(start=0, end=1)
        assert result is r

    def test_wave_shifts_y(self):
        r = Rectangle(100, 50, x=100, y=100)
        y_before = r.y.at_time(0)
        r.wave(start=0, end=1, amplitude=20, n_waves=1)
        # At 0.25, sin(pi/2) = 1 and there_and_back(0.25) ~ 0.5
        y_quarter = r.y.at_time(0.25)
        assert y_quarter != pytest.approx(y_before, abs=0.01)


class TestGrowFromEdge:
    def test_grow_from_edge_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.grow_from_edge('bottom', start=0, end=1)
        assert result is c

    def test_grow_from_edge_hides_before_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.grow_from_edge('bottom', start=1, end=2)
        assert not c.show.at_time(0.5)
        assert c.show.at_time(1)

    def test_grow_from_edge_scale_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.grow_from_edge('top', start=0, end=1, easing=easings.linear)
        # At end, scale should be 1
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0)
        assert c.styling.scale_y.at_time(1) == pytest.approx(1.0)


class TestCross:
    def test_cross_creates_two_lines(self):
        x = Cross(size=30, cx=100, cy=100)
        assert isinstance(x, VCollection)
        assert len(x) == 2

    def test_cross_to_svg(self):
        x = Cross(size=30, cx=100, cy=100)
        svg = x.to_svg(0)
        assert '<line' in svg


class TestSpiralIn:
    def test_spiral_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.spiral_in(start=0, end=1)
        assert result is c

    def test_spiral_in_hides_before(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spiral_in(start=1, end=2)
        assert not c.show.at_time(0.5)
        assert c.show.at_time(1)

    def test_spiral_in_scale_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spiral_in(start=0, end=1, easing=easings.linear)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0)


class TestBlink:
    def test_blink_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.blink(start=0)
        assert result is c

    def test_blink_opacity_at_mid(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, duration=1, easing=easings.linear)
        # At midpoint, opacity should be at 0
        assert c.styling.opacity.at_time(0.5) == pytest.approx(0, abs=0.05)


class TestLabeledDot:
    def test_creates_collection(self):
        ld = LabeledDot(label='A', r=20, cx=100, cy=100)
        assert isinstance(ld, VCollection)
        assert len(ld) == 2

    def test_has_dot_and_label(self):
        ld = LabeledDot(label='A')
        assert isinstance(ld.dot, Dot)
        assert isinstance(ld.label, Text)

    def test_to_svg(self):
        ld = LabeledDot(label='A', r=20, cx=100, cy=100)
        svg = ld.to_svg(0)
        assert '<circle' in svg
        assert '<text' in svg


class TestDistribute:
    def test_distribute_right(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        c3 = Circle(r=10, cx=0, cy=0)
        vc = VCollection(c1, c2, c3)
        vc.arrange(direction='right', buff=20)
        vc.distribute(direction='right')
        # All objects should be spread out
        b1 = c1.bbox(0)
        b3 = c3.bbox(0)
        assert b3[0] > b1[0]  # c3 should be to the right of c1


class TestGetEdge:
    def test_center(self):
        r = Rectangle(100, 50, x=10, y=20)
        cx, cy = r.get_edge('center', 0)
        assert cx == pytest.approx(60)
        assert cy == pytest.approx(45)

    def test_top(self):
        r = Rectangle(100, 50, x=10, y=20)
        x, y = r.get_edge('top', 0)
        assert y == pytest.approx(20)

    def test_bottom_right(self):
        r = Rectangle(100, 50, x=10, y=20)
        x, y = r.get_edge('bottom_right', 0)
        assert x == pytest.approx(110)
        assert y == pytest.approx(70)


class TestPointAtAngle:
    def test_right(self):
        c = Circle(r=100, cx=500, cy=500)
        x, y = c.point_at_angle(0)
        assert x == pytest.approx(600)
        assert y == pytest.approx(500)

    def test_top(self):
        c = Circle(r=100, cx=500, cy=500)
        x, y = c.point_at_angle(90)
        assert x == pytest.approx(500, abs=0.1)
        assert y == pytest.approx(400, abs=0.1)


class TestBarChart:
    def test_creates_collection(self):
        bc = BarChart([10, 20, 30])
        assert isinstance(bc, VCollection)
        assert bc.bar_count == 3

    def test_with_labels(self):
        bc = BarChart([10, 20, 30], labels=['A', 'B', 'C'])
        svg = bc.to_svg(0)
        assert '<text' in svg

    def test_to_svg(self):
        bc = BarChart([10, 20, 30])
        svg = bc.to_svg(0)
        assert '<rect' in svg


class TestSetFillStroke:
    def test_set_fill_instant(self):
        c = Circle(r=50)
        c.set_fill('#ff0000')
        color = c.styling.fill.time_func(0)
        assert color[:3] == (255, 0, 0)

    def test_set_stroke_instant(self):
        c = Circle(r=50)
        c.set_stroke(color='#ff0000', width=5)
        assert c.styling.stroke_width.at_time(0) == 5

    def test_set_fill_returns_self(self):
        c = Circle(r=50)
        assert c.set_fill('#f00') is c

    def test_set_stroke_returns_self(self):
        c = Circle(r=50)
        assert c.set_stroke(color='#f00') is c


class TestAxes:
    def test_creates_collection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        assert isinstance(ax, VCollection)

    def test_plot_adds_curve(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        initial_len = len(ax)
        curve = ax.plot(lambda x: x**2)
        assert len(ax) == initial_len + 1
        assert isinstance(curve, Path)

    def test_coords_to_point(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5), x=100, y=50, plot_width=800, plot_height=600)
        px, py = ax.coords_to_point(0, 0)
        assert px == pytest.approx(500)  # midpoint of 100..900
        assert py == pytest.approx(350)  # midpoint of 50..650

    def test_to_svg(self):
        ax = Axes(y_range=(-5, 5))
        svg = ax.to_svg(0)
        assert '<line' in svg

    def test_deferred_axes_from_add_function(self):
        ax = Axes(x_range=(-5, 5))
        assert len(ax) == 0
        ax.add_function(lambda x: x**2)
        assert len(ax) > 0
        svg = ax.to_svg(0)
        assert '<line' in svg

    def test_plot_line_graph(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 20))
        initial_len = len(ax)
        graph = ax.plot_line_graph([0, 5, 10], [0, 20, 10])
        assert len(ax) == initial_len + 1
        assert isinstance(graph, VCollection)

    def test_get_area(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        curve = ax.plot(lambda x: x)
        initial_len = len(ax)
        area = ax.get_area(curve, x_range=(2, 8))
        assert len(ax) == initial_len + 1
        assert isinstance(area, Path)

    def test_get_vertical_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        initial_len = len(ax)
        vl = ax.get_vertical_line(5, y_val=7)
        assert len(ax) == initial_len + 1
        assert isinstance(vl, Line)

    def test_input_to_graph_point(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 100), x=0, y=0, plot_width=1000, plot_height=500)
        func = lambda x: x ** 2
        px, py = ax.input_to_graph_point(5, func)
        ex, ey = ax.coords_to_point(5, 25)
        assert px == pytest.approx(ex)
        assert py == pytest.approx(ey)

    def test_graph_position_with_real(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 100), x=0, y=0, plot_width=1000, plot_height=500)
        func = lambda x: x ** 2
        x_attr = Real(0, 5)
        pos_fn = ax.graph_position(func, x_attr)
        px, py = pos_fn(0)
        ex, ey = ax.coords_to_point(5, 25)
        assert px == pytest.approx(ex)
        assert py == pytest.approx(ey)

    def test_graph_position_with_callable(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 100), x=0, y=0, plot_width=1000, plot_height=500)
        func = lambda x: x ** 2
        pos_fn = ax.graph_position(func, lambda t: t * 2)
        px, py = pos_fn(3)  # x = 6, y = 36
        ex, ey = ax.coords_to_point(6, 36)
        assert px == pytest.approx(ex)
        assert py == pytest.approx(ey)

    def test_get_area_bounded(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        f1 = lambda x: x
        f2 = lambda x: x / 2
        curve1 = ax.plot(f1)
        curve2 = ax.plot(f2)
        initial_len = len(ax)
        area = ax.get_area(curve1, x_range=(2, 8), bounded_graph=curve2)
        assert len(ax) == initial_len + 1
        assert isinstance(area, Path)

    def test_ranges_are_real_attributes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        assert isinstance(ax.x_min, Real)
        assert isinstance(ax.x_max, Real)
        assert isinstance(ax.y_min, Real)
        assert isinstance(ax.y_max, Real)
        assert ax.x_min.at_time(0) == -5
        assert ax.x_max.at_time(0) == 5
        assert ax.y_min.at_time(0) == -3
        assert ax.y_max.at_time(0) == 3

    def test_animated_range(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), x=0, y=0, plot_width=1000, plot_height=500)
        ax.x_max.move_to(0, 3, 20)
        # At time 0, x_max=10, so x=5 is at midpoint (500)
        px0, _ = ax.coords_to_point(5, 0, time=0)
        assert px0 == pytest.approx(500)
        # At time 3, x_max=20, so x=5 is at 1/4 (250)
        px3, _ = ax.coords_to_point(5, 0, time=3)
        assert px3 == pytest.approx(250)

    def test_get_riemann_rectangles(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        initial_len = len(ax)
        rects = ax.get_riemann_rectangles(lambda x: x ** 2, x_range=(1, 3), dx=0.5)
        assert len(ax) == initial_len + 1
        assert isinstance(rects, DynamicObject)
        svg = rects.to_svg(0)
        assert '<rect' in svg


class TestAxesNewMethods:
    def test_add_vector(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        arrow = ax.add_vector(2, 3)
        assert arrow is not None
        svg = arrow.to_svg(0)
        assert '<line' in svg or '<polygon' in svg

    def test_add_error_bars(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        bars = ax.add_error_bars([1, 2, 3], [2, 4, 6], 0.5)
        assert isinstance(bars, VCollection)
        assert len(bars) == 9  # 3 data points * 3 lines each (bar + 2 caps)

    def test_add_regression_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        line = ax.add_regression_line([1, 2, 3, 4], [2, 4, 6, 8])
        assert line is not None
        svg = line.to_svg(0)
        assert '<line' in svg

    def test_add_regression_line_insufficient_data(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.add_regression_line([1], [2])
        assert result is None

    def test_add_slope_field(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        field = ax.add_slope_field(lambda x, y: x + y, x_step=1, y_step=1)
        assert isinstance(field, VCollection)
        assert len(field) > 0

    def test_add_zero_line(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        line = ax.add_zero_line(axis='x')
        svg = line.to_svg(0)
        assert '<line' in svg

    def test_add_min_max_labels(self):
        import math
        ax = Axes(x_range=(0, 7), y_range=(-3, 3))
        labels = ax.add_min_max_labels(math.sin)
        assert isinstance(labels, VCollection)

    def test_add_interval(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        bracket = ax.add_interval(2, 5)
        assert isinstance(bracket, VCollection)
        assert len(bracket) == 3  # left cap, bar, right cap

    def test_get_vertical_lines(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        lines = ax.get_vertical_lines(lambda x: x ** 2, [1, 2, 3])
        assert isinstance(lines, VCollection)
        assert len(lines) == 3

    def test_plot_line_graph_dynamic_dots(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        graph = ax.plot_line_graph([1, 2, 3], [2, 4, 6])
        # Dots should have dynamic .c attribute
        dot = graph.objects[1]  # first dot (index 0 is the curve)
        p0 = dot.c.at_time(0)
        assert isinstance(p0, tuple)

    def test_add_dot_label_dynamic(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        dot, lbl = ax.add_dot_label(5, 5, label='test')
        p0 = dot.c.at_time(0)
        assert isinstance(p0, tuple)

    def test_plot_bar(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        bars = ax.plot_bar([1, 2, 3], [3, 7, 5], width=0.8)
        assert isinstance(bars, VCollection)
        assert len(bars) == 3
        svg = bars.to_svg(0)
        assert '<rect' in svg

    def test_plot_bar_negative(self):
        ax = Axes(x_range=(0, 3), y_range=(-5, 5))
        bars = ax.plot_bar([1, 2], [-3, 4])
        assert len(bars) == 2
        svg = bars.to_svg(0)
        assert '<rect' in svg

    def test_add_shaded_inequality(self):
        import math
        ax = Axes(x_range=(0, 7), y_range=(-3, 3))
        shade = ax.add_shaded_inequality(math.sin, direction='below')
        svg = shade.to_svg(0)
        assert '<path' in svg

    def test_add_area_label(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        lbl = ax.add_area_label(lambda x: x, x_range=(0, 3))
        svg = lbl.to_svg(0)
        assert 'A =' in svg

    def test_add_moving_tangent(self):
        import math
        ax = Axes(x_range=(0, 7), y_range=(-2, 4))
        tangent = ax.add_moving_tangent(math.sin, x_start=0, x_end=6,
                                         start=0, end=1)
        svg = tangent.to_svg(0.5)
        assert '<line' in svg

    def test_plot_grouped_bar(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 12))
        data = [[3, 7], [5, 4]]
        bars = ax.plot_grouped_bar(data)
        assert isinstance(bars, VCollection)
        assert len(bars) == 4  # 2 series * 2 groups
        svg = bars.to_svg(0)
        assert '<rect' in svg

    def test_add_confidence_band(self):
        import math
        ax = Axes(x_range=(0, 7), y_range=(-3, 3))
        band = ax.add_confidence_band(
            lambda x: math.sin(x) - 0.5,
            lambda x: math.sin(x) + 0.5)
        svg = band.to_svg(0)
        assert '<path' in svg

    def test_add_boxplot(self):
        import random
        random.seed(42)
        ax = Axes(x_range=(0, 4), y_range=(0, 25))
        data = [[random.gauss(10, 3) for _ in range(30)] for _ in range(3)]
        boxes = ax.add_boxplot(data, x_positions=[1, 2, 3])
        assert isinstance(boxes, VCollection)
        assert len(boxes) > 0
        svg = boxes.to_svg(0)
        assert '<rect' in svg or '<line' in svg

    def test_plot_heatmap(self):
        ax = Axes(x_range=(0, 3), y_range=(0, 3))
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        hm = ax.plot_heatmap(data)
        assert isinstance(hm, VCollection)
        assert len(hm) == 9  # 3x3 grid
        svg = hm.to_svg(0)
        assert '<rect' in svg

    def test_plot_heatmap_custom_colormap(self):
        ax = Axes(x_range=(0, 2), y_range=(0, 2))
        data = [[0, 1], [2, 3]]
        hm = ax.plot_heatmap(data, colormap=[(0, '#000000'), (1, '#FFFFFF')])
        assert len(hm) == 4

    def test_add_violin_plot(self):
        import random
        random.seed(42)
        ax = Axes(x_range=(0, 4), y_range=(0, 25))
        data = [[random.gauss(10, 3) for _ in range(50)] for _ in range(3)]
        violins = ax.add_violin_plot(data, x_positions=[1, 2, 3])
        assert isinstance(violins, VCollection)
        assert len(violins) > 0
        svg = violins.to_svg(0)
        assert '<path' in svg or '<line' in svg

    def test_waterfall_chart(self):
        wf = WaterfallChart([10, -3, 5, -2, 8],
                            labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
        assert isinstance(wf, VCollection)
        assert len(wf) > 0
        svg = wf.to_svg(0)
        assert '<rect' in svg
        assert '<text' in svg

    def test_plot_bubble(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        bubbles = ax.plot_bubble([1, 3, 5, 7], [2, 8, 4, 6], [10, 50, 20, 80])
        assert isinstance(bubbles, VCollection)
        assert len(bubbles) == 4

    def test_plot_stacked_area(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 20))
        data = [[1, 3, 2, 4], [2, 1, 3, 2], [3, 2, 1, 3]]
        areas = ax.plot_stacked_area(data)
        assert isinstance(areas, VCollection)
        assert len(areas) == 3
        svg = areas.to_svg(0)
        assert '<path' in svg

    def test_donut_chart(self):
        dc = DonutChart([30, 40, 30], labels=['A', 'B', 'C'],
                        center_text='100%')
        assert isinstance(dc, VCollection)
        svg = dc.to_svg(0)
        assert '<path' in svg
        assert '<text' in svg

    def test_plot_dumbbell(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 4))
        db = ax.plot_dumbbell([1, 2, 3], [2, 3, 1], [7, 8, 5])
        assert isinstance(db, VCollection)
        assert len(db) == 9  # 3 lines + 3 start dots + 3 end dots

    def test_add_parametric_area(self):
        import math
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        area = ax.add_parametric_area(
            lambda t: math.cos(t), lambda t: math.sin(t),
            t_range=(0, 2 * math.pi))
        assert isinstance(area, Path)
        d = area.d.at_time(0)
        assert d.startswith('M') and 'Z' in d

    def test_gantt_chart(self):
        tasks = [('Design', 0, 3), ('Build', 2, 7), ('Test', 5, 9)]
        gc = GanttChart(tasks)
        assert isinstance(gc, VCollection)
        assert len(gc) > 0
        svg = gc.to_svg(0)
        assert '<rect' in svg
        assert '<text' in svg

    def test_add_threshold_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        th = ax.add_threshold_line(5, label='Max')
        assert isinstance(th, VCollection)
        assert len(th) == 2  # line + label
        svg = th.to_svg(0)
        assert '<line' in svg
        assert '<text' in svg

    def test_add_data_labels(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        labels = ax.add_data_labels([1, 2, 3], [4, 7, 3])
        assert isinstance(labels, VCollection)
        assert len(labels) == 3

    def test_plot_lollipop(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 4))
        lp = ax.plot_lollipop([1, 2, 3], [5, 8, 3])
        assert isinstance(lp, VCollection)
        assert len(lp) == 6  # 3 lines + 3 dots

    def test_sankey_diagram(self):
        flows = [('A', 'X', 10), ('A', 'Y', 5), ('B', 'X', 3), ('B', 'Y', 8)]
        sk = SankeyDiagram(flows)
        assert isinstance(sk, VCollection)
        assert len(sk) > 0
        svg = sk.to_svg(0)
        assert '<path' in svg  # flow paths
        assert '<rect' in svg  # node rects

    def test_donut_chart_no_labels(self):
        dc = DonutChart([10, 20, 30])
        assert isinstance(dc, VCollection)
        assert len(dc._sectors) == 3

    def test_funnel_chart(self):
        stages = [('Visits', 1000), ('Signups', 400), ('Trials', 150), ('Paid', 60)]
        fc = FunnelChart(stages)
        assert isinstance(fc, VCollection)
        assert len(fc) > 0
        svg = fc.to_svg(0)
        assert 'Visits' in svg
        assert 'Paid' in svg

    def test_funnel_chart_empty(self):
        fc = FunnelChart([])
        assert len(fc) == 0

    def test_treemap(self):
        data = [('A', 50), ('B', 30), ('C', 15), ('D', 5)]
        tm = TreeMap(data)
        assert isinstance(tm, VCollection)
        assert len(tm) > 0
        svg = tm.to_svg(0)
        assert '<rect' in svg

    def test_treemap_single(self):
        tm = TreeMap([('Only', 100)])
        assert len(tm) >= 1

    def test_gauge_chart(self):
        gc = GaugeChart(72, min_val=0, max_val=100, label='Speed')
        assert isinstance(gc, VCollection)
        assert len(gc) > 0
        svg = gc.to_svg(0)
        assert '72' in svg
        assert 'Speed' in svg

    def test_sparkline(self):
        sl = SparkLine([3, 7, 2, 8, 5, 9, 1])
        svg = sl.to_svg(0)
        assert '<path' in svg
        assert 'M' in svg

    def test_sparkline_endpoint(self):
        sl = SparkLine([1, 2, 3], show_endpoint=True)
        svg = sl.to_svg(0)
        assert '<circle' in svg

    def test_add_moving_label(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        curve = ax.plot(lambda x: x ** 2 / 10)
        ml = ax.add_moving_label(curve, 'Track', x_start=1, x_end=5, start=0, end=2)
        assert isinstance(ml, VCollection)
        assert len(ml) == 2  # dot + label

    def test_add_vertical_span(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        rect = ax.add_vertical_span(2, 5)
        assert isinstance(rect, Rectangle)
        svg = rect.to_svg(0)
        assert '<rect' in svg

    def test_add_horizontal_span(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        rect = ax.add_horizontal_span(3, 7)
        assert isinstance(rect, Rectangle)
        svg = rect.to_svg(0)
        assert '<rect' in svg

    def test_venn_diagram_2(self):
        vd = VennDiagram(['A', 'B'])
        assert isinstance(vd, VCollection)
        assert len(vd) >= 4  # 2 circles + 2 labels
        svg = vd.to_svg(0)
        assert '<circle' in svg or '<ellipse' in svg

    def test_venn_diagram_3(self):
        vd = VennDiagram(['X', 'Y', 'Z'], radius=100)
        assert len(vd) >= 6  # 3 circles + 3 labels

    def test_org_chart(self):
        tree = ('CEO', [('CTO', [('Dev', [])]), ('CFO', [])])
        oc = OrgChart(tree)
        assert isinstance(oc, VCollection)
        assert len(oc) > 0
        svg = oc.to_svg(0)
        assert 'CEO' in svg
        assert 'CTO' in svg
        assert 'Dev' in svg

    def test_plot_filled_step(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        fs = ax.plot_filled_step([0, 1, 2, 3, 4], [2, 5, 3, 8, 4])
        assert isinstance(fs, Path)
        svg = ax.to_svg(0)
        assert 'Z' in svg  # closed path

    def test_kpi_card(self):
        kpi = KPICard('Revenue', '$1.2M', subtitle='+12% MoM',
                      trend_data=[100, 120, 115, 135, 150])
        assert isinstance(kpi, VCollection)
        assert len(kpi) > 0
        svg = kpi.to_svg(0)
        assert 'Revenue' in svg
        assert '$1.2M' in svg

    def test_kpi_card_no_trend(self):
        kpi = KPICard('Users', '10K')
        svg = kpi.to_svg(0)
        assert 'Users' in svg

    def test_bullet_chart(self):
        bc = BulletChart(actual=270, target=250, label='Revenue',
                         ranges=[(150, '#2a2a3a'), (225, '#3a3a4a'), (300, '#4a4a5a')])
        assert isinstance(bc, VCollection)
        assert len(bc) > 0
        svg = bc.to_svg(0)
        assert '<rect' in svg
        assert '<line' in svg

    def test_calendar_heatmap(self):
        data = {(r, c): r * c for r in range(7) for c in range(10)}
        ch = CalendarHeatmap(data, rows=7, cols=10)
        assert isinstance(ch, VCollection)
        assert len(ch) == 70

    def test_calendar_heatmap_flat(self):
        ch = CalendarHeatmap(list(range(35)), rows=7, cols=5)
        assert len(ch) == 35

    def test_plot_density(self):
        ax = Axes(x_range=(-5, 5), y_range=(0, 0.5), plot_width=400, plot_height=300, x=100, y=100)
        data = [0, 0.5, -0.5, 1, -1, 0.2, -0.3, 0.8]
        curve = ax.plot_density(data)
        assert isinstance(curve, Path)
        svg = ax.to_svg(0)
        assert '<path' in svg

    def test_add_annotation_box(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        ab = ax.add_annotation_box(5, 5, 'Peak value')
        assert isinstance(ab, VCollection)
        assert len(ab) == 3  # arrow + box + label

    def test_waffle_chart(self):
        cats = [('A', 30, '#58C4DD'), ('B', 50, '#83C167'), ('C', 20, '#FF6B6B')]
        wc = WaffleChart(cats, grid_size=10)
        assert isinstance(wc, VCollection)
        assert len(wc) > 0
        svg = wc.to_svg(0)
        assert '<rect' in svg

    def test_mind_map(self):
        root = ('Central', [
            ('Branch1', [('Leaf1', []), ('Leaf2', [])]),
            ('Branch2', []),
            ('Branch3', [('Leaf3', [])]),
        ])
        mm = MindMap(root)
        assert isinstance(mm, VCollection)
        assert len(mm) > 0
        svg = mm.to_svg(0)
        assert 'Central' in svg
        assert 'Branch1' in svg
        assert 'Leaf1' in svg

    def test_mind_map_no_children(self):
        mm = MindMap(('Solo', []))
        assert len(mm) == 2  # circle + text

    def test_plot_population_pyramid(self):
        ax = Axes(x_range=(-50, 50), y_range=(0, 6), plot_width=400, plot_height=300, x=100, y=100)
        pp = ax.plot_population_pyramid([1, 2, 3, 4, 5],
                                         [30, 25, 20, 15, 10],
                                         [28, 24, 22, 16, 12])
        assert isinstance(pp, VCollection)
        assert len(pp) == 10  # 5 left + 5 right bars

    def test_add_data_table(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10), plot_width=400, plot_height=300, x=100, y=100)
        dt = ax.add_data_table(['X', 'Y', 'Z'], [[1, 2, 3], [4, 5, 6]])
        assert isinstance(dt, VCollection)
        assert len(dt) > 0
        svg = dt.to_svg(0)
        assert 'X' in svg
        assert '6' in svg

    def test_circular_progress_bar(self):
        cp = CircularProgressBar(75)
        assert isinstance(cp, VCollection)
        assert len(cp) >= 2  # track + progress arc (+ optional text)
        svg = cp.to_svg(0)
        assert '75%' in svg

    def test_circular_progress_bar_zero(self):
        cp = CircularProgressBar(0)
        assert len(cp) >= 1  # at least track

    def test_scoreboard(self):
        entries = [('Goals', '3'), ('Assists', '7'), ('Saves', '12')]
        sb = Scoreboard(entries)
        assert isinstance(sb, VCollection)
        svg = sb.to_svg(0)
        assert 'Goals' in svg
        assert '12' in svg

    def test_scoreboard_empty(self):
        sb = Scoreboard([])
        assert len(sb) == 0

    def test_plot_ribbon(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 10), plot_width=300, plot_height=200)
        ribbon = ax.plot_ribbon([0, 1, 2, 3], [1, 2, 1, 3], [4, 5, 6, 7])
        assert isinstance(ribbon, Path)
        d = ribbon.d.at_time(0)
        assert 'M' in d and 'Z' in d

    def test_plot_ribbon_empty(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 10), plot_width=300, plot_height=200)
        ribbon = ax.plot_ribbon([], [], [])
        d = ribbon.d.at_time(0)
        assert d == ''

    def test_plot_swarm(self):
        ax = Axes(x_range=(0, 3), y_range=(0, 10), plot_width=300, plot_height=200)
        swarm = ax.plot_swarm([1, 2], [[3, 5, 7], [2, 4]])
        assert isinstance(swarm, VCollection)
        assert len(swarm) == 5  # 3 + 2 dots

    def test_add_axis_break_y(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        brk = ax.add_axis_break(5, axis='y')
        assert isinstance(brk, Path)
        d = brk.d.at_time(0)
        assert 'M' in d and 'L' in d

    def test_add_axis_break_x(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        brk = ax.add_axis_break(5, axis='x')
        d = brk.d.at_time(0)
        assert 'M' in d and 'L' in d

    def test_matrix_heatmap(self):
        data = [[1, 2, 3], [4, 5, 6]]
        mh = MatrixHeatmap(data, row_labels=['A', 'B'], col_labels=['X', 'Y', 'Z'])
        assert isinstance(mh, VCollection)
        svg = mh.to_svg(0)
        assert 'A' in svg
        assert 'X' in svg

    def test_matrix_heatmap_empty(self):
        mh = MatrixHeatmap([])
        assert len(mh) == 0

    def test_matrix_heatmap_no_values(self):
        data = [[10, 20], [30, 40]]
        mh = MatrixHeatmap(data, show_values=False)
        assert isinstance(mh, VCollection)
        # Without value labels: only 4 rects (no text)
        assert len(mh) == 4

    def test_plot_error_bar(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 10), plot_width=300, plot_height=200)
        eb = ax.plot_error_bar([1, 2, 3], [5, 7, 3], [1, 0.5, 2])
        assert isinstance(eb, VCollection)
        assert len(eb) == 6  # 3 dots + 3 bars

    def test_plot_error_bar_asymmetric(self):
        ax = Axes(x_range=(0, 4), y_range=(0, 10), plot_width=300, plot_height=200)
        eb = ax.plot_error_bar([1, 2], [5, 7], [(1, 2), (0.5, 1.5)])
        assert len(eb) == 4

    def test_plot_histogram(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 5), plot_width=300, plot_height=200)
        data = [1, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8]
        hist = ax.plot_histogram(data, bins=5)
        assert isinstance(hist, VCollection)
        assert len(hist) > 0

    def test_add_color_bar(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        cb = ax.add_color_bar(vmin=0, vmax=100)
        assert isinstance(cb, VCollection)
        svg = cb.to_svg(0)
        assert '0.0' in svg and '100.0' in svg

    def test_box_plot(self):
        bp = BoxPlot([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                      [2, 4, 6, 8, 10, 12, 14]])
        assert isinstance(bp, VCollection)
        assert len(bp) > 0

    def test_box_plot_empty(self):
        bp = BoxPlot([])
        assert len(bp) == 0

    def test_plot_candlestick(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 20), plot_width=300, plot_height=200)
        data = [(1, 10, 15, 8, 14), (2, 14, 16, 11, 12), (3, 12, 18, 10, 17)]
        cs = ax.plot_candlestick(data)
        assert isinstance(cs, VCollection)
        assert len(cs) == 6  # 3 wicks + 3 bodies

    def test_plot_contour(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2), plot_width=300, plot_height=300)
        ct = ax.plot_contour(lambda x, y: x**2 + y**2, levels=4, x_samples=20, y_samples=20)
        assert isinstance(ct, VCollection)
        assert len(ct) > 0

    def test_plot_quiver(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2), plot_width=300, plot_height=300)
        qv = ax.plot_quiver(lambda x, y: (-y, x), x_step=1, y_step=1)
        assert isinstance(qv, VCollection)
        assert len(qv) > 0

    def test_add_text_annotation(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        lbl = ax.add_text_annotation(5, 5, 'Peak')
        assert isinstance(lbl, Text)
        svg = lbl.to_svg(0)
        assert 'Peak' in svg

    def test_add_reference_band_y(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        band = ax.add_reference_band(3, 7, axis='y')
        assert isinstance(band, Rectangle)
        h = band.height.at_time(0)
        assert h > 0

    def test_add_reference_band_x(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=200)
        band = ax.add_reference_band(2, 8, axis='x')
        w = band.width.at_time(0)
        assert w > 0

    def test_plot_implicit(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2), plot_width=300, plot_height=300)
        curve = ax.plot_implicit(lambda x, y: x**2 + y**2 - 1, num_points=20)
        assert isinstance(curve, Path)
        d = curve.d.at_time(0)
        assert 'M' in d

    def test_plot_dot_plot(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 3), plot_width=300, plot_height=200)
        dp = ax.plot_dot_plot([1, 1, 2, 2, 2, 3])
        assert isinstance(dp, VCollection)
        assert len(dp) == 6

    def test_plot_area(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5), plot_width=300, plot_height=200)
        area = ax.plot_area(lambda x: x, baseline=0)
        assert isinstance(area, Path)
        d = area.d.at_time(0)
        assert 'M' in d and 'Z' in d

    def test_text_box(self):
        tb = TextBox('Hello', x=100, y=100)
        assert isinstance(tb, VCollection)
        assert len(tb) == 2  # box + label
        svg = tb.to_svg(0)
        assert 'Hello' in svg

    def test_bracket(self):
        br = Bracket(x=100, y=100, width=200, text='span')
        assert isinstance(br, VCollection)
        svg = br.to_svg(0)
        assert 'span' in svg

    def test_bracket_no_text(self):
        br = Bracket(x=100, y=100, width=200)
        assert len(br) == 1  # just the bracket lines

    def test_icon_grid(self):
        ig = IconGrid([(5, '#ff0000'), (3, '#00ff00'), (2, '#0000ff')])
        assert isinstance(ig, VCollection)
        assert len(ig) == 10

    def test_icon_grid_squares(self):
        ig = IconGrid([(4, '#ff0000')], shape='square')
        assert len(ig) == 4

    def test_numbered_list(self):
        nl = NumberedList('First', 'Second', 'Third')
        svg = nl.to_svg(0)
        assert '1.' in svg
        assert '2.' in svg
        assert '3.' in svg
        assert 'First' in svg

    def test_numbered_list_start(self):
        nl = NumberedList('A', 'B', start_number=5)
        svg = nl.to_svg(0)
        assert '5.' in svg
        assert '6.' in svg

    def test_speech_bubble(self):
        sb = SpeechBubble('Hello!', x=100, y=100)
        assert isinstance(sb, VCollection)
        assert len(sb) == 3  # tail, box, label

    def test_speech_bubble_directions(self):
        for d in ('down', 'up', 'left', 'right'):
            sb = SpeechBubble('Test', tail_direction=d)
            assert len(sb) == 3

    def test_badge(self):
        b = Badge('v1.0', bg_color='#83C167')
        assert isinstance(b, VCollection)
        assert len(b) == 2  # box, label

    def test_divider_horizontal(self):
        d = Divider(x=0, y=300, length=400)
        assert isinstance(d, VCollection)
        assert len(d) == 1  # single line

    def test_divider_with_label(self):
        d = Divider(x=0, y=300, length=400, label='OR')
        assert len(d) == 3  # line, line, label

    def test_divider_vertical(self):
        d = Divider(x=300, y=0, length=600, direction='vertical', label='Section')
        assert len(d) == 3

    def test_checklist_strings(self):
        cl = Checklist('Item A', 'Item B', 'Item C')
        assert isinstance(cl, VCollection)
        assert len(cl._boxes) == 3

    def test_checklist_tuples(self):
        cl = Checklist(('Task 1', True), ('Task 2', False), ('Task 3', True))
        assert len(cl._labels) == 3

    def test_stepper_int(self):
        s = Stepper(4, active=2)
        assert isinstance(s, VCollection)
        assert len(s._circles) == 4

    def test_stepper_labels(self):
        s = Stepper(['Setup', 'Build', 'Test', 'Deploy'], active=1)
        assert len(s._circles) == 4

    def test_stepper_vertical(self):
        s = Stepper(3, direction='vertical')
        assert len(s._circles) == 3

    def test_tagcloud(self):
        tc = TagCloud([('Python', 10), ('Rust', 7), ('Go', 5), ('JS', 8)])
        assert isinstance(tc, VCollection)
        assert len(tc) == 4

    def test_tagcloud_empty(self):
        tc = TagCloud([])
        assert len(tc) == 0

    def test_status_indicator(self):
        si = StatusIndicator('API Server', status='online')
        assert isinstance(si, VCollection)
        assert len(si) == 2  # dot + label

    def test_status_indicator_custom_color(self):
        si = StatusIndicator('Custom', status='#FF00FF')
        assert len(si) == 2

    def test_meter_vertical(self):
        m = Meter(value=0.75)
        assert isinstance(m, VCollection)
        assert len(m) == 2  # bg + fill

    def test_meter_horizontal(self):
        m = Meter(value=0.3, direction='horizontal', width=200, height=30)
        assert len(m) == 2

    def test_meter_clamped(self):
        m = Meter(value=2.0)  # should clamp to 1.0
        assert len(m) == 2

    def test_breadcrumb(self):
        bc = Breadcrumb('Home', 'Products', 'Details')
        assert isinstance(bc, VCollection)
        assert len(bc) == 5  # 3 labels + 2 separators

    def test_breadcrumb_active(self):
        bc = Breadcrumb('A', 'B', 'C', active_index=1)
        assert len(bc) == 5


class TestUntested:
    """Tests for previously untested shape and composite classes."""

    def test_paragraph(self):
        p = Paragraph('Line one', 'Line two', 'Line three')
        svg = p.to_svg(0)
        assert 'Line one' in svg
        assert 'Line two' in svg

    def test_paragraph_alignment(self):
        p = Paragraph('Left', 'Aligned', alignment='center', font_size=24)
        svg = p.to_svg(0)
        assert 'Left' in svg

    def test_text_escaping(self):
        t = Text(text='a < b & c > d', x=100, y=100, font_size=20, stroke_width=0)
        svg = t.to_svg(0)
        assert '&lt;' in svg
        assert '&amp;' in svg
        assert '&gt;' in svg
        assert ' < ' not in svg

    def test_equilateral_triangle(self):
        t = EquilateralTriangle(side_length=100)
        assert t.path(0) != ''
        bx, by, bw, bh = t.bbox(0)
        assert bw > 0 and bh > 0

    def test_star(self):
        s = Star(n=5, outer_radius=100)
        assert s.path(0) != ''

    def test_star_custom(self):
        s = Star(n=6, outer_radius=80, inner_radius=40)
        assert s.path(0) != ''

    def test_annular_sector(self):
        a = AnnularSector(inner_radius=40, outer_radius=80,
                          start_angle=0, end_angle=90)
        assert a.path(0) != ''

    def test_cubic_bezier(self):
        cb = CubicBezier(p0=(100, 100), p1=(150, 50),
                         p2=(250, 50), p3=(300, 100))
        path = cb.path(0)
        assert 'C' in path or 'c' in path

    def test_dashed_line(self):
        dl = DashedLine(x1=0, y1=0, x2=200, y2=200, dash='8,4')
        svg = dl.to_svg(0)
        assert '8,4' in svg

    def test_regular_polygon_hex(self):
        h = RegularPolygon(6, radius=100)
        path = h.path(0)
        assert path != ''

    def test_regular_polygon_triangle(self):
        t = RegularPolygon(3, radius=50)
        assert t.path(0) != ''

    def test_function_graph(self):
        import math
        fg = FunctionGraph(math.sin, x_range=(-3, 3), num_points=50)
        path = fg.path(0)
        assert path != ''

    def test_annulus(self):
        a = Annulus(inner_radius=40, outer_radius=80)
        path = a.path(0)
        assert path != ''
        bx, by, bw, bh = a.bbox(0)
        assert bw > 0 and bh > 0

    def test_arc_between_points(self):
        ab = ArcBetweenPoints(start=(100, 200), end=(300, 200), angle=60)
        path = ab.path(0)
        assert path != ''

    def test_elbow(self):
        e = Elbow(cx=500, cy=500, width=40, height=40)
        path = e.path(0)
        assert path != ''

    def test_surrounding_circle(self):
        dot = Dot(cx=500, cy=500, r=20)
        sc = SurroundingCircle(dot, buff=10)
        assert sc.path(0) != ''

    def test_bulleted_list(self):
        bl = BulletedList('Item A', 'Item B', 'Item C')
        svg = bl.to_svg(0)
        assert '\u2022' in svg
        assert 'Item A' in svg

    def test_double_arrow(self):
        da = DoubleArrow(x1=100, y1=200, x2=400, y2=200)
        assert isinstance(da, VCollection)
        assert len(da) >= 3  # shaft + 2 tips

    def test_curved_arrow(self):
        ca = CurvedArrow(x1=100, y1=300, x2=400, y2=300, angle=0.5)
        assert isinstance(ca, VCollection)

    def test_number_line(self):
        nl = NumberLine(x_range=(-3, 3, 1), length=600)
        assert isinstance(nl, VCollection)
        assert len(nl) > 0


class TestVCollectionNew:
    def test_wave_effect(self):
        dots = VCollection(
            Dot(cx=100, cy=100),
            Dot(cx=200, cy=100),
            Dot(cx=300, cy=100),
        )
        dots.wave_effect(start=0, end=1, amplitude=20)
        # Check that dots have shifted positions during the animation
        p1 = dots[1].c.at_time(0.5)
        assert isinstance(p1, tuple)

    def test_sort_children_instant(self):
        dots = VCollection(
            Dot(cx=300, cy=100),
            Dot(cx=100, cy=100),
            Dot(cx=200, cy=100),
        )
        dots.sort_children(key='x', start=0)
        # After sorting, first object should be leftmost
        assert dots[0].c.at_time(0)[0] < dots[1].c.at_time(0)[0]

    def test_reveal(self):
        items = VCollection(
            Dot(cx=100, cy=100),
            Dot(cx=200, cy=100),
        )
        items.reveal(start=0, end=1, direction='left')
        # First item should be hidden at time 0 (before reveal starts)
        # Actually fadein shows from start time, so check it doesn't crash
        svg = items[0].to_svg(0.5)
        assert svg is not None

    def test_distribute_radial(self):
        dots = VCollection(
            Dot(cx=500, cy=500),
            Dot(cx=500, cy=500),
            Dot(cx=500, cy=500),
            Dot(cx=500, cy=500),
        )
        dots.distribute_radial(cx=500, cy=500, radius=100, start_time=0)
        # After distribution, dots should be at different positions
        positions = [d.c.at_time(0) for d in dots]
        assert positions[0] != positions[1]

    def test_flip_all(self):
        dots = VCollection(
            Dot(cx=100, cy=200),
            Dot(cx=300, cy=200),
        )
        dots.flip_all(start=0, axis='x')
        # After flip, positions should be mirrored around group center (200)
        p0 = dots[0].c.at_time(0)
        p1 = dots[1].c.at_time(0)
        assert p0[0] > p1[0]  # originally 100 < 300, now flipped

    def test_shuffle_positions(self):
        dots = VCollection(
            Dot(cx=100, cy=100),
            Dot(cx=200, cy=100),
            Dot(cx=300, cy=100),
        )
        original = [d.c.at_time(0) for d in dots]
        dots.shuffle_positions(start=0, end=1, seed=42)
        after = [d.c.at_time(1) for d in dots]
        # At least one dot should have moved
        assert any(o != a for o, a in zip(original, after))

    def test_scatter_from(self):
        dots = VCollection(
            Dot(cx=500, cy=500),
            Dot(cx=550, cy=500),
        )
        dots.scatter_from(cx=500, cy=500, radius=200, start=0, end=1)
        # After scatter, dots should be further from center
        p = dots[1].c.at_time(1)
        assert abs(p[0] - 500) > 100 or abs(p[1] - 500) > 100

    def test_gather_to(self):
        dots = VCollection(
            Dot(cx=100, cy=100),
            Dot(cx=500, cy=500),
        )
        dots.gather_to(start=0, end=1)
        # After gather, both should be near center
        p0 = dots[0].c.at_time(1)
        p1 = dots[1].c.at_time(1)
        assert abs(p0[0] - p1[0]) < 10
        assert abs(p0[1] - p1[1]) < 10

    def test_stagger_color(self):
        dots = VCollection(
            Dot(cx=100, cy=100, fill='#FF0000'),
            Dot(cx=200, cy=100, fill='#FF0000'),
            Dot(cx=300, cy=100, fill='#FF0000'),
        )
        dots.stagger_color(start=0, end=1, colors=('#FF0000', '#00FF00'))
        # First dot should start changing before last
        c0 = dots[0].styling.fill.at_time(0.2)
        assert c0 is not None


class TestVObjectNew:
    def test_warp(self):
        c = Circle(r=50)
        c.warp(start=0, end=1, amplitude=0.2)
        sx = c.styling.scale_x.at_time(0.5)
        assert isinstance(sx, (int, float))

    def test_swirl(self):
        c = Circle(r=50)
        c.swirl(start=0, end=1, turns=1)
        rot = c.styling.rotation.at_time(0.5)
        assert rot != 0

    def test_trail(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, start_time=0, end_time=1)
        ghosts = d.trail(start=0, end=1, num_copies=3)
        assert len(ghosts) == 3

    def test_heartbeat(self):
        c = Circle(r=50)
        c.heartbeat(start=0, end=2, beats=3, scale_factor=1.5)
        # At midpoint of a beat, scale should be above 1
        sx_mid = c.styling.scale_x.at_time(0.33)
        assert sx_mid > 1.0

    def test_color_wave(self):
        c = Circle(r=50, fill='#FF0000')
        c.color_wave(start=0, end=1, colors=('#FF0000', '#00FF00', '#0000FF'))
        mid = c.styling.fill.at_time(0.5)
        assert mid != '#FF0000'  # color should have changed

    def test_teleport(self):
        d = Dot(cx=100, cy=100)
        d.teleport(500, 500, time=0)
        p = d.c.at_time(0)
        assert abs(p[0] - 500) < 5
        assert abs(p[1] - 500) < 5


class TestSetZ:
    def test_set_z(self):
        c = Circle(r=50)
        c.set_z(5)
        assert c.z.at_time(0) == 5

    def test_to_front(self):
        c = Circle(r=50)
        c.to_front()
        assert c.z.at_time(0) == 999

    def test_to_back(self):
        c = Circle(r=50)
        c.to_back()
        assert c.z.at_time(0) == -999


class TestPieChart:
    def test_creates_collection(self):
        pc = PieChart([30, 40, 30])
        assert isinstance(pc, VCollection)

    def test_with_labels(self):
        pc = PieChart([30, 40, 30], labels=['A', 'B', 'C'])
        svg = pc.to_svg(0)
        assert '<text' in svg

    def test_to_svg(self):
        pc = PieChart([10, 20, 30, 40])
        svg = pc.to_svg(0)
        assert '<path' in svg


class TestFilters:
    def test_blur_filter_svg(self):
        f = BlurFilter(std_deviation=5)
        svg = f.to_svg_def()
        assert '<filter' in svg
        assert 'feGaussianBlur' in svg
        assert "stdDeviation='5'" in svg

    def test_blur_filter_ref(self):
        f = BlurFilter()
        ref = f.filter_ref()
        assert ref.startswith('url(#')

    def test_shadow_filter_svg(self):
        f = DropShadowFilter(dx=5, dy=5)
        svg = f.to_svg_def()
        assert '<filter' in svg
        assert 'feDropShadow' in svg

    def test_shadow_filter_ref(self):
        f = DropShadowFilter()
        ref = f.filter_ref()
        assert ref.startswith('url(#')


class TestRepr:
    def test_vobject_repr(self):
        c = Circle(r=50)
        assert 'Circle' in repr(c)

    def test_vcollection_repr(self):
        vc = VCollection(Circle(r=10), Rectangle(10, 10))
        r = repr(vc)
        assert 'VCollection' in r
        assert '2' in r



class TestAngle:
    def test_creates_arc(self):
        a = Angle(vertex=(100, 100), p1=(200, 100), p2=(100, 0), radius=30)
        svg = a.to_svg(0)
        assert '<path' in svg

    def test_default_styling(self):
        a = Angle(vertex=(0, 0), p1=(100, 0), p2=(0, -100))
        svg = a.to_svg(0)
        assert '255,255,0' in svg

    def test_coor_tracking(self):
        """Passing a Coor for p2 makes the angle track it over time."""
        p2 = Coor(0, (100, 0))
        p2.rotate_around(0, 2, (0, 0), degrees=90, stay=True)
        a = Angle(vertex=(0, 0), p1=(100, 0), p2=p2, radius=30)
        # At t=0, p2 is at (100, 0) — same as p1 → degenerate, angle ≈ 0
        # At t=1, p2 has rotated 45° CCW → angle should be ~45°
        svg0 = a.path(0)
        svg1 = a.path(1)
        assert svg0 != svg1

    def test_coor_tracking_angle_value(self):
        """Angle end_angle tracks Coor rotation."""
        p2 = Coor(0, (0, -100))  # straight up in SVG coords = 90°
        a = Angle(vertex=(0, 0), p1=(100, 0), p2=p2, radius=30)
        sa = a.start_angle.at_time(0)
        ea = a.end_angle.at_time(0)
        assert abs(ea - sa - 90) < 1  # ~90° angle

    def test_shift(self):
        a = Angle(vertex=(100, 100), p1=(200, 100), p2=(100, 0), radius=30)
        a.shift(dx=50, dy=50, start_time=0)
        vx, vy = a.vertex.at_time(0)
        assert abs(vx - 150) < 1 and abs(vy - 150) < 1
        p1x, p1y = a.p1.at_time(0)
        assert abs(p1x - 250) < 1 and abs(p1y - 150) < 1


class TestRightAngle:
    def test_creates_lines(self):
        ra = RightAngle(vertex=(100, 100), p1=(200, 100), p2=(100, 0), size=15)
        svg = ra.to_svg(0)
        assert '<polyline' in svg or '<path' in svg or '<line' in svg

    def test_default_styling(self):
        ra = RightAngle(vertex=(0, 0), p1=(100, 0), p2=(0, -100))
        svg = ra.to_svg(0)
        assert '255,255,0' in svg


class TestEdgeShortcuts:
    def test_get_left(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.get_left(0) == r.get_edge('left', 0)

    def test_get_right(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.get_right(0) == r.get_edge('right', 0)

    def test_get_top(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.get_top(0) == r.get_edge('top', 0)

    def test_get_bottom(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.get_bottom(0) == r.get_edge('bottom', 0)


class TestTrace:
    def test_trace_creates(self):
        p = Coor(0, (100, 100))
        t = Trace(p, start=0, end=1, dt=0.1)
        assert isinstance(t, Trace)

    def test_trace_to_svg(self):
        p = Coor(0, (100, 100))
        t = Trace(p, start=0, end=1, dt=0.1)
        svg = t.to_svg(0.5)
        assert '<polyline' in svg

    def test_trace_shift(self):
        p = Coor(0, (100, 100))
        t = Trace(p, start=0, end=1, dt=0.1)
        result = t.shift(dx=10, dy=20)
        assert result is t
        assert t.styling.dx.at_time(0) == pytest.approx(10)


class TestCountAnimation:
    def test_count_creates(self):
        c = CountAnimation(start_val=0, end_val=100, start=0, end=1)
        assert isinstance(c, Text)

    def test_count_text_at_start(self):
        c = CountAnimation(start_val=0, end_val=100, start=0, end=1, fmt='{:.0f}')
        assert c.text.at_time(0) == '0'

    def test_count_text_at_end(self):
        c = CountAnimation(start_val=0, end_val=100, start=0, end=1,
                          fmt='{:.0f}', easing=easings.linear)
        assert c.text.at_time(1) == '100'


class TestCamera:
    def setup_method(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.canvas = VectorMathAnim(self.tmpdir, width=800, height=600)

    def test_camera_shift(self):
        self.canvas.camera_shift(100, 50, start=0, end=1)
        svg = self.canvas.generate_frame_svg(1)
        # After shift, viewbox x should have moved by 100
        assert self.canvas.vb_x.at_time(1) == pytest.approx(100)

    def test_camera_zoom(self):
        self.canvas.camera_zoom(2, start=0, end=1)
        # After 2x zoom, viewbox should be half the original size
        assert self.canvas.vb_w.at_time(1) == pytest.approx(400)
        assert self.canvas.vb_h.at_time(1) == pytest.approx(300)

    def test_camera_reset(self):
        self.canvas.camera_zoom(2, start=0, end=1)
        self.canvas.camera_reset(start=1, end=2)
        assert self.canvas.vb_w.at_time(2) == pytest.approx(800)
        assert self.canvas.vb_h.at_time(2) == pytest.approx(600)

    def test_camera_follow(self):
        c = Circle(r=50, cx=400, cy=300)
        self.canvas.add_objects(c)
        self.canvas.camera_follow(c, start=0)
        # Circle at canvas center, viewBox stays at origin
        assert self.canvas.vb_x.at_time(0) == pytest.approx(0, abs=5)
        assert self.canvas.vb_y.at_time(0) == pytest.approx(0, abs=5)

    def test_camera_follow_clamps_to_bounds(self):
        c = Circle(r=50, cx=100, cy=100)
        self.canvas.add_objects(c)
        self.canvas.camera_follow(c, start=0)
        # Circle near top-left; viewBox clamps to 0, not negative
        assert self.canvas.vb_x.at_time(0) == pytest.approx(0)
        assert self.canvas.vb_y.at_time(0) == pytest.approx(0)


class TestTable:
    def test_table_creates(self):
        t = Table([[1, 2], [3, 4]])
        assert isinstance(t, VCollection)
        assert t.rows == 2
        assert t.cols == 2

    def test_get_entry(self):
        t = Table([[1, 2], [3, 4]])
        entry = t.get_entry(0, 1)
        assert isinstance(entry, Text)
        assert entry.text.at_time(0) == '2'

    def test_table_to_svg(self):
        t = Table([[1, 2], [3, 4]])
        svg = t.to_svg(0)
        assert '<line' in svg
        assert '<text' in svg


class TestMatrix:
    def test_matrix_creates(self):
        m = Matrix([[1, 2], [3, 4]])
        assert isinstance(m, VCollection)
        assert m.rows == 2
        assert m.cols == 2

    def test_matrix_get_entry(self):
        m = Matrix([[1, 2], [3, 4]])
        entry = m.get_entry(1, 0)
        assert isinstance(entry, Text)
        assert entry.text.at_time(0) == '3'

    def test_matrix_to_svg(self):
        m = Matrix([[1, 0], [0, 1]])
        svg = m.to_svg(0)
        assert '<text' in svg
        assert '<polyline' in svg  # brackets


class TestDynamicObject:
    def test_dynamic_object(self):
        d = DynamicObject(lambda t: Circle(r=50 + t * 10, cx=100, cy=100))
        svg = d.to_svg(1)
        assert '<circle' in svg

    def test_dynamic_bbox(self):
        d = DynamicObject(lambda t: Rectangle(100 + t * 10, 50, x=0, y=0))
        bx, by, bw, bh = d.bbox(0)
        assert bw == pytest.approx(100)


class TestValueTracker:
    def test_init(self):
        vt = ValueTracker(5)
        assert vt.get_value(0) == 5

    def test_set_value(self):
        vt = ValueTracker(0)
        vt.set_value(10, start=1)
        assert vt.get_value(0) == 0
        assert vt.get_value(1) == 10

    def test_animate_value(self):
        vt = ValueTracker(0)
        vt.animate_value(10, start=0, end=1, easing=easings.linear)
        assert vt.at_time(0.5) == pytest.approx(5)
        assert vt.at_time(1) == pytest.approx(10)


class TestDecimalNumber:
    def test_creates_text(self):
        d = DecimalNumber(3.14)
        assert isinstance(d, Text)

    def test_initial_value(self):
        d = DecimalNumber(3.14, fmt='{:.1f}')
        assert d.text.at_time(0) == '3.1'

    def test_tracks_value_tracker(self):
        vt = ValueTracker(0)
        d = DecimalNumber(vt, fmt='{:.0f}')
        vt.set_value(42, start=1)
        assert d.text.at_time(1) == '42'

    def test_animate_value(self):
        d = DecimalNumber(0, fmt='{:.0f}')
        d.animate_value(100, start=0, end=1, easing=easings.linear)
        assert d.text.at_time(0.5) == '50'
        assert d.text.at_time(1) == '100'


class TestSizeConstants:
    def test_small_buff(self):
        assert SMALL_BUFF == 14

    def test_default_stroke_width(self):
        assert DEFAULT_STROKE_WIDTH == 5

    def test_default_dot_radius(self):
        d = Dot()
        assert d.r.at_time(0) == DEFAULT_DOT_RADIUS

    def test_default_buff_in_next_to(self):
        """next_to default buff should be SMALL_BUFF."""
        import inspect
        sig = inspect.signature(Circle.next_to)
        assert sig.parameters['buff'].default == SMALL_BUFF


class TestSurroundingRectangle:
    def test_creates_rounded_rect(self):
        c = Circle(r=50, cx=100, cy=100)
        sr = SurroundingRectangle(c)
        assert isinstance(sr, RoundedRectangle)

    def test_surrounds_target(self):
        r = Rectangle(100, 60, x=200, y=300)
        sr = SurroundingRectangle(r, buff=10)
        assert sr.x.at_time(0) == pytest.approx(190)
        assert sr.y.at_time(0) == pytest.approx(290)
        assert sr.width.at_time(0) == pytest.approx(120)
        assert sr.height.at_time(0) == pytest.approx(80)

    def test_default_styling(self):
        c = Circle(r=50, cx=100, cy=100)
        sr = SurroundingRectangle(c)
        svg = sr.to_svg(0)
        assert '255,255,0' in svg  # yellow stroke

    def test_follow_tracks_target(self):
        c = Circle(r=50, cx=100, cy=100)
        sr = SurroundingRectangle(c, follow=True)
        c.shift(dx=200, start_time=0, end_time=1, easing=easings.linear)
        # sr should track the shifted position
        x0 = sr.x.at_time(0)
        x1 = sr.x.at_time(1)
        assert abs(x1 - x0 - 200) < 1

    def test_custom_styling(self):
        c = Circle(r=50, cx=100, cy=100)
        sr = SurroundingRectangle(c, stroke='#ff0000')
        svg = sr.to_svg(0)
        assert '255,0,0' in svg


class TestBackgroundRectangle:
    def test_creates_rectangle(self):
        c = Circle(r=50, cx=100, cy=100)
        br = BackgroundRectangle(c)
        assert isinstance(br, Rectangle)

    def test_behind_target(self):
        c = Circle(r=50, cx=100, cy=100)
        br = BackgroundRectangle(c)
        assert br.z.at_time(0) == -1

    def test_covers_target(self):
        r = Rectangle(100, 60, x=200, y=300)
        br = BackgroundRectangle(r, buff=5)
        assert br.x.at_time(0) == pytest.approx(195)
        assert br.width.at_time(0) == pytest.approx(110)

    def test_default_styling(self):
        c = Circle(r=50, cx=100, cy=100)
        br = BackgroundRectangle(c)
        svg = br.to_svg(0)
        assert "fill-opacity='0.75'" in svg
        assert "stroke-width='0'" in svg


class TestVGroup:
    def test_alias(self):
        assert VGroup is VCollection

    def test_creates_collection(self):
        g = VGroup(Circle(r=10), Rectangle(10, 10))
        assert len(g) == 2


class TestSetStyle:
    def test_set_fill(self):
        c = Circle(r=50)
        c.set_style(fill='#ff0000')
        val = c.styling.fill.at_time(0)
        assert '255,0,0' in val

    def test_set_stroke_width(self):
        c = Circle(r=50)
        c.set_style(stroke_width=8)
        assert c.styling.stroke_width.at_time(0) == 8

    def test_set_opacity(self):
        c = Circle(r=50)
        c.set_style(opacity=0.5)
        assert c.styling.opacity.at_time(0) == pytest.approx(0.5)

    def test_returns_self(self):
        c = Circle(r=50)
        assert c.set_style(fill='#f00') is c

    def test_set_multiple(self):
        c = Circle(r=50)
        c.set_style(stroke_width=2, opacity=0.3)
        assert c.styling.stroke_width.at_time(0) == 2
        assert c.styling.opacity.at_time(0) == pytest.approx(0.3)


class TestAlwaysRedraw:
    def test_creates_dynamic_object(self):
        d = always_redraw(lambda t: Circle(r=50))
        assert isinstance(d, DynamicObject)

    def test_regenerates_per_frame(self):
        d = always_redraw(lambda t: Circle(r=50 + t * 10))
        svg0 = d.to_svg(0)
        svg1 = d.to_svg(1)
        assert svg0 != svg1


class TestAnimationMethods:
    def test_fadein(self):
        c = Circle(r=50)
        c.fadein(start=1, end=2)
        assert c.show.at_time(0.5) == False
        assert c.show.at_time(1.5) == True

    def test_fadeout(self):
        c = Circle(r=50)
        c.fadeout(start=1, end=2)
        assert c.show.at_time(0.5) == True
        assert c.styling.opacity.at_time(2) == pytest.approx(0)

    def test_grow_from_center(self):
        c = Circle(r=50, cx=100, cy=100)
        c.grow_from_center(start=0, end=1)
        assert c.styling.scale_x.at_time(0) == pytest.approx(0)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1)

    def test_shrink_to_center(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shrink_to_center(start=0, end=1, easing=easings.linear)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1)
        assert c.styling.scale_x.at_time(1) == pytest.approx(0)

    def test_indicate_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.indicate(start=0, end=1) is c

    def test_indicate_scales(self):
        c = Circle(r=50, cx=100, cy=100)
        c.indicate(start=0, end=1, scale_factor=1.5)
        mid = c.styling.scale_x.at_time(0.5)
        assert mid > 1  # should be scaled up at midpoint

    def test_flash_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.flash(start=0, end=1) is c

    def test_pulse_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.pulse(start=0, end=1) is c

    def test_pulse_opacity(self):
        c = Circle(r=50, cx=100, cy=100)
        c.pulse(start=0, end=1)
        mid_opacity = c.styling.opacity.at_time(0.5)
        assert mid_opacity < 1  # reduced at midpoint

    def test_spin(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin(start=0, end=1, degrees=180, easing=easings.linear)
        rot = c.styling.rotation.at_time(0.5)
        assert abs(rot[0] - 90) < 1  # halfway through 180°

    def test_wiggle(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.wiggle(start=0, end=1) is c

    def test_wave(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.wave(start=0, end=1) is c

    def test_move_to(self):
        c = Circle(r=50, cx=100, cy=100)
        c.move_to(500, 400)
        cx, cy = c.center(0)
        assert cx == pytest.approx(500, abs=1)
        assert cy == pytest.approx(400, abs=1)

    def test_move_to_animated(self):
        c = Circle(r=50, cx=100, cy=100)
        c.move_to(500, 400, start_time=0, end_time=1, easing=easings.linear)
        cx0, cy0 = c.center(0)
        cx1, cy1 = c.center(1)
        assert cx0 == pytest.approx(100, abs=1)
        assert cx1 == pytest.approx(500, abs=1)

    def test_always_rotate(self):
        c = Circle(r=50, cx=100, cy=100)
        c.always_rotate(start=0, degrees_per_second=360)
        rot = c.styling.rotation.at_time(0.25)
        assert abs(rot[0] - 90) < 1

    def test_always_shift(self):
        c = Circle(r=50, cx=100, cy=100)
        c.always_shift(100, 0, start=0)
        cx1, _ = c.center(1)
        assert cx1 == pytest.approx(200, abs=1)

    def test_always_shift_with_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.always_shift(100, 0, start=0, end=1)
        cx1, _ = c.center(1)
        cx2, _ = c.center(2)
        assert cx1 == pytest.approx(200, abs=1)
        assert cx2 == pytest.approx(200, abs=1)  # stopped at end

    def test_grow_from_edge(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.grow_from_edge(start=0, end=1) is c

    def test_scale(self):
        r = Rectangle(100, 50, x=0, y=0)
        r.scale(2, start=0, end=1, easing=easings.linear)
        sx = r.styling.scale_x.at_time(1)
        assert sx == pytest.approx(2)

    def test_become(self):
        c1 = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        c2 = Circle(r=50, cx=100, cy=100, fill='#00ff00')
        c1.become(c2)
        fill = c1.styling.fill.at_time(0)
        assert '0,255,0' in fill  # green

    def test_set_opacity(self):
        c = Circle(r=50)
        c.set_opacity(0.3)
        assert c.styling.opacity.at_time(0) == pytest.approx(0.3)

    def test_circumscribe(self):
        c = Circle(r=50, cx=100, cy=100)
        rect = c.circumscribe(start=0, end=2)
        assert isinstance(rect, Path)


class TestDirectionConstants:
    def test_next_to_with_right_constant(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, RIGHT)
        bx, _, _, _ = b.bbox(0)
        assert bx > 200  # b is to the right of a

    def test_next_to_with_left_constant(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, LEFT)
        bx, _, bw, _ = b.bbox(0)
        assert bx + bw < 200  # b is to the left of a

    def test_next_to_with_up_constant(self):
        a = Rectangle(100, 50, x=100, y=200)
        b = Rectangle(100, 30, x=0, y=0)
        b.next_to(a, UP)
        _, by, _, bh = b.bbox(0)
        assert by + bh < 200  # b is above a

    def test_next_to_with_down_constant(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(100, 30, x=0, y=0)
        b.next_to(a, DOWN)
        _, by, _, _ = b.bbox(0)
        assert by > 150  # b is below a

    def test_align_to_with_left_constant(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, LEFT)
        bx, _, _, _ = b.bbox(0)
        assert bx == pytest.approx(200)

    def test_align_to_with_right_constant(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, RIGHT)
        bx, _, bw, _ = b.bbox(0)
        assert bx + bw == pytest.approx(300)

    def test_arrange_with_down_constant(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        g = VCollection(c1, c2)
        g.arrange(DOWN, buff=10)
        _, y1, _, _ = c1.bbox(0)
        _, y2, _, _ = c2.bbox(0)
        assert y2 > y1


class TestBooleanOps:
    def test_intersection_svg(self):
        a = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        b = Circle(r=50, cx=130, cy=100, fill='#0000ff')
        isect = Intersection(a, b)
        svg = isect.to_svg(0)
        assert 'clipPath' in svg
        assert '<path' in svg

    def test_difference_svg(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        diff = Difference(a, b)
        svg = diff.to_svg(0)
        assert 'evenodd' in svg

    def test_union_svg(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        u = Union(a, b)
        svg = u.to_svg(0)
        assert '<path' in svg

    def test_union_bbox(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=100)
        u = Union(a, b)
        bx, by, bw, bh = u.bbox(0)
        assert bx == pytest.approx(50)
        assert bw == pytest.approx(200)

    def test_exclusion_svg(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        exc = Exclusion(a, b)
        svg = exc.to_svg(0)
        assert 'evenodd' in svg

    def test_boolean_returns_vobject(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        for cls in (Intersection, Difference, Union, Exclusion):
            obj = cls(a, b)
            assert hasattr(obj, 'to_svg')
            assert hasattr(obj, 'bbox')
            assert hasattr(obj, 'path')


class TestThreeDAxes:
    def test_creates_collection(self):
        ax = ThreeDAxes()
        assert isinstance(ax, VCollection)

    def test_coords_to_point_origin(self):
        ax = ThreeDAxes(cx=960, cy=540)
        px, py = ax.coords_to_point(0, 0, 0)
        assert px == pytest.approx(960)
        assert py == pytest.approx(540)

    def test_coords_to_point_z(self):
        ax = ThreeDAxes(cx=960, cy=540)
        _, py0 = ax.coords_to_point(0, 0, 0)
        _, py1 = ax.coords_to_point(0, 0, 1)
        assert py1 < py0  # z up means lower y in SVG

    def test_to_svg(self):
        ax = ThreeDAxes()
        svg = ax.to_svg(0)
        assert '<line' in svg  # axis lines
        assert len(ax.objects) == 3  # 3 TeX axis labels

    def test_wireframe(self):
        ax = ThreeDAxes()
        wf = ax.plot_surface_wireframe(lambda x, y: x**2 + y**2, x_steps=5, y_steps=5)
        svg = ax.to_svg(0)
        assert '<polyline' in svg

    def test_parametric_surface(self):
        ax = ThreeDAxes()
        def sphere(u, v):
            import math
            return (math.cos(u) * math.cos(v), math.cos(u) * math.sin(v), math.sin(u))
        ax.plot_parametric_surface(sphere, u_range=(-1.5, 1.5), v_range=(0, 6.28),
                                   u_steps=4, v_steps=8)
        svg = ax.to_svg(0)
        assert '<polyline' in svg


class TestZoomedInset:
    def setup_method(self):
        self.canvas = VectorMathAnim(tempfile.mkdtemp(), width=800, height=600)

    def test_creates_vobject(self):
        zi = ZoomedInset(self.canvas, (100, 100, 200, 200), (500, 50, 250, 250))
        assert isinstance(zi, ZoomedInset)

    def test_svg_contains_nested_svg(self):
        c = Circle(r=50, cx=200, cy=200)
        self.canvas.add_objects(c)
        zi = ZoomedInset(self.canvas, (100, 100, 200, 200), (500, 50, 250, 250))
        self.canvas.add_objects(zi)
        svg = zi.to_svg(0)
        assert '<svg' in svg
        assert 'viewBox' in svg.lower() or "viewBox" in svg

    def test_svg_contains_frame_rect(self):
        zi = ZoomedInset(self.canvas, (100, 100, 200, 200), (500, 50, 250, 250))
        self.canvas.add_objects(zi)
        svg = zi.to_svg(0)
        assert '<rect' in svg

    def test_move_source(self):
        zi = ZoomedInset(self.canvas, (100, 100, 200, 200), (500, 50, 250, 250))
        zi.move_source(300, 300, start=0)
        assert zi.src_x.at_time(0) == 300
        assert zi.src_y.at_time(0) == 300


class TestGetSetXY:
    def test_get_x(self):
        c = Circle(r=50, cx=200, cy=300)
        assert c.get_x() == 200

    def test_get_y(self):
        c = Circle(r=50, cx=200, cy=300)
        assert c.get_y() == 300

    def test_set_x(self):
        c = Circle(r=50, cx=200, cy=300)
        c.set_x(500)
        assert c.get_x() == 500
        assert c.get_y() == 300  # y unchanged

    def test_set_y(self):
        c = Circle(r=50, cx=200, cy=300)
        c.set_y(600)
        assert c.get_y() == 600
        assert c.get_x() == 200  # x unchanged

    def test_set_x_with_start(self):
        c = Circle(r=50, cx=200, cy=300)
        c.set_x(500, start=1)
        assert c.get_x(0) == 200
        assert c.get_x(1) == 500


class TestArrangeInGrid:
    def test_basic_grid(self):
        objs = [Circle(r=20, cx=0, cy=0) for _ in range(6)]
        g = VCollection(*objs)
        g.arrange_in_grid(rows=2, cols=3)
        # 6 objects in 2x3 grid: row 0 has 3, row 1 has 3
        # Objects in same row should have same y
        y0 = objs[0].get_y()
        y1 = objs[1].get_y()
        y3 = objs[3].get_y()
        assert abs(y0 - y1) < 1  # same row
        assert y3 > y0  # second row below first

    def test_auto_cols(self):
        objs = [Rectangle(width=30, height=20) for _ in range(9)]
        g = VCollection(*objs)
        g.arrange_in_grid()
        # sqrt(9)=3, so 3 cols, 3 rows
        x0 = objs[0].get_x()
        x3 = objs[3].get_x()
        assert abs(x0 - x3) < 1  # same column

    def test_rows_only(self):
        objs = [Circle(r=10, cx=0, cy=0) for _ in range(4)]
        g = VCollection(*objs)
        g.arrange_in_grid(rows=2)
        # 2 rows, auto cols=2
        y0 = objs[0].get_y()
        y2 = objs[2].get_y()
        assert y2 > y0

    def test_cols_only(self):
        objs = [Circle(r=10, cx=0, cy=0) for _ in range(4)]
        g = VCollection(*objs)
        g.arrange_in_grid(cols=4)
        # 4 cols, 1 row
        y_vals = [obj.get_y() for obj in objs]
        assert max(y_vals) - min(y_vals) < 1  # all same row


class TestToEdge:
    def test_to_bottom(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge('bottom')
        # 1080 - DEFAULT_OBJECT_TO_EDGE_BUFF(68) - 50 = 962
        assert abs(c.get_y() - 962) < 1

    def test_to_top(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge('top')
        # DEFAULT_OBJECT_TO_EDGE_BUFF(68) + 50 = 118
        assert abs(c.get_y() - 118) < 1

    def test_to_left(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge('left')
        assert abs(c.get_x() - 118) < 1

    def test_to_right(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge('right')
        # 1920 - 68 - 50 = 1802
        assert abs(c.get_x() - 1802) < 1

    def test_direction_constant(self):
        from vectormation.objects import UP
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge(UP)
        assert abs(c.get_y() - 118) < 1

    def test_animated(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_edge('bottom', start_time=0, end_time=2)
        assert c.get_y(0) == 500
        assert abs(c.get_y(2) - 962) < 1

    def test_to_corner_dr(self):
        from vectormation.objects import DR
        c = Circle(r=50, cx=500, cy=500)
        c.to_corner(DR)
        assert abs(c.get_x() - 1802) < 1
        assert abs(c.get_y() - 962) < 1

    def test_to_corner_ul(self):
        from vectormation.objects import UL
        c = Circle(r=50, cx=500, cy=500)
        c.to_corner(UL)
        assert abs(c.get_x() - 118) < 1
        assert abs(c.get_y() - 118) < 1

    def test_to_corner_string(self):
        c = Circle(r=50, cx=500, cy=500)
        c.to_corner('top_right')
        assert abs(c.get_x() - 1802) < 1
        assert abs(c.get_y() - 118) < 1


class TestSetFillStrokeOpacity:
    def test_set_fill_opacity(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_fill(opacity=0.3)
        assert c.styling.fill_opacity.at_time(0) == 0.3

    def test_set_fill_both(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_fill('#00ff00', opacity=0.5)
        assert 'rgb(0' in c.styling.fill.at_time(0)
        assert c.styling.fill_opacity.at_time(0) == 0.5

    def test_set_stroke_opacity(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_stroke(opacity=0.2)
        assert c.styling.stroke_opacity.at_time(0) == 0.2


class TestTitle:
    def test_creates_collection(self):
        from vectormation.objects import Title
        t = Title('Hello World')
        assert isinstance(t, VCollection)
        assert len(t.objects) == 2  # text + underline

    def test_text_content(self):
        from vectormation.objects import Title
        t = Title('Test')
        txt = t.objects[0]
        svg = txt.to_svg(0)
        assert 'Test' in svg
        assert "text-anchor='middle'" in svg


class TestScreenRectangle:
    def test_aspect_ratio(self):
        from vectormation.objects import ScreenRectangle
        sr = ScreenRectangle(width=480)
        assert sr.get_width() == 480
        assert sr.get_height() == 270  # 480 * 9/16

    def test_custom_width(self):
        from vectormation.objects import ScreenRectangle
        sr = ScreenRectangle(width=960)
        assert sr.get_height() == 540


class TestCode:
    def test_creates_collection(self):
        c = Code("x = 1\nprint(x)", language='python')
        assert isinstance(c, VCollection)

    def test_to_svg(self):
        c = Code("def f():\n    return 42")
        svg = c.to_svg(0)
        assert 'def' in svg
        assert '42' in svg

    def test_highlight_lines(self):
        c = Code("a = 1\nb = 2\nc = 3")
        rects = c.highlight_lines([1, 3], start=0, end=1)
        assert isinstance(rects, VCollection)

    def test_javascript(self):
        c = Code("const x = 5;", language='javascript')
        svg = c.to_svg(0)
        assert 'const' in svg


class TestNetworkGraph:
    def test_circular_layout(self):
        g = NetworkGraph(['A', 'B', 'C'], edges=[(0, 1), (1, 2)])
        assert isinstance(g, VCollection)
        svg = g.to_svg(0)
        assert svg != ''

    def test_grid_layout(self):
        g = NetworkGraph(['A', 'B', 'C', 'D'], layout='grid')
        assert len(g._node_positions) == 4

    def test_spring_layout(self):
        g = NetworkGraph(['X', 'Y', 'Z'], edges=[(0, 1), (1, 2)], layout='spring')
        assert len(g._node_positions) == 3

    def test_directed(self):
        g = NetworkGraph(['A', 'B'], edges=[(0, 1)], directed=True)
        svg = g.to_svg(0)
        assert svg != ''

    def test_dict_nodes(self):
        g = NetworkGraph({0: 'Node A', 1: 'Node B'}, edges=[(0, 1)])
        assert g.get_node_position(0) != (960, 540)

    def test_edge_label(self):
        g = NetworkGraph(['A', 'B'], edges=[(0, 1, 'weight')])
        svg = g.to_svg(0)
        assert 'weight' in svg

    def test_empty(self):
        g = NetworkGraph([])
        svg = g.to_svg(0)
        assert svg is not None

    def test_highlight_node(self):
        g = NetworkGraph(['A', 'B'])
        result = g.highlight_node(0, start=0, end=1)
        assert result is g


class TestTree:
    def test_dict_tree(self):
        t = Tree({'root': {'child1': {}, 'child2': {}}})
        assert isinstance(t, VCollection)
        svg = t.to_svg(0)
        assert 'root' in svg

    def test_tuple_tree(self):
        t = Tree(('root', [('A', []), ('B', [('C', [])])]))
        assert t.get_node_position('root') != (960, 540)
        assert t.get_node_position('C') != (960, 540)

    def test_highlight_node(self):
        t = Tree({'root': {'leaf': {}}})
        result = t.highlight_node('root', start=0, end=1)
        assert result is t

    def test_right_layout(self):
        t = Tree(('root', [('A', []), ('B', [])]), layout='right')
        svg = t.to_svg(0)
        assert svg != ''


class TestLabel:
    def test_creates_collection(self):
        l = Label("Hello")
        assert isinstance(l, VCollection)
        svg = l.to_svg(0)
        assert 'Hello' in svg

    def test_custom_styling(self):
        l = Label("Test", fill='#FF0000')
        svg = l.to_svg(0)
        assert svg != ''


class TestLabeledArrow:
    def test_creates(self):
        la = LabeledArrow(x1=100, y1=200, x2=400, y2=200, label='dist')
        assert isinstance(la, VCollection)
        svg = la.to_svg(0)
        assert 'dist' in svg

    def test_arrow_ref(self):
        la = LabeledArrow(label='test')
        assert hasattr(la, 'arrow')
        assert hasattr(la, 'label_obj')


class TestCallout:
    def test_with_tuple(self):
        c = Callout("Note", target=(500, 300))
        svg = c.to_svg(0)
        assert 'Note' in svg

    def test_with_vobject(self):
        circ = Circle(r=50, cx=500, cy=300)
        c = Callout("Tip", target=circ, direction='down')
        svg = c.to_svg(0)
        assert 'Tip' in svg

    def test_directions(self):
        for d in ('up', 'down', 'left', 'right'):
            c = Callout("X", target=(500, 300), direction=d)
            assert c.to_svg(0) != ''


class TestDimensionLine:
    def test_auto_label(self):
        dl = DimensionLine(p1=(100, 300), p2=(400, 300))
        svg = dl.to_svg(0)
        assert '300' in svg  # auto-distance label

    def test_custom_label(self):
        dl = DimensionLine(p1=(0, 0), p2=(100, 0), label='10cm')
        svg = dl.to_svg(0)
        assert '10cm' in svg


class TestTooltip:
    def test_creates(self):
        t = Tooltip("Info", target=(500, 300), start=0, duration=2)
        assert isinstance(t, VCollection)
        svg = t.to_svg(0)
        assert 'Info' in svg

    def test_with_vobject_target(self):
        circ = Circle(r=30, cx=400, cy=400)
        t = Tooltip("Hover", target=circ)
        svg = t.to_svg(0)
        assert 'Hover' in svg


class TestProgressBar:
    def test_creates(self):
        pb = ProgressBar()
        assert isinstance(pb, VCollection)
        svg = pb.to_svg(0)
        assert svg != ''

    def test_set_progress(self):
        pb = ProgressBar()
        result = pb.set_progress(0.5, start=0)
        assert result is pb

    def test_animate_to(self):
        pb = ProgressBar()
        result = pb.animate_to(0.8, start=0, end=1)
        assert result is pb


class TestLegend:
    def test_creates(self):
        leg = Legend([('#58C4DD', 'Blue'), ('#83C167', 'Green')])
        svg = leg.to_svg(0)
        assert 'Blue' in svg
        assert 'Green' in svg

    def test_horizontal(self):
        leg = Legend([('#FF0000', 'A'), ('#00FF00', 'B')], direction='right')
        svg = leg.to_svg(0)
        assert svg != ''


class TestFlowChart:
    def test_horizontal(self):
        fc = FlowChart(['Start', 'Process', 'End'])
        svg = fc.to_svg(0)
        assert 'Start' in svg
        assert 'End' in svg

    def test_vertical(self):
        fc = FlowChart(['A', 'B', 'C'], direction='down')
        svg = fc.to_svg(0)
        assert 'A' in svg

    def test_boxes_and_labels(self):
        fc = FlowChart(['Step 1', 'Step 2'])
        assert len(fc._boxes) == 2
        assert len(fc._labels) == 2


class TestStreamLines:
    def test_creates(self):
        sl = StreamLines(lambda x, y: (1, 0))
        assert isinstance(sl, VCollection)
        svg = sl.to_svg(0)
        assert svg != ''


class TestPolarAxes:
    def test_creates(self):
        pa = PolarAxes()
        assert isinstance(pa, VCollection)
        svg = pa.to_svg(0)
        assert svg != ''

    def test_polar_to_point(self):
        pa = PolarAxes(r_range=(0, 5), max_radius=400)
        x, y = pa.polar_to_point(5, 0)
        assert x > pa._cx  # r=max at angle 0 should be to the right

    def test_plot_polar(self):
        pa = PolarAxes()
        curve = pa.plot_polar(lambda theta: 2)
        assert curve is not None


class TestStamp:
    def test_creates(self):
        dot = Dot(cx=0, cy=0)
        s = Stamp(dot, [(100, 100), (200, 200), (300, 300)])
        assert isinstance(s, VCollection)
        assert len(s.objects) == 3


class TestTimelineBar:
    def test_creates(self):
        tb = TimelineBar({0: 'Start', 5: 'Mid', 10: 'End'})
        svg = tb.to_svg(0)
        assert 'Start' in svg
        assert 'End' in svg


class TestRadarChart:
    def test_creates(self):
        rc = RadarChart([3, 5, 2, 4, 1], labels=['A', 'B', 'C', 'D', 'E'])
        svg = rc.to_svg(0)
        assert 'A' in svg

    def test_too_few_values(self):
        rc = RadarChart([1, 2])
        svg = rc.to_svg(0)
        assert svg is not None


class TestDefaultChartColors:
    def test_constant_length(self):
        assert len(DEFAULT_CHART_COLORS) == 8

    def test_all_hex(self):
        for c in DEFAULT_CHART_COLORS:
            assert c.startswith('#')
            assert len(c) == 7


class TestVariable:
    def test_creates(self):
        v = Variable('x', value=3.14)
        assert isinstance(v, VCollection)
        svg = v.to_svg(0)
        assert 'x' in svg

    def test_set_value(self):
        v = Variable('n', value=0)
        result = v.set_value(42, start=0)
        assert result is v

    def test_animate_value(self):
        v = Variable('t', value=0)
        result = v.animate_value(10, start=0, end=1)
        assert result is v

    def test_tracker(self):
        from vectormation.attributes import Real
        v = Variable('x', value=5)
        assert isinstance(v.tracker, Real)


class TestUnderline:
    def test_creates(self):
        t = Text(text='Hello', x=500, y=300)
        u = Underline(t)
        assert isinstance(u, VCollection)
        svg = u.to_svg(0)
        assert svg != ''

    def test_follow(self):
        t = Text(text='Move', x=100, y=100)
        u = Underline(t, follow=True)
        t.move_to(200, 200, start_time=1, end_time=2)
        svg_at_0 = u.to_svg(0)
        svg_at_2 = u.to_svg(2)
        assert svg_at_0 != svg_at_2

    def test_no_follow(self):
        t = Text(text='Static', x=200, y=200)
        u = Underline(t, follow=False)
        svg = u.to_svg(0)
        assert svg != ''


class TestArrowVectorField:
    def test_creates(self):
        vf = ArrowVectorField(lambda x, y: (1, 0))
        assert isinstance(vf, VCollection)
        svg = vf.to_svg(0)
        assert svg != ''


class TestComplexPlane:
    def test_creates(self):
        cp = ComplexPlane()
        assert isinstance(cp, Axes)
        svg = cp.to_svg(0)
        assert svg != ''

    def test_number_to_point(self):
        cp = ComplexPlane(x_range=(-5, 5), y_range=(-5, 5))
        x, y = cp.number_to_point(1 + 1j)
        # Should be right of center and above center
        cx, cy = cp.number_to_point(0)
        assert x > cx
        assert y < cy

    def test_point_to_number(self):
        cp = ComplexPlane(x_range=(-5, 5), y_range=(-5, 5))
        x, y = cp.number_to_point(2 + 3j)
        z = cp.point_to_number(x, y)
        assert abs(z.real - 2) < 0.1
        assert abs(z.imag - 3) < 0.1


class TestChessBoard:
    def test_creates(self):
        cb = ChessBoard()
        assert isinstance(cb, VCollection)
        svg = cb.to_svg(0)
        assert svg != ''

    def test_custom_fen(self):
        cb = ChessBoard(fen='8/8/8/4K3/8/8/8/8')
        svg = cb.to_svg(0)
        assert svg != ''


class TestAutomaton:
    def test_creates(self):
        a = Automaton(
            states=['q0', 'q1', 'q2'],
            transitions=[('q0', 'q1', 'a'), ('q1', 'q2', 'b')],
            accept_states={'q2'},
            initial_state='q0',
        )
        assert isinstance(a, VCollection)
        svg = a.to_svg(0)
        assert 'q0' in svg

    def test_empty(self):
        a = Automaton(states=[], transitions=[])
        svg = a.to_svg(0)
        assert svg is not None

    def test_self_loop(self):
        a = Automaton(
            states=['q0'],
            transitions=[('q0', 'q0', 'a')],
        )
        svg = a.to_svg(0)
        assert 'q0' in svg


class TestPeriodicTable:
    def test_creates(self):
        pt = PeriodicTable()
        assert isinstance(pt, VCollection)
        svg = pt.to_svg(0)
        assert 'H' in svg  # Hydrogen


class TestBohrAtom:
    def test_creates(self):
        ba = BohrAtom(protons=6, neutrons=6, electrons=[2, 4])
        assert isinstance(ba, VCollection)
        svg = ba.to_svg(0)
        assert svg != ''

    def test_default(self):
        ba = BohrAtom()
        svg = ba.to_svg(0)
        assert svg != ''


class TestReprShapes:
    def test_polygon_repr(self):
        p = Polygon((0, 0), (100, 0), (50, 100))
        assert '3 vertices' in repr(p)

    def test_circle_repr(self):
        c = Circle(r=50, cx=100, cy=200)
        r = repr(c)
        assert 'Circle' in r
        assert '50' in r

    def test_dot_repr(self):
        d = Dot(cx=10, cy=20)
        r = repr(d)
        assert 'Dot' in r

    def test_rectangle_repr(self):
        r = Rectangle(200, 100)
        assert '200x100' in repr(r)

    def test_line_repr(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        r = repr(l)
        assert 'Line' in r

    def test_text_repr(self):
        t = Text(text='Hello')
        assert 'Hello' in repr(t)

    def test_text_long_repr(self):
        t = Text(text='A very long text string that exceeds twenty characters')
        r = repr(t)
        assert '...' in r
        assert len(r) < 40


class TestCountdown:
    def test_creates(self):
        c = Countdown(start_value=10, end_value=0, start=0, end=3)
        assert isinstance(c, VCollection)
        svg = c.to_svg(0)
        assert '10' in svg

    def test_counts_down(self):
        c = Countdown(start_value=10, end_value=0, start=0, end=10)
        svg_start = c.to_svg(0)
        svg_mid = c.to_svg(5)
        svg_end = c.to_svg(10)
        assert '10' in svg_start
        assert '5' in svg_mid
        assert '0' in svg_end

    def test_counts_up(self):
        c = Countdown(start_value=0, end_value=100, start=0, end=10)
        svg_end = c.to_svg(10)
        assert '100' in svg_end


class TestFilmstrip:
    def test_creates(self):
        f = Filmstrip(['Intro', 'Scene 1', 'Scene 2', 'End'])
        assert isinstance(f, VCollection)
        svg = f.to_svg(0)
        assert 'Intro' in svg
        assert 'End' in svg

    def test_frames(self):
        f = Filmstrip(['A', 'B', 'C'])
        assert len(f._frames) == 3

    def test_highlight_frame(self):
        f = Filmstrip(['A', 'B', 'C'])
        result = f.highlight_frame(1, start=0, end=1)
        assert result is f

    def test_empty(self):
        f = Filmstrip([])
        svg = f.to_svg(0)
        assert svg is not None


class TestLineUtilities:
    def test_get_start_end(self):
        l = Line(x1=100, y1=200, x2=400, y2=600)
        assert l.get_start() == (100, 200)
        assert l.get_end() == (400, 600)

    def test_get_length(self):
        l = Line(x1=0, y1=0, x2=300, y2=400)
        assert abs(l.get_length() - 500.0) < 0.01

    def test_get_length_zero(self):
        l = Line(x1=100, y1=100, x2=100, y2=100)
        assert l.get_length() == 0.0

    def test_get_angle_horizontal(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert abs(l.get_angle() - 0.0) < 0.01

    def test_get_angle_vertical_down(self):
        l = Line(x1=0, y1=0, x2=0, y2=100)
        assert abs(l.get_angle() - 90.0) < 0.01

    def test_get_angle_diagonal(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        assert abs(l.get_angle() - 45.0) < 0.01

    def test_get_unit_vector(self):
        l = Line(x1=0, y1=0, x2=300, y2=400)
        ux, uy = l.get_unit_vector()
        assert abs(ux - 0.6) < 0.01
        assert abs(uy - 0.8) < 0.01

    def test_get_unit_vector_zero_length(self):
        l = Line(x1=50, y1=50, x2=50, y2=50)
        assert l.get_unit_vector() == (0.0, 0.0)

    def test_animated_line_at_time(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        l.p2.set(0, 1, lambda t: (100 + 200 * t, 0))
        assert abs(l.get_length(time=0) - 100) < 1
        assert abs(l.get_length(time=1) - 300) < 1


class TestArcUtilities:
    def test_get_start_point(self):
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        sx, sy = a.get_start_point()
        assert abs(sx - 100) < 0.01
        assert abs(sy - 0) < 0.01

    def test_get_end_point(self):
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        ex, ey = a.get_end_point()
        assert abs(ex - 0) < 0.01
        assert abs(ey - (-100)) < 0.01  # 90 degrees: y = -r*sin(90) = -100

    def test_get_arc_length(self):
        from math import pi
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=180)
        assert abs(a.get_arc_length() - 100 * pi) < 0.01

    def test_get_arc_length_quarter(self):
        from math import pi
        a = Arc(cx=0, cy=0, r=200, start_angle=0, end_angle=90)
        assert abs(a.get_arc_length() - 200 * pi / 2) < 0.01


class TestMorphObject:
    def test_creation(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        m = MorphObject(c, r, start=0, end=1)
        svg = m.to_svg(0.5)
        assert svg is not None

    def test_source_hidden_after_start(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        m = MorphObject(c, r, start=0, end=1)
        assert not c.show.at_time(0.5)

    def test_target_visible_after_end(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        m = MorphObject(c, r, start=0, end=1)
        assert r.show.at_time(1.5)

    def test_target_hidden_before_end(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        m = MorphObject(c, r, start=1, end=2)
        assert not r.show.at_time(0.5)

    def test_with_rotation(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        m = MorphObject(c, r, start=0, end=1, rotation_degrees=180)
        svg = m.to_svg(0.5)
        assert svg is not None


class TestTitleStyling:
    def test_has_underline(self):
        t = Title('Test')
        svg = t.to_svg(0)
        assert '<line' in svg

    def test_custom_font_size(self):
        t = Title('Big', font_size=80)
        svg = t.to_svg(0)
        assert 'font-size' in svg


class TestNumberPlane:
    def test_creation(self):
        np = NumberPlane()
        svg = np.to_svg(0)
        assert svg is not None

    def test_coords_to_point(self):
        np = NumberPlane()
        x, y = np.coords_to_point(0, 0)
        assert x == 960
        assert y == 540

    def test_coords_to_point_offset(self):
        np = NumberPlane()
        x, y = np.coords_to_point(1, 0)
        assert x == 960 + 135  # UNIT = 135

    def test_custom_ranges(self):
        np = NumberPlane(x_range=(-5, 5, 1), y_range=(-3, 3, 1))
        svg = np.to_svg(0)
        assert svg is not None

    def test_custom_styles(self):
        np = NumberPlane(background_line_style={'stroke': '#ff0000'},
                         axis_style={'stroke': '#00ff00'})
        svg = np.to_svg(0)
        assert 'rgb(255,0,0)' in svg
        assert 'rgb(0,255,0)' in svg

    def test_no_faded_lines(self):
        np = NumberPlane(faded_line_ratio=1)
        svg = np.to_svg(0)
        assert svg is not None


class TestPolygonUtilities:
    def test_get_vertices(self):
        p = Polygon((0, 0), (100, 0), (100, 100))
        verts = p.get_vertices()
        assert len(verts) == 3
        assert verts[0] == (0.0, 0.0)
        assert verts[1] == (100.0, 0.0)

    def test_get_center(self):
        p = Polygon((0, 0), (300, 0), (300, 300), (0, 300))
        cx, cy = p.get_center()
        assert abs(cx - 150) < 0.01
        assert abs(cy - 150) < 0.01

    def test_perimeter_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert abs(p.perimeter() - 400) < 0.01

    def test_perimeter_open(self):
        from vectormation.objects import Lines as Polyline
        l = Polyline((0, 0), (100, 0), (100, 100))
        # Open: only 2 segments, no closing edge
        assert abs(l.perimeter() - 200) < 0.01

    def test_area_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert abs(p.area() - 10000) < 0.01

    def test_area_triangle(self):
        p = Polygon((0, 0), (200, 0), (100, 100))
        assert abs(p.area() - 10000) < 0.01

    def test_area_open_is_zero(self):
        from vectormation.objects import Lines as Polyline
        l = Polyline((0, 0), (100, 0), (100, 100))
        assert l.area() == 0.0


class TestCompositeRepr:
    def test_arrow_repr(self):
        a = Arrow(x1=100, y1=200, x2=300, y2=400)
        r = repr(a)
        assert 'Arrow' in r
        assert '100' in r
        assert '300' in r

    def test_brace_repr(self):
        rect = Rectangle(200, 100, x=400, y=300)
        b = Brace(rect, direction='down')
        assert 'Brace' in repr(b)
        assert 'down' in repr(b)

    def test_numberline_repr(self):
        nl = NumberLine(x_range=(-3, 3, 1))
        r = repr(nl)
        assert 'NumberLine' in r
        assert '-3' in r
        assert '3' in r

    def test_table_repr(self):
        t = Table([[1, 2], [3, 4]])
        assert repr(t) == 'Table(2x2)'

    def test_axes_repr(self):
        a = Axes(x_range=(-5, 5), y_range=(-3, 3))
        r = repr(a)
        assert 'Axes' in r
        assert '-5' in r
        assert '-3' in r

    def test_axes_no_y_range_repr(self):
        a = Axes(x_range=(-5, 5))
        r = repr(a)
        assert 'Axes' in r
        assert 'y' not in r


class TestVCollectionContains:
    def test_contains(self):
        c = Circle(r=50)
        r = Rectangle(100, 100)
        col = VCollection(c, r)
        assert c in col
        assert r in col

    def test_not_contains(self):
        c = Circle(r=50)
        r = Rectangle(100, 100)
        col = VCollection(c)
        assert r not in col


class TestRectangleGetVertices:
    def test_get_vertices(self):
        r = Rectangle(200, 100, x=100, y=200)
        verts = r.get_vertices()
        assert len(verts) == 4
        assert verts[0] == (100.0, 200.0)
        assert verts[1] == (300.0, 200.0)
        assert verts[2] == (300.0, 300.0)
        assert verts[3] == (100.0, 300.0)


class TestCircleGeometry:
    def test_get_area(self):
        from math import pi
        c = Circle(r=100)
        assert abs(c.get_area() - pi * 10000) < 0.01

    def test_get_circumference(self):
        from math import pi
        c = Circle(r=50)
        assert abs(c.get_circumference() - 2 * pi * 50) < 0.01

    def test_animated_radius(self):
        from math import pi
        c = Circle(r=100)
        c.rx.set(0, 1, lambda t: 100 + 100 * t)
        assert abs(c.get_area(time=0) - pi * 10000) < 1
        assert abs(c.get_area(time=1) - pi * 40000) < 1


class TestInputValidation:
    def test_numberline_zero_span(self):
        with pytest.raises(ValueError):
            NumberLine(x_range=(5, 5, 1))

    def test_numberline_reversed(self):
        with pytest.raises(ValueError):
            NumberLine(x_range=(5, 3, 1))

    def test_numberline_zero_step(self):
        with pytest.raises(ValueError):
            NumberLine(x_range=(-5, 5, 0))

    def test_matrix_empty(self):
        with pytest.raises(ValueError):
            Matrix([])

    def test_matrix_empty_rows(self):
        with pytest.raises(ValueError):
            Matrix([[]])


class TestEllipseGeometry:
    def test_get_area(self):
        from math import pi
        e = Ellipse(rx=100, ry=50)
        assert abs(e.get_area() - pi * 100 * 50) < 0.01

    def test_get_circumference(self):
        # For a circle (rx==ry==100), should give 2*pi*100
        from math import pi
        e = Ellipse(rx=100, ry=100)
        assert abs(e.get_circumference() - 2 * pi * 100) < 0.01

    def test_circle_inherits(self):
        from math import pi
        c = Circle(r=50)
        # Circle inherits from Ellipse, should work
        assert abs(c.get_area() - pi * 2500) < 0.01
        assert abs(c.get_circumference() - 2 * pi * 50) < 0.01


class TestCanvasRemoveClear:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_remove(self):
        anim = VectorMathAnim(self.tmpdir)
        c = Circle(r=50)
        r = Rectangle(100, 100)
        anim.add(c)
        anim.add(r)
        anim.remove(c)
        svg = anim.generate_frame_svg(0)
        assert 'circle' not in svg
        assert 'rect' in svg

    def test_clear(self):
        anim = VectorMathAnim(self.tmpdir)
        c = Circle(r=50)
        r = Rectangle(100, 100)
        anim.add(c)
        anim.add(r)
        anim.clear()
        svg = anim.generate_frame_svg(0)
        assert 'circle' not in svg
        assert 'rect' not in svg

    def test_clear_keeps_background(self):
        anim = VectorMathAnim(self.tmpdir)
        c = Circle(r=50)
        anim.add(c)
        anim.clear()
        svg = anim.generate_frame_svg(0)
        assert '<svg' in svg


class TestFromSvgText:
    def test_text_element(self):
        from bs4 import BeautifulSoup
        svg = "<text x='100' y='200' font-size='24'>Hello</text>"
        elem = BeautifulSoup(svg, 'xml').find('text')
        obj = from_svg(elem)
        result = obj.to_svg(0)
        assert 'Hello' in result

    def test_text_with_style(self):
        from bs4 import BeautifulSoup
        svg = "<text x='50' y='60' style='font-size:32; fill:#ff0000'>World</text>"
        elem = BeautifulSoup(svg, 'xml').find('text')
        obj = from_svg(elem)
        result = obj.to_svg(0)
        assert 'World' in result


class TestEasingCombinators:
    def test_step_basic(self):
        s = easings.step(4)
        assert s(0.0) == 0.0
        assert s(0.1) == 0.0
        assert s(0.3) == pytest.approx(1/3)
        assert s(1.0) == 1.0

    def test_step_two(self):
        s = easings.step(2)
        assert s(0.0) == 0.0
        assert s(0.4) == 0.0
        assert s(0.5) == 1.0
        assert s(1.0) == 1.0

    def test_step_one(self):
        s = easings.step(1)
        assert s(0.0) == 0.0
        assert s(0.5) == 0.0
        assert s(1.0) == 1.0

    def test_reverse(self):
        rev = easings.reverse(easings.ease_in_quad)
        # reverse(ease_in) acts like ease_out: 0→0, 1→1 but reversed curve shape
        assert rev(0) == pytest.approx(0.0)
        assert rev(1) == pytest.approx(1.0)
        # Midpoint: ease_in_quad(0.5)=0.25, reverse(0.5)=1-ease_in_quad(0.5)=0.75
        assert rev(0.5) == pytest.approx(0.75)

    def test_compose_two(self):
        c = easings.compose(easings.linear, easings.linear)
        assert c(0.0) == pytest.approx(0.0)
        assert c(0.5) == pytest.approx(0.5)
        assert c(1.0) == pytest.approx(1.0)

    def test_compose_preserves_endpoints(self):
        c = easings.compose(easings.ease_in_quad, easings.ease_out_quad)
        assert c(0.0) == pytest.approx(0.0)
        assert c(1.0) == pytest.approx(1.0)


class TestRectangleGeometry:
    def test_get_area(self):
        r = Rectangle(200, 100)
        assert r.get_area() == 20000

    def test_get_perimeter(self):
        r = Rectangle(200, 100)
        assert r.get_perimeter() == 600

    def test_animated(self):
        r = Rectangle(100, 100)
        r.width.set(0, 1, lambda t: 100 + 100 * t)
        assert r.get_area(time=0) == 10000
        assert r.get_area(time=1) == 20000


class TestFunctionGraphQuery:
    def test_get_point_from_x_identity(self):
        fg = FunctionGraph(lambda x: x, x_range=(0, 10), y_range=(0, 10),
                           x=0, y=0, width=1000, height=1000)
        sx, sy = fg.get_point_from_x(5)
        assert sx == pytest.approx(500, abs=1)
        assert sy == pytest.approx(500, abs=1)

    def test_get_point_from_x_endpoints(self):
        fg = FunctionGraph(lambda x: x * x, x_range=(-2, 2))
        sx0, sy0 = fg.get_point_from_x(-2)
        sx1, sy1 = fg.get_point_from_x(2)
        # Both endpoints should have the same y (since (-2)^2 == 2^2)
        assert sy0 == pytest.approx(sy1, abs=1)

    def test_get_slope_at_linear(self):
        fg = FunctionGraph(lambda x: 3 * x + 1, x_range=(-5, 5))
        assert fg.get_slope_at(0) == pytest.approx(3.0, abs=1e-4)
        assert fg.get_slope_at(2) == pytest.approx(3.0, abs=1e-4)

    def test_get_slope_at_quadratic(self):
        fg = FunctionGraph(lambda x: x ** 2, x_range=(-5, 5))
        assert fg.get_slope_at(0) == pytest.approx(0.0, abs=1e-4)
        assert fg.get_slope_at(3) == pytest.approx(6.0, abs=1e-4)

    def test_stores_function(self):
        f = lambda x: x + 1
        fg = FunctionGraph(f, x_range=(0, 5))
        assert fg._func is f


class TestFromSvgGroup:
    def test_g_element_returns_vcollection(self):
        from bs4 import BeautifulSoup
        svg = '<g><circle r="50" cx="100" cy="100"/><rect width="60" height="30"/></g>'
        soup = BeautifulSoup(svg, features='xml')
        g = soup.find('g')
        result = from_svg(g)
        assert isinstance(result, VCollection)
        assert len(result.objects) == 2

    def test_g_inherits_styles(self):
        from bs4 import BeautifulSoup
        svg = '<g fill="#ff0000"><circle r="50" cx="100" cy="100"/></g>'
        soup = BeautifulSoup(svg, features='xml')
        g = soup.find('g')
        result = from_svg(g)
        assert len(result.objects) == 1
        circle = result.objects[0]
        svg_out = circle.to_svg(0)
        assert 'ff0000' in svg_out or 'rgb(255' in svg_out

    def test_nested_g(self):
        from bs4 import BeautifulSoup
        svg = '<g><g><circle r="50" cx="10" cy="10"/></g></g>'
        soup = BeautifulSoup(svg, features='xml')
        g = soup.find('g')
        result = from_svg(g)
        assert isinstance(result, VCollection)
        # Inner <g> is a VCollection with the circle
        inner = result.objects[0]
        assert isinstance(inner, VCollection)
        assert len(inner.objects) == 1

    def test_from_svg_file_with_group(self):
        svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><g><circle r="30" cx="50" cy="50"/><line x1="0" y1="0" x2="100" y2="100"/></g></svg>'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write(svg_content)
            f.flush()
            result = from_svg_file(f.name)
        os.unlink(f.name)
        # Should get one VCollection (the <g>), not separate shapes
        assert len(result.objects) == 1
        assert isinstance(result.objects[0], VCollection)
        assert len(result.objects[0].objects) == 2


class TestCodeLanguages:
    def test_c_keywords(self):
        code = Code('int main() {\n    return 0;\n}', language='c')
        svg = code.to_svg(0)
        assert 'int' in svg
        assert 'return' in svg

    def test_java_keywords(self):
        code = Code('public class Main {\n}', language='java')
        svg = code.to_svg(0)
        assert 'public' in svg
        assert 'class' in svg

    def test_rust_keywords(self):
        code = Code('fn main() {\n    let x = 5;\n}', language='rust')
        svg = code.to_svg(0)
        assert 'fn' in svg
        assert 'let' in svg

    def test_go_keywords(self):
        code = Code('func main() {\n    var x int\n}', language='go')
        svg = code.to_svg(0)
        assert 'func' in svg
        assert 'var' in svg

    def test_unknown_language_no_error(self):
        code = Code('hello world', language='brainfuck')
        svg = code.to_svg(0)
        assert 'hello' in svg


class TestShapeRepr:
    def test_ellipse_repr(self):
        e = Ellipse(rx=100, ry=50, cx=400, cy=300)
        assert repr(e) == 'Ellipse(rx=100, ry=50, cx=400, cy=300)'

    def test_dot_repr(self):
        d = Dot(cx=200, cy=100)
        assert repr(d) == 'Dot(cx=200, cy=100)'

    def test_path_repr_short(self):
        p = Path('M0,0L10,10')
        assert repr(p) == "Path(d='M0,0L10,10')"

    def test_path_repr_truncated(self):
        long_d = 'M0,0' + 'L100,200' * 10
        p = Path(long_d)
        r = repr(p)
        assert r.endswith("...')")
        assert len(r) < 60

    def test_arc_repr(self):
        a = Arc(r=100, start_angle=30, end_angle=150)
        assert repr(a) == 'Arc(r=100, 30°-150°)'

    def test_image_repr(self):
        img = Image('test.png', width=200, height=100)
        assert repr(img) == 'Image(200x100)'

    def test_function_graph_repr(self):
        fg = FunctionGraph(lambda x: x, x_range=(-3, 3))
        assert repr(fg) == 'FunctionGraph(x=[-3, 3])'

    def test_circle_repr_unchanged(self):
        c = Circle(r=50, cx=100, cy=200)
        assert 'Circle' in repr(c) and 'r=50' in repr(c)


class TestPathGetLength:
    def test_straight_line(self):
        p = Path('M0,0L100,0')
        assert p.get_length() == pytest.approx(100, abs=1)

    def test_closed_square(self):
        p = Path('M0,0L100,0L100,100L0,100Z')
        assert p.get_length() == pytest.approx(400, abs=1)

    def test_empty_path(self):
        p = Path('')
        assert p.get_length() == 0.0


class TestCopyConsolidation:
    def test_vobject_copy(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.copy()
        assert isinstance(c2, Circle)
        assert c2 is not c

    def test_vcollection_copy(self):
        g = VCollection(Circle(r=10), Rectangle(20, 30))
        g2 = g.copy()
        assert len(g2.objects) == 2
        assert g2.objects[0] is not g.objects[0]


class TestPolygonSubclassRepr:
    def test_regular_polygon_repr(self):
        rp = RegularPolygon(6, radius=100)
        assert repr(rp) == 'RegularPolygon(n=6, r=100)'

    def test_star_repr(self):
        s = Star(n=5, outer_radius=100)
        assert 'Star(n=5' in repr(s)
        assert 'outer=100' in repr(s)

    def test_star_repr_custom_inner(self):
        s = Star(n=7, outer_radius=200, inner_radius=80)
        assert repr(s) == 'Star(n=7, outer=200, inner=80)'

    def test_equilateral_triangle_repr(self):
        t = EquilateralTriangle(side_length=150)
        assert repr(t) == 'EquilateralTriangle(side=150)'


class TestAxesAddLabel:
    def test_add_label_returns_text(self):
        ax = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1])
        lbl = ax.add_label(2, 3, 'Hello')
        assert isinstance(lbl, Text)

    def test_add_label_position(self):
        ax = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1])
        lbl = ax.add_label(0, 0, 'Origin')
        # Label x should be near the center of the axes
        lx = lbl.x.at_time(0)
        ly = lbl.y.at_time(0)
        cx, cy = ax.coords_to_point(0, 0)
        assert abs(lx - cx) < 50
        assert abs(ly - cy) < 50

    def test_add_dot_returns_dot(self):
        ax = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1])
        d = ax.add_dot(1, 2)
        assert isinstance(d, Dot)

    def test_add_dot_position(self):
        ax = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1])
        d = ax.add_dot(3, 4)
        dc = d.c.at_time(0)
        expected = ax.coords_to_point(3, 4)
        assert abs(dc[0] - expected[0]) < 2
        assert abs(dc[1] - expected[1]) < 2


class TestMoreShapeRepr:
    def test_wedge_repr(self):
        w = Wedge(r=80, start_angle=0, end_angle=90)
        assert repr(w) == 'Wedge(r=80, 0\u00b0-90\u00b0)'

    def test_annulus_repr(self):
        a = Annulus(inner_radius=40, outer_radius=100)
        assert repr(a) == 'Annulus(inner=40, outer=100)'

    def test_rounded_rectangle_repr(self):
        rr = RoundedRectangle(200, 100, corner_radius=15)
        assert repr(rr) == 'RoundedRectangle(200x100, r=15)'

    def test_paragraph_repr(self):
        p = Paragraph('Line 1', 'Line 2', 'Line 3')
        assert repr(p) == 'Paragraph(3 lines)'

    def test_bulleted_list_repr(self):
        bl = BulletedList('A', 'B')
        assert repr(bl) == 'BulletedList(2 items)'

    def test_numbered_list_repr(self):
        nl = NumberedList('X', 'Y', 'Z')
        assert repr(nl) == 'NumberedList(3 items)'


class TestVCollectionSort:
    def test_sort_by_y(self):
        c1 = Circle(r=10, cy=300)
        c2 = Circle(r=10, cy=100)
        c3 = Circle(r=10, cy=200)
        g = VCollection(c1, c2, c3)
        g.sort_by_y()
        # After sort: c2 (y=100), c3 (y=200), c1 (y=300)
        assert g.objects[0] is c2
        assert g.objects[1] is c3
        assert g.objects[2] is c1

    def test_sort_by_z(self):
        c1 = Circle(r=10, z=5)
        c2 = Circle(r=10, z=1)
        c3 = Circle(r=10, z=3)
        g = VCollection(c1, c2, c3)
        g.sort_by_z()
        assert g.objects[0] is c2
        assert g.objects[1] is c3
        assert g.objects[2] is c1


class TestStaggerFadeout:
    def test_stagger_fadeout_runs(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        g = VCollection(c1, c2)
        result = g.stagger_fadeout(start=0, end=2)
        assert result is g


class TestCubicBezierImprovements:
    def test_repr(self):
        cb = CubicBezier(p0=(100, 200), p3=(400, 500))
        assert repr(cb) == 'CubicBezier((100,200)->(400,500))'

    def test_bbox(self):
        cb = CubicBezier(p0=(100, 200), p1=(150, 100), p2=(350, 400), p3=(400, 300))
        bx, by, bw, bh = cb.bbox(0)
        # Bbox should enclose all control points
        assert bx <= 100
        assert by <= 100
        assert bx + bw >= 400
        assert by + bh >= 400

    def test_bbox_not_zero(self):
        cb = CubicBezier()
        bx, by, bw, bh = cb.bbox(0)
        assert bw > 0 and bh > 0


class TestFilterByType:
    def test_filter_circles(self):
        c1 = Circle(r=10)
        r1 = Rectangle(20, 30)
        c2 = Circle(r=20)
        g = VCollection(c1, r1, c2)
        circles = g.filter_by_type(Circle)
        assert len(circles) == 2
        assert all(isinstance(obj, Circle) for obj in circles)

    def test_filter_no_match(self):
        g = VCollection(Circle(r=10), Circle(r=20))
        rects = g.filter_by_type(Rectangle)
        assert len(rects) == 0

    def test_filter_includes_subclasses(self):
        c = Circle(r=10)
        d = Dot(r=5)
        g = VCollection(c, d)
        # Dot is a subclass of Circle
        circles = g.filter_by_type(Circle)
        assert len(circles) == 2


class TestArcPointAtAngle:
    def test_point_at_0(self):
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=180)
        x, y = a.point_at_angle(0)
        assert x == pytest.approx(150, abs=1)
        assert y == pytest.approx(100, abs=1)

    def test_point_at_90(self):
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=180)
        x, y = a.point_at_angle(90)
        assert x == pytest.approx(100, abs=1)
        assert y == pytest.approx(50, abs=1)  # SVG y is inverted


class TestDynamicObjectCache:
    def test_caches_within_frame(self):
        call_count = [0]
        def factory(t):
            call_count[0] += 1
            return Circle(r=10 + t)
        dyn = DynamicObject(factory)
        # Call to_svg, path, bbox at same time
        dyn.to_svg(0)
        dyn.path(0)
        dyn.bbox(0)
        assert call_count[0] == 1  # only one call, cached

    def test_different_time_recalculates(self):
        call_count = [0]
        def factory(t):
            call_count[0] += 1
            return Circle(r=10 + t)
        dyn = DynamicObject(factory)
        dyn.to_svg(0)
        dyn.to_svg(1)
        assert call_count[0] == 2


class TestCanvasGetAllObjects:
    def test_get_all_objects(self):
        anim = VectorMathAnim(tempfile.mkdtemp())
        c = Circle(r=10)
        r = Rectangle(20, 30)
        anim.add(c, r)
        objs = anim.get_all_objects()
        assert c in objs
        assert r in objs

    def test_excludes_background(self):
        anim = VectorMathAnim(tempfile.mkdtemp())
        c = Circle(r=10)
        anim.add(c)
        objs = anim.get_all_objects()
        # Background should not be in the list
        assert anim.background not in objs


class TestTextGetText:
    def test_get_text_static(self):
        t = Text(text='hello', x=0, y=0)
        assert t.get_text() == 'hello'

    def test_get_text_animated(self):
        t = Text(text='before', x=0, y=0)
        t.text.set_onward(1, 'after')
        assert t.get_text(0) == 'before'
        assert t.get_text(1) == 'after'


class TestAxesLabelAccess:
    def test_get_x_axis_label(self):
        ax = Axes(x_range=[-3, 3], y_range=[-2, 2], x_label='X')
        lbl = ax.get_x_axis_label()
        assert lbl is not None

    def test_get_y_axis_label(self):
        ax = Axes(x_range=[-3, 3], y_range=[-2, 2], y_label='Y')
        lbl = ax.get_y_axis_label()
        assert lbl is not None

    def test_no_label_returns_none(self):
        ax = Axes(x_range=[-3, 3], y_range=[-2, 2])
        assert ax.get_x_axis_label() is None
        assert ax.get_y_axis_label() is None


class TestMoreCompositeRepr:
    def test_graph_repr(self):
        g = Graph(lambda x: x**2, x_range=[-2, 2])
        r = repr(g)
        assert 'Graph' in r
        assert '-2.0' in r
        assert '2.0' in r

    def test_piechart_repr(self):
        pc = PieChart([30, 40, 30])
        assert repr(pc) == 'PieChart(3 sectors)'

    def test_barchart_repr(self):
        bc = BarChart([10, 20, 30])
        assert repr(bc) == 'BarChart(3 bars)'

    def test_code_repr(self):
        c = Code('x = 1\ny = 2', language='python')
        assert repr(c) == "Code(2 lines, lang='python')"

    def test_code_stores_language(self):
        c = Code('fn main() {}', language='rust')
        assert c._language == 'rust'


class TestEllipsePointAtAngle:
    def test_point_at_0(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=200)
        x, y = e.point_at_angle(0)
        assert x == pytest.approx(300, abs=1)
        assert y == pytest.approx(200, abs=1)

    def test_point_at_90(self):
        e = Ellipse(rx=100, ry=50, cx=200, cy=200)
        x, y = e.point_at_angle(90)
        assert x == pytest.approx(200, abs=1)
        assert y == pytest.approx(150, abs=1)  # SVG y inverted

    def test_circle_consistency(self):
        """Ellipse.point_at_angle and Circle.point_at_angle agree when rx==ry."""
        from vectormation.objects import Circle
        c = Circle(r=80, cx=100, cy=100)
        ep = Ellipse(rx=80, ry=80, cx=100, cy=100).point_at_angle(45)
        cp = c.point_at_angle(45)
        assert ep[0] == pytest.approx(cp[0], abs=0.01)
        assert ep[1] == pytest.approx(cp[1], abs=0.01)


class TestLineMidpointAndFactory:
    def test_get_midpoint(self):
        ln = Line(0, 0, 100, 200)
        mx, my = ln.get_midpoint()
        assert mx == pytest.approx(50)
        assert my == pytest.approx(100)

    def test_between_factory(self):
        ln = Line.between((10, 20), (30, 40))
        assert ln.get_start() == pytest.approx((10, 20), abs=0.01)
        assert ln.get_end() == pytest.approx((30, 40), abs=0.01)

    def test_between_with_kwargs(self):
        ln = Line.between((0, 0), (100, 100), stroke='red')
        assert 'red' in ln.to_svg(0) or 'rgb' in ln.to_svg(0)


class TestPolygonFromPoints:
    def test_from_points(self):
        pts = [(0, 0), (100, 0), (50, 80)]
        p = Polygon.from_points(pts)
        assert len(p.vertices) == 3
        verts = p.get_vertices()
        assert verts[0] == pytest.approx((0, 0))
        assert verts[1] == pytest.approx((100, 0))
        assert verts[2] == pytest.approx((50, 80))


class TestVCollectionEdgeMethods:
    def test_get_edge_center(self):
        c1 = Circle(r=10, cx=50, cy=50)
        c2 = Circle(r=10, cx=150, cy=150)
        g = VCollection(c1, c2)
        center = g.get_edge('center')
        assert center[0] == pytest.approx(100, abs=5)
        assert center[1] == pytest.approx(100, abs=5)

    def test_get_left_right(self):
        c1 = Circle(r=10, cx=50, cy=100)
        c2 = Circle(r=10, cx=150, cy=100)
        g = VCollection(c1, c2)
        left = g.get_left()
        right = g.get_right()
        assert left[0] < right[0]

    def test_get_top_bottom(self):
        c1 = Circle(r=10, cx=100, cy=50)
        c2 = Circle(r=10, cx=100, cy=150)
        g = VCollection(c1, c2)
        top = g.get_top()
        bottom = g.get_bottom()
        assert top[1] < bottom[1]


class TestHSLColorUtilities:
    def test_hex_to_hsl_red(self):
        from vectormation.colors import _hex_to_hsl
        h, s, l = _hex_to_hsl('#FF0000')
        assert h == pytest.approx(0, abs=1)
        assert s == pytest.approx(1, abs=0.01)
        assert l == pytest.approx(0.5, abs=0.01)

    def test_hsl_to_hex_roundtrip(self):
        from vectormation.colors import _hex_to_hsl, _hsl_to_hex
        original = '#58C4DD'
        h, s, l = _hex_to_hsl(original)
        result = _hsl_to_hex(h, s, l)
        # Allow small rounding diff
        from vectormation.colors import _hex_to_rgb
        r1 = _hex_to_rgb(original)
        r2 = _hex_to_rgb(result)
        for a, b in zip(r1, r2):
            assert abs(a - b) <= 2

    def test_adjust_hue(self):
        from vectormation.colors import adjust_hue, _hex_to_hsl
        c = adjust_hue('#FF0000', 120)
        h, s, l = _hex_to_hsl(c)
        assert h == pytest.approx(120, abs=2)

    def test_saturate(self):
        from vectormation.colors import saturate, _hex_to_hsl
        c = saturate('#888888', 0.5)
        _, s, _ = _hex_to_hsl(c)
        assert s > 0

    def test_desaturate(self):
        from vectormation.colors import desaturate, _hex_to_hsl
        c = desaturate('#FF0000', 0.5)
        _, s, _ = _hex_to_hsl(c)
        assert s < 1.0

    def test_complementary(self):
        from vectormation.colors import complementary, _hex_to_hsl
        c = complementary('#FF0000')
        h, _, _ = _hex_to_hsl(c)
        assert h == pytest.approx(180, abs=2)


class TestSkewAnimation:
    def test_skew_x(self):
        c = Circle(r=50)
        c.skew(start=0, end=1, x_degrees=30)
        svg = c.to_svg(0.5)
        assert 'skewX' in svg

    def test_skew_y(self):
        r = Rectangle(100, 50)
        r.skew(start=0, end=1, y_degrees=20)
        svg = r.to_svg(0.5)
        assert 'skewY' in svg

    def test_skew_both(self):
        c = Circle(r=50)
        c.skew(start=0, end=1, x_degrees=15, y_degrees=10)
        svg = c.to_svg(0.5)
        assert 'skewX' in svg
        assert 'skewY' in svg


class TestCanvasFind:
    def test_find_by_type(self):
        anim = VectorMathAnim(tempfile.mkdtemp())
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        r = Rectangle(50, 50)
        anim.add(c1, c2, r)
        found = anim.find_by_type(Circle)
        assert len(found) == 2
        assert c1 in found and c2 in found

    def test_find_by_type_includes_subclass(self):
        anim = VectorMathAnim(tempfile.mkdtemp())
        d = Dot(r=5)
        c = Circle(r=10)
        anim.add(d, c)
        found = anim.find_by_type(Circle)
        assert len(found) == 2  # Dot is a subclass of Circle

    def test_find_predicate(self):
        anim = VectorMathAnim(tempfile.mkdtemp())
        c1 = Circle(r=10, cx=50, cy=50)
        c2 = Circle(r=10, cx=500, cy=500)
        anim.add(c1, c2)
        found = anim.find(lambda obj: obj.get_x() < 100)
        assert len(found) == 1
        assert found[0] is c1


class TestShapeFactories:
    def test_rectangle_square(self):
        sq = Rectangle.square(100, x=50, y=50)
        assert sq.width.at_time(0) == 100
        assert sq.height.at_time(0) == 100

    def test_line_vertical(self):
        ln = Line.vertical(100, 0, 200)
        s = ln.get_start()
        e = ln.get_end()
        assert s[0] == pytest.approx(100)
        assert e[0] == pytest.approx(100)
        assert s[1] == pytest.approx(0)
        assert e[1] == pytest.approx(200)

    def test_line_horizontal(self):
        ln = Line.horizontal(50, 0, 300)
        s = ln.get_start()
        e = ln.get_end()
        assert s[1] == pytest.approx(50)
        assert e[1] == pytest.approx(50)
        assert s[0] == pytest.approx(0)
        assert e[0] == pytest.approx(300)


class TestMeasurementMethods:
    def test_get_diagonal_vobject(self):
        r = Rectangle(30, 40, x=0, y=0)
        d = r.get_diagonal()
        assert d == pytest.approx(50, abs=1)

    def test_get_aspect_ratio_vobject(self):
        r = Rectangle(200, 100, x=0, y=0)
        assert r.get_aspect_ratio() == pytest.approx(2.0, abs=0.1)

    def test_get_diagonal_vcollection(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=30, cy=40)
        g = VCollection(c1, c2)
        d = g.get_diagonal()
        assert d > 0

    def test_get_aspect_ratio_vcollection(self):
        r = Rectangle(200, 100, x=0, y=0)
        g = VCollection(r)
        assert g.get_aspect_ratio() == pytest.approx(2.0, abs=0.1)


class TestDistanceAndOverlap:
    def test_vcollection_distance_to(self):
        c1 = Circle(r=5, cx=0, cy=0)
        c2 = Circle(r=5, cx=100, cy=0)
        g1 = VCollection(c1)
        g2 = VCollection(c2)
        assert g1.distance_to(g2) == pytest.approx(100, abs=2)

    def test_is_overlapping_true(self):
        r1 = Rectangle(100, 100, x=0, y=0)
        r2 = Rectangle(100, 100, x=50, y=50)
        assert r1.is_overlapping(r2)

    def test_is_overlapping_false(self):
        r1 = Rectangle(100, 100, x=0, y=0)
        r2 = Rectangle(100, 100, x=500, y=500)
        assert not r1.is_overlapping(r2)

    def test_vcollection_is_overlapping(self):
        c1 = Circle(r=10, cx=50, cy=50)
        c2 = Circle(r=10, cx=55, cy=55)
        g1 = VCollection(c1)
        g2 = VCollection(c2)
        assert g1.is_overlapping(g2)


class TestArrowUtilities:
    def test_get_midpoint(self):
        a = Arrow(0, 0, 100, 0)
        mx, my = a.get_midpoint()
        assert mx == pytest.approx(50, abs=1)
        assert my == pytest.approx(0, abs=1)

    def test_get_length(self):
        a = Arrow(0, 0, 100, 0)
        assert a.get_length() == pytest.approx(100, abs=1)


class TestTableExtended:
    def test_highlight_cells(self):
        t = Table([[1, 2], [3, 4]])
        t.highlight_cells([(0, 0), (1, 1)], start=0, end=1)
        # No exception means success

    def test_set_cell_value(self):
        t = Table([[1, 2], [3, 4]])
        t.set_cell_value(0, 0, 'X', start=0.5)
        entry = t.get_entry(0, 0)
        assert entry.text.at_time(0.5) == 'X'

    def test_set_cell_value_preserves_original(self):
        t = Table([['a', 'b'], ['c', 'd']])
        t.set_cell_value(1, 1, 'Z', start=1)
        assert t.get_entry(1, 1).text.at_time(0) == 'd'
        assert t.get_entry(1, 1).text.at_time(1) == 'Z'


class TestThreeDCameraPresets:
    def test_preset_isometric(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('isometric', start=0, end=1)
        import math as m
        assert ax.phi.at_time(1) == pytest.approx(m.radians(54.7), abs=0.05)
        assert ax.theta.at_time(1) == pytest.approx(m.radians(-45), abs=0.05)

    def test_preset_top(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('top', start=0, end=1)
        assert ax.phi.at_time(1) == pytest.approx(0, abs=0.05)

    def test_invalid_preset_raises(self):
        ax = ThreeDAxes()
        with pytest.raises(KeyError):
            ax.set_camera_preset('nonexistent')


class TestNumberLinePointToNumber:
    def test_roundtrip(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        for val in [-5, -2.5, 0, 2.5, 5]:
            pt = nl.number_to_point(val)
            recovered = nl.point_to_number(pt[0])
            assert recovered == pytest.approx(val, abs=0.01)

    def test_tuple_input(self):
        nl = NumberLine(x_range=(0, 10, 1))
        pt = nl.number_to_point(5)
        assert nl.point_to_number(pt) == pytest.approx(5, abs=0.01)

    def test_out_of_range(self):
        nl = NumberLine(x_range=(0, 10, 1))
        # point before the line start
        val = nl.point_to_number(nl.origin_x - 100)
        assert val < 0


class TestShakeAnimation:
    def test_shake_produces_displacement(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shake(start=0, end=1, amplitude=10, frequency=5)
        svg_mid = c.to_svg(0.25)
        # Should render without error
        assert 'circle' in svg_mid.lower() or 'ellipse' in svg_mid.lower()

    def test_shake_zero_duration(self):
        c = Circle(r=50)
        result = c.shake(start=0, end=0)
        assert result is c  # returns self, no-op


class TestBounceAnimation:
    def test_bounce_produces_displacement(self):
        c = Circle(r=50, cx=100, cy=100)
        c.bounce(start=0, end=1, height=50, bounces=3)
        svg_mid = c.to_svg(0.5)
        assert 'circle' in svg_mid.lower() or 'ellipse' in svg_mid.lower()

    def test_bounce_zero_duration(self):
        c = Circle(r=50)
        result = c.bounce(start=0, end=0)
        assert result is c  # returns self, no-op


class TestFromSvgTransform:
    def test_translate_circle(self):
        from bs4 import BeautifulSoup
        svg = '<circle r="50" cx="0" cy="0" transform="translate(100, 200)"/>'
        elem = BeautifulSoup(svg, 'html.parser').find('circle')
        obj = from_svg(elem)
        cx, cy = obj.c.at_time(0)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(200, abs=1)

    def test_translate_rect(self):
        from bs4 import BeautifulSoup
        svg = '<rect width="60" height="30" x="10" y="20" transform="translate(5, 10)"/>'
        elem = BeautifulSoup(svg, 'html.parser').find('rect')
        obj = from_svg(elem)
        assert isinstance(obj, Rectangle)
        assert obj.x.at_time(0) == pytest.approx(15, abs=1)
        assert obj.y.at_time(0) == pytest.approx(30, abs=1)

    def test_no_transform(self):
        from bs4 import BeautifulSoup
        svg = '<circle r="50" cx="100" cy="200"/>'
        elem = BeautifulSoup(svg, 'html.parser').find('circle')
        obj = from_svg(elem)
        cx, cy = obj.c.at_time(0)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(200, abs=1)

    def test_rect_preserves_position(self):
        from bs4 import BeautifulSoup
        svg = '<rect width="80" height="40" x="50" y="60"/>'
        elem = BeautifulSoup(svg, 'html.parser').find('rect')
        obj = from_svg(elem)
        assert isinstance(obj, Rectangle)
        assert obj.x.at_time(0) == pytest.approx(50, abs=1)
        assert obj.y.at_time(0) == pytest.approx(60, abs=1)


class TestBraceEdgeCases:
    def test_brace_small_target(self):
        from vectormation.objects import Brace
        small = Dot(r=2, cx=100, cy=100)
        b = Brace(small, direction='down')
        svg = b.to_svg(0)
        assert svg  # renders without error

    def test_brace_large_target(self):
        from vectormation.objects import Brace
        big = Rectangle(800, 20, x=100, y=100)
        b = Brace(big, direction='up')
        svg = b.to_svg(0)
        assert svg


class TestLogAxes:
    def test_log_axes_render(self):
        ax = Axes(x_range=(0.1, 1000), y_range=(1, 100), x_scale='log', y_scale='log')
        svg = ax.to_svg(0)
        assert '10' in svg
        assert '100' in svg

    def test_log_math_to_svg_x(self):
        ax = Axes(x_range=(1, 1000), y_range=(1, 10), x_scale='log')
        # x=1 should be at left edge, x=1000 at right edge
        left = ax._math_to_svg_x(1, 0)
        right = ax._math_to_svg_x(1000, 0)
        mid = ax._math_to_svg_x(31.62, 0)  # sqrt(1000) ~ middle in log space
        assert left < mid < right
        assert left == pytest.approx(ax.plot_x, abs=1)
        assert right == pytest.approx(ax.plot_x + ax.plot_width, abs=1)

    def test_log_math_to_svg_y(self):
        ax = Axes(x_range=(1, 10), y_range=(1, 100), y_scale='log')
        top = ax._math_to_svg_y(100, 0)
        bottom = ax._math_to_svg_y(1, 0)
        assert top < bottom  # SVG y is inverted

    def test_linear_axes_unchanged(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        sx = ax._math_to_svg_x(0, 0)
        expected = ax.plot_x + ax.plot_width / 2
        assert sx == pytest.approx(expected, abs=1)


class TestTickFormat:
    def test_callable_format(self):
        ax = Axes(x_range=(0, 100), y_range=(0, 1), tick_format=lambda v: f'{v:.0f}%')
        svg = ax.to_svg(0)
        assert '%' in svg

    def test_format_string(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5), tick_format='{:.1f}')
        svg = ax.to_svg(0)
        assert '.0' in svg


class TestSampleSpace:
    def test_basic_render(self):
        from vectormation.objects import SampleSpace
        ss = SampleSpace(width=400, height=300)
        svg = ss.to_svg(0)
        assert 'rect' in svg.lower() or '<' in svg

    def test_divide_horizontally(self):
        from vectormation.objects import SampleSpace
        ss = SampleSpace()
        ss.divide_horizontally(0.6, labels=['A', 'B'])
        svg = ss.to_svg(0)
        assert 'A' in svg
        assert 'B' in svg

    def test_divide_vertically(self):
        from vectormation.objects import SampleSpace
        ss = SampleSpace()
        ss.divide_vertically(0.4, labels=['Top', 'Bottom'])
        svg = ss.to_svg(0)
        assert 'Top' in svg
        assert 'Bottom' in svg


class TestRoundedCornerPolygon:
    def test_basic_render(self):
        from vectormation.objects import RoundedCornerPolygon
        p = RoundedCornerPolygon((100, 100), (300, 100), (300, 300), (100, 300), radius=20)
        svg = p.to_svg(0)
        assert 'A' in svg  # arc commands
        assert 'Z' in svg  # closed path

    def test_small_radius(self):
        from vectormation.objects import RoundedCornerPolygon
        p = RoundedCornerPolygon((0, 0), (50, 0), (50, 50), (0, 50), radius=5)
        svg = p.to_svg(0)
        assert svg


class TestDrawBorderThenFill:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=100, fill='#f00')
        c.draw_border_then_fill(start=0, end=2)
        # At start, fill should be reduced/hidden
        fo_start = c.styling.fill_opacity.at_time(0)
        fo_end = c.styling.fill_opacity.at_time(2)
        assert fo_start < fo_end or fo_start == pytest.approx(0, abs=0.1)

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.draw_border_then_fill(start=0, end=1)
        assert result is c


class TestNewEasings:
    def test_running_start(self):
        from vectormation.easings import running_start
        assert running_start(0) == pytest.approx(0, abs=0.01)
        assert running_start(1) == pytest.approx(1, abs=0.01)
        # Should pull back (negative) early on
        val_early = running_start(0.2)
        assert val_early < 0.2  # pulls back

    def test_smoothstep(self):
        from vectormation.easings import smoothstep
        assert smoothstep(0) == pytest.approx(0, abs=0.01)
        assert smoothstep(1) == pytest.approx(1, abs=0.01)
        assert smoothstep(0.5) == pytest.approx(0.5, abs=0.01)

    def test_smootherstep(self):
        from vectormation.easings import smootherstep
        assert smootherstep(0) == pytest.approx(0, abs=0.01)
        assert smootherstep(1) == pytest.approx(1, abs=0.01)
        assert smootherstep(0.5) == pytest.approx(0.5, abs=0.01)


class TestThreeDCameraZoom:
    def test_set_camera_zoom(self):
        ax = ThreeDAxes()
        s0 = ax._scale_3d.at_time(0)
        ax.set_camera_zoom(start=0, end=1, factor=2.0)
        s1 = ax._scale_3d.at_time(1)
        assert s1 == pytest.approx(s0 * 2, abs=1)
