"""Tests for vector math utility functions in _constants.py."""
import pytest
from vectormation.objects import (
    dot_product, cross_product_2d, angle_between_vectors,
    rotate_vector, midpoint, interpolate_value, smooth_index,
)


class TestDotProduct:
    def test_perpendicular(self):
        assert dot_product((1, 0), (0, 1)) == 0

    def test_parallel(self):
        assert dot_product((3, 0), (5, 0)) == 15

    def test_antiparallel(self):
        assert dot_product((1, 0), (-1, 0)) == -1

    def test_general(self):
        assert dot_product((2, 3), (4, -1)) == 5

    def test_zero_vector(self):
        assert dot_product((0, 0), (5, 3)) == 0


class TestCrossProduct2D:
    def test_perpendicular(self):
        assert cross_product_2d((1, 0), (0, 1)) == 1

    def test_parallel(self):
        assert cross_product_2d((2, 0), (3, 0)) == 0

    def test_antiparallel(self):
        assert cross_product_2d((1, 0), (-1, 0)) == 0

    def test_general(self):
        assert cross_product_2d((2, 3), (4, -1)) == -14

    def test_opposite_order(self):
        # Cross product is antisymmetric
        assert cross_product_2d((0, 1), (1, 0)) == -1


class TestAngleBetweenVectors:
    def test_same_direction(self):
        assert angle_between_vectors((1, 0), (2, 0)) == pytest.approx(0, abs=1e-10)

    def test_perpendicular(self):
        assert angle_between_vectors((1, 0), (0, 1)) == pytest.approx(90)

    def test_opposite(self):
        assert angle_between_vectors((1, 0), (-1, 0)) == pytest.approx(180)

    def test_45_degrees(self):
        assert angle_between_vectors((1, 0), (1, 1)) == pytest.approx(45, abs=0.01)

    def test_zero_vector(self):
        assert angle_between_vectors((0, 0), (1, 0)) == 0.0

    def test_both_zero(self):
        assert angle_between_vectors((0, 0), (0, 0)) == 0.0


class TestRotateVector:
    def test_90_degrees(self):
        result = rotate_vector((1, 0), 90)
        assert result[0] == pytest.approx(0, abs=1e-10)
        assert result[1] == pytest.approx(1, abs=1e-10)

    def test_180_degrees(self):
        result = rotate_vector((1, 0), 180)
        assert result[0] == pytest.approx(-1, abs=1e-10)
        assert result[1] == pytest.approx(0, abs=1e-10)

    def test_360_degrees(self):
        result = rotate_vector((3, 4), 360)
        assert result[0] == pytest.approx(3, abs=1e-10)
        assert result[1] == pytest.approx(4, abs=1e-10)

    def test_negative_angle(self):
        result = rotate_vector((0, 1), -90)
        assert result[0] == pytest.approx(1, abs=1e-10)
        assert result[1] == pytest.approx(0, abs=1e-10)

    def test_zero_vector(self):
        result = rotate_vector((0, 0), 45)
        assert result == (0, 0)


class TestMidpoint:
    def test_same_point(self):
        assert midpoint((5, 5), (5, 5)) == (5, 5)

    def test_horizontal(self):
        assert midpoint((0, 0), (10, 0)) == (5, 0)

    def test_general(self):
        assert midpoint((2, 4), (6, 8)) == (4, 6)

    def test_negative_coords(self):
        assert midpoint((-2, -4), (2, 4)) == (0, 0)


class TestInterpolateValue:
    def test_start(self):
        assert interpolate_value(0, 10, 0) == 0

    def test_end(self):
        assert interpolate_value(0, 10, 1) == 10

    def test_middle(self):
        assert interpolate_value(0, 10, 0.5) == 5

    def test_negative(self):
        assert interpolate_value(-5, 5, 0.5) == 0


class TestSmoothIndex:
    def test_single_element(self):
        assert smooth_index([42], 0.5) == 42

    def test_two_elements(self):
        assert smooth_index([0, 10], 0.5) == 5

    def test_start(self):
        assert smooth_index([0, 10, 20], 0) == 0

    def test_end(self):
        assert smooth_index([0, 10, 20], 1) == 20

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            smooth_index([], 0.5)

    def test_tuple_values(self):
        result = smooth_index([(0, 0), (10, 20)], 0.5)
        assert result == (5, 10)


class TestCircumcenter:
    def test_equilateral_triangle(self):
        import math as _math
        from vectormation._constants import _circumcenter
        cx, cy, r = _circumcenter((0, 0), (2, 0), (1, _math.sqrt(3)))
        assert cx == pytest.approx(1.0)
        assert cy == pytest.approx(_math.sqrt(3) / 3, abs=1e-6)
        assert r == pytest.approx(2 * _math.sqrt(3) / 3, abs=1e-6)

    def test_right_triangle(self):
        from vectormation._constants import _circumcenter
        cx, cy, r = _circumcenter((0, 0), (4, 0), (0, 3))
        assert cx == pytest.approx(2.0)
        assert cy == pytest.approx(1.5)
        assert r == pytest.approx(2.5)

    def test_collinear_raises(self):
        from vectormation._constants import _circumcenter
        with pytest.raises(ValueError, match="collinear"):
            _circumcenter((0, 0), (1, 1), (2, 2))

    def test_coincident_points_raises(self):
        from vectormation._constants import _circumcenter
        with pytest.raises(ValueError):
            _circumcenter((5, 5), (5, 5), (5, 5))


class TestCircleProperty:
    def test_r_getter(self):
        from vectormation.objects import Circle
        c = Circle(r=50)
        assert c.r is c.rx

    def test_r_setter_with_real(self):
        from vectormation.objects import Circle
        import vectormation.attributes as attributes
        c = Circle(r=50)
        c.r = attributes.Real(0, 100)
        assert c.rx.at_time(0) == 100
        assert c.ry.at_time(0) == 100

    def test_r_setter_with_number(self):
        from vectormation.objects import Circle
        c = Circle(r=50)
        c.r = 100
        assert c.rx.at_time(0) == 100
        assert c.ry.at_time(0) == 100
        # Still has at_time method (didn't replace attribute with int)
        assert hasattr(c.rx, 'at_time')


class TestDecimalNumberTracker:
    def test_tracker_property(self):
        from vectormation.objects import DecimalNumber
        d = DecimalNumber(3.14)
        assert d.tracker is d._tracker
        assert d.tracker.at_time(0) == pytest.approx(3.14)


class TestParagraphLines:
    def test_lines_getter(self):
        from vectormation.objects import Paragraph
        p = Paragraph("Line 1", "Line 2", "Line 3")
        assert p.lines == ["Line 1", "Line 2", "Line 3"]

    def test_lines_setter(self):
        from vectormation.objects import Paragraph
        p = Paragraph("A", "B")
        p.lines = ["X", "Y", "Z"]
        assert len(p.lines) == 3
        assert p.lines[0] == "X"


class TestGetZ:
    def test_default_z(self):
        from vectormation.objects import Circle
        c = Circle(r=50)
        assert c.get_z() == 0

    def test_custom_z(self):
        from vectormation.objects import Rectangle
        r = Rectangle(100, 100, z=5)
        assert r.get_z() == 5

    def test_z_after_set(self):
        from vectormation.objects import Circle
        c = Circle(r=50)
        c.set_z(10, start=1)
        assert c.get_z(time=2) == 10


class TestLastChangeProperty:
    def test_no_changes(self):
        from vectormation.objects import Circle
        c = Circle(r=50, creation=0)
        assert c.last_change >= 0

    def test_after_shift(self):
        from vectormation.objects import Circle
        c = Circle(r=50, creation=0)
        c.shift(dx=10, start=2, end=3)
        assert c.last_change >= 3

    def test_after_color_change(self):
        from vectormation.objects import Rectangle
        r = Rectangle(100, 100, creation=0)
        r.set_color(5, 6, fill='#FF0000')
        assert r.last_change >= 5
