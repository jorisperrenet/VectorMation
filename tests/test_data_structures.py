"""Tests for vectormation._data_structures: Array, Stack, Queue, LinkedList, BinaryTree."""
import pytest
from vectormation.objects import Array, Stack, Queue, LinkedList, BinaryTree


class TestArray:
    def test_init_values(self):
        arr = Array([10, 20, 30])
        assert len(arr._cells) == 3
        assert len(arr._labels) == 3

    def test_repr(self):
        arr = Array([1, 2, 3])
        assert repr(arr) == 'Array(3 cells)'

    def test_empty_array(self):
        arr = Array([])
        assert len(arr._cells) == 0
        assert repr(arr) == 'Array(0 cells)'

    def test_highlight_cell(self):
        arr = Array([10, 20, 30])
        result = arr.highlight_cell(1, start=0, end=1)
        assert result is arr

    def test_highlight_cell_out_of_range(self):
        arr = Array([10, 20])
        with pytest.raises(IndexError):
            arr.highlight_cell(5, start=0, end=1)

    def test_swap_cells(self):
        arr = Array([10, 20, 30])
        result = arr.swap_cells(0, 2, start=0, end=1)
        assert result is arr

    def test_swap_out_of_range(self):
        arr = Array([10, 20])
        with pytest.raises(IndexError):
            arr.swap_cells(0, 5, start=0, end=1)

    def test_set_value(self):
        arr = Array([10, 20, 30])
        result = arr.set_value(1, 99, start=0, end=0.5)
        assert result is arr

    def test_set_value_out_of_range(self):
        arr = Array([10])
        with pytest.raises(IndexError):
            arr.set_value(5, 99)

    def test_sort_returns_self(self):
        arr = Array([3, 1, 2])
        result = arr.sort(start=0, end=2)
        assert result is arr

    def test_reverse_returns_self(self):
        arr = Array([1, 2, 3])
        result = arr.reverse(start=0, end=2)
        assert result is arr

    def test_add_pointer(self):
        arr = Array([10, 20, 30])
        arrow = arr.add_pointer(1, label='ptr')
        # Returns the Arrow, not self
        assert arrow is not arr

    def test_add_pointer_invalid_index(self):
        arr = Array([10, 20])
        result = arr.add_pointer(10)
        assert result is arr  # Returns self for invalid index

    def test_no_indices(self):
        arr = Array([1, 2], show_indices=False)
        assert len(arr._cells) == 2

    def test_single_element(self):
        arr = Array([42])
        assert len(arr._cells) == 1
        assert repr(arr) == 'Array(1 cells)'


class TestStack:
    def test_init_empty(self):
        s = Stack()
        assert s.is_empty()
        assert s.peek() is None
        assert repr(s) == 'Stack(0 items)'

    def test_init_with_values(self):
        s = Stack([10, 20, 30])
        assert not s.is_empty()
        assert repr(s) == 'Stack(3 items)'

    def test_push(self):
        s = Stack()
        result = s.push(42, start=0, end=0.5)
        assert result is s
        assert not s.is_empty()
        assert repr(s) == 'Stack(1 items)'

    def test_pop(self):
        s = Stack([10, 20])
        result = s.pop(start=0, end=0.5)
        assert result is s
        assert repr(s) == 'Stack(1 items)'

    def test_pop_empty(self):
        s = Stack()
        result = s.pop(start=0, end=0.5)
        assert result is s  # Returns self without error

    def test_push_pop_sequence(self):
        s = Stack()
        s.push(1, start=0, end=0.5)
        s.push(2, start=0.5, end=1)
        assert repr(s) == 'Stack(2 items)'
        s.pop(start=1, end=1.5)
        assert repr(s) == 'Stack(1 items)'


class TestQueue:
    def test_init_empty(self):
        q = Queue()
        assert q.is_empty()
        assert q.peek() is None
        assert repr(q) == 'Queue(0 items)'

    def test_init_with_values(self):
        q = Queue([10, 20, 30])
        assert not q.is_empty()
        assert repr(q) == 'Queue(3 items)'

    def test_enqueue(self):
        q = Queue()
        result = q.enqueue(42, start=0, end=0.5)
        assert result is q
        assert not q.is_empty()

    def test_dequeue(self):
        q = Queue([10, 20])
        result = q.dequeue(start=0, end=0.5)
        assert result is q
        assert repr(q) == 'Queue(1 items)'

    def test_dequeue_empty(self):
        q = Queue()
        result = q.dequeue(start=0, end=0.5)
        assert result is q  # Returns self without error

    def test_enqueue_dequeue_sequence(self):
        q = Queue()
        q.enqueue(1, start=0, end=0.5)
        q.enqueue(2, start=0.5, end=1)
        assert repr(q) == 'Queue(2 items)'
        q.dequeue(start=1, end=1.5)
        assert repr(q) == 'Queue(1 items)'


class TestLinkedList:
    def test_init(self):
        ll = LinkedList([10, 20, 30])
        assert repr(ll) == 'LinkedList(3 nodes)'

    def test_single_node(self):
        ll = LinkedList([42])
        assert repr(ll) == 'LinkedList(1 nodes)'

    def test_highlight_node(self):
        ll = LinkedList([10, 20])
        result = ll.highlight_node(0, start=0, end=1)
        assert result is ll

    def test_highlight_node_invalid(self):
        ll = LinkedList([10])
        result = ll.highlight_node(5, start=0, end=1)
        assert result is ll

    def test_append_node(self):
        ll = LinkedList([10, 20])
        result = ll.append_node(30, start=0, end=0.5)
        assert result is ll
        assert repr(ll) == 'LinkedList(3 nodes)'

    def test_remove_node(self):
        ll = LinkedList([10, 20, 30])
        result = ll.remove_node(1, start=0, end=0.5)
        assert result is ll
        assert repr(ll) == 'LinkedList(2 nodes)'

    def test_remove_node_invalid(self):
        ll = LinkedList([10])
        result = ll.remove_node(5, start=0, end=0.5)
        assert result is ll


class TestBinaryTree:
    def test_single_node(self):
        bt = BinaryTree(42)
        assert repr(bt) == 'BinaryTree(1 nodes)'

    def test_nested_tuple(self):
        bt = BinaryTree((1, (2,), (3,)))
        assert repr(bt) == 'BinaryTree(3 nodes)'

    def test_deeper_tree(self):
        tree = (1, (2, 4, 5), (3, 6, 7))
        bt = BinaryTree(tree)
        assert repr(bt) == 'BinaryTree(7 nodes)'

    def test_none_children(self):
        bt = BinaryTree((1, None, (3,)))
        assert repr(bt) == 'BinaryTree(2 nodes)'

    def test_highlight_node(self):
        bt = BinaryTree((1, 2, 3))
        result = bt.highlight_node(0, start=0, end=0.5)
        assert result is bt

    def test_highlight_node_invalid(self):
        bt = BinaryTree(42)
        result = bt.highlight_node(10, start=0, end=0.5)
        assert result is bt

    def test_traverse(self):
        bt = BinaryTree((1, 2, 3))
        result = bt.traverse(start=0, delay=0.3)
        assert result is bt
