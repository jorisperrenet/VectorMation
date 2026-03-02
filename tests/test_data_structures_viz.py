"""Tests for data structure visualization classes (ArrayViz, LinkedListViz, StackViz, QueueViz)."""
from vectormation.objects import (
    ArrayViz, LinkedListViz, StackViz, QueueViz,
)


class TestArrayViz:
    def test_creates_with_values(self):
        a = ArrayViz([1, 2, 3], creation=0)
        assert a.values == [1, 2, 3]

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

    def test_custom_colors(self):
        a = ArrayViz([1, 2, 3], colors=['#FF0000', '#00FF00', '#0000FF'], creation=0)
        assert len(a._cells) == 3

    def test_no_indices(self):
        a = ArrayViz([1, 2], show_indices=False, creation=0)
        assert len(a._index_labels) == 0


class TestLinkedListViz:
    def test_creates_with_values(self):
        ll = LinkedListViz([1, 2, 3], creation=0)
        assert ll.values == [1, 2, 3]

    def test_single_node(self):
        ll = LinkedListViz([42], creation=0)
        assert len(ll._nodes) == 1
        assert len(ll._arrows) == 0


class TestStackViz:
    def test_creates_with_values(self):
        s = StackViz([1, 2, 3], creation=0)
        assert s.values == [1, 2, 3]

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

    def test_push_then_pop(self):
        s = StackViz([], creation=0)
        s.push(42, start=0, end=0.5)
        assert s.values == [42]
        s.pop(start=1, end=1.5)
        assert s.values == []


class TestQueueViz:
    def test_creates_with_values(self):
        q = QueueViz([1, 2, 3], creation=0)
        assert q.values == [1, 2, 3]

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

    def test_enqueue_then_dequeue(self):
        q = QueueViz([], creation=0)
        q.enqueue(42, start=0, end=0.5)
        assert q.values == [42]
        q.dequeue(start=1, end=1.5)
        assert q.values == []
