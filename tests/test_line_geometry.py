"""Tests for Line geometry methods: intersection, perpendicular, parallel, distance, etc."""
import math
import pytest
from vectormation.objects import Line


class TestSplitAt:
    def test_midpoint(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        a, b = l.split_at(0.5)
        assert a.get_end() == pytest.approx((50, 0))
        assert b.get_start() == pytest.approx((50, 0))

    def test_at_start(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        a, b = l.split_at(0.0)
        assert a.get_start() == pytest.approx(a.get_end())

    def test_at_end(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        a, b = l.split_at(1.0)
        assert b.get_start() == pytest.approx(b.get_end())

    def test_diagonal(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        a, b = l.split_at(0.25)
        assert a.get_end() == pytest.approx((25, 25))
        assert b.get_start() == pytest.approx((25, 25))
        assert b.get_end() == pytest.approx((100, 100))


class TestIsParallel:
    def test_same_direction(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=50, x2=200, y2=50)
        assert a.is_parallel(b)

    def test_opposite_direction(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=200, y1=50, x2=0, y2=50)
        assert a.is_parallel(b)

    def test_not_parallel(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=0, x2=100, y2=100)
        assert not a.is_parallel(b)

    def test_diagonal_parallel(self):
        a = Line(x1=0, y1=0, x2=100, y2=100)
        b = Line(x1=50, y1=0, x2=150, y2=100)
        assert a.is_parallel(b)


class TestIsPerpendicular:
    def test_axes(self):
        h = Line(x1=0, y1=0, x2=100, y2=0)
        v = Line(x1=50, y1=-50, x2=50, y2=50)
        assert h.is_perpendicular(v)

    def test_diagonal(self):
        a = Line(x1=0, y1=0, x2=100, y2=100)
        b = Line(x1=0, y1=100, x2=100, y2=0)
        assert a.is_perpendicular(b)

    def test_not_perpendicular(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=0, x2=100, y2=50)
        assert not a.is_perpendicular(b)


class TestDistanceToPoint:
    def test_point_on_line(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.distance_to_point(50, 0) == pytest.approx(0)

    def test_point_above(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.distance_to_point(50, 30) == pytest.approx(30)

    def test_point_past_endpoint(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        # Distance to nearest endpoint (100, 0) = 50
        assert l.distance_to_point(150, 0) == pytest.approx(50)


class TestContainsPoint:
    def test_on_line(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 0)

    def test_near_line(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.contains_point(50, 1, tol=2)

    def test_far_from_line(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert not l.contains_point(50, 10, tol=2)


class TestIntersectLine:
    def test_crossing(self):
        a = Line(x1=0, y1=0, x2=100, y2=100)
        b = Line(x1=0, y1=100, x2=100, y2=0)
        pt = a.intersect_line(b)
        assert pt is not None
        assert pt == pytest.approx((50, 50))

    def test_parallel_returns_none(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=50, x2=100, y2=50)
        assert a.intersect_line(b) is None

    def test_extended_intersection(self):
        # Lines don't overlap as segments but do as infinite lines
        a = Line(x1=0, y1=0, x2=50, y2=0)
        b = Line(x1=100, y1=-50, x2=100, y2=50)
        pt = a.intersect_line(b)
        assert pt is not None
        assert pt == pytest.approx((100, 0))


class TestIntersectSegment:
    def test_crossing_segments(self):
        a = Line(x1=0, y1=0, x2=100, y2=100)
        b = Line(x1=0, y1=100, x2=100, y2=0)
        pt = a.intersect_segment(b)
        assert pt is not None
        assert pt == pytest.approx((50, 50))

    def test_non_overlapping_segments(self):
        a = Line(x1=0, y1=0, x2=50, y2=0)
        b = Line(x1=100, y1=-50, x2=100, y2=50)
        assert a.intersect_segment(b) is None

    def test_t_shaped(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=50, y1=-50, x2=50, y2=50)
        pt = a.intersect_segment(b)
        assert pt is not None
        assert pt == pytest.approx((50, 0))


class TestPerpendicular:
    def test_midpoint_perpendicular(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        p = l.perpendicular(at_proportion=0.5)
        assert isinstance(p, Line)
        # Perpendicular to horizontal is vertical
        assert p.is_perpendicular(l)

    def test_custom_length(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        p = l.perpendicular(length=200)
        assert p.get_length() == pytest.approx(200)


class TestParallel:
    def test_offset_line(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        p = l.parallel(offset=50)
        assert isinstance(p, Line)
        assert p.is_parallel(l)
        # Offset should be 50 units away
        start = p.get_start()
        assert abs(start[1]) == pytest.approx(50)

    def test_parallel_through_point(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        p = l.parallel_through((50, 100))
        assert isinstance(p, Line)
        assert p.is_parallel(l)


class TestParameterAt:
    def test_start(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.parameter_at(0, 0) == pytest.approx(0)

    def test_end(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.parameter_at(100, 0) == pytest.approx(1)

    def test_midpoint(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.parameter_at(50, 0) == pytest.approx(0.5)

    def test_beyond(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.parameter_at(200, 0) == pytest.approx(2.0)


class TestBisector:
    def test_horizontal_bisector(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        b = l.bisector()
        assert isinstance(b, Line)
        # Bisector should be perpendicular
        assert b.is_perpendicular(l)
        # Should pass through midpoint
        mid = l.get_midpoint()
        assert b.contains_point(mid[0], mid[1], tol=1)


class TestGetSlope:
    def test_horizontal(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        assert l.get_slope() == pytest.approx(0)

    def test_vertical(self):
        l = Line(x1=0, y1=0, x2=0, y2=100)
        assert l.get_slope() == math.inf

    def test_diagonal_45(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        assert l.get_slope() == pytest.approx(1)


class TestAngleTo:
    def test_same_direction(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=50, x2=100, y2=50)
        assert a.angle_to(b) == pytest.approx(0, abs=0.01)

    def test_perpendicular(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=0, x2=0, y2=100)
        assert a.angle_to(b) == pytest.approx(90, abs=0.01)

    def test_45_degrees(self):
        a = Line(x1=0, y1=0, x2=100, y2=0)
        b = Line(x1=0, y1=0, x2=100, y2=100)
        assert a.angle_to(b) == pytest.approx(45, abs=0.01)


class TestReflectOver:
    def test_reflect_over_horizontal(self):
        l = Line(x1=10, y1=-30, x2=90, y2=-30)
        axis = Line(x1=0, y1=0, x2=100, y2=0)
        r = l.reflect_over(axis)
        assert r.get_start() == pytest.approx((10, 30))
        assert r.get_end() == pytest.approx((90, 30))


class TestDivide:
    def test_two_segments(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        pts = l.divide(2)
        assert len(pts) == 3
        assert pts[0] == pytest.approx((0, 0))
        assert pts[1] == pytest.approx((50, 0))
        assert pts[2] == pytest.approx((100, 0))

    def test_three_segments(self):
        l = Line(x1=0, y1=0, x2=90, y2=0)
        pts = l.divide(3)
        assert len(pts) == 4
        assert pts[1] == pytest.approx((30, 0))
        assert pts[2] == pytest.approx((60, 0))

    def test_diagonal(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        pts = l.divide(2)
        assert pts[1] == pytest.approx((50, 50))

    def test_n_less_than_one(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        pts = l.divide(0)
        assert len(pts) == 2  # n clamped to 1


class TestSubdivideInto:
    def test_two_segments(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        segs = l.subdivide_into(2)
        assert len(segs) == 2
        assert segs[0].get_start() == pytest.approx((0, 0))
        assert segs[0].get_end() == pytest.approx((50, 0))
        assert segs[1].get_start() == pytest.approx((50, 0))
        assert segs[1].get_end() == pytest.approx((100, 0))

    def test_three_segments(self):
        l = Line(x1=0, y1=0, x2=90, y2=0)
        segs = l.subdivide_into(3)
        assert len(segs) == 3
        assert segs[0].get_end() == pytest.approx((30, 0))
        assert segs[2].get_start() == pytest.approx((60, 0))

    def test_n_less_than_one(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        segs = l.subdivide_into(0)
        assert len(segs) == 1  # n clamped to 1

    def test_returns_line_instances(self):
        l = Line(x1=0, y1=0, x2=100, y2=100)
        segs = l.subdivide_into(4)
        assert all(isinstance(s, Line) for s in segs)


class TestProjectOnto:
    def test_horizontal_onto_diagonal(self):
        h = Line(x1=0, y1=50, x2=100, y2=50)
        diag = Line(x1=0, y1=0, x2=100, y2=100)
        proj = h.project_onto(diag)
        assert isinstance(proj, Line)
        # Projection onto y=x: (0,50)->(25,25), (100,50)->(75,75)
        assert proj.get_start() == pytest.approx((25, 25))
        assert proj.get_end() == pytest.approx((75, 75))

    def test_onto_self(self):
        l = Line(x1=0, y1=0, x2=100, y2=0)
        proj = l.project_onto(l)
        assert proj.get_start() == pytest.approx((0, 0))
        assert proj.get_end() == pytest.approx((100, 0))

    def test_perpendicular_projection(self):
        v = Line(x1=50, y1=0, x2=50, y2=100)
        h = Line(x1=0, y1=0, x2=200, y2=0)
        proj = v.project_onto(h)
        # Vertical line projected onto horizontal collapses to a point
        assert proj.get_start() == pytest.approx((50, 0))
        assert proj.get_end() == pytest.approx((50, 0))
