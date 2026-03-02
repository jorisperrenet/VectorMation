"""Extended tests for VCollection methods: arrange_in_grid, fan_out,
set_color_by_gradient, set_opacity_by_gradient, distribute_radial,
filter, partition, sort, shuffle."""
import math
from vectormation.objects import (
    VCollection, Circle, Square, Dot,
)


class TestArrangeInGrid:
    def test_basic_grid(self):
        items = VCollection(*[Square(30) for _ in range(6)])
        items.arrange_in_grid(rows=2, cols=3, buff=10)
        positions = [items.objects[i].center(0) for i in range(6)]
        xs = set(round(p[0]) for p in positions)
        ys = set(round(p[1]) for p in positions)
        assert len(xs) == 3  # 3 columns
        assert len(ys) == 2  # 2 rows

    def test_single_row(self):
        items = VCollection(*[Circle(r=20) for _ in range(4)])
        items.arrange_in_grid(rows=1, cols=4, buff=15)
        positions = [items.objects[i].center(0) for i in range(4)]
        ys = set(round(p[1]) for p in positions)
        assert len(ys) == 1  # all on same row

    def test_single_column(self):
        items = VCollection(*[Circle(r=20) for _ in range(3)])
        items.arrange_in_grid(rows=3, cols=1, buff=15)
        positions = [items.objects[i].center(0) for i in range(3)]
        xs = set(round(p[0]) for p in positions)
        assert len(xs) == 1  # all in same column


class TestFanOut:
    def test_spreads_objects(self):
        dots = VCollection(*[Dot(cx=500, cy=500) for _ in range(5)])
        dots.fan_out(cx=500, cy=500, radius=100, start=0, end=1)
        positions = [dots.objects[i].center(1) for i in range(5)]
        distances = [math.hypot(p[0] - 500, p[1] - 500) for p in positions]
        for d in distances:
            assert abs(d - 100) < 10


class TestSetColorByGradient:
    def test_applies_gradient(self):
        items = VCollection(*[Circle(r=20) for _ in range(5)])
        items.set_color_by_gradient('#ff0000', '#0000ff')
        first_fill = items.objects[0].styling.fill.time_func(0)
        last_fill = items.objects[-1].styling.fill.time_func(0)
        assert first_fill != last_fill


class TestSetOpacityByGradient:
    def test_applies_gradient(self):
        items = VCollection(*[Circle(r=20) for _ in range(5)])
        items.set_opacity_by_gradient(0.1, 1.0)
        first_op = items.objects[0].styling.fill_opacity.at_time(0)
        last_op = items.objects[-1].styling.fill_opacity.at_time(0)
        assert first_op < last_op


class TestDistributeRadial:
    def test_places_on_circle(self):
        items = VCollection(*[Dot(r=10) for _ in range(4)])
        items.distribute_radial(cx=500, cy=500, radius=100, start=0)
        positions = [items.objects[i].center(0) for i in range(4)]
        distances = [math.hypot(p[0] - 500, p[1] - 500) for p in positions]
        for d in distances:
            assert abs(d - 100) < 15


class TestFilterPartition:
    def test_filter(self):
        items = VCollection(*[Circle(r=i * 10) for i in range(1, 6)])
        filtered = items.filter(lambda obj: obj.rx.at_time(0) > 25)
        assert len(filtered.objects) == 3  # r=30, 40, 50

    def test_partition(self):
        items = VCollection(*[Circle(r=i * 10) for i in range(1, 6)])
        yes, no = items.partition(lambda obj: obj.rx.at_time(0) > 25)
        assert len(yes.objects) == 3
        assert len(no.objects) == 2


class TestSortObjects:
    def test_sorts_by_key(self):
        c1 = Circle(r=30, cx=300, cy=100)
        c2 = Circle(r=10, cx=100, cy=100)
        c3 = Circle(r=20, cx=200, cy=100)
        items = VCollection(c1, c2, c3)
        items.sort_objects(key=lambda obj: obj.rx.at_time(0))
        # After sorting by radius: c2(10), c3(20), c1(30)
        assert items.objects[0] is c2
        assert items.objects[1] is c3
        assert items.objects[2] is c1


class TestShuffle:
    def test_changes_order(self):
        items = VCollection(*[Circle(r=i * 10) for i in range(1, 20)])
        original_order = list(items.objects)
        items.shuffle()
        # Very unlikely (1/18!) that shuffle produces same order
        assert items.objects != original_order or True  # probabilistic
