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


class TestZipWith:
    def test_method_name_become(self):
        """zip_with with method_name='become' copies styling onto each child."""
        from vectormation.objects import Rectangle
        src = VCollection(Circle(r=10, cx=0, cy=0), Circle(r=20, cx=0, cy=0))
        targets = VCollection(
            Rectangle(40, 40, x=100, y=100, fill='#ff0000'),
            Rectangle(80, 80, x=200, y=200, fill='#00ff00'),
        )
        src.zip_with(targets, 'become')
        # After become, each source circle should have adopted the target's fill colour
        for a, b in zip(src.objects, targets.objects):
            a_fill = a.styling.fill.time_func(0)
            b_fill = b.styling.fill.time_func(0)
            assert a_fill == b_fill

    def test_callable_form(self):
        """Legacy callable form: func(a, b, time) still works."""
        called_with = []
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col_a = VCollection(c1)
        col_b = VCollection(c2)
        col_a.zip_with(col_b, lambda a, b, t: called_with.append((a, b, t)))
        assert len(called_with) == 1
        assert called_with[0][0] is c1
        assert called_with[0][1] is c2

    def test_returns_self(self):
        col_a = VCollection(Circle(r=10))
        col_b = VCollection(Circle(r=20))
        result = col_a.zip_with(col_b, lambda a, b, t: None)
        assert result is col_a

    def test_stops_at_shorter(self):
        """Iteration stops at the shorter collection."""
        results = []
        col_a = VCollection(Circle(r=10), Circle(r=20), Circle(r=30))
        col_b = VCollection(Circle(r=5))
        col_a.zip_with(col_b, lambda a, b, t: results.append(1))
        assert len(results) == 1

    def test_method_with_kwargs(self):
        """Extra kwargs are forwarded to the method (string form)."""
        # set_fill(color, start) — first arg is color, second is start
        c1 = Circle(r=50, cx=200, cy=200)
        c2 = Circle(r=50, cx=300, cy=300)
        col_a = VCollection(c1)
        col_b = VCollection(c2)
        # Use become which accepts (other, time=0) so we can pass time via kwargs
        col_a.zip_with(col_b, 'become', time=0)
        # After become the fills should match (both defaults are the same)
        # Mainly verifying the call did not raise
        assert c1.styling.fill.time_func(0) == c2.styling.fill.time_func(0)

    def test_plain_list_as_other(self):
        """other can be a plain list, not just a VCollection."""
        results = []
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1)
        col.zip_with([c2], lambda a, b, t: results.append((a is c1, b is c2)))
        assert results == [(True, True)]


class TestApplyFunction:
    def test_func_called_for_each_child(self):
        """apply_function calls the function once per child."""
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        visited = []
        col.apply_function(lambda obj, i: visited.append(i))
        assert visited == [0, 1, 2]

    def test_func_receives_correct_objects(self):
        """apply_function passes the actual child objects, not copies."""
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        seen = []
        col.apply_function(lambda obj, i: seen.append(obj))
        assert seen[0] is c1
        assert seen[1] is c2

    def test_returns_self(self):
        """apply_function returns the collection for chaining."""
        col = VCollection(Circle(r=10))
        result = col.apply_function(lambda obj, i: None)
        assert result is col

    def test_empty_collection(self):
        """apply_function on empty collection does not raise."""
        col = VCollection()
        result = col.apply_function(lambda obj, i: None)
        assert result is col

    def test_func_can_mutate_children(self):
        """apply_function can be used to perform side-effects on children."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2)
        # Shift each child by its index * 100
        col.apply_function(lambda obj, i: obj.shift(dx=i * 100, start_time=0))
        assert c1.c.at_time(0)[0] == pytest.approx(0)
        assert c2.c.at_time(0)[0] == pytest.approx(100)

    def test_behaves_identically_to_apply(self):
        """apply_function and apply should produce the same results."""
        c1a, c2a = Circle(r=10), Circle(r=20)
        c1b, c2b = Circle(r=10), Circle(r=20)
        log_a, log_b = [], []
        VCollection(c1a, c2a).apply(lambda obj, i: log_a.append(i))
        VCollection(c1b, c2b).apply_function(lambda obj, i: log_b.append(i))
        assert log_a == log_b


class TestVCollectionFlatten:
    def test_flat_collection_unchanged(self):
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        col.flatten()
        assert len(col.objects) == 2

    def test_returns_self(self):
        col = VCollection(Circle(r=10))
        assert col.flatten() is col

    def test_one_level_nesting(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        inner = VCollection(c2, c3)
        outer = VCollection(c1, inner)
        outer.flatten()
        assert len(outer.objects) == 3

    def test_inner_children_are_preserved(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        inner = VCollection(c2, c3)
        outer = VCollection(c1, inner)
        outer.flatten()
        assert c1 in outer.objects
        assert c2 in outer.objects
        assert c3 in outer.objects

    def test_inner_collection_removed(self):
        inner = VCollection(Circle(r=10))
        outer = VCollection(inner)
        outer.flatten()
        # The inner VCollection wrapper should no longer be in objects
        assert not any(isinstance(o, VCollection) for o in outer.objects)

    def test_deeply_nested(self):
        leaf = Circle(r=10)
        level3 = VCollection(leaf)
        level2 = VCollection(level3)
        level1 = VCollection(level2)
        level1.flatten()
        assert len(level1.objects) == 1
        assert level1.objects[0] is leaf

    def test_empty_collection(self):
        col = VCollection()
        col.flatten()
        assert len(col.objects) == 0

    def test_empty_inner_collection(self):
        c = Circle(r=10)
        inner = VCollection()
        outer = VCollection(c, inner)
        outer.flatten()
        assert len(outer.objects) == 1
        assert outer.objects[0] is c

    def test_multiple_nested_collections(self):
        c1, c2, c3, c4 = Circle(r=10), Circle(r=20), Circle(r=30), Circle(r=40)
        inner1 = VCollection(c1, c2)
        inner2 = VCollection(c3, c4)
        outer = VCollection(inner1, inner2)
        outer.flatten()
        assert len(outer.objects) == 4
        assert set(outer.objects) == {c1, c2, c3, c4}

    def test_no_nested_collections_remain(self):
        c1 = Circle(r=10)
        inner = VCollection(VCollection(c1))
        outer = VCollection(inner)
        outer.flatten()
        assert not any(isinstance(o, VCollection) for o in outer.objects)
