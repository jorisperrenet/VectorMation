"""Tests for previously untested Arrow methods: grow, get_midpoint, get_length, CurvedArrow."""
from vectormation.objects import Arrow, DoubleArrow, CurvedArrow


class TestArrowGrow:
    def test_basic(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.grow(start=0, end=2)
        svg = a.to_svg(1)
        assert svg is not None

    def test_at_start(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.grow(start=0, end=1)
        svg = a.to_svg(0)
        assert svg is not None

    def test_at_end(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.grow(start=0, end=1)
        svg = a.to_svg(1)
        assert svg is not None

    def test_zero_duration(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        result = a.grow(start=1, end=1)
        assert result is a

    def test_no_change_existence(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.grow(start=0, end=1, change_existence=False)
        svg = a.to_svg(0.5)
        assert svg is not None

    def test_double_arrow_grow(self):
        a = DoubleArrow(x1=100, y1=100, x2=500, y2=500)
        a.grow(start=0, end=1)
        svg = a.to_svg(0.5)
        assert svg is not None


class TestArrowGetMidpoint:
    def test_horizontal(self):
        a = Arrow(x1=100, y1=200, x2=500, y2=200)
        mx, my = a.get_midpoint()
        assert abs(mx - 300) < 1
        assert abs(my - 200) < 1

    def test_diagonal(self):
        a = Arrow(x1=0, y1=0, x2=200, y2=200)
        mx, my = a.get_midpoint()
        assert abs(mx - 100) < 1
        assert abs(my - 100) < 1

    def test_vertical(self):
        a = Arrow(x1=300, y1=100, x2=300, y2=500)
        mx, my = a.get_midpoint()
        assert abs(mx - 300) < 1
        assert abs(my - 300) < 1


class TestArrowGetLength:
    def test_horizontal(self):
        a = Arrow(x1=100, y1=200, x2=500, y2=200)
        length = a.get_length()
        assert abs(length - 400) < 1

    def test_diagonal(self):
        a = Arrow(x1=0, y1=0, x2=300, y2=400)
        length = a.get_length()
        assert abs(length - 500) < 1

    def test_zero_length(self):
        a = Arrow(x1=100, y1=100, x2=100, y2=100)
        length = a.get_length()
        assert length < 1


class TestCurvedArrow:
    def test_basic(self):
        ca = CurvedArrow(x1=100, y1=100, x2=500, y2=500)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_negative_angle(self):
        ca = CurvedArrow(x1=100, y1=100, x2=500, y2=500, angle=-0.4)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_large_angle(self):
        ca = CurvedArrow(x1=100, y1=100, x2=500, y2=500, angle=1.0)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_custom_styling(self):
        ca = CurvedArrow(x1=100, y1=100, x2=500, y2=300,
                         stroke='#FF0000', stroke_width=3)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_repr(self):
        ca = CurvedArrow(x1=0, y1=0, x2=100, y2=100)
        assert 'CurvedArrow' in repr(ca)

    def test_horizontal(self):
        ca = CurvedArrow(x1=100, y1=300, x2=800, y2=300, angle=0.3)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_vertical(self):
        ca = CurvedArrow(x1=300, y1=100, x2=300, y2=700, angle=0.5)
        svg = ca.to_svg(0)
        assert svg is not None

    def test_custom_tip(self):
        ca = CurvedArrow(x1=0, y1=0, x2=200, y2=200,
                         tip_length=30, tip_width=25)
        svg = ca.to_svg(0)
        assert svg is not None


class TestArrowUpdateTipDynamic:
    def test_set_start_updates_tip(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.set_start(200, 200, start=0)
        svg = a.to_svg(0)
        assert svg is not None

    def test_set_end_updates_tip(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.set_end(600, 300, start=0, end=1)
        svg = a.to_svg(0.5)
        assert svg is not None

    def test_animated_start_and_end(self):
        a = Arrow(x1=100, y1=100, x2=500, y2=500)
        a.set_start(200, 200, start=0, end=1)
        a.set_end(600, 600, start=0, end=1)
        svg = a.to_svg(0.5)
        assert svg is not None
