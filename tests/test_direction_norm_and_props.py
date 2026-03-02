"""Tests for direction normalization in Axes methods and untested properties."""
import math
import sys, os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    Circle, Rectangle,
    ThreeDAxes,
    UP, DOWN, LEFT, RIGHT,
)
from vectormation._svg_utils import Angle


# ── get_edge with tuple direction (actual coordinate checks) ─────────

def test_get_edge_with_down():
    c = Circle(r=50, cx=100, cy=100)
    _, ey = c.get_edge(DOWN)
    assert ey == 150  # bottom of circle

def test_get_edge_with_up():
    c = Circle(r=50, cx=100, cy=100)
    _, ey = c.get_edge(UP)
    assert ey == 50  # top of circle

def test_get_edge_with_left():
    c = Circle(r=50, cx=100, cy=100)
    ex, _ = c.get_edge(LEFT)
    assert ex == 50  # left of circle

def test_get_edge_with_right():
    c = Circle(r=50, cx=100, cy=100)
    ex, _ = c.get_edge(RIGHT)
    assert ex == 150  # right of circle


# ── VObject.last_change property ────────────────────────────────────

def test_vobject_last_change_after_animation():
    """last_change should reflect the latest animation end time."""
    c = Circle(r=50, cx=100, cy=100)
    c.fadein(start=0, end=2)
    assert c.last_change >= 2


# ── Circle.r property ──────────────────────────────────────────────

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

def test_threedaxes_last_change_after_camera():
    ax = ThreeDAxes()
    ax.set_camera_orientation(start=0, end=3, phi=math.pi/4)
    assert ax.last_change >= 3


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


# ── Brace depth validation ─────────────────────────────────────────

def test_brace_zero_depth_raises():
    """Brace(depth=0) should raise ValueError, not ZeroDivisionError."""
    from vectormation.objects import Brace
    r = Rectangle(100, 50, x=100, y=100)
    with pytest.raises(ValueError, match='depth must be positive'):
        Brace(r, depth=0)

def test_brace_negative_depth_raises():
    from vectormation.objects import Brace
    r = Rectangle(100, 50, x=100, y=100)
    with pytest.raises(ValueError, match='depth must be positive'):
        Brace(r, depth=-5)


# ── Input validation ─────────────────────────────────────────────

def test_table_empty_data_raises():
    """Table with empty data should raise ValueError."""
    from vectormation.objects import Table
    with pytest.raises(ValueError, match="non-empty data"):
        Table([])

def test_table_ragged_rows_raises():
    """Table with ragged rows should raise ValueError."""
    from vectormation.objects import Table
    with pytest.raises(ValueError, match="same number of columns"):
        Table([['a', 'b'], ['c']])

def test_annulus_inner_ge_outer_raises():
    """Annulus with inner_radius >= outer_radius should raise ValueError."""
    from vectormation.objects import Annulus
    with pytest.raises(ValueError, match="inner_radius.*outer_radius"):
        Annulus(inner_radius=100, outer_radius=50)

def test_annulus_negative_inner_raises():
    """Annulus with negative inner_radius should raise ValueError."""
    from vectormation.objects import Annulus
    with pytest.raises(ValueError, match="inner_radius must be >= 0"):
        Annulus(inner_radius=-10, outer_radius=50)

def test_annulus_zero_outer_raises():
    """Annulus with outer_radius=0 should raise ValueError."""
    from vectormation.objects import Annulus
    with pytest.raises(ValueError, match="outer_radius must be > 0"):
        Annulus(inner_radius=0, outer_radius=0)
