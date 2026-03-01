"""Tests for direction normalization in Axes methods and untested properties."""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    Axes, Circle, Dot, Rectangle,
    ThreeDAxes, Surface,
    UP, DOWN, LEFT, RIGHT,
)
from vectormation._svg_utils import Angle


# ── Direction normalization in Axes ─────────────────────────────────

def test_get_graph_label_with_tuple_direction():
    """get_graph_label should accept tuple direction constants."""
    ax = Axes(x_range=(0, 5, 1), y_range=(0, 5, 1))
    lbl = ax.get_graph_label(lambda x: x, 'y=x', direction=UP)
    assert lbl is not None

def test_get_graph_label_direction_down():
    ax = Axes(x_range=(0, 5, 1), y_range=(0, 5, 1))
    lbl = ax.get_graph_label(lambda x: x, 'y=x', direction=DOWN)
    assert lbl is not None

def test_add_arrow_annotation_with_tuple_direction():
    """add_arrow_annotation should accept tuple direction constants."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_arrow_annotation(5, 5, 'Point', direction=UP)
    assert col is not None

def test_add_arrow_annotation_direction_left():
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_arrow_annotation(5, 5, 'Point', direction=LEFT)
    assert col is not None

def test_add_labeled_point_with_tuple_direction():
    """add_labeled_point should accept tuple direction constants."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_labeled_point(5, 5, label='P', direction=UP)
    assert col is not None

def test_add_labeled_point_direction_down():
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_labeled_point(5, 5, label='P', direction=DOWN)
    assert col is not None

def test_add_labeled_point_direction_left():
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_labeled_point(5, 5, label='P', direction=LEFT)
    assert col is not None

def test_add_labeled_point_direction_right():
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    col = ax.add_labeled_point(5, 5, label='P', direction=RIGHT)
    assert col is not None


# ── pin_to with tuple direction ─────────────────────────────────────

def test_pin_to_with_tuple_edge():
    """pin_to should accept tuple direction constants like DOWN."""
    r = Rectangle(100, 50, x=100, y=100)
    d = Dot(cx=0, cy=0)
    d.pin_to(r, edge=DOWN)
    # Should not raise; updater should position the dot at bottom edge
    svg = d.to_svg(0)
    assert svg is not None

def test_pin_to_with_tuple_edge_left():
    r = Rectangle(100, 50, x=100, y=100)
    d = Dot(cx=0, cy=0)
    d.pin_to(r, edge=LEFT)
    svg = d.to_svg(0)
    assert svg is not None


# ── get_edge with tuple direction ───────────────────────────────────

def test_get_edge_with_down():
    c = Circle(r=50, cx=100, cy=100)
    ex, ey = c.get_edge(DOWN)
    assert ey == 150  # bottom of circle

def test_get_edge_with_up():
    c = Circle(r=50, cx=100, cy=100)
    ex, ey = c.get_edge(UP)
    assert ey == 50  # top of circle

def test_get_edge_with_left():
    c = Circle(r=50, cx=100, cy=100)
    ex, ey = c.get_edge(LEFT)
    assert ex == 50  # left of circle

def test_get_edge_with_right():
    c = Circle(r=50, cx=100, cy=100)
    ex, ey = c.get_edge(RIGHT)
    assert ex == 150  # right of circle


# ── VObject.last_change property ────────────────────────────────────

def test_vobject_last_change_default():
    """VObject.last_change should be 0 for a freshly created object."""
    c = Circle(r=50, cx=100, cy=100)
    assert c.last_change == 0

def test_vobject_last_change_after_animation():
    """last_change should reflect the latest animation end time."""
    c = Circle(r=50, cx=100, cy=100)
    c.fadein(start=0, end=2)
    assert c.last_change >= 2


# ── Circle.r property ──────────────────────────────────────────────

def test_circle_r_property_get():
    """Circle.r should return the rx attribute."""
    c = Circle(r=75, cx=0, cy=0)
    assert c.r is c.rx

def test_circle_r_property_set():
    """Circle.r setter should set both rx and ry."""
    c = Circle(r=50, cx=0, cy=0)
    from vectormation.attributes import Real
    new_r = Real(0, 100)
    c.r = new_r
    assert c.rx is new_r
    assert c.ry is new_r

def test_circle_r_property_set_numeric():
    c = Circle(r=50, cx=0, cy=0)
    c.r = 80
    assert c.rx.at_time(0) == 80
    assert c.ry.at_time(0) == 80


# ── Angle properties ───────────────────────────────────────────────

def test_angle_start_angle():
    """Angle.start_angle should delegate to the internal arc."""
    a = Angle(vertex=(0, 0), p1=(100, 0), p2=(0, -100))
    assert a.start_angle.at_time(0) == 0  # 0 degrees (along positive x-axis)

def test_angle_end_angle():
    a = Angle(vertex=(0, 0), p1=(100, 0), p2=(0, -100))
    assert a.end_angle.at_time(0) == 90  # 90 degrees (along positive y up)

def test_angle_r_property():
    a = Angle(vertex=(0, 0), p1=(100, 0), p2=(0, -100), radius=50)
    assert a.r.at_time(0) == 50


# ── ThreeDAxes.last_change ─────────────────────────────────────────

def test_threedaxes_last_change():
    ax = ThreeDAxes()
    assert ax.last_change == 0

def test_threedaxes_last_change_after_camera():
    ax = ThreeDAxes()
    ax.set_camera_orientation(start=0, end=3, phi=math.pi/4)
    assert ax.last_change >= 3


# ── Surface.last_change ────────────────────────────────────────────

def test_surface_last_change():
    s = Surface(lambda u, v: (u, v, u + v), u_range=(0, 1), v_range=(0, 1))
    assert s.last_change == 0


# ── _Primitive3D / _Wireframe last_change ──────────────────────────

def test_dot3d_last_change():
    from vectormation._threed import Dot3D
    d = Dot3D(point=(0, 0, 0))
    assert d.last_change == 0

def test_line3d_last_change():
    from vectormation._threed import Line3D
    ln = Line3D(start=(0, 0, 0), end=(1, 1, 1))
    assert ln.last_change == 0


# ── FlowChart direction normalization ──────────────────────────────

def test_flowchart_with_tuple_direction():
    """FlowChart should accept tuple direction constants."""
    from vectormation.objects import FlowChart
    fc = FlowChart(steps=['A', 'B', 'C'], direction=RIGHT)
    assert fc is not None

def test_flowchart_direction_down():
    from vectormation.objects import FlowChart
    fc = FlowChart(steps=['A', 'B'], direction=DOWN)
    assert fc is not None


# ── VCollection.reveal direction normalization ─────────────────────

def test_reveal_with_tuple_direction():
    """VCollection.reveal should accept tuple direction constants."""
    from vectormation.objects import VCollection
    c1 = Circle(r=20, cx=100, cy=100)
    c2 = Circle(r=20, cx=200, cy=200)
    col = VCollection(c1, c2)
    col.reveal(start=0, end=1, direction=LEFT)
    assert col is not None

def test_reveal_with_down_direction():
    from vectormation.objects import VCollection
    c1 = Circle(r=20, cx=100, cy=100)
    c2 = Circle(r=20, cx=200, cy=200)
    col = VCollection(c1, c2)
    col.reveal(start=0, end=1, direction=DOWN)
    assert col is not None


# ── Brace depth validation ─────────────────────────────────────────

def test_brace_zero_depth_raises():
    """Brace(depth=0) should raise ValueError, not ZeroDivisionError."""
    from vectormation.objects import Brace
    import pytest
    r = Rectangle(100, 50, x=100, y=100)
    with pytest.raises(ValueError, match='depth must be positive'):
        Brace(r, depth=0)

def test_brace_negative_depth_raises():
    from vectormation.objects import Brace
    import pytest
    r = Rectangle(100, 50, x=100, y=100)
    with pytest.raises(ValueError, match='depth must be positive'):
        Brace(r, depth=-5)


# ── Graph x_range format ──────────────────────────────────────────

def test_graph_accepts_2tuple_x_range():
    """Graph should accept x_range as (min, max)."""
    from vectormation.objects import Graph
    g = Graph(lambda x: x**2, x_range=(0, 5))
    assert g is not None

def test_graph_accepts_3tuple_x_range():
    """Graph should accept x_range as (min, max, step) like Axes."""
    from vectormation.objects import Graph
    g = Graph(lambda x: x**2, x_range=(0, 5, 1))
    assert g is not None


# ── Rectangle.split direction normalization ──────────────────────

def test_rectangle_split_with_tuple_direction_up():
    """Rectangle.split should accept UP as 'vertical'."""
    r = Rectangle(200, 100, x=100, y=100)
    parts = r.split(direction=UP, count=2)
    assert len(parts.objects) == 2

def test_rectangle_split_with_tuple_direction_left():
    """Rectangle.split should accept LEFT as 'horizontal'."""
    r = Rectangle(200, 100, x=100, y=100)
    parts = r.split(direction=LEFT, count=3)
    assert len(parts.objects) == 3


# ── Axes direction normalization (extended) ──────────────────────

def test_add_shaded_inequality_with_tuple_direction():
    """add_shaded_inequality should accept UP/DOWN tuple direction."""
    ax = Axes(x_range=(0, 5, 1), y_range=(0, 5, 1))
    region = ax.add_shaded_inequality(lambda x: x, direction=DOWN)
    assert region is not None

def test_add_asymptote_with_tuple_direction():
    """add_asymptote should accept tuple direction for vertical/horizontal."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    line = ax.add_asymptote(5, direction=UP)
    assert line is not None

def test_add_threshold_line_with_tuple_direction():
    """add_threshold_line should accept tuple direction."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    line = ax.add_threshold_line(5, direction=LEFT)
    assert line is not None

def test_add_horizontal_label_with_tuple_side():
    """add_horizontal_label should accept LEFT/RIGHT tuple."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    lbl = ax.add_horizontal_label(5, 'label', side=LEFT)
    assert lbl is not None

def test_add_vertical_label_with_tuple_side():
    """add_vertical_label should accept UP/DOWN tuple."""
    ax = Axes(x_range=(0, 10, 1), y_range=(0, 10, 1))
    lbl = ax.add_vertical_label(5, 'label', side=UP)
    assert lbl is not None


# ── NumberLine.add_label with tuple side ─────────────────────────

def test_numberline_add_label_with_tuple_side():
    """NumberLine.add_label should accept UP tuple for 'above'."""
    from vectormation.objects import NumberLine
    nl = NumberLine(x_range=(-5, 5, 1))
    nl.add_label(0, 'zero', side=UP)
    assert nl is not None


# ── Legend with tuple direction ──────────────────────────────────

def test_legend_with_tuple_direction():
    """Legend should accept tuple direction constants."""
    from vectormation.objects import Legend
    lg = Legend([('#f00', 'Red'), ('#0f0', 'Green')], direction=RIGHT)
    assert lg is not None

def test_legend_with_tuple_direction_down():
    from vectormation.objects import Legend
    lg = Legend([('#f00', 'Red'), ('#0f0', 'Green')], direction=DOWN)
    assert lg is not None


# ── UI direction normalization ───────────────────────────────────

def test_bracket_with_tuple_direction():
    """Bracket should accept tuple direction constants."""
    from vectormation.objects import Bracket
    b = Bracket(direction=DOWN)
    assert b is not None

def test_bracket_with_tuple_direction_left():
    from vectormation.objects import Bracket
    b = Bracket(direction=LEFT)
    assert b is not None

def test_divider_with_tuple_direction():
    """Divider should accept tuple direction constants."""
    from vectormation.objects import Divider
    d = Divider(direction=UP)
    assert d is not None

def test_meter_with_tuple_direction():
    """Meter should accept tuple direction constants."""
    from vectormation.objects import Meter
    m = Meter(direction=LEFT)
    assert m is not None


# ── Input validation ─────────────────────────────────────────────

def test_table_empty_data_raises():
    """Table with empty data should raise ValueError."""
    from vectormation.objects import Table
    import pytest
    with pytest.raises(ValueError, match="non-empty data"):
        Table([])

def test_table_ragged_rows_raises():
    """Table with ragged rows should raise ValueError."""
    from vectormation.objects import Table
    import pytest
    with pytest.raises(ValueError, match="same number of columns"):
        Table([['a', 'b'], ['c']])

def test_annulus_inner_ge_outer_raises():
    """Annulus with inner_radius >= outer_radius should raise ValueError."""
    from vectormation.objects import Annulus
    import pytest
    with pytest.raises(ValueError, match="inner_radius.*outer_radius"):
        Annulus(inner_radius=100, outer_radius=50)

def test_annulus_negative_inner_raises():
    """Annulus with negative inner_radius should raise ValueError."""
    from vectormation.objects import Annulus
    import pytest
    with pytest.raises(ValueError, match="inner_radius must be >= 0"):
        Annulus(inner_radius=-10, outer_radius=50)

def test_annulus_zero_outer_raises():
    """Annulus with outer_radius=0 should raise ValueError."""
    from vectormation.objects import Annulus
    import pytest
    with pytest.raises(ValueError, match="outer_radius must be > 0"):
        Annulus(inner_radius=0, outer_radius=0)

def test_annulus_valid_creation():
    """Valid Annulus should create successfully."""
    from vectormation.objects import Annulus
    a = Annulus(inner_radius=30, outer_radius=60)
    assert a is not None
