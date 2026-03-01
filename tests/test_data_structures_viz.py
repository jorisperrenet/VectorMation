"""Tests for data structure visualization classes (ArrayViz, LinkedListViz, StackViz, QueueViz)."""
from vectormation.objects import (
    ArrayViz, LinkedListViz, StackViz, QueueViz, VectorMathAnim,
)


class TestArrayViz:
    def test_creates_with_values(self):
        a = ArrayViz([1, 2, 3], creation=0)
        assert len(a.objects) > 0
        assert a.values == [1, 2, 3]

    def test_repr(self):
        a = ArrayViz([10, 20], creation=0)
        assert '10' in repr(a)

    def test_highlight_returns_self(self):
        a = ArrayViz([1, 2, 3], creation=0)
        assert a.highlight(0, start=0, end=1) is a

    def test_highlight_out_of_range(self):
        a = ArrayViz([1, 2], creation=0)
        assert a.highlight(99, start=0, end=1) is a

    def test_swap(self):
        a = ArrayViz([1, 2, 3], creation=0)
        a.swap(0, 2, start=0, end=1)
        assert a.values == [3, 2, 1]

    def test_swap_same_index(self):
        a = ArrayViz([1, 2, 3], creation=0)
        a.swap(1, 1, start=0, end=1)
        assert a.values == [1, 2, 3]

    def test_set_value(self):
        a = ArrayViz([1, 2, 3], creation=0)
        a.set_value(1, 99, start=0)
        assert a.values[1] == 99

    def test_set_value_out_of_range(self):
        a = ArrayViz([1, 2], creation=0)
        a.set_value(99, 42, start=0)
        assert a.values == [1, 2]

    def test_pointer(self):
        a = ArrayViz([1, 2, 3], creation=0)
        arr = a.pointer(0, label='ptr', start=0)
        assert arr is not None

    def test_pointer_out_of_range(self):
        a = ArrayViz([1, 2], creation=0)
        result = a.pointer(99, start=0)
        assert result is a

    def test_renders(self):
        a = ArrayViz([1, 2, 3], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ds_viz')
        v.add(a)
        svg = v.generate_frame_svg(time=0)
        assert svg

    def test_custom_colors(self):
        a = ArrayViz([1, 2, 3], colors=['#FF0000', '#00FF00', '#0000FF'], creation=0)
        assert len(a._cells) == 3

    def test_no_indices(self):
        a = ArrayViz([1, 2], show_indices=False, creation=0)
        assert len(a._index_labels) == 0


class TestLinkedListViz:
    def test_creates_with_values(self):
        ll = LinkedListViz([1, 2, 3], creation=0)
        assert len(ll.objects) > 0
        assert ll.values == [1, 2, 3]

    def test_repr(self):
        ll = LinkedListViz([10, 20], creation=0)
        assert '10' in repr(ll)

    def test_highlight_returns_self(self):
        ll = LinkedListViz([1, 2, 3], creation=0)
        assert ll.highlight(0, start=0, end=1) is ll

    def test_highlight_out_of_range(self):
        ll = LinkedListViz([1, 2], creation=0)
        assert ll.highlight(99, start=0, end=1) is ll

    def test_traverse_returns_self(self):
        ll = LinkedListViz([1, 2, 3], creation=0)
        assert ll.traverse(start=0) is ll

    def test_renders(self):
        ll = LinkedListViz([1, 2, 3], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ds_viz')
        v.add(ll)
        svg = v.generate_frame_svg(time=0)
        assert svg

    def test_single_node(self):
        ll = LinkedListViz([42], creation=0)
        assert len(ll._nodes) == 1
        assert len(ll._arrows) == 0


class TestStackViz:
    def test_creates_with_values(self):
        s = StackViz([1, 2, 3], creation=0)
        assert len(s.objects) > 0
        assert s.values == [1, 2, 3]

    def test_repr(self):
        s = StackViz([10, 20], creation=0)
        assert '10' in repr(s)

    def test_push(self):
        s = StackViz([1, 2], creation=0)
        s.push(3, start=1, end=1.5)
        assert s.values == [1, 2, 3]
        assert len(s._stack_cells) == 3

    def test_pop(self):
        s = StackViz([1, 2, 3], creation=0)
        s.pop(start=1, end=1.5)
        assert s.values == [1, 2]
        assert len(s._stack_cells) == 2

    def test_pop_empty(self):
        s = StackViz([], creation=0)
        assert s.pop(start=0) is s

    def test_push_then_pop(self):
        s = StackViz([], creation=0)
        s.push(42, start=0, end=0.5)
        assert s.values == [42]
        s.pop(start=1, end=1.5)
        assert s.values == []

    def test_renders(self):
        s = StackViz([1, 2, 3], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ds_viz')
        v.add(s)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestQueueViz:
    def test_creates_with_values(self):
        q = QueueViz([1, 2, 3], creation=0)
        assert len(q.objects) > 0
        assert q.values == [1, 2, 3]

    def test_repr(self):
        q = QueueViz([10, 20], creation=0)
        assert '10' in repr(q)

    def test_enqueue(self):
        q = QueueViz([1, 2], creation=0)
        q.enqueue(3, start=1, end=1.5)
        assert q.values == [1, 2, 3]
        assert len(q._queue_cells) == 3

    def test_dequeue(self):
        q = QueueViz([1, 2, 3], creation=0)
        q.dequeue(start=1, end=1.5)
        assert q.values == [2, 3]
        assert len(q._queue_cells) == 2

    def test_dequeue_empty(self):
        q = QueueViz([], creation=0)
        assert q.dequeue(start=0) is q

    def test_enqueue_then_dequeue(self):
        q = QueueViz([], creation=0)
        q.enqueue(42, start=0, end=0.5)
        assert q.values == [42]
        q.dequeue(start=1, end=1.5)
        assert q.values == []

    def test_renders(self):
        q = QueueViz([1, 2, 3], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ds_viz')
        v.add(q)
        svg = v.generate_frame_svg(time=0)
        assert svg
