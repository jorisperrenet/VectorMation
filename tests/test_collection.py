"""Tests for VCollection: layout, grouping, and bulk operations."""
import pytest

from vectormation._collection import VCollection
from vectormation._shapes import Circle, Rectangle
from vectormation._constants import SMALL_BUFF
import vectormation.easings as easings


def _make_circles(n=3, r=20):
    """Create n circles all at the origin for testing layout."""
    return [Circle(r=r, cx=0, cy=0) for _ in range(n)]


class TestBboxAndCenter:

    def test_bbox_single_object(self):
        c = Circle(r=50, cx=100, cy=200)
        col = VCollection(c)
        x, y, w, h = col.bbox(0)
        assert (x, y, w, h) == pytest.approx((50, 150, 100, 100))

    def test_bbox_multiple_objects(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=200, cy=200)
        col = VCollection(c1, c2)
        x, y, w, h = col.bbox(0)
        assert x == pytest.approx(-50)
        assert y == pytest.approx(-50)
        assert w == pytest.approx(300)
        assert h == pytest.approx(300)

    def test_center_is_bbox_center(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=200, cy=200)
        col = VCollection(c1, c2)
        cx, cy = col.center(0)
        assert cx == pytest.approx(100)
        assert cy == pytest.approx(100)


class TestArrange:

    def test_arrange_right_spacing(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.arrange('right', buff=10, start=0)
        # After arranging, objects should be in a row with gaps
        bboxes = [c.bbox(0) for c in circles]
        for i in range(len(circles) - 1):
            right_edge_i = bboxes[i][0] + bboxes[i][2]
            left_edge_next = bboxes[i + 1][0]
            gap = left_edge_next - right_edge_i
            assert gap == pytest.approx(10, abs=1)

    def test_arrange_down_ordering(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.arrange('down', buff=10, start=0)
        # Each circle should be below the previous
        for i in range(len(circles) - 1):
            assert circles[i + 1].center(0)[1] > circles[i].center(0)[1]

    def test_arrange_left_reverse_order(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.arrange('left', buff=10, start=0)
        # First object should be rightmost
        for i in range(len(circles) - 1):
            assert circles[i].center(0)[0] > circles[i + 1].center(0)[0]

    def test_arrange_preserves_group_center(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        center_before = col.center(0)
        col.arrange('right', buff=10, start=0)
        center_after = col.center(0)
        assert center_before == pytest.approx(center_after, abs=1)

    def test_arrange_empty_collection(self):
        col = VCollection()
        col.arrange('right')  # should not crash


class TestArrangeInGrid:

    def test_grid_2x2(self):
        circles = _make_circles(4, r=20)
        col = VCollection(*circles)
        col.arrange_in_grid(rows=2, cols=2, buff=10, start=0)
        # All 4 should have distinct positions
        centers = [c.center(0) for c in circles]
        xs = {round(c[0], 1) for c in centers}
        ys = {round(c[1], 1) for c in centers}
        assert len(xs) == 2
        assert len(ys) == 2

    def test_grid_auto_rows(self):
        circles = _make_circles(6, r=20)
        col = VCollection(*circles)
        col.arrange_in_grid(cols=3, buff=10, start=0)
        # Should infer 2 rows
        centers = [c.center(0) for c in circles]
        ys = sorted({round(c[1]) for c in centers})
        assert len(ys) == 2


class TestDistribute:

    def test_distribute_even_spacing(self):
        circles = _make_circles(4, r=20)
        col = VCollection(*circles)
        col.arrange('right', buff=0)  # pack them first
        col.distribute('right', buff=0)
        centers = [c.center(0)[0] for c in circles]
        # Spacing between consecutive centers should be equal
        gaps = [centers[i + 1] - centers[i] for i in range(len(centers) - 1)]
        for gap in gaps:
            assert gap == pytest.approx(gaps[0], abs=1)


class TestShiftAndPosition:

    def test_shift_all_children(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        col.shift(dx=50, dy=50, start=0)
        assert c1.center(0) == pytest.approx((50, 50))
        assert c2.center(0) == pytest.approx((150, 150))

    def test_center_to_pos(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=0)
        col = VCollection(c1, c2)
        col.center_to_pos(500, 500, start=0)
        assert col.center(0) == pytest.approx((500, 500), abs=1)


class TestBulkOperations:

    def test_set_color_by_gradient(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.set_color_by_gradient('#ff0000', '#0000ff')
        # First should be red, last should be blue
        first_fill = circles[0].styling.fill.at_time(0)
        last_fill = circles[2].styling.fill.at_time(0)
        assert first_fill == 'rgb(255,0,0)'
        assert last_fill == 'rgb(0,0,255)'

    def test_filter(self):
        c_big = Circle(r=100, cx=0, cy=0)
        c_small = Circle(r=10, cx=0, cy=0)
        col = VCollection(c_big, c_small)
        big_ones = col.filter(lambda obj: obj.rx.at_time(0) > 50)
        assert len(big_ones.objects) == 1

    def test_for_each(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.arrange('right', buff=10)
        # for_each takes a method name string, not a callable
        col.for_each('shift', dx=10, dy=0, start=0)
        # Each circle should have shifted by 10px
        for c in circles:
            assert c.center(0)[0] != pytest.approx(0)

    def test_sort_children(self):
        c1 = Circle(r=20, cx=300, cy=0)
        c2 = Circle(r=20, cx=100, cy=0)
        c3 = Circle(r=20, cx=200, cy=0)
        col = VCollection(c1, c2, c3)
        col.sort_children(key='x')
        # After sorting by x, the first child should have the smallest x
        centers_x = [obj.center(0)[0] for obj in col.objects]
        assert centers_x == sorted(centers_x)

    def test_len(self):
        col = VCollection(*_make_circles(5))
        assert len(col) == 5

    def test_indexing(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        assert col[0] is circles[0]
        assert col[-1] is circles[-1]


class TestStagger:

    def test_stagger_calls_method_on_each(self):
        circles = _make_circles(3, r=20)
        col = VCollection(*circles)
        col.stagger('fadein', start=0, end=3, overlap=0)
        # After staggering fadein, each circle should become visible at different times
        # First circle visible at t=1 (after its fadein), third not yet visible at t=0.5
        assert circles[0].show.at_time(1) is True
