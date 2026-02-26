"""Tests for vectormation.pathbbox: SVG path bounding box computation."""
import pytest
import math
from vectormation.pathbbox import (
    path_bbox, _parse_path, _tokenize,
    _cubic_extrema, _quadratic_extrema,
    _cubic_eval, _quadratic_eval, _arc_bbox,
)


class TestTokenize:
    def test_simple_path(self):
        tokens = list(_tokenize('M 0 0 L 100 100'))
        assert tokens == ['M', 0.0, 0.0, 'L', 100.0, 100.0]

    def test_comma_separated(self):
        tokens = list(_tokenize('M0,0L100,100'))
        assert tokens == ['M', 0.0, 0.0, 'L', 100.0, 100.0]


class TestLineBbox:
    def test_simple_line(self):
        xmin, xmax, ymin, ymax = path_bbox('M 0,0 L 100,100')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(0)
        assert ymax == pytest.approx(100)

    def test_horizontal_line(self):
        xmin, xmax, ymin, ymax = path_bbox('M 0,50 H 100')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(50)
        assert ymax == pytest.approx(50)

    def test_vertical_line(self):
        xmin, xmax, ymin, ymax = path_bbox('M 50,0 V 100')
        assert xmin == pytest.approx(50)
        assert xmax == pytest.approx(50)
        assert ymin == pytest.approx(0)
        assert ymax == pytest.approx(100)


class TestCubicBbox:
    def test_straight_cubic(self):
        # A cubic that is essentially a straight line
        xmin, xmax, ymin, ymax = path_bbox('M 0,0 C 33,0 66,0 100,0')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(0)
        assert ymax == pytest.approx(0)

    def test_curved_cubic(self):
        # A cubic with control points that push above/below
        xmin, xmax, ymin, ymax = path_bbox('M 0,0 C 0,100 100,100 100,0')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(0)
        assert ymax > 50  # Should bulge upward

    def test_cubic_extrema_helper(self):
        # Simple case: linear (no extrema)
        assert _cubic_extrema(0, 33, 66, 100) == []

    def test_cubic_eval_at_endpoints(self):
        assert _cubic_eval(0, 10, 90, 100, 0) == pytest.approx(0)
        assert _cubic_eval(0, 10, 90, 100, 1) == pytest.approx(100)


class TestQuadraticBbox:
    def test_quadratic_curve(self):
        xmin, xmax, ymin, ymax = path_bbox('M 0,0 Q 50,100 100,0')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(0)
        assert ymax == pytest.approx(50)  # Peak of the quadratic

    def test_quadratic_extrema_helper(self):
        ts = _quadratic_extrema(0, 100, 0)
        assert len(ts) == 1
        assert ts[0] == pytest.approx(0.5)

    def test_quadratic_eval_at_endpoints(self):
        assert _quadratic_eval(0, 50, 100, 0) == pytest.approx(0)
        assert _quadratic_eval(0, 50, 100, 1) == pytest.approx(100)


class TestArcBbox:
    def test_semicircle_arc(self):
        # Arc from (100,50) to (100,50+100) with radius 50
        xmin, xmax, ymin, ymax = path_bbox('M 150,100 A 50,50 0 0,1 50,100')
        assert xmin <= 50
        assert xmax >= 150


class TestEmptyPath:
    def test_empty_string(self):
        result = path_bbox('')
        assert result == (0, 0, 0, 0)

    def test_whitespace_only(self):
        result = path_bbox('   ')
        assert result == (0, 0, 0, 0)

    def test_none_like(self):
        result = path_bbox('')
        assert result == (0, 0, 0, 0)


class TestRelativeCommands:
    def test_relative_line(self):
        xmin, xmax, ymin, ymax = path_bbox('M 10,10 l 90,90')
        assert xmin == pytest.approx(10)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(10)
        assert ymax == pytest.approx(100)

    def test_relative_move(self):
        xmin, xmax, ymin, ymax = path_bbox('m 10,10 l 90,0')
        assert xmin == pytest.approx(10)
        assert xmax == pytest.approx(100)

    def test_close_path(self):
        xmin, xmax, ymin, ymax = path_bbox('M 0,0 L 100,0 L 100,100 Z')
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)
        assert ymin == pytest.approx(0)
        assert ymax == pytest.approx(100)
