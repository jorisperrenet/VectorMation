"""Tests for previously untested Arrow methods: get_midpoint, get_length."""
from vectormation.objects import Arrow


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
