"""Tests for VCollection: delegation, stagger, and to_svg."""
import pytest
from vectormation.objects import VCollection, Circle, DOWN
import vectormation.easings as easings


class TestVCollection:
    def test_shift_delegates(self):
        c1 = Circle(r=50, cx=0, cy=0)
        c2 = Circle(r=50, cx=100, cy=100)
        col = VCollection(c1, c2)
        col.shift(dx=10, dy=20, start_time=0)
        p1 = c1.c.at_time(0)
        p2 = c2.c.at_time(0)
        assert p1[0] == pytest.approx(10)
        assert p1[1] == pytest.approx(20)
        assert p2[0] == pytest.approx(110)
        assert p2[1] == pytest.approx(120)

    def test_fadein_delegates(self):
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        col = VCollection(c1, c2)
        col.fadein(start=0, end=1)
        # After fadein, both objects should be visible
        assert c1.show.at_time(0) is True
        assert c2.show.at_time(0) is True

    def test_to_svg_wraps_in_g(self):
        c = Circle(r=50)
        col = VCollection(c)
        svg = col.to_svg(0)
        assert svg.startswith('<g')
        assert '</g>' in svg
        assert '<circle' in svg

    def test_bbox(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=100, cy=100)
        col = VCollection(c1, c2)
        bx, by, bw, bh = col.bbox(0)
        assert bx == pytest.approx(-10)
        assert by == pytest.approx(-10)
        assert bw == pytest.approx(120)
        assert bh == pytest.approx(120)

    def test_stagger_offsets(self):
        """Test that stagger correctly offsets timing for each sub-object."""
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        c3 = Circle(r=50)
        col = VCollection(c1, c2, c3)
        col.stagger('fadein', delay=0.5, start=0, end=1)
        # c1: fadein start=0 end=1
        # c2: fadein start=0.5 end=1.5
        # c3: fadein start=1.0 end=2.0
        # Before c2's start, c2 should not be visible (0 is falsy)
        assert not c2.show.at_time(-0.1)
        # After c3's end, c3 should be visible
        assert c3.show.at_time(2.0)

    def test_scale_to(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        col.scale_to(0, 1, 2, easing=easings.linear)
        # At time 1, scale should be 2
        sx = c.styling.scale_x.at_time(1)
        assert sx == pytest.approx(2, abs=0.1)

    def test_rotate_to(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        col.rotate_to(0, 1, 90, easing=easings.linear)
        rot = c.styling.rotation.at_time(1)
        assert rot[0] == pytest.approx(90, abs=1)

    def test_getitem(self):
        c1 = Circle(r=50)
        c2 = Circle(r=100)
        col = VCollection(c1, c2)
        assert col[0] is c1
        assert col[1] is c2

    def test_len(self):
        c1 = Circle(r=50)
        c2 = Circle(r=100)
        col = VCollection(c1, c2)
        assert len(col) == 2

    def test_copy_independent(self):
        c1 = Circle(r=50, cx=0, cy=0)
        col = VCollection(c1)
        col2 = col.copy()
        col2.shift(dx=100, start_time=0)
        # Original should be unchanged
        assert c1.c.at_time(0)[0] == pytest.approx(0)

    def test_scale_by(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        col.scale_to(0, 1, 2, easing=easings.linear)
        col.scale_by(1, 2, 1.5, easing=easings.linear)
        sx = c.styling.scale_x.at_time(2)
        assert sx == pytest.approx(3, abs=0.1)

    def test_rotate_by(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        col.rotate_to(0, 1, 45, easing=easings.linear)
        col.rotate_by(1, 2, 45, easing=easings.linear)
        rot = c.styling.rotation.at_time(2)
        assert rot[0] == pytest.approx(90, abs=1)

    def test_add(self):
        col = VCollection()
        c = Circle(r=10)
        col.add(c)
        assert len(col) == 1
        assert col[0] is c

    def test_add_multiple(self):
        col = VCollection()
        c1, c2 = Circle(r=10), Circle(r=20)
        col.add(c1, c2)
        assert len(col) == 2

    def test_remove(self):
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        col.remove(c1)
        assert len(col) == 1
        assert col[0] is c2

    def test_arrange_down(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        col = VCollection(c1, c2)
        col.arrange('down', buff=10)
        _, y1, _, _ = c1.bbox(0)
        _, y2, _, _ = c2.bbox(0)
        assert y2 > y1

    def test_arrange_up(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        col = VCollection(c1, c2)
        col.arrange('up', buff=10)
        _, y1, _, _ = c1.bbox(0)
        _, y2, _, _ = c2.bbox(0)
        assert y2 < y1

    def test_arrange_left(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        col = VCollection(c1, c2)
        col.arrange('left', buff=10)
        x1, _, _, _ = c1.bbox(0)
        x2, _, _, _ = c2.bbox(0)
        assert x2 < x1

    def test_arrange_with_direction_constant(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=0, cy=0)
        col = VCollection(c1, c2)
        col.arrange(DOWN, buff=10)
        _, y1, _, _ = c1.bbox(0)
        _, y2, _, _ = c2.bbox(0)
        assert y2 > y1

    def test_write_defaults(self):
        c1 = Circle(r=20)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        col.write()  # should work with defaults (start=0, end=1)
        assert c1.show.at_time(0) is True

    def test_iter(self):
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        items = list(col)
        assert items == [c1, c2]

    def test_center_to_pos(self):
        c1 = Circle(r=20, cx=0, cy=0)
        c2 = Circle(r=20, cx=50, cy=50)
        col = VCollection(c1, c2)
        col.center_to_pos(500, 300)
        bx, by, bw, bh = col.bbox(0)
        assert bx + bw/2 == pytest.approx(500, abs=2)
        assert by + bh/2 == pytest.approx(300, abs=2)


class TestSortBy:
    def test_sort_by_x_position(self):
        c1 = Circle(r=10, cx=300, cy=0)
        c2 = Circle(r=10, cx=100, cy=0)
        c3 = Circle(r=10, cx=200, cy=0)
        col = VCollection(c1, c2, c3)
        col.sort_by(lambda obj: obj.bbox(0)[0])
        # cx=100 < cx=200 < cx=300 → c2, c3, c1
        assert col.objects[0] is c2
        assert col.objects[1] is c3
        assert col.objects[2] is c1

    def test_sort_by_reverse(self):
        c1 = Circle(r=10, cx=300, cy=0)
        c2 = Circle(r=10, cx=100, cy=0)
        c3 = Circle(r=10, cx=200, cy=0)
        col = VCollection(c1, c2, c3)
        col.sort_by(lambda obj: obj.bbox(0)[0], reverse=True)
        assert col.objects[0] is c1
        assert col.objects[1] is c3
        assert col.objects[2] is c2

    def test_sort_by_returns_self(self):
        c1 = Circle(r=10, cx=100)
        c2 = Circle(r=10, cx=200)
        col = VCollection(c1, c2)
        result = col.sort_by(lambda o: o.bbox(0)[0])
        assert result is col

    def test_sort_by_size(self):
        c1 = Circle(r=50)
        c2 = Circle(r=10)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.sort_by(lambda obj: obj.rx.at_time(0))
        assert col.objects[0] is c2
        assert col.objects[1] is c3
        assert col.objects[2] is c1

    def test_sort_by_preserves_all_objects(self):
        circles = [Circle(r=10, cx=i * 50) for i in range(5)]
        col = VCollection(*circles)
        col.sort_by(lambda obj: -obj.bbox(0)[0])  # reverse by x
        assert len(col.objects) == 5
        xs = [obj.bbox(0)[0] for obj in col.objects]
        assert xs == sorted(xs, reverse=True)


class TestTotalWidthHeight:
    def test_total_width_single_child(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        assert col.total_width(0) == pytest.approx(c.get_width(0))

    def test_total_width_two_children(self):
        c1 = Circle(r=30, cx=0, cy=0)
        c2 = Circle(r=40, cx=200, cy=0)
        col = VCollection(c1, c2)
        expected = c1.get_width(0) + c2.get_width(0)
        assert col.total_width(0) == pytest.approx(expected)

    def test_total_height_two_children(self):
        c1 = Circle(r=30, cx=0, cy=0)
        c2 = Circle(r=40, cx=0, cy=200)
        col = VCollection(c1, c2)
        expected = c1.get_height(0) + c2.get_height(0)
        assert col.total_height(0) == pytest.approx(expected)

    def test_total_width_after_arrange(self):
        # After arrange, total_width should still be sum of individual widths
        circles = [Circle(r=20, cx=i * 100, cy=0) for i in range(4)]
        col = VCollection(*circles)
        expected = sum(c.get_width(0) for c in circles)
        assert col.total_width(0) == pytest.approx(expected)

    def test_total_width_less_than_get_width_with_gaps(self):
        # When children are spread apart, total_width < get_width
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=1000, cy=0)
        col = VCollection(c1, c2)
        assert col.total_width(0) < col.get_width(0)

    def test_total_width_empty_collection(self):
        col = VCollection()
        assert col.total_width(0) == pytest.approx(0)

    def test_total_height_empty_collection(self):
        col = VCollection()
        assert col.total_height(0) == pytest.approx(0)

    def test_total_width_returns_float(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        assert isinstance(col.total_width(0), (int, float))

    def test_total_height_returns_float(self):
        c = Circle(r=50, cx=100, cy=100)
        col = VCollection(c)
        assert isinstance(col.total_height(0), (int, float))


class TestVCollectionGetChild:
    def test_get_first_child(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        assert col.get_child(0) is c1

    def test_get_last_child_by_positive_index(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        assert col.get_child(1) is c2

    def test_get_child_negative_index(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        assert col.get_child(-1) is c2
        assert col.get_child(-2) is c1

    def test_out_of_range_positive(self):
        col = VCollection(Circle(r=10))
        with pytest.raises(IndexError):
            col.get_child(1)

    def test_out_of_range_negative(self):
        col = VCollection(Circle(r=10))
        with pytest.raises(IndexError):
            col.get_child(-2)

    def test_empty_collection_raises(self):
        col = VCollection()
        with pytest.raises(IndexError):
            col.get_child(0)

    def test_error_message_contains_index(self):
        col = VCollection(Circle(r=10))
        with pytest.raises(IndexError, match='5'):
            col.get_child(5)
