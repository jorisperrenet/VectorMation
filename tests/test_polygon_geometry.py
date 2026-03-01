"""Tests for Polygon geometry methods: winding number, edges, angles, triangulation, etc."""
import math
import pytest
from vectormation.objects import Polygon, RegularPolygon, VCollection


class TestWindingNumber:
    def test_inside_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.winding_number(50, 50) != 0

    def test_outside_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        assert sq.winding_number(200, 200) == 0

    def test_triangle_inside(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        assert tri.winding_number(50, 30) != 0

    def test_triangle_outside(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        assert tri.winding_number(-50, -50) == 0


class TestGetEdges:
    def test_triangle_edges(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        edges = tri.get_edges()
        assert len(edges) == 3

    def test_square_edges(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        edges = sq.get_edges()
        assert len(edges) == 4

    def test_edges_are_lines(self):
        from vectormation.objects import Line
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        edges = sq.get_edges()
        for e in edges:
            assert isinstance(e, Line)


class TestGetEdgeMidpoints:
    def test_triangle_midpoints(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        mids = tri.get_edge_midpoints()
        assert len(mids) == 3

    def test_square_midpoints(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        mids = sq.get_edge_midpoints()
        assert len(mids) == 4
        # First edge midpoint: (0,0)->(100,0) => (50, 0)
        assert mids[0] == pytest.approx((50, 0))


class TestInteriorAngles:
    def test_equilateral_triangle(self):
        # Build equilateral triangle
        p = RegularPolygon(n=3, radius=100, cx=0, cy=0)
        angles = p.interior_angles()
        for a in angles:
            assert a == pytest.approx(60, abs=1)

    def test_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        angles = sq.interior_angles()
        assert len(angles) == 4
        for a in angles:
            assert a == pytest.approx(90, abs=1)


class TestGetDiagonals:
    def test_square_diagonals(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        diags = sq.get_diagonals()
        # Square has 2 diagonals
        assert len(diags) == 2

    def test_triangle_no_diagonals(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        diags = tri.get_diagonals()
        assert len(diags) == 0

    def test_pentagon_diagonals(self):
        p = RegularPolygon(n=5, radius=100, cx=0, cy=0)
        diags = p.get_diagonals()
        # Pentagon has 5 diagonals
        assert len(diags) == 5


class TestTriangulate:
    def test_triangle_single(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        result = tri.triangulate()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_square(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.triangulate()
        assert isinstance(result, list)
        assert len(result) == 2

    def test_pentagon(self):
        p = RegularPolygon(n=5, radius=100, cx=0, cy=0)
        result = p.triangulate()
        assert isinstance(result, list)
        assert len(result) == 3  # n-2 triangles


class TestSubdivideEdges:
    def test_triangle_subdivide(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        sub = tri.subdivide_edges(iterations=1)
        # Each edge gets split, so 3 edges -> 6 vertices
        assert isinstance(sub, Polygon)

    def test_more_iterations(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        sub = sq.subdivide_edges(iterations=2)
        assert isinstance(sub, Polygon)


class TestSmoothCorners:
    def test_square_smooth(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.smooth_corners(radius=10)
        assert result is not None
        svg = result.to_svg(0)
        assert 'path' in svg.lower() or 'polygon' in svg.lower() or '<' in svg

    def test_triangle_smooth(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        result = tri.smooth_corners(radius=5)
        assert result is not None


class TestLabelVertices:
    def test_triangle_labels(self):
        tri = Polygon((0, 0), (100, 0), (50, 100))
        result = tri.label_vertices()
        assert isinstance(result, VCollection)

    def test_custom_labels(self):
        sq = Polygon((0, 0), (100, 0), (100, 100), (0, 100))
        result = sq.label_vertices(labels=['A', 'B', 'C', 'D'])
        assert isinstance(result, VCollection)
