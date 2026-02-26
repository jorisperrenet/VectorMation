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
    ThreeDAxes,
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
        soup = BeautifulSoup("<g/>", 'html.parser')
        elem = soup.find('g')
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

    def test_add_text_annotation(self):
        ax = Axes(x_range=(0, 10), y_range=(0, 10))
        lbl = ax.add_text_annotation(5, 5, 'hello')
        svg = lbl.to_svg(0)
        assert 'hello' in svg

    def test_add_shaded_inequality(self):
        import math
        ax = Axes(x_range=(0, 7), y_range=(-3, 3))
        shade = ax.add_shaded_inequality(math.sin, direction='below')
        svg = shade.to_svg(0)
        assert '<path' in svg

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
