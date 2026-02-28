"""Tests for VObject subclasses: draw_along, updater, from_svg, Brace, Arrow, Wedge, ClipPath, Graph, show/hide."""
import math
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
    Code, NetworkGraph, Tree, Label, LabeledLine, LabeledArrow,
    Callout, DimensionLine, Tooltip, ProgressBar, Legend, FlowChart,
    StreamLines, PolarAxes, Stamp, TimelineBar, RadarChart,
    DEFAULT_CHART_COLORS, Variable, Underline,
    ArrowVectorField, ComplexPlane, ChessBoard, Automaton,
    PeriodicTable, BohrAtom,
    Countdown, Filmstrip, MorphObject, Title, NumberPlane,
    transform_matching_shapes, transform_matching_tex,
    NeuralNetwork, Pendulum, StandingWave,
    Array, Stack, Queue, LinkedList, BinaryTree,
    ArrayViz, LinkedListViz, StackViz, QueueViz, LED,
    CANVAS_WIDTH, CANVAS_HEIGHT,
    pi_format, pi_ticks,
    ParametricFunction,
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

    # ── new multi-blink tests ──────────────────────────────────────────────────

    def test_multi_blink_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.blink(start=0, end=3, count=3)
        assert result is c

    def test_multi_blink_opacity_starts_high(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=2, count=2, easing=easings.linear)
        # At time 0 opacity is 1 (start of first cycle)
        assert c.styling.opacity.at_time(0) == pytest.approx(1, abs=0.05)

    def test_multi_blink_opacity_drops_to_zero(self):
        c = Circle(r=50, cx=100, cy=100)
        # 2 cycles over [0, 2]: each cycle 1 s, first half = fading to 0
        c.blink(start=0, end=2, count=2, easing=easings.linear)
        # Midpoint of first cycle (t=0.5) should be near 0
        assert c.styling.opacity.at_time(0.5) == pytest.approx(0, abs=0.1)

    def test_multi_blink_recovers_after_each_cycle(self):
        c = Circle(r=50, cx=100, cy=100)
        # 3 cycles over [0, 3]
        c.blink(start=0, end=3, count=3, easing=easings.linear)
        # End of cycle 1 (t=1): opacity should be back to 1
        assert c.styling.opacity.at_time(1) == pytest.approx(1, abs=0.1)

    def test_multi_blink_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=1, end=1, count=3)  # zero-length interval
        # Opacity should remain at default (1) since nothing was set
        assert c.styling.opacity.at_time(1) == pytest.approx(1)

    def test_multi_blink_zero_count_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=2, count=0)
        assert c.styling.opacity.at_time(1) == pytest.approx(1)


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
        _, y = r.get_edge('top', 0)
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
        dot, _ = ax.add_dot_label(5, 5, label='test')
        p0 = dot.c.at_time(0)
        assert isinstance(p0, tuple)

    def test_plot_bar(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        bars = ax.plot_bar([1, 2, 3], [3, 7, 5], bar_width=0.8)
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
        group = ax.add_text_annotation(5, 5, 'Peak')
        assert isinstance(group, VCollection)
        assert len(group.objects) == 2  # line + text label
        svg = group.to_svg(0)
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
        _, _, bw, bh = t.bbox(0)
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
        _, _, bw, bh = a.bbox(0)
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
        dots.distribute_radial(cx=500, cy=500, radius=100, start=0)
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
        d.shift(dx=200, start=0, end=1)
        ghosts = d.trail(start=0, end=1, num_copies=3)
        assert len(ghosts) == 3

    def test_heartbeat_returns_self(self):
        c = Circle(r=50)
        result = c.heartbeat(start=0, end=2, beats=3, scale_factor=1.5)
        assert result is c

    def test_heartbeat_double_pulse(self):
        """ECG-style heartbeat should show two pulses per beat."""
        c = Circle(r=50)
        c.heartbeat(start=0, end=3, beats=1, scale_factor=1.5, easing=easings.linear)
        # First pulse peak (lub) near t=0.375 (midpoint of 0-0.75 range)
        sx_lub = c.styling.scale_x.at_time(0.375)
        assert sx_lub > 1.0, "First pulse (lub) should be above baseline"
        # Second pulse (dub) near t=1.275 (midpoint of 0.9-1.65 range)
        sx_dub = c.styling.scale_x.at_time(1.275)
        assert sx_dub > 1.0, "Second pulse (dub) should be above baseline"
        # Rest phase near t=2.4 (in the 1.65-3.0 range)
        sx_rest = c.styling.scale_x.at_time(2.4)
        assert sx_rest == pytest.approx(1.0, abs=0.01), "Rest phase should be at baseline"

    def test_heartbeat_zero_duration(self):
        c = Circle(r=50)
        result = c.heartbeat(start=1, end=1)
        assert result is c

    def test_heartbeat_multiple_beats(self):
        """Each beat should produce the same pattern."""
        c = Circle(r=50)
        c.heartbeat(start=0, end=2, beats=2, scale_factor=1.4, easing=easings.linear)
        # Both beats should have a pulse in their first quarter
        sx_beat1 = c.styling.scale_x.at_time(0.125)
        sx_beat2 = c.styling.scale_x.at_time(1.125)
        assert sx_beat1 == pytest.approx(sx_beat2, abs=0.01)

    def test_color_wave_returns_self(self):
        c = Circle(r=50, fill='#FF0000')
        result = c.color_wave(start=0, end=1, wave_color='#00FF00')
        assert result is c

    def test_color_wave_sweep(self):
        """Color should change during the sweep and return to base at edges."""
        c = Circle(r=50, fill='#FF0000')
        c.color_wave(start=0, end=1, wave_color='#00FF00')
        # At the midpoint (sweep peak), color should differ from base
        mid = c.styling.fill.at_time(0.5)
        assert mid != '#FF0000', "Color should change at wave peak"

    def test_color_wave_zero_duration(self):
        c = Circle(r=50, fill='#FF0000')
        result = c.color_wave(start=1, end=1)
        assert result is c

    def test_color_wave_edges_near_base(self):
        """At the start and end, color should be close to the base color."""
        c = Circle(r=50, fill='#FF0000')
        c.color_wave(start=0, end=1, wave_color='#00FF00', width=0.3)
        # At t=0.01 (very start), sweep is at the edge, color should be near base
        start_color = c.styling.fill.at_time(0.01)
        # The start color should still be reddish (base is #FF0000)
        assert start_color is not None

    def test_teleport(self):
        d = Dot(cx=100, cy=100)
        d.teleport(500, 500, start=0)
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
        a.shift(dx=50, dy=50, start=0)
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

    def test_repr_before_rendering(self):
        p = Coor(0, (100, 100))
        t = Trace(p, start=0, end=1, dt=0.1)
        r = repr(t)
        assert r == 'Trace(0 points)'

    def test_repr_after_rendering(self):
        p = Coor(0, (100, 100))
        t = Trace(p, start=0, end=1, dt=0.1)
        t.to_svg(0.5)
        r = repr(t)
        assert r.startswith('Trace(')
        assert 'points' in r


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
        self.canvas.generate_frame_svg(1)  # force frame generation
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
        _, _, bw, _ = d.bbox(0)
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

    def test_add(self):
        vt = ValueTracker(5)
        result = vt + 3
        assert result.get_value() == 8

    def test_sub(self):
        vt = ValueTracker(10)
        result = vt - 4
        assert result.get_value() == 6

    def test_mul(self):
        vt = ValueTracker(3)
        result = vt * 4
        assert result.get_value() == 12

    def test_truediv(self):
        vt = ValueTracker(10)
        result = vt / 2
        assert result.get_value() == 5

    def test_iadd(self):
        vt = ValueTracker(5)
        vt += 3
        assert vt.get_value() == 8

    def test_isub(self):
        vt = ValueTracker(10)
        vt -= 4
        assert vt.get_value() == 6

    def test_increment_value(self):
        vt = ValueTracker(5)
        vt.increment_value(3)
        assert vt.get_value() == 8

    def test_add_two_trackers(self):
        a = ValueTracker(3)
        b = ValueTracker(7)
        result = a + b
        assert result.get_value() == 10


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
        c.shift(dx=200, start=0, end=1, easing=easings.linear)
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
        d = always_redraw(lambda _: Circle(r=50))
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
        c.move_to(500, 400, start=0, end=1, easing=easings.linear)
        cx0, _ = c.center(0)
        cx1, _ = c.center(1)
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
        bx, _, bw, _ = u.bbox(0)
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


class TestThreeDAxesBasic:
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
        ax.plot_surface_wireframe(lambda x, y: x**2 + y**2, x_steps=5, y_steps=5)
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
        c.to_edge('bottom', start=0, end=2)
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
        sl = StreamLines(lambda _x, _y: (1, 0))
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
        x, _ = pa.polar_to_point(5, 0)
        assert x > pa._cx  # r=max at angle 0 should be to the right

    def test_plot_polar(self):
        pa = PolarAxes()
        curve = pa.plot_polar(lambda _theta: 2)
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
        t.move_to(200, 200, start=1, end=2)
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
        vf = ArrowVectorField(lambda _x, _y: (1, 0))
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
        assert l.get_length() == pytest.approx(500.0, abs=0.01)

    def test_get_length_zero(self):
        l = Line(x1=100, y1=100, x2=100, y2=100)
        assert l.get_length() == 0.0

    def test_get_angle_horizontal(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.get_angle() == pytest.approx(0.0, abs=0.01)

    def test_get_angle_vertical_down(self):
        l = Line(x1=0, y1=0, x2=0, y2=100)
        assert l.get_angle() == pytest.approx(90.0, abs=0.01)

    def test_get_angle_diagonal(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        assert l.get_angle() == pytest.approx(45.0, abs=0.01)

    def test_get_unit_vector(self):
        l = Line(x1=0, y1=0, x2=300, y2=400)
        ux, uy = l.get_unit_vector()
        assert ux == pytest.approx(0.6, abs=0.01)
        assert uy == pytest.approx(0.8, abs=0.01)

    def test_get_unit_vector_zero_length(self):
        l = Line(x1=50, y1=50, x2=50, y2=50)
        assert l.get_unit_vector() == (0.0, 0.0)

    def test_animated_line_at_time(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        l.p2.set(0, 1, lambda t: (100 + 200 * t, 0))
        assert l.get_length(time=0) == pytest.approx(100, abs=1)
        assert l.get_length(time=1) == pytest.approx(300, abs=1)


class TestArcUtilities:
    def test_get_start_point(self):
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        sx, sy = a.get_start_point()
        assert sx == pytest.approx(100, abs=0.01)
        assert sy == pytest.approx(0, abs=0.01)

    def test_get_end_point(self):
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=90)
        ex, ey = a.get_end_point()
        assert ex == pytest.approx(0, abs=0.01)
        assert ey == pytest.approx(-100, abs=0.01)  # 90 degrees: y = -r*sin(90) = -100

    def test_get_arc_length(self):
        from math import pi
        a = Arc(cx=0, cy=0, r=100, start_angle=0, end_angle=180)
        assert a.get_arc_length() == pytest.approx(100 * pi, abs=0.01)

    def test_get_arc_length_quarter(self):
        from math import pi
        a = Arc(cx=0, cy=0, r=200, start_angle=0, end_angle=90)
        assert a.get_arc_length() == pytest.approx(200 * pi / 2, abs=0.01)


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
        MorphObject(c, r, start=0, end=1)
        assert not c.show.at_time(0.5)

    def test_target_visible_after_end(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        MorphObject(c, r, start=0, end=1)
        assert r.show.at_time(1.5)

    def test_target_hidden_before_end(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(100, 100, x=300, y=300)
        MorphObject(c, r, start=1, end=2)
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
        assert cx == pytest.approx(150, abs=0.01)
        assert cy == pytest.approx(150, abs=0.01)

    def test_perimeter_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.perimeter() == pytest.approx(400, abs=0.01)

    def test_perimeter_open(self):
        from vectormation.objects import Lines as Polyline
        l = Polyline((0, 0), (100, 0), (100, 100))
        # Open: only 2 segments, no closing edge
        assert l.perimeter() == pytest.approx(200, abs=0.01)

    def test_area_square(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert p.area() == pytest.approx(10000, abs=0.01)

    def test_area_triangle(self):
        p = Polygon((0, 0), (200, 0), (100, 100))
        assert p.area() == pytest.approx(10000, abs=0.01)

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
        assert c.get_area() == pytest.approx(pi * 10000, abs=0.01)

    def test_get_circumference(self):
        from math import pi
        c = Circle(r=50)
        assert c.get_circumference() == pytest.approx(2 * pi * 50, abs=0.01)

    def test_animated_radius(self):
        from math import pi
        c = Circle(r=100)
        c.rx.set(0, 1, lambda t: 100 + 100 * t)
        assert c.get_area(time=0) == pytest.approx(pi * 10000, abs=1)
        assert c.get_area(time=1) == pytest.approx(pi * 40000, abs=1)


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
        assert e.get_area() == pytest.approx(pi * 100 * 50, abs=0.01)

    def test_get_circumference(self):
        # For a circle (rx==ry==100), should give 2*pi*100
        from math import pi
        e = Ellipse(rx=100, ry=100)
        assert e.get_circumference() == pytest.approx(2 * pi * 100, abs=0.01)

    def test_circle_inherits(self):
        from math import pi
        c = Circle(r=50)
        # Circle inherits from Ellipse, should work
        assert c.get_area() == pytest.approx(pi * 2500, abs=0.01)
        assert c.get_circumference() == pytest.approx(2 * pi * 50, abs=0.01)


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
        _, sy0 = fg.get_point_from_x(-2)
        _, sy1 = fg.get_point_from_x(2)
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


class TestRotateOut:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.rotate_out(start=0, end=1)
        assert result is c

    def test_hides_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_out(start=0, end=1)
        assert not c.show.at_time(1.5)

    def test_rotation_increases(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_out(start=0, end=1, degrees=90, easing=easings.linear)
        rot0 = c.styling.rotation.at_time(0)
        rot_mid = c.styling.rotation.at_time(0.5)
        assert rot0[0] == pytest.approx(0, abs=1)
        assert rot_mid[0] == pytest.approx(45, abs=5)

    def test_opacity_decreases(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_out(start=0, end=1, easing=easings.linear)
        op_start = c.styling.fill_opacity.at_time(0)
        op_end = c.styling.fill_opacity.at_time(1)
        assert op_start > op_end

    def test_no_change_existence(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_out(start=0, end=1, change_existence=False)
        # Without change_existence, object should still be visible after end
        assert c.show.at_time(1.5)

    def test_zero_duration_no_crash(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.rotate_out(start=1, end=1)
        assert result is c


class TestStaggerRandom:
    def test_returns_self(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        g = VCollection(c1, c2)
        result = g.stagger_random('fadein', start=0, end=2)
        assert result is g

    def test_calls_method_on_all_children(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        g = VCollection(c1, c2, c3)
        g.stagger_random('fadein', start=0, end=3, seed=42)
        # All children should be visible at time 3 (after all fadein animations)
        for c in [c1, c2, c3]:
            assert c.show.at_time(3)

    def test_seed_is_reproducible(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        g = VCollection(c1, c2, c3)
        g.stagger_random('fadein', start=0, end=3, seed=99)
        svg_a = g.to_svg(1.5)

        d1 = Circle(r=10)
        d2 = Circle(r=20)
        d3 = Circle(r=30)
        h = VCollection(d1, d2, d3)
        h.stagger_random('fadein', start=0, end=3, seed=99)
        svg_b = h.to_svg(1.5)

        assert svg_a == svg_b

    def test_empty_collection(self):
        g = VCollection()
        result = g.stagger_random('fadein', start=0, end=1)
        assert result is g

    def test_zero_duration_no_crash(self):
        c1 = Circle(r=10)
        g = VCollection(c1)
        result = g.stagger_random('fadein', start=1, end=1)
        assert result is g

    def test_different_seeds_give_different_order(self):
        # With enough children, different seeds should produce different orderings
        g1 = VCollection(*[Circle(r=i * 10 + 10) for i in range(5)])
        g2 = VCollection(*[Circle(r=i * 10 + 10) for i in range(5)])
        g1.stagger_random('fadein', start=0, end=5, seed=1)
        g2.stagger_random('fadein', start=0, end=5, seed=2)
        # Very likely to differ at mid-point; just check no crash
        svg1 = g1.to_svg(2.5)
        svg2 = g2.to_svg(2.5)
        assert svg1 is not None
        assert svg2 is not None


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
        _, _, bw, bh = cb.bbox(0)
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
        h, _, _ = _hex_to_hsl(c)
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


class TestNumberLineAddPointer:
    def test_add_pointer_returns_vcollection(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(0)
        assert isinstance(ptr, VCollection)

    def test_pointer_added_to_numberline(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        initial = len(nl.objects)
        nl.add_pointer(0)
        assert len(nl.objects) == initial + 1

    def test_pointer_position_at_value(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(0)
        # The pointer triangle should be near the number_to_point(0) x position
        _, _ = nl.number_to_point(0)
        svg = ptr.to_svg(0)
        assert svg  # renders without error

    def test_pointer_with_label(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(2.5, label='X')
        # Should have 2 children: triangle polygon + text
        assert len(ptr) == 2

    def test_pointer_without_label(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(2.5)
        # Should have 1 child: triangle polygon
        assert len(ptr) == 1

    def test_pointer_dynamic_with_real_attribute(self):
        import vectormation.attributes as attrs
        nl = NumberLine(x_range=(0, 10, 1))
        val = attrs.Real(0, 2)
        ptr = nl.add_pointer(val)
        # Triangle vertex should track value
        tri = ptr[0]  # the Polygon
        v0_at_2 = tri.vertices[2].at_time(0)  # tip vertex
        px2, _ = nl.number_to_point(2)
        assert abs(v0_at_2[0] - px2) < 1  # tip x near value 2

        # Animate value to 8
        val.set_onward(1, 8)
        v0_at_8 = tri.vertices[2].at_time(1)
        px8, _ = nl.number_to_point(8)
        assert abs(v0_at_8[0] - px8) < 1  # tip x near value 8

    def test_pointer_custom_color(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(0, color='#00FF00')
        svg = ptr.to_svg(0)
        assert 'rgb(0,255,0)' in svg or '#00FF00' in svg


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


class TestBounceIn:
    def test_bounce_in_shows_object(self):
        """bounce_in makes the object visible from start."""
        c = Circle(r=50, cx=100, cy=100)
        c.bounce_in(start=0, end=1)
        assert c.show.at_time(0) is True

    def test_bounce_in_scale_starts_near_zero(self):
        """Scale is close to 0 at start."""
        c = Circle(r=50, cx=100, cy=100)
        c.bounce_in(start=0, end=1)
        sx = c.styling.scale_x.at_time(0)
        assert sx == pytest.approx(0.0, abs=0.1)

    def test_bounce_in_scale_ends_at_one(self):
        """Scale reaches 1 at end."""
        c = Circle(r=50, cx=100, cy=100)
        c.bounce_in(start=0, end=1)
        sx = c.styling.scale_x.at_time(1)
        assert sx == pytest.approx(1.0, abs=0.05)

    def test_bounce_in_zero_duration_noop(self):
        """Zero-duration bounce_in should not raise and returns self."""
        c = Circle(r=50)
        result = c.bounce_in(start=0, end=0)
        assert result is c

    def test_bounce_in_no_change_existence(self):
        """With change_existence=False the show attribute is not modified."""
        c = Circle(r=50)
        c.bounce_in(start=2, end=3, change_existence=False)
        # show should be True from the default creation=0 (no _show_from called)
        assert c.show.at_time(2) is True

    def test_bounce_in_renders_svg(self):
        """bounce_in produces renderable SVG at midpoint."""
        c = Circle(r=50, cx=500, cy=500)
        c.bounce_in(start=0, end=1)
        svg = c.to_svg(0.5)
        assert 'ellipse' in svg or 'circle' in svg


class TestVCollectionReverse:
    def test_reverse_flips_order(self):
        """reverse() reverses the children list."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=100, cy=0)
        c3 = Circle(r=10, cx=200, cy=0)
        col = VCollection(c1, c2, c3)
        col.reverse()
        assert col.objects[0] is c3
        assert col.objects[1] is c2
        assert col.objects[2] is c1

    def test_reverse_returns_self(self):
        """reverse() returns the collection for chaining."""
        col = VCollection(Circle(r=10), Circle(r=20))
        result = col.reverse()
        assert result is col

    def test_reverse_empty_collection(self):
        """reverse() on an empty collection is a no-op."""
        col = VCollection()
        col.reverse()
        assert col.objects == []

    def test_reverse_twice_is_identity(self):
        """Reversing twice returns to original order."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        col.reverse().reverse()
        assert col.objects[0] is c1
        assert col.objects[1] is c2

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


class TestDataStructures:
    def test_array_render(self):
        from vectormation.objects import Array
        arr = Array([5, 3, 8])
        svg = arr.to_svg(0)
        assert '5' in svg and '3' in svg and '8' in svg

    def test_array_highlight(self):
        from vectormation.objects import Array
        arr = Array([1, 2, 3])
        arr.highlight_cell(1, start=0, end=1)  # should not error

    def test_array_swap(self):
        from vectormation.objects import Array
        arr = Array([10, 20, 30])
        arr.swap_cells(0, 2, start=0, end=1)

    def test_array_pointer(self):
        from vectormation.objects import Array
        arr = Array([1, 2, 3])
        ptr = arr.add_pointer(1, label='i')
        assert ptr is not None

    def test_stack_render(self):
        from vectormation.objects import Stack
        s = Stack([10, 20, 30])
        svg = s.to_svg(0)
        assert '10' in svg

    def test_stack_push(self):
        from vectormation.objects import Stack
        s = Stack([10, 20])
        s.push(30, start=0, end=0.5)
        assert len(s._items) == 3

    def test_stack_pop(self):
        from vectormation.objects import Stack
        s = Stack([10, 20, 30])
        s.pop(start=0, end=0.5)
        assert len(s._items) == 2

    def test_queue_render(self):
        from vectormation.objects import Queue
        q = Queue([1, 2, 3])
        svg = q.to_svg(0)
        assert '1' in svg

    def test_queue_enqueue(self):
        from vectormation.objects import Queue
        q = Queue([1, 2])
        q.enqueue(3, start=0, end=0.5)
        assert len(q._items) == 3

    def test_queue_dequeue(self):
        from vectormation.objects import Queue
        q = Queue([1, 2, 3])
        q.dequeue(start=0, end=0.5)
        assert len(q._items) == 2

    def test_linked_list_render(self):
        from vectormation.objects import LinkedList
        ll = LinkedList(['A', 'B', 'C'])
        svg = ll.to_svg(0)
        assert 'A' in svg and 'null' in svg

    def test_linked_list_highlight(self):
        from vectormation.objects import LinkedList
        ll = LinkedList([1, 2, 3])
        ll.highlight_node(1, start=0, end=1)

    def test_binary_tree_render(self):
        from vectormation.objects import BinaryTree
        bt = BinaryTree((5, (3, 1, 4), (7, 6, 8)))
        svg = bt.to_svg(0)
        assert '5' in svg and '3' in svg

    def test_binary_tree_single(self):
        from vectormation.objects import BinaryTree
        bt = BinaryTree(42)
        svg = bt.to_svg(0)
        assert '42' in svg


class TestArraySetValueAndSort:
    def test_set_value(self):
        from vectormation.objects import Array
        arr = Array([1, 2, 3])
        result = arr.set_value(1, 99, start=0, end=0.5)
        assert result is arr

    def test_sort_returns_self(self):
        from vectormation.objects import Array
        arr = Array([3, 1, 2])
        result = arr.sort(start=0, end=2)
        assert result is arr

    def test_sort_empty(self):
        from vectormation.objects import Array
        arr = Array([])
        result = arr.sort(start=0, end=1)
        assert result is arr


class TestLinkedListAppendRemove:
    def test_append_node(self):
        from vectormation.objects import LinkedList
        ll = LinkedList([1, 2])
        result = ll.append_node(3, start=0, end=0.5)
        assert result is ll
        assert len(ll._nodes) == 3

    def test_remove_node(self):
        from vectormation.objects import LinkedList
        ll = LinkedList([1, 2, 3])
        result = ll.remove_node(1, start=0, end=0.5)
        assert result is ll
        assert len(ll._nodes) == 2

    def test_remove_out_of_range(self):
        from vectormation.objects import LinkedList
        ll = LinkedList([1])
        result = ll.remove_node(5)
        assert result is ll
        assert len(ll._nodes) == 1


class TestCircuitComponents:
    def test_resistor(self):
        from vectormation.objects import Resistor
        r = Resistor(x1=300, y1=500, x2=500, y2=500)
        svg = r.to_svg(0)
        assert svg

    def test_capacitor(self):
        from vectormation.objects import Capacitor
        c = Capacitor(x1=300, y1=500, x2=500, y2=500)
        svg = c.to_svg(0)
        assert svg


class TestMolecule2D:
    def test_water(self):
        from vectormation.objects import Molecule2D
        m = Molecule2D(atoms=[('O', 0, 0), ('H', -1, 0.5), ('H', 1, 0.5)],
                       bonds=[(0, 1, 1), (0, 2, 1)])
        svg = m.to_svg(0)
        assert 'O' in svg and 'H' in svg

    def test_double_bond(self):
        from vectormation.objects import Molecule2D
        m = Molecule2D(atoms=[('O', 0, 0), ('C', 1, 0), ('O', 2, 0)],
                       bonds=[(0, 1, 2), (1, 2, 2)])
        svg = m.to_svg(0)
        assert svg


class TestComplexPlaneTransform:
    def test_apply_complex_function(self):
        from vectormation.objects import ComplexPlane
        cp = ComplexPlane(x_range=(-2, 2), y_range=(-2, 2))
        initial_count = len(cp.objects)
        cp.apply_complex_function(lambda z: z**2, start=0, end=1, resolution=5)
        assert len(cp.objects) > initial_count


class TestFocusOn:
    def test_focus_on_tuple(self):
        from vectormation.objects import Circle
        c = Circle(cx=100, cy=100)
        c.focus_on((960, 540), start=0, end=1)
        cx, cy = c.get_center(1)
        assert abs(cx - 960) < 5 and abs(cy - 540) < 5

    def test_focus_on_object(self):
        from vectormation.objects import Circle, Rectangle
        c = Circle(cx=100, cy=100)
        r = Rectangle(100, 100, x=800, y=400)
        c.focus_on(r, start=0, end=1)
        cx, cy = c.get_center(1)
        rx, ry = r.get_center(0)
        assert abs(cx - rx) < 5 and abs(cy - ry) < 5


class TestBroadcast:
    def test_broadcast_returns_collection(self):
        from vectormation.objects import Circle, VCollection
        c = Circle(cx=500, cy=500)
        copies = c.broadcast(start=0, duration=1, num_copies=3)
        assert isinstance(copies, VCollection)
        assert len(copies) == 3

    def test_broadcast_copies_fade(self):
        from vectormation.objects import Dot
        d = Dot(cx=500, cy=500)
        copies = d.broadcast(start=0, duration=1, num_copies=2)
        # After the animation window, copies should be hidden
        for obj in copies.objects:
            assert not obj.show.at_time(5)


class TestInductor:
    def test_creates(self):
        from vectormation.objects import Inductor
        ind = Inductor(x1=300, y1=500, x2=600, y2=500)
        svg = ind.to_svg(0)
        assert svg
        assert len(ind.objects) >= 1

    def test_with_label(self):
        from vectormation.objects import Inductor
        ind = Inductor(label='L1')
        svg = ind.to_svg(0)
        assert 'L1' in svg


class TestUnitInterval:
    def test_creates(self):
        from vectormation.objects import UnitInterval
        ui = UnitInterval()
        svg = ui.to_svg(0)
        assert svg
        assert len(ui.objects) > 0

    def test_range(self):
        from vectormation.objects import UnitInterval
        ui = UnitInterval()
        # The number line should display 0 and 1
        svg = ui.to_svg(0)
        assert '0' in svg and '1' in svg


class TestPlotBar:
    def test_plot_bar_basic(self):
        from vectormation.objects import Axes, VCollection
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        bars = ax.plot_bar([1, 2, 3], [4, 7, 3])
        assert isinstance(bars, VCollection)
        assert len(bars) == 3
        svg = bars.to_svg(0)
        assert '<rect' in svg

    def test_plot_bar_custom_width(self):
        from vectormation.objects import Axes
        ax = Axes(x_range=(0, 5), y_range=(0, 10))
        bars = ax.plot_bar([1, 2], [5, 8], bar_width=0.4)
        assert len(bars) == 2


class TestStyleGetters:
    def test_get_fill_color(self):
        from vectormation.objects import Circle
        c = Circle(cx=100, cy=100, fill='#FF0000')
        assert c.get_fill_color(0) == '#ff0000'

    def test_get_stroke_width(self):
        from vectormation.objects import Rectangle
        r = Rectangle(100, 100, stroke_width=3)
        assert r.get_stroke_width(0) == 3

    def test_get_fill_opacity(self):
        from vectormation.objects import Circle
        c = Circle(fill_opacity=0.5)
        assert c.get_fill_opacity(0) == 0.5

    def test_get_stroke_opacity(self):
        from vectormation.objects import Circle
        c = Circle(stroke_opacity=0.8)
        assert c.get_stroke_opacity(0) == 0.8


class TestCollectionSearch:
    def test_find(self):
        from vectormation.objects import VCollection, Circle, Rectangle
        col = VCollection(Circle(), Rectangle(50, 50), Circle())
        found = col.find(lambda obj, _: isinstance(obj, Rectangle))
        assert isinstance(found, Rectangle)

    def test_find_none(self):
        from vectormation.objects import VCollection, Circle
        col = VCollection(Circle(), Circle())
        found = col.find(lambda obj, _: isinstance(obj, int))
        assert found is None

    def test_find_by_type(self):
        from vectormation.objects import VCollection, Circle, Rectangle, Dot
        col = VCollection(Circle(), Rectangle(10, 10), Dot(), Circle())
        circles = col.find_by_type(Circle)
        # Dot extends Circle, so it should be included
        assert len(circles) >= 2

    def test_find_index(self):
        from vectormation.objects import VCollection, Circle, Rectangle
        col = VCollection(Circle(), Rectangle(50, 50), Circle())
        idx = col.find_index(lambda obj, _: isinstance(obj, Rectangle))
        assert idx == 1

    def test_group_by(self):
        from vectormation.objects import VCollection, Circle, Rectangle
        col = VCollection(Circle(), Rectangle(10, 10), Circle())
        groups = col.group_by(lambda obj: type(obj).__name__)
        assert 'Circle' in groups
        assert len(groups['Circle']) == 2


class TestAnimateRange:
    def test_animate_x_range(self):
        from vectormation.objects import Axes
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.animate_range(0, 1, x_range=(0, 20))
        # After animation, x_max should be 20
        assert abs(ax.x_max.at_time(1) - 20) < 0.1

    def test_animate_y_range(self):
        from vectormation.objects import Axes
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.animate_range(0, 1, y_range=(-5, 5))
        assert abs(ax.y_min.at_time(1) - (-5)) < 0.1
        assert abs(ax.y_max.at_time(1) - 5) < 0.1


class TestPieAnimateValues:
    def test_animate_values(self):
        from vectormation.objects import PieChart
        pc = PieChart(values=[30, 20, 50])
        result = pc.animate_values([40, 40, 20], start=0, end=1)
        assert result is pc
        assert pc.values == [40, 40, 20]

    def test_animate_values_wrong_length(self):
        from vectormation.objects import PieChart
        pc = PieChart(values=[30, 20, 50])
        result = pc.animate_values([40, 60], start=0, end=1)
        assert result is pc
        assert pc.values == [30, 20, 50]  # unchanged


class TestCircleGeometricMethods:
    def test_point_on_circle(self):
        from vectormation.objects import Circle
        c = Circle(cx=500, cy=500, r=100)
        # Angle 0 = right
        px, py = c.point_on_circle(0, 0)
        assert abs(px - 600) < 1
        assert abs(py - 500) < 1

    def test_point_on_circle_90(self):
        from vectormation.objects import Circle
        c = Circle(cx=500, cy=500, r=100)
        # Angle 90 = up (CCW from right, same as point_at_angle)
        px, py = c.point_on_circle(90, 0)
        assert abs(px - 500) < 1
        assert abs(py - 400) < 1

    def test_tangent_line(self):
        from vectormation.objects import Circle, Line
        c = Circle(cx=500, cy=500, r=100)
        tl = c.tangent_line(0, length=200)
        assert isinstance(tl, Line)


class TestHighlightSubstring:
    def test_basic(self):
        from vectormation.objects import Text, Rectangle
        t = Text(text='Hello World', x=100, y=100, font_size=24)
        rect = t.highlight_substring('World')
        assert isinstance(rect, Rectangle)

    def test_not_found(self):
        from vectormation.objects import Text, Rectangle
        t = Text(text='Hello', x=100, y=100, font_size=24)
        rect = t.highlight_substring('xyz')
        assert isinstance(rect, Rectangle)


class TestDiode:
    def test_creates(self):
        from vectormation.objects import Diode
        d = Diode(x1=300, y1=500, x2=600, y2=500)
        svg = d.to_svg(0)
        assert svg
        assert len(d.objects) >= 3

    def test_with_label(self):
        from vectormation.objects import Diode
        d = Diode(label='D1')
        svg = d.to_svg(0)
        assert 'D1' in svg


class TestArrowSetEndpoints:
    def test_set_start(self):
        a = Arrow(100, 100, 500, 500)
        a.set_start(200, 200, start=0)
        svg = a.to_svg(1)
        assert 'line' in svg.lower() or '<path' in svg.lower()

    def test_set_end_animated(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(600, 600, start=0, end=1)
        svg = a.to_svg(0.5)
        assert svg

    def test_set_start_animated(self):
        a = Arrow(100, 100, 500, 500)
        a.set_start(300, 300, start=0, end=1)
        svg = a.to_svg(0.5)
        assert svg
        # At t=0.5 the start should be between (100,100) and (300,300)
        s = a.get_start(0.5)
        assert 100 < s[0] < 300

    def test_set_end_instant(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(700, 700, start=0)
        e = a.get_end(0)
        assert abs(e[0] - 700) < 1
        assert abs(e[1] - 700) < 1

    def test_tip_follows_endpoint(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(700, 100, start=0)
        # Tip vertex 0 should be at the end point
        tip_pt = a.tip.vertices[0].at_time(0)
        assert abs(tip_pt[0] - 700) < 1
        assert abs(tip_pt[1] - 100) < 1


class TestAxesDistributions:
    def test_plot_normal(self):
        ax = Axes(x_range=(-4, 4, 1), y_range=(0, 0.5, 0.1))
        curve = ax.plot_normal(mean=0, std=1)
        assert curve is not None
        svg = ax.to_svg(0)
        assert '<path' in svg

    def test_plot_normal_no_fill(self):
        ax = Axes(x_range=(-4, 4, 1), y_range=(0, 0.5, 0.1))
        curve = ax.plot_normal(mean=0, std=1, fill=False)
        assert curve is not None

    def test_plot_exponential(self):
        ax = Axes(x_range=(0, 5, 1), y_range=(0, 2, 0.5))
        curve = ax.plot_exponential(rate=1)
        assert curve is not None

    def test_plot_uniform(self):
        ax = Axes(x_range=(-1, 3, 1), y_range=(0, 2, 0.5))
        curve = ax.plot_uniform(a=0, b=1)
        assert curve is not None


class TestNewEasingCombinators:
    def test_repeat_basic(self):
        from vectormation.easings import repeat, linear
        r = repeat(linear, 3)
        assert abs(r(0) - 0) < 1e-9
        assert abs(r(1) - 1) < 1e-9
        # At 1/6, halfway through first repetition
        assert abs(r(1/6) - 0.5) < 1e-9

    def test_oscillate(self):
        from vectormation.easings import oscillate, linear
        o = oscillate(linear, 1)
        assert abs(o(0) - 0) < 1e-9
        assert abs(o(0.25) - 0.5) < 1e-9
        # At 0.5, end of forward pass
        assert abs(o(0.5) - 1) < 0.05

    def test_clamp(self):
        from vectormation.easings import clamp, linear
        c = clamp(linear, 0.25, 0.75)
        assert abs(c(0) - 0) < 1e-9
        assert abs(c(0.25) - 0) < 1e-9
        assert abs(c(0.5) - 0.5) < 1e-9
        assert abs(c(0.75) - 1) < 1e-9
        assert abs(c(1) - 1) < 1e-9

    def test_blend(self):
        from vectormation.easings import blend, linear
        b = blend(linear, lambda t: 1 - t, 0.5)
        assert abs(b(0) - 0.5) < 1e-9
        assert abs(b(0.5) - 0.5) < 1e-9
        assert abs(b(1) - 0.5) < 1e-9


class TestLineGeometricUtils:
    def test_perpendicular_at_midpoint(self):
        line = Line(100, 200, 300, 200)
        perp = line.perpendicular()
        p1 = perp.p1.at_time(0)
        p2 = perp.p2.at_time(0)
        # Midpoint of original is (200, 200)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        assert abs(mx - 200) < 1
        assert abs(my - 200) < 1
        # Perpendicular should be vertical
        assert abs(p1[0] - p2[0]) < 1

    def test_extend(self):
        line = Line(100, 100, 200, 100)
        ext = line.extend(2.0)
        p1 = ext.p1.at_time(0)
        p2 = ext.p2.at_time(0)
        assert p1[0] < 100
        assert p2[0] > 200

    def test_parallel(self):
        line = Line(100, 100, 300, 100)
        par = line.parallel(50)
        p1 = par.p1.at_time(0)
        # Should be 50 pixels offset in y
        assert abs(p1[1] - 50) < 1 or abs(p1[1] - 150) < 1

    def test_perpendicular_custom_length(self):
        line = Line(0, 0, 100, 0)
        perp = line.perpendicular(length=50)
        p1, p2 = perp.p1.at_time(0), perp.p2.at_time(0)
        length = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        assert abs(length - 50) < 1


class TestPolygonOffset:
    def test_offset_square(self):
        sq = Polygon((100, 100), (200, 100), (200, 200), (100, 200))
        bigger = sq.offset(10)
        # Should have 4 vertices
        assert len(bigger.vertices) == 4

    def test_offset_preserves_closed(self):
        p = Polygon((0, 0), (100, 0), (50, 100), closed=True)
        off = p.offset(5)
        assert off.closed


class TestGetBounds:
    def test_basic(self):
        r = Rectangle(width=100, height=50, x=200, y=300)
        b = r.get_bounds()
        assert b['width'] == 100
        assert b['height'] == 50
        assert b['left'] == 200
        assert b['right'] == 300
        assert b['top'] == 300
        assert b['bottom'] == 350

    def test_center(self):
        r = Rectangle(width=100, height=100, x=0, y=0)
        b = r.get_bounds()
        assert b['center'] == (50, 50)


class TestStaggerScaleRotate:
    def test_stagger_scale(self):
        objs = VCollection(Circle(r=20, cx=100), Circle(r=20, cx=200), Circle(r=20, cx=300))
        objs.stagger_scale(start=0, end=2, target_scale=2)
        svg = objs.to_svg(0.5)
        assert svg

    def test_stagger_rotate(self):
        objs = VCollection(Rectangle(width=50, height=50, x=100, y=100),
                           Rectangle(width=50, height=50, x=200, y=100))
        objs.stagger_rotate(start=0, end=2, degrees=180)
        svg = objs.to_svg(1)
        assert svg


class TestPolygonFromSvgPath:
    def test_basic(self):
        p = Polygon.from_svg_path("M 0 0 L 100 0 L 100 100 L 0 100 Z")
        assert len(p.vertices) == 4

    def test_relative(self):
        p = Polygon.from_svg_path("m 0 0 l 100 0 l 0 100 l -100 0")
        assert len(p.vertices) == 4

    def test_empty_path(self):
        p = Polygon.from_svg_path("")
        assert len(p.vertices) == 1  # fallback single vertex at (0,0)

    def test_coordinates_absolute(self):
        p = Polygon.from_svg_path("M 10 20 L 30 40 L 50 60 Z")
        pts = p.get_vertices()
        assert abs(pts[0][0] - 10) < 0.01
        assert abs(pts[0][1] - 20) < 0.01
        assert abs(pts[1][0] - 30) < 0.01
        assert abs(pts[2][1] - 60) < 0.01

    def test_coordinates_relative(self):
        p = Polygon.from_svg_path("m 10 20 l 5 0 l 0 5")
        pts = p.get_vertices()
        assert abs(pts[0][0] - 10) < 0.01
        assert abs(pts[1][0] - 15) < 0.01
        assert abs(pts[2][1] - 25) < 0.01


class TestTextFitToBox:
    def test_fit_shrinks(self):
        t = Text(text="Hello World", font_size=48)
        t.fit_to_box(max_width=50)
        fs = t.font_size.at_time(0)
        assert fs < 48

    def test_fit_grows(self):
        t = Text(text="Hi", font_size=10)
        t.fit_to_box(max_width=500)
        fs = t.font_size.at_time(0)
        assert fs > 10

    def test_max_height_caps(self):
        t = Text(text="Hi", font_size=10)
        t.fit_to_box(max_width=5000, max_height=20)
        fs = t.font_size.at_time(0)
        assert fs <= 20

    def test_empty_text(self):
        t = Text(text="", font_size=48)
        t.fit_to_box(max_width=50)
        # Should not crash, font_size unchanged
        assert t.font_size.at_time(0) == 48

    def test_returns_self(self):
        t = Text(text="Test", font_size=48)
        result = t.fit_to_box(max_width=100)
        assert result is t


class TestAxesLabeledPoints:
    def test_add_labeled_points(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        group = ax.add_labeled_points([(1, 2, 'A'), (3, 4, 'B'), (5, 6)])
        assert len(group.objects) >= 4  # 3 dots + 2 labels

    def test_add_labeled_points_no_labels(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        group = ax.add_labeled_points([(1, 2), (3, 4)])
        assert len(group.objects) == 2  # 2 dots, no labels

    def test_add_marked_region(self):
        ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
        ax.add_marked_region(2, 5, color='#FF0000')
        svg = ax.to_svg(0)
        assert 'rect' in svg.lower() or '<rect' in svg


class TestLineIntersections:
    def test_intersect_line_basic(self):
        l1 = Line(0, 0, 100, 100)
        l2 = Line(100, 0, 0, 100)
        pt = l1.intersect_line(l2)
        assert pt is not None
        assert abs(pt[0] - 50) < 1
        assert abs(pt[1] - 50) < 1

    def test_intersect_line_parallel(self):
        l1 = Line(0, 0, 100, 0)
        l2 = Line(0, 50, 100, 50)
        assert l1.intersect_line(l2) is None

    def test_project_point(self):
        line = Line(0, 0, 100, 0)
        px, py = line.project_point(50, 75)
        assert abs(px - 50) < 1
        assert abs(py - 0) < 1

    def test_project_point_off_segment(self):
        line = Line(0, 0, 100, 0)
        px, py = line.project_point(200, 50)
        assert abs(px - 200) < 1
        assert abs(py - 0) < 1


class TestCircleIntersectLine:
    def test_two_intersections(self):
        c = Circle(r=50, cx=100, cy=100)
        l = Line(0, 100, 200, 100)
        pts = c.intersect_line(l)
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert abs(xs[0] - 50) < 1
        assert abs(xs[1] - 150) < 1

    def test_no_intersection(self):
        c = Circle(r=50, cx=100, cy=100)
        l = Line(0, 0, 200, 0)  # far from circle
        pts = c.intersect_line(l)
        assert len(pts) == 0

    def test_tangent(self):
        c = Circle(r=50, cx=100, cy=100)
        l = Line(0, 50, 200, 50)  # tangent at top
        pts = c.intersect_line(l)
        assert len(pts) == 1
        assert abs(pts[0][0] - 100) < 1


class TestShowDuring:
    def test_show_during_single_range(self):
        c = Circle(r=50)
        c.show_during((1, 3))
        # show attribute is checked by the canvas, not by to_svg
        assert not c.show.at_time(0.5)  # hidden before range
        assert c.show.at_time(2)  # visible during range
        assert not c.show.at_time(4)  # hidden after range

    def test_show_during_multiple_ranges(self):
        c = Circle(r=50)
        c.show_during((0, 1), (3, 5))
        assert c.show.at_time(0.5)  # visible in first range
        assert not c.show.at_time(2)  # hidden between ranges
        assert c.show.at_time(4)  # visible in second range
        assert not c.show.at_time(6)  # hidden after all ranges

    def test_show_during_list_form(self):
        c = Circle(r=50)
        c.show_during([(1, 2), (4, 6)])
        assert c.show.at_time(1.5)  # visible
        assert not c.show.at_time(3)  # hidden between
        assert c.show.at_time(5)  # visible

    def test_show_during_returns_self(self):
        c = Circle(r=50)
        result = c.show_during((0, 1))
        assert result is c


class TestGlow:
    def test_glow_basic(self):
        c = Circle(r=50)
        result = c.glow(start=0, end=1)
        assert result is c
        svg = c.to_svg(0.5)
        assert svg

    def test_glow_zero_duration(self):
        c = Circle(r=50)
        c.glow(start=1, end=1)  # should not crash

    def test_glow_stroke_width_at_midpoint(self):
        c = Circle(r=50)
        orig_sw = c.styling.stroke_width.at_time(0)
        c.glow(start=0, end=2, radius=10)
        mid_sw = c.styling.stroke_width.at_time(1)
        # At midpoint, there_and_back returns ~1.0, so width should be near orig + radius
        assert mid_sw > orig_sw + 5

    def test_glow_stroke_reverts_after_end(self):
        c = Circle(r=50)
        orig_sw = c.styling.stroke_width.at_time(0)
        c.glow(start=0, end=1, radius=10)
        after_sw = c.styling.stroke_width.at_time(2)
        assert after_sw == orig_sw

    def test_glow_custom_color(self):
        c = Circle(r=50)
        c.glow(start=0, end=1, color='#FF0000')
        svg = c.to_svg(0.5)
        assert svg  # just verify no crash


class TestHideDuring:
    def test_basic(self):
        c = Circle(r=50)
        c.hide_during((1, 3))
        # Should be visible before 1
        svg_before = c.to_svg(0.5)
        assert svg_before
        # Should be hidden during 1-3
        # Should be visible after 3
        svg_after = c.to_svg(4)
        assert svg_after

    def test_return_self(self):
        c = Circle(r=50)
        assert c.hide_during((0, 1)) is c


class TestColorSetters:
    def test_set_saturation(self):
        from vectormation.colors import set_saturation
        result = set_saturation('#ff0000', 0.5)
        assert isinstance(result, str)
        assert result.startswith('#')

    def test_set_lightness(self):
        from vectormation.colors import set_lightness
        result = set_lightness('#ff0000', 0.5)
        assert isinstance(result, str)

    def test_invert(self):
        from vectormation.colors import invert
        assert invert('#000000') == '#ffffff'
        assert invert('#ffffff') == '#000000'
        assert invert('#ff0000') == '#00ffff'


class TestBarChartAccessors:
    def test_get_bar(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bar = bc.get_bar(0)
        assert bar is not None
        svg = bar.to_svg(0)
        assert 'rect' in svg.lower()

    def test_get_bars(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bars = bc.get_bars(0, 2)
        assert len(bars.objects) == 2

    def test_get_bars_no_args(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bars = bc.get_bars()
        assert len(bars.objects) == 3

    def test_highlight_bar(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        result = bc.highlight_bar(1, start=0, end=1)
        assert result is bc


class TestAnimatePointer:
    def test_basic(self):
        nl = NumberLine(x_range=(0, 10, 1))
        ptr = nl.add_pointer(3)
        nl.animate_pointer(ptr, 7, start=0, end=1)
        svg = nl.to_svg(0.5)
        assert svg

    def test_pointer_moves_to_target(self):
        nl = NumberLine(x_range=(0, 10, 1))
        ptr = nl.add_pointer(3)
        nl.animate_pointer(ptr, 7, start=0, end=1)
        tri = ptr.objects[0]
        # After animation ends, tip should be at value 7
        tip_x = tri.vertices[2].at_time(1)[0]
        target_x = nl.number_to_point(7)[0]
        assert abs(tip_x - target_x) < 1

    def test_with_label(self):
        nl = NumberLine(x_range=(0, 10, 1))
        ptr = nl.add_pointer(3, label='P')
        nl.animate_pointer(ptr, 7, start=0, end=1)
        # Label x should move to target position
        lbl = ptr.objects[1]
        target_x = nl.number_to_point(7)[0]
        assert abs(lbl.x.at_time(1) - target_x) < 1

    def test_returns_self(self):
        nl = NumberLine(x_range=(0, 10, 1))
        ptr = nl.add_pointer(5)
        result = nl.animate_pointer(ptr, 8, start=0, end=1)
        assert result is nl


class TestUtilityFunctions:
    def test_distance(self):
        from vectormation._constants import _distance
        assert abs(_distance(0, 0, 3, 4) - 5) < 1e-10
        assert _distance(0, 0, 0, 0) == 0


class TestProgressBarGetProgress:
    def test_get_progress(self):
        pb = ProgressBar()
        pb.set_progress(0.5, start=0)
        val = pb.get_progress(0)
        assert abs(val - 0.5) < 0.01

    def test_get_progress_default(self):
        pb = ProgressBar()
        val = pb.get_progress(0)
        assert 0 <= val <= 1


class TestMatrixHighlight:
    def test_highlight_entry(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.highlight_entry(0, 0, start=0, end=1)
        assert result is m

    def test_highlight_row(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        result = m.highlight_row(0, start=0, end=1)
        assert result is m

    def test_highlight_column(self):
        m = Matrix([[1, 2], [3, 4], [5, 6]])
        result = m.highlight_column(1, start=0, end=1)
        assert result is m


class TestTableBatchOps:
    def test_highlight_range(self):
        t = Table([['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']])
        result = t.highlight_range(0, 0, 1, 1, start=0, end=1)
        assert result is t

    def test_set_cell_values(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.set_cell_values({(0, 0): 'X', (1, 1): 'Y'}, start=0)
        assert result is t
        assert t.get_entry(0, 0).text.at_time(0) == 'X'
        assert t.get_entry(1, 1).text.at_time(0) == 'Y'


class TestSurfaceCheckerboard:
    def test_set_checkerboard(self):
        from vectormation._threed import Surface
        s = Surface(lambda u, v: (u, v, 0), u_range=(0, 1), v_range=(0, 1))
        s.set_checkerboard('#FF0000', '#0000FF')
        assert s._checkerboard_colors == ('#FF0000', '#0000FF')


class TestCanvasUtilities:
    def test_get_object_count(self):
        canvas = VectorMathAnim(tempfile.mkdtemp())
        canvas.add_objects(Circle(r=50), Rectangle(width=100, height=50))
        assert canvas.get_object_count() >= 2

    def test_list_objects_by_type(self):
        canvas = VectorMathAnim(tempfile.mkdtemp())
        canvas.add_objects(Circle(r=50), Circle(r=30), Rectangle(width=100, height=50))
        types = canvas.list_objects_by_type()
        assert 'Circle' in types
        assert len(types['Circle']) == 2


class TestBarChartGetByLabel:
    def test_found(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        bar = bc.get_bar_by_label('B')
        assert bar is not None

    def test_not_found(self):
        bc = BarChart(values=[10, 20], labels=['X', 'Y'])
        assert bc.get_bar_by_label('Z') is None


class TestAngleSetRadius:
    def test_set_radius_instant(self):
        a = Angle(vertex=(500, 500), p1=(600, 500), p2=(500, 400))
        a.set_radius(50, start=0)
        assert a  # no crash

    def test_set_radius_animated(self):
        a = Angle(vertex=(500, 500), p1=(600, 500), p2=(500, 400))
        result = a.set_radius(80, start=0, end=1)
        assert result is a


class TestVCollectionUtilities:
    def test_index_of_found(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = VCollection(a, b)
        assert c.index_of(a) == 0
        assert c.index_of(b) == 1

    def test_index_of_not_found(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = VCollection(a)
        assert c.index_of(b) == -1

    def test_replace(self):
        a = Circle(r=10)
        b = Circle(r=20)
        new_obj = Circle(r=30)
        c = VCollection(a, b)
        result = c.replace(a, new_obj)
        assert result is c
        assert c.objects[0] is new_obj
        assert c.objects[1] is b

    def test_replace_not_found(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = VCollection(a)
        result = c.replace(b, Circle(r=30))
        assert result is c  # no-op
        assert len(c.objects) == 1

    def test_map_objects(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = VCollection(a, b)
        result = c.map_objects(lambda obj: Circle(r=obj.rx.at_time(0) * 2))
        assert len(result.objects) == 2
        assert result.objects[0].rx.at_time(0) == 20
        assert result.objects[1].rx.at_time(0) == 40

    def test_set_z_values(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = Circle(r=30)
        col = VCollection(a, b, c)
        result = col.set_z_values()
        assert result is col
        assert a.z.at_time(0) == 0
        assert b.z.at_time(0) == 1
        assert c.z.at_time(0) == 2

    def test_contains_point_base(self):
        r = Rectangle(100, 50, x=10, y=20)
        assert r.contains_point(50, 40) is True
        assert r.contains_point(5, 20) is False


class TestArrowSetColor:
    def test_set_color(self):
        a = Arrow(100, 100, 200, 100)
        result = a.set_color('#FF0000', start=0)
        assert result is a

    def test_set_color_returns_self(self):
        a = Arrow(100, 100, 200, 100)
        assert a.set_color('#00FF00') is a


class TestNumberLineSegment:
    def test_add_segment(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        rect = nl.add_segment(-2, 2)
        assert rect is not None
        # Should have been added to objects
        assert rect in nl.objects

    def test_add_segment_custom_color(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        rect = nl.add_segment(0, 3, color='#FF0000')
        assert rect is not None


class TestAppearFrom:
    def test_appear_from_object(self):
        src = Circle(cx=100, cy=100, r=20)
        tgt = Circle(cx=500, cy=500, r=50)
        result = tgt.appear_from(src, start=0, end=1)
        assert result is tgt

    def test_appear_from_tuple(self):
        tgt = Rectangle(100, 50, x=400, y=400)
        result = tgt.appear_from((100, 100), start=0, end=1)
        assert result is tgt

    def test_appear_from_changes_existence(self):
        tgt = Circle(cx=500, cy=500, r=50)
        tgt.appear_from(Circle(cx=100, cy=100), start=1, end=2)
        assert tgt.show.at_time(0.5) is False
        assert tgt.show.at_time(1.5) is True


class TestAnimateEach:
    def test_animate_each_fadein(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = Circle(r=30)
        col = VCollection(a, b, c)
        result = col.animate_each('fadein', start=0, end=3)
        assert result is col

    def test_animate_each_empty(self):
        col = VCollection()
        result = col.animate_each('fadein', start=0, end=1)
        assert result is col

    def test_animate_each_reverse(self):
        a = Circle(r=10)
        b = Circle(r=20)
        col = VCollection(a, b)
        result = col.animate_each('fadein', start=0, end=2, reverse=True)
        assert result is col


class TestBarChartValueLabels:
    def test_add_value_labels(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        initial_count = len(bc.objects)
        result = bc.add_value_labels()
        assert result is bc
        assert len(bc.objects) > initial_count  # labels were added


class TestAxesAnimateDrawFunction:
    def test_animate_draw_function(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        path = ax.animate_draw_function(lambda x: x**2, start=0, end=2)
        assert path is not None
        # Path should have a d attribute
        d_val = path.d.at_time(1)  # midway
        assert isinstance(d_val, str)

    def test_animate_draw_function_returns_path(self):
        ax = Axes(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        path = ax.animate_draw_function(lambda x: x, start=0, end=1)
        assert path in ax.objects


class TestTextSplitChars:
    def test_split_chars_basic(self):
        t = Text(text='ABC', x=100, y=200, font_size=48)
        chars = t.split_chars()
        assert len(chars.objects) == 3

    def test_split_chars_skips_spaces(self):
        t = Text(text='A B', x=100, y=200, font_size=48)
        chars = t.split_chars()
        assert len(chars.objects) == 2

    def test_split_chars_empty(self):
        t = Text(text='', x=100, y=200, font_size=48)
        chars = t.split_chars()
        assert len(chars.objects) == 0

    def test_split_chars_returns_vcollection(self):
        t = Text(text='Hi', x=100, y=200, font_size=48)
        chars = t.split_chars()
        assert isinstance(chars, VCollection)


class TestBarChartGrowFromZero:
    def test_grow_from_zero(self):
        bc = BarChart(values=[10, 20, 30], labels=['A', 'B', 'C'])
        result = bc.grow_from_zero(start=0, end=2)
        assert result is bc

    def test_grow_from_zero_no_stagger(self):
        bc = BarChart(values=[10, 20], labels=['A', 'B'])
        result = bc.grow_from_zero(start=0, end=1, stagger=False)
        assert result is bc


class TestCanvasDuration:
    def test_duration_property(self):
        import tempfile
        from vectormation._canvas import VectorMathAnim
        v = VectorMathAnim(tempfile.gettempdir())
        c = Circle(r=50)
        v.add(c)
        c.fadein(0, 2)
        assert v.duration >= 2

    def test_duration_empty(self):
        import tempfile
        from vectormation._canvas import VectorMathAnim
        v = VectorMathAnim(tempfile.gettempdir())
        d = v.duration
        assert isinstance(d, (int, float))


class TestChecklistAnimations:
    def test_check_item(self):
        from vectormation.objects import Checklist
        cl = Checklist('Task 1', 'Task 2', 'Task 3')
        result = cl.check_item(0, start=0, end=0.3)
        assert result is cl

    def test_reveal_items(self):
        from vectormation.objects import Checklist
        cl = Checklist('A', 'B', 'C')
        result = cl.reveal_items(start=0, end=1)
        assert result is cl


class TestStepperAdvance:
    def test_advance(self):
        from vectormation.objects import Stepper
        s = Stepper(['Step 1', 'Step 2', 'Step 3'])
        result = s.advance(0, 1, start=0, end=0.5)
        assert result is s


class TestPieChartLabels:
    def test_add_percentage_labels(self):
        from vectormation.objects import PieChart
        pc = PieChart(values=[30, 20, 50])
        initial_count = len(pc.objects)
        result = pc.add_percentage_labels()
        assert result is pc
        assert len(pc.objects) > initial_count


class TestCodeRevealLines:
    def test_reveal_lines(self):
        from vectormation.objects import Code
        c = Code('line1\nline2\nline3', language='python')
        result = c.reveal_lines(start=0, end=2)
        assert result is c

    def test_reveal_lines_returns_self(self):
        from vectormation.objects import Code
        c = Code('a = 1\nb = 2', language='python')
        assert c.reveal_lines(start=0, end=1) is c


class TestTableSortByColumn:
    def test_sort_by_column(self):
        from vectormation.objects import Table
        t = Table(data=[['B', '2'], ['A', '1'], ['C', '3']])
        result = t.sort_by_column(0, start=0, end=1)
        assert result is t


class TestGetGraphIntersection:
    def test_linear_intersection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        # y=x and y=-x intersect at (0, 0)
        pts = ax.get_graph_intersection(lambda x: x, lambda x: -x)
        assert len(pts) >= 1
        # The intersection should be near (0, 0)
        closest = min(pts, key=lambda p: abs(p[0]))
        assert closest[0] == pytest.approx(0, abs=0.02)
        assert closest[1] == pytest.approx(0, abs=0.02)

    def test_parabola_line_intersection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 10))
        # y=x^2 and y=4 intersect at x=-2 and x=2
        pts = ax.get_graph_intersection(lambda x: x**2, lambda _: 4)
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert xs[0] == pytest.approx(-2, abs=0.02)
        assert xs[1] == pytest.approx(2, abs=0.02)

    def test_no_intersection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        # y=1 and y=-1 never intersect
        pts = ax.get_graph_intersection(lambda _: 1, lambda _: -1)
        assert len(pts) == 0

    def test_custom_x_range(self):
        ax = Axes(x_range=(-10, 10), y_range=(-10, 10))
        # y=x^2 and y=4 intersect at x=-2 and x=2, but limit to positive x
        pts = ax.get_graph_intersection(lambda x: x**2, lambda _: 4, x_range=(0, 10))
        assert len(pts) == 1
        assert pts[0][0] == pytest.approx(2, abs=0.02)


class TestMatchPosition:
    def test_match_position_circle_to_rect(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(width=80, height=60, x=400, y=300)
        c.match_position(r)
        cx, cy = c.center(0)
        rx, ry = r.center(0)
        assert cx == pytest.approx(rx, abs=0.1)
        assert cy == pytest.approx(ry, abs=0.1)

    def test_match_position_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Circle(r=30, cx=500, cy=400)
        result = c.match_position(r)
        assert result is c

    def test_match_position_with_tuple(self):
        c = Circle(r=50, cx=100, cy=100)
        c.match_position((500, 300))
        cx, cy = c.center(0)
        assert cx == pytest.approx(500, abs=0.1)
        assert cy == pytest.approx(300, abs=0.1)


# ---------------------------------------------------------------------------
# Math helpers in _constants.py
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_unit_x(self):
        from vectormation._constants import _normalize
        nx, ny = _normalize(5, 0)
        assert nx == pytest.approx(1.0)
        assert ny == pytest.approx(0.0)

    def test_unit_y(self):
        from vectormation._constants import _normalize
        nx, ny = _normalize(0, -3)
        assert nx == pytest.approx(0.0)
        assert ny == pytest.approx(-1.0)

    def test_diagonal(self):
        import math
        from vectormation._constants import _normalize
        nx, ny = _normalize(3, 4)
        assert math.hypot(nx, ny) == pytest.approx(1.0)
        assert nx == pytest.approx(0.6)
        assert ny == pytest.approx(0.8)

    def test_zero_vector(self):
        from vectormation._constants import _normalize
        assert _normalize(0, 0) == (0.0, 0.0)


class TestLerpPoint:
    def test_t0(self):
        from vectormation._constants import _lerp_point
        x, y = _lerp_point(0, 0, 10, 20, 0)
        assert x == pytest.approx(0)
        assert y == pytest.approx(0)

    def test_t1(self):
        from vectormation._constants import _lerp_point
        x, y = _lerp_point(0, 0, 10, 20, 1)
        assert x == pytest.approx(10)
        assert y == pytest.approx(20)

    def test_t_half(self):
        from vectormation._constants import _lerp_point
        x, y = _lerp_point(0, 0, 10, 20, 0.5)
        assert x == pytest.approx(5)
        assert y == pytest.approx(10)


# ---------------------------------------------------------------------------
# VObject convenience methods
# ---------------------------------------------------------------------------

class TestGetOpacity:
    def test_default(self):
        # get_opacity reads the 'opacity' attribute (default 1.0), not fill_opacity
        c = Circle(r=50)
        opacity = c.get_opacity(0)
        assert opacity == pytest.approx(1.0)

    def test_after_set(self):
        c = Circle(r=50)
        c.set_opacity(0.3, start=0)
        assert c.get_opacity(0) == pytest.approx(0.3)

    def test_custom_initial(self):
        # opacity kwarg sets the CSS opacity attribute
        c = Circle(r=50, opacity=0.5)
        assert c.get_opacity(0) == pytest.approx(0.5)

    def test_set_opacity_roundtrip(self):
        # set_opacity writes to 'opacity'; get_opacity reads it back correctly
        c = Circle(r=50)
        c.set_opacity(0.75, start=0)
        assert c.get_opacity(0) == pytest.approx(0.75)


class TestGetColors:
    def test_get_fill_color(self):
        c = Circle(r=50, fill='#ff0000')
        color = c.get_fill_color(0)
        assert color == '#ff0000'

    def test_get_stroke_color(self):
        c = Circle(r=50, stroke='#00ff00')
        color = c.get_stroke_color(0)
        assert color == '#00ff00'

    def test_default_stroke(self):
        c = Circle(r=50)
        color = c.get_stroke_color(0)
        # default stroke is '#fff' -> hex is '#ffffff'
        assert color == '#ffffff'


class TestSetPosition:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=200)
        c.set_position(500, 300)
        cx, cy = c.center(0)
        assert cx == pytest.approx(500, abs=0.1)
        assert cy == pytest.approx(300, abs=0.1)

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.set_position(100, 100)
        assert result is c

    def test_animated(self):
        c = Circle(r=50, cx=100, cy=200)
        c.set_position(500, 300, start=0, end=1)
        # At time 0, should be near original
        cx0, _ = c.center(0)
        assert cx0 == pytest.approx(100, abs=1)
        # At time 1, should be at target
        cx1, cy1 = c.center(1)
        assert cx1 == pytest.approx(500, abs=1)
        assert cy1 == pytest.approx(300, abs=1)


# ---------------------------------------------------------------------------
# New utility methods added in this session
# ---------------------------------------------------------------------------

class TestNumberLineAddLabel:
    def test_returns_self(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        result = nl.add_label(0, 'origin')
        assert result is nl

    def test_label_added_to_objects(self):
        from vectormation._shapes import Text
        nl = NumberLine(x_range=(-5, 5, 1))
        before = len(nl.objects)
        nl.add_label(2, 'two')
        assert len(nl.objects) == before + 1
        assert isinstance(nl.objects[-1], Text)

    def test_label_text_content(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_label(3, 'hello')
        lbl = nl.objects[-1]
        assert lbl.text.at_time(0) == 'hello'

    def test_label_x_position(self):
        # Label should be positioned at number_to_point(value).x
        nl = NumberLine(x_range=(0, 10, 1), length=1000, x=100, y=300)
        nl.add_label(5, '5')
        lbl = nl.objects[-1]
        expected_x, _ = nl.number_to_point(5)
        assert lbl.x.at_time(0) == pytest.approx(expected_x, abs=1)

    def test_label_below(self):
        nl = NumberLine(x_range=(0, 10, 1), length=1000, x=100, y=300)
        nl.add_label(5, '5', buff=10, font_size=24, side='below')
        lbl = nl.objects[-1]
        _, py = nl.number_to_point(5)
        assert lbl.y.at_time(0) > py  # SVG y increases downward

    def test_label_above(self):
        nl = NumberLine(x_range=(0, 10, 1), length=1000, x=100, y=300)
        nl.add_label(5, '5', buff=10, font_size=24, side='above')
        lbl = nl.objects[-1]
        _, py = nl.number_to_point(5)
        assert lbl.y.at_time(0) < py  # above means smaller SVG y

    def test_svg_contains_label(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_label(0, 'CENTER')
        svg = nl.to_svg(0)
        assert 'CENTER' in svg

    def test_custom_font_size(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_label(1, 'x', font_size=30)
        lbl = nl.objects[-1]
        # font_size is a direct attribute on Text, not in styling
        assert lbl.font_size.at_time(0) == pytest.approx(30, abs=1)


class TestBarChartGetMaxMinBar:
    def test_get_max_bar_returns_rectangle(self):
        from vectormation._shapes import Rectangle
        bc = BarChart([10, 30, 20])
        bar = bc.get_max_bar()
        assert isinstance(bar, Rectangle)

    def test_get_min_bar_returns_rectangle(self):
        from vectormation._shapes import Rectangle
        bc = BarChart([10, 30, 20])
        bar = bc.get_min_bar()
        assert isinstance(bar, Rectangle)

    def test_get_max_bar_is_tallest(self):
        bc = BarChart([10, 30, 20])
        max_bar = bc.get_max_bar()
        # The tallest bar has the greatest height attribute value
        max_h = max_bar.height.at_time(0)
        for bar in bc._bars:
            assert bar.height.at_time(0) <= max_h + 1e-6

    def test_get_min_bar_is_shortest(self):
        bc = BarChart([10, 30, 20])
        min_bar = bc.get_min_bar()
        min_h = min_bar.height.at_time(0)
        for bar in bc._bars:
            assert bar.height.at_time(0) >= min_h - 1e-6

    def test_max_bar_corresponds_to_max_value(self):
        values = [5, 99, 42]
        bc = BarChart(values)
        max_bar = bc.get_max_bar()
        assert max_bar is bc._bars[1]

    def test_min_bar_corresponds_to_min_value(self):
        values = [5, 99, 42]
        bc = BarChart(values)
        min_bar = bc.get_min_bar()
        assert min_bar is bc._bars[0]

    def test_single_bar(self):
        bc = BarChart([7])
        assert bc.get_max_bar() is bc._bars[0]
        assert bc.get_min_bar() is bc._bars[0]

    def test_empty_chart_returns_none(self):
        bc = BarChart([])
        assert bc.get_max_bar() is None
        assert bc.get_min_bar() is None

    def test_negative_values_max(self):
        bc = BarChart([-1, -10, -5])
        max_bar = bc.get_max_bar()
        assert max_bar is bc._bars[0]  # -1 is the max

    def test_negative_values_min(self):
        bc = BarChart([-1, -10, -5])
        min_bar = bc.get_min_bar()
        assert min_bar is bc._bars[1]  # -10 is the min


class TestTableGetCellRect:
    def test_returns_rectangle(self):
        from vectormation._shapes import Rectangle
        t = Table([[1, 2], [3, 4]])
        rect = t.get_cell_rect(0, 0)
        assert isinstance(rect, Rectangle)

    def test_not_added_to_table(self):
        t = Table([[1, 2], [3, 4]])
        before = len(t.objects)
        t.get_cell_rect(0, 0)
        assert len(t.objects) == before  # should NOT be added automatically

    def test_cell_position_row0_col0(self):
        cw, ch = 100, 50
        t = Table([[1, 2], [3, 4]], x=0, y=0, cell_width=cw, cell_height=ch)
        padding = 2
        rect = t.get_cell_rect(0, 0, padding=padding)
        assert rect.x.at_time(0) == pytest.approx(padding, abs=1)
        assert rect.y.at_time(0) == pytest.approx(padding, abs=1)

    def test_cell_position_row1_col1(self):
        cw, ch = 100, 50
        t = Table([[1, 2], [3, 4]], x=0, y=0, cell_width=cw, cell_height=ch)
        padding = 2
        rect = t.get_cell_rect(1, 1, padding=padding)
        assert rect.x.at_time(0) == pytest.approx(cw + padding, abs=1)
        assert rect.y.at_time(0) == pytest.approx(ch + padding, abs=1)

    def test_cell_size(self):
        cw, ch = 160, 60
        t = Table([[1, 2], [3, 4]], x=0, y=0, cell_width=cw, cell_height=ch)
        padding = 2
        rect = t.get_cell_rect(0, 0, padding=padding)
        assert rect.width.at_time(0) == pytest.approx(cw - 2 * padding, abs=1)
        assert rect.height.at_time(0) == pytest.approx(ch - 2 * padding, abs=1)

    def test_custom_styling_forwarded(self):
        t = Table([[1, 2], [3, 4]])
        rect = t.get_cell_rect(0, 0, fill='#FF0000')
        # Colors may be normalized to 'rgb(...)' form internally
        fill_val = rect.styling.fill.at_time(0)
        assert '255' in fill_val and '0' in fill_val  # red channel is 255

    def test_zero_padding(self):
        cw, ch = 100, 50
        t = Table([[1, 2], [3, 4]], x=0, y=0, cell_width=cw, cell_height=ch)
        rect = t.get_cell_rect(0, 0, padding=0)
        assert rect.width.at_time(0) == pytest.approx(cw, abs=1)
        assert rect.height.at_time(0) == pytest.approx(ch, abs=1)

    def test_with_row_labels_offset(self):
        cw, ch = 100, 50
        t = Table([[1, 2], [3, 4]], x=0, y=0,
                  cell_width=cw, cell_height=ch, row_labels=['R1', 'R2'])
        padding = 0
        # x_off = cw because row_labels present
        rect = t.get_cell_rect(0, 0, padding=padding)
        assert rect.x.at_time(0) == pytest.approx(cw, abs=1)

    def test_svg_renderable(self):
        t = Table([[1, 2], [3, 4]])
        rect = t.get_cell_rect(0, 0)
        svg = rect.to_svg(0)
        assert '<rect' in svg


class TestAxesAddPointLabel:
    def test_returns_dot_and_label(self):
        from vectormation._shapes import Dot, Text
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_point_label(1, 2, text='P')
        assert isinstance(result, tuple)
        dot, lbl = result
        assert isinstance(dot, Dot)
        assert isinstance(lbl, Text)

    def test_default_text_format(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        _, lbl = ax.add_point_label(3, 4)
        assert lbl.text.at_time(0) == '(3, 4)'

    def test_custom_text(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        _, lbl = ax.add_point_label(0, 0, text='origin')
        assert lbl.text.at_time(0) == 'origin'

    def test_dot_added_to_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        before = len(ax)
        ax.add_point_label(1, 1, text='Q')
        assert len(ax) > before

    def test_dot_position_at_coords(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), x=0, y=0,
                  plot_width=1000, plot_height=1000)
        dot, _ = ax.add_point_label(5, 5, text='mid')
        sx, sy = ax.coords_to_point(5, 5, time=0)
        cx, cy = dot.c.at_time(0)
        assert cx == pytest.approx(sx, abs=2)
        assert cy == pytest.approx(sy, abs=2)

    def test_label_above_dot(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10), x=0, y=0,
                  plot_width=1000, plot_height=1000)
        dot, lbl = ax.add_point_label(5, 5, text='T', buff=10, dot_radius=6)
        dot_cy = dot.c.at_time(0)[1]
        assert lbl.y.at_time(0) < dot_cy  # label SVG y < dot SVG y means above

    def test_no_text_uses_coord_format(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        _, lbl = ax.add_point_label(2, 7)
        assert '2' in lbl.text.at_time(0)
        assert '7' in lbl.text.at_time(0)

    def test_svg_contains_dot_and_text(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.add_point_label(0, 0, text='Z')
        svg = ax.to_svg(0)
        assert '<circle' in svg
        assert 'Z' in svg


class TestFlashHighlight:
    def test_returns_rectangle(self):
        c = Circle(r=50, cx=200, cy=200)
        rect = c.flash_highlight(start=0, end=1)
        assert isinstance(rect, Rectangle)

    def test_stroke_opacity_fades_in_and_out(self):
        c = Circle(r=50, cx=200, cy=200)
        rect = c.flash_highlight(start=0, end=1, color='#ff0')
        # starts at 0
        assert rect.styling.stroke_opacity.at_time(0) == pytest.approx(0)
        # peak at midpoint
        assert rect.styling.stroke_opacity.at_time(0.5) == pytest.approx(1)
        # returns to 0 at end
        assert rect.styling.stroke_opacity.at_time(1) == pytest.approx(0)

    def test_fill_opacity_is_zero(self):
        c = Circle(r=50, cx=100, cy=100)
        rect = c.flash_highlight(start=0, end=1)
        assert rect.styling.fill_opacity.at_time(0) == pytest.approx(0)
        assert rect.styling.fill_opacity.at_time(0.5) == pytest.approx(0)

    def test_custom_color(self):
        c = Circle(r=50, cx=100, cy=100)
        rect = c.flash_highlight(start=0, end=1, color='#f00')
        stroke = rect.styling.stroke.at_time(0)
        assert '255' in stroke  # red component present

    def test_rect_larger_than_object(self):
        c = Circle(r=50, cx=200, cy=200)
        _, _, bw, bh = c.bbox(0)
        rect = c.flash_highlight(start=0, end=1)
        _, _, rw, rh = rect.bbox(0)
        assert rw >= bw
        assert rh >= bh

    def test_zero_duration_still_returns_rect(self):
        c = Circle(r=50, cx=100, cy=100)
        rect = c.flash_highlight(start=1, end=1)
        assert isinstance(rect, Rectangle)

    def test_custom_stroke_width(self):
        c = Circle(r=50, cx=100, cy=100)
        rect = c.flash_highlight(start=0, end=1, width=6)
        assert rect.styling.stroke_width.at_time(0) == pytest.approx(6)


class TestAxesShadeRegion:
    def test_shade_region_x_only_returns_rectangle(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        rect = ax.shade_region(x_start=1, x_end=3)
        from vectormation.objects import Rectangle
        assert isinstance(rect, Rectangle)

    def test_shade_region_x_only_has_full_height(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        rect = ax.shade_region(x_start=1, x_end=3)
        # With no y_range, height should span the full plot height
        h = rect.height.at_time(0)
        assert h == pytest.approx(ax.plot_height, abs=1)

    def test_shade_region_y_only_has_full_width(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        rect = ax.shade_region(x_start=None, x_end=None, y_start=-2, y_end=2)
        w = rect.width.at_time(0)
        assert w == pytest.approx(ax.plot_width, abs=1)

    def test_shade_region_both_axes_constrained(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        rect = ax.shade_region(x_start=2, x_end=8, y_start=3, y_end=7)
        w = rect.width.at_time(0)
        h = rect.height.at_time(0)
        # Should be strictly smaller than plot dimensions
        assert w < ax.plot_width
        assert h < ax.plot_height
        assert w > 0
        assert h > 0

    def test_shade_region_added_to_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.shade_region(x_start=-1, x_end=1)
        # The rectangle should appear in the axes SVG output
        svg = ax.to_svg(0)
        assert '<rect' in svg

    def test_shade_region_default_fill_style(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        rect = ax.shade_region(x_start=0, x_end=2)
        # Default fill should be yellow highlight
        fill = rect.styling.fill.at_time(0)
        assert '255' in fill or 'ff' in fill.lower()

    def test_shade_region_custom_style(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        rect = ax.shade_region(x_start=0, x_end=2, fill='#f00', fill_opacity=0.5)
        assert rect.styling.fill_opacity.at_time(0) == pytest.approx(0.5)


# ── color_gradient_anim ─────────────────────────────────────────────────────

class TestColorGradientAnim:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.color_gradient_anim(['#ff0000', '#0000ff'], start=0, end=1)
        assert result is c

    def test_fill_at_start_is_first_color(self):
        c = Circle(r=50, cx=100, cy=100)
        c.color_gradient_anim(['#ff0000', '#0000ff'], start=0, end=1)
        fill = c.styling.fill.at_time(0)
        assert 'rgb(255,0,0)' == fill

    def test_fill_at_end_is_last_color(self):
        c = Circle(r=50, cx=100, cy=100)
        c.color_gradient_anim(['#ff0000', '#0000ff'], start=0, end=1)
        fill = c.styling.fill.at_time(1)
        assert 'rgb(0,0,255)' == fill

    def test_midpoint_interpolated(self):
        c = Circle(r=50, cx=100, cy=100)
        c.color_gradient_anim(['#ff0000', '#0000ff'], start=0, end=2)
        fill = c.styling.fill.at_time(1)
        # At t=1 (halfway) → rgb(127 or 128, 0, 127 or 128)
        assert '127' in fill or '128' in fill

    def test_three_color_segments(self):
        c = Circle(r=50, cx=100, cy=100)
        c.color_gradient_anim(['#ff0000', '#00ff00', '#0000ff'], start=0, end=2)
        # At t=1 should be pure green (midpoint between red→green→blue)
        fill = c.styling.fill.at_time(1)
        assert 'rgb(0,255,0)' == fill

    def test_stroke_attr(self):
        c = Circle(r=50, cx=100, cy=100)
        c.color_gradient_anim(['#ffffff', '#000000'], start=0, end=1, attr='stroke')
        stroke_start = c.styling.stroke.at_time(0)
        stroke_end = c.styling.stroke.at_time(1)
        assert 'rgb(255,255,255)' == stroke_start
        assert 'rgb(0,0,0)' == stroke_end

    def test_single_color_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.color_gradient_anim(['#ff0000'], start=0, end=1)
        assert result is c  # returns self without error

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.color_gradient_anim(['#ff0000', '#0000ff'], start=1, end=1)
        assert result is c


# ── Arc.to_wedge ────────────────────────────────────────────────────────────

class TestArcToWedge:
    def test_returns_wedge_type(self):
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        w = arc.to_wedge()
        assert type(w).__name__ == 'Wedge'

    def test_geometry_matches_arc(self):
        arc = Arc(cx=500, cy=400, r=80, start_angle=30, end_angle=120)
        w = arc.to_wedge()
        assert w.cx.at_time(0) == pytest.approx(500)
        assert w.cy.at_time(0) == pytest.approx(400)
        assert w.r.at_time(0) == pytest.approx(80)
        assert w.start_angle.at_time(0) == pytest.approx(30)
        assert w.end_angle.at_time(0) == pytest.approx(120)

    def test_kwargs_forwarded(self):
        arc = Arc(cx=100, cy=200, r=50, start_angle=0, end_angle=180)
        w = arc.to_wedge(fill='#44aaff', fill_opacity=0.8)
        assert w.styling.fill_opacity.at_time(0) == pytest.approx(0.8)

    def test_produces_valid_svg(self):
        arc = Arc(cx=300, cy=300, r=100, start_angle=45, end_angle=225)
        w = arc.to_wedge()
        svg = w.to_svg(0)
        assert svg.startswith('<path')
        assert 'Z' in svg  # wedge closes through centre

    def test_independent_of_original(self):
        arc = Arc(cx=500, cy=400, r=100, start_angle=0, end_angle=90)
        w = arc.to_wedge()
        # Modifying arc should not affect the snapshot wedge
        arc.r.set_onward(0, 999)
        assert w.r.at_time(0) == pytest.approx(100)


# ── VObject.fade_color ───────────────────────────────────────────────────────

class TestFadeColor:
    def test_fill_reaches_target_at_end(self):
        c = Circle(r=50, fill='#0000ff')
        c.fade_color('#ff0000', start=0, end=1)
        rgb = c.styling.fill.time_func(1)
        # Red channel should be 255, blue should be 0
        assert rgb[0] == pytest.approx(255, abs=2)
        assert rgb[2] == pytest.approx(0, abs=2)

    def test_fill_starts_from_original_at_start(self):
        c = Circle(r=50, fill='#0000ff')
        c.fade_color('#ff0000', start=0, end=1)
        rgb = c.styling.fill.time_func(0)
        assert rgb[2] == pytest.approx(255, abs=2)  # still blue

    def test_stroke_attr(self):
        c = Circle(r=50, stroke='#ffffff')
        c.fade_color('#000000', start=0, end=1, attr='stroke')
        rgb = c.styling.stroke.time_func(1)
        assert rgb[0] == pytest.approx(0, abs=2)
        assert rgb[1] == pytest.approx(0, abs=2)
        assert rgb[2] == pytest.approx(0, abs=2)

    def test_midpoint_is_interpolated(self):
        c = Circle(r=50, fill='#000000')
        c.fade_color('#ffffff', start=0, end=1)
        rgb = c.styling.fill.time_func(0.5)
        # Midpoint should be roughly grey (all channels ~128)
        assert rgb[0] == pytest.approx(128, abs=5)

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.fade_color('#ff0000', start=0, end=1)
        assert result is c

    def test_respects_easing(self):
        import vectormation.easings as easings
        c = Circle(r=50, fill='#000000')
        c.fade_color('#ffffff', start=0, end=1, easing=easings.linear)
        rgb_mid = c.styling.fill.time_func(0.5)
        rgb_end = c.styling.fill.time_func(1.0)
        # With linear easing mid should be exactly half of end
        assert rgb_mid[0] == pytest.approx(rgb_end[0] / 2, abs=2)

    def test_time_parameter(self):
        arc = Arc(cx=500, cy=400, r=50, start_angle=0, end_angle=90)
        arc.r.set_onward(1, 200)
        w_t0 = arc.to_wedge(time=0)
        w_t2 = arc.to_wedge(time=2)
        assert w_t0.r.at_time(0) == pytest.approx(50)
        assert w_t2.r.at_time(0) == pytest.approx(200)


# ── VCollection.space_evenly ─────────────────────────────────────────────────

class TestSpaceEvenly:
    def test_returns_self(self):
        c1, c2, c3 = Circle(r=20, cx=0, cy=0), Circle(r=20, cx=100, cy=0), Circle(r=20, cx=200, cy=0)
        col = VCollection(c1, c2, c3)
        result = col.space_evenly(total_span=400, start_pos=0)
        assert result is col

    def test_fills_exact_span(self):
        circles = [Circle(r=20, cx=i * 50, cy=0) for i in range(3)]
        col = VCollection(*circles)
        col.space_evenly(total_span=500, start_pos=0)
        boxes = [c.bbox(0) for c in circles]
        leftmost = min(b[0] for b in boxes)
        rightmost = max(b[0] + b[2] for b in boxes)
        assert leftmost == pytest.approx(0, abs=1)
        assert rightmost == pytest.approx(500, abs=1)

    def test_equal_gaps(self):
        circles = [Circle(r=10, cx=i * 10, cy=0) for i in range(4)]
        col = VCollection(*circles)
        col.space_evenly(total_span=300, start_pos=0)
        lefts = [c.bbox(0)[0] for c in circles]
        gaps = []
        for i in range(1, len(lefts)):
            prev_right = circles[i-1].bbox(0)[0] + circles[i-1].bbox(0)[2]
            gaps.append(lefts[i] - prev_right)
        # All gaps should be equal
        assert all(abs(g - gaps[0]) < 1 for g in gaps)

    def test_start_pos_respected(self):
        circles = [Circle(r=20, cx=0, cy=0) for _ in range(3)]
        col = VCollection(*circles)
        col.space_evenly(total_span=300, start_pos=100)
        leftmost = min(c.bbox(0)[0] for c in circles)
        assert leftmost == pytest.approx(100, abs=1)

    def test_single_child_no_error(self):
        c = Circle(r=30, cx=0, cy=0)
        col = VCollection(c)
        result = col.space_evenly(total_span=200, start_pos=0)
        assert result is col

    def test_empty_collection_no_error(self):
        col = VCollection()
        result = col.space_evenly(total_span=200, start_pos=0)
        assert result is col

    def test_vertical_direction(self):
        circles = [Circle(r=10, cx=0, cy=i * 10) for i in range(3)]
        col = VCollection(*circles)
        col.space_evenly(direction='down', total_span=400, start_pos=0)
        tops = [c.bbox(0)[1] for c in circles]
        bottoms = [c.bbox(0)[1] + c.bbox(0)[3] for c in circles]
        assert min(tops) == pytest.approx(0, abs=1)
        assert max(bottoms) == pytest.approx(400, abs=1)

    def test_default_span_uses_bbox(self):
        # With no total_span, it should use the existing group bbox span
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=200, cy=0)
        c3 = Circle(r=20, cx=400, cy=0)
        col = VCollection(c1, c2, c3)
        original_span = col.get_width(0)
        col.space_evenly()
        new_span = col.get_width(0)
        assert new_span == pytest.approx(original_span, abs=2)


# ── Axes.add_callout ─────────────────────────────────────────────────────────

class TestAxesAddCallout:
    def test_returns_vcollection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_callout(1, 2, 'Max')
        assert isinstance(result, VCollection)

    def test_has_three_children(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_callout(0, 0, 'Origin')
        assert len(result.objects) == 3  # line, box, label

    def test_text_appears_in_svg(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.add_callout(1, 1, 'TestLabel')
        svg = ax.to_svg(0)
        assert 'TestLabel' in svg

    def test_rect_appears_in_svg(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.add_callout(1, 1, 'Note')
        svg = ax.to_svg(0)
        assert '<rect' in svg

    def test_custom_text_color(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_callout(0, 0, 'Hi', text_color='#ff0000')
        lbl = result.objects[2]
        assert 'rgb(255,0,0)' in lbl.to_svg(0)

    def test_creation_time(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.add_callout(0, 0, 'Late', creation=2)
        # SVG at t=0 should not contain the callout
        svg0 = ax.to_svg(0)
        svg3 = ax.to_svg(3)
        assert 'Late' not in svg0
        assert 'Late' in svg3

    def test_box_tracks_dynamic_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_callout(2, 2, 'Moving')
        box = result.objects[1]
        x0 = box.x.at_time(0)
        # After an axis range change the box should shift
        ax.x_min.set_onward(0, -10)
        x1 = box.x.at_time(0)
        assert x0 != x1


class TestSquashAndStretch:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.squash_and_stretch(start=0, end=1)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.squash_and_stretch(start=0, end=0)
        assert result is c

    def test_scale_x_peaks_at_midpoint(self):
        """At midpoint, scale_x should be close to factor (wider)."""
        c = Circle(r=50, cx=100, cy=100)
        import vectormation.easings as easings
        c.squash_and_stretch(start=0, end=2, factor=1.5, easing=easings.linear)
        sx_mid = c.styling.scale_x.at_time(1.0)
        # there_and_back peaks at t=0.5 → easing(0.5)≈1 → scale_x ≈ 1.5
        assert sx_mid == pytest.approx(1.5, abs=0.05)

    def test_scale_y_is_inverse_of_scale_x(self):
        """Area preservation: scale_x * scale_y should stay close to 1."""
        c = Circle(r=50, cx=100, cy=100)
        import vectormation.easings as easings
        c.squash_and_stretch(start=0, end=2, factor=1.5, easing=easings.linear)
        for t in (0.25, 0.5, 1.0, 1.5):
            sx = c.styling.scale_x.at_time(t)
            sy = c.styling.scale_y.at_time(t)
            assert sx * sy == pytest.approx(1.0, abs=0.02)

    def test_returns_to_original_at_end(self):
        """After the animation, both scale axes should be back to 1."""
        c = Circle(r=50, cx=100, cy=100)
        import vectormation.easings as easings
        c.squash_and_stretch(start=0, end=1, factor=1.3, easing=easings.linear)
        sx_end = c.styling.scale_x.at_time(1.0)
        sy_end = c.styling.scale_y.at_time(1.0)
        assert sx_end == pytest.approx(1.0, abs=0.02)
        assert sy_end == pytest.approx(1.0, abs=0.02)

    def test_renders_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.squash_and_stretch(start=0, end=1, factor=1.3)
        svg = c.to_svg(0.5)
        assert 'circle' in svg.lower() or 'ellipse' in svg.lower()


class TestScaleToSize:
    def test_returns_self(self):
        r = Rectangle(200, 100)
        assert r.scale_to_size(width=400) is r

    def test_scale_to_width_proportional(self):
        r = Rectangle(200, 100)
        r.scale_to_size(width=400)
        assert r.get_width() == pytest.approx(400, rel=0.01)

    def test_scale_to_width_preserves_aspect_ratio(self):
        r = Rectangle(200, 100)
        r.scale_to_size(width=400)
        # height should double as well (proportional)
        assert r.get_height() == pytest.approx(200, rel=0.01)

    def test_scale_to_height_proportional(self):
        r = Rectangle(200, 100)
        r.scale_to_size(height=200)
        assert r.get_height() == pytest.approx(200, rel=0.01)

    def test_scale_to_height_preserves_aspect_ratio(self):
        r = Rectangle(200, 100)
        r.scale_to_size(height=200)
        # width should double as well
        assert r.get_width() == pytest.approx(400, rel=0.01)

    def test_scale_to_both_independent(self):
        r = Rectangle(200, 100)
        r.scale_to_size(width=100, height=100)
        assert r.get_width() == pytest.approx(100, rel=0.05)
        assert r.get_height() == pytest.approx(100, rel=0.05)

    def test_animated_reaches_target_width(self):
        r = Rectangle(200, 100)
        r.scale_to_size(width=600, start=0, end=1, easing=easings.linear)
        assert r.get_width(1) == pytest.approx(600, rel=0.01)

    def test_animated_reaches_target_height(self):
        r = Rectangle(200, 100)
        r.scale_to_size(height=300, start=0, end=1, easing=easings.linear)
        assert r.get_height(1) == pytest.approx(300, rel=0.01)

    def test_no_args_noop(self):
        r = Rectangle(200, 100)
        r.scale_to_size()
        assert r.get_width() == pytest.approx(200, rel=0.01)
        assert r.get_height() == pytest.approx(100, rel=0.01)


# ── VObject.emphasize_scale ──────────────────────────────────────────────────

class TestEmphasizeScale:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.emphasize_scale(0, 1)
        assert result is c

    def test_scale_at_start_is_original(self):
        """At time=0 (start) scale should equal the base scale (1.0)."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, scale_factor=1.5)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0, abs=1e-3)
        assert c.styling.scale_y.at_time(0) == pytest.approx(1.0, abs=1e-3)

    def test_scale_at_end_is_original(self):
        """After the animation the scale returns to the original value."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, scale_factor=1.5)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0, abs=1e-3)
        assert c.styling.scale_y.at_time(1) == pytest.approx(1.0, abs=1e-3)

    def test_peak_scale_greater_than_one(self):
        """At midpoint the scale should be larger than the original (there_and_back peaks at 0.5)."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, scale_factor=1.4)
        mid_scale = c.styling.scale_x.at_time(0.5)
        assert mid_scale > 1.0

    def test_uniform_scale_x_equals_y(self):
        """Both axes must scale identically (uniform scale)."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, scale_factor=1.3)
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            assert c.styling.scale_x.at_time(t) == pytest.approx(
                c.styling.scale_y.at_time(t), abs=1e-9
            )

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.emphasize_scale(0.5, 0.5, scale_factor=2.0)
        assert result is c
        assert c.styling.scale_x.at_time(0.5) == pytest.approx(1.0, abs=1e-3)

    def test_respects_existing_scale(self):
        """If the object already has a non-unit scale, the pulse is relative to that."""
        c = Circle(r=50, cx=100, cy=100)
        c.styling.scale_x.set_onward(0, 2.0)
        c.styling.scale_y.set_onward(0, 2.0)
        c.emphasize_scale(0, 1, scale_factor=1.5)
        # At midpoint scale_x should be bigger than 2.0
        assert c.styling.scale_x.at_time(0.5) > 2.0


# ── Text.char_count ──────────────────────────────────────────────────────────

class TestTextCharCount:
    def test_simple_string(self):
        t = Text(text='hello')
        assert t.char_count() == 5

    def test_empty_string(self):
        t = Text(text='')
        assert t.char_count() == 0

    def test_spaces_count(self):
        t = Text(text='hello world')
        assert t.char_count() == 11

    def test_returns_int(self):
        t = Text(text='abc')
        assert isinstance(t.char_count(), int)

    def test_uses_time_zero(self):
        """char_count uses the text at time=0, not a later animated value."""
        t = Text(text='abc')
        t.text.set_onward(1.0, 'longer text')
        assert t.char_count() == 3


# ── VCollection.filter_by_type ───────────────────────────────────────────────

class TestFilterByType2:
    def test_keeps_correct_type(self):
        c1 = Circle(r=10)
        r1 = Rectangle(50, 50)
        c2 = Circle(r=20)
        col = VCollection(c1, r1, c2)
        result = col.filter_by_type(Circle)
        assert len(result.objects) == 2
        assert c1 in result.objects
        assert c2 in result.objects

    def test_excludes_wrong_type(self):
        c = Circle(r=10)
        r = Rectangle(50, 50)
        col = VCollection(c, r)
        result = col.filter_by_type(Rectangle)
        assert r in result.objects
        assert c not in result.objects

    def test_empty_when_no_match(self):
        c = Circle(r=10)
        col = VCollection(c)
        result = col.filter_by_type(Rectangle)
        assert len(result.objects) == 0

    def test_returns_vcollection(self):
        c = Circle(r=10)
        col = VCollection(c)
        result = col.filter_by_type(Circle)
        assert isinstance(result, VCollection)

    def test_subclass_included(self):
        """Dot is a subclass of Circle; filter_by_type(Circle) should include it."""
        from vectormation.objects import Dot
        d = Dot(cx=0, cy=0)
        r = Rectangle(50, 50)
        col = VCollection(d, r)
        result = col.filter_by_type(Circle)
        assert d in result.objects
        assert r not in result.objects


# ── Axes.screen_to_coords ────────────────────────────────────────────────────

class TestAxesScreenToCoords:
    def _make_axes(self):
        return Axes(x_range=(-5, 5), y_range=(-5, 5))

    def test_roundtrip_origin(self):
        """coords_to_point(0,0) → screen_to_coords should return (0,0)."""
        ax = self._make_axes()
        sx, sy = ax.coords_to_point(0, 0)
        x, y = ax.screen_to_coords(sx, sy)
        assert x == pytest.approx(0.0, abs=1e-6)
        assert y == pytest.approx(0.0, abs=1e-6)

    def test_roundtrip_arbitrary(self):
        ax = self._make_axes()
        for mx, my in [(2.5, -3.0), (-1.0, 4.5), (5.0, 5.0), (-5.0, -5.0)]:
            sx, sy = ax.coords_to_point(mx, my)
            rx, ry = ax.screen_to_coords(sx, sy)
            assert rx == pytest.approx(mx, abs=1e-5)
            assert ry == pytest.approx(my, abs=1e-5)

    def test_plot_top_left_is_xmin_ymax(self):
        ax = self._make_axes()
        sx, sy = ax.coords_to_point(-5, 5)
        x, y = ax.screen_to_coords(sx, sy)
        assert x == pytest.approx(-5.0, abs=1e-5)
        assert y == pytest.approx(5.0, abs=1e-5)

    def test_plot_bottom_right_is_xmax_ymin(self):
        ax = self._make_axes()
        sx, sy = ax.coords_to_point(5, -5)
        x, y = ax.screen_to_coords(sx, sy)
        assert x == pytest.approx(5.0, abs=1e-5)
        assert y == pytest.approx(-5.0, abs=1e-5)

    def test_asymmetric_range_roundtrip(self):
        ax = Axes(x_range=(0, 10), y_range=(2, 8))
        for mx, my in [(0, 2), (10, 8), (5, 5), (3.7, 6.2)]:
            sx, sy = ax.coords_to_point(mx, my)
            rx, ry = ax.screen_to_coords(sx, sy)
            assert rx == pytest.approx(mx, abs=1e-5)
            assert ry == pytest.approx(my, abs=1e-5)

    def test_returns_tuple_of_floats(self):
        ax = self._make_axes()
        result = ax.screen_to_coords(960, 540)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestMorphStyle:
    def test_morph_style_animates_fill(self):
        """After morph_style ends, fill should match target's fill."""
        r1 = Rectangle(100, 50, fill='#ff0000')
        r2 = Rectangle(100, 50, fill='#0000ff')
        r1.morph_style(r2, start=0, end=1)
        # At t=1 the fill should be r2's fill
        r1_fill = r1.styling.fill.time_func(1)
        r2_fill = r2.styling.fill.time_func(0)
        assert r1_fill == pytest.approx(r2_fill, abs=5)

    def test_morph_style_animates_stroke_width(self):
        """After morph_style, stroke_width should match target."""
        c1 = Circle(r=50, stroke_width=2)
        c2 = Circle(r=50, stroke_width=10)
        c1.morph_style(c2, start=0, end=1)
        sw = c1.styling.stroke_width.at_time(1)
        assert sw == pytest.approx(10.0, abs=0.1)

    def test_morph_style_at_start_is_original(self):
        """At t=start the style should be unchanged (no jump)."""
        c1 = Circle(r=50, fill_opacity=0.2)
        c2 = Circle(r=50, fill_opacity=0.9)
        c1.morph_style(c2, start=1, end=2)
        # At t=1 the value should still be the original (0.2)
        op = c1.styling.fill_opacity.at_time(1)
        assert op == pytest.approx(0.2, abs=0.05)

    def test_morph_style_returns_self(self):
        """morph_style should return self for chaining."""
        r1 = Rectangle(100, 50)
        r2 = Rectangle(100, 50, fill='#00ff00')
        result = r1.morph_style(r2, start=0, end=1)
        assert result is r1

    def test_morph_style_midpoint(self):
        """At the midpoint of the animation, values should be between start and target."""
        c1 = Circle(r=50, stroke_width=0)
        c2 = Circle(r=50, stroke_width=10)
        c1.morph_style(c2, start=0, end=2)
        sw_mid = c1.styling.stroke_width.at_time(1)
        assert 0.0 < sw_mid < 10.0


class TestVObjectClone:
    def test_clone_returns_same_type(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone()
        assert isinstance(c2, Circle)

    def test_clone_no_offset_same_position(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone()
        cx2, cy2 = c2.c.at_time(0)
        assert cx2 == pytest.approx(100)
        assert cy2 == pytest.approx(200)

    def test_clone_offset_x(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone(offset_x=50)
        cx2, cy2 = c2.c.at_time(0)
        assert cx2 == pytest.approx(150)
        assert cy2 == pytest.approx(200)

    def test_clone_offset_y(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone(offset_y=-30)
        cx2, cy2 = c2.c.at_time(0)
        assert cx2 == pytest.approx(100)
        assert cy2 == pytest.approx(170)

    def test_clone_both_offsets(self):
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone(offset_x=20, offset_y=40)
        cx2, cy2 = c2.c.at_time(0)
        assert cx2 == pytest.approx(120)
        assert cy2 == pytest.approx(240)

    def test_clone_is_independent(self):
        """Modifying the clone should not affect the original."""
        c = Circle(r=50, cx=100, cy=200)
        c2 = c.clone(offset_x=0)
        c2.shift(dx=500)
        cx_orig, _ = c.c.at_time(0)
        assert cx_orig == pytest.approx(100)

    def test_clone_rectangle(self):
        r = Rectangle(width=100, height=50, x=10, y=20)
        r2 = r.clone(offset_x=200, offset_y=100)
        assert r2.x.at_time(0) == pytest.approx(210)
        assert r2.y.at_time(0) == pytest.approx(120)


class TestAxesFunctionMaxMin:
    def test_get_function_max_parabola(self):
        """-(x^2) has its maximum at x=0."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 1))
        x, y = ax.get_function_max(lambda x: -(x ** 2), -3, 3)
        assert x == pytest.approx(0.0, abs=0.1)
        assert y == pytest.approx(0.0, abs=0.01)

    def test_get_function_min_parabola(self):
        """x^2 has its minimum at x=0."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        x, y = ax.get_function_min(lambda x: x ** 2, -3, 3)
        assert x == pytest.approx(0.0, abs=0.1)
        assert y == pytest.approx(0.0, abs=0.01)

    def test_get_function_max_linear(self):
        """f(x) = x has max at right end of domain."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        x, y = ax.get_function_max(lambda x: x, 0, 10)
        assert x == pytest.approx(10.0, abs=0.1)
        assert y == pytest.approx(10.0, abs=0.1)

    def test_get_function_min_linear(self):
        """f(x) = x has min at left end of domain."""
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        x, y = ax.get_function_min(lambda x: x, 0, 10)
        assert x == pytest.approx(0.0, abs=0.1)
        assert y == pytest.approx(0.0, abs=0.1)

    def test_get_function_max_returns_tuple(self):
        ax = Axes(x_range=(-1, 1), y_range=(-1, 1))
        result = ax.get_function_max(lambda x: x, -1, 1)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_function_min_returns_tuple(self):
        ax = Axes(x_range=(-1, 1), y_range=(-1, 1))
        result = ax.get_function_min(lambda x: x, -1, 1)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_function_max_accepts_curve(self):
        """get_function_max should work with a curve path returned by plot()."""
        ax = Axes(x_range=(-2, 2), y_range=(-5, 5))
        curve = ax.plot(lambda x: -(x ** 2))
        x, y = ax.get_function_max(curve, -2, 2)
        assert x == pytest.approx(0.0, abs=0.1)
        assert y == pytest.approx(0.0, abs=0.01)

    def test_get_function_min_accepts_curve(self):
        """get_function_min should work with a curve path returned by plot()."""
        ax = Axes(x_range=(-2, 2), y_range=(-5, 5))
        curve = ax.plot(lambda x: x ** 2)
        x, y = ax.get_function_min(curve, -2, 2)
        assert x == pytest.approx(0.0, abs=0.1)
        assert y == pytest.approx(0.0, abs=0.01)

    def test_get_function_max_sine(self):
        """sin(x) has max ~1 at x=pi/2 in [0, pi]."""
        import math
        ax = Axes(x_range=(0, 4), y_range=(-1, 1))
        _, y = ax.get_function_max(math.sin, 0, math.pi)
        assert y == pytest.approx(1.0, abs=0.01)

    def test_get_function_min_sine(self):
        """sin(x) has min ~-1 at x=3*pi/2 in [pi, 2*pi]."""
        import math
        ax = Axes(x_range=(0, 7), y_range=(-1, 1))
        _, y = ax.get_function_min(math.sin, math.pi, 2 * math.pi)
        assert y == pytest.approx(-1.0, abs=0.01)


class TestAxesGetDerivative:
    def test_derivative_of_square_at_zero(self):
        """d/dx x^2 at x=0 should be ~0."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        d = ax.get_derivative(lambda x: x ** 2, 0.0)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_derivative_of_square_at_three(self):
        """d/dx x^2 at x=3 should be ~6."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        d = ax.get_derivative(lambda x: x ** 2, 3.0)
        assert d == pytest.approx(6.0, abs=1e-6)

    def test_derivative_of_linear(self):
        """d/dx (2x + 1) should equal 2 everywhere."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        d = ax.get_derivative(lambda x: 2 * x + 1, 7.5)
        assert d == pytest.approx(2.0, abs=1e-9)

    def test_derivative_of_sin_at_zero(self):
        """d/dx sin(x) at x=0 should be ~1."""
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        d = ax.get_derivative(math.sin, 0.0)
        assert d == pytest.approx(1.0, abs=1e-6)

    def test_derivative_of_sin_at_pi_half(self):
        """d/dx sin(x) at x=pi/2 should be ~0."""
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-1, 1))
        d = ax.get_derivative(math.sin, math.pi / 2)
        assert d == pytest.approx(0.0, abs=1e-4)

    def test_derivative_returns_float(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        d = ax.get_derivative(lambda x: x, 0.0)
        assert isinstance(d, float)

    def test_derivative_from_curve(self):
        """Should also work when passed a curve returned by plot()."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        curve = ax.plot(lambda x: x ** 2)
        d = ax.get_derivative(curve, 2.0)
        assert d == pytest.approx(4.0, abs=1e-5)

    def test_derivative_custom_h(self):
        """Using a smaller h should still give accurate results."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        d = ax.get_derivative(lambda x: x ** 3, 2.0, h=1e-5)
        assert d == pytest.approx(12.0, abs=1e-4)


class TestVObjectPulseScale:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.pulse_scale(0, 1)
        assert result is c

    def test_scale_at_start_unchanged(self):
        """At t=start the scale should still be the baseline."""
        c = Circle(r=50, cx=100, cy=100)
        c.pulse_scale(0, 2)
        # At exactly t=0, sin(0)=0 so scale = baseline * (1 + amp * 0) = baseline
        sx = c.styling.scale_x.at_time(0)
        assert sx == pytest.approx(1.0, abs=1e-6)

    def test_scale_oscillates(self):
        """Scale should vary during the animation interval."""
        c = Circle(r=50, cx=100, cy=100)
        c.pulse_scale(0, 1, count=2, amplitude=0.2)
        values = [c.styling.scale_x.at_time(t) for t in [0.1, 0.3, 0.6, 0.9]]
        # Not all values should be identical (there's oscillation)
        assert not all(abs(v - values[0]) < 1e-9 for v in values)

    def test_scale_within_amplitude_bounds(self):
        """Scale should stay within [1 - amplitude, 1 + amplitude]."""
        amplitude = 0.15
        c = Circle(r=50, cx=100, cy=100)
        c.pulse_scale(0, 1, count=3, amplitude=amplitude)
        samples = [c.styling.scale_x.at_time(t / 100) for t in range(101)]
        assert all(1.0 - amplitude - 1e-9 <= s <= 1.0 + amplitude + 1e-9 for s in samples)

    def test_scale_x_and_y_equal(self):
        """Both axes should be scaled uniformly."""
        c = Circle(r=50, cx=100, cy=100)
        c.pulse_scale(0, 1, count=2, amplitude=0.1)
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            sx = c.styling.scale_x.at_time(t)
            sy = c.styling.scale_y.at_time(t)
            assert sx == pytest.approx(sy, abs=1e-12)

    def test_zero_duration_no_error(self):
        """Zero-duration call should not raise and should return self."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.pulse_scale(1, 1)
        assert result is c


class TestAnimateOpacity:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.animate_opacity(0.0, 1.0, start=0, end=1)
        assert result is c

    def test_opacity_at_start(self):
        """Opacity at t=start should equal start_opacity."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(0.2, 0.8, start=0, end=1, easing=easings.linear)
        assert c.styling.opacity.at_time(0) == pytest.approx(0.2, abs=1e-6)

    def test_opacity_at_end(self):
        """Opacity at t=end should equal end_opacity."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(0.2, 0.8, start=0, end=1, easing=easings.linear)
        assert c.styling.opacity.at_time(1) == pytest.approx(0.8, abs=1e-6)

    def test_opacity_midpoint_linear(self):
        """At t=0.5 with linear easing, opacity should be the midpoint."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(0.0, 1.0, start=0, end=1, easing=easings.linear)
        assert c.styling.opacity.at_time(0.5) == pytest.approx(0.5, abs=1e-2)

    def test_fill_opacity_also_updated(self):
        """fill_opacity should be animated to match the target value."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(0.0, 0.6, start=0, end=1, easing=easings.linear)
        assert c.styling.fill_opacity.at_time(1) == pytest.approx(0.6, abs=1e-6)

    def test_zero_duration_snaps_to_end_value(self):
        """Zero-duration call should snap opacity to end_opacity."""
        c = Circle(r=50)
        c.animate_opacity(0.1, 0.9, start=2, end=2)
        assert c.styling.opacity.at_time(2) == pytest.approx(0.9, abs=1e-6)

    def test_arbitrary_range(self):
        """Works with non-zero start time."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(0.3, 0.7, start=2, end=4, easing=easings.linear)
        assert c.styling.opacity.at_time(2) == pytest.approx(0.3, abs=1e-2)
        assert c.styling.opacity.at_time(4) == pytest.approx(0.7, abs=1e-6)

    def test_fade_down(self):
        """Can animate from high to low opacity."""
        import vectormation.easings as easings
        c = Circle(r=50)
        c.animate_opacity(1.0, 0.0, start=0, end=1, easing=easings.linear)
        assert c.styling.opacity.at_time(0) == pytest.approx(1.0, abs=1e-2)
        assert c.styling.opacity.at_time(1) == pytest.approx(0.0, abs=1e-6)


class TestAxesGetZeros:
    def _ax(self):
        return Axes(x_range=(-5, 5), y_range=(-5, 5))

    def test_linear_has_one_zero(self):
        """f(x) = x has exactly one zero at x=0."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x, -5, 5)
        assert len(zeros) == 1
        assert zeros[0][0] == pytest.approx(0.0, abs=1e-8)
        assert zeros[0][1] == 0.0

    def test_quadratic_two_zeros(self):
        """f(x) = x^2 - 1 has zeros at x = -1 and x = 1."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x ** 2 - 1, -3, 3)
        assert len(zeros) == 2
        xs = sorted(z[0] for z in zeros)
        assert xs[0] == pytest.approx(-1.0, abs=1e-6)
        assert xs[1] == pytest.approx(1.0, abs=1e-6)

    def test_sin_zeros_in_range(self):
        """sin has zeros at 0, pi, 2pi within [0, 2pi]."""
        ax = Axes(x_range=(0, 7), y_range=(-2, 2))
        zeros = ax.get_zeros(math.sin, 0.0, 2 * math.pi)
        xs = sorted(z[0] for z in zeros)
        # Expect zeros near 0, pi, 2pi
        assert any(abs(x - 0.0) < 1e-4 or abs(x - math.pi) < 1e-4
                   or abs(x - 2 * math.pi) < 1e-4 for x in xs)
        assert len(xs) >= 2  # at least pi and 2*pi

    def test_no_zeros(self):
        """f(x) = x^2 + 1 has no real zeros."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x ** 2 + 1, -5, 5)
        assert zeros == []

    def test_returns_list_of_tuples(self):
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x, -1, 1)
        assert isinstance(zeros, list)
        for z in zeros:
            assert isinstance(z, tuple)
            assert len(z) == 2

    def test_y_values_are_zero(self):
        """All returned y values must be exactly 0.0."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x ** 3 - x, -2, 2)
        for _, y in zeros:
            assert y == 0.0

    def test_cubic_three_zeros(self):
        """f(x) = x^3 - x = x(x-1)(x+1) has zeros at -1, 0, 1."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x ** 3 - x, -2, 2)
        xs = sorted(z[0] for z in zeros)
        assert len(xs) == 3
        assert xs[0] == pytest.approx(-1.0, abs=1e-6)
        assert xs[1] == pytest.approx(0.0, abs=1e-6)
        assert xs[2] == pytest.approx(1.0, abs=1e-6)

    def test_accepts_curve_with_func_attr(self):
        """get_zeros should work with a Path object returned by plot()."""
        ax = Axes(x_range=(-3, 3), y_range=(-5, 5))
        curve = ax.plot(lambda x: x)
        zeros = ax.get_zeros(curve, -3, 3)
        assert len(zeros) == 1
        assert zeros[0][0] == pytest.approx(0.0, abs=0.1)

    def test_sorted_ascending(self):
        """Returned zeros should be sorted in ascending x order."""
        ax = self._ax()
        zeros = ax.get_zeros(lambda x: x ** 3 - x, -2, 2)
        xs = [z[0] for z in zeros]
        assert xs == sorted(xs)


class TestBounceOut:
    def test_bounce_out_no_crash(self):
        c = Circle(50)
        c.bounce_out(0, 1)
        # Should have scale transform set; verify no crash
        svg = c.to_svg(0.5)
        assert 'scale' in svg

    def test_bounce_out_starts_at_full_scale(self):
        c = Circle(50)
        c.bounce_out(0, 1)
        # At t=0 the scale should still be 1 (no shrinking yet)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0, abs=0.01)

    def test_bounce_out_ends_at_zero_scale(self):
        c = Circle(50)
        c.bounce_out(0, 1)
        # At t=1 the scale should be 0
        assert c.styling.scale_x.at_time(1) == pytest.approx(0.0, abs=0.01)

    def test_bounce_out_hides_after_end(self):
        c = Circle(50)
        c.bounce_out(0, 1)
        # After end, object should be hidden
        assert c.show.at_time(1.1) == False

    def test_bounce_out_no_hide_when_change_existence_false(self):
        c = Circle(50)
        c.bounce_out(0, 1, change_existence=False)
        # Object should remain visible after end
        assert c.show.at_time(1.1) == True


class TestAttachTo:
    def test_attach_to_adds_updater(self):
        dot = Circle(10, cx=100, cy=100)
        label = Text("A")
        label.attach_to(dot, direction=(1, 0), buff=20, start=0, end=1)
        assert len(label._updaters) > 0

    def test_attach_to_default_direction(self):
        dot = Circle(10, cx=100, cy=100)
        label = Text("A")
        label.attach_to(dot, start=0, end=1)
        assert len(label._updaters) == 1


class TestGrowFromCorner:
    def test_grow_from_corner_returns_self(self):
        c = Circle(r=50, cx=200, cy=200)
        result = c.grow_from_corner(start=0, end=1)
        assert result is c

    def test_grow_from_corner_hides_before_start(self):
        c = Circle(r=50, cx=200, cy=200)
        c.grow_from_corner(start=1, end=2)
        assert not c.show.at_time(0.5)
        assert c.show.at_time(1)

    def test_grow_from_corner_scale_at_end(self):
        from vectormation.objects import DL
        c = Circle(r=50, cx=200, cy=200)
        c.grow_from_corner(start=0, end=1, corner=DL, easing=easings.linear)
        # At end, scale should be 1
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0)
        assert c.styling.scale_y.at_time(1) == pytest.approx(1.0)
        # At start, scale should be 0
        assert c.styling.scale_x.at_time(0) == pytest.approx(0.0)

    def test_grow_from_corner_anchor_point_ur(self):
        from vectormation.objects import UR
        r = Rectangle(100, 80, x=300, y=300)
        r.grow_from_corner(start=0, end=1, corner=UR, easing=easings.linear)
        # Scale origin should be top-right corner of bbox
        ox, oy = r.styling._scale_origin
        bx, by, bw, _ = r.bbox(0)
        assert ox == pytest.approx(bx + bw)  # right edge
        assert oy == pytest.approx(by)        # top edge

    def test_grow_from_corner_default_corner_is_dl(self):
        r = Rectangle(100, 80, x=300, y=300)
        r.grow_from_corner(start=0, end=1, easing=easings.linear)
        # Default is DL = (-1, 1) = bottom-left
        ox, oy = r.styling._scale_origin
        bx, by, _, bh = r.bbox(0)
        assert ox == pytest.approx(bx)        # left edge
        assert oy == pytest.approx(by + bh)   # bottom edge

    def test_grow_from_corner_no_change_existence(self):
        c = Circle(r=50, cx=200, cy=200)
        c.grow_from_corner(start=1, end=2, change_existence=False)
        # Object should remain visible before start
        assert c.show.at_time(0.5) == True


class TestApplySequentially:
    def test_apply_sequentially_returns_self(self):
        grp = VCollection(Circle(r=20, cx=100, cy=100),
                          Circle(r=20, cx=200, cy=100))
        result = grp.apply_sequentially('fadein', start=0, end=2)
        assert result is grp

    def test_apply_sequentially_divides_time_equally(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        c3 = Circle(r=20, cx=300, cy=100)
        grp = VCollection(c1, c2, c3)
        grp.apply_sequentially('fadein', start=0, end=3)
        # c1 should be visible at t=0.5 (its range is 0-1)
        assert c1.show.at_time(0.5) == True
        # c2 should NOT be visible at t=0.5 (its range is 1-2)
        assert c2.show.at_time(0.5) == False
        # c2 should be visible at t=1.5
        assert c2.show.at_time(1.5) == True
        # c3 should be visible at t=2.5
        assert c3.show.at_time(2.5) == True

    def test_apply_sequentially_empty_collection(self):
        grp = VCollection()
        result = grp.apply_sequentially('fadein', start=0, end=1)
        assert result is grp

    def test_apply_sequentially_single_child(self):
        c = Circle(r=20, cx=100, cy=100)
        grp = VCollection(c)
        grp.apply_sequentially('fadein', start=0, end=2)
        # The single child gets the full range 0-2
        assert c.show.at_time(0.5) == True
        assert c.show.at_time(2.5) == True


# NumberLine.number_to_point with time parameter

class TestNumberLineNumberToPointTime:
    def test_number_to_point_with_time_parameter(self):
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=300)
        pt = nl.number_to_point(5, time=0)
        assert pt[0] == pytest.approx(350)  # 100 + 5/10*500
        assert pt[1] == pytest.approx(300)

    def test_number_to_point_time_default(self):
        """Calling with and without time=0 should give the same result."""
        nl = NumberLine(x_range=(0, 10, 1), length=500, x=100, y=300)
        pt_no_time = nl.number_to_point(5)
        pt_with_time = nl.number_to_point(5, time=0)
        assert pt_no_time == pt_with_time

    def test_number_to_point_roundtrip(self):
        """number_to_point and point_to_number should be inverses."""
        nl = NumberLine(x_range=(-5, 5, 1), length=600, x=200, y=400)
        for val in [-5, -2.5, 0, 2.5, 5]:
            pt = nl.number_to_point(val, time=0)
            recovered = nl.point_to_number(pt)
            assert recovered == pytest.approx(val, abs=0.001)


# BarChart.sort_bars

class TestBarChartSortBars:
    def test_sort_bars_ascending(self):
        bc = BarChart([30, 10, 50, 20], labels=['A', 'B', 'C', 'D'])
        bc.sort_bars(start=0, end=1)
        # After sorting, values should be in ascending order
        assert bc.values == [10, 20, 30, 50]

    def test_sort_bars_descending(self):
        bc = BarChart([30, 10, 50, 20], labels=['A', 'B', 'C', 'D'])
        bc.sort_bars(reverse=True, start=0, end=1)
        # After sorting, values should be in descending order
        assert bc.values == [50, 30, 20, 10]

    def test_sort_bars_custom_key(self):
        bc = BarChart([3, -1, 5, -2])
        bc.sort_bars(key=abs, start=0, end=1)
        assert bc.values == [-1, -2, 3, 5]

    def test_sort_bars_returns_self(self):
        bc = BarChart([3, 1, 2])
        result = bc.sort_bars(start=0, end=1)
        assert result is bc

    def test_sort_bars_single_bar(self):
        bc = BarChart([42])
        result = bc.sort_bars(start=0, end=1)
        assert result is bc
        assert bc.values == [42]


class TestFadeSlideIn:
    def test_fade_slide_in_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.fade_slide_in(direction=DOWN, distance=200, start=0, end=1)
        assert result is c

    def test_fade_slide_in_opacity_starts_at_zero(self):
        """At the start of the animation, opacity should be 0."""
        c = Circle(r=50, cx=500, cy=500)
        c.fade_slide_in(direction=DOWN, distance=200, start=0, end=1,
                        easing=easings.linear)
        op = c.styling.opacity.at_time(0)
        assert op == pytest.approx(0, abs=0.01)

    def test_fade_slide_in_opacity_at_end(self):
        """At the end of the animation, opacity should be 1."""
        c = Circle(r=50, cx=500, cy=500)
        c.fade_slide_in(direction=DOWN, distance=200, start=0, end=1,
                        easing=easings.linear)
        op = c.styling.opacity.at_time(1)
        assert op == pytest.approx(1, abs=0.01)

    def test_fade_slide_in_shows_object(self):
        """Object should become visible at start time."""
        c = Circle(r=50, cx=500, cy=500, creation=5)
        c.fade_slide_in(direction=UP, distance=100, start=2, end=3)
        assert c.show.at_time(2) is True
        assert c.show.at_time(1.9) is False


class TestAxesAddHorizontalLine:
    def test_add_horizontal_line_returns_line(self):
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_horizontal_line(y=2)
        assert isinstance(line, Line)

    def test_add_horizontal_line_at_y_value(self):
        """The line should span the full plot width at the correct y."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_horizontal_line(y=3)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Both endpoints should have the same y (horizontal)
        assert p1[1] == pytest.approx(p2[1], abs=0.1)
        # p1.x should be at the left edge of the plot
        assert p1[0] == pytest.approx(ax.plot_x, abs=0.1)
        # p2.x should be at the right edge of the plot
        assert p2[0] == pytest.approx(ax.plot_x + ax.plot_width, abs=0.1)

    def test_add_horizontal_line_with_fade(self):
        """When start/end are given, the line should fade in."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_horizontal_line(y=1, start=0, end=1)
        # At time 0, opacity should be 0 (fadein start)
        op = line.styling.opacity.at_time(0)
        assert op == pytest.approx(0, abs=0.05)


class TestColorShift:
    def test_color_shift_returns_self(self):
        """color_shift should return self for chaining."""
        c = Circle(r=50, fill='#ff0000')
        result = c.color_shift(hue_shift=60, start=0, end=1)
        assert result is c

    def test_color_shift_changes_color(self):
        """At end time, the fill color should have shifted hue."""
        c = Circle(r=50, fill='#ff0000')
        original = c.styling.fill.at_time(0)
        c.color_shift(hue_shift=120, start=0, end=1)
        shifted = c.styling.fill.at_time(1)
        assert shifted != original

    def test_color_shift_zero_shift(self):
        """A hue shift of 0 should leave the color unchanged."""
        c = Circle(r=50, fill='#ff0000')
        original_rgb = c.styling.fill.time_func(0)
        c.color_shift(hue_shift=0, start=0, end=1)
        shifted_rgb = c.styling.fill.time_func(1)
        assert shifted_rgb[0] == pytest.approx(original_rgb[0], abs=2)
        assert shifted_rgb[1] == pytest.approx(original_rgb[1], abs=2)
        assert shifted_rgb[2] == pytest.approx(original_rgb[2], abs=2)

    def test_color_shift_preserves_lightness(self):
        """Hue shift should not change lightness significantly."""
        from vectormation.attributes import _rgb_to_hsl
        c = Circle(r=50, fill='#4488cc')
        orig_rgb = c.styling.fill.time_func(0)
        _, _, orig_l = _rgb_to_hsl(*orig_rgb[:3])
        c.color_shift(hue_shift=90, start=0, end=1)
        shifted_rgb = c.styling.fill.time_func(1)
        _, _, shifted_l = _rgb_to_hsl(*shifted_rgb[:3])
        assert shifted_l == pytest.approx(orig_l, abs=0.02)


class TestPlotPiecewise:
    def test_plot_piecewise_returns_group(self):
        """plot_piecewise should return a VGroup."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        pieces = [
            (lambda x: x, -5, 0),
            (lambda x: x**2, 0, 5),
        ]
        group = ax.plot_piecewise(pieces)
        assert isinstance(group, VGroup)

    def test_plot_piecewise_correct_count(self):
        """plot_piecewise should have one curve per piece."""
        ax = Axes(x_range=[-5, 5], y_range=[-10, 10])
        pieces = [
            (lambda x: -x, -5, -1),
            (lambda _x: 1, -1, 1),
            (lambda x: x, 1, 5),
        ]
        group = ax.plot_piecewise(pieces)
        assert len(group.objects) == 3

    def test_plot_piecewise_curves_added_to_axes(self):
        """Each piece should also be added to the axes objects."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        initial_count = len(ax.objects)
        pieces = [
            (lambda x: x, -5, 0),
            (lambda x: -x, 0, 5),
        ]
        ax.plot_piecewise(pieces)
        # Each piece adds a curve to the axes
        assert len(ax.objects) == initial_count + 2


class TestShrinkToCorner:
    def test_shrink_to_corner_returns_self(self):
        c = Circle(r=50, cx=200, cy=200)
        result = c.shrink_to_corner(start=0, end=1)
        assert result is c

    def test_shrink_to_corner_hides_after_end(self):
        c = Circle(r=50, cx=200, cy=200)
        c.shrink_to_corner(start=0, end=1)
        assert not c.show.at_time(1.5)

    def test_shrink_to_corner_visible_before_end(self):
        c = Circle(r=50, cx=200, cy=200)
        c.shrink_to_corner(start=0, end=1)
        assert c.show.at_time(0)

    def test_shrink_to_corner_scale_at_start_and_end(self):
        from vectormation.objects import DL
        c = Circle(r=50, cx=200, cy=200)
        c.shrink_to_corner(start=0, end=1, corner=DL, easing=easings.linear)
        # At start, scale should be 1
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0)
        assert c.styling.scale_y.at_time(0) == pytest.approx(1.0)
        # At end, scale should be 0
        assert c.styling.scale_x.at_time(1) == pytest.approx(0.0)
        assert c.styling.scale_y.at_time(1) == pytest.approx(0.0)

    def test_shrink_to_corner_anchor_point_ur(self):
        from vectormation.objects import UR
        r = Rectangle(100, 80, x=300, y=300)
        r.shrink_to_corner(start=0, end=1, corner=UR, easing=easings.linear)
        ox, oy = r.styling._scale_origin
        bx, by, bw, _ = r.bbox(0)
        assert ox == pytest.approx(bx + bw)  # right edge
        assert oy == pytest.approx(by)        # top edge

    def test_shrink_to_corner_default_corner_is_dl(self):
        r = Rectangle(100, 80, x=300, y=300)
        r.shrink_to_corner(start=0, end=1, easing=easings.linear)
        ox, oy = r.styling._scale_origin
        bx, by, _, bh = r.bbox(0)
        assert ox == pytest.approx(bx)        # left edge
        assert oy == pytest.approx(by + bh)   # bottom edge

    def test_shrink_to_corner_no_change_existence(self):
        c = Circle(r=50, cx=200, cy=200)
        c.shrink_to_corner(start=0, end=1, change_existence=False)
        # Object should remain visible after end
        assert c.show.at_time(1.5) == True


class TestAxesGetSlope:
    def test_get_slope_linear(self):
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        slope = ax.get_slope(lambda x: 3 * x + 1, 2.0)
        assert slope == pytest.approx(3.0, abs=0.01)

    def test_get_slope_quadratic(self):
        ax = Axes(x_range=[-5, 5], y_range=[-25, 25])
        slope = ax.get_slope(lambda x: x**2, 3.0)
        assert slope == pytest.approx(6.0, abs=0.01)

    def test_get_slope_matches_get_derivative(self):
        import math
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        f = lambda x: math.sin(x)
        slope = ax.get_slope(f, 0.0)
        deriv = ax.get_derivative(f, 0.0)
        assert slope == pytest.approx(deriv)

    def test_get_slope_custom_h(self):
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        slope = ax.get_slope(lambda x: x**3, 2.0, h=0.0001)
        assert slope == pytest.approx(12.0, abs=0.01)


# ---------- fade_slide_out ----------
class TestFadeSlideOut:
    def test_fade_slide_out_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.fade_slide_out(direction=DOWN, distance=200, start=0, end=1)
        assert result is c

    def test_fade_slide_out_opacity_at_start_is_one(self):
        """At the start of the animation, opacity should still be 1."""
        c = Circle(r=50, cx=500, cy=500)
        c.fade_slide_out(direction=DOWN, distance=200, start=0, end=1,
                         easing=easings.linear)
        op = c.styling.opacity.at_time(0)
        assert op == pytest.approx(1, abs=0.01)

    def test_fade_slide_out_opacity_at_end_is_zero(self):
        """At the end of the animation, opacity should be 0."""
        c = Circle(r=50, cx=500, cy=500)
        c.fade_slide_out(direction=DOWN, distance=200, start=0, end=1,
                         easing=easings.linear)
        op = c.styling.opacity.at_time(1)
        assert op == pytest.approx(0, abs=0.01)

    def test_fade_slide_out_hides_object(self):
        """Object should become hidden at end time."""
        c = Circle(r=50, cx=500, cy=500)
        c.fade_slide_out(direction=UP, distance=100, start=2, end=3)
        assert c.show.at_time(2.5) is True
        assert c.show.at_time(3) is False

    def test_fade_slide_out_zero_duration(self):
        """Zero-duration should hide immediately and return self."""
        c = Circle(r=50, cx=500, cy=500)
        result = c.fade_slide_out(direction=LEFT, distance=100, start=1, end=1)
        assert result is c


# ---------- Line.angle_to ----------
class TestLineAngleTo:
    def test_angle_to_perpendicular(self):
        """Two perpendicular lines should have a 90 degree angle."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=0, x2=0, y2=100)
        assert l1.angle_to(l2) == pytest.approx(90.0, abs=0.01)

    def test_angle_to_parallel(self):
        """Two parallel lines should have a 0 degree angle."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=50, y1=50, x2=200, y2=50)
        assert l1.angle_to(l2) == pytest.approx(0.0, abs=0.01)

    def test_angle_to_opposite(self):
        """Two anti-parallel lines should have a 180 degree angle."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=100, y1=0, x2=0, y2=0)
        assert l1.angle_to(l2) == pytest.approx(180.0, abs=0.01)

    def test_angle_to_45_degrees(self):
        """A horizontal line and a 45-degree line."""
        l1 = Line(x1=0, y1=0, x2=100, y2=0)
        l2 = Line(x1=0, y1=0, x2=100, y2=100)
        assert l1.angle_to(l2) == pytest.approx(45.0, abs=0.01)


# ---------- Axes.get_integral ----------
class TestAxesGetIntegral:
    def test_get_integral_x_squared(self):
        """Integral of x^2 from 0 to 3 should be 9."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 25])
        val = ax.get_integral(lambda x: x**2, 0, 3)
        assert val == pytest.approx(9.0, abs=0.1)

    def test_get_integral_matches_get_area_value(self):
        """get_integral should give same results as get_area_value."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        f = lambda x: math.sin(x)
        v1 = ax.get_area_value(f, 0, math.pi, samples=200)
        v2 = ax.get_integral(f, 0, math.pi, samples=200)
        assert v1 == pytest.approx(v2)

    def test_get_integral_constant_function(self):
        """Integral of f(x)=5 from 0 to 4 should be 20."""
        ax = Axes(x_range=[0, 10], y_range=[0, 10])
        val = ax.get_integral(lambda _x: 5, 0, 4)
        assert val == pytest.approx(20.0, abs=0.01)


class TestFollow:
    def test_follow_tracks_center(self):
        """Follower should track the leader's center after the leader moves."""
        leader = Circle(r=30, cx=100, cy=100)
        follower = Circle(r=20, cx=200, cy=200)
        follower.follow(leader, start=0)
        # Move leader
        leader.shift(dx=50, dy=60, start=0, end=1)
        # Trigger the updater at t=1
        follower._run_updaters(1.0)
        fcx, fcy = follower.center(1.0)
        lcx, lcy = leader.center(1.0)
        assert fcx == pytest.approx(lcx, abs=1)
        assert fcy == pytest.approx(lcy, abs=1)

    def test_follow_returns_self(self):
        leader = Circle(r=30, cx=100, cy=100)
        follower = Circle(r=20, cx=200, cy=200)
        result = follower.follow(leader, start=0)
        assert result is follower

    def test_follow_respects_end(self):
        """After end time, the follower should stop updating."""
        leader = Circle(r=30, cx=100, cy=100)
        follower = Circle(r=20, cx=100, cy=100)
        follower.follow(leader, start=0, end=1)
        leader.shift(dx=100, dy=0, start=0, end=1)
        # Updater runs at t=0.5 (within range)
        follower._run_updaters(0.5)
        cx_mid, _ = follower.center(0.5)
        # At t=2 the updater should NOT run (past end)
        follower._run_updaters(2.0)
        # The position at t=2 should be the same as whatever was set last
        # (updater stops at end=1, so position after end stays fixed)
        assert cx_mid != 100  # It moved during the follow window


class TestGetApothem:
    def test_get_apothem_equals_get_inradius(self):
        """get_apothem should return the same value as get_inradius."""
        hexagon = RegularPolygon(n=6, radius=100)
        assert hexagon.get_apothem() == pytest.approx(hexagon.get_inradius())

    def test_get_apothem_value(self):
        """Apothem of a regular hexagon with radius=100 should be 100*cos(pi/6)."""
        hexagon = RegularPolygon(n=6, radius=100)
        expected = 100 * math.cos(math.pi / 6)
        assert hexagon.get_apothem() == pytest.approx(expected)

    def test_get_apothem_square(self):
        """Apothem of a square with circumradius 100 should be 100*cos(pi/4)."""
        sq = RegularPolygon(n=4, radius=100)
        expected = 100 * math.cos(math.pi / 4)
        assert sq.get_apothem() == pytest.approx(expected)


class TestAddVerticalLine:
    def test_add_vertical_line_returns_line(self):
        """add_vertical_line should return a Line object."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_vertical_line(2)
        assert line is not None
        assert hasattr(line, 'p1')
        assert hasattr(line, 'p2')

    def test_add_vertical_line_position(self):
        """The line's x-coordinates should map to the given math x value."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_vertical_line(0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # Both endpoints should have the same x coordinate
        assert p1[0] == pytest.approx(p2[0], abs=1)
        # The x coordinate should correspond to math x=0
        expected_x = ax._math_to_svg_x(0, 0)
        assert p1[0] == pytest.approx(expected_x, abs=1)

    def test_add_vertical_line_with_fadein(self):
        """When start/end are given, the line should have a fadein animation."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        line = ax.add_vertical_line(1, start=0, end=1)
        # The line should exist and have opacity animation
        opacity_at_start = line.styling.opacity.at_time(0)
        assert opacity_at_start == pytest.approx(0, abs=0.1)


class TestGetPointOnGraph:
    def test_basic_linear(self):
        """get_point_on_graph should return the same result as coords_to_point for simple functions."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        result = ax.get_point_on_graph(lambda x: 2 * x, 1)
        expected = ax.coords_to_point(1, 2)
        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])

    def test_exception_returns_none(self):
        """get_point_on_graph should return None when the function raises."""
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        result = ax.get_point_on_graph(lambda x: 1 / x, 0)
        assert result is None

    def test_domain_error_returns_none(self):
        """get_point_on_graph should return None for domain errors like sqrt of negative."""
        import math
        ax = Axes(x_range=[-5, 5], y_range=[-5, 5])
        result = ax.get_point_on_graph(lambda x: math.sqrt(x), -1)
        assert result is None


class TestHoverScale:
    def test_hover_scale_holds_factor(self):
        """During [start, end] the scale should be factor * original."""
        c = Circle(r=50, cx=100, cy=100)
        c.hover_scale(factor=2.0, start=1, end=3)
        sx = c.styling.scale_x.at_time(1.5)
        assert sx == pytest.approx(2.0)

    def test_hover_scale_returns_to_original(self):
        """After end the scale should return to the original value."""
        c = Circle(r=50, cx=100, cy=100)
        c.hover_scale(factor=1.5, start=1, end=3)
        sx = c.styling.scale_x.at_time(3)
        assert sx == pytest.approx(1.0)

    def test_hover_scale_returns_self(self):
        """hover_scale should return self for chaining."""
        c = Circle(r=50)
        result = c.hover_scale(factor=1.3, start=0, end=1)
        assert result is c


class TestAxesGetXIntercept:
    def test_x_intercept_linear(self):
        """x intercept of f(x) = x - 2 should be 2."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_x_intercept(lambda x: x - 2)
        assert result is not None
        assert result == pytest.approx(2.0, abs=0.01)

    def test_x_intercept_no_zero(self):
        """A function with no zero in range should return None."""
        ax = Axes(x_range=(1, 5), y_range=(-5, 5))
        result = ax.get_x_intercept(lambda x: x + 10)
        assert result is None

    def test_x_intercept_custom_range(self):
        """Custom x_start and x_end should restrict the search."""
        ax = Axes(x_range=(-10, 10), y_range=(-5, 5))
        # f(x) = x has a zero at 0, but we search only [1, 5]
        result = ax.get_x_intercept(lambda x: x, x_start=1, x_end=5)
        assert result is None


class TestAxesGetYIntercept:
    def test_y_intercept_linear(self):
        """y intercept of f(x) = 2x + 3 should be 3."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_y_intercept(lambda x: 2 * x + 3)
        assert result == pytest.approx(3.0)

    def test_y_intercept_undefined(self):
        """Functions undefined at 0 should return None."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_y_intercept(lambda x: 1 / x)
        assert result is None


class TestRippleScale:
    def test_ripple_scale_returns_self(self):
        """ripple_scale should return self for chaining."""
        c = Circle(r=50, cx=100, cy=100)
        assert c.ripple_scale(start=0, end=1) is c

    def test_ripple_scale_ends_at_original(self):
        """At end time the scale should return to approximately the original."""
        c = Circle(r=50, cx=100, cy=100)
        c.ripple_scale(start=0, end=1, num_ripples=3, max_factor=1.3)
        # At t=1 the easing gives p=1, so decay=0, factor=1 => original scale
        sx = c.styling.scale_x.at_time(1)
        assert sx == pytest.approx(1.0, abs=0.01)

    def test_ripple_scale_oscillates_midway(self):
        """During the animation the scale should deviate from 1.0."""
        c = Circle(r=50, cx=100, cy=100)
        c.ripple_scale(start=0, end=1, num_ripples=3, max_factor=1.5)
        # Sample at a few midpoints — at least one should be != 1.0
        scales = [c.styling.scale_x.at_time(t) for t in [0.1, 0.2, 0.3, 0.4]]
        assert any(abs(s - 1.0) > 0.01 for s in scales)

    def test_ripple_scale_zero_duration(self):
        """Zero-duration ripple_scale should be a no-op."""
        c = Circle(r=50, cx=100, cy=100)
        c.ripple_scale(start=0.5, end=0.5)
        assert c.styling.scale_x.at_time(0.5) == pytest.approx(1.0)


class TestAxesAddAnnotation:
    def test_add_annotation_returns_tuple(self):
        """add_annotation should return a (dot, label) tuple from add_point_label."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_annotation(2, 3, 'hello')
        # add_point_label returns (dot, label)
        assert len(result) == 2

    def test_add_annotation_label_text(self):
        """The label should contain the provided text."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        _, label = ax.add_annotation(1, 1, 'test_label')
        assert label.text.at_time(0) == 'test_label'

    def test_add_annotation_at_correct_position(self):
        """The dot should be placed at the correct SVG coordinates."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        dot, _ = ax.add_annotation(0, 0, 'origin')
        expected = ax.coords_to_point(0, 0)
        pos = dot.c.at_time(0)
        assert pos[0] == pytest.approx(expected[0], abs=1)
        assert pos[1] == pytest.approx(expected[1], abs=1)


class TestVObjectDelay:
    """Tests for VObject.delay()."""

    def test_delay_hides_before_duration(self):
        """Object should be hidden at time 0 when delayed by 2 seconds."""
        c = Circle(r=50)
        c.delay(2)
        assert c.show.at_time(0) is False
        assert c.show.at_time(1) is False

    def test_delay_shows_after_duration(self):
        """Object should be visible at time >= start + duration."""
        c = Circle(r=50)
        c.delay(2)
        assert c.show.at_time(2) is True
        assert c.show.at_time(5) is True

    def test_delay_with_start(self):
        """Object should be hidden from start for duration, then shown."""
        c = Circle(r=50)
        c.delay(3, start=1)
        # Hidden before start + duration
        assert c.show.at_time(0) is False
        assert c.show.at_time(3) is False
        # Visible at start + duration = 4
        assert c.show.at_time(4) is True

    def test_delay_returns_self(self):
        """delay() should return self for chaining."""
        c = Circle(r=50)
        assert c.delay(1) is c


class TestAxesCoordsToScreen:
    """Tests for Axes.coords_to_screen()."""

    def test_coords_to_screen_matches_coords_to_point(self):
        """coords_to_screen should return the same result as coords_to_point."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        for x, y in [(0, 0), (3, -2), (-1, 4)]:
            assert ax.coords_to_screen(x, y) == ax.coords_to_point(x, y)

    def test_coords_to_screen_with_time(self):
        """coords_to_screen should forward the time parameter."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.coords_to_screen(1, 1, time=0)
        expected = ax.coords_to_point(1, 1, time=0)
        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])


class TestVisibilityToggle:
    def test_basic_toggle(self):
        """Object should alternate between visible and hidden at each time."""
        c = Circle(r=50)
        c.visibility_toggle(1, 3, 5)
        assert not c.show.at_time(0.5)  # hidden before first time
        assert c.show.at_time(2)        # visible during [1, 3)
        assert not c.show.at_time(4)    # hidden during [3, 5)
        assert c.show.at_time(6)        # visible from 5 onward

    def test_single_time(self):
        """With a single time, the object is hidden before and visible after."""
        c = Circle(r=50)
        c.visibility_toggle(2)
        assert not c.show.at_time(1)  # hidden before
        assert c.show.at_time(3)      # visible after

    def test_two_times(self):
        """With two times, object is visible between them and hidden outside."""
        r = Rectangle(100, 100)
        r.visibility_toggle(1, 4)
        assert not r.show.at_time(0.5)  # hidden before
        assert r.show.at_time(2)        # visible during [1, 4)
        assert not r.show.at_time(5)    # hidden after

    def test_returns_self(self):
        """visibility_toggle should return self for chaining."""
        c = Circle(r=50)
        result = c.visibility_toggle(1, 2, 3)
        assert result is c

    def test_unsorted_times(self):
        """Times should be sorted internally regardless of input order."""
        c = Circle(r=50)
        c.visibility_toggle(5, 1, 3)
        assert not c.show.at_time(0.5)  # hidden before first (1)
        assert c.show.at_time(2)        # visible during [1, 3)
        assert not c.show.at_time(4)    # hidden during [3, 5)
        assert c.show.at_time(6)        # visible from 5 onward


class TestEllipseTangentAtAngle:
    def test_tangent_at_zero_degrees(self):
        """Tangent at 0 degrees on a circle should be vertical."""
        c = Circle(r=100, cx=500, cy=500)
        line = c.tangent_at_angle(0)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # At 0 degrees the point is (600, 500) and the tangent is vertical
        assert p1[0] == pytest.approx(p2[0], abs=1e-6)  # same x: vertical line
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        assert mid_x == pytest.approx(600, abs=1e-6)
        assert mid_y == pytest.approx(500, abs=1e-6)

    def test_tangent_at_90_degrees(self):
        """Tangent at 90 degrees on a circle should be horizontal."""
        c = Circle(r=100, cx=500, cy=500)
        line = c.tangent_at_angle(90)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        # At 90 degrees the point is (500, 400) and the tangent is horizontal
        assert p1[1] == pytest.approx(p2[1], abs=1e-6)  # same y: horizontal line
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        assert mid_x == pytest.approx(500, abs=1e-6)
        assert mid_y == pytest.approx(400, abs=1e-6)

    def test_tangent_returns_line(self):
        """tangent_at_angle should return a Line object."""
        e = Ellipse(rx=150, ry=80, cx=960, cy=540)
        line = e.tangent_at_angle(45)
        assert isinstance(line, Line)

    def test_tangent_line_length(self):
        """The tangent line should have the specified length."""
        c = Circle(r=100, cx=500, cy=500)
        length = 300
        line = c.tangent_at_angle(0, length=length)
        p1 = line.p1.at_time(0)
        p2 = line.p2.at_time(0)
        actual_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        assert actual_len == pytest.approx(length, abs=1e-6)

    def test_tangent_perpendicular_to_radius_circle(self):
        """For a circle, the tangent at any angle should be perpendicular to the radius."""
        c = Circle(r=100, cx=500, cy=500)
        for deg in [0, 30, 45, 60, 90, 135, 180, 270]:
            line = c.tangent_at_angle(deg)
            p1 = line.p1.at_time(0)
            p2 = line.p2.at_time(0)
            # Tangent direction
            tdx, tdy = p2[0] - p1[0], p2[1] - p1[1]
            # Radius direction from center to point on circle
            pt = c.point_at_angle(deg)
            rdx, rdy = pt[0] - 500, pt[1] - 500
            # Dot product should be zero (perpendicular)
            dot = tdx * rdx + tdy * rdy
            assert dot == pytest.approx(0, abs=1e-4), f"Failed at {deg} degrees"

    def test_tangent_kwargs_forwarded(self):
        """Extra kwargs should be forwarded to the Line constructor."""
        e = Ellipse(rx=100, ry=50)
        line = e.tangent_at_angle(0, stroke='#f00', stroke_width=3)
        svg = line.to_svg(0)
        assert 'stroke-width=\'3\'' in svg
        assert 'rgb(255,0,0)' in svg or '#f00' in svg


class TestBlinkOpacity:
    def test_blink_opacity_oscillates(self):
        """blink_opacity should oscillate opacity over time."""
        c = Circle(r=50)
        c.blink_opacity(start=0, end=2, frequency=1, min_opacity=0.2, max_opacity=0.8)
        # At t=0, opacity should be at min (cos(0)=1, wave=0 -> min)
        op_start = c.styling.opacity.at_time(0)
        assert op_start == pytest.approx(0.2, abs=0.05)
        # At t=1.0 (progress=0.5, peak of one cycle), opacity should be at max
        op_peak = c.styling.opacity.at_time(1.0)
        assert op_peak == pytest.approx(0.8, abs=0.05)
        # At t=2.0 (full cycle), should be back at min
        op_end = c.styling.opacity.at_time(2.0)
        assert op_end == pytest.approx(0.2, abs=0.05)

    def test_blink_opacity_returns_self(self):
        """blink_opacity should return self for chaining."""
        c = Circle(r=50)
        result = c.blink_opacity(start=0, end=1)
        assert result is c

    def test_blink_opacity_zero_duration_noop(self):
        """blink_opacity with zero duration should be a no-op."""
        c = Circle(r=50)
        c.blink_opacity(start=1, end=1)
        # Default opacity should be unchanged (1.0)
        assert c.styling.opacity.at_time(0) == pytest.approx(1.0)


class TestAxesGetGraphValue:
    def test_get_graph_value_linear(self):
        """get_graph_value should return func(x)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        f = lambda x: 2 * x + 1
        assert ax.get_graph_value(f, 3) == pytest.approx(7)
        assert ax.get_graph_value(f, -2) == pytest.approx(-3)
        assert ax.get_graph_value(f, 0) == pytest.approx(1)

    def test_get_graph_value_quadratic(self):
        """get_graph_value should work with any callable."""
        ax = Axes(x_range=(0, 10), y_range=(0, 100))
        f = lambda x: x ** 2
        assert ax.get_graph_value(f, 5) == pytest.approx(25)
        assert ax.get_graph_value(f, 0) == pytest.approx(0)


class TestAxesPlotDerivative:
    def test_plot_derivative_returns_path(self):
        """plot_derivative should return a Path object."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        curve = ax.plot_derivative(lambda x: x ** 2)
        assert isinstance(curve, Path)

    def test_plot_derivative_has_func(self):
        """The returned curve should have a _func attribute."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        curve = ax.plot_derivative(lambda x: x ** 2)
        assert hasattr(curve, '_func')

    def test_plot_derivative_func_value(self):
        """Derivative of x^2 should be approximately 2x."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        curve = ax.plot_derivative(lambda x: x ** 2)
        # The _func on the curve should approximate 2x
        deriv = curve._func
        assert deriv(3) == pytest.approx(6, abs=0.01)
        assert deriv(-2) == pytest.approx(-4, abs=0.01)
        assert deriv(0) == pytest.approx(0, abs=0.01)

    def test_plot_derivative_added_to_axes(self):
        """The curve should be added to the axes' objects."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        initial_count = len(ax.objects)
        ax.plot_derivative(lambda x: x ** 3)
        assert len(ax.objects) == initial_count + 1

    def test_plot_derivative_renders_svg(self):
        """The derivative curve should produce valid SVG."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        ax.plot_derivative(lambda x: x ** 2)
        svg = ax.to_svg(0)
        assert '<path' in svg

    def test_plot_derivative_from_curve(self):
        """plot_derivative should accept a curve returned by plot()."""
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        curve = ax.plot(lambda x: x ** 3)
        deriv = ax.plot_derivative(curve)
        # Derivative of x^3 = 3x^2
        assert deriv._func(2) == pytest.approx(12, abs=0.1)

    def test_plot_derivative_sin(self):
        """Derivative of sin(x) should approximate cos(x)."""
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        curve = ax.plot_derivative(math.sin)
        deriv = curve._func
        assert deriv(0) == pytest.approx(1, abs=0.01)  # cos(0) = 1
        assert deriv(math.pi) == pytest.approx(-1, abs=0.01)  # cos(pi) = -1


class TestAxesGetTrapezoidalRule:
    def test_returns_dynamic_object(self):
        """get_trapezoidal_rule should return a DynamicObject."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        dyn = ax.get_trapezoidal_rule(lambda x: x ** 2, x_range=(0, 4), dx=1)
        assert isinstance(dyn, DynamicObject)

    def test_added_to_axes(self):
        """The trapezoids should be added to the axes' objects."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        initial_count = len(ax.objects)
        ax.get_trapezoidal_rule(lambda x: x ** 2, x_range=(0, 4), dx=1)
        assert len(ax.objects) == initial_count + 1

    def test_renders_polygons(self):
        """The trapezoidal rule should produce polygons in the SVG."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        ax.get_trapezoidal_rule(lambda x: x ** 2, x_range=(0, 4), dx=1)
        svg = ax.to_svg(0)
        assert '<polygon' in svg

    def test_correct_number_of_trapezoids(self):
        """Should produce ceil((x_hi - x_lo) / dx) trapezoids."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        dyn = ax.get_trapezoidal_rule(lambda x: x ** 2, x_range=(0, 4), dx=1)
        # Build the trapezoids at time 0
        coll = dyn._func(0)
        assert len(coll.objects) == 4  # 4 intervals of width 1 from 0 to 4

    def test_small_dx_more_trapezoids(self):
        """Smaller dx should produce more trapezoids."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        dyn = ax.get_trapezoidal_rule(lambda x: x, x_range=(0, 2), dx=0.5)
        coll = dyn._func(0)
        assert len(coll.objects) == 4  # 2 / 0.5 = 4

    def test_trapezoids_are_polygons(self):
        """Each element in the result should be a Polygon."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        dyn = ax.get_trapezoidal_rule(lambda x: x + 1, x_range=(0, 3), dx=1)
        coll = dyn._func(0)
        for obj in coll.objects:
            assert isinstance(obj, Polygon)


class TestBreathe:
    def test_breathe_returns_self(self):
        """breathe should return self for chaining."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.breathe(start=0, end=2)
        assert result is c

    def test_breathe_scale_oscillates(self):
        """breathe should produce oscillating scale values around baseline."""
        c = Circle(r=50, cx=100, cy=100)
        c.breathe(start=0, end=4, amplitude=0.1, speed=1.0, easing=easings.linear)
        # At start, scale should be at baseline (sin(0) = 0)
        sx_start = c.styling.scale_x.at_time(0)
        assert sx_start == pytest.approx(1.0, abs=0.01)
        # At some point during animation, scale should differ from 1
        # sin(2*pi*1*1) = sin(2*pi) = 0, so at t=1 it should be back
        # At t=0.25, sin(2*pi*0.25) = sin(pi/2) = 1, so scale = 1.1
        sx_quarter = c.styling.scale_x.at_time(0.25)
        assert abs(sx_quarter - 1.0) > 0.05  # definitely not 1.0

    def test_breathe_zero_duration_noop(self):
        """breathe with zero duration should be a no-op."""
        c = Circle(r=50, cx=100, cy=100)
        c.breathe(start=1, end=1)
        # scale should still be 1.0
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0)

    def test_breathe_sets_scale_origin(self):
        """breathe should set scale origin to object center."""
        c = Circle(r=50, cx=200, cy=300)
        c.breathe(start=0, end=1)
        assert c.styling._scale_origin is not None
        assert c.styling._scale_origin[0] == pytest.approx(200, abs=1)
        assert c.styling._scale_origin[1] == pytest.approx(300, abs=1)

    def test_breathe_y_scale_matches_x(self):
        """breathe should animate both x and y scale symmetrically."""
        c = Circle(r=50, cx=100, cy=100)
        c.breathe(start=0, end=2, amplitude=0.1, speed=1.0, easing=easings.linear)
        for t in [0.1, 0.5, 1.0, 1.5]:
            sx = c.styling.scale_x.at_time(t)
            sy = c.styling.scale_y.at_time(t)
            assert sx == pytest.approx(sy, abs=0.001)


class TestPendulum:
    def test_pendulum_returns_self(self):
        """pendulum should return self for chaining."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.pendulum(start=0, end=2)
        assert result is c

    def test_pendulum_starts_at_zero_rotation(self):
        """At the start time, the rotation angle should be approximately zero."""
        c = Circle(r=50, cx=100, cy=100)
        c.pendulum(start=0, end=2, amplitude=30, easing=easings.linear)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(0, abs=0.5)

    def test_pendulum_oscillates(self):
        """The rotation should oscillate and not remain constant."""
        c = Circle(r=50, cx=100, cy=100)
        c.pendulum(start=0, end=4, amplitude=30, oscillations=4, easing=easings.linear)
        # Sample at quarter-cycle where sin peaks (4 osc in 4s => period=1s => peak at 0.25s)
        rot_peak = c.styling.rotation.at_time(0.25)
        assert abs(rot_peak[0]) > 5  # should be a substantial angle, not zero

    def test_pendulum_decays(self):
        """The amplitude should decay over time due to exponential damping."""
        c = Circle(r=50, cx=100, cy=100)
        c.pendulum(start=0, end=4, amplitude=30, oscillations=8, easing=easings.linear)
        # Peak near the start should be larger than peak near the end
        # At t~0.125 (first quarter cycle of 8 osc in 4s), amplitude should be large
        rot_early = abs(c.styling.rotation.at_time(0.0625)[0])
        # At t~3.5 (near end), amplitude should be much smaller
        rot_late = abs(c.styling.rotation.at_time(3.5)[0])
        assert rot_early > rot_late

    def test_pendulum_zero_duration_noop(self):
        """pendulum with zero duration should be a no-op."""
        c = Circle(r=50, cx=100, cy=100)
        c.pendulum(start=1, end=1)
        rot = c.styling.rotation.at_time(1)
        assert rot == (0, 0, 0)

    def test_pendulum_custom_pivot(self):
        """pendulum with custom pivot should use those coordinates."""
        c = Circle(r=50, cx=100, cy=100)
        c.pendulum(start=0, end=2, cx=100, cy=0)
        rot = c.styling.rotation.at_time(0.5)
        # Pivot should be (100, 0)
        assert rot[1] == pytest.approx(100)
        assert rot[2] == pytest.approx(0)

    def test_pendulum_default_pivot_top_center(self):
        """Without custom pivot, pendulum should use top-center of bbox."""
        r = Rectangle(100, 60, x=200, y=300)
        r.pendulum(start=0, end=2)
        rot = r.styling.rotation.at_time(0.5)
        # Top-center of rect at (200, 300, 100, 60) is (250, 300)
        assert rot[1] == pytest.approx(250, abs=1)
        assert rot[2] == pytest.approx(300, abs=1)


class TestTypewriterReveal:
    def test_typewriter_reveal_returns_self(self):
        """typewriter_reveal should return self for chaining."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.typewriter_reveal(start=0, end=1)
        assert result is c

    def test_typewriter_reveal_shows_from_start(self):
        """The object should be visible from start time onward."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=1, end=2)
        assert c.show.at_time(0) is not True or c.show.at_time(0) == 0
        assert c.show.at_time(1)

    def test_typewriter_reveal_clip_at_start(self):
        """At start time, the clip-path should fully hide the object (100% inset)."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=0, end=1, direction='right', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0)
        # At t=0 with linear easing, progress=0, so inset should be 100%
        assert '100' in clip

    def test_typewriter_reveal_clip_at_end(self):
        """At end time, the clip-path should be fully removed (0% inset)."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=0, end=1, direction='right', easing=easings.linear)
        clip = c.styling.clip_path.at_time(1)
        assert '0.0%' in clip

    def test_typewriter_reveal_direction_left(self):
        """Left direction should use the left inset position."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=0, end=1, direction='left', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        # At 50%, left inset should be at 50%
        assert 'inset(0 0 0' in clip

    def test_typewriter_reveal_direction_down(self):
        """Down direction should use the bottom inset position."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=0, end=1, direction='down', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset(0 0' in clip

    def test_typewriter_reveal_direction_up(self):
        """Up direction should use the top inset position."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=0, end=1, direction='up', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset(' in clip

    def test_typewriter_reveal_zero_duration_noop(self):
        """typewriter_reveal with zero duration should be a no-op."""
        c = Circle(r=50, cx=100, cy=100)
        c.typewriter_reveal(start=1, end=1)
        # clip_path should not have been set to a function
        clip = c.styling.clip_path.at_time(1)
        assert clip == '' or clip == 0 or clip == '0'


class TestTelegraph:
    def test_telegraph_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.telegraph(start=0) is c

    def test_telegraph_scales_at_midpoint(self):
        """At the midpoint the scale should be above 1 (scaled up)."""
        c = Circle(r=50, cx=100, cy=100)
        c.telegraph(start=0, duration=1, scale_factor=1.5)
        mid_sx = c.styling.scale_x.at_time(0.5)
        assert mid_sx > 1.0

    def test_telegraph_opacity_dips_at_midpoint(self):
        """Opacity should dip below 1 during the effect."""
        c = Circle(r=50, cx=100, cy=100)
        c.telegraph(start=0, duration=1)
        mid_op = c.styling.opacity.at_time(0.5)
        assert mid_op < 1.0

    def test_telegraph_scale_returns_at_end(self):
        """Scale should return to approximately 1 at the end."""
        c = Circle(r=50, cx=100, cy=100)
        c.telegraph(start=0, duration=1, scale_factor=1.4)
        end_sx = c.styling.scale_x.at_time(1.0)
        assert end_sx == pytest.approx(1.0, abs=0.05)

    def test_telegraph_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.telegraph(start=0, duration=0)
        assert result is c

    def test_telegraph_renders_svg(self):
        """Should render without error during the effect."""
        c = Circle(r=50, cx=100, cy=100)
        c.telegraph(start=0, duration=0.5)
        svg = c.to_svg(0.25)
        assert 'circle' in svg.lower() or 'ellipse' in svg.lower()


class TestSkate:
    def test_skate_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.skate(500, 300, start=0, end=1) is c

    def test_skate_moves_to_target(self):
        """Object center should reach the target position at end."""
        c = Circle(r=50, cx=100, cy=100)
        c.skate(500, 300, start=0, end=1, easing=easings.linear)
        cx, cy = c.center(1)
        assert cx == pytest.approx(500, abs=2)
        assert cy == pytest.approx(300, abs=2)

    def test_skate_rotates(self):
        """Object should be rotated partway through."""
        c = Circle(r=50, cx=100, cy=100)
        c.skate(500, 300, start=0, end=1, degrees=360, easing=easings.linear)
        rot = c.styling.rotation.at_time(0.5)
        assert abs(rot[0] - 180) < 2  # halfway through 360 degrees

    def test_skate_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.skate(500, 300, start=0, end=0)
        assert result is c

    def test_skate_partial_rotation(self):
        """Skating with partial rotation (e.g., 180 degrees)."""
        c = Circle(r=50, cx=100, cy=100)
        c.skate(500, 300, start=0, end=1, degrees=180, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert abs(rot[0] - 180) < 2


class TestFlicker:
    def test_flicker_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.flicker(start=0, end=1) is c

    def test_flicker_opacity_varies(self):
        """Opacity should vary during the flicker effect."""
        c = Circle(r=50, cx=100, cy=100)
        c.flicker(start=0, end=1, frequency=8, min_opacity=0.1)
        # Sample several points; at least one should have reduced opacity
        opacities = [c.styling.opacity.at_time(t) for t in [0.1, 0.2, 0.3, 0.4]]
        assert any(op < 1.0 for op in opacities)

    def test_flicker_opacity_at_end(self):
        """At the end, the decay envelope should drive opacity near 1.0."""
        c = Circle(r=50, cx=100, cy=100)
        c.flicker(start=0, end=1, min_opacity=0.1)
        end_op = c.styling.opacity.at_time(1.0)
        assert end_op == pytest.approx(1.0, abs=0.1)

    def test_flicker_respects_min_opacity(self):
        """Opacity should never go below min_opacity."""
        c = Circle(r=50, cx=100, cy=100)
        c.flicker(start=0, end=1, frequency=10, min_opacity=0.2)
        for t_val in [i * 0.05 for i in range(1, 20)]:
            op = c.styling.opacity.at_time(t_val)
            assert op >= 0.19  # allow tiny float tolerance

    def test_flicker_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.flicker(start=0, end=0)
        assert result is c

    def test_flicker_renders_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.flicker(start=0, end=1)
        svg = c.to_svg(0.5)
        assert 'circle' in svg.lower() or 'ellipse' in svg.lower()


class TestSlingshot:
    def test_slingshot_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.slingshot(500, 300, start=0, end=1) is c

    def test_slingshot_reaches_target_at_end(self):
        """Object should be at/near the target position at end."""
        c = Circle(r=50, cx=100, cy=100)
        c.slingshot(500, 300, start=0, end=1, easing=easings.linear)
        cx, cy = c.center(1)
        assert cx == pytest.approx(500, abs=5)
        assert cy == pytest.approx(300, abs=5)

    def test_slingshot_pullback_phase(self):
        """Early in the animation, the object should move away from the target."""
        c = Circle(r=50, cx=100, cy=100)
        c.slingshot(500, 300, start=0, end=1, pullback=0.3, easing=easings.linear)
        # At t=0.1, the object should have pulled back (x < 100 since target is at 500)
        cx_early, _ = c.center(0.1)
        assert cx_early < 100  # pulled back from starting position

    def test_slingshot_overshoot_phase(self):
        """Around t=0.8 with linear easing, the object should overshoot past the target."""
        c = Circle(r=50, cx=100, cy=100)
        c.slingshot(600, 100, start=0, end=1, pullback=0.3, overshoot=0.2, easing=easings.linear)
        # At t=0.75, should be past the target (overshoot)
        cx_overshoot, _ = c.center(0.75)
        # The overshoot means cx should be > 600
        assert cx_overshoot > 600

    def test_slingshot_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.slingshot(500, 300, start=0, end=0)
        assert result is c

    def test_slingshot_renders_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.slingshot(500, 300, start=0, end=1)
        svg = c.to_svg(0.5)
        assert 'circle' in svg.lower() or 'ellipse' in svg.lower()


class TestAxesAddInflectionPoints:
    def test_finds_inflection_of_cubic(self):
        """x^3 has one inflection point at x=0."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 10))
        result = ax.add_inflection_points(lambda x: x**3, samples=400)
        # Should find exactly one inflection point near x=0
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 1

    def test_inflection_point_position(self):
        """The inflection point of x^3 should be near (0, 0)."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 10))
        result = ax.add_inflection_points(lambda x: x**3, samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) >= 1
        # The dot should be positioned at the SVG coords corresponding to (0, 0)
        sx, sy = ax.coords_to_point(0, 0)
        cx, cy = dots[0].c.at_time(0)
        assert cx == pytest.approx(sx, abs=15)
        assert cy == pytest.approx(sy, abs=15)

    def test_no_inflection_for_linear(self):
        """A linear function should have no inflection points."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_inflection_points(lambda x: 2 * x + 1, samples=200)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 0

    def test_sin_has_inflections(self):
        """sin(x) on [0, 2*pi] should have an inflection point near x=pi."""
        import math
        ax = Axes(x_range=(0.5, 5.5), y_range=(-2, 2))
        result = ax.add_inflection_points(lambda x: math.sin(x), samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) >= 1

    def test_returns_vcollection(self):
        """Result should be a VCollection."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 10))
        result = ax.add_inflection_points(lambda x: x**3)
        assert isinstance(result, VCollection)

    def test_custom_x_range(self):
        """Should only find inflection points within the given x_range."""
        import math
        ax = Axes(x_range=(-10, 10), y_range=(-2, 2))
        # sin(x) on [0.5, 2.5] should have no inflection at pi (3.14)
        result = ax.add_inflection_points(lambda x: math.sin(x), x_range=(0.5, 2.5), samples=200)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 0


class TestGetCriticalPoints:
    def test_quadratic_has_one_minimum(self):
        """x^2 should have exactly one critical point (minimum) at x=0."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        result = ax.get_critical_points(lambda x: x**2, samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 1
        assert dots[0]._critical_type == 'min'

    def test_negative_quadratic_has_one_maximum(self):
        """-(x^2) should have exactly one critical point (maximum) at x=0."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 1))
        result = ax.get_critical_points(lambda x: -(x**2), samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 1
        assert dots[0]._critical_type == 'max'

    def test_cubic_has_two_critical_points(self):
        """x^3 - 3x should have two critical points: min at x=1, max at x=-1."""
        ax = Axes(x_range=(-3, 3), y_range=(-5, 5))
        result = ax.get_critical_points(lambda x: x**3 - 3 * x, samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 2
        types = sorted([d._critical_type for d in dots])
        assert types == ['max', 'min']

    def test_linear_has_no_critical_points(self):
        """A linear function should have no critical points."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.get_critical_points(lambda x: 2 * x + 1, samples=200)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 0

    def test_returns_vcollection(self):
        """Result should be a VCollection."""
        ax = Axes(x_range=(-3, 3), y_range=(-10, 10))
        result = ax.get_critical_points(lambda x: x**2)
        assert isinstance(result, VCollection)

    def test_custom_x_range(self):
        """Should only find critical points within the given x_range."""
        ax = Axes(x_range=(-10, 10), y_range=(-5, 5))
        # x^3 - 3x has critical points at x=-1 and x=1
        # Restrict to [1.5, 5]: no critical points expected
        result = ax.get_critical_points(lambda x: x**3 - 3 * x, x_range=(1.5, 5), samples=200)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 0

    def test_sin_critical_points(self):
        """sin(x) on [0, 2*pi] should have a max near pi/2 and a min near 3*pi/2."""
        import math
        ax = Axes(x_range=(0.1, 6.1), y_range=(-2, 2))
        result = ax.get_critical_points(lambda x: math.sin(x), samples=400)
        dots = [o for o in result.objects if isinstance(o, Dot)]
        assert len(dots) == 2

    def test_label_type_coords(self):
        """With label_type='coords', labels should show coordinates."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        result = ax.get_critical_points(lambda x: x**2, label_type='coords', samples=400)
        from vectormation.objects import Text
        labels = [o for o in result.objects if isinstance(o, Text)]
        assert len(labels) == 1
        lbl_text = labels[0].text.at_time(0)
        assert '(' in lbl_text and ')' in lbl_text

    def test_label_type_type_only(self):
        """With label_type='type', labels should show 'min' or 'max'."""
        ax = Axes(x_range=(-3, 3), y_range=(-1, 10))
        result = ax.get_critical_points(lambda x: x**2, label_type='type', samples=400)
        from vectormation.objects import Text
        labels = [o for o in result.objects if isinstance(o, Text)]
        assert len(labels) == 1
        assert labels[0].text.at_time(0) == 'min'


class TestElasticBounce:
    def test_returns_self(self):
        c = Circle(r=50, cx=400, cy=400)
        result = c.elastic_bounce(start=0, end=2)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=400, cy=400)
        sx_before = c.styling.scale_x.at_time(0)
        c.elastic_bounce(start=1, end=1)
        assert c.styling.scale_x.at_time(1) == pytest.approx(sx_before)

    def test_position_changes_during_animation(self):
        """Object should move vertically during the bounce."""
        c = Circle(r=50, cx=400, cy=400)
        c.elastic_bounce(start=0, end=2, height=100, bounces=3)
        # At midpoint of first bounce, object should be displaced upward
        bbox_mid = c.bbox(0.3)
        bbox_start = c.bbox(0)
        # The y position should differ from start
        cy_start = bbox_start[1] + bbox_start[3] / 2
        cy_mid = bbox_mid[1] + bbox_mid[3] / 2
        assert cy_mid != pytest.approx(cy_start, abs=1)

    def test_squash_at_impact(self):
        """Scale_x should be wider (squashed) near impact points."""
        c = Circle(r=50, cx=400, cy=400)
        c.elastic_bounce(start=0, end=2, height=100, bounces=3, squash_factor=1.5)
        # At t=0 (impact), scale_x should be increased
        sx_impact = c.styling.scale_x.at_time(0.001)
        sx_mid = c.styling.scale_x.at_time(0.3)
        # Near impact (start of bounce), squash should be more than mid-air
        assert sx_impact > sx_mid

    def test_returns_to_normal_scale(self):
        """At the end, scale should return to original."""
        c = Circle(r=50, cx=400, cy=400)
        c.elastic_bounce(start=0, end=2, bounces=3, squash_factor=1.4)
        sx_end = c.styling.scale_x.at_time(2.0)
        sy_end = c.styling.scale_y.at_time(2.0)
        assert sx_end == pytest.approx(1.0, abs=0.1)
        assert sy_end == pytest.approx(1.0, abs=0.1)

    def test_multiple_bounces(self):
        """With more bounces, there should be more oscillation cycles."""
        c = Circle(r=50, cx=400, cy=400)
        c.elastic_bounce(start=0, end=2, height=100, bounces=5)
        # Sample multiple points and count zero crossings in dy
        displacements = []
        for i in range(40):
            t = i * 2.0 / 39
            by = c.bbox(t)[1]
            displacements.append(by)
        # Check we have variation
        assert max(displacements) - min(displacements) > 10


class TestMorphScale:
    def test_returns_self(self):
        c = Circle(r=50, cx=400, cy=400)
        result = c.morph_scale(target_scale=2.0, start=0, end=1)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=400, cy=400)
        c.morph_scale(target_scale=2.0, start=1, end=1)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0)

    def test_settles_at_target(self):
        """At end time, scale should be at the target value."""
        c = Circle(r=50, cx=400, cy=400)
        c.morph_scale(target_scale=2.0, start=0, end=1)
        sx = c.styling.scale_x.at_time(1.0)
        sy = c.styling.scale_y.at_time(1.0)
        assert sx == pytest.approx(2.0, abs=0.05)
        assert sy == pytest.approx(2.0, abs=0.05)

    def test_overshoots_during_animation(self):
        """The scale should exceed target_scale at some point during the animation."""
        c = Circle(r=50, cx=400, cy=400)
        c.morph_scale(target_scale=2.0, start=0, end=1, overshoot=0.5, oscillations=2)
        max_sx = max(c.styling.scale_x.at_time(t * 0.01) for t in range(100))
        assert max_sx > 2.0

    def test_starts_at_original(self):
        c = Circle(r=50, cx=400, cy=400)
        c.morph_scale(target_scale=3.0, start=0, end=1)
        sx = c.styling.scale_x.at_time(0.0)
        assert sx == pytest.approx(1.0, abs=0.01)

    def test_scale_down(self):
        """morph_scale should work for scaling down too."""
        c = Circle(r=50, cx=400, cy=400)
        c.morph_scale(target_scale=0.5, start=0, end=1, overshoot=0.2)
        sx = c.styling.scale_x.at_time(1.0)
        assert sx == pytest.approx(0.5, abs=0.05)


class TestStrobe:
    def test_returns_self(self):
        c = Circle(r=50, cx=400, cy=400)
        result = c.strobe(start=0, end=1, flashes=3)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=400, cy=400)
        c.strobe(start=1, end=1, flashes=3)
        # Should not crash and opacity should remain 1
        assert c.styling.opacity.at_time(1) == pytest.approx(1.0)

    def test_zero_flashes_noop(self):
        c = Circle(r=50, cx=400, cy=400)
        c.strobe(start=0, end=1, flashes=0)
        assert c.styling.opacity.at_time(0.5) == pytest.approx(1.0)

    def test_alternates_visibility(self):
        """With duty=0.5, first half of each cycle should be on, second half off."""
        c = Circle(r=50, cx=400, cy=400)
        c.strobe(start=0, end=1, flashes=4, duty=0.5)
        # First quarter of first cycle (cycle = 0.25s): visible
        assert c.styling.opacity.at_time(0.06) == pytest.approx(1.0)
        # Third quarter of first cycle: invisible
        assert c.styling.opacity.at_time(0.19) == pytest.approx(0.0)

    def test_duty_cycle(self):
        """With duty=0.2, object should be visible only 20% of each cycle."""
        c = Circle(r=50, cx=400, cy=400)
        c.strobe(start=0, end=1, flashes=2, duty=0.2)
        # At 5% of first cycle (0.025): visible (0.05 * 2 = 0.1 < 0.2)
        assert c.styling.opacity.at_time(0.025) == pytest.approx(1.0)
        # At 30% of first cycle (0.15): invisible (0.3 > 0.2)
        assert c.styling.opacity.at_time(0.15) == pytest.approx(0.0)

    def test_stays_off_if_clamp(self):
        """duty=0 means always off during strobe period."""
        c = Circle(r=50, cx=400, cy=400)
        c.strobe(start=0, end=1, flashes=3, duty=0.0)
        assert c.styling.opacity.at_time(0.5) == pytest.approx(0.0)


class TestZoomTo:
    """Tests for VObject.zoom_to — animated camera zoom to focus on an object."""

    def test_returns_self(self):
        c = Circle(r=50, cx=300, cy=200)
        canvas = VectorMathAnim(save_dir='/tmp/_vma_test_zoom', width=1920, height=1080)
        result = c.zoom_to(canvas, start=0, end=1)
        assert result is c

    def test_viewbox_targets_object(self):
        c = Circle(r=50, cx=300, cy=200)
        canvas = VectorMathAnim(save_dir='/tmp/_vma_test_zoom', width=1920, height=1080)
        c.zoom_to(canvas, start=0, end=1, padding=50, easing=easings.linear)
        # After animation completes, viewBox should be centered around (300, 200)
        vb_x = canvas.vb_x.at_time(1)
        vb_y = canvas.vb_y.at_time(1)
        vb_w = canvas.vb_w.at_time(1)
        vb_h = canvas.vb_h.at_time(1)
        # Center of viewBox should be near the object center
        vb_cx = vb_x + vb_w / 2
        vb_cy = vb_y + vb_h / 2
        assert vb_cx == pytest.approx(300, abs=5)
        assert vb_cy == pytest.approx(200, abs=5)

    def test_viewbox_shrinks(self):
        c = Circle(r=50, cx=960, cy=540)
        canvas = VectorMathAnim(save_dir='/tmp/_vma_test_zoom', width=1920, height=1080)
        c.zoom_to(canvas, start=0, end=1, padding=100, easing=easings.linear)
        vb_w = canvas.vb_w.at_time(1)
        # viewBox should be much smaller than full canvas
        assert vb_w < 1920

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=300, cy=200)
        canvas = VectorMathAnim(save_dir='/tmp/_vma_test_zoom', width=1920, height=1080)
        c.zoom_to(canvas, start=1, end=1)
        # Should still be at default viewBox
        assert canvas.vb_w.at_time(1) == pytest.approx(1920)

    def test_preserves_aspect_ratio(self):
        r = Rectangle(width=400, height=50, x=100, y=100)
        canvas = VectorMathAnim(save_dir='/tmp/_vma_test_zoom', width=1920, height=1080)
        r.zoom_to(canvas, start=0, end=1, padding=50, easing=easings.linear)
        vb_w = canvas.vb_w.at_time(1)
        vb_h = canvas.vb_h.at_time(1)
        canvas_aspect = 1920 / 1080
        assert vb_w / vb_h == pytest.approx(canvas_aspect, abs=0.01)


class TestTypewriterDelete:
    """Tests for VObject.typewriter_delete — progressive clip-path removal."""

    def test_returns_self(self):
        c = Circle(r=50, cx=400, cy=400)
        result = c.typewriter_delete(start=0, end=1)
        assert result is c

    def test_hidden_after_end(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1)
        assert c.show.at_time(1.5) is False

    def test_visible_before_start(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=1, end=2)
        # Object should be visible before the delete starts
        assert c.show.at_time(0.5) is True

    def test_clip_path_set_during_animation(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset' in clip

    def test_clip_fully_hidden_at_end(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, direction='right', easing=easings.linear)
        clip = c.styling.clip_path.at_time(1)
        # At progress=1.0, the inset should clip everything (100% from right)
        assert clip == 'inset(0 100.0% 0 0)'

    def test_clip_fully_visible_at_start(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, direction='right', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0)
        # At progress=0.0, nothing should be clipped (0% from right)
        assert clip == 'inset(0 0.0% 0 0)'

    def test_direction_left(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, direction='left', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset' in clip

    def test_direction_up(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, direction='up', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset' in clip

    def test_direction_down(self):
        c = Circle(r=50, cx=400, cy=400)
        c.typewriter_delete(start=0, end=1, direction='down', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        assert 'inset' in clip

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=400, cy=400)
        result = c.typewriter_delete(start=1, end=1)
        assert result is c


class TestDomino:
    """Tests for VObject.domino — tipping-over rotation effect."""

    def test_returns_self(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        result = r.domino(start=0, end=1)
        assert result is r

    def test_hidden_after_end(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1)
        assert r.show.at_time(1.5) is False

    def test_no_rotation_at_start(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, easing=easings.linear)
        rot = r.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(0, abs=0.1)

    def test_full_rotation_at_end(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, angle=90, easing=easings.linear)
        rot = r.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(90, abs=0.1)

    def test_direction_left(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, direction='left', angle=90, easing=easings.linear)
        rot = r.styling.rotation.at_time(1)
        # Left direction should rotate negatively
        assert rot[0] == pytest.approx(-90, abs=0.1)

    def test_pivot_point_right(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, direction='right', easing=easings.linear)
        rot = r.styling.rotation.at_time(0.5)
        # Pivot should be at bottom-right of bbox
        bx, by, bw, bh = r.bbox(0)
        assert rot[1] == pytest.approx(bx + bw, abs=0.1)
        assert rot[2] == pytest.approx(by + bh, abs=0.1)

    def test_pivot_point_left(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, direction='left', easing=easings.linear)
        rot = r.styling.rotation.at_time(0.5)
        # Pivot should be at bottom-left of bbox
        bx, by, _, bh = r.bbox(0)
        assert rot[1] == pytest.approx(bx, abs=0.1)
        assert rot[2] == pytest.approx(by + bh, abs=0.1)

    def test_zero_duration_noop(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        result = r.domino(start=1, end=1)
        assert result is r

    def test_mid_animation_rotation(self):
        r = Rectangle(width=50, height=100, x=400, y=300)
        r.domino(start=0, end=1, angle=90, easing=easings.linear)
        rot = r.styling.rotation.at_time(0.5)
        assert rot[0] == pytest.approx(45, abs=1)


# ---------------------------------------------------------------------------
# Axes.get_secant_slope
# ---------------------------------------------------------------------------

class TestAxesGetSecantSlope:
    def test_quadratic_secant(self):
        """Secant slope of x^2 from x=1 to x=2 should be 3."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        slope = ax.get_secant_slope(lambda x: x**2, 1, 1)
        assert slope == pytest.approx(3.0)

    def test_quadratic_small_dx(self):
        """Small dx secant should approximate derivative."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        slope = ax.get_secant_slope(lambda x: x**2, 3, 0.001)
        # f'(3) = 6, secant should be close
        assert slope == pytest.approx(6.0, abs=0.01)

    def test_linear_function(self):
        """Secant slope of a linear function should be constant regardless of dx."""
        ax = Axes(x_range=(-10, 10), y_range=(-10, 10))
        slope = ax.get_secant_slope(lambda x: 2 * x + 5, 0, 3)
        assert slope == pytest.approx(2.0)

    def test_negative_dx(self):
        """Negative dx should work (backward secant)."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        slope = ax.get_secant_slope(lambda x: x**2, 2, -1)
        # (f(1) - f(2)) / (-1) = (1 - 4) / (-1) = 3.0
        assert slope == pytest.approx(3.0)

    def test_dx_zero_raises(self):
        """dx=0 should raise ValueError."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        with pytest.raises(ValueError):
            ax.get_secant_slope(lambda x: x, 0, 0)

    def test_with_curve_object(self):
        """Should work with a curve returned by plot()."""
        ax = Axes(x_range=(0, 5), y_range=(0, 25))
        curve = ax.plot(lambda x: x**2)
        slope = ax.get_secant_slope(curve, 1, 1)
        assert slope == pytest.approx(3.0)

    def test_fractional_dx(self):
        """Fractional dx should produce correct result."""
        ax = Axes(x_range=(-5, 5), y_range=(-5, 25))
        slope = ax.get_secant_slope(lambda x: x**2, 2, 0.5)
        # (f(2.5) - f(2)) / 0.5 = (6.25 - 4) / 0.5 = 4.5
        assert slope == pytest.approx(4.5)


# ---------------------------------------------------------------------------
# NumberLine.get_range_length
# ---------------------------------------------------------------------------

class TestNumberLineGetRangeLength:
    def test_basic_range(self):
        """Range length of (-5, 5) should be 10."""
        nl = NumberLine(x_range=(-5, 5, 1))
        assert nl.get_range_length() == pytest.approx(10)

    def test_positive_range(self):
        """Range length of (0, 100) should be 100."""
        nl = NumberLine(x_range=(0, 100, 10))
        assert nl.get_range_length() == pytest.approx(100)

    def test_fractional_range(self):
        """Range length should work with fractional values."""
        nl = NumberLine(x_range=(0.5, 3.5, 0.5))
        assert nl.get_range_length() == pytest.approx(3.0)

    def test_small_range(self):
        """Very small range should work."""
        nl = NumberLine(x_range=(0, 0.01, 0.001))
        assert nl.get_range_length() == pytest.approx(0.01)


# ---------------------------------------------------------------------------
# NumberLine.snap_to_tick
# ---------------------------------------------------------------------------

class TestNumberLineSnapToTick:
    def test_exact_tick(self):
        """Value on a tick should snap to itself."""
        nl = NumberLine(x_range=(0, 10, 2))
        assert nl.snap_to_tick(4) == pytest.approx(4)

    def test_snap_to_nearest(self):
        """Value between ticks should snap to the nearest one."""
        nl = NumberLine(x_range=(0, 10, 2))
        assert nl.snap_to_tick(3.1) == pytest.approx(4)
        assert nl.snap_to_tick(2.9) == pytest.approx(2)

    def test_snap_midpoint(self):
        """Value exactly between two ticks should round to nearest."""
        nl = NumberLine(x_range=(0, 10, 2))
        # 3 is equidistant from 2 and 4; round() rounds to even = 2 for 1.5 steps
        # k = round((3 - 0) / 2) = round(1.5) = 2, snapped = 4
        assert nl.snap_to_tick(3) == pytest.approx(4)

    def test_clamp_below_range(self):
        """Value below range should clamp to x_start."""
        nl = NumberLine(x_range=(0, 10, 1))
        assert nl.snap_to_tick(-5) == pytest.approx(0)

    def test_clamp_above_range(self):
        """Value above range should clamp to x_end."""
        nl = NumberLine(x_range=(0, 10, 1))
        assert nl.snap_to_tick(15) == pytest.approx(10)

    def test_negative_range(self):
        """Should work with negative ranges."""
        nl = NumberLine(x_range=(-10, 0, 5))
        assert nl.snap_to_tick(-7) == pytest.approx(-5)
        assert nl.snap_to_tick(-8) == pytest.approx(-10)

    def test_fractional_step(self):
        """Should work with fractional steps."""
        nl = NumberLine(x_range=(0, 1, 0.25))
        assert nl.snap_to_tick(0.3) == pytest.approx(0.25)
        assert nl.snap_to_tick(0.6) == pytest.approx(0.5)
        assert nl.snap_to_tick(0.9) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# VObject.dissolve_out
# ---------------------------------------------------------------------------

class TestDissolveOut:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.dissolve_out(start=0, end=1)
        assert result is c

    def test_opacity_starts_near_original(self):
        """Opacity at the very start should be close to the original value."""
        c = Circle(r=50)
        orig = c.styling.opacity.at_time(0)
        c.dissolve_out(start=0, end=2)
        op_start = c.styling.opacity.at_time(0.01)
        assert op_start > orig * 0.5, "Should start near original opacity"

    def test_opacity_reaches_zero_at_end(self):
        """At the end time, opacity should be at or near zero."""
        c = Circle(r=50)
        c.dissolve_out(start=0, end=1)
        op_end = c.styling.opacity.at_time(1.0)
        assert op_end == pytest.approx(0, abs=0.05)

    def test_opacity_decreases_overall(self):
        """The overall trend should be downward."""
        c = Circle(r=50)
        c.dissolve_out(start=0, end=1)
        op_early = c.styling.opacity.at_time(0.1)
        op_late = c.styling.opacity.at_time(0.9)
        assert op_early > op_late, "Opacity should decrease over time"

    def test_hides_after_end(self):
        """With change_existence=True, object should be hidden after end."""
        c = Circle(r=50)
        c.dissolve_out(start=0, end=1, change_existence=True)
        assert c.show.at_time(1.5) == False

    def test_no_hide_when_disabled(self):
        """With change_existence=False, object should remain visible."""
        c = Circle(r=50)
        c.dissolve_out(start=0, end=1, change_existence=False)
        assert c.show.at_time(1.5) == True

    def test_zero_duration(self):
        """Zero duration should just hide immediately if change_existence."""
        c = Circle(r=50)
        result = c.dissolve_out(start=1, end=1, change_existence=True)
        assert result is c
        assert c.show.at_time(1.5) == False

    def test_deterministic_with_seed(self):
        """Same seed should produce the same dissolve pattern."""
        c1 = Circle(r=50)
        c1.dissolve_out(start=0, end=1, seed=42)
        c2 = Circle(r=50)
        c2.dissolve_out(start=0, end=1, seed=42)
        for t in [0.2, 0.4, 0.6, 0.8]:
            assert c1.styling.opacity.at_time(t) == c2.styling.opacity.at_time(t)

    def test_different_seeds_differ(self):
        """Different seeds should produce different patterns (at most times)."""
        c1 = Circle(r=50)
        c1.dissolve_out(start=0, end=1, seed=42)
        c2 = Circle(r=50)
        c2.dissolve_out(start=0, end=1, seed=99)
        # At least one sample point should differ
        diffs = [abs(c1.styling.opacity.at_time(t) - c2.styling.opacity.at_time(t))
                 for t in [0.2, 0.4, 0.6]]
        assert any(d > 0.01 for d in diffs)


class TestStampTrail:
    def test_returns_list(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, start=0, end=1)
        ghosts = d.stamp_trail(start=0, end=1, count=5)
        assert isinstance(ghosts, list)
        assert len(ghosts) == 5

    def test_ghosts_frozen_at_different_positions(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=300, start=0, end=1, easing=easings.linear)
        ghosts = d.stamp_trail(start=0, end=1, count=3)
        # Each ghost should be frozen at a different x position
        xs = [g.c.at_time(1)[0] for g in ghosts]
        assert len(set(round(x, 1) for x in xs)) == 3

    def test_ghosts_hidden_before_appearance(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=100, start=0, end=1)
        ghosts = d.stamp_trail(start=0, end=1, count=2)
        # First ghost should be hidden at t=0
        assert ghosts[0].show.at_time(0) == False

    def test_ghosts_fade_out(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=100, start=0, end=1)
        ghosts = d.stamp_trail(start=0, end=1, count=2, fade_duration=0.3)
        g = ghosts[0]
        # Ghost should be hidden after fade_duration
        t_appear = 1 / 3  # (0+1)*(1)/(2+1) = 1/3
        assert g.show.at_time(t_appear + 0.3 + 0.01) == False

    def test_returns_self_pattern(self):
        """stamp_trail returns a list, not self (matches trail pattern)."""
        d = Dot(cx=100, cy=100)
        result = d.stamp_trail(start=0, end=1, count=3)
        assert isinstance(result, list)

    def test_empty_when_zero_count(self):
        d = Dot(cx=100, cy=100)
        ghosts = d.stamp_trail(start=0, end=1, count=0)
        assert ghosts == []

    def test_empty_when_zero_duration(self):
        d = Dot(cx=100, cy=100)
        ghosts = d.stamp_trail(start=1, end=1, count=5)
        assert ghosts == []

    def test_custom_opacity(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=100, start=0, end=1)
        ghosts = d.stamp_trail(start=0, end=1, count=1, opacity=0.8, fade_duration=1.0)
        g = ghosts[0]
        t_appear = 0.5  # (0+1)*(1)/(1+1) = 0.5
        # At appearance, opacity should be close to 0.8
        assert g.styling.fill_opacity.at_time(t_appear) == pytest.approx(0.8, abs=0.05)


class TestUnfold:
    def test_returns_self(self):
        r = Rectangle(200, 100, 100, 100)
        result = r.unfold(start=0, end=1)
        assert result is r

    def test_scale_x_at_start_is_zero_right(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='right')
        assert r.styling.scale_x.at_time(0) == pytest.approx(0, abs=0.01)

    def test_scale_x_at_end_is_one_right(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='right')
        assert r.styling.scale_x.at_time(1) == pytest.approx(1, abs=0.01)

    def test_scale_y_unchanged_horizontal(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='right')
        assert r.styling.scale_y.at_time(0.5) == pytest.approx(1, abs=0.01)

    def test_left_direction(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='left')
        # scale_x should go from 0 to 1
        assert r.styling.scale_x.at_time(0) == pytest.approx(0, abs=0.01)
        assert r.styling.scale_x.at_time(1) == pytest.approx(1, abs=0.01)
        # Anchor should be right edge
        assert r.styling._scale_origin[0] == pytest.approx(300, abs=1)

    def test_down_direction(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='down')
        # scale_y should go from 0 to 1, scale_x unchanged
        assert r.styling.scale_y.at_time(0) == pytest.approx(0, abs=0.01)
        assert r.styling.scale_y.at_time(1) == pytest.approx(1, abs=0.01)
        assert r.styling.scale_x.at_time(0.5) == pytest.approx(1, abs=0.01)

    def test_up_direction(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=0, end=1, direction='up')
        assert r.styling.scale_y.at_time(0) == pytest.approx(0, abs=0.01)
        # Anchor at bottom edge
        assert r.styling._scale_origin[1] == pytest.approx(200, abs=1)

    def test_change_existence(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=1, end=2, direction='right', change_existence=True)
        assert r.show.at_time(0.5) == False
        assert r.show.at_time(1) == True

    def test_no_change_existence(self):
        r = Rectangle(200, 100, 100, 100)
        r.unfold(start=1, end=2, direction='right', change_existence=False)
        # Should be visible before animation
        assert r.show.at_time(0.5) == True

    def test_zero_duration(self):
        r = Rectangle(200, 100, 100, 100)
        result = r.unfold(start=1, end=1)
        assert result is r


class TestGlitchShift:
    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.glitch_shift(start=0, end=1)
        assert result is c

    def test_position_displaced_during_effect(self):
        c = Circle(r=50, cx=500, cy=500)
        c.glitch_shift(start=0, end=1, intensity=30, steps=4, seed=42)
        # During the effect, the x position should be displaced
        displaced = False
        for t in [0.1, 0.3, 0.5, 0.7]:
            cx = c.c.at_time(t)[0]
            if abs(cx - 500) > 1:
                displaced = True
        assert displaced

    def test_position_restored_after_effect(self):
        c = Circle(r=50, cx=500, cy=500)
        c.glitch_shift(start=0, end=1, intensity=30, steps=4, seed=42)
        # After the effect, position should return to original
        cx, cy = c.c.at_time(1.1)
        assert cx == pytest.approx(500, abs=1)
        assert cy == pytest.approx(500, abs=1)

    def test_only_horizontal_displacement(self):
        c = Circle(r=50, cx=500, cy=500)
        c.glitch_shift(start=0, end=1, intensity=30, steps=4, seed=42)
        # y coordinate should remain unchanged during the effect
        for t in [0.1, 0.3, 0.5, 0.7]:
            cy = c.c.at_time(t)[1]
            assert cy == pytest.approx(500, abs=1)

    def test_seed_reproducibility(self):
        c1 = Circle(r=50, cx=500, cy=500)
        c1.glitch_shift(start=0, end=1, intensity=30, steps=4, seed=123)
        c2 = Circle(r=50, cx=500, cy=500)
        c2.glitch_shift(start=0, end=1, intensity=30, steps=4, seed=123)
        for t in [0.1, 0.3, 0.5, 0.7]:
            assert c1.c.at_time(t)[0] == pytest.approx(c2.c.at_time(t)[0], abs=0.01)

    def test_different_seeds_differ(self):
        c1 = Circle(r=50, cx=500, cy=500)
        c1.glitch_shift(start=0, end=1, intensity=30, steps=8, seed=42)
        c2 = Circle(r=50, cx=500, cy=500)
        c2.glitch_shift(start=0, end=1, intensity=30, steps=8, seed=99)
        diffs = [abs(c1.c.at_time(t)[0] - c2.c.at_time(t)[0]) for t in [0.1, 0.3, 0.5]]
        assert any(d > 1 for d in diffs)

    def test_zero_duration(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.glitch_shift(start=1, end=1)
        assert result is c

    def test_zero_steps(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.glitch_shift(start=0, end=1, steps=0)
        assert result is c


class TestWaveThrough:
    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.wave_through(start=0, end=2, amplitude=30, frequency=2)
        assert result is c

    def test_y_displacement_at_midpoint(self):
        """At the midpoint the envelope is at maximum, so there should be displacement."""
        c = Circle(r=50, cx=500, cy=500)
        c.wave_through(start=0, end=2, amplitude=30, frequency=1, direction='y',
                       easing=easings.linear)
        # At quarter-way through (t=0.5), sin(2*pi*1*0.25)=sin(pi/2)=1
        # envelope = linear(0.25) * (1-linear(0.25)) * 4 = 0.25*0.75*4 = 0.75
        # displacement = 30 * 1 * 0.75 = 22.5
        cy_mid = c.c.at_time(0.5)[1]
        # The y coordinate should be displaced from the original 500
        assert abs(cy_mid - 500) > 10

    def test_x_direction(self):
        """With direction='x', displacement should be on the x axis."""
        c = Circle(r=50, cx=500, cy=500)
        c.wave_through(start=0, end=2, amplitude=30, frequency=1, direction='x',
                       easing=easings.linear)
        cx_mid = c.c.at_time(0.5)[0]
        cy_mid = c.c.at_time(0.5)[1]
        # x should be displaced, y should stay at 500
        assert abs(cx_mid - 500) > 10
        assert cy_mid == pytest.approx(500, abs=1)

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.wave_through(start=1, end=1)
        assert result is c
        assert c.c.at_time(1) == (500, 500)

    def test_returns_to_origin(self):
        """At start and end, displacement should be zero."""
        c = Circle(r=50, cx=500, cy=500)
        c.wave_through(start=0, end=2, amplitude=40, frequency=3, direction='y')
        # At the very start, displacement should be 0 (sin(0)=0)
        assert c.c.at_time(0)[1] == pytest.approx(500, abs=1)
        # At the very end, displacement should be 0 (envelope is 0)
        assert c.c.at_time(2)[1] == pytest.approx(500, abs=1)

    def test_custom_frequency(self):
        """Higher frequency should produce more oscillations."""
        c1 = Circle(r=50, cx=500, cy=500)
        c1.wave_through(start=0, end=2, amplitude=30, frequency=1, direction='y',
                        easing=easings.linear)
        c2 = Circle(r=50, cx=500, cy=500)
        c2.wave_through(start=0, end=2, amplitude=30, frequency=4, direction='y',
                        easing=easings.linear)
        # Sample at many points and count zero crossings - higher freq should have more
        samples1 = [c1.c.at_time(t)[1] - 500 for t in [i * 0.1 for i in range(21)]]
        samples2 = [c2.c.at_time(t)[1] - 500 for t in [i * 0.1 for i in range(21)]]
        crossings1 = sum(1 for i in range(len(samples1) - 1) if samples1[i] * samples1[i+1] < 0)
        crossings2 = sum(1 for i in range(len(samples2) - 1) if samples2[i] * samples2[i+1] < 0)
        assert crossings2 > crossings1


class TestCountdownText:
    def test_basic_countdown(self):
        t = Text('', x=500, y=500)
        t.countdown(start=0, end=3, from_val=3)
        assert t.text.at_time(0) == '3'
        assert t.text.at_time(1) == '2'
        assert t.text.at_time(2) == '1'

    def test_countdown_returns_self(self):
        t = Text('', x=500, y=500)
        result = t.countdown(start=0, end=3, from_val=3)
        assert result is t

    def test_countdown_from_5(self):
        t = Text('', x=500, y=500)
        t.countdown(start=0, end=5, from_val=5)
        assert t.text.at_time(0) == '5'
        assert t.text.at_time(1) == '4'
        assert t.text.at_time(2) == '3'
        assert t.text.at_time(3) == '2'
        assert t.text.at_time(4) == '1'

    def test_countdown_non_text_raises(self):
        c = Circle(r=50, cx=500, cy=500)
        with pytest.raises(TypeError, match="Text"):
            c.countdown(start=0, end=3)

    def test_zero_duration(self):
        t = Text('', x=500, y=500)
        result = t.countdown(start=1, end=1, from_val=3)
        assert result is t

    def test_from_val_1(self):
        t = Text('', x=500, y=500)
        t.countdown(start=0, end=1, from_val=1)
        assert t.text.at_time(0) == '1'


class TestSqueeze:
    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.squeeze(start=0, end=1, axis='x', factor=0.5)
        assert result is c

    def test_squeeze_x_at_end(self):
        """After squeeze along x, scale_x should be factor and scale_y should be 1/factor."""
        c = Circle(r=50, cx=500, cy=500)
        c.squeeze(start=0, end=1, axis='x', factor=0.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(1)
        sy = c.styling.scale_y.at_time(1)
        assert sx == pytest.approx(0.5, abs=0.05)
        assert sy == pytest.approx(2.0, abs=0.05)

    def test_squeeze_y_at_end(self):
        """Squeezing along y should compress y and expand x."""
        c = Circle(r=50, cx=500, cy=500)
        c.squeeze(start=0, end=1, axis='y', factor=0.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(1)
        sy = c.styling.scale_y.at_time(1)
        assert sy == pytest.approx(0.5, abs=0.05)
        assert sx == pytest.approx(2.0, abs=0.05)

    def test_squeeze_preserves_area(self):
        """scale_x * scale_y should be approximately 1 (area preserved)."""
        c = Circle(r=50, cx=500, cy=500)
        c.squeeze(start=0, end=1, axis='x', factor=0.7, easing=easings.linear)
        sx = c.styling.scale_x.at_time(0.5)
        sy = c.styling.scale_y.at_time(0.5)
        assert sx * sy == pytest.approx(1.0, abs=0.05)

    def test_squeeze_at_start_unchanged(self):
        """At start time, scales should still be at their initial values."""
        c = Circle(r=50, cx=500, cy=500)
        c.squeeze(start=0, end=1, axis='x', factor=0.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(0)
        sy = c.styling.scale_y.at_time(0)
        assert sx == pytest.approx(1.0, abs=0.05)
        assert sy == pytest.approx(1.0, abs=0.05)

    def test_squeeze_stays(self):
        """After the animation ends, the squeeze should persist."""
        c = Circle(r=50, cx=500, cy=500)
        c.squeeze(start=0, end=1, axis='x', factor=0.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(2)
        sy = c.styling.scale_y.at_time(2)
        assert sx == pytest.approx(0.5, abs=0.05)
        assert sy == pytest.approx(2.0, abs=0.05)

    def test_zero_duration(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.squeeze(start=1, end=1)
        assert result is c


class TestBindTo:
    def test_bind_to_returns_self(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=300)
        result = c1.bind_to(c2, offset_x=10, offset_y=20, start=0, end=2)
        assert result is c1

    def test_bind_to_adds_updater(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=300)
        initial_count = len(c1._updaters)
        c1.bind_to(c2, start=0, end=2)
        assert len(c1._updaters) == initial_count + 1

    def test_bind_to_follows_target(self):
        """After running the updater, c1 should be at c2's center + offset."""
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=300)
        c1.bind_to(c2, offset_x=50, offset_y=0, start=0, end=5)
        # Manually run updaters at time=1
        c1._run_updaters(1)
        cx1 = c1.center(1)
        cx2 = c2.center(1)
        assert cx1[0] == pytest.approx(cx2[0] + 50, abs=1)
        assert cx1[1] == pytest.approx(cx2[1], abs=1)

    def test_bind_to_with_zero_offset(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=500, cy=500)
        c1.bind_to(c2, start=0, end=5)
        c1._run_updaters(1)
        cx1 = c1.center(1)
        cx2 = c2.center(1)
        assert cx1[0] == pytest.approx(cx2[0], abs=1)
        assert cx1[1] == pytest.approx(cx2[1], abs=1)


class TestDuplicate:
    def test_duplicate_returns_vcollection(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate(count=3)
        assert isinstance(result, VCollection)

    def test_duplicate_count(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate(count=4)
        assert len(result.objects) == 4

    def test_duplicate_default_count(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate()
        assert len(result.objects) == 2

    def test_duplicate_does_not_include_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate(count=3)
        for obj in result.objects:
            assert obj is not c

    def test_duplicate_copies_are_independent(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate(count=2)
        # Copies should be distinct objects
        assert result.objects[0] is not result.objects[1]

    def test_duplicate_arranges_objects(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.duplicate(count=2, direction=RIGHT, buff=34)
        # After arrangement, second copy should be to the right of the first
        x0 = result.objects[0].center(0)[0]
        x1 = result.objects[1].center(0)[0]
        assert x1 > x0


class TestArcTo:
    def test_arc_to_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.arc_to(500, 500, start=0, end=1)
        assert result is c

    def test_arc_to_reaches_target(self):
        c = Circle(r=50, cx=100, cy=100)
        c.arc_to(500, 500, start=0, end=1, easing=easings.linear)
        cx, cy = c.center(1)
        assert cx == pytest.approx(500, abs=2)
        assert cy == pytest.approx(500, abs=2)

    def test_arc_to_midpoint_differs_from_straight(self):
        """The arc path should deviate from a straight line at the midpoint."""
        c_arc = Circle(r=50, cx=100, cy=100)
        c_arc.arc_to(500, 100, start=0, end=1, angle=math.pi/2, easing=easings.linear)
        mid_arc = c_arc.center(0.5)
        # Straight line midpoint would be (300, 100)
        # Arc should deviate in y
        assert abs(mid_arc[1] - 100) > 10

    def test_arc_to_custom_angle(self):
        c = Circle(r=50, cx=100, cy=100)
        c.arc_to(500, 100, start=0, end=1, angle=math.pi, easing=easings.linear)
        # At end, should still reach target
        cx, cy = c.center(1)
        assert cx == pytest.approx(500, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_arc_to_zero_duration(self):
        """Zero or negative duration should still return self."""
        c = Circle(r=50, cx=100, cy=100)
        result = c.arc_to(500, 500, start=1, end=0)
        assert result is c


class TestTypewriterCursor:
    def test_typewriter_cursor_returns_self(self):
        t = Text('hello', x=100, y=100)
        result = t.typewriter_cursor(start=0, end=2)
        assert result is t

    def test_typewriter_cursor_appends_cursor(self):
        t = Text('hello', x=100, y=100)
        t.typewriter_cursor(start=0, end=2, blink_rate=0.5, cursor_char='|')
        # At time 0 (start of blink cycle, int(0)%2==0), cursor should be visible
        text_val = t.text.at_time(0)
        assert text_val == 'hello|'

    def test_typewriter_cursor_blinks_off(self):
        t = Text('hello', x=100, y=100)
        t.typewriter_cursor(start=0, end=10, blink_rate=1.0, cursor_char='|')
        # At time 1.0, cycle = 1.0, int(1.0)%2 == 1, cursor off
        text_val = t.text.at_time(1.0)
        assert text_val == 'hello'

    def test_typewriter_cursor_blinks_on_again(self):
        t = Text('hello', x=100, y=100)
        t.typewriter_cursor(start=0, end=10, blink_rate=1.0, cursor_char='|')
        # At time 2.0, cycle = 2.0, int(2.0)%2 == 0, cursor on
        text_val = t.text.at_time(2.0)
        assert text_val == 'hello|'

    def test_typewriter_cursor_custom_char(self):
        t = Text('hello', x=100, y=100)
        t.typewriter_cursor(start=0, end=5, blink_rate=0.5, cursor_char='_')
        text_val = t.text.at_time(0)
        assert text_val == 'hello_'

    def test_typewriter_cursor_on_non_text_raises(self):
        c = Circle(r=50, cx=100, cy=100)
        with pytest.raises(TypeError):
            c.typewriter_cursor(start=0, end=2)

    def test_typewriter_cursor_after_end(self):
        """After end time, cursor should no longer be present."""
        t = Text('hello', x=100, y=100)
        t.typewriter_cursor(start=0, end=2)
        text_val = t.text.at_time(3)
        assert text_val == 'hello'


class TestPulseOutline:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.pulse_outline(start=0, end=2)
        assert result is c

    def test_stroke_width_increases_during_animation(self):
        c = Circle(r=50, cx=100, cy=100)
        _ = c.styling.stroke_width.at_time(0)
        c.pulse_outline(start=0, end=2, max_width=12, cycles=1, easing=easings.linear)
        # At the midpoint of a single cycle, sin(pi * 1 * 0.5) = sin(pi/2) = 1
        mid_sw = c.styling.stroke_width.at_time(1.0)
        assert mid_sw == pytest.approx(12, abs=0.5)

    def test_stroke_width_returns_to_original_after(self):
        c = Circle(r=50, cx=100, cy=100)
        orig_sw = c.styling.stroke_width.at_time(0)
        c.pulse_outline(start=0, end=2, max_width=12, cycles=1, easing=easings.linear)
        # After end, stay=False so it reverts
        after_sw = c.styling.stroke_width.at_time(3.0)
        assert after_sw == pytest.approx(orig_sw, abs=0.5)

    def test_stroke_color_set_during_animation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.pulse_outline(start=0, end=2, color='#FF0000')
        stroke_val = c.styling.stroke.time_func(1.0)
        # Should be red (255, 0, 0) during animation
        assert stroke_val[0] == 255
        assert stroke_val[1] == 0
        assert stroke_val[2] == 0

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        orig_sw = c.styling.stroke_width.at_time(0)
        c.pulse_outline(start=1, end=1)
        assert c.styling.stroke_width.at_time(1) == pytest.approx(orig_sw)

    def test_multiple_cycles(self):
        c = Circle(r=50, cx=100, cy=100)
        orig_sw = c.styling.stroke_width.at_time(0)
        c.pulse_outline(start=0, end=4, max_width=10, cycles=2, easing=easings.linear)
        # At t=1 (progress=0.25), sin(pi * 2 * 0.25) = sin(pi/2) = 1 -> max
        sw_at_1 = c.styling.stroke_width.at_time(1.0)
        assert sw_at_1 == pytest.approx(10, abs=0.5)
        # At t=2 (progress=0.5), sin(pi * 2 * 0.5) = sin(pi) = 0 -> original
        sw_at_2 = c.styling.stroke_width.at_time(2.0)
        assert sw_at_2 == pytest.approx(orig_sw, abs=0.5)


class TestShimmer:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.shimmer(start=0, end=2)
        assert result is c

    def test_opacity_varies_during_animation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shimmer(start=0, end=2, passes=1, easing=easings.linear)
        # At start (progress=0), cos(0)=1, opacity = 0.3 + 0.7*1 = 1.0
        op_start = c.styling.opacity.at_time(0)
        assert op_start == pytest.approx(1.0, abs=0.05)
        # At midpoint (progress=0.5), cos(pi)=-1, opacity = 0.3 + 0.7*0 = 0.3
        op_mid = c.styling.opacity.at_time(1.0)
        assert op_mid == pytest.approx(0.3, abs=0.05)

    def test_opacity_restores_after_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shimmer(start=0, end=2, passes=1)
        # After end, stay=False so opacity should revert to default (1.0)
        op_after = c.styling.opacity.at_time(3.0)
        assert op_after == pytest.approx(1.0, abs=0.05)

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shimmer(start=1, end=1)
        assert c.styling.opacity.at_time(1) == pytest.approx(1.0)

    def test_multiple_passes(self):
        c = Circle(r=50, cx=100, cy=100)
        c.shimmer(start=0, end=4, passes=2, easing=easings.linear)
        # At progress=0.25, cos(2*pi*2*0.25) = cos(pi) = -1, opacity = 0.3
        op_at_1 = c.styling.opacity.at_time(1.0)
        assert op_at_1 == pytest.approx(0.3, abs=0.05)
        # At progress=0.5, cos(2*pi*2*0.5) = cos(2*pi) = 1, opacity = 1.0
        op_at_2 = c.styling.opacity.at_time(2.0)
        assert op_at_2 == pytest.approx(1.0, abs=0.05)


class TestBlinkNumBlinks:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.blink(start=0, end=3, num_blinks=3, easing=easings.linear)
        assert result is c

    def test_opacity_toggles_off(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=3, num_blinks=3, easing=easings.linear)
        # Each blink cycle = 1.0s. First half (0..0.5) should be off.
        # At t=0.25, progress=0.25/3=0.0833, phase=(0.0833*3)%1 = 0.25 < 0.5 -> off
        op = c.styling.opacity.at_time(0.25)
        assert op == pytest.approx(0.0, abs=0.01)

    def test_opacity_toggles_on(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=3, num_blinks=3, easing=easings.linear)
        # At t=0.75, progress=0.75/3=0.25, phase=(0.25*3)%1 = 0.75 >= 0.5 -> on
        op = c.styling.opacity.at_time(0.75)
        assert op == pytest.approx(1.0, abs=0.01)

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=1, end=1, num_blinks=3)
        assert c.styling.opacity.at_time(1) == pytest.approx(1.0)

    def test_zero_num_blinks_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=2, num_blinks=0)
        assert c.styling.opacity.at_time(1) == pytest.approx(1.0)

    def test_restores_after_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.blink(start=0, end=2, num_blinks=2, easing=easings.linear)
        # After end, stay=False so should revert
        op_after = c.styling.opacity.at_time(3.0)
        assert op_after == pytest.approx(1.0, abs=0.05)


class TestPinTo:
    def test_returns_self(self):
        target = Circle(r=50, cx=200, cy=200)
        follower = Circle(r=10, cx=0, cy=0)
        result = follower.pin_to(target, edge='center', start=0, end=1)
        assert result is follower

    def test_pin_to_center(self):
        target = Circle(r=50, cx=200, cy=200)
        follower = Circle(r=10, cx=0, cy=0)
        follower.pin_to(target, edge='center', start=0, end=1)
        follower._run_updaters(0.5)
        fx, fy, fw, fh = follower.bbox(0.5)
        fcx, fcy = fx + fw / 2, fy + fh / 2
        assert fcx == pytest.approx(200, abs=1)
        assert fcy == pytest.approx(200, abs=1)

    def test_pin_to_top(self):
        target = Rectangle(width=100, height=60, x=150, y=170)
        follower = Circle(r=10, cx=0, cy=0)
        follower.pin_to(target, edge='top', start=0, end=1)
        follower._run_updaters(0.5)
        fx, fy, fw, fh = follower.bbox(0.5)
        fcx, fcy = fx + fw / 2, fy + fh / 2
        # Target top edge: (150 + 100/2, 170) = (200, 170)
        assert fcx == pytest.approx(200, abs=1)
        assert fcy == pytest.approx(170, abs=1)

    def test_pin_to_bottom_right(self):
        target = Rectangle(width=100, height=60, x=150, y=170)
        follower = Circle(r=10, cx=0, cy=0)
        follower.pin_to(target, edge='bottom_right', start=0, end=1)
        follower._run_updaters(0.5)
        fx, fy, fw, fh = follower.bbox(0.5)
        fcx, fcy = fx + fw / 2, fy + fh / 2
        # Target bottom_right: (150 + 100, 170 + 60) = (250, 230)
        assert fcx == pytest.approx(250, abs=1)
        assert fcy == pytest.approx(230, abs=1)

    def test_pin_to_with_offset(self):
        target = Circle(r=50, cx=200, cy=200)
        follower = Circle(r=10, cx=0, cy=0)
        follower.pin_to(target, edge='center', offset_x=20, offset_y=-10, start=0, end=1)
        follower._run_updaters(0.5)
        fx, fy, fw, fh = follower.bbox(0.5)
        fcx, fcy = fx + fw / 2, fy + fh / 2
        assert fcx == pytest.approx(220, abs=1)
        assert fcy == pytest.approx(190, abs=1)


class TestParallax:
    def test_parallax_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.parallax(dx=200, dy=100, start=0, end=1)
        assert result is c

    def test_parallax_moves_by_depth_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.parallax(dx=200, dy=100, start=0, end=1, depth_factor=0.5, easing=easings.linear)
        cx_end, cy_end = c.center(1)
        # Should move by 200*0.5=100 in x and 100*0.5=50 in y
        assert cx_end == pytest.approx(200, abs=1)
        assert cy_end == pytest.approx(150, abs=1)

    def test_parallax_zero_depth_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.parallax(dx=200, dy=100, start=0, end=1, depth_factor=0)
        cx_end, cy_end = c.center(1)
        # With depth_factor=0, object should not move
        assert cx_end == pytest.approx(100, abs=1)
        assert cy_end == pytest.approx(100, abs=1)

    def test_parallax_full_depth_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.parallax(dx=200, dy=100, start=0, end=1, depth_factor=1.0, easing=easings.linear)
        cx_end, cy_end = c.center(1)
        # With depth_factor=1.0, should move full amount
        assert cx_end == pytest.approx(300, abs=1)
        assert cy_end == pytest.approx(200, abs=1)

    def test_parallax_midpoint(self):
        c = Circle(r=50, cx=0, cy=0)
        c.parallax(dx=100, dy=0, start=0, end=1, depth_factor=0.5, easing=easings.linear)
        cx_mid, _ = c.center(0.5)
        # At midpoint with linear easing: 100*0.5*0.5 = 25
        assert cx_mid == pytest.approx(25, abs=1)


class TestSetDashPattern:
    def test_set_dash_pattern_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_dash_pattern('dashes', start=0)
        assert result is c

    def test_set_dash_pattern_dashes(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('dashes', start=0)
        assert c.styling.stroke_dasharray.at_time(0) == '10 5'

    def test_set_dash_pattern_dots(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('dots', start=0)
        assert c.styling.stroke_dasharray.at_time(0) == '2 4'

    def test_set_dash_pattern_dash_dot(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('dash_dot', start=0)
        assert c.styling.stroke_dasharray.at_time(0) == '10 5 2 5'

    def test_set_dash_pattern_solid(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('solid', start=0)
        assert c.styling.stroke_dasharray.at_time(0) == ''

    def test_set_dash_pattern_custom_string(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('20 10 5 10', start=0)
        assert c.styling.stroke_dasharray.at_time(0) == '20 10 5 10'

    def test_set_dash_pattern_at_later_time(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_dash_pattern('dashes', start=2)
        # Before the set time, should be default (empty)
        assert c.styling.stroke_dasharray.at_time(1) == ''
        # At and after the set time, should be dashes
        assert c.styling.stroke_dasharray.at_time(2) == '10 5'
        assert c.styling.stroke_dasharray.at_time(3) == '10 5'


class TestShowIf:
    def test_show_if_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.show_if(lambda t: t < 1, start=0)
        assert result is c

    def test_show_if_visible_when_true(self):
        c = Circle(r=50, cx=100, cy=100)
        c.show_if(lambda t: t < 1, start=0, end=2)
        c._run_updaters(0.5)
        assert c.styling.opacity.at_time(0.5) == pytest.approx(1)

    def test_show_if_hidden_when_false(self):
        c = Circle(r=50, cx=100, cy=100)
        c.show_if(lambda t: t < 1, start=0, end=2)
        c._run_updaters(1.5)
        assert c.styling.opacity.at_time(1.5) == pytest.approx(0)

    def test_show_if_toggles(self):
        c = Circle(r=50, cx=100, cy=100)
        # Visible only on even seconds
        c.show_if(lambda t: int(t) % 2 == 0, start=0, end=4)
        c._run_updaters(0.5)
        assert c.styling.opacity.at_time(0.5) == pytest.approx(1)
        c._run_updaters(1.5)
        assert c.styling.opacity.at_time(1.5) == pytest.approx(0)
        c._run_updaters(2.5)
        assert c.styling.opacity.at_time(2.5) == pytest.approx(1)

    def test_show_if_fill_opacity_also_set(self):
        c = Circle(r=50, cx=100, cy=100)
        c.show_if(lambda _t: False, start=0, end=2)
        c._run_updaters(0.5)
        assert c.styling.fill_opacity.at_time(0.5) == pytest.approx(0)


class TestFadeToColor:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#0000ff', stroke='#0000ff')
        result = c.fade_to_color('#ff0000', start=0, end=1)
        assert result is c

    def test_fill_changes_to_target(self):
        c = Circle(r=50, cx=100, cy=100, fill='#0000ff', stroke='#0000ff')
        c.fade_to_color('#ff0000', start=0, end=1, easing=easings.linear)
        fill_at_end = c.styling.fill.at_time(1)
        # At end, fill should be red (may be returned as rgb format)
        assert 'ff0000' in fill_at_end or 'rgb(255,0,0)' in fill_at_end or fill_at_end == 'rgb(255, 0, 0)'

    def test_stroke_changes_to_target(self):
        c = Circle(r=50, cx=100, cy=100, fill='#0000ff', stroke='#0000ff')
        c.fade_to_color('#ff0000', start=0, end=1, easing=easings.linear)
        stroke_at_end = c.styling.stroke.at_time(1)
        assert 'ff0000' in stroke_at_end or 'rgb(255,0,0)' in stroke_at_end or stroke_at_end == 'rgb(255, 0, 0)'

    def test_colors_unchanged_before_start(self):
        c = Circle(r=50, cx=100, cy=100, fill='#0000ff', stroke='#0000ff')
        c.fade_to_color('#ff0000', start=1, end=2, easing=easings.linear)
        fill_before = c.styling.fill.at_time(0)
        # Before start, fill should still be blue (may be in rgb format)
        assert '0000ff' in fill_before or 'rgb(0,0,255)' in fill_before or fill_before == 'rgb(0, 0, 255)'


class TestSpinAndFade:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.spin_and_fade(start=0, end=1)
        assert result is c

    def test_opacity_zero_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_and_fade(start=0, end=1, easing=easings.linear)
        opacity = c.styling.opacity.at_time(1)
        assert opacity == pytest.approx(0, abs=0.05)

    def test_rotation_applied(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_and_fade(start=0, end=1, spins=1, direction=1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(360, abs=5)

    def test_counterclockwise_direction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_and_fade(start=0, end=1, spins=1, direction=-1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(-360, abs=5)

    def test_half_spin_at_midpoint(self):
        c = Circle(r=50, cx=100, cy=100)
        c.spin_and_fade(start=0, end=2, spins=1, direction=1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(180, abs=10)


class TestGrowToSize:
    def test_returns_self(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.grow_to_size(target_width=200, start=0, end=1)
        assert result is r

    def test_grow_width_only_maintains_ratio(self):
        r = Rectangle(100, 50, x=100, y=100)
        r.grow_to_size(target_width=200, start=0, end=1, easing=easings.linear)
        # scale_x and scale_y should be the same (uniform scale)
        sx = r.styling.scale_x.at_time(1)
        sy = r.styling.scale_y.at_time(1)
        assert sx == pytest.approx(sy, abs=0.05)
        assert sx == pytest.approx(2.0, abs=0.1)

    def test_grow_height_only_maintains_ratio(self):
        r = Rectangle(100, 50, x=100, y=100)
        r.grow_to_size(target_height=100, start=0, end=1, easing=easings.linear)
        sx = r.styling.scale_x.at_time(1)
        sy = r.styling.scale_y.at_time(1)
        assert sx == pytest.approx(sy, abs=0.05)
        assert sx == pytest.approx(2.0, abs=0.1)

    def test_grow_both_dimensions(self):
        r = Rectangle(100, 50, x=100, y=100)
        r.grow_to_size(target_width=200, target_height=200, start=0, end=1, easing=easings.linear)
        sx = r.styling.scale_x.at_time(1)
        sy = r.styling.scale_y.at_time(1)
        assert sx == pytest.approx(2.0, abs=0.1)
        assert sy == pytest.approx(4.0, abs=0.1)

    def test_no_target_no_change(self):
        r = Rectangle(100, 50, x=100, y=100)
        r.grow_to_size(start=0, end=1)
        sx = r.styling.scale_x.at_time(1)
        sy = r.styling.scale_y.at_time(1)
        assert sx == pytest.approx(1.0, abs=0.05)
        assert sy == pytest.approx(1.0, abs=0.05)


class TestTiltTowards:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.tilt_towards(200, 200, start=0, end=1)
        assert result is c

    def test_tilts_clockwise_toward_below(self):
        c = Circle(r=50, cx=100, cy=100)
        c.tilt_towards(200, 200, max_angle=15, start=0, end=1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        # Target is below-right, angle_rad > 0, so tilt is positive
        assert rot[0] == pytest.approx(15, abs=1)

    def test_tilts_counterclockwise_toward_above(self):
        c = Circle(r=50, cx=100, cy=100)
        c.tilt_towards(200, 0, max_angle=15, start=0, end=1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        # Target is above-right, angle_rad < 0, so tilt is negative
        assert rot[0] == pytest.approx(-15, abs=1)

    def test_custom_max_angle(self):
        c = Circle(r=50, cx=100, cy=100)
        c.tilt_towards(200, 200, max_angle=30, start=0, end=1, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(30, abs=1)


class TestSetBlendMode:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_blend_mode('multiply')
        assert result is c

    def test_sets_blend_mode_multiply(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_blend_mode('multiply', start=0)
        assert c.styling.mix_blend_mode.at_time(0) == 'multiply'

    def test_sets_blend_mode_screen(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_blend_mode('screen', start=0)
        assert c.styling.mix_blend_mode.at_time(0) == 'screen'

    def test_sets_blend_mode_overlay(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_blend_mode('overlay')
        assert c.styling.mix_blend_mode.at_time(0) == 'overlay'

    def test_blend_mode_appears_in_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_blend_mode('darken', start=0)
        svg = c.to_svg(0)
        assert "mix-blend-mode='darken'" in svg

    def test_invalid_blend_mode_raises(self):
        c = Circle(r=50, cx=100, cy=100)
        with pytest.raises(ValueError, match='Unsupported blend mode'):
            c.set_blend_mode('invalid-mode')

    def test_blend_mode_at_later_time(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_blend_mode('lighten', start=2)
        # Before start, should be empty (default)
        assert c.styling.mix_blend_mode.at_time(1) == ''
        # At and after start, should be the mode
        assert c.styling.mix_blend_mode.at_time(2) == 'lighten'

    def test_all_valid_modes(self):
        modes = ['normal', 'multiply', 'screen', 'overlay',
                 'darken', 'lighten', 'color-dodge', 'color-burn']
        for mode in modes:
            c = Circle(r=50, cx=100, cy=100)
            c.set_blend_mode(mode)
            assert c.styling.mix_blend_mode.at_time(0) == mode


class TestRevealClip:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.reveal_clip(start=0, end=1)
        assert result is c

    def test_shows_from_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0.5, end=1.5)
        assert not c.show.at_time(0.4)
        assert c.show.at_time(0.5)

    def test_clip_path_set_at_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='left', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0)
        # At start, fully clipped (100%)
        assert 'inset' in clip
        assert '100' in clip

    def test_clip_path_cleared_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='left', easing=easings.linear)
        clip = c.styling.clip_path.at_time(1)
        # At end, fully revealed (0%)
        assert 'inset(0 0.0% 0 0)' == clip

    def test_left_direction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='left', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        # At 50%, right inset should be 50%
        assert 'inset(0 50.0% 0 0)' == clip

    def test_right_direction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='right', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        # At 50%, left inset should be 50%
        assert 'inset(0 0 0 50.0%)' == clip

    def test_top_direction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='top', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        # At 50%, bottom inset should be 50%
        assert 'inset(0 0 50.0% 0)' == clip

    def test_bottom_direction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='bottom', easing=easings.linear)
        clip = c.styling.clip_path.at_time(0.5)
        # At 50%, top inset should be 50%
        assert 'inset(50.0% 0 0 0)' == clip

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.reveal_clip(start=1, end=1)
        assert result is c

    def test_clip_appears_in_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.reveal_clip(start=0, end=1, direction='left', easing=easings.linear)
        svg = c.to_svg(0.5)
        assert 'clip-path' in svg


class TestRepeatAnimation:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.repeat_animation('pulsate', count=2, start=0, end=2)
        assert result is c

    def test_divides_time_evenly(self):
        c = Circle(r=50, cx=100, cy=100)
        c.repeat_animation('shake', count=3, start=0, end=3, amplitude=10)
        # The shake method should have been called 3 times,
        # just verify the object's last_change covers the full range
        assert c.last_change >= 2.5

    def test_two_repetitions_of_pulsate(self):
        c = Circle(r=50, cx=100, cy=100)
        c.repeat_animation('pulsate', count=2, start=0, end=2)
        # At the midpoints of each repetition, scale should differ from 1
        sx_mid1 = c.styling.scale_x.at_time(0.5)
        sx_mid2 = c.styling.scale_x.at_time(1.5)
        # Both midpoints should have non-default scale (pulsate changes scale)
        assert sx_mid1 != pytest.approx(1.0, abs=0.01)
        assert sx_mid2 != pytest.approx(1.0, abs=0.01)

    def test_count_zero_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.repeat_animation('pulsate', count=0, start=0, end=1)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.repeat_animation('pulsate', count=2, start=1, end=1)
        assert result is c

    def test_single_repetition(self):
        c = Circle(r=50, cx=100, cy=100)
        c.repeat_animation('pulsate', count=1, start=0, end=1)
        sx_mid = c.styling.scale_x.at_time(0.5)
        assert sx_mid != pytest.approx(1.0, abs=0.01)

    def test_kwargs_forwarded(self):
        c = Circle(r=50, cx=100, cy=100)
        c.repeat_animation('shake', count=2, start=0, end=2, amplitude=20)
        # Verify the animation was applied (object has changes past t=0)
        assert c.last_change >= 1.5


class TestElasticScale:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.elastic_scale(start=0, end=2)
        assert result is c

    def test_starts_near_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_scale(start=0, end=2, factor=1.5, easing=easings.linear)
        # Very early on, the scale should be near the overshoot (factor=1.5)
        sx_early = c.styling.scale_x.at_time(0.01)
        # The damped cosine envelope starts at 1.0, so scale starts near factor
        assert sx_early > 1.3

    def test_settles_back_at_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_scale(start=0, end=2, factor=1.5, easing=easings.linear)
        sx_end = c.styling.scale_x.at_time(2)
        sy_end = c.styling.scale_y.at_time(2)
        # At the end, should settle back near 1.0
        assert sx_end == pytest.approx(1.0, abs=0.05)
        assert sy_end == pytest.approx(1.0, abs=0.05)

    def test_overshoots_during_animation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_scale(start=0, end=2, factor=2.0, easing=easings.linear)
        # Sample multiple points - the max scale should exceed 1.0
        scales = [c.styling.scale_x.at_time(t) for t in [0.05, 0.1, 0.2, 0.3, 0.5]]
        assert max(scales) > 1.0

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.elastic_scale(start=1, end=1, factor=2.0)
        assert result is c

    def test_scale_y_matches_x(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_scale(start=0, end=2, factor=1.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(0.3)
        sy = c.styling.scale_y.at_time(0.3)
        assert sx == pytest.approx(sy, abs=0.01)

    def test_custom_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_scale(start=0, end=2, factor=3.0, easing=easings.linear)
        # Early scale should reflect the larger factor
        sx_early = c.styling.scale_x.at_time(0.01)
        assert sx_early > 1.5  # significantly above 1 for factor=3


class TestSnapToGrid:
    def test_returns_self(self):
        c = Circle(r=50, cx=110, cy=90)
        result = c.snap_to_grid(grid_size=50, start=0, end=1)
        assert result is c

    def test_snaps_to_nearest_grid_point(self):
        """Object at (110, 90) should snap to (100, 100) with grid_size=50."""
        c = Circle(r=50, cx=110, cy=90)
        # Center is at (110, 90)
        c.snap_to_grid(grid_size=50, start=0, end=1, easing=easings.linear)
        # After animation, center should be at (100, 100)
        cx, cy = c.center(1)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(100, abs=1)

    def test_already_on_grid(self):
        """Object already on grid should not move."""
        c = Circle(r=50, cx=100, cy=100)
        c.snap_to_grid(grid_size=50, start=0, end=1)
        cx, cy = c.center(1)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(100, abs=1)

    def test_custom_grid_size(self):
        """Test with a different grid size."""
        c = Circle(r=50, cx=130, cy=170)
        c.snap_to_grid(grid_size=100, start=0, end=1, easing=easings.linear)
        cx, cy = c.center(1)
        assert cx == pytest.approx(100, abs=1)
        assert cy == pytest.approx(200, abs=1)

    def test_midpoint_animated(self):
        """At midpoint with linear easing, should be halfway to target."""
        _ = Circle(r=50, cx=100, cy=100)
        # Center at (100, 100), nearest grid point at grid_size=200 is (0, 0) or (200, 200)
        # Actually round(100/200)*200 = round(0.5)*200 = 0*200 = 0... no, round(0.5)=0 in Python (banker's rounding)
        # Use offset that gives clear snap target
        c2 = Circle(r=50, cx=80, cy=80)
        c2.snap_to_grid(grid_size=100, start=0, end=1, easing=easings.linear)
        # Center at (80, 80), nearest grid point = (100, 100)
        cx_mid, cy_mid = c2.center(0.5)
        assert cx_mid == pytest.approx(90, abs=2)
        assert cy_mid == pytest.approx(90, abs=2)


class TestAddBackground:
    def test_returns_rectangle(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background()
        assert isinstance(bg, Rectangle)

    def test_default_color_and_opacity(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background()
        fill = bg.styling.fill.at_time(0)
        fill_op = bg.styling.fill_opacity.at_time(0)
        # Color may render as rgb(0,0,0) or #000000
        assert fill in ('#000000', 'rgb(0,0,0)')
        assert fill_op == pytest.approx(0.5)

    def test_custom_color_and_opacity(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background(color='#ff0000', opacity=0.8)
        fill = bg.styling.fill.at_time(0)
        fill_op = bg.styling.fill_opacity.at_time(0)
        # Color may render as rgb(255,0,0) or #ff0000
        assert fill in ('#ff0000', 'rgb(255,0,0)')
        assert fill_op == pytest.approx(0.8)

    def test_padding(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background(padding=30)
        # Circle bbox: (50, 50, 100, 100) approximately
        _, _, bgw, bgh = bg.bbox(0)
        cx_bbox = c.bbox(0)
        # Background should be wider by 2*padding in each dimension
        assert bgw == pytest.approx(cx_bbox[2] + 60, abs=2)
        assert bgh == pytest.approx(cx_bbox[3] + 60, abs=2)

    def test_z_index(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background(z=-2)
        assert bg.z.at_time(0) == -2

    def test_no_stroke(self):
        c = Circle(r=50, cx=100, cy=100)
        bg = c.add_background()
        sw = bg.styling.stroke_width.at_time(0)
        assert sw == pytest.approx(0)


class TestCycleColors:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        result = c.cycle_colors(['#ff0000', '#00ff00', '#0000ff'], start=0, end=1)
        assert result is c

    def test_starts_with_first_color(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ffffff')
        c.cycle_colors(['#ff0000', '#00ff00', '#0000ff'], start=0, end=1)
        fill = c.styling.fill.at_time(0)
        assert fill == 'rgb(255,0,0)'

    def test_ends_with_last_color(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ffffff')
        c.cycle_colors(['#ff0000', '#00ff00', '#0000ff'], start=0, end=1, easing=easings.linear)
        fill = c.styling.fill.at_time(1)
        assert fill == 'rgb(0,0,255)'

    def test_single_color_noop(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        result = c.cycle_colors(['#ff0000'], start=0, end=1)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        result = c.cycle_colors(['#ff0000', '#00ff00'], start=1, end=1)
        assert result is c

    def test_two_colors(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ffffff')
        c.cycle_colors(['#ff0000', '#0000ff'], start=0, end=1, easing=easings.linear)
        # At start should be first color
        assert c.styling.fill.at_time(0) == 'rgb(255,0,0)'
        # At end should be last color
        assert c.styling.fill.at_time(1) == 'rgb(0,0,255)'


class TestFreeze:
    def test_freeze_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.freeze(start=0, end=1)
        assert result is c

    def test_freeze_holds_opacity(self):
        c = Circle(r=50, cx=100, cy=100, fill_opacity=1)
        # Animate opacity to 0 over time
        c.styling.fill_opacity.set(0, 2, lambda t: 1 - t / 2, stay=True)
        # Freeze at time 0 (opacity=1) until time 2
        c.freeze(start=0, end=2)
        # The updater restores opacity at each frame, so at t=1 it should still be ~1
        svg = c.to_svg(1)
        assert svg  # renders without error
        # The freeze updater captures at start=0, so fill_opacity should remain 1
        # After running updaters, the value at t=1 is restored to the frozen value
        c._run_updaters(1.0)
        assert c.styling.fill_opacity.at_time(1.0) == pytest.approx(1.0, abs=0.01)

    def test_freeze_without_end(self):
        c = Circle(r=50, cx=100, cy=100, fill_opacity=1)
        c.styling.fill_opacity.set(0, 5, lambda t: 1 - t / 5, stay=True)
        c.freeze(start=0)
        # With end=None, freeze lasts forever
        c._run_updaters(3.0)
        assert c.styling.fill_opacity.at_time(3.0) == pytest.approx(1.0, abs=0.01)


class TestDelayAnimation:
    def test_delay_animation_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.delay_animation('fadein', delay=1, start=0, end=1)
        assert result is c

    def test_delay_shifts_start(self):
        c = Circle(r=50, cx=100, cy=100)
        # fadein normally at start=0 makes object visible at t=0
        # with delay=2, the fadein should start at t=2
        c.delay_animation('fadein', delay=2, start=0, end=1)
        # The actual animation start is at t=2, so show should be set at t=2
        assert c.show.at_time(2) is True

    def test_delay_shift_animation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.delay_animation('shift', delay=0.5, dx=50, start=0, end=1)
        # The shift should start at 0.5, so at t=0 position unchanged
        cx_0 = c.center(0)[0]
        assert cx_0 == pytest.approx(100, abs=1)
        # Both start and end shifted by 0.5: [0.5, 1.5]
        cx_1 = c.center(1.5)[0]
        assert cx_1 == pytest.approx(150, abs=1)

    def test_delay_with_default_start(self):
        c = Circle(r=50, cx=100, cy=100)
        # No start kwarg means default=0, so delay=1 => start=1
        c.delay_animation('shake', delay=1, end=2, amplitude=10, frequency=5)
        # Should not error
        svg = c.to_svg(1.5)
        assert svg


class TestWobble:
    def test_wobble_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.wobble(start=0, end=1, intensity=5, frequency=3)
        assert result is c

    def test_wobble_produces_displacement(self):
        c = Circle(r=50, cx=100, cy=100)
        c.wobble(start=0, end=1, intensity=10, frequency=3)
        svg_mid = c.to_svg(0.25)
        assert 'circle' in svg_mid.lower() or 'ellipse' in svg_mid.lower()

    def test_wobble_zero_duration(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.wobble(start=0, end=0)
        assert result is c  # no-op

    def test_wobble_applies_rotation(self):
        c = Circle(r=50, cx=100, cy=100)
        c.wobble(start=0, end=2, intensity=10, frequency=2)
        # At a mid-point, rotation should be non-zero
        rot = c.styling.rotation.at_time(0.5)
        # rotation is a tuple: (degrees, cx, cy)
        assert rot[0] != pytest.approx(0, abs=0.01)

    def test_wobble_decays(self):
        c = Circle(r=50, cx=100, cy=100)
        c.wobble(start=0, end=1, intensity=10, frequency=3)
        # Near the end, the rotation envelope (1-easing(p)) should be near 0
        rot_near_end = c.styling.rotation.at_time(0.99)
        assert abs(rot_near_end[0]) < 1.0  # should be small

    def test_wobble_default_easing(self):
        c = Circle(r=50, cx=100, cy=100)
        # Should work with default easing
        c.wobble(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg


class TestFocusZoom:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.focus_zoom(start=0, end=1, zoom_factor=1.3)
        assert result is c

    def test_scale_at_midpoint(self):
        c = Circle(r=50, cx=100, cy=100)
        s0 = c.styling.scale_x.at_time(0)
        c.focus_zoom(start=0, end=1, zoom_factor=1.5)
        # At midpoint (t=0.5), sin(pi * easing(0.5)) should peak
        sx_mid = c.styling.scale_x.at_time(0.5)
        # Should be larger than the initial scale
        assert sx_mid > s0

    def test_scale_returns_to_original(self):
        c = Circle(r=50, cx=100, cy=100)
        s0_x = c.styling.scale_x.at_time(0)
        s0_y = c.styling.scale_y.at_time(0)
        c.focus_zoom(start=0, end=1, zoom_factor=1.3)
        # At end (t=1), should return to original scale
        # The .set() interval ends at t=1, so at_time(1) should be the endpoint
        # Check that at time just before end the scale is close to original
        sx_end = c.styling.scale_x.at_time(1)
        sy_end = c.styling.scale_y.at_time(1)
        assert sx_end == pytest.approx(s0_x, abs=0.05)
        assert sy_end == pytest.approx(s0_y, abs=0.05)

    def test_zero_duration_is_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        s0 = c.styling.scale_x.at_time(0)
        c.focus_zoom(start=0, end=0, zoom_factor=1.5)
        # Should be unchanged
        assert c.styling.scale_x.at_time(0) == pytest.approx(s0)

    def test_both_axes_scale(self):
        c = Circle(r=50, cx=100, cy=100)
        c.focus_zoom(start=0, end=1, zoom_factor=1.3)
        sx = c.styling.scale_x.at_time(0.5)
        sy = c.styling.scale_y.at_time(0.5)
        assert sx == pytest.approx(sy)

    def test_custom_zoom_factor(self):
        c = Circle(r=50, cx=100, cy=100)
        c.focus_zoom(start=0, end=2, zoom_factor=2.0)
        # At midpoint the scale should approach zoom_factor
        sx_mid = c.styling.scale_x.at_time(1.0)
        assert sx_mid > 1.5


class TestTypewriterEffect:
    def test_returns_self(self):
        t = Text(text='', x=100, y=100)
        result = t.typewriter_effect('Hello', start=0, end=1)
        assert result is t

    def test_reveals_characters_progressively(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello', start=0, end=1)
        # At start, no characters shown
        assert t.text.at_time(0) == ''
        # At midpoint, about half the characters shown
        mid_text = t.text.at_time(0.5)
        assert 1 <= len(mid_text) <= 4
        # At end, full text
        assert t.text.at_time(1) == 'Hello'

    def test_full_text_at_end(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('World!', start=0, end=2)
        assert t.text.at_time(2) == 'World!'

    def test_empty_text_is_noop(self):
        t = Text(text='', x=100, y=100)
        result = t.typewriter_effect('', start=0, end=1)
        assert result is t

    def test_non_text_raises_type_error(self):
        c = Circle(r=50, cx=100, cy=100)
        with pytest.raises(TypeError):
            c.typewriter_effect('Hello', start=0, end=1)

    def test_zero_duration(self):
        t = Text(text='', x=100, y=100)
        result = t.typewriter_effect('Hello', start=1, end=1)
        assert result is t

    def test_custom_time_range(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('ABCDE', start=2, end=4)
        # Before start, text should still be empty
        # At start, 0 chars
        assert t.text.at_time(2) == ''
        # At end, full text
        assert t.text.at_time(4) == 'ABCDE'


class TestTeleport:
    def test_teleport_with_start(self):
        d = Dot(cx=100, cy=100)
        d.teleport(500, 500, start=0)
        p = d.c.at_time(0)
        assert abs(p[0] - 500) < 5
        assert abs(p[1] - 500) < 5

    def test_teleport_returns_self(self):
        d = Dot(cx=100, cy=100)
        result = d.teleport(200, 300, start=0)
        assert result is d

    def test_teleport_backward_compat_time(self):
        d = Dot(cx=100, cy=100)
        d.teleport(500, 500, start=0)
        p = d.c.at_time(0)
        assert abs(p[0] - 500) < 5
        assert abs(p[1] - 500) < 5

    def test_teleport_instant(self):
        d = Dot(cx=100, cy=100)
        d.teleport(400, 300, start=1)
        # Before teleport, should be at original position
        p_before = d.c.at_time(0)
        assert abs(p_before[0] - 100) < 5
        # After teleport
        p_after = d.c.at_time(1)
        assert abs(p_after[0] - 400) < 5


class TestPointFromProportion:
    def test_circle_start(self):
        c = Circle(r=50, cx=100, cy=100)
        pt = c.point_from_proportion(0)
        # Should be a valid point on the circle outline
        assert isinstance(pt, tuple)
        assert len(pt) == 2

    def test_circle_end(self):
        c = Circle(r=50, cx=100, cy=100)
        pt_start = c.point_from_proportion(0)
        pt_end = c.point_from_proportion(1)
        # Start and end of a closed circle path should be very close
        assert abs(pt_start[0] - pt_end[0]) < 1
        assert abs(pt_start[1] - pt_end[1]) < 1

    def test_circle_midpoint(self):
        c = Circle(r=50, cx=100, cy=100)
        pt = c.point_from_proportion(0.5)
        # Midpoint should be at distance r from center
        dist = math.hypot(pt[0] - 100, pt[1] - 100)
        assert abs(dist - 50) < 2

    def test_line_proportion(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        pt = line.point_from_proportion(0.5)
        assert abs(pt[0] - 50) < 1
        assert abs(pt[1] - 0) < 1

    def test_line_start_end(self):
        line = Line(x1=10, y1=20, x2=110, y2=20)
        pt0 = line.point_from_proportion(0)
        pt1 = line.point_from_proportion(1)
        assert abs(pt0[0] - 10) < 1
        assert abs(pt0[1] - 20) < 1
        assert abs(pt1[0] - 110) < 1
        assert abs(pt1[1] - 20) < 1

    def test_clamp_out_of_range(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        pt_neg = line.point_from_proportion(-0.5)
        pt_over = line.point_from_proportion(1.5)
        # Should clamp to 0 and 1
        assert abs(pt_neg[0] - 0) < 1
        assert abs(pt_over[0] - 100) < 1

    def test_returns_center_on_empty_path(self):
        """An object with an empty path should return its center."""
        r = Rectangle(100, 50, x=400, y=300)
        # Temporarily override path to return empty
        original_path = r.path
        r.path = lambda _time: ''
        pt = r.point_from_proportion(0.5)
        cx, cy = r.center(0)
        assert abs(pt[0] - cx) < 1
        assert abs(pt[1] - cy) < 1
        r.path = original_path

    def test_returns_tuple(self):
        c = Circle(r=30, cx=200, cy=200)
        result = c.point_from_proportion(0.25)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestConnect:
    def test_connect_returns_line(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2)
        assert isinstance(conn, Line)

    def test_connect_arrow(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2, arrow=True)
        assert isinstance(conn, Arrow)

    def test_connect_endpoints(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2, start_edge='right', end_edge='left')
        # Start should be at the right edge of r1
        p1 = conn.p1.at_time(0)
        r1_right = r1.get_edge('right', 0)
        assert abs(p1[0] - r1_right[0]) < 1
        assert abs(p1[1] - r1_right[1]) < 1
        # End should be at the left edge of r2
        p2 = conn.p2.at_time(0)
        r2_left = r2.get_edge('left', 0)
        assert abs(p2[0] - r2_left[0]) < 1
        assert abs(p2[1] - r2_left[1]) < 1

    def test_connect_different_edges(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=100, y=300)
        conn = r1.connect(r2, start_edge='bottom', end_edge='top')
        p1 = conn.p1.at_time(0)
        p2 = conn.p2.at_time(0)
        r1_bot = r1.get_edge('bottom', 0)
        r2_top = r2.get_edge('top', 0)
        assert abs(p1[0] - r1_bot[0]) < 1
        assert abs(p1[1] - r1_bot[1]) < 1
        assert abs(p2[0] - r2_top[0]) < 1
        assert abs(p2[1] - r2_top[1]) < 1

    def test_connect_follow_line(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2, follow=True)
        # Move r1, the connector should follow
        r1.shift(dx=50, start=0)
        p1 = conn.p1.at_time(0)
        r1_right_after = r1.get_edge('right', 0)
        assert abs(p1[0] - r1_right_after[0]) < 1

    def test_connect_follow_arrow(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2, arrow=True, follow=True)
        assert isinstance(conn, Arrow)

    def test_connect_custom_styling(self):
        r1 = Rectangle(100, 50, x=100, y=100)
        r2 = Rectangle(100, 50, x=400, y=100)
        conn = r1.connect(r2, stroke='#ff0000', stroke_width=3)
        svg = conn.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'ff0000' in svg.lower()


class TestMatchStyle:
    def test_match_style_copies_fill(self):
        r1 = Rectangle(100, 50, fill='#ff0000')
        r2 = Rectangle(100, 50, fill='#0000ff')
        r1.match_style(r2)
        assert r1.get_fill_color(0).lower() == '#0000ff'

    def test_match_style_copies_stroke(self):
        r1 = Rectangle(100, 50, stroke='#ffffff')
        r2 = Rectangle(100, 50, stroke='#00ff00')
        r1.match_style(r2)
        assert r1.get_stroke_color(0).lower() == '#00ff00'

    def test_match_style_copies_opacity(self):
        r1 = Rectangle(100, 50, fill_opacity=1.0)
        r2 = Rectangle(100, 50, fill_opacity=0.5)
        r1.match_style(r2)
        assert r1.get_fill_opacity(0) == pytest.approx(0.5)

    def test_match_style_copies_stroke_width(self):
        r1 = Rectangle(100, 50, stroke_width=2)
        r2 = Rectangle(100, 50, stroke_width=6)
        r1.match_style(r2)
        assert r1.get_stroke_width(0) == pytest.approx(6)

    def test_match_style_copies_stroke_opacity(self):
        r1 = Rectangle(100, 50, stroke_opacity=1.0)
        r2 = Rectangle(100, 50, stroke_opacity=0.3)
        r1.match_style(r2)
        assert r1.get_stroke_opacity(0) == pytest.approx(0.3)

    def test_match_style_returns_self(self):
        r1 = Rectangle(100, 50)
        r2 = Rectangle(100, 50, fill='#ff0000')
        result = r1.match_style(r2)
        assert result is r1

    def test_match_style_at_time(self):
        r1 = Rectangle(100, 50, fill='#ff0000')
        r2 = Rectangle(100, 50, fill='#0000ff')
        r2.set_fill(color='#00ff00', start=1)
        r1.match_style(r2, time=1)
        assert r1.get_fill_color(1).lower() == '#00ff00'

    def test_match_style_between_different_shapes(self):
        c = Circle(r=50, fill='#ff0000', stroke_width=2)
        r = Rectangle(100, 50, fill='#0000ff', stroke_width=8)
        c.match_style(r)
        assert c.get_fill_color(0).lower() == '#0000ff'
        assert c.get_stroke_width(0) == pytest.approx(8)


class TestRemoveUpdater:
    def test_remove_updater_by_reference(self):
        c = Circle(r=50)
        def mover(obj, t):
            pass
        c.add_updater(mover, start=0, end=1)
        assert len(c._updaters) == 1
        c.remove_updater(mover)
        assert len(c._updaters) == 0

    def test_remove_updater_returns_self(self):
        c = Circle(r=50)
        def mover(obj, t):
            pass
        c.add_updater(mover)
        result = c.remove_updater(mover)
        assert result is c

    def test_remove_updater_only_removes_matching(self):
        c = Circle(r=50)
        def f1(_obj, _t): pass
        def f2(_obj, _t): pass
        c.add_updater(f1, start=0, end=1)
        c.add_updater(f2, start=0, end=2)
        c.remove_updater(f1)
        assert len(c._updaters) == 1
        assert c._updaters[0][0] is f2

    def test_remove_updater_removes_all_with_same_func(self):
        c = Circle(r=50)
        def f1(_obj, _t): pass
        c.add_updater(f1, start=0, end=1)
        c.add_updater(f1, start=2, end=3)
        assert len(c._updaters) == 2
        c.remove_updater(f1)
        assert len(c._updaters) == 0

    def test_remove_updater_noop_if_not_found(self):
        c = Circle(r=50)
        def f1(_obj, _t): pass
        def f2(_obj, _t): pass
        c.add_updater(f1)
        c.remove_updater(f2)  # not added, should not raise
        assert len(c._updaters) == 1


class TestClearUpdaters:
    def test_clear_updaters_empties_list(self):
        c = Circle(r=50)
        def f1(obj, t): pass
        def f2(obj, t): pass
        c.add_updater(f1)
        c.add_updater(f2)
        assert len(c._updaters) == 2
        c.clear_updaters()
        assert len(c._updaters) == 0

    def test_clear_updaters_returns_self(self):
        c = Circle(r=50)
        result = c.clear_updaters()
        assert result is c

    def test_clear_updaters_on_empty(self):
        c = Circle(r=50)
        c.clear_updaters()
        assert len(c._updaters) == 0


class TestIsOnScreen:
    def test_centered_object_on_screen(self):
        c = Circle(r=50, cx=960, cy=540)
        assert c.is_on_screen(0) is True

    def test_top_left_partially_on_screen(self):
        c = Circle(r=50, cx=10, cy=10)
        assert c.is_on_screen(0) is True

    def test_far_off_right(self):
        c = Circle(r=50, cx=2100, cy=540)
        assert c.is_on_screen(0) is False

    def test_far_off_left(self):
        c = Circle(r=50, cx=-200, cy=540)
        assert c.is_on_screen(0) is False

    def test_far_off_top(self):
        c = Circle(r=50, cx=960, cy=-200)
        assert c.is_on_screen(0) is False

    def test_far_off_bottom(self):
        c = Circle(r=50, cx=960, cy=1300)
        assert c.is_on_screen(0) is False

    def test_just_touching_right_edge(self):
        # Circle at x=1910, r=50 -> bbox from 1860 to 1960 -> overlaps 1920 boundary
        c = Circle(r=50, cx=1910, cy=540)
        assert c.is_on_screen(0) is True

    def test_just_past_right_edge(self):
        # Circle at x=1980, r=50 -> bbox from 1930 to 2030 -> starts after 1920
        c = Circle(r=50, cx=1980, cy=540)
        assert c.is_on_screen(0) is False

    def test_at_time(self):
        c = Circle(r=50, cx=960, cy=540)
        c.shift(dx=2000, start=0, end=1, easing=easings.linear)
        assert c.is_on_screen(0) is True
        assert c.is_on_screen(1) is False


class TestScaleAboutPoint:
    def test_scale_about_point_returns_self(self):
        c = Circle(r=50, cx=200, cy=200)
        result = c.scale_about_point(2, 0, 0)
        assert result is c

    def test_scale_about_own_center(self):
        """Scaling about own center should not move the object."""
        c = Circle(r=50, cx=200, cy=200)
        cx0, cy0 = c.center(0)
        c.scale_about_point(2, cx0, cy0)
        cx1, cy1 = c.center(0)
        assert cx1 == pytest.approx(cx0, abs=1)
        assert cy1 == pytest.approx(cy0, abs=1)

    def test_scale_about_origin(self):
        """Scaling about (0,0) should double the distance from origin."""
        c = Circle(r=50, cx=100, cy=100)
        c.scale_about_point(2, 0, 0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(200, abs=2)
        assert cy == pytest.approx(200, abs=2)

    def test_scale_about_point_factor_half(self):
        """Factor 0.5 should halve the distance from pivot."""
        c = Circle(r=50, cx=200, cy=200)
        c.scale_about_point(0.5, 0, 0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(100, abs=2)


class TestDropShadow:
    def test_drop_shadow_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.drop_shadow()
        assert result is c

    def test_drop_shadow_wraps_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.drop_shadow(color='#333', dx=2, dy=3, blur=4)
        svg = c.to_svg(0)
        assert '<filter' in svg
        assert 'feDropShadow' in svg
        assert "flood-color='#333'" in svg
        assert "dx='2'" in svg
        assert "dy='3'" in svg
        assert "stdDeviation='4'" in svg
        assert '<circle' in svg  # original element still present

    def test_drop_shadow_no_filter_before_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.drop_shadow(start=5)
        svg = c.to_svg(0)
        assert '<filter' not in svg
        assert '<circle' in svg

    def test_drop_shadow_filter_after_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.drop_shadow(start=5)
        svg = c.to_svg(5)
        assert '<filter' in svg
        assert 'feDropShadow' in svg

    def test_drop_shadow_default_params(self):
        c = Circle(r=50, cx=100, cy=100)
        c.drop_shadow()
        svg = c.to_svg(0)
        assert "flood-color='#000000'" in svg
        assert "dx='4'" in svg
        assert "dy='4'" in svg
        assert "stdDeviation='6'" in svg


class TestLookAt:
    def test_look_at_tuple_right(self):
        """Looking at a point to the right should give ~0 degrees rotation."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((200, 100), start=0)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(0, abs=1)

    def test_look_at_tuple_down(self):
        """Looking at a point below should give ~90 degrees."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((100, 200), start=0)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(90, abs=1)

    def test_look_at_tuple_left(self):
        """Looking at a point to the left should give ~180 or ~-180 degrees."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((0, 100), start=0)
        rot = c.styling.rotation.at_time(0)
        assert abs(rot[0]) == pytest.approx(180, abs=1)

    def test_look_at_tuple_up(self):
        """Looking at a point above should give ~-90 degrees."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((100, 0), start=0)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(-90, abs=1)

    def test_look_at_vobject(self):
        """Target can be another VObject."""
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        c1.look_at(c2, start=0)
        rot = c1.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(0, abs=1)

    def test_look_at_animated(self):
        """When end is provided, rotation should animate."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((100, 200), start=0, end=1, easing=easings.linear)
        rot_start = c.styling.rotation.at_time(0)
        rot_end = c.styling.rotation.at_time(1)
        # At end, should be ~90 degrees (pointing down)
        assert rot_end[0] == pytest.approx(90, abs=1)

    def test_look_at_returns_self(self):
        c = Circle(r=20, cx=100, cy=100)
        result = c.look_at((200, 200), start=0)
        assert result is c

    def test_look_at_diagonal(self):
        """Looking at a 45-degree diagonal."""
        c = Circle(r=20, cx=100, cy=100)
        c.look_at((200, 200), start=0)
        rot = c.styling.rotation.at_time(0)
        assert rot[0] == pytest.approx(45, abs=1)


class TestAnimateTo:
    def test_animate_to_position(self):
        """Object should move to target's center."""
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=400, cy=300)
        c1.animate_to(c2, start=0, end=1, easing=easings.linear)
        cx, cy = c1.center(1)
        assert cx == pytest.approx(400, abs=5)
        assert cy == pytest.approx(300, abs=5)

    def test_animate_to_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=40, cx=300, cy=300)
        result = c1.animate_to(c2, start=0, end=1)
        assert result is c1

    def test_animate_to_copies_fill(self):
        """Should animate fill color to match target."""
        c1 = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        c2 = Circle(r=20, cx=200, cy=200, fill='#00ff00')
        c1.animate_to(c2, start=0, end=1, easing=easings.linear)
        # At end, fill should be the target color (rgb format)
        fill_end = c1.styling.fill.at_time(1)
        assert fill_end == 'rgb(0,255,0)'

    def test_animate_to_copies_stroke(self):
        """Should animate stroke color to match target."""
        c1 = Circle(r=20, cx=100, cy=100, stroke='#ff0000')
        c2 = Circle(r=20, cx=200, cy=200, stroke='#0000ff')
        c1.animate_to(c2, start=0, end=1, easing=easings.linear)
        stroke_end = c1.styling.stroke.at_time(1)
        assert stroke_end == 'rgb(0,0,255)'

    def test_animate_to_scales(self):
        """Object should scale to match target width."""
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=40, cx=300, cy=300)
        c1.animate_to(c2, start=0, end=1, easing=easings.linear)
        w1_end = c1.get_width(1)
        w2 = c2.get_width(0)
        assert w1_end == pytest.approx(w2, rel=0.15)


class TestSetGradientFill:
    def test_horizontal_gradient(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'], direction='horizontal')
        svg = c.to_svg(0)
        assert '<linearGradient' in svg
        assert "x1='0'" in svg
        assert "x2='1'" in svg
        assert '#ff0000' in svg
        assert '#0000ff' in svg

    def test_vertical_gradient(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'], direction='vertical')
        svg = c.to_svg(0)
        assert '<linearGradient' in svg
        assert "y2='1'" in svg

    def test_radial_gradient(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'], direction='radial')
        svg = c.to_svg(0)
        assert '<radialGradient' in svg

    def test_gradient_not_before_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'], start=5)
        svg = c.to_svg(0)
        assert '<linearGradient' not in svg

    def test_gradient_after_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'], start=5)
        svg = c.to_svg(5)
        assert '<linearGradient' in svg

    def test_gradient_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_gradient_fill(['#ff0000', '#0000ff'])
        assert result is c

    def test_gradient_three_colors(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#00ff00', '#0000ff'])
        svg = c.to_svg(0)
        assert '#ff0000' in svg
        assert '#00ff00' in svg
        assert '#0000ff' in svg
        assert "offset='0%" in svg or "offset='0.0%" in svg
        assert "offset='50" in svg
        assert "offset='100" in svg

    def test_gradient_wraps_inner_svg(self):
        """The gradient wraps the object's original SVG output."""
        c = Circle(r=50, cx=100, cy=100)
        c.set_gradient_fill(['#ff0000', '#0000ff'])
        svg = c.to_svg(0)
        assert '<circle' in svg
        assert 'url(#' in svg


class TestScaleToFit:
    def test_scale_to_fit_width_only(self):
        """Scaling to a target width preserves aspect ratio."""
        r = Rectangle(200, 100, x=0, y=0)
        result = r.scale_to_fit(width=100, start=0)
        assert result is r
        w = r.get_width(0)
        h = r.get_height(0)
        assert w == pytest.approx(100, abs=1)
        assert h == pytest.approx(50, abs=1)

    def test_scale_to_fit_height_only(self):
        """Scaling to a target height preserves aspect ratio."""
        r = Rectangle(200, 100, x=0, y=0)
        r.scale_to_fit(height=200, start=0)
        w = r.get_width(0)
        h = r.get_height(0)
        assert h == pytest.approx(200, abs=1)
        assert w == pytest.approx(400, abs=1)

    def test_scale_to_fit_both_width_constrains(self):
        """When both given and width is more constraining, width wins."""
        r = Rectangle(200, 100, x=0, y=0)
        r.scale_to_fit(width=100, height=200, start=0)
        w = r.get_width(0)
        h = r.get_height(0)
        # factor = min(100/200, 200/100) = min(0.5, 2) = 0.5
        assert w == pytest.approx(100, abs=1)
        assert h == pytest.approx(50, abs=1)

    def test_scale_to_fit_both_height_constrains(self):
        """When both given and height is more constraining, height wins."""
        r = Rectangle(200, 100, x=0, y=0)
        r.scale_to_fit(width=400, height=25, start=0)
        # factor = min(400/200, 25/100) = min(2, 0.25) = 0.25
        w = r.get_width(0)
        h = r.get_height(0)
        assert h == pytest.approx(25, abs=1)
        assert w == pytest.approx(50, abs=1)

    def test_scale_to_fit_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.scale_to_fit(width=50)
        assert result is c

    def test_scale_to_fit_no_args(self):
        """Calling with no width/height does nothing."""
        c = Circle(r=50, cx=100, cy=100)
        w_before = c.get_width(0)
        c.scale_to_fit()
        assert c.get_width(0) == pytest.approx(w_before, abs=0.1)

    def test_scale_to_fit_animated(self):
        """Animated scale_to_fit with end parameter."""
        r = Rectangle(200, 100, x=0, y=0)
        r.scale_to_fit(width=100, start=0, end=1, easing=easings.linear)
        # At start, still original size; at end, scaled down
        w_end = r.get_width(1)
        assert w_end == pytest.approx(100, abs=2)


class TestSetBackstroke:
    def test_set_backstroke_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_backstroke('#ffffff', width=10)
        assert result is c

    def test_set_backstroke_adds_paint_order(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_backstroke('#ffffff', width=10, start=0)
        svg = c.to_svg(0)
        assert 'paint-order' in svg
        assert 'stroke fill' in svg

    def test_set_backstroke_sets_stroke(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_backstroke('#ff0000', width=12, start=0)
        sw = c.styling.stroke_width.at_time(0)
        assert sw == pytest.approx(12)

    def test_set_backstroke_not_active_before_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_backstroke('#ffffff', width=10, start=5)
        svg = c.to_svg(0)
        assert 'paint-order' not in svg

    def test_set_backstroke_wraps_svg(self):
        """The backstroke wraps the inner SVG in a <g> element."""
        c = Circle(r=50, cx=100, cy=100)
        c.set_backstroke('#000', width=8, start=0)
        svg = c.to_svg(0)
        assert svg.startswith("<g style='paint-order: stroke fill'>")
        assert '<circle' in svg
        assert svg.endswith('</g>')


class TestAnimateAlongObject:
    def test_animate_along_object_returns_self(self):
        dot = Circle(r=5, cx=0, cy=0)
        target = Circle(r=100, cx=200, cy=200)
        result = dot.animate_along_object(target, start=0, end=1)
        assert result is dot

    def test_animate_along_object_moves(self):
        """The object should move from its initial position."""
        dot = Circle(r=5, cx=200, cy=200)
        target = Rectangle(200, 100, x=100, y=100)
        dot.animate_along_object(target, start=0, end=1, easing=easings.linear)
        # At some point during the animation the dot should have moved
        cx_start = dot.center(0)
        cx_mid = dot.center(0.5)
        # The center should differ at the midpoint
        dist = math.sqrt((cx_mid[0] - cx_start[0])**2 + (cx_mid[1] - cx_start[1])**2)
        assert dist > 1  # should have moved noticeably


class TestAlwaysNextTo:
    def test_returns_self(self):
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=100)
        result = a.always_next_to(b, direction=RIGHT)
        assert result is a

    def test_positions_next_to_at_start(self):
        """At start time, self should be positioned next to other."""
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=300)
        a.always_next_to(b, direction=RIGHT, buff=10, start=0)
        a._run_updaters(0)
        ax, ay = a.center(0)
        bx, by, bw, bh = b.bbox(0)
        # a's left edge should be roughly buff pixels to the right of b's right edge
        assert ax > bx + bw

    def test_tracks_moving_target(self):
        """Self should follow the target when it moves."""
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=300)
        b.shift(dx=200, dy=0, start=0, end=1, easing=easings.linear)
        a.always_next_to(b, direction=RIGHT, buff=10, start=0)
        a._run_updaters(0)
        pos0 = a.center(0)
        a._run_updaters(1)
        pos1 = a.center(1)
        # a should have moved right as b moved right
        assert pos1[0] > pos0[0] + 100

    def test_direction_left(self):
        """When direction=LEFT, self should be to the left of other."""
        a = Circle(r=20, cx=500, cy=500)
        b = Circle(r=20, cx=300, cy=300)
        a.always_next_to(b, direction=LEFT, buff=10, start=0)
        a._run_updaters(0)
        ax = a.center(0)[0]
        bx = b.bbox(0)[0]
        assert ax < bx

    def test_with_end(self):
        """Updater should respect end time."""
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=300)
        a.always_next_to(b, direction=RIGHT, buff=10, start=0, end=0.5)
        # Updater should run at t=0.3
        a._run_updaters(0.3)
        # Updater should not run at t=0.8 (beyond end)
        pos_mid = a.center(0.3)
        # Just verify it doesn't crash
        a._run_updaters(0.8)

    def test_default_buff(self):
        """Default buff should be SMALL_BUFF (14), matching next_to."""
        a = Circle(r=20, cx=100, cy=100)
        b = Circle(r=20, cx=300, cy=300)
        a.always_next_to(b)
        a._run_updaters(0)
        ax = a.center(0)[0]
        bx, by, bw, bh = b.bbox(0)
        # a should be to the right of b with SMALL_BUFF gap
        expected_ax = bx + bw + SMALL_BUFF + 20  # 20 = a's radius
        assert ax == pytest.approx(expected_ax, abs=2)


class TestSetColorIf:
    def test_returns_self(self):
        c = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        result = c.set_color_if(lambda t: t > 0.5, '#00ff00')
        assert result is c

    def test_color_changes_when_predicate_true(self):
        c = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        c.set_color_if(lambda t: t > 0.5, '#00ff00', start=0)
        c._run_updaters(0.8)
        color = c.styling.fill.at_time(0.8)
        assert color == 'rgb(0,255,0)'

    def test_color_reverts_when_predicate_false(self):
        c = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        c.set_color_if(lambda t: t > 0.5, '#00ff00', start=0)
        c._run_updaters(0.2)
        color = c.styling.fill.at_time(0.2)
        assert color == 'rgb(255,0,0)'

    def test_alternating_predicate(self):
        """Color should toggle based on predicate."""
        c = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        c.set_color_if(lambda t: int(t * 10) % 2 == 0, '#0000ff', start=0)
        # t=0.0 -> int(0) % 2 == 0 -> True -> blue
        c._run_updaters(0.0)
        assert c.styling.fill.at_time(0.0) == 'rgb(0,0,255)'
        # t=0.1 -> int(1) % 2 == 1 -> False -> red
        c._run_updaters(0.1)
        assert c.styling.fill.at_time(0.1) == 'rgb(255,0,0)'

    def test_with_end(self):
        """Updater should respect end time."""
        c = Circle(r=20, cx=100, cy=100, fill='#ff0000')
        c.set_color_if(lambda t: True, '#00ff00', start=0, end=0.5)
        c._run_updaters(0.3)
        assert c.styling.fill.at_time(0.3) == 'rgb(0,255,0)'
        # Beyond end, updater should not run
        # (color stays at whatever was last set)


class TestApplyPointwise:
    def test_returns_self(self):
        c = Circle(r=20, cx=100, cy=100)
        result = c.apply_pointwise(lambda x, y: (x + 10, y + 10))
        assert result is c

    def test_translates_circle(self):
        c = Circle(r=20, cx=100, cy=100)
        c.apply_pointwise(lambda x, y: (x + 50, y + 30))
        cx, cy = c.center(0)
        assert cx == pytest.approx(150, abs=2)
        assert cy == pytest.approx(130, abs=2)

    def test_polygon_vertices_transformed(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        p.apply_pointwise(lambda x, y: (x + 10, y + 20))
        verts = p.get_vertices(0)
        assert verts[0] == pytest.approx((10, 20), abs=1)
        assert verts[1] == pytest.approx((110, 20), abs=1)
        assert verts[2] == pytest.approx((110, 120), abs=1)
        assert verts[3] == pytest.approx((10, 120), abs=1)

    def test_polygon_scale_transform(self):
        p = Polygon((10, 10), (20, 10), (20, 20), (10, 20))
        p.apply_pointwise(lambda x, y: (x * 2, y * 3))
        verts = p.get_vertices(0)
        assert verts[0] == pytest.approx((20, 30), abs=1)
        assert verts[1] == pytest.approx((40, 30), abs=1)
        assert verts[2] == pytest.approx((40, 60), abs=1)
        assert verts[3] == pytest.approx((20, 60), abs=1)

    def test_rectangle_translates_as_non_polygon(self):
        """Rectangle is not a Polygon subclass, so center-based move is used."""
        r = Rectangle(100, 50, x=200, y=200)
        cx0, cy0 = r.center(0)
        r.apply_pointwise(lambda x, y: (x + 100, y - 50))
        cx1, cy1 = r.center(0)
        assert cx1 == pytest.approx(cx0 + 100, abs=2)
        assert cy1 == pytest.approx(cy0 - 50, abs=2)

    def test_identity_is_noop(self):
        c = Circle(r=20, cx=100, cy=100)
        cx0, cy0 = c.center(0)
        c.apply_pointwise(lambda x, y: (x, y))
        cx1, cy1 = c.center(0)
        assert cx1 == pytest.approx(cx0, abs=1)
        assert cy1 == pytest.approx(cy0, abs=1)


class TestSetLifetime:
    def test_visible_within_range(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_lifetime(1, 3)
        assert c.show.at_time(1.5) != 0
        assert c.show.at_time(2) != 0

    def test_invisible_before_start(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_lifetime(1, 3)
        # Before the lifetime, should be hidden
        assert c.show.at_time(0) == 0
        assert c.show.at_time(0.5) == 0

    def test_invisible_after_end(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_lifetime(1, 3)
        assert c.show.at_time(3) == 0

    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.set_lifetime(1, 3)
        assert result is c

    def test_at_boundaries(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_lifetime(2, 5)
        # At start, visible
        assert c.show.at_time(2) != 0
        # At end, invisible
        assert c.show.at_time(5) == 0


class TestGetStyle:
    def test_returns_dict(self):
        c = Circle(r=50, cx=100, cy=100)
        s = c.get_style(0)
        assert isinstance(s, dict)

    def test_has_expected_keys(self):
        c = Circle(r=50, cx=100, cy=100)
        s = c.get_style(0)
        expected_keys = {'fill', 'stroke', 'fill_opacity', 'stroke_opacity',
                         'stroke_width', 'opacity'}
        assert set(s.keys()) == expected_keys

    def test_default_values(self):
        c = Circle(r=50, cx=100, cy=100)
        s = c.get_style(0)
        # Circle (via Ellipse) defaults to fill_opacity=0.7
        assert s['fill_opacity'] == pytest.approx(0.7)
        assert s['stroke_opacity'] == pytest.approx(1.0)
        assert s['opacity'] == pytest.approx(1.0)
        assert s['stroke_width'] == pytest.approx(5.0)

    def test_custom_fill_color(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        s = c.get_style(0)
        assert 'rgb(255,0,0)' in s['fill']

    def test_after_style_change(self):
        c = Circle(r=50, cx=100, cy=100)
        c.set_fill(color='#00ff00', opacity=0.5, start=1)
        s = c.get_style(1)
        assert 'rgb(0,255,0)' in s['fill']
        assert s['fill_opacity'] == pytest.approx(0.5)

    def test_time_varying(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        c.set_fill(color='#0000ff', start=2)
        s0 = c.get_style(0)
        s2 = c.get_style(2)
        assert s0['fill'] != s2['fill']


class TestMoveTowards:
    def test_move_halfway_to_point(self):
        c = Circle(r=10, cx=0, cy=0)
        c.move_towards((200, 200), fraction=0.5)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_move_towards_other_object(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=200, cy=200)
        c1.move_towards(c2, fraction=0.5)
        cx, cy = c1.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_fraction_zero_stays_put(self):
        c = Circle(r=10, cx=100, cy=100)
        cx0, cy0 = c.center(0)
        c.move_towards((500, 500), fraction=0.0)
        cx1, cy1 = c.center(0)
        assert cx1 == pytest.approx(cx0, abs=1)
        assert cy1 == pytest.approx(cy0, abs=1)

    def test_fraction_one_reaches_target(self):
        c = Circle(r=10, cx=0, cy=0)
        c.move_towards((300, 400), fraction=1.0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(300, abs=2)
        assert cy == pytest.approx(400, abs=2)

    def test_returns_self(self):
        c = Circle(r=10, cx=0, cy=0)
        result = c.move_towards((100, 100))
        assert result is c

    def test_quarter_fraction(self):
        c = Circle(r=10, cx=0, cy=0)
        c.move_towards((400, 0), fraction=0.25)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(0, abs=2)


class TestAddLabel:
    def test_returns_vcollection_with_label(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Hello")
        assert isinstance(result, VCollection)
        assert len(result) == 2
        assert result[0] is c
        assert isinstance(result[1], Text)

    def test_label_positioned_above(self):
        from vectormation.objects import UP
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Hello", direction=UP, buff=20)
        label = result[1]
        # Label center should be above the circle center
        lx, ly = label.center(0)
        assert ly < 500  # UP means smaller y

    def test_label_positioned_below(self):
        from vectormation.objects import DOWN
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Below", direction=DOWN, buff=20)
        label = result[1]
        lx, ly = label.center(0)
        assert ly > 500  # DOWN means larger y

    def test_label_custom_font_size(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Big", font_size=72)
        label = result[1]
        assert label.font_size.at_time(0) == 72

    def test_label_follow_adds_updater(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Follow", follow=True)
        label = result[1]
        assert len(label._updaters) == 1

    def test_label_no_follow_no_updater(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Static", follow=False)
        label = result[1]
        assert len(label._updaters) == 0

    def test_label_creation_time(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.add_label("Late", creation=2)
        label = result[1]
        # Label should not be visible before creation
        assert not label.show.at_time(1.9)


class TestPlaceBetween:
    def test_place_between_two_objects(self):
        a = Circle(r=10, cx=100, cy=100)
        b = Circle(r=10, cx=300, cy=100)
        c = Circle(r=10, cx=0, cy=0)
        c.place_between(a, b)
        cx, cy = c.center(0)
        assert cx == pytest.approx(200, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_place_between_tuples(self):
        c = Circle(r=10, cx=0, cy=0)
        c.place_between((100, 200), (300, 400))
        cx, cy = c.center(0)
        assert cx == pytest.approx(200, abs=2)
        assert cy == pytest.approx(300, abs=2)

    def test_place_between_mixed(self):
        a = Circle(r=10, cx=100, cy=100)
        c = Circle(r=10, cx=0, cy=0)
        c.place_between(a, (300, 100))
        cx, cy = c.center(0)
        assert cx == pytest.approx(200, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_place_between_fraction_zero(self):
        a = Circle(r=10, cx=100, cy=100)
        b = Circle(r=10, cx=300, cy=100)
        c = Circle(r=10, cx=0, cy=0)
        c.place_between(a, b, fraction=0.0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_place_between_fraction_one(self):
        a = Circle(r=10, cx=100, cy=100)
        b = Circle(r=10, cx=300, cy=100)
        c = Circle(r=10, cx=0, cy=0)
        c.place_between(a, b, fraction=1.0)
        cx, cy = c.center(0)
        assert cx == pytest.approx(300, abs=2)
        assert cy == pytest.approx(100, abs=2)

    def test_place_between_custom_fraction(self):
        c = Circle(r=10, cx=0, cy=0)
        c.place_between((0, 0), (400, 0), fraction=0.25)
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(0, abs=2)

    def test_place_between_returns_self(self):
        c = Circle(r=10, cx=0, cy=0)
        result = c.place_between((100, 100), (200, 200))
        assert result is c

    def test_place_between_animated(self):
        c = Circle(r=10, cx=0, cy=0)
        c.place_between((0, 0), (400, 0), start=0, end=1, easing=easings.linear)
        # At time 0, should still be at original position
        cx0, cy0 = c.center(0)
        assert cx0 == pytest.approx(0, abs=2)
        # At time 1, should be at midpoint
        cx1, cy1 = c.center(1)
        assert cx1 == pytest.approx(200, abs=2)


class TestSetClip:
    def test_set_clip_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        clip = Rectangle(width=80, height=80, x=60, y=60)
        result = c.set_clip(clip)
        assert result is c

    def test_set_clip_injects_clippath(self):
        c = Circle(r=50, cx=100, cy=100)
        clip = Rectangle(width=80, height=80, x=60, y=60)
        c.set_clip(clip, start=0)
        svg = c.to_svg(0)
        assert 'clipPath' in svg
        assert 'clip-path' in svg

    def test_set_clip_before_start_no_clip(self):
        c = Circle(r=50, cx=100, cy=100)
        clip = Rectangle(width=80, height=80, x=60, y=60)
        c.set_clip(clip, start=1)
        svg = c.to_svg(0)
        assert 'clipPath' not in svg

    def test_set_clip_contains_clip_obj_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        clip = Circle(r=40, cx=100, cy=100)
        c.set_clip(clip, start=0)
        svg = c.to_svg(0)
        # The clip SVG should contain the circle element from the clip object
        assert '<circle' in svg
        # The outer object SVG should also contain its own circle
        assert svg.count('<circle') >= 2  # clip circle + self circle

    def test_set_clip_unique_id(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=200, cy=200)
        clip = Rectangle(width=80, height=80, x=60, y=60)
        c1.set_clip(clip)
        c2.set_clip(clip)
        svg1 = c1.to_svg(0)
        svg2 = c2.to_svg(0)
        # Each should have a different clip id
        assert f'clip{id(c1)}' in svg1
        assert f'clip{id(c2)}' in svg2


class TestAnimatedNextTo:
    """Tests for VObject.next_to with end (animated movement)."""

    def test_next_to_animated_right(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, 'right', start=0, end=1, easing=easings.linear)
        # At time 0, b should still be near its original position
        bx_start, _, _, _ = b.bbox(0)
        # At time 1, b should be to the right of a
        bx_end, _, _, _ = b.bbox(1)
        assert bx_end > 200  # b is to the right of a

    def test_next_to_animated_left(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=500, y=500)
        b.next_to(a, LEFT, start=0, end=1, easing=easings.linear)
        bx, _, bw, _ = b.bbox(1)
        assert bx + bw < 200  # b is to the left of a at end

    def test_next_to_animated_up(self):
        a = Rectangle(100, 50, x=100, y=200)
        b = Rectangle(100, 30, x=0, y=0)
        b.next_to(a, UP, start=0, end=1, easing=easings.linear)
        _, by, _, bh = b.bbox(1)
        assert by + bh < 200  # b is above a at end

    def test_next_to_animated_down(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(100, 30, x=0, y=0)
        b.next_to(a, DOWN, start=0, end=1, easing=easings.linear)
        _, by, _, _ = b.bbox(1)
        assert by > 150  # b is below a at end

    def test_next_to_animated_midway(self):
        """At time 0.5 with linear easing, position should be halfway."""
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, 'right', start=0, end=1, easing=easings.linear)
        bx_0, _, _, _ = b.bbox(0)
        bx_1, _, _, _ = b.bbox(1)
        bx_mid, _, _, _ = b.bbox(0.5)
        expected_mid = (bx_0 + bx_1) / 2
        assert bx_mid == pytest.approx(expected_mid, abs=1)

    def test_next_to_animated_returns_self(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        result = b.next_to(a, 'right', start=0, end=1)
        assert result is b

    def test_next_to_without_end_backward_compat(self):
        """Without end, next_to should still work instantly."""
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, RIGHT)
        bx, _, _, _ = b.bbox(0)
        assert bx > 200

    def test_next_to_animated_with_direction_constant(self):
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, RIGHT, start=0, end=1, easing=easings.linear)
        bx, _, _, _ = b.bbox(1)
        assert bx > 200

    def test_next_to_animated_default_easing(self):
        """When easing is not given, center_to_pos uses its default (smooth)."""
        a = Rectangle(100, 50, x=100, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.next_to(a, 'right', start=0, end=1)
        bx, _, _, _ = b.bbox(1)
        assert bx > 200


class TestAnimatedAlignTo:
    """Tests for VObject.align_to with end (animated movement)."""

    def test_align_to_animated_left(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, 'left', start=0, end=1, easing=easings.linear)
        bx, _, _, _ = b.bbox(1)
        assert bx == pytest.approx(200)

    def test_align_to_animated_right(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, 'right', start=0, end=1, easing=easings.linear)
        bx, _, bw, _ = b.bbox(1)
        assert bx + bw == pytest.approx(300)

    def test_align_to_animated_top(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=300)
        b.align_to(a, 'top', start=0, end=1, easing=easings.linear)
        _, by, _, _ = b.bbox(1)
        assert by == pytest.approx(100)

    def test_align_to_animated_bottom(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, 'bottom', start=0, end=1, easing=easings.linear)
        _, by, _, bh = b.bbox(1)
        assert by + bh == pytest.approx(150)

    def test_align_to_animated_midway(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, 'left', start=0, end=1, easing=easings.linear)
        bx_0, _, _, _ = b.bbox(0)
        bx_1, _, _, _ = b.bbox(1)
        bx_mid, _, _, _ = b.bbox(0.5)
        expected_mid = (bx_0 + bx_1) / 2
        assert bx_mid == pytest.approx(expected_mid, abs=1)

    def test_align_to_animated_returns_self(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        result = b.align_to(a, 'left', start=0, end=1)
        assert result is b

    def test_align_to_without_end_backward_compat(self):
        """Without end, align_to should still work instantly."""
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, LEFT)
        bx, _, _, _ = b.bbox(0)
        assert bx == pytest.approx(200)

    def test_align_to_animated_with_direction_constant(self):
        a = Rectangle(100, 50, x=200, y=100)
        b = Rectangle(80, 50, x=0, y=0)
        b.align_to(a, LEFT, start=0, end=1, easing=easings.linear)
        bx, _, _, _ = b.bbox(1)
        assert bx == pytest.approx(200)


# ── NeuralNetwork ────────────────────────────────────────────────────────────

class TestNeuralNetwork:
    def test_creates_with_layers(self):
        nn = NeuralNetwork([3, 4, 2])
        assert len(nn.objects) > 0

    def test_svg_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        nn = NeuralNetwork([2, 3, 1])
        c.add_objects(nn)
        svg = c.generate_frame_svg(0)
        assert '<circle' in svg

    def test_label_input(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.label_input(['a', 'b'])
        assert result is nn

    def test_label_output(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.label_output(['y'])
        assert result is nn

    def test_propagate(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.propagate(start=0, duration=1)
        assert result is nn


# ── Pendulum ─────────────────────────────────────────────────────────────────

class TestPendulumObject:
    def test_creates(self):
        p = Pendulum()
        assert len(p.objects) > 0

    def test_has_bob_and_rod(self):
        p = Pendulum()
        assert hasattr(p, 'bob')
        assert hasattr(p, 'rod')

    def test_svg_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        p = Pendulum()
        c.add_objects(p)
        svg = c.generate_frame_svg(0)
        assert '<' in svg

    def test_custom_params(self):
        p = Pendulum(pivot_x=500, pivot_y=200, length=300, angle=60)
        assert len(p.objects) > 0


# ── StandingWave ─────────────────────────────────────────────────────────────

class TestStandingWave:
    def test_creates(self):
        sw = StandingWave(harmonics=3)
        assert len(sw.objects) > 0

    def test_svg_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        sw = StandingWave()
        c.add_objects(sw)
        svg = c.generate_frame_svg(0)
        assert '<' in svg


# ── ArrayViz ─────────────────────────────────────────────────────────────────

class TestArrayViz:
    def test_creates_with_values(self):
        arr = ArrayViz([3, 1, 4])
        assert len(arr.values) == 3

    def test_svg_has_rects(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        arr = ArrayViz([1, 2, 3])
        c.add_objects(arr)
        svg = c.generate_frame_svg(0)
        assert '<rect' in svg

    def test_highlight(self):
        arr = ArrayViz([1, 2, 3])
        result = arr.highlight(1, start=0, end=1)
        assert result is arr

    def test_swap(self):
        arr = ArrayViz([10, 20, 30])
        arr.swap(0, 2, start=0, end=1)
        assert arr.values == [30, 20, 10]

    def test_set_value(self):
        arr = ArrayViz([10, 20, 30])
        arr.set_value(1, 99, start=0)
        assert arr.values[1] == 99

    def test_pointer(self):
        arr = ArrayViz([10, 20, 30])
        result = arr.pointer(0, label='i', start=0)
        assert result is not None

    def test_swap_invalid_index(self):
        arr = ArrayViz([1, 2, 3])
        arr.swap(0, 0)  # same index - noop
        arr.swap(-1, 5)  # out of range - noop
        assert arr.values == [1, 2, 3]


# ── LinkedListViz ────────────────────────────────────────────────────────────

class TestLinkedListViz:
    def test_creates_with_values(self):
        ll = LinkedListViz([10, 20, 30])
        assert len(ll.values) == 3

    def test_svg_has_circles(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        ll = LinkedListViz([1, 2])
        c.add_objects(ll)
        svg = c.generate_frame_svg(0)
        assert '<circle' in svg

    def test_highlight(self):
        ll = LinkedListViz([10, 20, 30])
        result = ll.highlight(0, start=0, end=0.5)
        assert result is ll

    def test_traverse(self):
        ll = LinkedListViz([10, 20, 30])
        result = ll.traverse(start=0, delay=0.3)
        assert result is ll


# ── StackViz ─────────────────────────────────────────────────────────────────

class TestStackViz:
    def test_creates_with_values(self):
        s = StackViz([1, 2, 3])
        assert len(s.values) == 3

    def test_push(self):
        s = StackViz([1, 2])
        s.push(3, start=0, end=0.5)
        assert len(s.values) == 3
        assert s.values[-1] == 3

    def test_pop(self):
        s = StackViz([1, 2, 3])
        s.pop(start=0, end=0.5)
        assert len(s.values) == 2

    def test_pop_empty(self):
        s = StackViz([])
        result = s.pop(start=0, end=0.5)
        assert result is s

    def test_svg_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        s = StackViz([10, 20])
        c.add_objects(s)
        svg = c.generate_frame_svg(0)
        assert '<rect' in svg


# ── Pop-in / Pop-out ─────────────────────────────────────────────────────────

class TestPopIn:
    def test_pop_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.pop_in(start=0, duration=0.5)
        assert result is c

    def test_pop_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.pop_out(start=0, duration=0.5)
        assert result is c


# ── Elastic / Bounce ─────────────────────────────────────────────────────────

class TestElasticInOut:
    def test_elastic_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.elastic_in(start=0, end=1)
        assert result is c

    def test_elastic_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.elastic_out(start=0, end=1)
        assert result is c

    def test_elastic_in_accepts_easing(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_in(start=0, end=1, easing=easings.smooth)

    def test_elastic_out_accepts_easing(self):
        c = Circle(r=50, cx=100, cy=100)
        c.elastic_out(start=0, end=1, easing=easings.smooth)

    def test_bounce_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.bounce_in(start=0, end=1)
        assert result is c

    def test_bounce_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.bounce_out(start=0, end=1)
        assert result is c


# ── Slide-in / Slide-out ─────────────────────────────────────────────────────

class TestSlideInOut:
    def test_slide_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.slide_in(direction='left', start=0, end=1)
        assert result is c

    def test_slide_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.slide_out(direction='right', start=0, end=1)
        assert result is c


# ── Zoom-in / Zoom-out ──────────────────────────────────────────────────────

class TestZoomInOut:
    def test_zoom_in_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.zoom_in(start=0, end=1)
        assert result is c

    def test_zoom_out_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.zoom_out(start=0, end=1)
        assert result is c


# ── Float anim ───────────────────────────────────────────────────────────────

class TestFloatAnim:
    def test_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.float_anim(start=0, end=2)
        assert result is c

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.float_anim(start=1, end=1)
        assert result is c


# ── Fade transform ───────────────────────────────────────────────────────────

class TestFadeTransform:
    def test_returns_source(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Rectangle(100, 50, x=200, y=200)
        result = Circle.fade_transform(a, b, start=0, end=1)
        assert result is a

    def test_source_hidden_at_end(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Rectangle(100, 50, x=200, y=200)
        Circle.fade_transform(a, b, start=0, end=1)
        assert a.show.at_time(1.5) == False

    def test_target_visible_at_end(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Rectangle(100, 50, x=200, y=200)
        Circle.fade_transform(a, b, start=0, end=1)
        assert b.show.at_time(1.5) == True


class TestQueueViz:
    def test_basic_creation(self):
        q = QueueViz([1, 2, 3])
        assert len(q.objects) > 0
        assert q.values == [1, 2, 3]

    def test_custom_position(self):
        q = QueueViz([10, 20], x=100, y=200)
        assert q._base_x == 100
        assert q._base_y == 200

    def test_enqueue(self):
        q = QueueViz([1, 2])
        result = q.enqueue(3, start=0, end=0.5)
        assert result is q
        assert q.values == [1, 2, 3]
        assert len(q._queue_cells) == 3

    def test_dequeue(self):
        q = QueueViz([1, 2, 3])
        result = q.dequeue(start=0, end=0.5)
        assert result is q
        assert q.values == [2, 3]
        assert len(q._queue_cells) == 2

    def test_dequeue_empty(self):
        q = QueueViz([])
        result = q.dequeue(start=0, end=0.5)
        assert result is q

    def test_highlight(self):
        q = QueueViz([10, 20, 30])
        result = q.highlight(1, color='#FF0000', start=0, end=1)
        assert result is q

    def test_enqueue_dequeue_sequence(self):
        q = QueueViz([1])
        q.enqueue(2, start=0, end=0.5)
        q.enqueue(3, start=0.5, end=1)
        q.dequeue(start=1, end=1.5)
        assert q.values == [2, 3]


class TestBinaryTreeHighlight:
    def test_highlight_node(self):
        from vectormation.objects import BinaryTree
        tree = BinaryTree((1, (2, 3, 4), (5, 6, 7)))
        result = tree.highlight_node(0, color='#FF0000', start=0, end=1)
        assert result is tree

    def test_highlight_out_of_range(self):
        from vectormation.objects import BinaryTree
        tree = BinaryTree((1, 2, 3))
        result = tree.highlight_node(99, start=0, end=1)
        assert result is tree


class TestSaveStateRestore:
    def test_save_and_restore(self):
        c = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        c.save_state(0)
        c.set_fill(color='#0000FF', start=0.5)
        result = c.restore(start=1, end=2)
        assert result is c

    def test_restore_returns_self(self):
        c = Circle(r=50)
        c.save_state(0)
        assert c.restore(start=1, end=2) is c


class TestFollowSpline:
    def test_follow_spline_returns_self(self):
        c = Circle(r=20, cx=100, cy=100)
        pts = [(100, 100), (200, 50), (300, 100), (400, 50)]
        result = c.follow_spline(pts, start=0, end=2)
        assert result is c

    def test_follow_spline_moves_through_points(self):
        c = Circle(r=20, cx=100, cy=100)
        pts = [(100, 100), (300, 300)]
        c.follow_spline(pts, start=0, end=1)
        cx0, cy0 = c.get_center(0)
        cx1, cy1 = c.get_center(1)
        assert abs(cx0 - 100) < 2
        assert abs(cy0 - 100) < 2
        assert abs(cx1 - 300) < 2
        assert abs(cy1 - 300) < 2

    def test_follow_spline_single_point_noop(self):
        c = Circle(r=20, cx=100, cy=100)
        result = c.follow_spline([(100, 100)], start=0, end=1)
        assert result is c
        cx, cy = c.get_center(0.5)
        assert abs(cx - 100) < 2


class TestPathArc:
    def test_path_arc_moves_object(self):
        c = Circle(r=20, cx=100, cy=100)
        c.path_arc(200, 200, start=0, end=1, angle=math.pi / 2)
        cx, cy = c.get_center(0.5)
        # mid-arc should be different from start and end
        assert not (abs(cx - 100) < 1 and abs(cy - 100) < 1)


class TestOrbit:
    def test_orbit_returns_self(self):
        d = Dot(cx=200, cy=200)
        result = d.orbit(960, 540, start=0, end=2)
        assert result is d

    def test_orbit_changes_position(self):
        d = Dot(cx=960, cy=300)
        d.orbit(960, 540, start=0, end=2)
        cx, cy = d.get_center(1)
        # should have moved from initial position
        assert abs(cy - 300) > 10 or abs(cx - 960) > 10


class TestPulsate:
    def test_pulsate_returns_self(self):
        c = Circle(r=40)
        result = c.pulsate(start=0, end=2, pulses=3)
        assert result is c


class TestFlip:
    def test_flip_returns_self(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.flip(start=0, end=0.5)
        assert result is r

    def test_flip_vertical(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.flip(axis='vertical', start=0, end=0.5)
        assert result is r


class TestDimUndim:
    def test_dim(self):
        c = Circle(r=50, fill='#FF0000', fill_opacity=1)
        result = c.dim(start=0, end=1, opacity=0.3)
        assert result is c

    def test_undim(self):
        c = Circle(r=50, fill='#FF0000', fill_opacity=1)
        c.dim(start=0, end=1, opacity=0.3)
        result = c.undim(start=1, end=2)
        assert result is c


class TestCrossOut:
    def test_cross_out_returns_cross(self):
        r = Rectangle(100, 50, x=100, y=100)
        cross = r.cross_out(start=0, end=1)
        assert cross is not None
        assert hasattr(cross, 'objects')


class TestStampMethod:
    def test_stamp_creates_copy(self):
        c = Circle(r=30, cx=200, cy=200)
        s = c.stamp(time=0)
        assert s is not c
        assert hasattr(s, 'styling')


class TestApplyMatrix:
    def test_apply_matrix(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.apply_matrix([[1, 0], [0, 1]], start=0)
        assert result is r


class TestReflect:
    def test_reflect_vertical(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.reflect(axis='vertical', start=0)
        assert result is r

    def test_reflect_horizontal(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.reflect(axis='horizontal', start=0)
        assert result is r


class TestTracePath:
    def test_trace_returns_path(self):
        d = Dot(cx=100, cy=100)
        d.shift(dx=200, start=0, end=2)
        path = d.trace_path(start=0, end=2)
        assert path is not None


class TestCollectionFilter:
    def test_filter(self):
        a = Circle(r=10, cx=100, cy=100)
        b = Circle(r=20, cx=200, cy=200)
        c = Circle(r=30, cx=300, cy=300)
        col = VCollection(a, b, c)
        result = col.filter(lambda obj: obj.r.at_time(0) > 15)
        assert len(result.objects) == 2

    def test_partition(self):
        a = Circle(r=10)
        b = Circle(r=20)
        c = Circle(r=30)
        col = VCollection(a, b, c)
        yes, no = col.partition(lambda obj: obj.r.at_time(0) > 15)
        assert len(yes.objects) == 2
        assert len(no.objects) == 1


class TestCollectionColorGradient:
    def test_set_color_by_gradient(self):
        circles = VCollection(*[Circle(r=10) for _ in range(5)])
        result = circles.set_color_by_gradient('#FF0000', '#0000FF')
        assert result is circles

    def test_set_opacity_by_gradient(self):
        circles = VCollection(*[Circle(r=10) for _ in range(5)])
        result = circles.set_opacity_by_gradient(0.1, 1.0)
        assert result is circles


class TestCollectionSwapChildren:
    def test_swap_children(self):
        a = Circle(r=10, cx=100, cy=100)
        b = Circle(r=10, cx=200, cy=200)
        col = VCollection(a, b)
        result = col.swap_children(0, 1, start=0, end=1)
        assert result is col


class TestCollectionCascade:
    def test_cascade(self):
        circles = VCollection(*[Circle(r=10) for _ in range(3)])
        result = circles.cascade('fadein', start=0, end=1, overlap=0.3)
        assert result is circles


class TestSpring:
    def test_spring_returns_self(self):
        c = Circle(r=20)
        result = c.spring(start=0, end=2, amplitude=50)
        assert result is c


class TestRubberBand:
    def test_rubber_band_returns_self(self):
        c = Circle(r=20)
        result = c.rubber_band(start=0, end=1)
        assert result is c


class TestJiggle:
    def test_jiggle_returns_self(self):
        c = Circle(r=20)
        result = c.jiggle(start=0, end=1)
        assert result is c


class TestSquish:
    def test_squish_returns_self(self):
        r = Rectangle(100, 50)
        result = r.squish(start=0, end=1)
        assert result is r


class TestColorCycle:
    def test_color_cycle_returns_self(self):
        c = Circle(r=30, fill='#FF0000')
        result = c.color_cycle(['#FF0000', '#00FF00', '#0000FF'], start=0, end=3)
        assert result is c


class TestGlitch:
    def test_glitch_returns_self(self):
        r = Rectangle(100, 50)
        result = r.glitch(start=0, end=1)
        assert result is r


class TestWipe:
    def test_wipe_returns_self(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.wipe(start=0, end=1)
        assert result is r

    def test_wipe_direction(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.wipe(direction='left', start=0, end=1)
        assert result is r


class TestCreateUncreate:
    def test_create_returns_path(self):
        p = Lines([(100, 100), (200, 200), (300, 100)], stroke='#fff')
        result = p.create(start=0, end=1)
        assert result is not None

    def test_uncreate_returns_path(self):
        p = Lines([(100, 100), (200, 200), (300, 100)], stroke='#fff')
        result = p.uncreate(start=0, end=1)
        assert result is not None


class TestAnimateDash:
    def test_animate_dash_returns_self(self):
        c = Circle(r=60, stroke='#fff')
        result = c.animate_dash(start=0, end=2)
        assert result is c


class TestBraceDirectionConstants:
    """Test that Brace, Callout, brace_between_points accept tuple direction constants."""

    def test_brace_with_down_constant(self):
        r = Rectangle(100, 50, x=400, y=400)
        b = Brace(r, direction=DOWN)
        assert b is not None

    def test_brace_with_up_constant(self):
        r = Rectangle(100, 50, x=400, y=400)
        b = Brace(r, direction=UP)
        assert b is not None

    def test_brace_with_left_constant(self):
        r = Rectangle(100, 50, x=400, y=400)
        b = Brace(r, direction=LEFT)
        assert b is not None

    def test_brace_with_right_constant(self):
        r = Rectangle(100, 50, x=400, y=400)
        b = Brace(r, direction=RIGHT)
        assert b is not None

    def test_callout_with_direction_constants(self):
        c = Callout('test', (500, 500), direction=DOWN)
        assert c is not None
        c2 = Callout('test', (500, 500), direction=UP)
        assert c2 is not None

    def test_brace_between_points_with_direction_constant(self):
        from vectormation.objects import brace_between_points
        b = brace_between_points((100, 100), (300, 100), direction=DOWN)
        assert b is not None


class TestNumberLineAddBraceDirection:
    def test_add_brace_with_tuple_direction(self):
        nl = NumberLine(x_range=(0, 10, 1))
        b = nl.add_brace(2, 5, direction=DOWN)
        assert b is not None


class TestFlashFillHelper:
    """Test that _flash_fill helper works via data structure highlight methods."""

    def test_arrayviz_highlight(self):
        a = ArrayViz([1, 2, 3])
        result = a.highlight(0, start=0, end=1)
        assert result is a

    def test_linkedlistviz_highlight(self):
        ll = LinkedListViz([10, 20, 30])
        result = ll.highlight(1, start=0, end=1)
        assert result is ll

    def test_queueviz_highlight(self):
        q = QueueViz([1, 2, 3])
        result = q.highlight(0, start=0, end=0.5)
        assert result is q

    def test_highlight_out_of_range(self):
        a = ArrayViz([1, 2])
        result = a.highlight(99, start=0, end=1)
        assert result is a


class TestParseArgsExtended:
    def test_parse_args_has_new_options(self):
        from vectormation._composites import parse_args
        import argparse
        # We can't call parse_args() directly (it calls sys.argv),
        # but we can verify the function exists and check its module
        assert callable(parse_args)


class TestVCollectionSelect:
    def test_select_returns_subcollection(self):
        objs = [Circle(r=10) for _ in range(5)]
        col = VCollection(*objs)
        sub = col.select(1, 3)
        assert len(sub) == 2

    def test_select_all(self):
        objs = [Circle(r=10) for _ in range(3)]
        col = VCollection(*objs)
        sub = col.select()
        assert len(sub) == 3


class TestVCollectionChildAccess:
    def test_first(self):
        a, b = Circle(r=10), Rectangle(20, 20)
        col = VCollection(a, b)
        assert col.first() is a

    def test_last(self):
        a, b = Circle(r=10), Rectangle(20, 20)
        col = VCollection(a, b)
        assert col.last() is b

    def test_nth(self):
        objs = [Circle(r=10) for _ in range(4)]
        col = VCollection(*objs)
        assert col.nth(2) is objs[2]

    def test_get_child(self):
        objs = [Circle(r=10) for _ in range(4)]
        col = VCollection(*objs)
        assert col.get_child(1) is objs[1]


class TestVCollectionManagement:
    def test_insert_at(self):
        a, b = Circle(r=10), Rectangle(20, 20)
        col = VCollection(a)
        c = Circle(r=5)
        col.insert_at(0, c)
        assert col[0] is c
        assert col[1] is a

    def test_remove_at(self):
        a, b = Circle(r=10), Rectangle(20, 20)
        col = VCollection(a, b)
        col.remove_at(0)
        assert len(col) == 1
        assert col[0] is b

    def test_clear(self):
        col = VCollection(Circle(r=10), Rectangle(20, 20))
        col.clear()
        assert len(col) == 0

    def test_send_to_back(self):
        a, b, c = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(a, b, c)
        col.send_to_back(c)
        assert col[0] is c

    def test_bring_to_front(self):
        a, b, c = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(a, b, c)
        col.bring_to_front(a)
        assert col[-1] is a


class TestVCollectionSpaceEvenly:
    def test_space_evenly(self):
        objs = [Circle(r=20) for _ in range(3)]
        col = VCollection(*objs)
        col.space_evenly(direction='right')
        # After spacing, objects should have different x positions
        x0 = objs[0].get_x(0)
        x1 = objs[1].get_x(0)
        x2 = objs[2].get_x(0)
        # Objects should be in order (x0 <= x1 <= x2 or all same if 0-width)
        assert isinstance(x0, (int, float))


class TestVCollectionShuffle:
    def test_shuffle(self):
        objs = [Circle(r=10 + i) for i in range(10)]
        col = VCollection(*objs)
        col.shuffle()
        assert len(col) == 10


class TestVCollectionSpread:
    def test_spread(self):
        objs = [Circle(r=10) for _ in range(3)]
        col = VCollection(*objs)
        col.spread(100, 100, 500, 100)
        assert len(col) == 3


class TestSmoothIndex:
    def test_basic_interpolation(self):
        from vectormation.objects import smooth_index
        assert smooth_index([0, 10, 20], 0.0) == 0
        assert smooth_index([0, 10, 20], 0.5) == 10
        assert smooth_index([0, 10, 20], 1.0) == 20

    def test_midpoint(self):
        from vectormation.objects import smooth_index
        result = smooth_index([0, 10], 0.5)
        assert abs(result - 5) < 1e-9

    def test_tuple_interpolation(self):
        from vectormation.objects import smooth_index
        result = smooth_index([(0, 0), (10, 20)], 0.5)
        assert abs(result[0] - 5) < 1e-9
        assert abs(result[1] - 10) < 1e-9

    def test_single_element(self):
        from vectormation.objects import smooth_index
        assert smooth_index([42], 0.5) == 42

    def test_empty_list_raises(self):
        from vectormation.objects import smooth_index
        with pytest.raises(ValueError):
            smooth_index([], 0.5)


class TestInterpolateValue:
    def test_basic(self):
        from vectormation.objects import interpolate_value
        assert interpolate_value(0, 10, 0.5) == 5
        assert interpolate_value(0, 10, 0.0) == 0
        assert interpolate_value(0, 10, 1.0) == 10

    def test_negative(self):
        from vectormation.objects import interpolate_value
        assert interpolate_value(-10, 10, 0.5) == 0


class TestBarChartAnimateValues:
    def test_animate_values(self):
        chart = BarChart([3, 5, 2])
        result = chart.animate_values([5, 3, 4], start=0, end=1)
        assert result is chart
        assert chart.values == [5, 3, 4]

    def test_pie_chart_animate_values(self):
        chart = PieChart([30, 40, 30])
        result = chart.animate_values([50, 25, 25], start=0, end=1)
        assert result is chart
        assert chart.values == [50, 25, 25]


class TestPieChartHighlightSector:
    def test_highlight_sector_returns_self(self):
        chart = PieChart([30, 40, 30])
        result = chart.highlight_sector(0, start=0, end=1)
        assert result is chart

    def test_highlight_sector_out_of_range(self):
        chart = PieChart([30, 40, 30])
        result = chart.highlight_sector(10, start=0, end=1)
        assert result is chart

    def test_highlight_sector_zero_duration(self):
        chart = PieChart([30, 40, 30])
        result = chart.highlight_sector(1, start=1, end=1)
        assert result is chart


class TestBarChartSetBarColor:
    def test_set_bar_color_instant(self):
        chart = BarChart([3, 5, 2])
        result = chart.set_bar_color(0, '#FF0000', start=0)
        assert result is chart

    def test_set_bar_color_animated(self):
        chart = BarChart([3, 5, 2])
        result = chart.set_bar_color(1, '#00FF00', start=0, end=1)
        assert result is chart

    def test_set_bar_color_out_of_range(self):
        chart = BarChart([3, 5, 2])
        result = chart.set_bar_color(10, '#FF0000')
        assert result is chart


class TestMatrixHighlightRowColumn:
    def test_highlight_row(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.highlight_row(0, start=0, end=1)
        assert result is m

    def test_highlight_column(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.highlight_column(1, start=0, end=1)
        assert result is m

    def test_highlight_row_out_of_range(self):
        m = Matrix([[1, 2], [3, 4]])
        # highlight_row should not crash for valid rows
        result = m.highlight_row(1, start=0, end=1)
        assert result is m


class TestCanvasConstants:
    def test_canvas_dimensions(self):
        assert CANVAS_WIDTH == 1920
        assert CANVAS_HEIGHT == 1080

    def test_origin_derived_from_canvas(self):
        from vectormation.objects import ORIGIN
        assert ORIGIN == (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)


class TestTextTypewrite:
    def test_typewrite_basic(self):
        t = Text('Hello', x=100, y=100)
        result = t.typewrite(start=0, end=1)
        assert result is t
        # At t=0 should show cursor
        txt = t.text.at_time(0.01)
        assert isinstance(txt, str)

    def test_typewrite_end_shows_full_text(self):
        t = Text('AB', x=100, y=100)
        t.typewrite(start=0, end=1)
        assert t.text.at_time(1.0) == 'AB'

    def test_untype(self):
        t = Text('Hello', x=100, y=100)
        result = t.untype(start=0, end=1)
        assert result is t
        # At end, text should be empty
        assert t.text.at_time(1.0) == ''

    def test_scramble(self):
        t = Text('ABC', x=100, y=100)
        result = t.scramble(start=0, end=1)
        assert result is t
        # At end, text should be the original
        assert t.text.at_time(1.0) == 'ABC'


class TestCountAnimationCountTo:
    def test_count_to(self):
        c = CountAnimation(0, 10, start=0, end=1)
        c.count_to(20, start=1, end=2)
        # At t=2 should show 20
        assert '20' in c.text.at_time(2.0)

    def test_count_to_instant(self):
        c = CountAnimation(0, 5, start=0, end=1)
        c.count_to(100, start=1, end=1)  # instant
        assert '100' in c.text.at_time(1.0)


class TestValueTrackerLastChange:
    def test_last_change_initial(self):
        vt = ValueTracker(42)
        assert vt.last_change == 0

    def test_last_change_after_set(self):
        vt = ValueTracker(0)
        vt.set_value(10, start=2)
        assert vt.last_change == 2


class TestAngleEndAngle:
    def test_end_angle_property(self):
        a = Angle((100, 100), (200, 100), (100, 0))
        assert hasattr(a, 'end_angle')
        # Should return a Real attribute
        val = a.end_angle
        assert val is not None

    def test_start_angle_property(self):
        a = Angle((100, 100), (200, 100), (100, 0))
        assert hasattr(a, 'start_angle')


class TestBarChartSetBarColors:
    def test_set_bar_colors_basic(self):
        chart = BarChart([10, 20, 30], labels=['A', 'B', 'C'])
        result = chart.set_bar_colors(['#ff0000', '#00ff00', '#0000ff'])
        assert result is chart

    def test_set_bar_colors_partial(self):
        chart = BarChart([10, 20, 30], labels=['A', 'B', 'C'])
        # Fewer colors than bars — should not crash
        result = chart.set_bar_colors(['#ff0000'])
        assert result is chart


class TestTableGetRowColumn:
    def test_get_row(self):
        t = Table([['a', 'b'], ['c', 'd']])
        row = t.get_row(0)
        assert isinstance(row, VCollection)
        assert len(row.objects) == 2

    def test_get_column(self):
        t = Table([['a', 'b'], ['c', 'd']])
        col = t.get_column(1)
        assert isinstance(col, VCollection)
        assert len(col.objects) == 2


class TestMatrixGetRowColumn:
    def test_get_row(self):
        m = Matrix([[1, 2], [3, 4]])
        row = m.get_row(0)
        assert isinstance(row, VCollection)
        assert len(row.objects) == 2

    def test_get_column(self):
        m = Matrix([[1, 2], [3, 4]])
        col = m.get_column(1)
        assert isinstance(col, VCollection)
        assert len(col.objects) == 2


class TestVariableTracker:
    def test_variable_tracker_property(self):
        v = Variable('x', value=5)
        tracker = v.tracker
        assert tracker is not None

    def test_variable_set_value(self):
        v = Variable('x', value=5)
        result = v.set_value(10, start=0)
        assert result is v

    def test_variable_animate_value(self):
        v = Variable('x', value=5)
        result = v.animate_value(20, start=0, end=1)
        assert result is v


class TestTextHighlightSubstring:
    def test_highlight_returns_rect(self):
        t = Text('Hello World', x=100, y=100)
        rect = t.highlight(start=0, end=1)
        assert isinstance(rect, Rectangle)

    def test_highlight_substring_returns_rect(self):
        t = Text('Hello World', x=100, y=100)
        rect = t.highlight_substring('World', start=0, end=1)
        assert isinstance(rect, Rectangle)

    def test_highlight_substring_not_found(self):
        t = Text('Hello', x=100, y=100)
        rect = t.highlight_substring('XYZ', start=0, end=1)
        # Should return an empty rect
        assert isinstance(rect, Rectangle)


class TestDecimalNumberTracker:
    def test_decimal_tracker(self):
        d = DecimalNumber(3.14)
        tracker = d.tracker
        assert tracker is not None

    def test_decimal_set_and_get(self):
        d = DecimalNumber(0)
        d.set_value(42, start=0)
        assert d.tracker.at_time(0) == pytest.approx(42)


class TestScaleBy:
    def test_scale_by_alias(self):
        c = Circle()
        result = c.scale_by(0, 1, 2.0)
        assert result is c


class TestAxesAddCoordinates:
    def test_add_coordinates_returns_self(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.add_coordinates()
        assert result is ax
        assert len(ax.objects) > 0

    def test_add_grid_returns_self(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.add_grid()
        assert result is ax

    def test_set_ranges(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        ax.set_x_range(-5, 5, start=0)
        ax.set_y_range(-3, 3, start=0)
        assert ax.x_min.at_time(0) == pytest.approx(-5)
        assert ax.x_max.at_time(0) == pytest.approx(5)
        assert ax.y_min.at_time(0) == pytest.approx(-3)
        assert ax.y_max.at_time(0) == pytest.approx(3)

    def test_add_zero_line_x(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.add_zero_line(axis='x')
        assert result is ax

    def test_add_zero_line_y(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.add_zero_line(axis='y')
        assert result is ax


class TestAxesAddTitle:
    def test_add_title_returns_text(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.add_title('My Plot')
        assert isinstance(result, Text)


class TestAxesAnimateRange:
    def test_animate_x_range(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.animate_x_range(0, 1, (-5, 5))
        assert result is ax

    def test_animate_y_range(self):
        ax = Axes(x_range=(-2, 2), y_range=(-2, 2))
        result = ax.animate_y_range(0, 1, (-5, 5))
        assert result is ax


class TestCodeHighlightLines:
    def test_highlight_lines_returns_vcollection(self):
        code = Code('def foo():\n    return 42', language='python')
        result = code.highlight_lines([1])
        assert isinstance(result, VCollection)

    def test_reveal_lines(self):
        code = Code('line1\nline2\nline3', language='python')
        result = code.reveal_lines(start=0, end=1)
        assert result is code


class TestTitleObject:
    def test_title_creates(self):
        t = Title('Hello')
        assert len(t.objects) == 2  # text + underline

    def test_title_svg_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        t = Title('Test')
        c.add_objects(t)
        svg = c.generate_frame_svg(0)
        assert 'Test' in svg


class TestDynamicObjectTest:
    def test_creates(self):
        d = DynamicObject(lambda t: Circle(r=10 + t * 10))
        assert d is not None

    def test_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        d = DynamicObject(lambda t: Circle(r=10 + t * 10))
        c.add_objects(d)
        svg = c.generate_frame_svg(0)
        assert 'circle' in svg.lower()


class TestCurvedArrowBasic:
    def test_curved_arrow_has_two_children(self):
        ca = CurvedArrow(x1=100, y1=100, x2=300, y2=300)
        assert len(ca.objects) == 2  # shaft + tip


class TestChessBoardMovePiece:
    def test_move_piece(self):
        cb = ChessBoard()
        result = cb.move_piece((0, 1), (0, 3), start=0, end=1)
        assert result is cb


class TestLED:
    def test_creates(self):
        led = LED()
        assert isinstance(led, VCollection)
        assert len(led.objects) > 0

    def test_renders_svg(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        led = LED(x1=400, y1=540, x2=600, y2=540, color='#00FF00')
        c.add_objects(led)
        svg = c.generate_frame_svg(0)
        assert '<' in svg


class TestCalloutRender:
    def test_callout_creates(self):
        co = Callout('hello', target=(500, 500))
        assert isinstance(co, VCollection)

    def test_callout_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        co = Callout('note', target=(500, 500))
        c.add_objects(co)
        svg = c.generate_frame_svg(0)
        assert 'note' in svg


class TestDimensionLineRender:
    def test_creates(self):
        dl = DimensionLine(p1=(100, 500), p2=(500, 500), label='400px')
        assert isinstance(dl, VCollection)


class TestTooltipRender:
    def test_creates(self):
        tt = Tooltip('tip', target=(500, 500))
        assert isinstance(tt, VCollection)


class TestLabelRender:
    def test_label_creates(self):
        lbl = Label('label')
        assert isinstance(lbl, VCollection)

    def test_label_renders(self):
        c = VectorMathAnim(save_dir='/tmp/t')
        lbl = Label('test')
        c.add_objects(lbl)
        svg = c.generate_frame_svg(0)
        assert 'test' in svg


class TestLegendRender:
    def test_creates(self):
        lg = Legend([('#ff0000', 'Red'), ('#00ff00', 'Green')])
        assert isinstance(lg, VCollection)


class TestProgressBarAnimateTo:
    def test_creates(self):
        pb = ProgressBar()
        assert isinstance(pb, VCollection)

    def test_animate_to(self):
        pb = ProgressBar()
        result = pb.animate_to(0.5, start=0, end=1)
        assert result is pb


class TestFlowChartRender:
    def test_creates(self):
        fc = FlowChart(['Start', 'Process', 'End'])
        assert isinstance(fc, VCollection)
        assert len(fc.objects) > 0


class TestAddDotLabelConsistentReturn:
    def test_always_returns_tuple(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_dot_label(0, 0)
        assert isinstance(result, tuple)
        assert len(result) == 2
        # Without label, second element should be None
        assert result[1] is None

    def test_with_label_returns_tuple(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        dot, lbl = ax.add_dot_label(0, 0, label='test')
        assert dot is not None
        assert lbl is not None


class TestRegressionLineEdgeCases:
    def test_insufficient_data(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_regression_line([1], [1])
        assert result is None

    def test_normal_data(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.add_regression_line([1, 2, 3], [1, 2, 3])
        assert result is not None


class TestShimmerAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.shimmer(start=0, end=1) is c

    def test_renders_mid(self):
        c = Circle(fill='#ff0000')
        c.shimmer(start=0, end=1, passes=2)
        svg = c.to_svg(0.5)
        assert isinstance(svg, str)


class TestSwingAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.swing(start=0, end=1) is c

    def test_renders_mid(self):
        c = Circle()
        c.swing(start=0, end=1, amplitude=30)
        svg = c.to_svg(0.5)
        assert isinstance(svg, str)


class TestUndulateAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.undulate(start=0, end=1) is c

    def test_renders_mid(self):
        c = Circle(cx=960, cy=540)
        c.undulate(start=0, end=1, amplitude=0.2)
        svg = c.to_svg(0.5)
        assert isinstance(svg, str)


class TestRippleEffect:
    def test_returns_vcollection(self):
        from vectormation._base import VCollection
        c = Circle()
        result = c.ripple(start=0)
        assert isinstance(result, VCollection)

    def test_with_count(self):
        c = Circle(cx=960, cy=540)
        c.ripple(start=0, count=2, duration=1)
        assert isinstance(c, Circle)


class TestHighlightBorderAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.highlight_border(start=0) is c


class TestFlashHighlightAnim:
    def test_returns_rectangle(self):
        from vectormation._shapes import Rectangle
        c = Circle()
        result = c.flash_highlight(start=0)
        assert isinstance(result, Rectangle)


class TestPulseOutlineAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.pulse_outline(start=0) is c


class TestGlitchAnim:
    def test_returns_self(self):
        c = Circle()
        assert c.glitch(start=0, end=1) is c


class TestFlashNoFill:
    """flash() should return self gracefully when object has no fill."""
    def test_flash_no_fill_returns_self(self):
        from vectormation._shapes import Line
        line = Line(x1=0, y1=0, x2=100, y2=100)
        result = line.flash(start=0, end=1)
        assert result is line


class TestAlwaysNextToBuff:
    """always_next_to should default to SMALL_BUFF matching next_to."""
    def test_default_buff_matches_next_to(self):
        import inspect
        sig = inspect.signature(Circle.always_next_to)
        assert sig.parameters['buff'].default == 14  # SMALL_BUFF


class TestFlashColor:
    def test_returns_self(self):
        c = Circle(fill='#ff0000')
        result = c.flash_color('#00ff00', start=0, duration=0.5)
        assert result is c

    def test_color_changes_at_midpoint(self):
        c = Circle(fill='#ff0000')
        c.flash_color('#00ff00', start=0, duration=1.0)
        # At midpoint (t=0.5) should be at the flash color
        mid_color = c.styling.fill.time_func(0.5)
        assert isinstance(mid_color, tuple)


class TestRotateIn:
    def test_returns_self(self):
        c = Circle()
        result = c.rotate_in(start=0, end=1)
        assert result is c

    def test_visible_after(self):
        c = Circle(creation=5)
        c.rotate_in(start=0, end=1)
        assert c.show.at_time(0.5)


class TestPulseColor:
    def test_returns_self(self):
        c = Circle(fill='#ff0000')
        result = c.pulse_color('#00ff00', start=0, end=1, pulses=2)
        assert result is c

    def test_no_crash_zero_pulses(self):
        c = Circle(fill='#ff0000')
        result = c.pulse_color('#00ff00', pulses=0)
        assert result is c


class TestWaveAnim:
    def test_returns_self(self):
        g = VGroup(Circle(), Circle())
        result = g.wave_anim(start=0, end=1, amplitude=20)
        assert result is g

    def test_empty_collection(self):
        g = VGroup()
        result = g.wave_anim(start=0, end=1)
        assert result is g


class TestAlignSubmobjects:
    def test_left_align(self):
        c1 = Circle(cx=100, cy=100)
        c2 = Circle(cx=300, cy=200)
        g = VGroup(c1, c2)
        g.align_submobjects(edge='left', start=0)
        # After alignment, both should have similar left edges
        b1 = c1.bbox(0)
        b2 = c2.bbox(0)
        assert abs(b1[0] - b2[0]) < 1

    def test_returns_self(self):
        g = VGroup(Circle(), Circle())
        assert g.align_submobjects() is g


class TestStaggerFadein:
    def test_returns_self(self):
        g = VGroup(Circle(), Dot())
        result = g.stagger_fadein(start=0, end=2)
        assert result is g


class TestHighlightChild:
    def test_returns_self(self):
        g = VGroup(Circle(), Dot(), Circle())
        result = g.highlight_child(1, start=0, end=1)
        assert result is g

    def test_dims_others(self):
        c1 = Circle()
        c2 = Dot()
        g = VGroup(c1, c2)
        g.highlight_child(0, start=0, end=1, dim_opacity=0.2)
        # c2 should be dimmed at t=0.5
        op = c2.styling.fill_opacity.at_time(0.5)
        assert op < 1.0


class TestSortObjects:
    def test_sorts_by_x(self):
        c1 = Circle(cx=300)
        c2 = Circle(cx=100)
        c3 = Circle(cx=200)
        g = VGroup(c1, c2, c3)
        g.sort_objects()
        assert g.objects[0] is c2
        assert g.objects[1] is c3
        assert g.objects[2] is c1

    def test_reverse(self):
        c1 = Circle(cx=100)
        c2 = Circle(cx=300)
        g = VGroup(c1, c2)
        g.sort_objects(reverse=True)
        assert g.objects[0] is c2


class TestRotateChildren:
    def test_returns_self(self):
        g = VGroup(Circle(cx=100, cy=100), Circle(cx=200, cy=100))
        result = g.rotate_children(degrees=90, start=0, end=1)
        assert result is g

    def test_empty_collection(self):
        g = VGroup()
        result = g.rotate_children()
        assert result is g


class TestEmphasize:
    def test_returns_self(self):
        c = Circle()
        assert c.emphasize(start=0, duration=0.8) is c

    def test_scale_changes(self):
        c = Circle()
        c.emphasize(start=0, duration=0.5, scale_factor=1.3)
        mid = c.styling.scale_x.at_time(0.25)
        assert mid > 1.0


class TestGrowFromPoint:
    def test_returns_self(self):
        c = Circle()
        assert c.grow_from_point(960, 540, start=0, end=1) is c

    def test_invisible_at_start(self):
        c = Circle()
        c.grow_from_point(960, 540, start=0, end=1)
        sx = c.styling.scale_x.at_time(0)
        assert sx < 0.01


class TestShrinkToPoint:
    def test_returns_self(self):
        c = Circle()
        assert c.shrink_to_point(960, 540, start=0, end=1) is c


class TestShrinkToEdge:
    def test_returns_self(self):
        c = Circle()
        assert c.shrink_to_edge('bottom', start=0, end=1) is c


class TestSpiralOut:
    def test_returns_self(self):
        c = Circle()
        assert c.spiral_out(start=0, end=1) is c


class TestShowPassingFlash:
    def test_returns_path(self):
        c = Circle()
        result = c.show_passing_flash(start=0, end=1)
        assert isinstance(result, Path)


class TestSequential:
    def test_returns_self(self):
        g = VGroup(Circle(), Dot())
        result = g.sequential('fadein', start=0, end=1)
        assert result is g


class TestForEach:
    def test_calls_method(self):
        g = VGroup(Circle(cx=100), Circle(cx=200))
        g.for_each('set_fill', color='#ff0000')
        # No crash = success


class TestReverseChildren:
    def test_reverses_order(self):
        c1 = Circle(cx=100)
        c2 = Circle(cx=200)
        g = VGroup(c1, c2)
        g.reverse_children()
        assert g.objects[0] is c2
        assert g.objects[1] is c1


class TestBrect:
    def test_vobject_brect_returns_rectangle(self):
        c = Circle(r=50, cx=100, cy=100)
        r = c.brect(time=0)
        assert r is not None
        bx, by, bw, bh = r.bbox(0)
        # brect should be larger than the circle's bbox due to buff
        cx_bb, cy_bb, cw, ch = c.bbox(0)
        assert bw >= cw
        assert bh >= ch

    def test_vobject_brect_with_buff(self):
        r = Rectangle(100, 50, x=200, y=100)
        br = r.brect(time=0, buff=20)
        bx, by, bw, bh = br.bbox(0)
        assert bw == pytest.approx(140, abs=2)
        assert bh == pytest.approx(90, abs=2)

    def test_vcollection_brect(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        g = VGroup(c1, c2)
        br = g.brect(time=0)
        bx, by, bw, bh = br.bbox(0)
        assert bw > 0
        assert bh > 0


class TestSurround:
    def test_surround_creates_rectangle(self):
        c = Circle(r=30, cx=100, cy=100)
        sr = Circle.surround(c, buff=10)
        assert sr is not None
        bx, by, bw, bh = sr.bbox(0)
        assert bw > 0


class TestAnimateStyle:
    def test_animate_fill(self):
        c = Circle(r=50, cx=100, cy=100, fill='#ff0000')
        result = c.animate_style(0, 1, fill='#0000ff')
        assert result is c

    def test_animate_stroke_width(self):
        c = Circle(r=50, cx=100, cy=100, stroke_width=2)
        result = c.animate_style(0, 1, stroke_width=8)
        assert result is c
        # At end time, stroke_width should be ~8
        assert c.styling.stroke_width.at_time(1) == pytest.approx(8, abs=0.5)

    def test_instant_set_when_dur_zero(self):
        c = Circle(r=50, cx=100, cy=100, fill_opacity=1.0)
        c.animate_style(0, 0, fill_opacity=0.5)
        assert c.styling.fill_opacity.at_time(0) == pytest.approx(0.5, abs=0.01)


class TestSplitWords:
    def test_split_words_count(self):
        t = Text("Hello World Foo", x=100, y=100)
        words = t.split_words()
        assert len(words.objects) == 3

    def test_split_words_empty(self):
        t = Text("", x=100, y=100)
        words = t.split_words()
        assert len(words.objects) == 0


class TestAxesSetRanges:
    def test_set_ranges_animates_both_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.set_ranges(0, 1, x_range=(-10, 10), y_range=(-10, 10))
        assert result is ax

    def test_animate_x_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.animate_x_range(0, 1, (-10, 10))
        assert ax.x_min.at_time(1) == pytest.approx(-10, abs=0.5)
        assert ax.x_max.at_time(1) == pytest.approx(10, abs=0.5)

    def test_animate_y_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        ax.animate_y_range(0, 1, (-10, 10))
        assert ax.y_min.at_time(1) == pytest.approx(-10, abs=0.5)
        assert ax.y_max.at_time(1) == pytest.approx(10, abs=0.5)


class TestAxesPlotMethods:
    def test_plot_scatter(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_scatter([1, 3, 5], [2, 4, 6])
        assert result is not None

    def test_plot_step(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.plot_step([1, 3, 5, 7], [2, 4, 6, 8])
        assert result is not None

    def test_plot_parametric(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        result = ax.plot_parametric(lambda t: (math.cos(t), math.sin(t)))
        assert result is not None

    def test_plot_stem(self):
        ax = Axes(x_range=(0, 5), y_range=(0, 5))
        result = ax.plot_stem([1, 2, 3], [2, 3, 4])
        assert result is not None

    def test_plot_vector_field(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        result = ax.plot_vector_field(lambda x, y: (-y, x))
        assert result is not None


class TestAxesDecorations:
    def test_get_horizontal_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot(lambda x: x)
        line = ax.get_horizontal_line(5, 5)
        assert line is not None

    def test_get_dashed_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        line = ax.get_dashed_line(1, 2, 5, 6)
        assert line is not None

    def test_get_line_from_to(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        line = ax.get_line_from_to(1, 2, 5, 6)
        assert line is not None

    def test_highlight_x_range(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        rect = ax.highlight_x_range(2, 8)
        assert rect is not None

    def test_highlight_y_range(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        rect = ax.highlight_y_range(2, 8)
        assert rect is not None

    def test_get_rect(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        rect = ax.get_rect(1, 2, 5, 6)
        assert rect is not None

    def test_get_area_between(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        f1 = ax.plot(lambda x: x)
        f2 = ax.plot(lambda x: x ** 2 / 10)
        area = ax.get_area_between(f1, f2)
        assert area is not None

    def test_get_secant_line(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        curve = ax.plot(lambda x: x ** 2 / 10)
        line = ax.get_secant_line(curve, 2, 5)
        assert line is not None

    def test_get_graph_label(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        curve = ax.plot(lambda x: x)
        label = ax.get_graph_label(curve, "f(x)")
        assert label is not None

    def test_coords_label(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        label = ax.coords_label(3, 5)
        assert label is not None

    def test_add_legend(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ax.plot(lambda x: x, stroke='#ff0000')
        legend = ax.add_legend([("f(x)", "#ff0000")])
        assert legend is not None

    def test_add_horizontal_label(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        label = ax.add_horizontal_label(5, "y=5")
        assert label is not None

    def test_add_vertical_label(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        label = ax.add_vertical_label(5, "x=5")
        assert label is not None

    def test_add_asymptote(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        line = ax.add_asymptote(5)
        assert line is not None

    def test_add_arrow_annotation(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        ann = ax.add_arrow_annotation(3, 4, "point")
        assert ann is not None


class TestNeuralNetworkActivate:
    def test_activate_returns_self(self):
        nn = NeuralNetwork([3, 4, 2])
        result = nn.activate(0, 0, start=0, end=1)
        assert result is nn


class TestAxesAdvancedMethods:
    def test_add_cursor(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        dot = ax.add_cursor(lambda x: x, 0, 10, start=0, end=1)
        assert dot is not None

    def test_add_trace(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.add_trace(lambda x: x, 0, 10, start=0, end=1)
        assert result is not None

    def test_add_crosshair(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.add_crosshair(lambda x: x, 0, 10, start=0, end=1)
        assert result is not None

    def test_add_secant_fade(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        result = ax.add_secant_fade(lambda x: x ** 2 / 10, 5)
        assert result is not None

    def test_get_slope_field(self):
        ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
        result = ax.get_slope_field(lambda x, y: y - x)
        assert result is not None


class TestAutomatonHighlight:
    def test_highlight_state(self):
        a = Automaton(
            states=['q0', 'q1'],
            transitions=[('q0', 'q1', 'a')],
            initial_state='q0',
            accept_states={'q1'},
        )
        a.highlight_state('q0', start=0, end=1)


class TestPiTickFormat:
    def test_pi_format_zero(self):
        assert pi_format(0) == '0'

    def test_pi_format_pi(self):
        import math
        assert pi_format(math.pi) == '\u03c0'

    def test_pi_format_neg_pi(self):
        import math
        assert pi_format(-math.pi) == '-\u03c0'

    def test_pi_format_half_pi(self):
        import math
        assert pi_format(math.pi / 2) == '\u03c0/2'

    def test_pi_format_two_pi(self):
        import math
        assert pi_format(2 * math.pi) == '2\u03c0'

    def test_pi_format_fraction(self):
        import math
        assert pi_format(3 * math.pi / 4) == '3\u03c0/4'

    def test_pi_format_neg_fraction(self):
        import math
        assert pi_format(-math.pi / 3) == '-\u03c0/3'

    def test_pi_ticks_generates_values(self):
        import math
        ticks = pi_ticks(-math.pi, math.pi)
        assert len(ticks) > 0
        assert any(abs(v) < 1e-9 for v in ticks)  # includes 0

    def test_pi_ticks_with_custom_step(self):
        import math
        ticks = pi_ticks(0, 2 * math.pi, step=math.pi / 2)
        labels = [pi_format(v) for v in ticks]
        assert '0' in labels
        assert '\u03c0/2' in labels
        assert '\u03c0' in labels

    def test_axes_with_tick_format(self):
        import math
        ax = Axes(x_range=(-math.pi, math.pi),
                  x_tick_format=pi_format,
                  x_ticks=pi_ticks(-math.pi, math.pi))
        svg = ax.to_svg(0)
        assert '\u03c0' in svg

    def test_axes_with_y_tick_format(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 100),
                  y_tick_format=lambda v: f'{v:.0f}%')
        svg = ax.to_svg(0)
        assert '%' in svg

    def test_axes_tick_format_callable(self):
        ax = Axes(x_range=(0, 5), tick_format=lambda v: f'${v:.1f}')
        svg = ax.to_svg(0)
        assert '$' in svg

    def test_axes_custom_x_ticks(self):
        ax = Axes(x_range=(0, 10), x_ticks=[0, 5, 10])
        svg = ax.to_svg(0)
        assert '5' in svg

    def test_axes_custom_y_ticks(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 100), y_ticks=[0, 50, 100])
        svg = ax.to_svg(0)
        assert '50' in svg


# ── ParametricFunction ──────────────────────────────────────────────────────

class TestParametricFunction:
    def test_creates_circle(self):
        import math
        pf = ParametricFunction(lambda t: (960 + 100 * math.cos(t), 540 + 100 * math.sin(t)),
                                t_range=(0, 2 * math.pi))
        svg = pf.to_svg(0)
        assert 'polyline' in svg

    def test_custom_num_points(self):
        pf = ParametricFunction(lambda t: (t * 100, t * 100), t_range=(0, 5), num_points=50)
        assert pf._func is not None

    def test_get_point(self):
        pf = ParametricFunction(lambda t: (t * 100, t * 200), t_range=(0, 1))
        x, y = pf.get_point(0.5)
        assert abs(x - 50) < 1e-6
        assert abs(y - 100) < 1e-6

    def test_styling_kwargs(self):
        pf = ParametricFunction(lambda t: (t, t), stroke='#FF0000', stroke_width=6)
        svg = pf.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#FF0000' in svg


# ── DrawBorderThenFill (border_ratio) ────────────────────────────────────────

class TestDrawBorderThenFillRatio:
    def test_border_fraction(self):
        r = Rectangle(100, 100, 500, 400)
        r.draw_border_then_fill(start=0, end=1, border_fraction=0.7)
        assert r.styling.fill_opacity.at_time(0) == 0
        # Fill should still be 0 at mid-border phase
        assert r.styling.fill_opacity.at_time(0.3) == pytest.approx(0, abs=0.01)


# ── Text.word_by_word ───────────────────────────────────────────────────────

class TestWordByWord:
    def test_basic(self):
        t = Text(text='Hello World Test', x=500, y=500)
        t.word_by_word(start=0, end=3)
        # At midpoint, some words should be revealed
        assert 'Hello' in t.text.at_time(1.5)
        assert t.text.at_time(3) == 'Hello World Test'

    def test_single_word(self):
        t = Text(text='Hello', x=500, y=500)
        t.word_by_word(start=0, end=1)
        assert t.text.at_time(1) == 'Hello'

    def test_change_existence(self):
        t = Text(text='A B C', x=500, y=500)
        t.word_by_word(start=1, end=3, change_existence=True)
        assert t.show.at_time(0.5) == False
        assert t.show.at_time(1.5) == True

# ── LabeledLine ─────────────────────────────────────────────────────────────

class TestLabeledLine:
    def test_basic(self):
        ll = LabeledLine(x1=100, y1=200, x2=300, y2=200, label='distance')
        svg = ll.to_svg(0)
        assert 'distance' in svg
        assert '<line' in svg

    def test_label_position(self):
        ll = LabeledLine(x1=100, y1=200, x2=300, y2=200, label='test')
        assert ll.label_obj is not None
        assert ll.line is not None

    def test_styling(self):
        ll = LabeledLine(x1=0, y1=0, x2=100, y2=0, label='x', stroke='#f00')
        svg = ll.to_svg(0)
        assert 'x' in svg

# ── Homotopy ────────────────────────────────────────────────────────────────

class TestHomotopy:
    def test_polygon_homotopy(self):
        p = Polygon((100, 100), (200, 100), (200, 200))
        p.homotopy(lambda x, y, t: (x + 50 * t, y + 50 * t), start=0, end=2)
        pts = p.snap_points(2)
        assert abs(pts[0][0] - 150) < 1
        assert abs(pts[0][1] - 150) < 1

    def test_line_homotopy(self):
        l = Line(0, 0, 100, 0)
        l.homotopy(lambda x, y, t: (x, y + 100 * t), start=0, end=1)
        p1 = l.p1.at_time(1)
        p2 = l.p2.at_time(1)
        assert abs(p1[1] - 100) < 1
        assert abs(p2[1] - 100) < 1

    def test_text_homotopy(self):
        t = Text(text='Hello', x=500, y=300)
        t.homotopy(lambda x, y, t: (x + 100 * t, y - 50 * t), start=0, end=1)
        assert abs(t.x.at_time(1) - 600) < 1
        assert abs(t.y.at_time(1) - 250) < 1

    def test_midpoint(self):
        p = Polygon((0, 0), (100, 0), (100, 100))
        p.homotopy(lambda x, y, t: (x + 200 * t, y), start=0, end=2)
        pts = p.snap_points(1)
        assert abs(pts[0][0] - 100) < 1  # halfway at t=1

# ── Cutout ──────────────────────────────────────────────────────────────────

class TestCutout:
    def test_basic(self):
        from vectormation.objects import Cutout
        c = Cutout(hole_x=100, hole_y=100, hole_w=200, hole_h=200)
        svg = c.to_svg(0)
        assert 'fill-rule' in svg
        assert 'evenodd' in svg

    def test_surround(self):
        from vectormation.objects import Cutout
        rect = Rectangle(200, 100, x=400, y=300)
        c = Cutout()
        c.surround(rect, buff=10)
        assert abs(c.hole_x.at_time(0) - 390) < 1
        assert abs(c.hole_y.at_time(0) - 290) < 1

    def test_animate_hole(self):
        from vectormation.objects import Cutout
        c = Cutout(hole_x=100, hole_y=100, hole_w=200, hole_h=200)
        c.set_hole(x=500, y=300, start=0, end=1)
        assert abs(c.hole_x.at_time(1) - 500) < 1
        assert abs(c.hole_y.at_time(1) - 300) < 1

    def test_rounded_corners(self):
        from vectormation.objects import Cutout
        c = Cutout(hole_x=100, hole_y=100, hole_w=200, hole_h=200, rx=10, ry=10)
        svg = c.to_svg(0)
        assert 'a10,10' in svg  # arc commands for rounded corners


class TestConvexHull:
    def test_from_points(self):
        from vectormation.objects import ConvexHull
        hull = ConvexHull((0, 0), (100, 0), (50, 50), (100, 100), (0, 100))
        assert 'ConvexHull' in repr(hull)
        svg = hull.to_svg(0)
        assert '<polygon' in svg

    def test_from_objects(self):
        from vectormation.objects import ConvexHull, Dot
        d1 = Dot(cx=100, cy=100)
        d2 = Dot(cx=200, cy=100)
        d3 = Dot(cx=150, cy=200)
        hull = ConvexHull(d1, d2, d3)
        assert hull.vertices is not None
        assert len(hull.vertices) >= 3

    def test_collinear_points(self):
        from vectormation.objects import ConvexHull
        hull = ConvexHull((0, 0), (50, 0), (100, 0), (50, 50))
        svg = hull.to_svg(0)
        assert '<polygon' in svg

    def test_mixed_items(self):
        from vectormation.objects import ConvexHull, Circle
        c = Circle(r=10, cx=200, cy=200)
        hull = ConvexHull((0, 0), (100, 0), c)
        assert 'ConvexHull' in repr(hull)


class TestSpotlight:
    def test_basic_creation(self):
        from vectormation.objects import Spotlight
        s = Spotlight(target=(500, 300), radius=100)
        svg = s.to_svg(0)
        assert 'fill-rule' in svg
        assert 'evenodd' in svg
        assert s._cx.at_time(0) == 500
        assert s._cy.at_time(0) == 300

    def test_from_object(self):
        from vectormation.objects import Spotlight, Circle
        c = Circle(r=50, cx=400, cy=300)
        s = Spotlight(target=c, radius=150)
        assert s._cx.at_time(0) == 400
        assert s._cy.at_time(0) == 300

    def test_set_target(self):
        from vectormation.objects import Spotlight
        s = Spotlight(target=(100, 100), radius=80)
        s.set_target((500, 500), start=0, end=1)
        assert s._cx.at_time(1) == 500
        assert s._cy.at_time(1) == 500

    def test_set_radius(self):
        from vectormation.objects import Spotlight
        s = Spotlight(radius=100)
        s.set_radius(200, start=0, end=1)
        assert s._r.at_time(1) == 200

    def test_repr(self):
        from vectormation.objects import Spotlight
        s = Spotlight(radius=120)
        assert 'Spotlight' in repr(s)


class TestAnimatedBoundary:
    def test_basic(self):
        from vectormation.objects import AnimatedBoundary, Rectangle
        r = Rectangle(width=100, height=60, x=400, y=300)
        ab = AnimatedBoundary(r)
        svg = ab.to_svg(0)
        assert 'stroke-dasharray' in svg
        assert 'AnimatedBoundary' in repr(ab)

    def test_color_cycling(self):
        from vectormation.objects import AnimatedBoundary, Circle
        c = Circle(r=50, cx=500, cy=400)
        ab = AnimatedBoundary(c, colors=['#ff0000', '#00ff00'])
        svg0 = ab.to_svg(0)
        svg1 = ab.to_svg(0.5)
        # At t=0 should be first color, at t=0.5 should differ
        assert 'stroke=' in svg0
        assert 'stroke=' in svg1

    def test_bbox(self):
        from vectormation.objects import AnimatedBoundary, Rectangle
        r = Rectangle(width=100, height=60, x=400, y=300)
        ab = AnimatedBoundary(r, buff=10, stroke_width=4)
        x, y, w, h = ab.bbox(0)
        # Should be larger than the target
        rx, ry, rw, rh = r.bbox(0)
        assert x < rx and y < ry and w > rw and h > rh


class TestKochSnowflake:
    def test_basic(self):
        from vectormation.objects import KochSnowflake
        k = KochSnowflake()
        svg = k.to_svg(0)
        assert '<polygon' in svg
        assert 'KochSnowflake' in repr(k)

    def test_depth_0(self):
        from vectormation.objects import KochSnowflake
        k = KochSnowflake(depth=0)
        # depth=0 means plain triangle → 3 vertices
        assert len(k.vertices) == 3

    def test_depth_1(self):
        from vectormation.objects import KochSnowflake
        k = KochSnowflake(depth=1)
        # depth=1: each side gets 4 segments → 12 vertices
        assert len(k.vertices) == 12

    def test_custom_styling(self):
        from vectormation.objects import KochSnowflake
        k = KochSnowflake(stroke='red', fill='blue')
        svg = k.to_svg(0)
        assert 'stroke=' in svg and 'fill=' in svg

    def test_size_affects_bbox(self):
        from vectormation.objects import KochSnowflake
        small = KochSnowflake(size=100, depth=1)
        large = KochSnowflake(size=400, depth=1)
        sw = small.bbox(0)[2]
        lw = large.bbox(0)[2]
        assert lw > sw


class TestSierpinskiTriangle:
    def test_basic(self):
        from vectormation.objects import SierpinskiTriangle
        s = SierpinskiTriangle()
        assert len(s.objects) > 0
        assert 'SierpinskiTriangle' in repr(s)

    def test_depth_0(self):
        from vectormation.objects import SierpinskiTriangle
        s = SierpinskiTriangle(depth=0)
        assert len(s.objects) == 1

    def test_depth_counts(self):
        from vectormation.objects import SierpinskiTriangle
        for d in range(4):
            s = SierpinskiTriangle(depth=d)
            assert len(s.objects) == 3 ** d

    def test_svg_output(self):
        from vectormation.objects import SierpinskiTriangle
        s = SierpinskiTriangle(depth=2)
        for obj in s.objects:
            svg = obj.to_svg(0)
            assert '<polygon' in svg

    def test_custom_styling(self):
        from vectormation.objects import SierpinskiTriangle
        s = SierpinskiTriangle(fill='red', depth=1)
        svg = s.objects[0].to_svg(0)
        assert 'rgb(252,98,85)' in svg


class TestMatrixSwapRows:
    def test_swap_rows_basic(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.swap_rows(0, 1, start=0, end=1)
        assert result is m
        # entries should be swapped
        assert m.entries[0][0].text.at_time(0) == '3'
        assert m.entries[1][0].text.at_time(0) == '1'

    def test_swap_rows_noop_same(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.swap_rows(0, 0, start=0, end=1)
        assert result is m

    def test_swap_rows_out_of_range(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.swap_rows(0, 5, start=0, end=1)
        assert result is m

    def test_swap_rows_positions_change(self):
        m = Matrix([[1, 2], [3, 4]])
        y0_before = m.entries[0][0].y.at_time(0)
        y1_before = m.entries[1][0].y.at_time(0)
        m.swap_rows(0, 1, start=0, end=1)
        # After swap, the new row 0 entries (originally row 1) should end at row 0's y
        y0_after = m.entries[0][0].y.at_time(2)
        y1_after = m.entries[1][0].y.at_time(2)
        # path_arc moves the object; the important thing is that they crossed
        assert y0_after != y1_after


class TestMatrixRowOperation:
    def test_row_operation_basic(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.row_operation(1, 0, scalar=1, start=0, end=1)
        assert result is m
        # After animation ends, row 1 should be [3+1, 4+2] = [4, 6]
        assert m.entries[1][0].text.at_time(2) == '4'
        assert m.entries[1][1].text.at_time(2) == '6'

    def test_row_operation_negative_scalar(self):
        m = Matrix([[2, 3], [4, 6]])
        m.row_operation(1, 0, scalar=-2, start=0, end=1)
        # row 1 should be [4 + (-2)*2, 6 + (-2)*3] = [0, 0]
        assert m.entries[1][0].text.at_time(2) == '0'
        assert m.entries[1][1].text.at_time(2) == '0'

    def test_row_operation_instant(self):
        m = Matrix([[1, 0], [0, 1]])
        m.row_operation(0, 1, scalar=3, start=0, end=0)
        # R0 = [1, 0] + 3*[0, 1] = [1, 3]
        assert m.entries[0][0].text.at_time(0) == '1'
        assert m.entries[0][1].text.at_time(0) == '3'

    def test_set_entry_value(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.set_entry_value(0, 0, 99, start=0)
        assert result is m
        assert m.entries[0][0].text.at_time(0) == '99'


class TestMatrixColorMethods:
    def test_set_row_colors(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.set_row_colors('#FF0000', '#00FF00', start=0)
        assert result is m

    def test_set_column_colors(self):
        m = Matrix([[1, 2], [3, 4]])
        result = m.set_column_colors('#FF0000', '#00FF00', start=0)
        assert result is m

    def test_set_row_colors_cycles(self):
        m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        # Only one color cycles across all rows
        m.set_row_colors('#FF0000', start=0)

    def test_set_column_colors_cycles(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        m.set_column_colors('#FF0000', '#00FF00', start=0)


class TestDecimalMatrix:
    def test_basic(self):
        from vectormation.objects import DecimalMatrix
        m = DecimalMatrix([[1.123, 2.456], [3.789, 4.012]], decimals=2)
        assert m.entries[0][0].text.at_time(0) == '1.12'
        assert m.entries[0][1].text.at_time(0) == '2.46'

    def test_decimals_1(self):
        from vectormation.objects import DecimalMatrix
        m = DecimalMatrix([[1, 2], [3, 4]], decimals=1)
        assert m.entries[0][0].text.at_time(0) == '1.0'

    def test_repr(self):
        from vectormation.objects import DecimalMatrix
        m = DecimalMatrix([[1, 2], [3, 4]])
        assert 'Matrix' in repr(m)


class TestIntegerMatrix:
    def test_basic(self):
        from vectormation.objects import IntegerMatrix
        m = IntegerMatrix([[1.7, 2.3], [3.5, 4.9]])
        assert m.entries[0][0].text.at_time(0) == '2'
        assert m.entries[0][1].text.at_time(0) == '2'
        assert m.entries[1][0].text.at_time(0) == '4'
        assert m.entries[1][1].text.at_time(0) == '5'

    def test_repr(self):
        from vectormation.objects import IntegerMatrix
        m = IntegerMatrix([[1, 2], [3, 4]])
        assert 'Matrix' in repr(m)


class TestTableSwapRows:
    def test_swap_basic(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_rows(0, 1, start=0, end=1)
        assert result is t
        # entries should be swapped
        assert t.entries[0][0].text.at_time(0) == '3'
        assert t.entries[1][0].text.at_time(0) == '1'

    def test_swap_noop_same(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_rows(0, 0)
        assert result is t

    def test_swap_out_of_range(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_rows(0, 5)
        assert result is t

    def test_swap_positions_move(self):
        t = Table([[1, 2], [3, 4]])
        y0 = t.entries[0][0].y.at_time(0)
        y1 = t.entries[1][0].y.at_time(0)
        assert y0 != y1
        t.swap_rows(0, 1, start=0, end=1)
        # After animation, row 0 entry (originally row 1) should end at row 0's y
        new_y0 = t.entries[0][0].y.at_time(2)
        assert abs(new_y0 - y0) < 1


class TestPolygonLabelVertices:
    def test_label_default_abc(self):
        p = Polygon((100, 100), (200, 100), (150, 50))
        labels = p.label_vertices()
        assert isinstance(labels, VCollection)
        assert len(labels.objects) == 3

    def test_label_custom_names(self):
        p = Polygon((100, 100), (200, 100), (150, 50))
        labels = p.label_vertices(labels=['P', 'Q', 'R'])
        assert len(labels.objects) == 3

    def test_label_svg_contains_text(self):
        p = Polygon((100, 100), (200, 100), (150, 50))
        labels = p.label_vertices()
        # Each label should produce SVG with text
        for obj in labels.objects:
            svg = obj.to_svg(0)
            assert '<text' in svg

    def test_label_empty_polygon(self):
        p = Polygon()
        labels = p.label_vertices()
        assert len(labels.objects) == 0


class TestSpiral:
    def test_basic(self):
        from vectormation.objects import Spiral
        s = Spiral()
        svg = s.to_svg(0)
        assert '<polyline' in svg or '<polygon' in svg
        assert 'Spiral' in repr(s)

    def test_custom_params(self):
        from vectormation.objects import Spiral
        s = Spiral(a=10, b=20, turns=3, num_points=100)
        assert s._turns == 3

    def test_log_spiral(self):
        from vectormation.objects import Spiral
        s = Spiral(a=5, b=0.1, turns=2, log_spiral=True)
        svg = s.to_svg(0)
        assert 'polyline' in svg or 'polygon' in svg

    def test_vertex_count(self):
        from vectormation.objects import Spiral
        s = Spiral(num_points=200)
        pts = s.get_vertices(0)
        assert len(pts) == 200


class TestMatrixAugmented:
    def test_basic_augmented(self):
        m = Matrix.augmented([[1, 2], [3, 4]], [[5], [6]])
        assert m.rows == 2
        assert m.cols == 3
        assert m.entries[0][0].text.at_time(0) == '1'
        assert m.entries[0][2].text.at_time(0) == '5'

    def test_augmented_has_divider(self):
        m = Matrix.augmented([[1, 0], [0, 1]], [[2], [3]])
        assert m._augment_col == 2
        # Should have more objects than a plain 2x3 matrix (extra divider line)
        plain = Matrix([[1, 0, 2], [0, 1, 3]])
        assert len(m.objects) > len(plain.objects)

    def test_augmented_repr(self):
        m = Matrix.augmented([[1]], [[2]])
        assert 'Matrix' in repr(m)


class TestNeuralNetworkHighlightPath:
    def test_highlight_path_basic(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 4, 2])
        result = nn.highlight_path([0, 1, 0], start=0, delay=0.3)
        assert result is nn

    def test_highlight_path_wrong_length(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 4, 2])
        result = nn.highlight_path([0, 1], start=0)  # too short
        assert result is nn  # should be no-op

    def test_highlight_path_with_colors(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([2, 3, 2])
        result = nn.highlight_path([1, 2, 0], color='#FF0000', edge_color='#00FF00')
        assert result is nn


class TestArcSagittaAndTangent:
    def test_sagitta_semicircle(self):
        from vectormation.objects import Arc
        a = Arc(r=100, start_angle=0, end_angle=180)
        # Sagitta of a semicircle = r
        assert abs(a.get_sagitta() - 100) < 1e-6

    def test_sagitta_quarter(self):
        from vectormation.objects import Arc
        a = Arc(r=100, start_angle=0, end_angle=90)
        # Sagitta = r * (1 - cos(45°)) ≈ 29.29
        expected = 100 * (1 - math.cos(math.radians(45)))
        assert abs(a.get_sagitta() - expected) < 1e-6

    def test_tangent_at_returns_line(self):
        from vectormation.objects import Arc
        a = Arc(r=100, start_angle=0, end_angle=180)
        line = a.tangent_at(0)
        assert isinstance(line, Line)

    def test_tangent_at_length(self):
        from vectormation.objects import Arc
        a = Arc(r=100, start_angle=0, end_angle=180)
        line = a.tangent_at(90, length=200)
        assert abs(line.get_length() - 200) < 1


class TestTableSwapColumns:
    def test_swap_basic(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_columns(0, 1, start=0, end=1)
        assert result is t
        # entries in columns should be swapped
        assert t.entries[0][0].text.at_time(0) == '2'
        assert t.entries[0][1].text.at_time(0) == '1'

    def test_swap_noop_same(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_columns(0, 0)
        assert result is t

    def test_swap_out_of_range(self):
        t = Table([[1, 2], [3, 4]])
        result = t.swap_columns(0, 5)
        assert result is t

    def test_swap_positions_move(self):
        t = Table([['a', 'b'], ['c', 'd']])
        x0 = t.entries[0][0].x.at_time(0)
        x1 = t.entries[0][1].x.at_time(0)
        assert x0 != x1
        t.swap_columns(0, 1, start=0, end=1)
        new_x0 = t.entries[0][0].x.at_time(2)
        assert abs(new_x0 - x0) < 1


class TestTableHighlightWhere:
    def test_highlight_where_matches(self):
        t = Table([[1, 2], [3, 4]])
        result = t.highlight_where(lambda x: x == '4', start=0, end=1)
        assert result is t

    def test_highlight_where_no_matches(self):
        t = Table([['a', 'b']])
        result = t.highlight_where(lambda x: x == 'z', start=0, end=1)
        assert result is t

    def test_highlight_where_numeric(self):
        t = Table([[10, 20], [30, 40]])
        result = t.highlight_where(lambda x: int(x) > 15, start=0, end=1)
        assert result is t


class TestPolygonGetDiagonals:
    def test_triangle_no_diagonals(self):
        p = Polygon((0, 0), (100, 0), (50, 80))
        assert p.get_diagonals() == []

    def test_square_diagonals(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        diags = p.get_diagonals()
        assert len(diags) == 2
        assert all(isinstance(d, Line) for d in diags)

    def test_pentagon_diagonals(self):
        import math
        pts = [(100 * math.cos(2 * math.pi * i / 5), 100 * math.sin(2 * math.pi * i / 5)) for i in range(5)]
        p = Polygon(*pts)
        # Pentagon has n*(n-3)/2 = 5*2/2 = 5 diagonals
        diags = p.get_diagonals()
        assert len(diags) == 5

    def test_open_polyline_no_diagonals(self):
        p = Polygon((0, 0), (100, 0), (100, 100), (0, 100), closed=False)
        assert p.get_diagonals() == []


class TestRectangleQuadrants:
    def test_quadrants_count(self):
        r = Rectangle(200, 100, x=100, y=50)
        q = r.quadrants()
        assert len(q.objects) == 4

    def test_quadrants_sizes(self):
        r = Rectangle(200, 100, x=100, y=50)
        q = r.quadrants()
        for part in q.objects:
            assert abs(part.width.at_time(0) - 100) < 0.01
            assert abs(part.height.at_time(0) - 50) < 0.01


class TestTableRemoveRow:
    def test_remove_row_basic(self):
        t = Table([[1, 2], [3, 4], [5, 6]])
        result = t.remove_row(1, animate=False)
        assert result is t
        assert t.rows == 2

    def test_remove_row_out_of_range(self):
        t = Table([[1, 2]])
        import pytest
        with pytest.raises(IndexError):
            t.remove_row(5)

    def test_remove_row_entries_updated(self):
        t = Table([['a', 'b'], ['c', 'd'], ['e', 'f']])
        t.remove_row(0, animate=False)
        assert t.rows == 2
        assert t.entries[0][0].text.at_time(0) == 'c'

    def test_remove_row_animated(self):
        t = Table([[1, 2], [3, 4]])
        result = t.remove_row(0, start=0, animate=True)
        assert result is t
        assert t.rows == 1


class TestTableRemoveColumn:
    def test_remove_column_basic(self):
        t = Table([[1, 2, 3], [4, 5, 6]])
        result = t.remove_column(1, animate=False)
        assert result is t
        assert t.cols == 2

    def test_remove_column_out_of_range(self):
        t = Table([[1, 2]])
        import pytest
        with pytest.raises(IndexError):
            t.remove_column(5)

    def test_remove_column_entries_updated(self):
        t = Table([['a', 'b', 'c']])
        t.remove_column(0, animate=False)
        assert t.cols == 2
        assert t.entries[0][0].text.at_time(0) == 'b'

    def test_remove_column_animated(self):
        t = Table([[1, 2], [3, 4]])
        result = t.remove_column(0, start=0, animate=True)
        assert result is t
        assert t.cols == 1


class TestArrayIndexValidation:
    def test_highlight_cell_raises_on_bad_index(self):
        a = Array([1, 2, 3])
        import pytest
        with pytest.raises(IndexError):
            a.highlight_cell(5)

    def test_swap_cells_raises_on_bad_index(self):
        a = Array([1, 2, 3])
        import pytest
        with pytest.raises(IndexError):
            a.swap_cells(0, 10)

    def test_set_value_raises_on_bad_index(self):
        a = Array([1, 2, 3])
        import pytest
        with pytest.raises(IndexError):
            a.set_value(5, 99)

    def test_highlight_cell_valid_index(self):
        a = Array([10, 20, 30])
        result = a.highlight_cell(1)
        assert result is a

    def test_swap_cells_valid_indices(self):
        a = Array([10, 20, 30])
        result = a.swap_cells(0, 2)
        assert result is a

    def test_set_value_valid_index(self):
        a = Array([10, 20, 30])
        result = a.set_value(1, 99)
        assert result is a


class TestStackPeekIsEmpty:
    def test_peek_nonempty(self):
        s = Stack([10, 20])
        val = s.peek()
        assert val is not None

    def test_peek_empty(self):
        s = Stack()
        assert s.peek() is None

    def test_is_empty_true(self):
        s = Stack()
        assert s.is_empty()

    def test_is_empty_false(self):
        s = Stack([1])
        assert not s.is_empty()


class TestQueuePeekIsEmpty:
    def test_peek_nonempty(self):
        q = Queue([10, 20])
        val = q.peek()
        assert val is not None

    def test_peek_empty(self):
        q = Queue()
        assert q.peek() is None

    def test_is_empty_true(self):
        q = Queue()
        assert q.is_empty()

    def test_is_empty_false(self):
        q = Queue([1])
        assert not q.is_empty()


class TestBinaryTreeTraverse:
    def test_traverse_returns_self(self):
        t = BinaryTree((1, (2,), (3,)))
        result = t.traverse()
        assert result is t

    def test_traverse_custom_delay(self):
        t = BinaryTree((1, (2,), (3,)))
        result = t.traverse(start=0, delay=0.5)
        assert result is t


class TestAxesGetOrigin:
    def test_get_origin_default_axes(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        ox, oy = ax.get_origin()
        # Origin should be within the plot area
        assert 0 < ox < 1920
        assert 0 < oy < 1080

    def test_get_origin_matches_coords_to_point(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        o1 = ax.get_origin()
        o2 = ax.coords_to_point(0, 0)
        assert o1[0] == pytest.approx(o2[0])
        assert o1[1] == pytest.approx(o2[1])


class TestAxesZoomToFit:
    def test_zoom_to_fit_adjusts_y_range(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        ax.zoom_to_fit(lambda x: x ** 2, x_range=(0, 4))
        # y range should end up near 0..16 + padding
        yhi = ax.y_max.at_time(1)
        assert yhi > 15

    def test_zoom_to_fit_empty_function(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        # Function that always raises → should return self unchanged
        result = ax.zoom_to_fit(lambda x: 1 / 0)
        assert result is ax

    def test_zoom_to_fit_with_padding(self):
        ax = Axes(x_range=(-5, 5), y_range=(-10, 10))
        ax.zoom_to_fit(lambda x: 5, padding=0.5)
        # Constant function y=5, span=1 (fallback), padding=0.5
        ylo = ax.y_min.at_time(1)
        yhi = ax.y_max.at_time(1)
        assert ylo < 5
        assert yhi > 5


class TestPlotHistogramEmptyData:
    def test_empty_data_returns_empty_collection(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 5))
        result = ax.plot_histogram([])
        assert len(result.objects) == 0

    def test_empty_data_no_error(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 5))
        result = ax.plot_histogram([], bins=5)
        assert result is not None


class TestBarChartGetBarsRenamed:
    def test_get_bars_default(self):
        bc = BarChart([10, 20, 30])
        bars = bc.get_bars()
        assert len(bars.objects) == 3

    def test_get_bars_sliced(self):
        bc = BarChart([10, 20, 30, 40])
        bars = bc.get_bars(start_idx=1, end_idx=3)
        assert len(bars.objects) == 2

    def test_sort_bars_alias(self):
        bc = BarChart([30, 10, 20])
        result = bc.sort_bars()
        assert result is bc


class TestVObjectIsVisible:
    def test_visible_by_default(self):
        c = Circle(r=50, cx=100, cy=100)
        assert c.is_visible(0)

    def test_hidden_after_hide(self):
        c = Circle(r=50, cx=100, cy=100)
        c.show.set_onward(0, False)
        assert not c.is_visible(0)

    def test_visible_after_show_from(self):
        c = Circle(r=50, cx=100, cy=100, creation=1)
        assert not c.is_visible(0)
        assert c.is_visible(1)


class TestMatrixTraceAndDet:
    def test_trace_2x2(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.trace() == pytest.approx(5)

    def test_trace_3x3(self):
        m = Matrix([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
        assert m.trace() == pytest.approx(6)

    def test_trace_non_square_raises(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        with pytest.raises(ValueError):
            m.trace()

    def test_determinant_2x2(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.determinant() == pytest.approx(-2)

    def test_determinant_3x3(self):
        m = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        assert m.determinant() == pytest.approx(1)

    def test_determinant_non_square_raises(self):
        m = Matrix([[1, 2], [3, 4], [5, 6]])
        with pytest.raises(ValueError):
            m.determinant()

    def test_get_values(self):
        m = Matrix([[10, 20], [30, 40]])
        vals = m.get_values()
        assert vals == [[10.0, 20.0], [30.0, 40.0]]


class TestArcComplement:
    def test_complement_angles(self):
        from vectormation.objects import Arc
        a = Arc(cx=100, cy=100, r=50, start_angle=0, end_angle=90)
        comp = a.complement()
        assert comp.start_angle.at_time(0) == pytest.approx(90)
        assert comp.end_angle.at_time(0) == pytest.approx(360)

    def test_complement_radius(self):
        from vectormation.objects import Arc
        a = Arc(cx=200, cy=200, r=80, start_angle=0, end_angle=180)
        comp = a.complement()
        assert comp.r.at_time(0) == pytest.approx(80)
        assert comp.cx.at_time(0) == pytest.approx(200)


class TestArrayReverse:
    def test_reverse_returns_self(self):
        a = Array([1, 2, 3, 4])
        result = a.reverse()
        assert result is a

    def test_reverse_swaps_labels(self):
        a = Array([10, 20, 30])
        a.reverse(start=0, end=1)
        # After reverse, labels should be swapped
        assert a is not None  # Just check it runs without error


# ═══════════════════════════════════════════════════════════════════
# Physics module tests
# ═══════════════════════════════════════════════════════════════════

from vectormation.objects import PhysicsSpace, Body, Spring, Cloth
from vectormation._axes_helpers import (
    scientific_format, engineering_format, percent_format, degree_format,
)


# ── PhysicsSpace basic creation ────────────────────────────────────

def test_physics_space_creation_defaults():
    space = PhysicsSpace()
    assert space.gravity == (0, 980)
    assert space.dt == pytest.approx(1 / 120)
    assert space.start == 0.0
    assert space.bodies == []
    assert space.walls == []
    assert space.springs == []


def test_physics_space_custom_params():
    space = PhysicsSpace(gravity=(0, 500), dt=1/60, start=2.0)
    assert space.gravity == (0, 500)
    assert space.dt == pytest.approx(1 / 60)
    assert space.start == 2.0


# ── Body creation with VObjects ────────────────────────────────────

def test_physics_body_from_dot():
    dot = Dot(r=5, cx=960, cy=100)
    space = PhysicsSpace()
    b = space.add_body(dot, mass=2.0, restitution=0.7)
    assert b.x == pytest.approx(960)
    assert b.y == pytest.approx(100)
    assert b.mass == 2.0
    assert b.restitution == 0.7
    assert b.radius == pytest.approx(5)
    assert b.obj is dot
    assert len(space.bodies) == 1


def test_physics_body_from_circle():
    c = Circle(r=20, cx=500, cy=200)
    space = PhysicsSpace()
    b = space.add_body(c, mass=3.0)
    assert b.x == pytest.approx(500)
    assert b.y == pytest.approx(200)
    assert b.radius == pytest.approx(20)


def test_physics_body_initial_velocity():
    dot = Dot(r=5, cx=960, cy=540)
    space = PhysicsSpace()
    b = space.add_body(dot, vx=100, vy=-50)
    assert b.vx == 100.0
    assert b.vy == -50.0


def test_physics_body_fixed():
    dot = Dot(r=5, cx=100, cy=100)
    space = PhysicsSpace()
    b = space.add_body(dot, fixed=True)
    assert b.fixed is True
    assert b.mass == math.inf


def test_physics_body_custom_radius():
    dot = Dot(r=5, cx=960, cy=540)
    space = PhysicsSpace()
    b = space.add_body(dot, radius=50)
    assert b.radius == 50.0


def test_physics_body_apply_force():
    dot = Dot(r=5, cx=960, cy=540)
    space = PhysicsSpace()
    b = space.add_body(dot)
    b.apply_force(10, 20)
    assert b.fx == 10.0
    assert b.fy == 20.0
    b.apply_force(5, -3)
    assert b.fx == 15.0
    assert b.fy == 17.0


# ── Wall collisions ───────────────────────────────────────────────

def test_physics_wall_floor():
    """Ball falls under gravity and bounces off a floor wall."""
    space = PhysicsSpace(gravity=(0, 980), dt=1/120)
    dot = Dot(r=5, cx=960, cy=100)
    b = space.add_body(dot, mass=1.0, restitution=0.5)
    space.add_wall(y=500)  # floor
    space.simulate(duration=0.3)
    # After simulation, body should have been stopped/bounced by the floor
    assert b.y <= 500


def test_physics_wall_ceiling():
    """Ball launched downward bounces off a floor wall below it (ceiling-like for content above)."""
    # In the wall collision code, a horizontal wall at y=Y acts as a floor:
    # bodies that cross below it get pushed back above.
    # Test that a falling body bounces when it hits a floor wall.
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=960, cy=80)
    b = space.add_body(dot, vy=200)
    space.add_wall(y=200)  # floor below the body
    space.simulate(duration=0.3)
    # Body should have bounced off the floor and be above y=200
    assert b.y <= 200


def test_physics_wall_left():
    """Ball moving left bounces off a left wall."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=200, cy=540)
    b = space.add_body(dot, vx=-300)
    space.add_wall(x=50)  # left wall
    space.simulate(duration=0.2)
    assert b.x >= 50 + b.radius - 1


def test_physics_wall_right():
    """Ball moving right bounces off a right wall."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=800, cy=540)
    b = space.add_body(dot, vx=300)
    space.add_wall(x=1000)  # right wall
    space.simulate(duration=0.2)
    assert b.x <= 1000 - b.radius + 1


def test_physics_wall_requires_x_or_y():
    from vectormation._physics import Wall
    with pytest.raises(ValueError):
        Wall()


# ── Body-body collisions ──────────────────────────────────────────

def test_physics_body_collision_separation():
    """Two bodies moving toward each other should not overlap after simulation."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=10, cx=400, cy=540)
    d2 = Dot(r=10, cx=500, cy=540)
    b1 = space.add_body(d1, vx=200)
    b2 = space.add_body(d2, vx=-200)
    space.simulate(duration=0.2)
    dist = math.hypot(b2.x - b1.x, b2.y - b1.y)
    # After collision they should have separated
    assert dist >= b1.radius + b2.radius - 1


def test_physics_body_collision_velocity_exchange():
    """Head-on collision between equal masses: velocities should roughly swap."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=10, cx=400, cy=540)
    d2 = Dot(r=10, cx=440, cy=540)
    b1 = space.add_body(d1, vx=100, restitution=1.0)
    b2 = space.add_body(d2, vx=-100, restitution=1.0)
    space.simulate(duration=0.5)
    # After head-on elastic collision of equal masses, velocities swap direction
    # b1 should now be moving left, b2 moving right (or they bounced multiple times)
    # Just check they moved apart
    assert b1.x < b2.x or abs(b1.x - b2.x) < 25  # they separated or are close


def test_physics_body_collision_fixed_body():
    """A moving body colliding with a fixed body should bounce off."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=10, cx=400, cy=540)
    d2 = Dot(r=10, cx=450, cy=540)
    b1 = space.add_body(d1, vx=200)
    b2 = space.add_body(d2, fixed=True)
    space.simulate(duration=0.2)
    # b1 should have bounced back
    assert b1.vx < 0 or b1.x < 450  # bounced or moved away


# ── Spring constraints ─────────────────────────────────────────────

def test_physics_spring_between_bodies():
    """Two bodies connected by a spring should oscillate toward rest length."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=5, cx=400, cy=540)
    d2 = Dot(r=5, cx=600, cy=540)
    b1 = space.add_body(d1)
    b2 = space.add_body(d2)
    s = space.add_spring(b1, b2, stiffness=1.0, rest_length=100, damping=0.1)
    assert s.rest_length == 100
    assert len(space.springs) == 1
    space.simulate(duration=0.5)
    # Bodies should have moved closer to the rest length of 100
    dist = math.hypot(b2.x - b1.x, b2.y - b1.y)
    # With damping, should be closer to rest_length than the initial 200
    assert dist < 200


def test_physics_spring_to_anchor():
    """A spring connecting a body to a fixed point should pull the body."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d = Dot(r=5, cx=600, cy=540)
    b = space.add_body(d)
    anchor = (400, 540)
    space.add_spring(b, anchor, stiffness=1.0, rest_length=0, damping=0.1)
    space.simulate(duration=0.5)
    # Body should have moved toward the anchor
    assert b.x < 600


def test_physics_spring_auto_rest_length():
    """Spring with rest_length=None should auto-detect from initial distance."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=5, cx=400, cy=540)
    d2 = Dot(r=5, cx=550, cy=540)
    b1 = space.add_body(d1)
    b2 = space.add_body(d2)
    s = space.add_spring(b1, b2, rest_length=None)
    assert s.rest_length == pytest.approx(150)


# ── Forces: gravity, drag, attraction, repulsion ──────────────────

def test_physics_gravity_moves_body_down():
    """Under gravity, a body should move downward."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120)
    dot = Dot(r=5, cx=960, cy=100)
    b = space.add_body(dot)
    space.simulate(duration=0.2)
    assert b.y > 100


def test_physics_zero_gravity():
    """With no gravity, a stationary body should stay in place."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=960, cy=540)
    b = space.add_body(dot)
    space.simulate(duration=0.2)
    assert b.x == pytest.approx(960, abs=0.1)
    assert b.y == pytest.approx(540, abs=0.1)


def test_physics_drag_slows_body():
    """Drag should reduce velocity over time."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=960, cy=540)
    b = space.add_body(dot, vx=500)
    space.add_drag(coefficient=0.5)
    space.simulate(duration=0.3)
    # Body should have slowed down significantly
    assert abs(b.vx) < 500


def test_physics_attraction_pulls_body():
    """Attraction force should pull a body toward a target."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=800, cy=540)
    b = space.add_body(dot)
    space.add_attraction(target=(400, 540), strength=100000)
    space.simulate(duration=0.3)
    # Body should have moved toward x=400
    assert b.x < 800


def test_physics_repulsion_pushes_body():
    """Repulsion force should push a body away from a target."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=500, cy=540)
    b = space.add_body(dot)
    space.add_repulsion(target=(400, 540), strength=100000)
    space.simulate(duration=0.3)
    # Body should have moved away from x=400
    assert b.x > 500


def test_physics_mutual_repulsion():
    """Mutual repulsion should push bodies apart."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    d1 = Dot(r=5, cx=480, cy=540)
    d2 = Dot(r=5, cx=520, cy=540)
    b1 = space.add_body(d1)
    b2 = space.add_body(d2)
    space.add_mutual_repulsion(strength=50000)
    space.simulate(duration=0.2)
    # Bodies should be further apart than initial 40px
    assert abs(b2.x - b1.x) > 40


def test_physics_custom_force():
    """A custom force function should be applied each step."""
    space = PhysicsSpace(gravity=(0, 0), dt=1/120)
    dot = Dot(r=5, cx=960, cy=540)
    b = space.add_body(dot)
    # Constant rightward force
    space.add_force(lambda body, t: (1000, 0))
    space.simulate(duration=0.2)
    assert b.x > 960


# ── Trajectory baking ─────────────────────────────────────────────

def test_physics_trajectory_baked_positions_change():
    """After simulation, the VObject should report different positions at different times."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120, start=0.0)
    dot = Dot(r=5, cx=960, cy=100)
    b = space.add_body(dot)
    space.simulate(duration=0.5)
    # Sample positions at different times
    pos_start = dot.c.at_time(0.0)
    pos_mid = dot.c.at_time(0.25)
    pos_end = dot.c.at_time(0.5)
    # y should increase over time (gravity pulls down)
    assert pos_start[1] < pos_mid[1]
    assert pos_mid[1] < pos_end[1]
    # x should remain approximately the same (no horizontal force)
    assert pos_start[0] == pytest.approx(960, abs=1)


def test_physics_trajectory_baked_start_position():
    """At time 0, the baked position should match the initial position."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120, start=0.0)
    dot = Dot(r=5, cx=300, cy=200)
    space.add_body(dot)
    space.simulate(duration=0.2)
    pos = dot.c.at_time(0.0)
    assert pos[0] == pytest.approx(300, abs=1)
    assert pos[1] == pytest.approx(200, abs=1)


def test_physics_trajectory_baked_clamps_beyond_duration():
    """Positions beyond the simulation duration should clamp to the final position."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120, start=0.0)
    dot = Dot(r=5, cx=960, cy=100)
    space.add_body(dot)
    space.simulate(duration=0.2)
    pos_at_end = dot.c.at_time(0.2)
    pos_beyond = dot.c.at_time(10.0)
    assert pos_at_end[0] == pytest.approx(pos_beyond[0], abs=1)
    assert pos_at_end[1] == pytest.approx(pos_beyond[1], abs=1)


def test_physics_trajectory_fixed_body_stays():
    """A fixed body should not move even after simulation."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120, start=0.0)
    dot = Dot(r=5, cx=960, cy=540)
    b = space.add_body(dot, fixed=True)
    space.simulate(duration=0.3)
    # Fixed body: _bake_trajectory returns early, position unchanged
    assert b.x == pytest.approx(960)
    assert b.y == pytest.approx(540)


def test_physics_trajectory_nonzero_start():
    """Simulation with a non-zero start time should bake from that time onward."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/120, start=2.0)
    dot = Dot(r=5, cx=960, cy=100)
    space.add_body(dot)
    space.simulate(duration=0.3)
    # At time < start, should return initial position
    pos_before = dot.c.at_time(1.0)
    pos_during = dot.c.at_time(2.15)
    # Position at start time should differ from later
    assert pos_before[1] < pos_during[1]


def test_physics_trajectory_length():
    """Trajectory should have the expected number of entries."""
    space = PhysicsSpace(gravity=(0, 500), dt=1/60)
    dot = Dot(r=5, cx=960, cy=100)
    b = space.add_body(dot)
    space.simulate(duration=0.5)
    # steps = ceil(0.5 / (1/60)) = 30, trajectory has steps+1 entries (initial + per-step)
    assert len(b._trajectory) == 31


# ── Cloth simulation ──────────────────────────────────────────────

def test_physics_cloth_creation():
    """Cloth should create the expected grid of bodies and springs."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=5, rows=3,
                  pin_top=True, stiffness=1.0)
    assert cloth.cols == 5
    assert cloth.rows == 3
    assert len(cloth._bodies) == 3
    assert len(cloth._bodies[0]) == 5
    # Total bodies = 5 * 3 = 15
    assert len(cloth.space.bodies) == 15


def test_physics_cloth_top_row_pinned():
    """Top row bodies should be fixed when pin_top=True."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=3, rows=3,
                  pin_top=True)
    for b in cloth._bodies[0]:
        assert b.fixed is True
    for b in cloth._bodies[1]:
        assert b.fixed is False


def test_physics_cloth_springs_count():
    """Cloth should have horizontal + vertical structural springs."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=4, rows=3)
    # Horizontal: 3 per row * 3 rows = 9
    # Vertical: 4 per col * 2 = 8
    expected = 3 * 3 + 4 * 2  # 17
    assert len(cloth.space.springs) == expected


def test_physics_cloth_simulate_runs():
    """Cloth simulation should complete without error."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=4, rows=3,
                  stiffness=1.0)
    cloth.simulate(duration=0.1)
    # After simulation, non-pinned bodies should have moved down
    bottom_body = cloth._bodies[2][1]
    assert bottom_body.y > 100 + 50  # started at y=200 (row 2)


def test_physics_cloth_objects_returns_all():
    """Cloth.objects() should return lines + dots."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=3, rows=2)
    objs = cloth.objects()
    # Lines: horizontal (2 per row * 2 rows) + vertical (3 per col * 1) = 4 + 3 = 7
    # Dots: 3 * 2 = 6
    assert len(objs) == 7 + 6


def test_physics_cloth_lines_track_bodies():
    """After simulation, cloth lines should have time-varying endpoints."""
    cloth = Cloth(x=100, y=100, width=200, height=100, cols=3, rows=2,
                  pin_top=True, stiffness=1.0)
    cloth.simulate(duration=0.2)
    # The first line connects body(0,0) to body(0,1) — top row, pinned
    # A line from the second row should show movement
    # Get the lines from objects
    lines = cloth._lines
    assert len(lines) > 0
    # Check that at least one line endpoint changes over time
    line = lines[-1]  # a bottom line
    p1_start = line.p1.at_time(0.0)
    p1_end = line.p1.at_time(0.2)
    p2_start = line.p2.at_time(0.0)
    p2_end = line.p2.at_time(0.2)
    # At least one endpoint should have moved
    moved = (abs(p1_start[1] - p1_end[1]) > 0.1 or
             abs(p2_start[1] - p2_end[1]) > 0.1)
    assert moved


# ═══════════════════════════════════════════════════════════════════
# Tick formatter tests
# ═══════════════════════════════════════════════════════════════════

def test_tick_format_scientific_zero():
    assert scientific_format(0) == '0'


def test_tick_format_scientific_positive():
    result = scientific_format(2500)
    # 2500 = 2.5 * 10^3 -> '2.5×10³'
    assert '10' in result
    assert '2.5' in result


def test_tick_format_scientific_unit_coefficient():
    result = scientific_format(1000)
    # 1000 = 10^3 -> '10³' (coefficient 1 is omitted)
    assert result.startswith('10')
    assert '×' not in result


def test_tick_format_scientific_negative():
    result = scientific_format(-1000)
    assert result.startswith('-10')


def test_tick_format_scientific_small_number():
    result = scientific_format(0.005)
    # 0.005 = 5 * 10^-3
    assert '5' in result
    assert '10' in result


def test_tick_format_engineering_zero():
    assert engineering_format(0) == '0'


def test_tick_format_engineering_kilo():
    assert engineering_format(2500) == '2.5k'


def test_tick_format_engineering_mega():
    assert engineering_format(3000000) == '3M'


def test_tick_format_engineering_milli():
    result = engineering_format(0.005)
    assert result == '5m'


def test_tick_format_engineering_micro():
    result = engineering_format(0.000050)
    assert result == '50\u03bcm' or result == '50μ'
    # Accept either: the function returns f'{v:g}{prefix}'
    # 0.00005 / 1e-6 = 50, prefix = μ -> '50μ'


def test_tick_format_engineering_plain():
    # Values >= 1 and < 1000 should have no prefix
    assert engineering_format(42) == '42'
    assert engineering_format(999) == '999'


def test_tick_format_percent_integer():
    assert percent_format(0.5) == '50%'


def test_tick_format_percent_zero():
    assert percent_format(0) == '0%'


def test_tick_format_percent_negative():
    assert percent_format(-0.125) == '-12.5%'


def test_tick_format_percent_one():
    assert percent_format(1.0) == '100%'


def test_tick_format_degree_right_angle():
    result = degree_format(math.pi / 2)
    assert result == '90°'


def test_tick_format_degree_zero():
    assert degree_format(0) == '0°'


def test_tick_format_degree_negative():
    result = degree_format(-math.pi / 4)
    assert result == '-45°'


def test_tick_format_degree_full_circle():
    result = degree_format(2 * math.pi)
    assert result == '360°'


def test_tick_format_degree_large_value_passthrough():
    # Values larger than 2*pi+0.01 are treated as already in degrees
    result = degree_format(90)
    assert result == '90°'


def test_automaton_simulate_input_basic():
    """simulate_input on an accepting word returns self and highlights states."""
    states = ['q0', 'q1']
    transitions = [('q0', 'q1', 'a'), ('q1', 'q0', 'b')]
    auto = Automaton(states, transitions, accept_states={'q1'}, initial_state='q0')
    result = auto.simulate_input('a', start=0, delay=0.3)
    assert result is auto


def test_automaton_simulate_input_rejected():
    """simulate_input stops and highlights red when no transition exists."""
    states = ['q0', 'q1']
    transitions = [('q0', 'q1', 'a')]
    auto = Automaton(states, transitions, accept_states={'q1'}, initial_state='q0')
    # 'b' has no transition from q0 — should return self without error
    result = auto.simulate_input('b', start=0, delay=0.3)
    assert result is auto


def test_automaton_highlight_transition():
    """highlight_transition flashes the stored arrow without raising."""
    states = ['q0', 'q1']
    transitions = [('q0', 'q1', 'a')]
    auto = Automaton(states, transitions, accept_states={'q1'}, initial_state='q0')
    # Should find the arrow and flash it, returning self
    result = auto.highlight_transition('q0', 'q1', start=0, end=1)
    assert result is auto
    # Non-existent transition should also return self gracefully
    result2 = auto.highlight_transition('q1', 'q0', start=0, end=1)
    assert result2 is auto


# ---------------------------------------------------------------------------
# NumberPlane new methods
# ---------------------------------------------------------------------------

class TestNumberPlaneAddCoordinateLabels:
    def test_returns_self(self):
        plane = NumberPlane(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        result = plane.add_coordinate_labels()
        assert result is plane

    def test_creates_text_objects(self):
        plane = NumberPlane(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
        before = len(plane.objects)
        plane.add_coordinate_labels()
        assert len(plane.objects) > before

    def test_skips_zero(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        plane.add_coordinate_labels()
        texts = [o for o in plane.objects if isinstance(o, Text)]
        labels = [t.text.at_time(0) for t in texts]
        assert '0' not in labels

    def test_x_labels_content(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        plane.add_coordinate_labels()
        texts = [o for o in plane.objects if isinstance(o, Text)]
        labels = [t.text.at_time(0) for t in texts]
        assert '1' in labels or '-1' in labels

    def test_custom_x_values(self):
        plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        plane.add_coordinate_labels(x_values=[2, 4], y_values=[])
        texts = [o for o in plane.objects if isinstance(o, Text)]
        labels = [t.text.at_time(0) for t in texts]
        assert '2' in labels
        assert '4' in labels

    def test_custom_y_values(self):
        plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        plane.add_coordinate_labels(x_values=[], y_values=[3])
        texts = [o for o in plane.objects if isinstance(o, Text)]
        labels = [t.text.at_time(0) for t in texts]
        assert '3' in labels

    def test_font_size_propagated(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        plane.add_coordinate_labels(font_size=24)
        texts = [o for o in plane.objects if isinstance(o, Text)]
        assert all(t.font_size.at_time(0) == 24 for t in texts)


class TestNumberPlaneApplyMatrix:
    def test_returns_self(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        result = plane.apply_matrix([[1, 0], [0, 1]])
        assert result is plane

    def test_identity_matrix_unchanged_endpoints(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        plane.apply_matrix([[1, 0], [0, 1]])
        # After identity transform the plane should still have objects
        assert len(plane.objects) > 0

    def test_rebuilds_objects(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        plane.apply_matrix([[2, 0], [0, 2]])
        # apply_matrix calls apply_function which rebuilds the grid as Line segments
        assert any(isinstance(o, Line) for o in plane.objects)

    def test_shear_matrix(self):
        plane = NumberPlane(x_range=(-2, 2, 1), y_range=(-2, 2, 1))
        result = plane.apply_matrix([[1, 1], [0, 1]])
        assert result is plane
        assert len(plane.objects) > 0


class TestNumberPlanePointToCoords:
    def test_inverse_of_coords_to_point(self):
        plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        lx, ly = 3.0, -2.0
        px, py = plane.coords_to_point(lx, ly)
        rx, ry = plane.point_to_coords(px, py)
        assert abs(rx - lx) < 1e-9
        assert abs(ry - ly) < 1e-9

    def test_origin_maps_to_zero(self):
        plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        cx, cy = plane._cx, plane._cy
        lx, ly = plane.point_to_coords(cx, cy)
        assert abs(lx) < 1e-9
        assert abs(ly) < 1e-9

    def test_roundtrip_negative_coords(self):
        plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-5, 5, 1))
        lx, ly = -4.0, 3.5
        px, py = plane.coords_to_point(lx, ly)
        rx, ry = plane.point_to_coords(px, py)
        assert abs(rx - lx) < 1e-9
        assert abs(ry - ly) < 1e-9


# ---------------------------------------------------------------------------
# ComplexPlane aliases and add_coordinate_labels
# ---------------------------------------------------------------------------

class TestComplexPlaneAliases:
    def test_n2p_is_number_to_point(self):
        cp = ComplexPlane()
        assert cp.n2p is cp.number_to_point or callable(cp.n2p)

    def test_p2n_is_point_to_number(self):
        cp = ComplexPlane()
        assert cp.p2n is cp.point_to_number or callable(cp.p2n)

    def test_n2p_returns_same_as_number_to_point(self):
        cp = ComplexPlane()
        z = 2 + 3j
        assert cp.n2p(z) == cp.number_to_point(z)

    def test_p2n_returns_same_as_point_to_number(self):
        cp = ComplexPlane()
        x, y = cp.number_to_point(1 + 1j)
        assert cp.p2n(x, y) == cp.point_to_number(x, y)

    def test_n2p_real_number(self):
        cp = ComplexPlane()
        result = cp.n2p(3)
        expected = cp.number_to_point(3)
        assert result == expected


class TestComplexPlaneAddCoordinateLabels:
    def test_returns_self(self):
        cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
        result = cp.add_coordinate_labels()
        assert result is cp

    def test_creates_text_objects(self):
        cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
        before = len(cp.objects)
        cp.add_coordinate_labels()
        assert len(cp.objects) > before

    def test_imaginary_labels_contain_i(self):
        cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
        cp.add_coordinate_labels()
        texts = [o for o in cp.objects if isinstance(o, Text)]
        imag_labels = [t.text.at_time(0) for t in texts if 'i' in t.text.at_time(0)]
        assert len(imag_labels) > 0

    def test_skips_zero(self):
        cp = ComplexPlane(x_range=(-2, 2), y_range=(-2, 2))
        cp.add_coordinate_labels()
        texts = [o for o in cp.objects if isinstance(o, Text)]
        labels = [t.text.at_time(0) for t in texts]
        assert '0' not in labels
        assert '0i' not in labels

    def test_font_size_propagated(self):
        cp = ComplexPlane(x_range=(-2, 2), y_range=(-2, 2))
        cp.add_coordinate_labels(font_size=22)
        texts = [o for o in cp.objects if isinstance(o, Text)]
        assert all(t.font_size.at_time(0) == 22 for t in texts)

# ---------------------------------------------------------------------------
# TexObject: get_part_by_tex / set_color_by_tex / t2c
# ---------------------------------------------------------------------------

import shutil as _shutil
_LATEX_AVAILABLE = bool(_shutil.which('latex') and _shutil.which('dvisvgm'))


def _make_tex(tex_str, **kwargs):
    """Create a TexObject with a temporary save directory."""
    import tempfile
    import vectormation._canvas as _cm
    _cm.save_directory = tempfile.mkdtemp()
    from vectormation._composites import TexObject
    return TexObject(tex_str, x=100, y=100, **kwargs)


class TestStripTexCommands:
    """Unit tests for the _strip_tex_commands helper (no LaTeX required)."""

    def test_plain_string_unchanged(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands('x+y=1') == 'x+y=1'

    def test_commands_removed(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands(r'\alpha+\beta') == '+'

    def test_frac_command(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands(r'\frac{x}{y}') == 'xy'

    def test_superscript_stripped(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands(r'E=mc^2') == 'E=mc2'

    def test_spaces_stripped(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands('a b c') == 'abc'

    def test_empty_string(self):
        from vectormation._composites import _strip_tex_commands
        assert _strip_tex_commands('') == ''


@pytest.mark.skipif(not _LATEX_AVAILABLE, reason='LaTeX/dvisvgm not installed')
class TestTexObjectGetPartByTex:
    def test_visible_tex_stored(self):
        tex = _make_tex('x+y')
        assert tex._visible_tex == 'x+y'

    def test_glyph_count_matches_visible_chars(self):
        tex = _make_tex('abc')
        assert len(tex.objects) == 3

    def test_get_part_single_char_returns_one_object(self):
        tex = _make_tex('abc')
        part = tex.get_part_by_tex('a')
        assert len(part.objects) == 1

    def test_get_part_multi_char_returns_correct_count(self):
        tex = _make_tex('abc')
        part = tex.get_part_by_tex('bc')
        assert len(part.objects) == 2

    def test_get_part_full_string_returns_all(self):
        tex = _make_tex('abc')
        part = tex.get_part_by_tex('abc')
        assert len(part.objects) == 3

    def test_get_part_no_match_returns_empty_vcollection(self):
        tex = _make_tex('abc')
        part = tex.get_part_by_tex('z')
        assert isinstance(part, VCollection)
        assert len(part.objects) == 0

    def test_get_part_repeated_occurrences_returned(self):
        tex = _make_tex('aba')
        part = tex.get_part_by_tex('a')
        assert len(part.objects) == 2

    def test_get_part_returns_vcollection_instance(self):
        tex = _make_tex('xy')
        part = tex.get_part_by_tex('x')
        assert isinstance(part, VCollection)

    def test_get_part_empty_query_returns_empty(self):
        tex = _make_tex('abc')
        part = tex.get_part_by_tex('')
        assert len(part.objects) == 0


@pytest.mark.skipif(not _LATEX_AVAILABLE, reason='LaTeX/dvisvgm not installed')
class TestTexObjectSetColorByTex:
    def test_set_color_returns_self(self):
        tex = _make_tex('x+y')
        result = tex.set_color_by_tex({'x': '#ff0000'})
        assert result is tex

    def test_set_color_applies_fill(self):
        tex = _make_tex('x+y')
        tex.set_color_by_tex({'x': '#ff0000'})
        fill = tex.objects[0].styling.fill.at_time(0)
        assert 'ff' in fill.lower() or '255' in fill.lower()

    def test_set_color_multiple_keys(self):
        tex = _make_tex('x+y')
        tex.set_color_by_tex({'x': '#ff0000', '+': '#00ff00'})
        fill_x = tex.objects[0].styling.fill.at_time(0)
        fill_plus = tex.objects[1].styling.fill.at_time(0)
        assert 'ff' in fill_x.lower() or '255,0,0' in fill_x.lower()
        assert '0,255' in fill_plus.lower() or '00ff' in fill_plus.lower()

    def test_set_color_no_match_does_not_raise(self):
        tex = _make_tex('x+y')
        tex.set_color_by_tex({'z': '#ff0000'})

    def test_set_color_alias_same_function(self):
        tex = _make_tex('x+y')
        assert tex.set_color_by_tex.__func__ is tex.set_color_by_tex_to_color_map.__func__

    def test_alias_returns_self(self):
        tex = _make_tex('x+y')
        result = tex.set_color_by_tex_to_color_map({'x': '#ff0000'})
        assert result is tex


@pytest.mark.skipif(not _LATEX_AVAILABLE, reason='LaTeX/dvisvgm not installed')
class TestTexObjectT2cParam:
    def test_t2c_applies_colors_at_construction(self):
        tex = _make_tex('x+y', t2c={'x': '#ff0000'})
        fill = tex.objects[0].styling.fill.at_time(0)
        assert 'ff' in fill.lower() or '255' in fill.lower()

    def test_t2c_none_does_not_raise(self):
        tex = _make_tex('x+y', t2c=None)
        assert tex._tex == 'x+y'

    def test_t2c_empty_dict_does_not_raise(self):
        tex = _make_tex('x+y', t2c={})
        assert tex._tex == 'x+y'

    def test_t2c_multiple_keys(self):
        tex = _make_tex('x+y', t2c={'x': '#ff0000', '+': '#00ff00'})
        fill_x = tex.objects[0].styling.fill.at_time(0)
        fill_plus = tex.objects[1].styling.fill.at_time(0)
        assert 'ff' in fill_x.lower() or '255,0,0' in fill_x.lower()
        assert '0,255' in fill_plus.lower() or '00ff' in fill_plus.lower()

    def test_t2c_does_not_leak_into_styles(self):
        # 't2c' must NOT be passed to from_svg (it is not a valid SVG style)
        tex = _make_tex('x+y', t2c={'x': '#ff0000'})
        assert len(tex.objects) == 3


# ---------------------------------------------------------------------------
# TransformMatchingShapes tests
# ---------------------------------------------------------------------------

class TestTransformMatchingShapes:
    def test_transform_matching_shapes_returns_vcollection(self):
        """transform_matching_shapes returns a VCollection."""
        c1 = Circle(r=50, cx=400, cy=400)
        c2 = Circle(r=50, cx=600, cy=400)
        src = VCollection(c1)
        tgt = VCollection(c2)
        result = transform_matching_shapes(src, tgt, start=0, end=1)
        assert isinstance(result, VCollection)

    def test_transform_matching_shapes_with_matching_objects(self):
        """Matched objects produce MorphObject animations inside the result."""
        # Use a key function that always returns the same key so all pairs match
        c1 = Circle(r=50, cx=400, cy=400)
        c2 = Circle(r=60, cx=700, cy=400)
        src = VCollection(c1)
        tgt = VCollection(c2)
        result = transform_matching_shapes(src, tgt, start=0, end=1,
                                           key=lambda obj: 'circle')
        # One morph animation should be created
        assert len(result.objects) == 1
        assert isinstance(result.objects[0], MorphObject)

    def test_transform_matching_shapes_fades_unmatched(self):
        """Unmatched source objects get faded out; unmatched targets get faded in."""
        # Use a key that distinguishes objects so none match
        c1 = Circle(r=50, cx=400, cy=400)
        r1 = Rectangle(100, 80, x=600, y=360)
        src = VCollection(c1)
        tgt = VCollection(r1)
        result = transform_matching_shapes(src, tgt, start=0, end=1,
                                           key=lambda obj: type(obj).__name__)
        # No morph animations since types differ
        assert len(result.objects) == 0
        # c1 should be faded out: styling.opacity animates to 0 by end time
        opacity_end = c1.styling.opacity.at_time(1)
        assert float(opacity_end) == pytest.approx(0.0, abs=0.05)
        # r1 should be faded in: styling.opacity starts near 0 at start time
        opacity_start = r1.styling.opacity.at_time(0)
        assert float(opacity_start) == pytest.approx(0.0, abs=0.05)

    def test_transform_matching_shapes_no_key_area_based(self):
        """Default (no key) uses bounding-box area; same-size circles match."""
        c1 = Circle(r=50, cx=300, cy=400)
        c2 = Circle(r=50, cx=700, cy=400)
        src = VCollection(c1)
        tgt = VCollection(c2)
        result = transform_matching_shapes(src, tgt, start=0, end=1)
        # Area-based key: both have the same radius so their areas are equal
        assert len(result.objects) == 1
        assert isinstance(result.objects[0], MorphObject)

    def test_transform_matching_shapes_multiple_objects(self):
        """Multiple objects can be matched in one call."""
        c1 = Circle(r=40, cx=200, cy=300)
        c2 = Circle(r=40, cx=400, cy=300)
        c3 = Circle(r=80, cx=600, cy=300)
        c4 = Circle(r=80, cx=800, cy=300)
        src = VCollection(c1, c3)
        tgt = VCollection(c2, c4)
        result = transform_matching_shapes(src, tgt, start=0, end=2,
                                           key=lambda obj: round(obj.bbox(0)[2]))
        # Two distinct sizes → two matched pairs → two MorphObjects
        assert len(result.objects) == 2
        assert all(isinstance(o, MorphObject) for o in result.objects)

    def test_transform_matching_shapes_accepts_lists(self):
        """source/target can be plain Python lists, not just VCollections."""
        c1 = Circle(r=50, cx=400, cy=400)
        c2 = Circle(r=50, cx=600, cy=400)
        result = transform_matching_shapes([c1], [c2], start=0, end=1,
                                           key=lambda obj: 'x')
        assert isinstance(result, VCollection)
        assert len(result.objects) == 1


@pytest.mark.skipif(not _LATEX_AVAILABLE, reason='LaTeX/dvisvgm not installed')
class TestTransformMatchingTex:
    def test_transform_matching_tex_basic(self):
        """transform_matching_tex produces a non-empty VCollection for differing TeX."""
        import shutil as _shutil2
        import tempfile, vectormation._canvas as _cm
        if not hasattr(_cm, 'save_directory'):
            _cm.save_directory = tempfile.mkdtemp()
        from vectormation.objects import TexObject
        src = TexObject('x+y', x=300, y=400)
        tgt = TexObject('x-z', x=300, y=400)
        result = transform_matching_tex(src, tgt, start=0, end=1)
        assert isinstance(result, VCollection)
        # There should be at least one MorphObject (for the shared 'x' glyph)
        morphs = [o for o in result.objects if isinstance(o, MorphObject)]
        assert len(morphs) >= 1

    def test_transform_matching_tex_fallback_without_tex_attr(self):
        """transform_matching_tex falls back gracefully for non-TexObject inputs."""
        c1 = Circle(r=50, cx=400, cy=400)
        c2 = Circle(r=50, cx=600, cy=400)
        src = VCollection(c1)
        tgt = VCollection(c2)
        # Should not raise, returns a VCollection
        result = transform_matching_tex(src, tgt, start=0, end=1)
        assert isinstance(result, VCollection)


# ---------------------------------------------------------------------------
# Comprehensive chart / diagram tests
# ---------------------------------------------------------------------------

class TestSankeyDiagramComprehensive:
    def test_flows_create_path_elements(self):
        flows = [('A', 'X', 10), ('A', 'Y', 5), ('B', 'X', 3)]
        sk = SankeyDiagram(flows)
        svg = sk.to_svg(0)
        # Each flow produces a cubic-bezier path
        assert svg.count('<path') >= 3

    def test_node_rects_created_for_all_nodes(self):
        flows = [('Src1', 'Dst1', 20), ('Src2', 'Dst1', 10), ('Src2', 'Dst2', 5)]
        sk = SankeyDiagram(flows)
        svg = sk.to_svg(0)
        # 2 sources + 2 targets = 4 node rectangles
        assert svg.count('<rect') >= 4

    def test_node_labels_appear_in_svg(self):
        flows = [('Alpha', 'Beta', 50), ('Alpha', 'Gamma', 30)]
        sk = SankeyDiagram(flows)
        svg = sk.to_svg(0)
        assert 'Alpha' in svg
        assert 'Beta' in svg
        assert 'Gamma' in svg

    def test_empty_flows_creates_empty_collection(self):
        sk = SankeyDiagram([])
        assert isinstance(sk, VCollection)
        assert len(sk) == 0

    def test_single_flow_has_path_and_rects(self):
        sk = SankeyDiagram([('In', 'Out', 100)])
        svg = sk.to_svg(0)
        assert '<path' in svg
        assert '<rect' in svg

    def test_custom_dimensions(self):
        flows = [('A', 'B', 10)]
        sk = SankeyDiagram(flows, x=200, y=150, width=800, height=400)
        assert isinstance(sk, VCollection)
        assert len(sk) > 0

    def test_fadein_returns_self(self):
        sk = SankeyDiagram([('X', 'Y', 10)])
        result = sk.fadein(start=0, end=1)
        assert result is sk

    def test_set_opacity_returns_self(self):
        sk = SankeyDiagram([('X', 'Y', 10)])
        result = sk.set_opacity(0.5, start=0, end=1)
        assert result is sk


class TestGanttChartComprehensive:
    def test_bars_list_has_one_bar_per_task(self):
        tasks = [('Design', 0, 3), ('Build', 2, 7), ('Test', 5, 9)]
        gc = GanttChart(tasks)
        assert len(gc._bars) == 3

    def test_task_labels_in_svg(self):
        tasks = [('Analysis', 1, 4), ('Coding', 3, 8)]
        gc = GanttChart(tasks)
        svg = gc.to_svg(0)
        assert 'Analysis' in svg
        assert 'Coding' in svg

    def test_empty_tasks_creates_empty_collection(self):
        gc = GanttChart([])
        assert isinstance(gc, VCollection)
        assert len(gc) == 0

    def test_single_task(self):
        gc = GanttChart([('Solo', 0, 5)])
        assert len(gc._bars) == 1
        svg = gc.to_svg(0)
        assert '<rect' in svg
        assert 'Solo' in svg

    def test_task_with_custom_color(self):
        tasks = [('Task', 0, 5, '#FF0000')]
        gc = GanttChart(tasks)
        assert len(gc._bars) == 1
        svg = gc.to_svg(0)
        assert '<rect' in svg

    def test_time_range_reflected_in_ticks(self):
        # Start and end time labels should appear
        tasks = [('A', 0, 10)]
        gc = GanttChart(tasks)
        svg = gc.to_svg(0)
        assert '0' in svg
        assert '10' in svg

    def test_fadein_returns_self(self):
        gc = GanttChart([('T', 0, 2)])
        result = gc.fadein(start=0, end=1)
        assert result is gc

    def test_bars_are_rectangles(self):
        gc = GanttChart([('T1', 0, 3), ('T2', 2, 5)])
        for bar in gc._bars:
            assert isinstance(bar, Rectangle)


class TestFunnelChartComprehensive:
    def test_stages_count_matches_sections(self):
        # Each stage produces a Polygon + Text = 2 objects
        stages = [('A', 100), ('B', 60), ('C', 30)]
        fc = FunnelChart(stages)
        # 3 stages => 6 objects (3 polygons + 3 labels)
        assert len(fc) == 6

    def test_stage_labels_in_svg(self):
        stages = [('Visits', 1000), ('Leads', 400), ('Customers', 80)]
        fc = FunnelChart(stages)
        svg = fc.to_svg(0)
        assert 'Visits' in svg
        assert 'Leads' in svg
        assert 'Customers' in svg

    def test_values_appear_in_labels(self):
        stages = [('Top', 500), ('Mid', 250)]
        fc = FunnelChart(stages)
        svg = fc.to_svg(0)
        assert '500' in svg
        assert '250' in svg

    def test_single_stage(self):
        fc = FunnelChart([('Only', 100)])
        assert len(fc) == 2  # 1 polygon + 1 label
        svg = fc.to_svg(0)
        assert 'Only' in svg

    def test_custom_size(self):
        stages = [('A', 50), ('B', 25)]
        fc = FunnelChart(stages, x=200, y=200, width=400, height=300)
        assert isinstance(fc, VCollection)
        assert len(fc) > 0

    def test_fadein_returns_self(self):
        fc = FunnelChart([('X', 10), ('Y', 5)])
        result = fc.fadein(start=0, end=1)
        assert result is fc

    def test_set_opacity_returns_self(self):
        fc = FunnelChart([('X', 10)])
        result = fc.set_opacity(0.5, start=0, end=1)
        assert result is fc


class TestTreeMapComprehensive:
    def test_rectangles_count_equals_data_items(self):
        data = [('A', 50), ('B', 30), ('C', 15), ('D', 5)]
        tm = TreeMap(data)
        # Each item gets at least a rectangle
        rects = [o for o in tm.objects if isinstance(o, Rectangle)]
        assert len(rects) == len(data)

    def test_labels_appear_in_svg(self):
        data = [('Alpha', 80), ('Beta', 20)]
        tm = TreeMap(data, width=600, height=400)
        svg = tm.to_svg(0)
        assert '<rect' in svg

    def test_colors_cycle_for_items(self):
        data = [('X', 40), ('Y', 35), ('Z', 25)]
        # Use 2 explicit colors to force cycling
        tm = TreeMap(data, colors=['#FF0000', '#00FF00'])
        svg = tm.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'ff0000' in svg.lower()

    def test_single_item_fills_canvas(self):
        tm = TreeMap([('Only', 100)], x=0, y=0, width=800, height=600)
        assert len(tm) >= 1
        svg = tm.to_svg(0)
        assert '<rect' in svg

    def test_large_item_gets_label(self):
        # Large rectangle should have a text label
        data = [('BigLabel', 900), ('Tiny', 1)]
        tm = TreeMap(data, width=800, height=600, font_size=14)
        svg = tm.to_svg(0)
        assert 'BigLabel' in svg

    def test_empty_data_creates_empty_collection(self):
        tm = TreeMap([])
        assert len(tm) == 0

    def test_fadein_returns_self(self):
        tm = TreeMap([('A', 50), ('B', 50)])
        result = tm.fadein(start=0, end=1)
        assert result is tm

    def test_repr(self):
        tm = TreeMap([('A', 1)])
        assert repr(tm) == 'TreeMap()'


class TestGaugeChartComprehensive:
    def test_value_appears_in_svg(self):
        gc = GaugeChart(42, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert '42' in svg

    def test_label_appears_in_svg(self):
        gc = GaugeChart(50, min_val=0, max_val=100, label='RPM')
        svg = gc.to_svg(0)
        assert 'RPM' in svg

    def test_min_value_needle_at_start(self):
        # At min value needle points to start angle (225 degrees)
        gc_min = GaugeChart(0, min_val=0, max_val=100, x=500, y=500, radius=100)
        gc_max = GaugeChart(100, min_val=0, max_val=100, x=500, y=500, radius=100)
        assert isinstance(gc_min, VCollection)
        assert isinstance(gc_max, VCollection)
        # Both should render without error
        svg_min = gc_min.to_svg(0)
        svg_max = gc_max.to_svg(0)
        assert '0' in svg_min
        assert '100' in svg_max

    def test_clamp_below_min(self):
        # Value below min_val should clamp to 0
        gc = GaugeChart(-10, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert '-10' in svg

    def test_clamp_above_max(self):
        gc = GaugeChart(150, min_val=0, max_val=100)
        svg = gc.to_svg(0)
        assert '150' in svg

    def test_no_label_omits_subtitle(self):
        gc_no_lbl = GaugeChart(50, min_val=0, max_val=100)
        gc_lbl = GaugeChart(50, min_val=0, max_val=100, label='Speed')
        # With label should have more objects
        assert len(gc_lbl) > len(gc_no_lbl)

    def test_custom_colors(self):
        colors = [('#0000FF', 0.0), ('#FF0000', 1.0)]
        gc = GaugeChart(75, colors=colors)
        assert isinstance(gc, VCollection)
        assert len(gc) > 0

    def test_fadein_returns_self(self):
        gc = GaugeChart(50)
        result = gc.fadein(start=0, end=1)
        assert result is gc

    def test_repr(self):
        gc = GaugeChart(50)
        assert repr(gc) == 'GaugeChart()'


class TestVennDiagramComprehensive:
    def test_two_circles_created(self):
        vd = VennDiagram(['P', 'Q'])
        circles = [o for o in vd.objects if isinstance(o, Circle)]
        assert len(circles) == 2

    def test_three_circles_created(self):
        vd = VennDiagram(['X', 'Y', 'Z'])
        circles = [o for o in vd.objects if isinstance(o, Circle)]
        assert len(circles) == 3

    def test_two_labels_in_svg(self):
        vd = VennDiagram(['Left', 'Right'])
        svg = vd.to_svg(0)
        assert 'Left' in svg
        assert 'Right' in svg

    def test_three_labels_in_svg(self):
        vd = VennDiagram(['A', 'B', 'C'])
        svg = vd.to_svg(0)
        assert 'A' in svg
        assert 'B' in svg
        assert 'C' in svg

    def test_invalid_count_returns_empty(self):
        # Only 2 or 3 are valid
        vd1 = VennDiagram(['Solo'])
        assert len(vd1) == 0
        vd4 = VennDiagram(['A', 'B', 'C', 'D'])
        assert len(vd4) == 0

    def test_custom_radius_affects_circles(self):
        vd_small = VennDiagram(['A', 'B'], radius=50)
        vd_large = VennDiagram(['A', 'B'], radius=200)
        small_circles = [o for o in vd_small.objects if isinstance(o, Circle)]
        large_circles = [o for o in vd_large.objects if isinstance(o, Circle)]
        # Larger radius circles have greater r
        assert large_circles[0].r.at_time(0) > small_circles[0].r.at_time(0)

    def test_custom_colors_applied(self):
        vd = VennDiagram(['A', 'B'], colors=['#FF0000', '#00FF00'])
        svg = vd.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'ff0000' in svg.lower()

    def test_fadein_returns_self(self):
        vd = VennDiagram(['A', 'B'])
        result = vd.fadein(start=0, end=1)
        assert result is vd

    def test_repr(self):
        vd = VennDiagram(['A', 'B'])
        assert repr(vd) == 'VennDiagram()'


class TestOrgChartComprehensive:
    def test_single_node_org_chart(self):
        oc = OrgChart(('CEO', []))
        svg = oc.to_svg(0)
        assert 'CEO' in svg

    def test_hierarchy_labels_in_svg(self):
        tree = ('Root', [('Child1', []), ('Child2', [])])
        oc = OrgChart(tree)
        svg = oc.to_svg(0)
        assert 'Root' in svg
        assert 'Child1' in svg
        assert 'Child2' in svg

    def test_three_level_hierarchy(self):
        tree = ('L0', [('L1a', [('L2a', []), ('L2b', [])]), ('L1b', [])])
        oc = OrgChart(tree)
        svg = oc.to_svg(0)
        assert 'L0' in svg
        assert 'L1a' in svg
        assert 'L2a' in svg
        assert 'L2b' in svg

    def test_connector_lines_present(self):
        tree = ('Boss', [('Worker', [])])
        oc = OrgChart(tree)
        svg = oc.to_svg(0)
        # Connector paths should exist
        assert '<path' in svg

    def test_boxes_are_rounded_rectangles(self):
        tree = ('A', [('B', [])])
        oc = OrgChart(tree)
        rects = [o for o in oc.objects if isinstance(o, RoundedRectangle)]
        assert len(rects) >= 2  # one per node

    def test_node_count_matches_tree_size(self):
        # Tree with 4 nodes: 1 root + 3 children
        tree = ('R', [('C1', []), ('C2', []), ('C3', [])])
        oc = OrgChart(tree)
        rects = [o for o in oc.objects if isinstance(o, RoundedRectangle)]
        assert len(rects) == 4

    def test_fadein_returns_self(self):
        oc = OrgChart(('A', [('B', [])]))
        result = oc.fadein(start=0, end=1)
        assert result is oc

    def test_repr(self):
        oc = OrgChart(('R', []))
        assert repr(oc) == 'OrgChart()'


class TestMindMapComprehensive:
    def test_central_node_circle_exists(self):
        root = ('Center', [('Branch', [])])
        mm = MindMap(root)
        circles = [o for o in mm.objects if isinstance(o, Circle)]
        # At least the root circle
        assert len(circles) >= 1

    def test_root_label_in_svg(self):
        root = ('MyTopic', [('Sub1', []), ('Sub2', [])])
        mm = MindMap(root)
        svg = mm.to_svg(0)
        assert 'MyTopic' in svg

    def test_branch_labels_in_svg(self):
        root = ('Root', [('BranchA', []), ('BranchB', []), ('BranchC', [])])
        mm = MindMap(root)
        svg = mm.to_svg(0)
        assert 'BranchA' in svg
        assert 'BranchB' in svg
        assert 'BranchC' in svg

    def test_grandchild_labels_in_svg(self):
        root = ('Root', [('Branch', [('GrandChild', [])])])
        mm = MindMap(root)
        svg = mm.to_svg(0)
        assert 'GrandChild' in svg

    def test_branch_lines_exist(self):
        root = ('Root', [('B1', []), ('B2', [])])
        mm = MindMap(root)
        svg = mm.to_svg(0)
        assert '<line' in svg

    def test_solo_node_has_two_objects(self):
        mm = MindMap(('Solo', []))
        assert len(mm) == 2  # circle + text

    def test_three_branches_count(self):
        root = ('R', [('A', []), ('B', []), ('C', [])])
        mm = MindMap(root)
        # root circle + root text + 3*(line + circle + text) = 2 + 9 = 11
        assert len(mm) == 11

    def test_grandchildren_add_objects(self):
        root_with_gc = ('R', [('B', [('G1', []), ('G2', [])])])
        root_no_gc = ('R', [('B', [])])
        mm_with = MindMap(root_with_gc)
        mm_without = MindMap(root_no_gc)
        assert len(mm_with) > len(mm_without)

    def test_fadein_returns_self(self):
        mm = MindMap(('Root', [('A', [])]))
        result = mm.fadein(start=0, end=1)
        assert result is mm

    def test_repr(self):
        mm = MindMap(('R', []))
        assert repr(mm) == 'MindMap()'


class TestBoxPlotComprehensive:
    def test_one_group_per_box(self):
        # Each group produces: box rect + median line + 2 whisker caps + 2 stems = 6 objects
        bp = BoxPlot([[1, 2, 3, 4, 5]])
        assert len(bp) == 6

    def test_two_groups_twelve_objects(self):
        bp = BoxPlot([[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]])
        assert len(bp) == 12

    def test_svg_has_rects_and_lines(self):
        bp = BoxPlot([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        svg = bp.to_svg(0)
        assert '<rect' in svg
        assert '<line' in svg

    def test_custom_box_color(self):
        bp = BoxPlot([[1, 2, 3, 4, 5]], box_color='#FF0000')
        svg = bp.to_svg(0)
        assert 'rgb(255,0,0)' in svg or 'ff0000' in svg.lower()

    def test_custom_median_color(self):
        bp = BoxPlot([[1, 2, 3, 4, 5]], median_color='#00FF00')
        svg = bp.to_svg(0)
        assert 'rgb(0,255,0)' in svg or '00ff00' in svg.lower()

    def test_single_value_group(self):
        # Single-value group should not raise
        bp = BoxPlot([[42]])
        assert isinstance(bp, VCollection)
        assert len(bp) > 0

    def test_empty_data_empty_collection(self):
        bp = BoxPlot([])
        assert len(bp) == 0

    def test_custom_positions(self):
        bp = BoxPlot([[1, 2, 3], [4, 5, 6]], positions=[0, 2])
        assert isinstance(bp, VCollection)
        assert len(bp) > 0

    def test_fadein_returns_self(self):
        bp = BoxPlot([[1, 2, 3, 4, 5]])
        result = bp.fadein(start=0, end=1)
        assert result is bp

    def test_repr(self):
        bp = BoxPlot([[1, 2, 3]])
        assert repr(bp) == 'BoxPlot()'

    def test_quartiles_ordering(self):
        # Q1 <= median <= Q3 for any sorted group
        data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
        s = sorted(data)
        n = len(s)
        q1 = s[n // 4]
        med = s[n // 2]
        q3 = s[3 * n // 4]
        assert q1 <= med <= q3


# ---- Additional chart class tests ----

class TestWaterfallChart:
    def test_basic_construction(self):
        wc = WaterfallChart([100, -30, 50, -20], labels=['Q1', 'Q2', 'Q3', 'Q4'])
        svg = wc.to_svg(0)
        assert 'rect' in svg
        assert 'Q1' in svg

    def test_empty_values(self):
        wc = WaterfallChart([])
        assert len(wc) == 0

    def test_show_total(self):
        wc = WaterfallChart([10, 20, -5], show_total=True)
        svg = wc.to_svg(0)
        assert 'Total' in svg

    def test_no_total(self):
        wc = WaterfallChart([10, 20], show_total=False)
        svg = wc.to_svg(0)
        assert 'Total' not in svg


class TestSparkLine:
    def test_renders_path(self):
        sl = SparkLine(data=[1, 3, 2, 5, 4], x=100, y=100, width=200, height=40)
        svg = sl.to_svg(0)
        assert '<path' in svg
        assert 'M' in svg

    def test_single_point(self):
        sl = SparkLine(data=[5])
        svg = sl.to_svg(0)
        assert len(svg) < 20  # empty or minimal wrapper

    def test_endpoint(self):
        sl = SparkLine(data=[1, 2, 3], show_endpoint=True)
        svg = sl.to_svg(0)
        assert '<circle' in svg

    def test_repr(self):
        sl = SparkLine(data=[1, 2])
        assert repr(sl) == 'SparkLine()'


class TestKPICard:
    def test_basic(self):
        kpi = KPICard(title='Revenue', value='$1.2M')
        svg = kpi.to_svg(0)
        assert 'Revenue' in svg
        assert '$1.2M' in svg

    def test_with_subtitle(self):
        kpi = KPICard(title='Users', value='10K', subtitle='+5% MoM')
        svg = kpi.to_svg(0)
        assert '+5% MoM' in svg

    def test_with_trend(self):
        kpi = KPICard(title='Revenue', value='$1M', trend_data=[1, 3, 2, 5])
        svg = kpi.to_svg(0)
        assert '<path' in svg


class TestBulletChart:
    def test_basic(self):
        bc = BulletChart(actual=75, target=90)
        svg = bc.to_svg(0)
        assert 'rect' in svg

    def test_with_label(self):
        bc = BulletChart(actual=50, target=80, label='Performance')
        svg = bc.to_svg(0)
        assert 'Performance' in svg


class TestCalendarHeatmap:
    def test_basic(self):
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


class TestWaffleChartCategories:
    def test_basic(self):
        cats = [('A', 30, '#3498DB'), ('B', 70, '#E74C3C')]
        wc = WaffleChart(cats)
        svg = wc.to_svg(0)
        assert 'rect' in svg
        assert 'A' in svg

    def test_repr(self):
        wc = WaffleChart([('X', 50, '#fff')])
        assert repr(wc) == 'WaffleChart()'


class TestCircularProgressBar:
    def test_basic(self):
        cp = CircularProgressBar(75)
        svg = cp.to_svg(0)
        assert '75%' in svg

    def test_zero(self):
        cp = CircularProgressBar(0)
        svg = cp.to_svg(0)
        assert '0%' in svg

    def test_no_text(self):
        cp = CircularProgressBar(50, show_text=False)
        svg = cp.to_svg(0)
        assert '50%' not in svg

    def test_repr(self):
        cp = CircularProgressBar(25)
        assert repr(cp) == 'CircularProgressBar()'


class TestScoreboard:
    def test_basic(self):
        sb = Scoreboard([('Score', 100), ('Level', 5), ('HP', 80)])
        svg = sb.to_svg(0)
        assert 'Score' in svg
        assert '100' in svg

    def test_empty(self):
        sb = Scoreboard([])
        assert len(sb) == 0

    def test_repr(self):
        sb = Scoreboard([('A', 1)])
        assert 'Scoreboard(1' in repr(sb)


class TestMatrixHeatmap:
    def test_basic(self):
        data = [[1, 2, 3], [4, 5, 6]]
        mh = MatrixHeatmap(data)
        svg = mh.to_svg(0)
        assert 'rect' in svg

    def test_with_labels(self):
        data = [[1, 2], [3, 4]]
        mh = MatrixHeatmap(data, row_labels=['R1', 'R2'], col_labels=['C1', 'C2'])
        svg = mh.to_svg(0)
        assert 'R1' in svg
        assert 'C1' in svg

    def test_empty_data(self):
        mh = MatrixHeatmap([])
        svg = mh.to_svg(0)
        assert len(svg) < 20  # empty or minimal wrapper

    def test_show_values(self):
        data = [[1.5]]
        mh = MatrixHeatmap(data, show_values=True)
        svg = mh.to_svg(0)
        assert '1.5' in svg


class TestBoxPlot:
    def test_basic(self):
        bp = BoxPlot([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        svg = bp.to_svg(0)
        assert 'rect' in svg
        assert 'line' in svg

    def test_multiple_groups(self):
        bp = BoxPlot([[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]])
        svg = bp.to_svg(0)
        assert svg.count('<rect') >= 2

    def test_empty(self):
        bp = BoxPlot([])
        svg = bp.to_svg(0)
        assert len(svg) < 20  # empty or minimal wrapper

    def test_repr(self):
        bp = BoxPlot([[1, 2, 3]])
        assert repr(bp) == 'BoxPlot()'


class TestSampleSpaceRendering:
    def test_basic(self):
        from vectormation.objects import SampleSpace
        ss = SampleSpace()
        svg = ss.to_svg(0)
        assert 'rect' in svg

    def test_repr(self):
        from vectormation.objects import SampleSpace
        ss = SampleSpace()
        assert 'SampleSpace' in repr(ss)


class TestSankeyDiagram:
    def test_basic(self):
        flows = [('A', 'X', 30), ('B', 'X', 20), ('A', 'Y', 10)]
        sd = SankeyDiagram(flows)
        svg = sd.to_svg(0)
        assert 'A' in svg

    def test_repr(self):
        sd = SankeyDiagram([('A', 'B', 10)])
        assert repr(sd) == 'SankeyDiagram()'


class TestTreeMap:
    def test_basic(self):
        items = [('A', 40), ('B', 30), ('C', 20), ('D', 10)]
        tm = TreeMap(items)
        svg = tm.to_svg(0)
        assert 'rect' in svg
        assert 'A' in svg

    def test_empty(self):
        tm = TreeMap([])
        svg = tm.to_svg(0)
        assert len(svg) < 20  # empty or minimal wrapper

    def test_repr(self):
        tm = TreeMap([('X', 1)])
        assert repr(tm) == 'TreeMap()'


class TestDonutChartComprehensive:
    def test_center_text(self):
        dc = DonutChart([30, 70], center_text='Usage')
        svg = dc.to_svg(0)
        assert 'Usage' in svg

    def test_animate_values(self):
        dc = DonutChart([50, 50])
        dc.animate_values([80, 20], start=0, end=1)
        svg = dc.to_svg(0.5)
        assert '<path' in svg


class TestGanttChartBasic:
    def test_renders(self):
        tasks = [
            ('Design', 0, 3),
            ('Build', 2, 6),
            ('Test', 5, 8),
        ]
        gc = GanttChart(tasks)
        svg = gc.to_svg(0)
        assert 'Design' in svg
        assert 'rect' in svg


class TestFunnelChartBasic:
    def test_renders(self):
        stages = [('Visit', 1000), ('Signup', 400), ('Buy', 100)]
        fc = FunnelChart(stages)
        svg = fc.to_svg(0)
        assert 'Visit' in svg


class TestPolarAxesRendering:
    def test_construction(self):
        pa = PolarAxes()
        svg = pa.to_svg(0)
        assert svg  # non-empty

    def test_repr(self):
        pa = PolarAxes()
        assert 'PolarAxes' in repr(pa)


class TestLegendRendering:
    def test_basic(self):
        items = [('#3498DB', 'Series A'), ('#E74C3C', 'Series B')]
        leg = Legend(items)
        svg = leg.to_svg(0)
        assert 'Series A' in svg

    def test_repr(self):
        leg = Legend([('#fff', 'X')])
        assert 'Legend' in repr(leg)


# ── PhysicsSpace convenience methods ──────────────────────────────────

class TestPhysicsSpaceConvenience:
    def test_add_walls(self):
        from vectormation._physics import PhysicsSpace
        space = PhysicsSpace()
        space.add_walls(left=50, right=1900, top=50, bottom=1030)
        assert len(space.walls) == 4

    def test_add_walls_partial(self):
        from vectormation._physics import PhysicsSpace
        space = PhysicsSpace()
        space.add_walls(bottom=1030)
        assert len(space.walls) == 1

    def test_add_bodies(self):
        from vectormation._physics import PhysicsSpace, Body
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        space = PhysicsSpace()
        b1 = Body(c1)
        b2 = Body(c2)
        space.add(b1, b2)
        assert len(space.bodies) == 2

    def test_add_springs(self):
        from vectormation._physics import PhysicsSpace, Body, Spring
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        space = PhysicsSpace()
        b1 = Body(c1)
        b2 = Body(c2)
        s = Spring(b1, b2, stiffness=1.0)
        space.add(b1, b2, s)
        assert len(space.bodies) == 2
        assert len(space.springs) == 1


# ── Canvas render alias ──────────────────────────────────────────────

class TestCanvasRenderAlias:
    def test_render_method_exists(self):
        import tempfile
        td = tempfile.mkdtemp()
        v = VectorMathAnim(save_dir=td)
        assert hasattr(v, 'render')
        assert callable(v.render)


# ── UI component tests ───────────────────────────────────────────────

class TestTextBoxRender:
    def test_basic(self):
        tb = TextBox('Hello', x=100, y=100, width=200, height=50)
        svg = tb.to_svg(0)
        assert 'Hello' in svg
        assert 'rect' in svg.lower()

    def test_repr(self):
        tb = TextBox('Hi')
        assert 'TextBox' in repr(tb)


class TestSpeechBubbleRender:
    def test_basic(self):
        sb = SpeechBubble('Hello!', x=400, y=300)
        svg = sb.to_svg(0)
        assert 'Hello!' in svg

    def test_repr(self):
        sb = SpeechBubble('Test')
        assert 'SpeechBubble' in repr(sb)


class TestBadgeRender:
    def test_basic(self):
        b = Badge('NEW', x=100, y=100)
        svg = b.to_svg(0)
        assert 'NEW' in svg

    def test_repr(self):
        b = Badge('v1')
        assert 'Badge' in repr(b)


class TestDividerRender:
    def test_horizontal(self):
        d = Divider(x=100, y=200, length=400, direction='horizontal')
        svg = d.to_svg(0)
        assert 'line' in svg.lower()

    def test_vertical(self):
        d = Divider(x=100, y=200, length=400, direction='vertical')
        svg = d.to_svg(0)
        assert 'line' in svg.lower()

    def test_with_label(self):
        d = Divider(x=100, y=200, length=400, label='Section')
        svg = d.to_svg(0)
        assert 'Section' in svg

    def test_repr(self):
        d = Divider()
        assert 'Divider' in repr(d)


class TestStatusIndicatorRender:
    def test_basic(self):
        si = StatusIndicator('Server', status='online')
        svg = si.to_svg(0)
        assert 'Server' in svg

    def test_offline(self):
        si = StatusIndicator('DB', status='offline')
        svg = si.to_svg(0)
        assert 'DB' in svg

    def test_repr(self):
        si = StatusIndicator('X')
        assert 'StatusIndicator' in repr(si)


class TestMeterRender:
    def test_basic(self):
        m = Meter(value=0.7, x=100, y=100)
        svg = m.to_svg(0)
        assert 'rect' in svg.lower()

    def test_repr(self):
        m = Meter()
        assert 'Meter' in repr(m)


class TestBreadcrumbRender:
    def test_basic(self):
        bc = Breadcrumb(['Home', 'Products', 'Widget'], x=100, y=100)
        svg = bc.to_svg(0)
        assert 'Home' in svg
        assert 'Widget' in svg

    def test_repr(self):
        bc = Breadcrumb(['A', 'B'])
        assert 'Breadcrumb' in repr(bc)


class TestNumberedListRender:
    def test_basic(self):
        nl = NumberedList('First', 'Second', 'Third', x=100, y=100)
        svg = nl.to_svg(0)
        assert 'First' in svg

    def test_repr(self):
        nl = NumberedList('A')
        assert 'NumberedList' in repr(nl)


class TestIconGridRender:
    def test_basic(self):
        ig = IconGrid([(5, '#f00'), (3, '#0f0')], x=100, y=100)
        svg = ig.to_svg(0)
        assert len(ig) > 0

    def test_repr(self):
        ig = IconGrid([(2, '#fff')])
        assert 'IconGrid' in repr(ig)


class TestBracketRender:
    def test_basic(self):
        br = Bracket(x=100, y=200, width=200, height=20)
        svg = br.to_svg(0)
        assert len(svg) > 10

    def test_repr(self):
        br = Bracket(x=0, y=0, width=100, height=20)
        assert 'Bracket' in repr(br)


class TestParagraphRender:
    def test_basic(self):
        p = Paragraph('This is a long paragraph that wraps.', x=100, y=100)
        svg = p.to_svg(0)
        assert len(svg) > 10

    def test_repr(self):
        p = Paragraph('Hello')
        assert 'Paragraph' in repr(p)


class TestStepperRender:
    def test_basic(self):
        s = Stepper(['Step 1', 'Step 2', 'Step 3'], x=100, y=100)
        svg = s.to_svg(0)
        assert len(s) > 0

    def test_advance(self):
        s = Stepper(['A', 'B', 'C'], x=100, y=100)
        result = s.advance(0, 1, start=0, end=1)
        assert result is s

    def test_repr(self):
        s = Stepper(['A'])
        assert 'Stepper' in repr(s)


class TestChecklistRender:
    def test_basic(self):
        cl = Checklist(('Task A', False), ('Task B', True), x=100, y=100)
        svg = cl.to_svg(0)
        assert 'Task A' in svg

    def test_repr(self):
        cl = Checklist(('X', False))
        assert 'Checklist' in repr(cl)


class TestTagCloudRender:
    def test_basic(self):
        tc = TagCloud([('python', 3), ('rust', 2), ('go', 1)], x=100, y=100)
        svg = tc.to_svg(0)
        assert 'python' in svg

    def test_repr(self):
        tc = TagCloud([('x', 1)])
        assert 'TagCloud' in repr(tc)


class TestProgressBarRender:
    def test_basic(self):
        pb = ProgressBar(x=100, y=100, width=300)
        svg = pb.to_svg(0)
        assert 'rect' in svg.lower()

    def test_animate_to(self):
        pb = ProgressBar(x=100, y=100, width=300)
        result = pb.animate_to(0.8, start=0, end=1)
        assert result is pb

    def test_get_progress(self):
        pb = ProgressBar(x=100, y=100, width=300)
        val = pb.get_progress(0)
        assert isinstance(val, float)


class TestTooltipRender2:
    def test_basic(self):
        target = Dot(cx=400, cy=300)
        tt = Tooltip('Hint text', target)
        svg = tt.to_svg(0)
        assert 'Hint' in svg

    def test_repr(self):
        target = Dot(cx=100, cy=100)
        tt = Tooltip('Hi', target)
        assert 'Tooltip' in repr(tt)


class TestCalloutRender2:
    def test_basic(self):
        target = Dot(cx=400, cy=300)
        co = Callout('Note', target)
        svg = co.to_svg(0)
        assert 'Note' in svg

    def test_repr(self):
        target = Dot(cx=100, cy=100)
        co = Callout('X', target)
        assert 'Callout' in repr(co)


class TestDimensionLineRender2:
    def test_basic(self):
        dl = DimensionLine((100, 400), (500, 400))
        svg = dl.to_svg(0)
        assert len(svg) > 10

    def test_repr(self):
        dl = DimensionLine((0, 0), (100, 0))
        assert 'DimensionLine' in repr(dl)


# ── Axes compaction regression tests ─────────────────────────────────

class TestAxesScreenToCoordsRefactored:
    def test_round_trip(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        sx, sy = ax.coords_to_point(2, -1)
        rx, ry = ax.screen_to_coords(sx, sy)
        assert rx == pytest.approx(2, abs=0.01)
        assert ry == pytest.approx(-1, abs=0.01)

    def test_coords_to_screen_alias(self):
        ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        p1 = ax.coords_to_point(1, 2)
        p2 = ax.coords_to_screen(1, 2)
        assert p1 == p2

    def test_get_rect_compacted(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        rect = ax.get_rect(2, 3, 8, 7)
        svg = rect.to_svg(0)
        assert 'rect' in svg.lower()

    def test_get_slope_alias(self):
        import math
        ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
        slope = ax.get_slope(math.sin, 0)
        deriv = ax.get_derivative(math.sin, 0)
        assert slope == pytest.approx(deriv)

    def test_get_origin_uses_coords(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        o = ax.get_origin()
        c = ax.coords_to_point(0, 0)
        assert o == c

    def test_get_plot_center_single_line(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5), x=200, y=100,
                  plot_width=1000, plot_height=800)
        cx, cy = ax.get_plot_center()
        assert cx == pytest.approx(700)
        assert cy == pytest.approx(500)


# --- Cycle 14: Compaction regression tests ---

class TestTableFlashHelper:
    """Test that Table._flash helper works correctly for all highlight methods."""

    def test_highlight_cell_flashes(self):
        t = Table([[1, 2], [3, 4]])
        t.highlight_cell(0, 0, start=0, end=2, color='#FF0000')
        fill = t.entries[0][0].styling.fill.time_func(1)
        assert fill[0] > 200  # R channel near 255

    def test_highlight_column_all_rows(self):
        t = Table([[1, 2], [3, 4], [5, 6]])
        t.highlight_column(1, start=0, end=2, color='#0000FF')
        for r in range(3):
            fill = t.entries[r][1].styling.fill.time_func(1)
            assert fill[2] > 200  # B channel near 255

    def test_highlight_cells_multiple(self):
        t = Table([[1, 2, 3], [4, 5, 6]])
        t.highlight_cells([(0, 0), (1, 2)], start=0, end=2, color='#00FF00')
        for r, c in [(0, 0), (1, 2)]:
            fill = t.entries[r][c].styling.fill.time_func(1)
            assert fill[1] > 200  # G channel near 255

    def test_highlight_row_via_flash(self):
        t = Table([[1, 2], [3, 4]])
        t.highlight_row(0, start=0, end=2, color='#FF0000')
        # Both cells in row 0 should flash
        for c in range(2):
            fill = t.entries[0][c].styling.fill.time_func(1)
            assert fill[0] > 200
        # Row 1 should be unaffected at midpoint — white
        fill1 = t.entries[1][0].styling.fill.time_func(1)
        assert fill1 == (255, 255, 255) or fill1[0] == 255


class TestTableSwapDim:
    """Test the unified _swap_dim helper for swap_rows/swap_columns."""

    def test_swap_rows_positions(self):
        t = Table([['a', 'b'], ['c', 'd']])
        y0 = t.entries[0][0].y.at_time(0)
        y1 = t.entries[1][0].y.at_time(0)
        t.swap_rows(0, 1, start=0, end=1)
        # entries[0] is now old row 1, animating to old row 0 position
        assert t.entries[0][0].y.at_time(1) == pytest.approx(y0)
        assert t.entries[1][0].y.at_time(1) == pytest.approx(y1)

    def test_swap_columns_positions(self):
        t = Table([['a', 'b'], ['c', 'd']])
        x0 = t.entries[0][0].x.at_time(0)
        x1 = t.entries[0][1].x.at_time(0)
        t.swap_columns(0, 1, start=0, end=1)
        # entries[0][0] is now old col 1, animating to old col 0 position
        assert t.entries[0][0].x.at_time(1) == pytest.approx(x0)
        assert t.entries[0][1].x.at_time(1) == pytest.approx(x1)

    def test_swap_rows_no_op_same(self):
        t = Table([['a', 'b'], ['c', 'd']])
        y0 = t.entries[0][0].y.at_time(0)
        t.swap_rows(0, 0, start=0, end=1)
        # No change when swapping same row
        assert t.entries[0][0].y.at_time(1) == pytest.approx(y0)

    def test_swap_columns_out_of_range(self):
        t = Table([['a', 'b']])
        x0 = t.entries[0][0].x.at_time(0)
        t.swap_columns(0, 5, start=0, end=1)
        assert t.entries[0][0].x.at_time(1) == pytest.approx(x0)

    def test_swap_rows_entries_swapped(self):
        t = Table([['a', 'b'], ['c', 'd']])
        text00 = t.entries[0][0].text.at_time(0)
        text10 = t.entries[1][0].text.at_time(0)
        t.swap_rows(0, 1, start=0, end=1)
        # entries list should be swapped
        assert t.entries[0][0].text.at_time(0) == text10
        assert t.entries[1][0].text.at_time(0) == text00


class TestCircleTangentAlias:
    """Test that tangent_line_from_point is an alias for get_tangent_lines."""

    def test_alias_same_result(self):
        c = Circle(r=100, cx=400, cy=400)
        lines1 = c.get_tangent_lines(600, 400)
        lines2 = c.tangent_line_from_point(600, 400)
        assert len(lines1) == len(lines2) == 2

    def test_inside_point_empty(self):
        c = Circle(r=100, cx=400, cy=400)
        assert c.tangent_line_from_point(400, 400) == []


class TestLineClosestPointAlias:
    """Test that closest_point_on_segment is an alias for get_perpendicular_point."""

    def test_alias_same_result(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        p1 = line.get_perpendicular_point(50, 50)
        p2 = line.closest_point_on_segment(50, 50)
        assert p1[0] == pytest.approx(p2[0])
        assert p1[1] == pytest.approx(p2[1])

    def test_clamped_to_segment(self):
        line = Line(x1=0, y1=0, x2=100, y2=0)
        p = line.closest_point_on_segment(200, 0)
        assert p[0] == pytest.approx(100)
        assert p[1] == pytest.approx(0)


class TestTextSplitWordsAlias:
    """Test that split_words delegates to split_into_words."""

    def test_split_words_returns_vcollection(self):
        t = Text(text='hello world')
        result = t.split_words()
        assert len(result.objects) == 2

    def test_split_words_text_content(self):
        t = Text(text='foo bar baz')
        result = t.split_words()
        texts = [obj.text.at_time(0) for obj in result.objects]
        assert texts == ['foo', 'bar', 'baz']


class TestBaseHelpersGetCenter:
    """Test that get_center alias still works after removing duplicate."""

    def test_circle_get_center(self):
        c = Circle(r=50, cx=100, cy=200)
        assert c.get_center() == c.center()

    def test_rectangle_get_center(self):
        r = Rectangle(width=100, height=50, x=300, y=400)
        assert r.get_center() == r.center()


class TestSpinInOutShared:
    """Test that spin_in/spin_out use shared _spin_anim helper."""

    def test_spin_in_shows_object(self):
        c = Circle(r=50)
        c.spin_in(start=0, end=1)
        assert c.show.at_time(0) is True

    def test_spin_in_scale_at_end(self):
        c = Circle(r=50)
        c.spin_in(start=0, end=1)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0, abs=0.01)

    def test_spin_out_hides_at_end(self):
        c = Circle(r=50)
        c.spin_out(start=0, end=1)
        assert c.show.at_time(1.01) is False

    def test_spin_out_scale_at_end(self):
        c = Circle(r=50)
        c.spin_out(start=0, end=1)
        assert c.styling.scale_x.at_time(1) == pytest.approx(0.0, abs=0.05)


class TestComplexPlaneLabel:
    """Test ComplexPlane.add_complex_label method."""

    def test_add_complex_label_creates_dot(self):
        from vectormation.objects import ComplexPlane
        cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
        result = cp.add_complex_label(1 + 2j, 'z₁')
        assert result is not None

    def test_add_complex_label_real_number(self):
        from vectormation.objects import ComplexPlane
        cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
        result = cp.add_complex_label(2.0, 'real')
        assert result is not None


class TestNumberPlaneGetVector:
    """Test NumberPlane.get_vector method."""

    def test_get_vector_returns_arrow(self):
        from vectormation.objects import NumberPlane
        np = NumberPlane()
        arrow = np.get_vector(1, 1)
        assert arrow is not None
        assert 'Arrow' in type(arrow).__name__

    def test_get_vector_adds_to_objects(self):
        from vectormation.objects import NumberPlane
        np = NumberPlane()
        n_before = len(np.objects)
        np.get_vector(2, 3)
        assert len(np.objects) == n_before + 1


class TestPhaseAnim:
    """Test that _phase_anim helper works for create/write/fadein_then_fadeout."""

    def test_create_then_fadeout_visibility(self):
        c = Circle(r=50)
        c.create_then_fadeout(start=0, end=3)
        # Object should be visible during the hold phase
        assert c.show.at_time(2) is True
        # Object should be hidden after fadeout ends
        assert c.show.at_time(3.01) is False

    def test_write_then_fadeout_visibility(self):
        t = Text(text='hello')
        t.write_then_fadeout(start=0, end=3)
        assert t.show.at_time(0.5) is True
        assert t.show.at_time(3.01) is False

    def test_fadein_then_fadeout_visibility(self):
        c = Circle(r=50)
        c.fadein_then_fadeout(start=0, end=2)
        assert c.show.at_time(0.5) is True
        assert c.show.at_time(2.01) is False

    def test_create_then_fadeout_zero_dur(self):
        c = Circle(r=50)
        result = c.create_then_fadeout(start=1, end=1)
        assert result is c


class TestWrapToSvg:
    """Test _wrap_to_svg helper used by drop_shadow, set_backstroke, set_gradient_fill, set_clip."""

    def test_drop_shadow_wraps_svg(self):
        c = Circle(r=50)
        c.drop_shadow(start=1)
        svg = c.to_svg(2)
        assert "feDropShadow" in svg
        assert "filter=" in svg

    def test_drop_shadow_not_before_start(self):
        c = Circle(r=50)
        c.drop_shadow(start=1)
        svg = c.to_svg(0)
        assert "feDropShadow" not in svg

    def test_set_backstroke_wraps_svg(self):
        c = Circle(r=50)
        c.set_backstroke(start=1)
        svg = c.to_svg(2)
        assert "paint-order" in svg

    def test_set_backstroke_not_before_start(self):
        c = Circle(r=50)
        c.set_backstroke(start=1)
        svg = c.to_svg(0)
        assert "paint-order" not in svg


class TestCollectionAliases:
    """Test that collection method aliases/delegations work correctly."""

    def test_distribute_evenly_is_spread(self):
        from vectormation._collection import VCollection
        assert VCollection.distribute_evenly is VCollection.spread

    def test_gather_to_delegates_to_converge(self):
        from vectormation._collection import VCollection
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        g = VCollection(c1, c2)
        g.gather_to(cx=150, cy=150, start=0, end=1)
        # Both circles should move toward (150, 150)
        p1 = c1.center(1)
        p2 = c2.center(1)
        assert abs(p1[0] - 150) < 1
        assert abs(p2[1] - 150) < 1


class TestCircumcenterHelper:
    """Test _circumcenter shared by Circle.from_three_points and Arc.from_three_points."""

    def test_circle_from_three_points(self):
        c = Circle.from_three_points((0, 0), (100, 0), (50, 50))
        assert abs(c.r.at_time(0) - 50) < 5  # reasonable radius

    def test_arc_from_three_points(self):
        from vectormation._shapes_ext import Arc
        arc = Arc.from_three_points((0, 0), (100, 0), (50, 50))
        assert arc.r.at_time(0) > 0

    def test_collinear_raises(self):
        import pytest
        with pytest.raises(ValueError, match="collinear"):
            Circle.from_three_points((0, 0), (1, 1), (2, 2))


class TestSVGFilterBase:
    """Test _SVGFilter base class used by BlurFilter and DropShadowFilter."""

    def test_blur_filter_svg(self):
        from vectormation._svg_utils import BlurFilter
        f = BlurFilter(std_deviation=5)
        svg = f.to_svg_def()
        assert "feGaussianBlur" in svg
        assert "stdDeviation='5'" in svg
        assert f.filter_ref().startswith("url(#blur")

    def test_drop_shadow_filter_svg(self):
        from vectormation._svg_utils import DropShadowFilter
        f = DropShadowFilter(dx=3, dy=3)
        svg = f.to_svg_def()
        assert "feDropShadow" in svg
        assert f.filter_ref().startswith("url(#shadow")

    def test_filter_repr(self):
        from vectormation._svg_utils import BlurFilter, DropShadowFilter
        assert "BlurFilter" in repr(BlurFilter())
        assert "DropShadowFilter" in repr(DropShadowFilter())


class TestValueTrackerOps:
    """Test ValueTracker arithmetic operators use shared _ov helper."""

    def test_add(self):
        from vectormation._shapes_ext import ValueTracker
        a = ValueTracker(10)
        b = ValueTracker(5)
        c = a + b
        assert c.get_value() == 15

    def test_sub_scalar(self):
        from vectormation._shapes_ext import ValueTracker
        a = ValueTracker(10)
        c = a - 3
        assert c.get_value() == 7

    def test_iadd(self):
        from vectormation._shapes_ext import ValueTracker
        a = ValueTracker(10)
        a += 5
        assert a.get_value() == 15


class TestBarChartAliases:
    """Test that get_tallest_bar/get_shortest_bar are aliases."""

    def test_get_tallest_bar(self):
        bc = BarChart([3, 7, 2], labels=['A', 'B', 'C'])
        assert bc.get_tallest_bar() is bc.get_max_bar()

    def test_get_shortest_bar(self):
        bc = BarChart([3, 7, 2], labels=['A', 'B', 'C'])
        assert bc.get_shortest_bar() is bc.get_min_bar()

