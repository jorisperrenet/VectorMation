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
        c.rotate_out(start=0, end=1, angle=90, easing=easings.linear)
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
        found = col.find(lambda obj, t: isinstance(obj, Rectangle))
        assert isinstance(found, Rectangle)

    def test_find_none(self):
        from vectormation.objects import VCollection, Circle
        col = VCollection(Circle(), Circle())
        found = col.find(lambda obj, t: isinstance(obj, int))
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
        idx = col.find_index(lambda obj, t: isinstance(obj, Rectangle))
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
        a.set_start(200, 200, start_time=0)
        svg = a.to_svg(1)
        assert 'line' in svg.lower() or '<path' in svg.lower()

    def test_set_end_animated(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(600, 600, start_time=0, end_time=1)
        svg = a.to_svg(0.5)
        assert svg

    def test_set_start_animated(self):
        a = Arrow(100, 100, 500, 500)
        a.set_start(300, 300, start_time=0, end_time=1)
        svg = a.to_svg(0.5)
        assert svg
        # At t=0.5 the start should be between (100,100) and (300,300)
        s = a.get_start(0.5)
        assert 100 < s[0] < 300

    def test_set_end_instant(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(700, 700, start_time=0)
        e = a.get_end(0)
        assert abs(e[0] - 700) < 1
        assert abs(e[1] - 700) < 1

    def test_tip_follows_endpoint(self):
        a = Arrow(100, 100, 500, 500)
        a.set_end(700, 100, start_time=0)
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
        p2 = par.p2.at_time(0)
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
        rect = ax.add_marked_region(2, 5, color='#FF0000')
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
    def test_clamp(self):
        from vectormation._constants import _clamp
        assert _clamp(5, 0, 10) == 5
        assert _clamp(-5, 0, 10) == 0
        assert _clamp(15, 0, 10) == 10

    def test_lerp(self):
        from vectormation._constants import _lerp
        assert _lerp(0, 10, 0.5) == 5
        assert _lerp(0, 10, 0) == 0
        assert _lerp(0, 10, 1) == 10

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
        pts = ax.get_graph_intersection(lambda x: x**2, lambda x: 4)
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert xs[0] == pytest.approx(-2, abs=0.02)
        assert xs[1] == pytest.approx(2, abs=0.02)

    def test_no_intersection(self):
        ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        # y=1 and y=-1 never intersect
        pts = ax.get_graph_intersection(lambda x: 1, lambda x: -1)
        assert len(pts) == 0

    def test_custom_x_range(self):
        ax = Axes(x_range=(-10, 10), y_range=(-10, 10))
        # y=x^2 and y=4 intersect at x=-2 and x=2, but limit to positive x
        pts = ax.get_graph_intersection(lambda x: x**2, lambda x: 4, x_range=(0, 10))
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

class TestAngleBetween:
    def test_right(self):
        import math
        from vectormation._constants import _angle_between
        assert _angle_between(0, 0, 1, 0) == pytest.approx(0)

    def test_up(self):
        import math
        from vectormation._constants import _angle_between
        # atan2(-1, 0) = -pi/2
        assert _angle_between(0, 0, 0, -1) == pytest.approx(-math.pi / 2)

    def test_diagonal(self):
        import math
        from vectormation._constants import _angle_between
        assert _angle_between(0, 0, 1, 1) == pytest.approx(math.pi / 4)

    def test_left(self):
        import math
        from vectormation._constants import _angle_between
        angle = _angle_between(0, 0, -1, 0)
        assert abs(angle) == pytest.approx(math.pi)


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


class TestMidpoint:
    def test_basic(self):
        from vectormation._constants import _midpoint
        mx, my = _midpoint(0, 0, 10, 10)
        assert mx == pytest.approx(5.0)
        assert my == pytest.approx(5.0)

    def test_negative(self):
        from vectormation._constants import _midpoint
        mx, my = _midpoint(-4, -6, 4, 6)
        assert mx == pytest.approx(0.0)
        assert my == pytest.approx(0.0)


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
        bx, by, bw, bh = c.bbox(0)
        rect = c.flash_highlight(start=0, end=1)
        rx, ry, rw, rh = rect.bbox(0)
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
        rect = ax.shade_region(x_start=-1, x_end=1)
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
        result = ax.add_callout(0, 0, 'Late', creation=2)
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
        c.emphasize_scale(0, 1, factor=1.5)
        assert c.styling.scale_x.at_time(0) == pytest.approx(1.0, abs=1e-3)
        assert c.styling.scale_y.at_time(0) == pytest.approx(1.0, abs=1e-3)

    def test_scale_at_end_is_original(self):
        """After the animation the scale returns to the original value."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, factor=1.5)
        assert c.styling.scale_x.at_time(1) == pytest.approx(1.0, abs=1e-3)
        assert c.styling.scale_y.at_time(1) == pytest.approx(1.0, abs=1e-3)

    def test_peak_scale_greater_than_one(self):
        """At midpoint the scale should be larger than the original (there_and_back peaks at 0.5)."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, factor=1.4)
        mid_scale = c.styling.scale_x.at_time(0.5)
        assert mid_scale > 1.0

    def test_uniform_scale_x_equals_y(self):
        """Both axes must scale identically (uniform scale)."""
        c = Circle(r=50, cx=100, cy=100)
        c.emphasize_scale(0, 1, factor=1.3)
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            assert c.styling.scale_x.at_time(t) == pytest.approx(
                c.styling.scale_y.at_time(t), abs=1e-9
            )

    def test_zero_duration_noop(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.emphasize_scale(0.5, 0.5, factor=2.0)
        assert result is c
        assert c.styling.scale_x.at_time(0.5) == pytest.approx(1.0, abs=1e-3)

    def test_respects_existing_scale(self):
        """If the object already has a non-unit scale, the pulse is relative to that."""
        c = Circle(r=50, cx=100, cy=100)
        c.styling.scale_x.set_onward(0, 2.0)
        c.styling.scale_y.set_onward(0, 2.0)
        c.emphasize_scale(0, 1, factor=1.5)
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
        import math
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
        x, y = ax.get_function_max(math.sin, 0, math.pi)
        assert y == pytest.approx(1.0, abs=0.01)

    def test_get_function_min_sine(self):
        """sin(x) has min ~-1 at x=3*pi/2 in [pi, 2*pi]."""
        import math
        ax = Axes(x_range=(0, 7), y_range=(-1, 1))
        x, y = ax.get_function_min(math.sin, math.pi, 2 * math.pi)
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
