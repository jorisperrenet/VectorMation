"""Tests for helper functions: lerp, ramp, direction normalization, constants."""
import math
import pytest

from vectormation._base_helpers import (
    _lerp, _ramp, _ramp_down, _lerp_point, _norm_dir, _norm_edge,
    _BBoxMethodsMixin,
)
from vectormation._constants import (
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
    ORIGIN, CANVAS_WIDTH, CANVAS_HEIGHT, UNIT,
    _distance, _rotate_point, _normalize,
)
import vectormation.easings as easings


class TestLerp:

    def test_lerp_endpoints(self):
        fn = _lerp(0, 1, 10, 20, easings.linear)
        assert fn(0) == pytest.approx(10)
        assert fn(1) == pytest.approx(20)

    def test_lerp_midpoint(self):
        fn = _lerp(0, 1, 0, 100, easings.linear)
        assert fn(0.5) == pytest.approx(50)

    def test_lerp_custom_range(self):
        fn = _lerp(2, 3, 0, 100, easings.linear)
        assert fn(2) == pytest.approx(0)
        assert fn(5) == pytest.approx(100)  # t=5: (5-2)/3 = 1

    def test_ramp_from_zero(self):
        fn = _ramp(0, 1, 100, easings.linear)
        assert fn(0) == pytest.approx(0)
        assert fn(1) == pytest.approx(100)

    def test_ramp_down_to_zero(self):
        fn = _ramp_down(0, 1, 100, easings.linear)
        assert fn(0) == pytest.approx(100)
        assert fn(1) == pytest.approx(0)

    def test_lerp_point_2d(self):
        fn = _lerp_point(0, 1, (0, 0), (100, 200), easings.linear)
        assert fn(0) == pytest.approx((0, 0))
        assert fn(0.5) == pytest.approx((50, 100))
        assert fn(1) == pytest.approx((100, 200))


class TestDirectionNorm:

    def test_norm_dir_tuples(self):
        assert _norm_dir(RIGHT) == 'right'
        assert _norm_dir(LEFT) == 'left'
        assert _norm_dir(DOWN) == 'down'
        assert _norm_dir(UP) == 'up'

    def test_norm_dir_strings_passthrough(self):
        assert _norm_dir('right') == 'right'
        assert _norm_dir('down') == 'down'

    def test_norm_edge_tuples(self):
        assert _norm_edge(LEFT) == 'left'
        assert _norm_edge(RIGHT) == 'right'
        assert _norm_edge(UP) == 'top'
        assert _norm_edge(DOWN) == 'bottom'


class TestConstants:

    def test_origin_is_center(self):
        assert ORIGIN == (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
        assert ORIGIN == (960, 540)

    def test_direction_vectors(self):
        assert UP == (0, -1)
        assert DOWN == (0, 1)
        assert LEFT == (-1, 0)
        assert RIGHT == (1, 0)

    def test_unit_value(self):
        assert UNIT == 135  # 1080 / 8


class TestGeometryHelpers:

    def test_distance(self):
        assert _distance(0, 0, 3, 4) == pytest.approx(5)
        assert _distance(0, 0, 0, 0) == pytest.approx(0)

    def test_rotate_point_90_degrees(self):
        # Rotate (1, 0) around (0, 0) by 90° → (0, 1)
        rx, ry = _rotate_point(1, 0, 0, 0, math.pi / 2)
        assert rx == pytest.approx(0, abs=1e-9)
        assert ry == pytest.approx(1, abs=1e-9)

    def test_rotate_point_360_returns_same(self):
        rx, ry = _rotate_point(3, 4, 0, 0, 2 * math.pi)
        assert rx == pytest.approx(3, abs=1e-9)
        assert ry == pytest.approx(4, abs=1e-9)

    def test_rotate_point_around_self(self):
        rx, ry = _rotate_point(5, 5, 5, 5, math.pi)
        assert rx == pytest.approx(5)
        assert ry == pytest.approx(5)

    def test_normalize(self):
        ux, uy = _normalize(3, 4)
        assert math.hypot(ux, uy) == pytest.approx(1)
        assert ux == pytest.approx(0.6)
        assert uy == pytest.approx(0.8)

    def test_normalize_zero_vector(self):
        assert _normalize(0, 0) == (0, 0)
