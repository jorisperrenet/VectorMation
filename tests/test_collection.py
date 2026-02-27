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
