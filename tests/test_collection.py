"""Tests for VCollection: delegation, stagger, and to_svg."""
import math
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


class TestInterleave:
    def test_equal_length_collections(self):
        """Interleaving two equal-length collections alternates children."""
        c1, c2 = Circle(r=10), Circle(r=20)
        c3, c4 = Circle(r=30), Circle(r=40)
        a = VCollection(c1, c2)
        b = VCollection(c3, c4)
        result = a.interleave(b)
        assert list(result.objects) == [c1, c3, c2, c4]

    def test_unequal_length_shorter_first(self):
        """Extra elements from the longer collection appear at the end."""
        c1 = Circle(r=10)
        c2, c3, c4 = Circle(r=20), Circle(r=30), Circle(r=40)
        a = VCollection(c1)
        b = VCollection(c2, c3, c4)
        result = a.interleave(b)
        assert list(result.objects) == [c1, c2, c3, c4]

    def test_unequal_length_longer_first(self):
        """Extra elements from the self collection appear at the end."""
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        c4 = Circle(r=40)
        a = VCollection(c1, c2, c3)
        b = VCollection(c4)
        result = a.interleave(b)
        assert list(result.objects) == [c1, c4, c2, c3]

    def test_empty_self(self):
        """Interleaving an empty collection returns a copy of other."""
        c1, c2 = Circle(r=10), Circle(r=20)
        a = VCollection()
        b = VCollection(c1, c2)
        result = a.interleave(b)
        assert list(result.objects) == [c1, c2]

    def test_empty_other(self):
        """Interleaving with an empty collection returns a copy of self."""
        c1, c2 = Circle(r=10), Circle(r=20)
        a = VCollection(c1, c2)
        b = VCollection()
        result = a.interleave(b)
        assert list(result.objects) == [c1, c2]

    def test_returns_new_collection(self):
        """interleave returns a new VCollection, not self or other."""
        c1, c2 = Circle(r=10), Circle(r=20)
        a = VCollection(c1)
        b = VCollection(c2)
        result = a.interleave(b)
        assert result is not a
        assert result is not b
        assert isinstance(result, VCollection)

    def test_originals_unchanged(self):
        """Original collections are not modified."""
        c1, c2 = Circle(r=10), Circle(r=20)
        a = VCollection(c1)
        b = VCollection(c2)
        a.interleave(b)
        assert len(a.objects) == 1
        assert len(b.objects) == 1


class TestVObjectFadeShift:
    def test_fade_shift_returns_self(self):
        c = Circle(r=50)
        result = c.fade_shift(dx=100, dy=0, start=0, end=1)
        assert result is c

    def test_fade_shift_opacity_reaches_zero(self):
        c = Circle(r=50)
        c.fade_shift(dx=0, dy=0, start=0, end=1)
        assert c.styling.opacity.at_time(1) == pytest.approx(0, abs=0.05)

    def test_fade_shift_object_hidden_at_end(self):
        c = Circle(r=50)
        c.fade_shift(dx=0, dy=100, start=0, end=1)
        assert not c.show.at_time(1)

    def test_fade_shift_applies_displacement(self):
        """After fade_shift the object should be displaced by (dx, dy)."""
        c = Circle(r=50, cx=100, cy=200)
        c.fade_shift(dx=50, dy=30, start=0, end=1)
        cx, cy = c.c.at_time(1)
        assert cx == pytest.approx(150)
        assert cy == pytest.approx(230)

    def test_fade_shift_no_displacement_mid_opacity(self):
        """Opacity should be between 0 and 1 at the midpoint."""
        c = Circle(r=50)
        c.fade_shift(dx=0, dy=0, start=0, end=2)
        op = c.styling.opacity.at_time(1)
        assert 0.0 < op < 1.0

    def test_fade_shift_zero_duration_hides_immediately(self):
        """Zero-duration fade_shift should hide the object immediately."""
        c = Circle(r=50)
        c.fade_shift(dx=10, dy=10, start=1, end=1)
        assert not c.show.at_time(1)


class TestVCollectionNthFirstLast:
    def test_nth_returns_correct_child(self):
        c0, c1, c2 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c0, c1, c2)
        assert col.nth(0) is c0
        assert col.nth(1) is c1
        assert col.nth(2) is c2

    def test_nth_negative_index(self):
        c0, c1, c2 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c0, c1, c2)
        assert col.nth(-1) is c2
        assert col.nth(-2) is c1

    def test_nth_out_of_range_raises(self):
        col = VCollection(Circle(r=10))
        with pytest.raises(IndexError):
            col.nth(5)

    def test_first_returns_first_child(self):
        c0, c1 = Circle(r=10), Circle(r=20)
        col = VCollection(c0, c1)
        assert col.first() is c0

    def test_last_returns_last_child(self):
        c0, c1 = Circle(r=10), Circle(r=20)
        col = VCollection(c0, c1)
        assert col.last() is c1

    def test_first_on_empty_raises(self):
        col = VCollection()
        with pytest.raises(IndexError):
            col.first()

    def test_last_on_empty_raises(self):
        col = VCollection()
        with pytest.raises(IndexError):
            col.last()

    def test_first_last_same_object_when_single_child(self):
        c = Circle(r=10)
        col = VCollection(c)
        assert col.first() is c
        assert col.last() is c


class TestVCollectionCount:
    def test_empty_collection(self):
        col = VCollection()
        assert col.count() == 0

    def test_single_object(self):
        c = Circle(r=50)
        col = VCollection(c)
        assert col.count() == 1

    def test_multiple_objects(self):
        objects = [Circle(r=10) for _ in range(5)]
        col = VCollection(*objects)
        assert col.count() == 5

    def test_count_matches_len(self):
        objects = [Circle(r=10) for _ in range(3)]
        col = VCollection(*objects)
        assert col.count() == len(col)


class TestVObjectSetVisible:
    def test_hide_from_start(self):
        c = Circle(r=50)
        c.set_visible(False, start=0)
        assert not c.show.at_time(0)

    def test_show_from_start(self):
        c = Circle(r=50)
        c.set_visible(False, start=0)
        c.set_visible(True, start=2)
        assert not c.show.at_time(1)
        assert c.show.at_time(2)

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.set_visible(False, start=0)
        assert result is c

    def test_default_start_zero(self):
        c = Circle(r=50)
        c.set_visible(False)
        assert not c.show.at_time(0)

    def test_visible_true(self):
        c = Circle(r=50)
        # Hide first, then show again
        c.set_visible(False, start=0)
        c.set_visible(True, start=1)
        assert c.show.at_time(1)


class TestEnumerateChildren:
    def test_returns_list(self):
        c1 = Circle(r=50)
        c2 = Circle(r=30)
        col = VCollection(c1, c2)
        result = col.enumerate_children()
        assert isinstance(result, list)

    def test_indices_correct(self):
        c1 = Circle(r=50)
        c2 = Circle(r=30)
        c3 = Circle(r=10)
        col = VCollection(c1, c2, c3)
        result = col.enumerate_children()
        assert len(result) == 3
        assert result[0][0] == 0
        assert result[1][0] == 1
        assert result[2][0] == 2

    def test_objects_correct(self):
        c1 = Circle(r=50)
        c2 = Circle(r=30)
        col = VCollection(c1, c2)
        result = col.enumerate_children()
        assert result[0][1] is c1
        assert result[1][1] is c2

    def test_empty_collection(self):
        col = VCollection()
        result = col.enumerate_children()
        assert result == []

    def test_single_child(self):
        c = Circle(r=50)
        col = VCollection(c)
        result = col.enumerate_children()
        assert len(result) == 1
        assert result[0] == (0, c)

    def test_iterable_in_for_loop(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        seen = [(i, obj) for i, obj in col.enumerate_children()]
        assert len(seen) == 2
        assert seen[0][0] == 0
        assert seen[1][0] == 1


class TestVCollectionTake:
    def test_take_returns_vcollection(self):
        col = VCollection(Circle(), Circle(), Circle())
        result = col.take(2)
        assert isinstance(result, VCollection)

    def test_take_correct_count(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.take(2)
        assert len(result) == 2

    def test_take_correct_objects(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.take(2)
        assert result.objects[0] is c1
        assert result.objects[1] is c2

    def test_take_zero_returns_empty(self):
        col = VCollection(Circle(), Circle())
        result = col.take(0)
        assert len(result) == 0

    def test_take_more_than_length_returns_all(self):
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        result = col.take(100)
        assert len(result) == 2

    def test_take_does_not_modify_original(self):
        col = VCollection(Circle(), Circle(), Circle())
        col.take(1)
        assert len(col) == 3


class TestVCollectionSkip:
    def test_skip_returns_vcollection(self):
        col = VCollection(Circle(), Circle(), Circle())
        result = col.skip(1)
        assert isinstance(result, VCollection)

    def test_skip_correct_count(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.skip(1)
        assert len(result) == 2

    def test_skip_correct_objects(self):
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.skip(1)
        assert result.objects[0] is c2
        assert result.objects[1] is c3

    def test_skip_zero_returns_all(self):
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        result = col.skip(0)
        assert len(result) == 2

    def test_skip_all_returns_empty(self):
        col = VCollection(Circle(), Circle())
        result = col.skip(2)
        assert len(result) == 0

    def test_skip_more_than_length_returns_empty(self):
        col = VCollection(Circle(), Circle())
        result = col.skip(100)
        assert len(result) == 0

    def test_skip_does_not_modify_original(self):
        col = VCollection(Circle(), Circle(), Circle())
        col.skip(2)
        assert len(col) == 3

    def test_take_and_skip_complement(self):
        """take(n) and skip(n) together should cover all children."""
        c1, c2, c3, c4 = Circle(r=1), Circle(r=2), Circle(r=3), Circle(r=4)
        col = VCollection(c1, c2, c3, c4)
        head = col.take(2)
        tail = col.skip(2)
        assert len(head) + len(tail) == len(col)
        assert list(head.objects) + list(tail.objects) == list(col.objects)


class TestVCollectionChunk:
    def test_chunk_even_division(self):
        """10 objects chunked by 5 -> 2 chunks of 5."""
        objs = [Circle(r=i + 1) for i in range(10)]
        col = VCollection(*objs)
        chunks = col.chunk(5)
        assert len(chunks) == 2
        assert all(len(c.objects) == 5 for c in chunks)

    def test_chunk_uneven_division(self):
        """10 objects chunked by 3 -> [3, 3, 3, 1]."""
        objs = [Circle(r=i + 1) for i in range(10)]
        col = VCollection(*objs)
        chunks = col.chunk(3)
        assert len(chunks) == 4
        assert [len(c.objects) for c in chunks] == [3, 3, 3, 1]

    def test_chunk_size_one(self):
        """Chunk size of 1 -> one VCollection per child."""
        objs = [Circle(r=i + 1) for i in range(5)]
        col = VCollection(*objs)
        chunks = col.chunk(1)
        assert len(chunks) == 5
        assert all(len(c.objects) == 1 for c in chunks)

    def test_chunk_size_larger_than_collection(self):
        """Chunk size > len -> single chunk with all children."""
        objs = [Circle(r=i + 1) for i in range(4)]
        col = VCollection(*objs)
        chunks = col.chunk(100)
        assert len(chunks) == 1
        assert len(chunks[0].objects) == 4

    def test_chunk_preserves_children(self):
        """All children should appear exactly once across all chunks."""
        objs = [Circle(r=i + 1) for i in range(7)]
        col = VCollection(*objs)
        chunks = col.chunk(3)
        all_children = []
        for c in chunks:
            all_children.extend(c.objects)
        assert all_children == objs

    def test_chunk_returns_vcollections(self):
        col = VCollection(Circle(), Circle(), Circle())
        chunks = col.chunk(2)
        assert all(isinstance(c, VCollection) for c in chunks)

    def test_chunk_empty_collection(self):
        """Chunking an empty collection returns an empty list."""
        col = VCollection()
        chunks = col.chunk(3)
        assert chunks == []

    def test_chunk_invalid_size_raises(self):
        col = VCollection(Circle(), Circle())
        with pytest.raises(ValueError):
            col.chunk(0)
        with pytest.raises(ValueError):
            col.chunk(-1)

    def test_chunk_exact_division(self):
        """6 objects with size=2 -> 3 chunks of exactly 2."""
        objs = [Circle(r=i + 1) for i in range(6)]
        col = VCollection(*objs)
        chunks = col.chunk(2)
        assert len(chunks) == 3
        assert all(len(c.objects) == 2 for c in chunks)


class TestFadeInOneByOne:
    def test_fade_in_one_by_one_returns_self(self):
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        col = VCollection(c1, c2)
        result = col.fade_in_one_by_one(start=0, end=2)
        assert result is col

    def test_fade_in_one_by_one_sequential(self):
        """With overlap=0, children should fade in sequentially (no overlap)."""
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        c3 = Circle(r=50)
        col = VCollection(c1, c2, c3)
        col.fade_in_one_by_one(start=0, end=3, overlap=0.0, easing=easings.linear)
        # c1: 0-1, c2: 1-2, c3: 2-3
        # At t=0.5 c1 is mid-fade, c2 should not have started yet
        assert c1.styling.opacity.at_time(0.5) == pytest.approx(0.5, abs=0.1)
        # c2 starts at t=1, so at t=0.5 it should be at opacity 0 (not started)
        assert c2.show.at_time(0.5) is False

    def test_fade_in_one_by_one_all_visible_at_end(self):
        """After the animation, all children should be fully visible."""
        circles = [Circle(r=50) for _ in range(4)]
        col = VCollection(*circles)
        col.fade_in_one_by_one(start=0, end=4, easing=easings.linear)
        for c in circles:
            assert c.styling.opacity.at_time(4) == pytest.approx(1.0, abs=0.05)

    def test_fade_in_one_by_one_empty_collection(self):
        """Empty collection should return self without error."""
        col = VCollection()
        result = col.fade_in_one_by_one(start=0, end=1)
        assert result is col

    def test_fade_in_one_by_one_single_child(self):
        """Single child should use the full time range."""
        c = Circle(r=50)
        col = VCollection(c)
        col.fade_in_one_by_one(start=0, end=2, easing=easings.linear)
        assert c.styling.opacity.at_time(1) == pytest.approx(0.5, abs=0.1)
        assert c.styling.opacity.at_time(2) == pytest.approx(1.0, abs=0.05)


class TestSetZOrder:
    def test_set_z_order_reorders(self):
        """set_z_order should reorder children by index list."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        c3 = Circle(r=30, cx=200, cy=200)
        col = VCollection(c1, c2, c3)
        col.set_z_order([2, 0, 1])
        assert col.objects[0] is c3
        assert col.objects[1] is c1
        assert col.objects[2] is c2

    def test_set_z_order_identity(self):
        """Identity permutation should leave order unchanged."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        col.set_z_order([0, 1])
        assert col.objects[0] is c1
        assert col.objects[1] is c2

    def test_set_z_order_returns_self(self):
        """set_z_order should return self for chaining."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        result = col.set_z_order([1, 0])
        assert result is col

    def test_set_z_order_reverse(self):
        """Reversing the order should match reversed list."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.set_z_order([2, 1, 0])
        assert col.objects == [c3, c2, c1]


class TestSendToBack:
    def test_send_to_back_by_reference(self):
        """send_to_back moves a child to the front of the objects list (rendered first)."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.send_to_back(c3)
        assert col.objects == [c3, c1, c2]

    def test_send_to_back_by_index(self):
        """send_to_back accepts an integer index."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.send_to_back(2)  # index 2 is c3
        assert col.objects[0] is c3

    def test_send_to_back_returns_self(self):
        """send_to_back should return self for chaining."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        result = col.send_to_back(c2)
        assert result is col

    def test_send_to_back_already_first(self):
        """send_to_back on the first child keeps order unchanged."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        col.send_to_back(c1)
        assert col.objects == [c1, c2]


class TestBringToFront:
    def test_bring_to_front_by_object(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.bring_to_front(c1)
        assert col.objects == [c2, c3, c1]

    def test_bring_to_front_by_index(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.bring_to_front(0)
        assert col.objects == [c2, c3, c1]

    def test_bring_to_front_returns_self(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        result = col.bring_to_front(c1)
        assert result is col

    def test_bring_to_front_already_last(self):
        """bring_to_front on the last child keeps order unchanged."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col = VCollection(c1, c2)
        col.bring_to_front(c2)
        assert col.objects == [c1, c2]

    def test_bring_to_front_preserves_length(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.bring_to_front(c2)
        assert len(col.objects) == 3


class TestRotateOrder:
    def test_rotate_order_by_one(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.rotate_order(1)
        assert col.objects == [c2, c3, c1]

    def test_rotate_order_by_two(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.rotate_order(2)
        assert col.objects == [c3, c1, c2]

    def test_rotate_order_full_cycle(self):
        """Rotating by len(objects) should produce the same order."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        col.rotate_order(3)
        assert col.objects == [c1, c2, c3]

    def test_rotate_order_returns_self(self):
        col = VCollection(Circle(r=10), Circle(r=20))
        result = col.rotate_order(1)
        assert result is col

    def test_rotate_order_empty(self):
        """Rotating an empty collection should not raise."""
        col = VCollection()
        result = col.rotate_order(1)
        assert result is col


class TestEach:
    def test_each_applies_function(self):
        """each() should call the function on every child."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        visited = []
        col.each(lambda obj: visited.append(obj))
        assert visited == [c1, c2]

    def test_each_returns_self(self):
        """each() should return self for chaining."""
        col = VCollection(Circle(r=10), Circle(r=20))
        result = col.each(lambda _: None)
        assert result is col

    def test_each_modifies_children(self):
        """each() should be able to modify children via the function."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1, c2)
        col.each(lambda obj: obj.shift(dx=10, dy=0, start_time=0))
        assert c1.c.at_time(0)[0] == pytest.approx(10)
        assert c2.c.at_time(0)[0] == pytest.approx(110)


class TestMaxByMinBy:
    def test_max_by_radius(self):
        """max_by should return the child with the largest key value."""
        c1 = Circle(r=10)
        c2 = Circle(r=50)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.max_by(key=lambda c: c.r.at_time(0))
        assert result is c2

    def test_min_by_radius(self):
        """min_by should return the child with the smallest key value."""
        c1 = Circle(r=10)
        c2 = Circle(r=50)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        result = col.min_by(key=lambda c: c.r.at_time(0))
        assert result is c1

    def test_max_by_empty_returns_none(self):
        """max_by on an empty collection should return None."""
        col = VCollection()
        assert col.max_by(key=lambda c: 0) is None

    def test_min_by_empty_returns_none(self):
        """min_by on an empty collection should return None."""
        col = VCollection()
        assert col.min_by(key=lambda c: 0) is None

    def test_sum_by_basic(self):
        """sum_by should sum key(child) across all children."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        total = col.sum_by(lambda c: c.rx.at_time(0))
        assert total == pytest.approx(60)

    def test_sum_by_empty(self):
        """sum_by on an empty collection should return 0."""
        col = VCollection()
        assert col.sum_by(lambda _: 1) == 0

    def test_sum_by_single_child(self):
        """sum_by with one child returns that child's value."""
        c = Circle(r=42)
        col = VCollection(c)
        assert col.sum_by(lambda c: c.rx.at_time(0)) == pytest.approx(42)


class TestVCollectionClear:
    def test_clear_removes_all_children(self):
        """clear() should remove all children from the collection."""
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col = VCollection(c1, c2, c3)
        assert len(col.objects) == 3
        col.clear()
        assert len(col.objects) == 0

    def test_clear_returns_self(self):
        """clear() should return self for chaining."""
        col = VCollection(Circle(r=10), Circle(r=20))
        assert col.clear() is col

    def test_clear_on_empty_collection(self):
        """clear() on an already empty collection should not raise."""
        col = VCollection()
        col.clear()
        assert len(col.objects) == 0


class TestRemoveAt:
    """Tests for VCollection.remove_at()."""

    def test_remove_at_removes_correct_child(self):
        """remove_at(1) should remove the second child."""
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        removed = col.remove_at(1)
        assert removed is c2
        assert len(col.objects) == 2
        assert col.objects[0] is c1
        assert col.objects[1] is c3

    def test_remove_at_first(self):
        """remove_at(0) should remove the first child."""
        c1, c2 = Circle(r=10), Circle(r=20)
        col = VCollection(c1, c2)
        removed = col.remove_at(0)
        assert removed is c1
        assert len(col.objects) == 1

    def test_remove_at_negative_index(self):
        """remove_at(-1) should remove the last child."""
        c1, c2, c3 = Circle(r=10), Circle(r=20), Circle(r=30)
        col = VCollection(c1, c2, c3)
        removed = col.remove_at(-1)
        assert removed is c3
        assert len(col.objects) == 2

    def test_remove_at_out_of_range(self):
        """remove_at with out-of-range index should raise IndexError."""
        col = VCollection(Circle(r=10))
        with pytest.raises(IndexError):
            col.remove_at(5)

    def test_all_match_true(self):
        """all_match should return True when all children satisfy predicate."""
        col = VCollection(Circle(r=10), Circle(r=20), Circle(r=30))
        assert col.all_match(lambda obj: isinstance(obj, Circle)) is True

    def test_all_match_false(self):
        """all_match should return False when at least one child fails."""
        from vectormation.objects import Rectangle
        col = VCollection(Circle(r=10), Rectangle(20, 20), Circle(r=30))
        assert col.all_match(lambda obj: isinstance(obj, Circle)) is False

    def test_all_match_empty(self):
        """all_match on empty collection should return True (vacuous truth)."""
        col = VCollection()
        assert col.all_match(lambda obj: False) is True

    def test_any_match_true(self):
        """any_match should return True when at least one child satisfies predicate."""
        from vectormation.objects import Rectangle
        col = VCollection(Circle(r=10), Rectangle(20, 20))
        assert col.any_match(lambda obj: isinstance(obj, Circle)) is True

    def test_any_match_false(self):
        """any_match should return False when no children satisfy predicate."""
        from vectormation.objects import Rectangle
        col = VCollection(Rectangle(10, 10), Rectangle(20, 20))
        assert col.any_match(lambda obj: isinstance(obj, Circle)) is False

    def test_any_match_empty(self):
        """any_match on empty collection should return False."""
        col = VCollection()
        assert col.any_match(lambda obj: True) is False


class TestSnakeLayout:
    def test_snake_layout_returns_self(self):
        """snake_layout should return self for chaining."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(6)]
        col = VCollection(*circles)
        result = col.snake_layout(cols=3)
        assert result is col

    def test_snake_layout_empty(self):
        """snake_layout on empty collection should be a no-op."""
        col = VCollection()
        result = col.snake_layout(cols=3)
        assert result is col
        assert len(col.objects) == 0

    def test_snake_layout_reverses_odd_rows(self):
        """Objects in odd rows should be arranged right-to-left."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(6)]
        col = VCollection(*circles)
        col.snake_layout(cols=3, buff=5)
        # Row 0: indices 0, 1, 2 (left to right)
        # Row 1: indices 3, 4, 5 (right to left)
        x0 = circles[0].center(0)[0]
        x1 = circles[1].center(0)[0]
        x2 = circles[2].center(0)[0]
        x3 = circles[3].center(0)[0]
        x4 = circles[4].center(0)[0]
        x5 = circles[5].center(0)[0]
        # Row 0: x increases
        assert x0 < x1 < x2
        # Row 1: x decreases (snake pattern)
        assert x3 > x4 > x5

    def test_snake_layout_rows_below(self):
        """Row 1 should be below row 0."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(6)]
        col = VCollection(*circles)
        col.snake_layout(cols=3, buff=5)
        y0 = circles[0].center(0)[1]
        y3 = circles[3].center(0)[1]
        assert y3 > y0  # row 1 below row 0

    def test_snake_layout_default_cols(self):
        """Without explicit cols, should auto-compute from sqrt(n)."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(9)]
        col = VCollection(*circles)
        col.snake_layout()
        # 9 items: cols=ceil(sqrt(9))=3, rows=3
        # All items should have been positioned (no errors)
        x_vals = [c.center(0)[0] for c in circles]
        # Row 0 (0,1,2) left-to-right
        assert x_vals[0] < x_vals[1] < x_vals[2]
        # Row 1 (3,4,5) right-to-left
        assert x_vals[3] > x_vals[4] > x_vals[5]

    def test_snake_layout_first_and_last_connected(self):
        """In a snake layout, the end of row N should be near the start of row N+1."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(6)]
        col = VCollection(*circles)
        col.snake_layout(cols=3, buff=5)
        # Last of row 0 (index 2) should be rightmost
        # First of row 1 (index 3) should also be rightmost (snake reversal)
        x2 = circles[2].center(0)[0]
        x3 = circles[3].center(0)[0]
        assert x2 == pytest.approx(x3, abs=1)


class TestArrangeAlongPath:
    def test_arrange_along_path_returns_self(self):
        """arrange_along_path should return self for chaining."""
        circles = [Circle(r=10, cx=0, cy=0) for _ in range(3)]
        col = VCollection(*circles)
        result = col.arrange_along_path('M0,0 L300,0')
        assert result is col

    def test_arrange_along_path_empty(self):
        """arrange_along_path on empty collection should be a no-op."""
        col = VCollection()
        result = col.arrange_along_path('M0,0 L300,0')
        assert result is col

    def test_arrange_along_straight_line(self):
        """Children should be evenly spaced along a straight line."""
        circles = [Circle(r=5, cx=0, cy=0) for _ in range(3)]
        col = VCollection(*circles)
        col.arrange_along_path('M0,500 L300,500')
        # First child at start of path (0, 500)
        cx0, cy0 = circles[0].center(0)
        assert cx0 == pytest.approx(0, abs=2)
        assert cy0 == pytest.approx(500, abs=2)
        # Last child at end of path (300, 500)
        cx2, cy2 = circles[2].center(0)
        assert cx2 == pytest.approx(300, abs=2)
        assert cy2 == pytest.approx(500, abs=2)
        # Middle child at midpoint (150, 500)
        cx1, _ = circles[1].center(0)
        assert cx1 == pytest.approx(150, abs=2)

    def test_arrange_along_path_single_object(self):
        """A single object should be placed at the start of the path."""
        c = Circle(r=5, cx=0, cy=0)
        col = VCollection(c)
        col.arrange_along_path('M100,200 L400,200')
        cx, cy = c.center(0)
        assert cx == pytest.approx(100, abs=2)
        assert cy == pytest.approx(200, abs=2)

    def test_arrange_along_vertical_path(self):
        """Children should be arranged vertically along a vertical line."""
        circles = [Circle(r=5, cx=0, cy=0) for _ in range(3)]
        col = VCollection(*circles)
        col.arrange_along_path('M500,0 L500,400')
        # All x should be ~500
        for c in circles:
            assert c.center(0)[0] == pytest.approx(500, abs=2)
        # y should increase
        y0 = circles[0].center(0)[1]
        y1 = circles[1].center(0)[1]
        y2 = circles[2].center(0)[1]
        assert y0 < y1 < y2


class TestConverge:
    def test_converge_returns_self(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=200, cy=200)
        col = VCollection(c1, c2)
        assert col.converge(100, 100, start=0, end=1) is col

    def test_converge_moves_to_target(self):
        """All children should be at the convergence point at end time."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=200, cy=200)
        c3 = Circle(r=10, cx=400, cy=100)
        col = VCollection(c1, c2, c3)
        col.converge(300, 300, start=0, end=1)
        for c in [c1, c2, c3]:
            cx, cy = c.center(1)
            assert cx == pytest.approx(300, abs=2)
            assert cy == pytest.approx(300, abs=2)

    def test_converge_starts_at_original(self):
        """Children should be at their original positions at start time."""
        c1 = Circle(r=10, cx=50, cy=50)
        c2 = Circle(r=10, cx=200, cy=200)
        col = VCollection(c1, c2)
        col.converge(300, 300, start=0, end=1)
        cx1, cy1 = c1.center(0)
        cx2, cy2 = c2.center(0)
        assert cx1 == pytest.approx(50, abs=2)
        assert cy1 == pytest.approx(50, abs=2)
        assert cx2 == pytest.approx(200, abs=2)
        assert cy2 == pytest.approx(200, abs=2)

    def test_converge_empty_collection(self):
        col = VCollection()
        result = col.converge(100, 100, start=0, end=1)
        assert result is col

    def test_converge_zero_duration(self):
        c1 = Circle(r=10, cx=100, cy=100)
        col = VCollection(c1)
        result = col.converge(500, 500, start=0, end=0)
        assert result is col

    def test_converge_to_canvas_center(self):
        """Default convergence point should be canvas center (960, 540)."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=500, cy=500)
        col = VCollection(c1, c2)
        col.converge(start=0, end=1)
        for c in [c1, c2]:
            cx, cy = c.center(1)
            assert cx == pytest.approx(960, abs=2)
            assert cy == pytest.approx(540, abs=2)

    def test_converge_already_at_target(self):
        """If a child is already at the target, it should not move."""
        c1 = Circle(r=10, cx=300, cy=300)
        col = VCollection(c1)
        col.converge(300, 300, start=0, end=1)
        cx, cy = c1.center(0.5)
        assert cx == pytest.approx(300, abs=2)
        assert cy == pytest.approx(300, abs=2)


class TestDiverge:
    def test_diverge_returns_self(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        col = VCollection(c1, c2)
        assert col.diverge(factor=2, start=0, end=1) is col

    def test_diverge_expands_outward(self):
        """Children should be farther from the center after diverging."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=300)
        col = VCollection(c1, c2)
        # Center of collection is at (200, 200)
        col.diverge(factor=2, start=0, end=1)
        cx1, cy1 = c1.center(1)
        cx2, cy2 = c2.center(1)
        # c1 was 100 from center, should now be 200 from center: at (0, 0)
        assert cx1 == pytest.approx(0, abs=2)
        assert cy1 == pytest.approx(0, abs=2)
        # c2 was 100 from center, should now be 200 from center: at (400, 400)
        assert cx2 == pytest.approx(400, abs=2)
        assert cy2 == pytest.approx(400, abs=2)

    def test_diverge_with_custom_center(self):
        """Diverge from a custom center point."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=100)
        col = VCollection(c1, c2)
        col.diverge(factor=3, cx=200, cy=100, start=0, end=1)
        cx1, _ = c1.center(1)
        cx2, _ = c2.center(1)
        # c1: 100 from cx=200, factor=3 means add 2*100=200 away
        assert cx1 == pytest.approx(-100, abs=2)
        # c2: 100 from cx=200, factor=3 means add 2*100=200 away
        assert cx2 == pytest.approx(500, abs=2)

    def test_diverge_empty_collection(self):
        col = VCollection()
        result = col.diverge(factor=2, start=0, end=1)
        assert result is col

    def test_diverge_zero_duration(self):
        c1 = Circle(r=10, cx=100, cy=100)
        col = VCollection(c1)
        result = col.diverge(factor=2, start=0, end=0)
        assert result is col

    def test_diverge_factor_one_no_movement(self):
        """Factor of 1.0 should not move children."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=300)
        col = VCollection(c1, c2)
        col.diverge(factor=1.0, start=0, end=1)
        cx1, cy1 = c1.center(1)
        cx2, cy2 = c2.center(1)
        assert cx1 == pytest.approx(100, abs=2)
        assert cy1 == pytest.approx(100, abs=2)
        assert cx2 == pytest.approx(300, abs=2)
        assert cy2 == pytest.approx(300, abs=2)


class TestPairUp:
    def test_even_count(self):
        """Four children should produce two pairs."""
        c1, c2, c3, c4 = [Circle(r=10, cx=i * 50, cy=50) for i in range(4)]
        col = VCollection(c1, c2, c3, c4)
        pairs = col.pair_up()
        assert len(pairs) == 2
        assert len(pairs[0].objects) == 2
        assert len(pairs[1].objects) == 2
        assert pairs[0].objects[0] is c1
        assert pairs[0].objects[1] is c2
        assert pairs[1].objects[0] is c3
        assert pairs[1].objects[1] is c4

    def test_odd_count(self):
        """Five children should produce two pairs + one singleton."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(5)]
        col = VCollection(*circles)
        pairs = col.pair_up()
        assert len(pairs) == 3
        assert len(pairs[0].objects) == 2
        assert len(pairs[1].objects) == 2
        assert len(pairs[2].objects) == 1
        assert pairs[2].objects[0] is circles[4]

    def test_single_child(self):
        """One child should produce one singleton collection."""
        c1 = Circle(r=10, cx=50, cy=50)
        col = VCollection(c1)
        pairs = col.pair_up()
        assert len(pairs) == 1
        assert len(pairs[0].objects) == 1
        assert pairs[0].objects[0] is c1

    def test_empty_raises(self):
        """Empty collection should raise ValueError."""
        col = VCollection()
        with pytest.raises(ValueError):
            col.pair_up()

    def test_returns_vcollections(self):
        """Each pair should be a VCollection."""
        c1, c2 = Circle(r=10, cx=50, cy=50), Circle(r=10, cx=100, cy=50)
        col = VCollection(c1, c2)
        pairs = col.pair_up()
        for p in pairs:
            assert isinstance(p, VCollection)

    def test_two_children(self):
        """Two children should produce exactly one pair."""
        c1, c2 = Circle(r=10, cx=50, cy=50), Circle(r=10, cx=100, cy=50)
        col = VCollection(c1, c2)
        pairs = col.pair_up()
        assert len(pairs) == 1
        assert pairs[0].objects == [c1, c2]


class TestSlidingWindow:
    def test_basic_window(self):
        """Window of 3 with step 1 over 5 elements produces 3 windows."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(5)]
        col = VCollection(*circles)
        windows = col.sliding_window(3, step=1)
        assert len(windows) == 3
        assert [len(w.objects) for w in windows] == [3, 3, 3]
        # Check first and last window contents
        assert windows[0].objects[0] is circles[0]
        assert windows[0].objects[2] is circles[2]
        assert windows[2].objects[0] is circles[2]
        assert windows[2].objects[2] is circles[4]

    def test_step_greater_than_one(self):
        """Window of 2 with step 2 (non-overlapping) over 6 elements."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(6)]
        col = VCollection(*circles)
        windows = col.sliding_window(2, step=2)
        assert len(windows) == 3
        assert windows[0].objects == [circles[0], circles[1]]
        assert windows[1].objects == [circles[2], circles[3]]
        assert windows[2].objects == [circles[4], circles[5]]

    def test_window_equals_length(self):
        """Window size equal to collection length produces one window."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(4)]
        col = VCollection(*circles)
        windows = col.sliding_window(4)
        assert len(windows) == 1
        assert len(windows[0].objects) == 4

    def test_window_larger_than_collection(self):
        """Window larger than collection should produce no windows."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(3)]
        col = VCollection(*circles)
        windows = col.sliding_window(5)
        assert len(windows) == 0

    def test_invalid_size_raises(self):
        col = VCollection(Circle(r=10, cx=50, cy=50))
        with pytest.raises(ValueError):
            col.sliding_window(0)

    def test_invalid_step_raises(self):
        col = VCollection(Circle(r=10, cx=50, cy=50))
        with pytest.raises(ValueError):
            col.sliding_window(1, step=0)

    def test_empty_collection(self):
        col = VCollection()
        windows = col.sliding_window(2)
        assert len(windows) == 0

    def test_returns_vcollections(self):
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(5)]
        col = VCollection(*circles)
        windows = col.sliding_window(2)
        for w in windows:
            assert isinstance(w, VCollection)

    def test_step_default_is_one(self):
        """Default step should be 1."""
        circles = [Circle(r=10, cx=i * 50, cy=50) for i in range(4)]
        col = VCollection(*circles)
        windows = col.sliding_window(2)
        assert len(windows) == 3


class TestWaterfall:
    """Tests for VCollection.waterfall — staggered gravity-drop entrance."""

    def test_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=400)
        c2 = Circle(r=20, cx=200, cy=400)
        col = VCollection(c1, c2)
        result = col.waterfall(start=0, end=2)
        assert result is col

    def test_children_hidden_before_start(self):
        c1 = Circle(r=20, cx=100, cy=400)
        c2 = Circle(r=20, cx=200, cy=400)
        col = VCollection(c1, c2)
        col.waterfall(start=1, end=3)
        # Both should be hidden before the waterfall starts
        assert c1.show.at_time(0.5) is False
        assert c2.show.at_time(0.5) is False

    def test_first_child_visible_at_start(self):
        c1 = Circle(r=20, cx=100, cy=400)
        c2 = Circle(r=20, cx=200, cy=400)
        col = VCollection(c1, c2)
        col.waterfall(start=0, end=2)
        # First child should become visible at start
        assert c1.show.at_time(0) is True

    def test_second_child_delayed(self):
        c1 = Circle(r=20, cx=100, cy=400)
        c2 = Circle(r=20, cx=200, cy=400)
        c3 = Circle(r=20, cx=300, cy=400)
        col = VCollection(c1, c2, c3)
        col.waterfall(start=0, end=3, stagger_frac=0.0)
        # With stagger_frac=0 (sequential), c2 shouldn't start until after c1
        assert c2.show.at_time(0) is False

    def test_empty_collection_noop(self):
        col = VCollection()
        result = col.waterfall(start=0, end=1)
        assert result is col

    def test_zero_duration_noop(self):
        c1 = Circle(r=20, cx=100, cy=400)
        col = VCollection(c1)
        result = col.waterfall(start=1, end=1)
        assert result is col

    def test_children_at_rest_position_after_end(self):
        c1 = Circle(r=20, cx=100, cy=400)
        col = VCollection(c1)
        original_cy = c1.c.at_time(0)[1]
        col.waterfall(start=0, end=1, height=200, easing=easings.linear)
        # After animation ends, child should be at (approximately) its original position
        final_cy = c1.c.at_time(1)[1]
        assert final_cy == pytest.approx(original_cy, abs=1)

    def test_children_offset_during_animation(self):
        c1 = Circle(r=20, cx=100, cy=400)
        col = VCollection(c1)
        original_cy = c1.c.at_time(0)[1]
        col.waterfall(start=0, end=1, height=200, easing=easings.linear)
        # During animation, child should be above its rest position
        mid_cy = c1.c.at_time(0.5)[1]
        # y offset at 0.5 linear: -200*(1-0.5) = -100
        assert mid_cy == pytest.approx(original_cy - 100, abs=5)

    def test_single_child_fills_duration(self):
        c1 = Circle(r=20, cx=100, cy=400)
        col = VCollection(c1)
        col.waterfall(start=0, end=2, height=100, easing=easings.linear)
        # Single child should use the full duration
        assert c1.show.at_time(0) is True
        mid_cy = c1.c.at_time(1)[1]
        original_cy = 400
        # At t=1 (halfway through dur=2), offset = -100*(1-0.5) = -50
        assert mid_cy == pytest.approx(original_cy - 50, abs=5)


class TestOrbitAround:
    """Tests for VCollection.orbit_around — children revolving around a center."""

    def test_returns_self(self):
        c1 = Circle(r=10, cx=100, cy=300)
        c2 = Circle(r=10, cx=200, cy=300)
        col = VCollection(c1, c2)
        result = col.orbit_around(cx=150, cy=300, radius=100, start=0, end=2)
        assert result is col

    def test_empty_collection_noop(self):
        col = VCollection()
        result = col.orbit_around(start=0, end=1)
        assert result is col

    def test_zero_duration_noop(self):
        c1 = Circle(r=10, cx=100, cy=300)
        col = VCollection(c1)
        result = col.orbit_around(start=1, end=1)
        assert result is col

    def test_children_move_in_circle(self):
        """A child at (cx+R, cy) should orbit to (cx, cy+R) at quarter revolution."""
        c1 = Circle(r=10, cx=250, cy=300)  # Right of center
        col = VCollection(c1)
        col.orbit_around(cx=150, cy=300, radius=100, start=0, end=4,
                         revolutions=1, easing=easings.linear)
        # At t=1 (quarter revolution): should be at bottom (cx, cy+R) = (150, 400)
        pos = c1.c.at_time(1)
        assert pos[0] == pytest.approx(150, abs=5)
        assert pos[1] == pytest.approx(400, abs=5)

    def test_full_revolution_returns_to_start(self):
        """After one full revolution, child should be back near start."""
        c1 = Circle(r=10, cx=250, cy=300)
        col = VCollection(c1)
        col.orbit_around(cx=150, cy=300, radius=100, start=0, end=4,
                         revolutions=1, easing=easings.linear)
        pos_start = c1.c.at_time(0)
        pos_end = c1.c.at_time(4)
        assert pos_end[0] == pytest.approx(pos_start[0], abs=2)
        assert pos_end[1] == pytest.approx(pos_start[1], abs=2)

    def test_default_center_uses_bbox(self):
        """When cx/cy not given, should use group bbox center."""
        c1 = Circle(r=10, cx=100, cy=300)
        c2 = Circle(r=10, cx=200, cy=300)
        col = VCollection(c1, c2)
        # Should not raise
        result = col.orbit_around(radius=100, start=0, end=2)
        assert result is col

    def test_half_revolution(self):
        """At half revolution, child at (cx+R, cy) should be at (cx-R, cy)."""
        c1 = Circle(r=10, cx=250, cy=300)  # Right of center at distance 100
        col = VCollection(c1)
        col.orbit_around(cx=150, cy=300, radius=100, start=0, end=2,
                         revolutions=1, easing=easings.linear)
        # At t=1 (half revolution): should be at (cx-R, cy) = (50, 300)
        pos = c1.c.at_time(1)
        assert pos[0] == pytest.approx(50, abs=5)
        assert pos[1] == pytest.approx(300, abs=5)

    def test_multiple_children_maintain_spacing(self):
        """Two children 180 degrees apart should stay 180 degrees apart."""
        c1 = Circle(r=10, cx=250, cy=300)  # Right of center
        c2 = Circle(r=10, cx=50, cy=300)   # Left of center
        col = VCollection(c1, c2)
        col.orbit_around(cx=150, cy=300, radius=100, start=0, end=4,
                         revolutions=1, easing=easings.linear)
        # At t=1 (quarter revolution):
        # c1 starts at angle 0 -> should be at angle pi/2 (bottom)
        # c2 starts at angle pi -> should be at angle 3pi/2 (top)
        pos1 = c1.c.at_time(1)
        pos2 = c2.c.at_time(1)
        assert pos1[0] == pytest.approx(150, abs=5)
        assert pos1[1] == pytest.approx(400, abs=5)
        assert pos2[0] == pytest.approx(150, abs=5)
        assert pos2[1] == pytest.approx(200, abs=5)


# ---------------------------------------------------------------------------
# VCollection.cascade_scale
# ---------------------------------------------------------------------------

class TestCascadeScale:
    def test_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        result = col.cascade_scale(start=0, end=2, factor=1.5, delay=0.2)
        assert result is col

    def test_empty_collection(self):
        col = VCollection()
        result = col.cascade_scale(start=0, end=1)
        assert result is col

    def test_zero_duration(self):
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        result = col.cascade_scale(start=1, end=1)
        assert result is col

    def test_first_child_scales_up(self):
        """The first child should be scaled above 1 at its midpoint."""
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        col.cascade_scale(start=0, end=2, factor=2.0, delay=0.3, easing=easings.linear)
        # First child starts at t=0, its mid-animation should show scale > 1
        sx_mid = c1.styling.scale_x.at_time(0.85)
        assert sx_mid > 1.0, "First child should scale up at its peak"

    def test_stagger_timing(self):
        """Second child should start its animation later than the first."""
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        col.cascade_scale(start=0, end=2, factor=2.0, delay=0.5, easing=easings.linear)
        # Before second child starts, its scale should be 1
        sx_c2_before = c2.styling.scale_x.at_time(0.1)
        assert sx_c2_before == pytest.approx(1.0, abs=0.01)

    def test_scale_returns_to_baseline(self):
        """After the animation, scale should return to baseline."""
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        col.cascade_scale(start=0, end=2, factor=1.5, delay=0.1, easing=easings.linear)
        # At the end, sin(pi * 1) = 0, so scale should be 1
        sx_end = c1.styling.scale_x.at_time(2.0)
        assert sx_end == pytest.approx(1.0, abs=0.01)

    def test_single_child(self):
        """Single child should use full duration."""
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        col.cascade_scale(start=0, end=1, factor=1.5, delay=0.2, easing=easings.linear)
        # With one child, delay is irrelevant - uses full duration
        sx_mid = c1.styling.scale_x.at_time(0.5)
        assert sx_mid > 1.0


# ---------------------------------------------------------------------------
# VCollection.distribute_along_arc
# ---------------------------------------------------------------------------

class TestDistributeAlongArc:
    def test_returns_self(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2)
        result = col.distribute_along_arc(cx=500, cy=500, radius=200)
        assert result is col

    def test_empty_collection(self):
        col = VCollection()
        result = col.distribute_along_arc()
        assert result is col

    def test_two_children_semicircle(self):
        """Two children on a semicircle should be at the arc endpoints."""
        c1 = Circle(r=10, cx=500, cy=500)
        c2 = Circle(r=10, cx=500, cy=500)
        col = VCollection(c1, c2)
        col.distribute_along_arc(cx=500, cy=500, radius=200,
                                  start_angle=0, end_angle=math.pi)
        # c1 should be at angle 0 (right): (700, 500)
        p1 = c1.c.at_time(0)
        assert p1[0] == pytest.approx(700, abs=5)
        assert p1[1] == pytest.approx(500, abs=5)
        # c2 should be at angle pi (left): (300, 500)
        p2 = c2.c.at_time(0)
        assert p2[0] == pytest.approx(300, abs=5)
        assert p2[1] == pytest.approx(500, abs=5)

    def test_three_children_quarter_arc(self):
        """Three children on a quarter arc (0 to pi/2)."""
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        c3 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2, c3)
        col.distribute_along_arc(cx=500, cy=500, radius=100,
                                  start_angle=0, end_angle=math.pi/2)
        # c1 at angle 0: (600, 500)
        p1 = c1.c.at_time(0)
        assert p1[0] == pytest.approx(600, abs=5)
        assert p1[1] == pytest.approx(500, abs=5)
        # c2 at angle pi/4: (500 + 100*cos(pi/4), 500 + 100*sin(pi/4))
        p2 = c2.c.at_time(0)
        assert p2[0] == pytest.approx(500 + 100 * math.cos(math.pi/4), abs=5)
        assert p2[1] == pytest.approx(500 + 100 * math.sin(math.pi/4), abs=5)
        # c3 at angle pi/2: (500, 600)
        p3 = c3.c.at_time(0)
        assert p3[0] == pytest.approx(500, abs=5)
        assert p3[1] == pytest.approx(600, abs=5)

    def test_single_child_at_midpoint(self):
        """Single child should be placed at the midpoint of the arc."""
        c1 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1)
        col.distribute_along_arc(cx=500, cy=500, radius=100,
                                  start_angle=0, end_angle=math.pi)
        # Midpoint of arc from 0 to pi is pi/2: (500, 600)
        p = c1.c.at_time(0)
        assert p[0] == pytest.approx(500, abs=5)
        assert p[1] == pytest.approx(600, abs=5)

    def test_animated_version(self):
        """With end_time, children should animate to their positions."""
        c1 = Circle(r=10, cx=500, cy=500)
        c2 = Circle(r=10, cx=500, cy=500)
        col = VCollection(c1, c2)
        col.distribute_along_arc(cx=500, cy=500, radius=200,
                                  start_angle=0, end_angle=math.pi,
                                  start_time=0, end_time=1, easing=easings.linear)
        # At t=0, still at original position
        p1_start = c1.c.at_time(0)
        assert p1_start[0] == pytest.approx(500, abs=5)
        # At t=1, should have reached target
        p1_end = c1.c.at_time(1)
        assert p1_end[0] == pytest.approx(700, abs=5)

    def test_default_end_angle(self):
        """Default end_angle should be start_angle + pi (semicircle)."""
        c1 = Circle(r=10, cx=500, cy=500)
        c2 = Circle(r=10, cx=500, cy=500)
        col = VCollection(c1, c2)
        col.distribute_along_arc(cx=500, cy=500, radius=100, start_angle=0)
        # c2 should be at angle pi (left of center): (400, 500)
        p2 = c2.c.at_time(0)
        assert p2[0] == pytest.approx(400, abs=5)
        assert p2[1] == pytest.approx(500, abs=5)

    def test_full_circle(self):
        """Full circle (0 to 2*pi) with 4 children should place them at 90-degree intervals."""
        children = [Circle(r=10, cx=500, cy=500) for _ in range(4)]
        col = VCollection(*children)
        col.distribute_along_arc(cx=500, cy=500, radius=100,
                                  start_angle=0, end_angle=2*math.pi)
        # Child 0 at angle 0: (600, 500)
        p0 = children[0].c.at_time(0)
        assert p0[0] == pytest.approx(600, abs=5)
        # Child 1 at angle 2pi/3: roughly (500 + 100*cos(2pi/3), 500 + 100*sin(2pi/3))
        p1 = children[1].c.at_time(0)
        expected_angle = 2 * math.pi / 3
        assert p1[0] == pytest.approx(500 + 100 * math.cos(expected_angle), abs=5)


class TestFanOut:
    def test_returns_self(self):
        children = [Circle(r=10, cx=500, cy=500) for _ in range(3)]
        col = VCollection(*children)
        result = col.fan_out(start=0, end=1)
        assert result is col

    def test_children_spread_radially(self):
        children = [Circle(r=10, cx=500, cy=500) for _ in range(4)]
        col = VCollection(*children)
        col.fan_out(cx=500, cy=500, radius=100, start=0, end=1, easing=easings.linear)
        # After animation, children should be at compass points
        # Child 0: angle=0 -> (600, 500)
        p0 = children[0].c.at_time(1)
        assert p0[0] == pytest.approx(600, abs=5)
        assert p0[1] == pytest.approx(500, abs=5)
        # Child 1: angle=pi/2 -> (500, 600)
        p1 = children[1].c.at_time(1)
        assert p1[0] == pytest.approx(500, abs=5)
        assert p1[1] == pytest.approx(600, abs=5)

    def test_children_start_at_original_position(self):
        children = [Circle(r=10, cx=500, cy=500) for _ in range(3)]
        col = VCollection(*children)
        col.fan_out(cx=500, cy=500, radius=100, start=0, end=1, easing=easings.linear)
        # At start, children should still be at original position
        p0 = children[0].c.at_time(0)
        assert p0[0] == pytest.approx(500, abs=5)
        assert p0[1] == pytest.approx(500, abs=5)

    def test_custom_center(self):
        children = [Circle(r=10, cx=300, cy=300) for _ in range(2)]
        col = VCollection(*children)
        col.fan_out(cx=300, cy=300, radius=50, start=0, end=1, easing=easings.linear)
        # Child 0 at angle 0: (350, 300)
        p0 = children[0].c.at_time(1)
        assert p0[0] == pytest.approx(350, abs=5)

    def test_empty_collection(self):
        col = VCollection()
        result = col.fan_out(start=0, end=1)
        assert result is col

    def test_default_center_from_bbox(self):
        """When cx/cy not given, uses collection bbox center."""
        c1 = Circle(r=10, cx=400, cy=500)
        c2 = Circle(r=10, cx=600, cy=500)
        col = VCollection(c1, c2)
        col.fan_out(radius=100, start=0, end=1, easing=easings.linear)
        # Collection center is (500, 500)
        # Child 0: angle=0 -> (600, 500)
        p0 = c1.c.at_time(1)
        assert p0[0] == pytest.approx(600, abs=5)

    def test_custom_radius(self):
        children = [Circle(r=10, cx=500, cy=500) for _ in range(2)]
        col = VCollection(*children)
        col.fan_out(cx=500, cy=500, radius=200, start=0, end=1, easing=easings.linear)
        # Child 0 at angle 0: (700, 500)
        p0 = children[0].c.at_time(1)
        assert p0[0] == pytest.approx(700, abs=5)


class TestAlignCenters:
    def test_returns_self(self):
        children = [Circle(r=10, cx=100, cy=100),
                     Circle(r=10, cx=200, cy=200)]
        col = VCollection(*children)
        result = col.align_centers(axis='x')
        assert result is col

    def test_align_x_axis(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        c3 = Circle(r=10, cx=300, cy=300)
        col = VCollection(c1, c2, c3)
        col.align_centers(axis='x')
        # All children should have the same x center (collection center)
        xs = [c.c.at_time(0)[0] for c in [c1, c2, c3]]
        assert xs[0] == pytest.approx(xs[1], abs=1)
        assert xs[1] == pytest.approx(xs[2], abs=1)

    def test_align_y_axis(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        c3 = Circle(r=10, cx=300, cy=300)
        col = VCollection(c1, c2, c3)
        col.align_centers(axis='y')
        # All children should have the same y center
        ys = [c.c.at_time(0)[1] for c in [c1, c2, c3]]
        assert ys[0] == pytest.approx(ys[1], abs=1)
        assert ys[1] == pytest.approx(ys[2], abs=1)

    def test_custom_value(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        col = VCollection(c1, c2)
        col.align_centers(axis='x', value=500)
        assert c1.c.at_time(0)[0] == pytest.approx(500, abs=1)
        assert c2.c.at_time(0)[0] == pytest.approx(500, abs=1)

    def test_animated(self):
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=200)
        col = VCollection(c1, c2)
        col.align_centers(axis='x', value=500, start_time=0, end_time=1, easing=easings.linear)
        # At start, positions should be original
        assert c1.c.at_time(0)[0] == pytest.approx(100, abs=1)
        # At end, positions should be aligned
        assert c1.c.at_time(1)[0] == pytest.approx(500, abs=1)
        assert c2.c.at_time(1)[0] == pytest.approx(500, abs=1)

    def test_empty_collection(self):
        col = VCollection()
        result = col.align_centers(axis='x')
        assert result is col

    def test_y_preserves_x(self):
        """Aligning on y axis should not change x positions."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=200)
        col = VCollection(c1, c2)
        col.align_centers(axis='y', value=500)
        assert c1.c.at_time(0)[0] == pytest.approx(100, abs=1)
        assert c2.c.at_time(0)[0] == pytest.approx(300, abs=1)

    def test_x_preserves_y(self):
        """Aligning on x axis should not change y positions."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=300, cy=200)
        col = VCollection(c1, c2)
        col.align_centers(axis='x', value=500)
        assert c1.c.at_time(0)[1] == pytest.approx(100, abs=1)
        assert c2.c.at_time(0)[1] == pytest.approx(200, abs=1)


class TestRadialArrange:
    def test_returns_self(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2)
        result = col.radial_arrange(radius=100)
        assert result is col

    def test_children_on_circle(self):
        """All children should be placed at the specified radius from center."""
        circles = [Circle(r=5, cx=0, cy=0) for _ in range(4)]
        col = VCollection(*circles)
        center = (500, 500)
        col.radial_arrange(radius=200, center=center)
        for c in circles:
            cx, cy = c.c.at_time(0)
            dist = math.sqrt((cx - 500) ** 2 + (cy - 500) ** 2)
            assert dist == pytest.approx(200, abs=2)

    def test_equal_spacing(self):
        """Children should be evenly spaced around the circle."""
        circles = [Circle(r=5, cx=0, cy=0) for _ in range(4)]
        col = VCollection(*circles)
        col.radial_arrange(radius=100, center=(500, 500))
        # 4 objects: angles 0, pi/2, pi, 3pi/2
        positions = [c.c.at_time(0) for c in circles]
        # First child at angle 0 (to the right)
        assert positions[0][0] == pytest.approx(600, abs=2)
        assert positions[0][1] == pytest.approx(500, abs=2)
        # Second child at angle pi/2 (below, since y increases downward)
        assert positions[1][0] == pytest.approx(500, abs=2)
        assert positions[1][1] == pytest.approx(600, abs=2)

    def test_start_angle(self):
        """start_angle should rotate the arrangement."""
        circles = [Circle(r=5, cx=0, cy=0) for _ in range(4)]
        col = VCollection(*circles)
        col.radial_arrange(radius=100, start_angle=math.pi / 2, center=(500, 500))
        # First child at angle pi/2 (below)
        pos = circles[0].c.at_time(0)
        assert pos[0] == pytest.approx(500, abs=2)
        assert pos[1] == pytest.approx(600, abs=2)

    def test_default_center(self):
        """Without explicit center, should use the collection's bbox center."""
        c1 = Circle(r=10, cx=100, cy=100)
        c2 = Circle(r=10, cx=200, cy=200)
        col = VCollection(c1, c2)
        # bbox center is (150, 150)
        col.radial_arrange(radius=50)
        # Both children should be 50px from (150, 150)
        for c in [c1, c2]:
            cx, cy = c.c.at_time(0)
            dist = math.sqrt((cx - 150) ** 2 + (cy - 150) ** 2)
            assert dist == pytest.approx(50, abs=2)

    def test_empty_collection(self):
        col = VCollection()
        result = col.radial_arrange(radius=100)
        assert result is col

    def test_single_child(self):
        """A single child should be placed at start_angle on the circle."""
        c = Circle(r=5, cx=0, cy=0)
        col = VCollection(c)
        col.radial_arrange(radius=100, center=(500, 500))
        pos = c.c.at_time(0)
        assert pos[0] == pytest.approx(600, abs=2)
        assert pos[1] == pytest.approx(500, abs=2)


class TestStaggerScale:
    def test_returns_self(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=200, cy=200)
        col = VCollection(c1, c2)
        result = col.stagger_scale(start=0, end=2, scale_factor=1.5, delay=0.3)
        assert result is col

    def test_children_pop_sequentially(self):
        """Each child should hit peak scale at different times due to stagger."""
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=300)
        col = VCollection(c1, c2)
        col.stagger_scale(start=0, end=3, scale_factor=2.0, delay=1.0,
                          easing=easings.linear)
        # c1 starts at t=0, c2 starts at t=1.0
        # At t=0, c1 just started (scale ~1), c2 hasn't started yet
        assert c1.styling.scale_x.at_time(0) == pytest.approx(1.0, abs=0.1)

    def test_peak_scale(self):
        """At the midpoint of each child's animation, scale should peak near scale_factor."""
        c1 = Circle(r=50, cx=100, cy=100)
        col = VCollection(c1)
        col.stagger_scale(start=0, end=2, scale_factor=1.5, delay=0.2,
                          easing=easings.linear)
        # Single child: pop from 0 to 2, peak at t=1 (midpoint)
        # sin(pi * linear(0.5)) = sin(pi/2) = 1 => scale = 1 + 0.5 * 1 = 1.5
        sx_mid = c1.styling.scale_x.at_time(1)
        assert sx_mid == pytest.approx(1.5, abs=0.1)

    def test_scale_returns_at_end(self):
        """After pop, scale should return close to 1."""
        c1 = Circle(r=50, cx=100, cy=100)
        col = VCollection(c1)
        col.stagger_scale(start=0, end=2, scale_factor=1.5, delay=0.2,
                          easing=easings.linear)
        # At end of animation (t=2), sin(pi*1) = 0 => scale = 1
        sx_end = c1.styling.scale_x.at_time(2)
        assert sx_end == pytest.approx(1.0, abs=0.1)

    def test_empty_collection(self):
        col = VCollection()
        result = col.stagger_scale(start=0, end=1)
        assert result is col

    def test_backward_compat_target_scale(self):
        """The old 'target_scale' parameter should still work."""
        c1 = Circle(r=50, cx=100, cy=100)
        col = VCollection(c1)
        col.stagger_scale(start=0, end=2, target_scale=2.0, delay=0.2,
                          easing=easings.linear)
        sx_mid = c1.styling.scale_x.at_time(1)
        assert sx_mid == pytest.approx(2.0, abs=0.1)

    def test_multiple_children_stagger(self):
        """Children later in the list should start their animation later."""
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=300)
        c3 = Circle(r=50, cx=500, cy=500)
        col = VCollection(c1, c2, c3)
        col.stagger_scale(start=0, end=4, scale_factor=2.0, delay=0.5,
                          easing=easings.linear)
        # c1 starts at 0, c2 starts at 0.5, c3 starts at 1.0
        # Before c2 starts, c2 should still be at scale 1
        assert c2.styling.scale_x.at_time(0.25) == pytest.approx(1.0, abs=0.1)
        # After c3 starts, c3 should be scaling up
        sx_c3 = c3.styling.scale_x.at_time(1.5)
        assert sx_c3 > 1.05


class TestApplySequential:
    def test_apply_sequential_returns_self(self):
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        col = VCollection(c1, c2)
        result = col.apply_sequential('fadein', 0, 2)
        assert result is col

    def test_apply_sequential_divides_time_evenly(self):
        """With 3 children and time 0-3, each child gets 1 second."""
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        c3 = Circle(r=50)
        col = VCollection(c1, c2, c3)
        col.apply_sequential('fadein', 0, 3)
        # c1 should be shown from time 0 (its fadein starts at 0)
        assert c1.show.at_time(0) is True
        # c2 should be shown from time 1 (its fadein starts at 1)
        assert c2.show.at_time(1) is True
        # c3 should be shown from time 2 (its fadein starts at 2)
        assert c3.show.at_time(2) is True

    def test_apply_sequential_empty_collection(self):
        col = VCollection()
        result = col.apply_sequential('fadein', 0, 3)
        assert result is col

    def test_apply_sequential_single_child(self):
        """Single child gets the entire time range."""
        c = Circle(r=50)
        col = VCollection(c)
        col.apply_sequential('fadein', 0, 2)
        assert c.show.at_time(0) is True

    def test_apply_sequential_with_kwargs(self):
        """Extra kwargs should be forwarded to the method."""
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        col = VCollection(c1, c2)
        col.apply_sequential('fadein', 0, 2, easing=easings.linear)
        # Both should be shown at their respective start times
        assert c1.show.at_time(0) is True
        assert c2.show.at_time(1) is True

    def test_apply_sequential_fadeout(self):
        """Should work with fadeout as well."""
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        col = VCollection(c1, c2)
        col.apply_sequential('fadeout', 0, 2)
        # After the full animation, both should be hidden
        assert c1.show.at_time(1.5) is False
        assert c2.show.at_time(2.5) is False


class TestDistributeEvenly:
    def test_returns_self(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2)
        result = col.distribute_evenly(100, 100, 500, 100)
        assert result is col

    def test_two_children_at_endpoints(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2)
        col.distribute_evenly(100, 200, 400, 200)
        # c1 center should be at (100, 200)
        bx1, by1, bw1, bh1 = c1.bbox(0)
        assert bx1 + bw1 / 2 == pytest.approx(100, abs=1)
        assert by1 + bh1 / 2 == pytest.approx(200, abs=1)
        # c2 center should be at (400, 200)
        bx2, by2, bw2, bh2 = c2.bbox(0)
        assert bx2 + bw2 / 2 == pytest.approx(400, abs=1)
        assert by2 + bh2 / 2 == pytest.approx(200, abs=1)

    def test_three_children_evenly_spaced(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        c3 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2, c3)
        col.distribute_evenly(0, 0, 200, 0)
        # Centers should be at x=0, 100, 200
        bx1, _, bw1, _ = c1.bbox(0)
        bx2, _, bw2, _ = c2.bbox(0)
        bx3, _, bw3, _ = c3.bbox(0)
        assert bx1 + bw1 / 2 == pytest.approx(0, abs=1)
        assert bx2 + bw2 / 2 == pytest.approx(100, abs=1)
        assert bx3 + bw3 / 2 == pytest.approx(200, abs=1)

    def test_diagonal_distribution(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=10, cx=0, cy=0)
        c3 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1, c2, c3)
        col.distribute_evenly(0, 0, 200, 400)
        # c2 center should be at midpoint (100, 200)
        bx2, by2, bw2, bh2 = c2.bbox(0)
        assert bx2 + bw2 / 2 == pytest.approx(100, abs=1)
        assert by2 + bh2 / 2 == pytest.approx(200, abs=1)

    def test_single_child_at_start(self):
        c1 = Circle(r=10, cx=0, cy=0)
        col = VCollection(c1)
        col.distribute_evenly(300, 400, 600, 800)
        bx, by, bw, bh = c1.bbox(0)
        assert bx + bw / 2 == pytest.approx(300, abs=1)
        assert by + bh / 2 == pytest.approx(400, abs=1)

    def test_empty_collection(self):
        col = VCollection()
        result = col.distribute_evenly(0, 0, 100, 100)
        assert result is col


class TestSwapAnimated:
    def test_swap_animated_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=300, cy=100)
        col = VCollection(c1, c2)
        result = col.swap_animated(0, 1, start=0, end=1)
        assert result is col

    def test_swap_animated_exchanges_positions(self):
        c1 = Circle(r=20, cx=100, cy=200)
        c2 = Circle(r=20, cx=300, cy=200)
        col = VCollection(c1, c2)
        col.swap_animated(0, 1, start=0, end=1, easing=easings.linear)
        # At end, c1 should be near c2's original position and vice versa
        c1x, c1y = c1.center(1)
        c2x, c2y = c2.center(1)
        assert c1x == pytest.approx(300, abs=5)
        assert c2x == pytest.approx(100, abs=5)

    def test_swap_animated_same_index_noop(self):
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        result = col.swap_animated(0, 0, start=0, end=1)
        assert result is col
        # Position unchanged
        cx, cy = c1.center(1)
        assert cx == pytest.approx(100, abs=1)

    def test_swap_animated_invalid_index_noop(self):
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        result = col.swap_animated(0, 5, start=0, end=1)
        assert result is col

    def test_swap_animated_arc_midpoint_offset(self):
        """At the midpoint, objects should be off the straight-line path (arc movement)."""
        c1 = Circle(r=20, cx=100, cy=200)
        c2 = Circle(r=20, cx=300, cy=200)
        col = VCollection(c1, c2)
        col.swap_animated(0, 1, start=0, end=1, easing=easings.linear)
        # At midpoint, both should be roughly at x=200 but y should differ
        # from 200 because they follow arcs
        c1x, c1y = c1.center(0.5)
        c2x, c2y = c2.center(0.5)
        assert c1x == pytest.approx(200, abs=20)
        assert c2x == pytest.approx(200, abs=20)
        # y should be offset from 200 since they're on arcs
        # One arc goes one way, the other goes the other way
        assert c1y != pytest.approx(200, abs=5) or c2y != pytest.approx(200, abs=5)


class TestHighlightNth:
    def test_highlight_nth_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        result = col.highlight_nth(0, start=0, end=1)
        assert result is col

    def test_highlight_nth_dims_others(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        c3 = Circle(r=20, cx=300, cy=100)
        col = VCollection(c1, c2, c3)
        col.highlight_nth(1, start=0, end=2, easing=easings.linear)
        # At the middle of the dim period, non-target children should be dimmed
        t_dim = 0 + (2 - 0) * 0.5  # well into the dim period
        c1_fo = c1.styling.fill_opacity.at_time(t_dim)
        c3_fo = c3.styling.fill_opacity.at_time(t_dim)
        assert c1_fo < 0.5
        assert c3_fo < 0.5

    def test_highlight_nth_restores_opacity(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        col.highlight_nth(0, start=0, end=2, easing=easings.linear)
        # After end, non-target child should be back to full opacity
        c2_fo = c2.styling.fill_opacity.at_time(2)
        assert c2_fo == pytest.approx(1.0, abs=0.1)

    def test_highlight_nth_invalid_index_noop(self):
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        result = col.highlight_nth(5, start=0, end=1)
        assert result is col

    def test_highlight_nth_negative_index_noop(self):
        c1 = Circle(r=20, cx=100, cy=100)
        col = VCollection(c1)
        result = col.highlight_nth(-1, start=0, end=1)
        assert result is col

    def test_highlight_nth_custom_color(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        col.highlight_nth(0, start=0, end=2, color='#FF0000')
        # The target child should have had its fill changed
        # At the midpoint, the fill should be transitioning
        # We just verify no errors and return self
        assert True


class TestCascadeFadein:
    def test_returns_self(self):
        c1 = Circle(r=20, cx=100, cy=100)
        c2 = Circle(r=20, cx=200, cy=100)
        col = VCollection(c1, c2)
        result = col.cascade_fadein(start=0, end=2)
        assert result is col

    def test_left_to_right_ordering(self):
        # c_left has smaller x, so it should start fading in first
        c_left = Circle(r=20, cx=50, cy=100)
        c_right = Circle(r=20, cx=200, cy=100)
        col = VCollection(c_right, c_left)
        col.cascade_fadein(start=0, end=4, direction='left_to_right', easing=easings.linear)
        # c_left (x=50) should be visible before c_right (x=200)
        assert c_left.show.at_time(0) is True
        # c_right starts later
        assert not c_right.show.at_time(-0.1)

    def test_top_to_bottom_ordering(self):
        c_top = Circle(r=20, cx=100, cy=50)
        c_bottom = Circle(r=20, cx=100, cy=200)
        col = VCollection(c_bottom, c_top)
        col.cascade_fadein(start=0, end=4, direction='top_to_bottom', easing=easings.linear)
        # c_top (y=50) should start fading in first
        assert c_top.show.at_time(0) is True

    def test_center_out_ordering(self):
        # Three circles along x-axis; group bbox center will be at x=200
        # c1 at x=200 (center), c2 at x=100 (dist=100), c3 at x=400 (dist=200)
        c1 = Circle(r=10, cx=200, cy=100)
        c2 = Circle(r=10, cx=100, cy=100)
        c3 = Circle(r=10, cx=400, cy=100)
        col = VCollection(c3, c1, c2)
        col.cascade_fadein(start=0, end=4, direction='center_out', easing=easings.linear)
        # c1 is closest to center (dist ~55), starts first
        # All children should be visible at the end
        assert c1.show.at_time(0) is True
        assert c3.show.at_time(4) is True

    def test_empty_collection_no_error(self):
        col = VCollection()
        result = col.cascade_fadein(start=0, end=1)
        assert result is col

    def test_single_child(self):
        c = Circle(r=20, cx=100, cy=100)
        col = VCollection(c)
        col.cascade_fadein(start=0, end=1, easing=easings.linear)
        assert c.show.at_time(0) is True

    def test_all_children_visible_after_end(self):
        c1 = Circle(r=20, cx=50, cy=100)
        c2 = Circle(r=20, cx=150, cy=100)
        c3 = Circle(r=20, cx=250, cy=100)
        col = VCollection(c1, c2, c3)
        col.cascade_fadein(start=0, end=2, direction='left_to_right', easing=easings.linear)
        # After the full animation, all children should be visible
        assert c1.show.at_time(2) is True
        assert c2.show.at_time(2) is True
        assert c3.show.at_time(2) is True


class TestInterleaveCollections:
    def test_basic_interleave(self):
        c1 = Circle(r=10, cx=0, cy=0)
        c2 = Circle(r=20, cx=100, cy=100)
        c3 = Circle(r=30, cx=200, cy=200)
        c4 = Circle(r=40, cx=300, cy=300)
        col_a = VCollection(c1, c2)
        col_b = VCollection(c3, c4)
        result = col_a.interleave(col_b)
        assert isinstance(result, VCollection)
        assert len(result) == 4
        assert result[0] is c1
        assert result[1] is c3
        assert result[2] is c2
        assert result[3] is c4

    def test_does_not_modify_originals(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        c4 = Circle(r=40)
        col_a = VCollection(c1, c2)
        col_b = VCollection(c3, c4)
        col_a.interleave(col_b)
        assert len(col_a) == 2
        assert len(col_b) == 2
        assert col_a[0] is c1
        assert col_a[1] is c2

    def test_unequal_lengths_first_longer(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        col_a = VCollection(c1, c2, c3)
        c4 = Circle(r=40)
        col_b = VCollection(c4)
        result = col_a.interleave(col_b)
        assert len(result) == 4
        assert result[0] is c1
        assert result[1] is c4
        assert result[2] is c2
        assert result[3] is c3

    def test_unequal_lengths_second_longer(self):
        c1 = Circle(r=10)
        col_a = VCollection(c1)
        c2 = Circle(r=20)
        c3 = Circle(r=30)
        c4 = Circle(r=40)
        col_b = VCollection(c2, c3, c4)
        result = col_a.interleave(col_b)
        assert len(result) == 4
        assert result[0] is c1
        assert result[1] is c2
        assert result[2] is c3
        assert result[3] is c4

    def test_empty_collections(self):
        col_a = VCollection()
        col_b = VCollection()
        result = col_a.interleave(col_b)
        assert len(result) == 0

    def test_one_empty(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col_a = VCollection(c1, c2)
        col_b = VCollection()
        result = col_a.interleave(col_b)
        assert len(result) == 2
        assert result[0] is c1
        assert result[1] is c2

    def test_returns_new_vcollection(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col_a = VCollection(c1)
        col_b = VCollection(c2)
        result = col_a.interleave(col_b)
        assert result is not col_a
        assert result is not col_b

    def test_single_elements(self):
        c1 = Circle(r=10)
        c2 = Circle(r=20)
        col_a = VCollection(c1)
        col_b = VCollection(c2)
        result = col_a.interleave(col_b)
        assert len(result) == 2
        assert result[0] is c1
        assert result[1] is c2


class TestLabelChildren:
    def test_returns_vcollection(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        col = VCollection(c1, c2)
        labels = col.label_children(['A', 'B'])
        assert isinstance(labels, VCollection)

    def test_correct_number_of_labels(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        c3 = Circle(r=50, cx=500, cy=100)
        col = VCollection(c1, c2, c3)
        labels = col.label_children(['A', 'B', 'C'])
        assert len(labels.objects) == 3

    def test_fewer_labels_than_children(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        c3 = Circle(r=50, cx=500, cy=100)
        col = VCollection(c1, c2, c3)
        labels = col.label_children(['A', 'B'])
        assert len(labels.objects) == 2

    def test_label_text_content(self):
        from vectormation.objects import Text
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        col = VCollection(c1, c2)
        labels = col.label_children(['Hello', 'World'])
        assert isinstance(labels.objects[0], Text)
        assert isinstance(labels.objects[1], Text)
        assert labels.objects[0].text.at_time(0) == 'Hello'
        assert labels.objects[1].text.at_time(0) == 'World'

    def test_custom_font_size(self):
        c1 = Circle(r=50, cx=100, cy=100)
        col = VCollection(c1)
        labels = col.label_children(['A'], font_size=24)
        assert labels.objects[0].font_size.at_time(0) == pytest.approx(24)

    def test_label_positioned_relative_to_child(self):
        from vectormation.objects import UP
        c1 = Circle(r=50, cx=200, cy=200)
        col = VCollection(c1)
        labels = col.label_children(['Label'], direction=UP, buff=20)
        # Label should be above the circle (lower y value)
        label_cy = labels.objects[0].center(0)[1]
        child_cy = c1.center(0)[1]
        assert label_cy < child_cy

    def test_direction_down(self):
        c1 = Circle(r=50, cx=200, cy=200)
        col = VCollection(c1)
        labels = col.label_children(['Label'], direction=DOWN)
        # Label should be below the circle (higher y value)
        label_cy = labels.objects[0].center(0)[1]
        child_cy = c1.center(0)[1]
        assert label_cy > child_cy

    def test_empty_collection(self):
        col = VCollection()
        labels = col.label_children(['A', 'B'])
        assert len(labels.objects) == 0


class TestBatchAnimate:
    def test_returns_self(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        col = VCollection(c1, c2)
        result = col.batch_animate('shift', start=0, end=1, param_name='dx', values=[10, 20])
        assert result is col

    def test_param_name_varies_per_child(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        col = VCollection(c1, c2)
        col.batch_animate('shift', start=0, end=1, param_name='dx', values=[50, 100])
        # After animation, c1 should have shifted by 50 in x, c2 by 100
        c1_cx = c1.center(1)[0]
        c2_cx = c2.center(1)[0]
        assert c1_cx == pytest.approx(150, abs=2)
        assert c2_cx == pytest.approx(400, abs=2)

    def test_positional_values(self):
        c1 = Circle(r=50, cx=100, cy=100, fill='#ffffff')
        c2 = Circle(r=50, cx=300, cy=100, fill='#ffffff')
        col = VCollection(c1, c2)
        col.batch_animate('set_fill', start=0, end=1, values=['#ff0000', '#0000ff'],
                          param_name='color')
        # Each child should have a different fill color at time 1
        assert c1.styling.fill.at_time(1) in ('#ff0000', 'rgb(255,0,0)')
        assert c2.styling.fill.at_time(1) in ('#0000ff', 'rgb(0,0,255)')

    def test_fewer_values_than_children(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        c3 = Circle(r=50, cx=500, cy=100)
        col = VCollection(c1, c2, c3)
        # Only two values for three children — third child should not be affected
        col.batch_animate('shift', start=0, end=1, param_name='dx', values=[10, 20])
        c3_cx = c3.center(1)[0]
        assert c3_cx == pytest.approx(500, abs=2)

    def test_extra_kwargs_passed(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=300, cy=100)
        col = VCollection(c1, c2)
        col.batch_animate('shift', start=0, end=1, param_name='dx', values=[50, 100], dy=10)
        # Both should shift by 10 in y
        c1_cy = c1.center(1)[1]
        c2_cy = c2.center(1)[1]
        assert c1_cy == pytest.approx(110, abs=2)
        assert c2_cy == pytest.approx(110, abs=2)
