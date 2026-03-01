"""Edge case tests for _composites.py and _data_structures.py."""
import pytest
from vectormation.objects import (
    Circle, Rectangle, VCollection,
    MorphObject, NumberLine, Table, Matrix, DecimalMatrix, IntegerMatrix,
    DynamicObject, always_redraw, succession,
    Array, Stack, Queue, LinkedList, BinaryTree,
)
from vectormation._data_structures import (
    _make_cell, _flash_fill, _shift_pair, _fadeout_pair, _make_viz_cell,
)


# ── _make_cell helper ─────────────────────────────────────────────────────

class TestMakeCell:
    def test_returns_pair(self):
        cell, lbl = _make_cell(100, 100, 80, 60, 'A', 24, '#111', '#fff', '#fff')
        assert cell is not None
        assert lbl is not None

    def test_cell_is_rectangle(self):
        cell, lbl = _make_cell(100, 100, 80, 60, 42, 24, '#111', '#fff', '#fff')
        assert isinstance(cell, Rectangle)

    def test_zero_size_cell(self):
        cell, lbl = _make_cell(100, 100, 0, 0, '', 24, '#111', '#fff', '#fff')
        assert cell is not None


# ── _flash_fill helper ────────────────────────────────────────────────────

class TestFlashFill:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500, fill='#264653')
        _flash_fill(c, '#FF0000', start=0, end=1)
        # After end, fill should revert

    def test_custom_default(self):
        c = Circle(r=50, cx=500, cy=500)
        _flash_fill(c, '#FF0000', start=0, end=1, default='#333')


# ── _shift_pair / _fadeout_pair ───────────────────────────────────────────

class TestShiftPair:
    def test_shifts_both(self):
        cell, lbl = _make_cell(100, 100, 80, 60, 'X', 24, '#111', '#fff', '#fff')
        _shift_pair(cell, lbl, dx=50, dy=50, start=0, end=1)
        # Should not crash


class TestFadeoutPair:
    def test_fades_both(self):
        cell, lbl = _make_cell(100, 100, 80, 60, 'X', 24, '#111', '#fff', '#fff')
        _fadeout_pair(cell, lbl, start=0, end=1)
        # Should not crash

    def test_change_existence(self):
        cell, lbl = _make_cell(100, 100, 80, 60, 'X', 24, '#111', '#fff', '#fff')
        _fadeout_pair(cell, lbl, start=0, end=1, change_existence=True)


# ── _make_viz_cell ────────────────────────────────────────────────────────

class TestMakeVizCell:
    def test_returns_pair(self):
        cell, lbl = _make_viz_cell(100, 100, 80, 60, 'V', 24, '#111')
        assert cell is not None
        assert lbl is not None


# ── MorphObject ───────────────────────────────────────────────────────────

class TestMorphObjectEdgeCases:
    def test_type_error_on_wrong_from(self):
        with pytest.raises(TypeError, match='morph_from'):
            MorphObject("not_a_vobject", Circle(r=50))

    def test_type_error_on_wrong_to(self):
        with pytest.raises(TypeError, match='morph_to'):
            MorphObject(Circle(r=50), "not_a_vobject")

    def test_vobject_auto_wraps(self):
        """Single VObjects should be auto-wrapped to VCollection."""
        m = MorphObject(Circle(r=50, cx=500, cy=500), Rectangle(100, 100, x=500, y=500))
        assert m is not None

    def test_vcollection_input(self):
        m = MorphObject(
            VCollection(Circle(r=50, cx=500, cy=500)),
            VCollection(Rectangle(100, 100, x=500, y=500)),
        )
        assert m is not None


# ── Array data structure ──────────────────────────────────────────────────

class TestArrayEdgeCases:
    def test_empty_array(self):
        a = Array([])
        svg = a.to_svg(0)
        assert svg is not None

    def test_single_element(self):
        a = Array([42])
        assert len(a._cells) == 1

    def test_no_indices(self):
        a = Array([1, 2, 3], show_indices=False)
        svg = a.to_svg(0)
        assert svg is not None

    def test_string_values(self):
        a = Array(['a', 'b', 'c'])
        assert len(a._cells) == 3

    def test_highlight_nth(self):
        """Highlighting an index."""
        a = Array([1, 2, 3])
        a.highlight_nth(1, start=0)


# ── Stack data structure ──────────────────────────────────────────────────

class TestStackEdgeCases:
    def test_empty_stack(self):
        s = Stack()
        assert s.is_empty()

    def test_push_and_peek(self):
        s = Stack()
        s.push(42, start=0)
        assert not s.is_empty()
        val = s.peek()
        assert val == '42'  # values are stored as strings

    def test_pop_empty(self):
        s = Stack()
        result = s.pop(start=0)
        # pop on empty returns self (no-op)
        assert result is s


# ── Queue data structure ──────────────────────────────────────────────────

class TestQueueEdgeCases:
    def test_empty_queue(self):
        q = Queue()
        assert q.is_empty()

    def test_enqueue_and_peek(self):
        q = Queue()
        q.enqueue(10, start=0)
        assert not q.is_empty()
        val = q.peek()
        assert val == '10'  # values are stored as strings

    def test_dequeue_empty(self):
        q = Queue()
        result = q.dequeue(start=0)
        # dequeue on empty returns self (no-op)
        assert result is q


# ── LinkedList data structure ─────────────────────────────────────────────

class TestLinkedListEdgeCases:
    def test_empty_list(self):
        ll = LinkedList([])
        svg = ll.to_svg(0)
        assert svg is not None

    def test_single_element(self):
        ll = LinkedList([42])
        svg = ll.to_svg(0)
        assert svg is not None

    def test_renders_multiple(self):
        ll = LinkedList([1, 2, 3])
        svg = ll.to_svg(0)
        assert svg is not None


# ── BinaryTree ────────────────────────────────────────────────────────────

class TestBinaryTreeEdgeCases:
    def test_single_node(self):
        bt = BinaryTree([42])
        svg = bt.to_svg(0)
        assert svg is not None

    def test_full_tree(self):
        bt = BinaryTree([1, 2, 3, 4, 5, 6, 7])
        svg = bt.to_svg(0)
        assert svg is not None

    def test_none_children(self):
        """Tree with None placeholders for missing children."""
        bt = BinaryTree([1, None, 3])
        svg = bt.to_svg(0)
        assert svg is not None


# ── NumberLine edge cases ─────────────────────────────────────────────────

class TestNumberLineExtended:
    def test_add_pointer_returns_vcollection(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(0)
        assert isinstance(ptr, VCollection)

    def test_add_pointer_with_label(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(2, label='Two')
        assert ptr is not None

    def test_animate_pointer(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        ptr = nl.add_pointer(0)
        nl.animate_pointer(ptr, 3, start=0, end=1)

    def test_add_segment(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        seg = nl.add_segment(-2, 2)
        assert isinstance(seg, Rectangle)

    def test_add_label(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        result = nl.add_label(0, 'Zero')
        assert result is nl

    def test_add_label_above(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        nl.add_label(3, 'Three', side='above')

    def test_add_brace(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        brace = nl.add_brace(-2, 2, label='range')
        assert brace is not None

    def test_add_interval_bracket(self):
        nl = NumberLine(x_range=(-5, 5, 1))
        bracket = nl.add_interval_bracket(-1, 1, closed_left=True, closed_right=False)
        assert isinstance(bracket, VCollection)

    def test_snap_to_tick(self):
        nl = NumberLine(x_range=(0, 10, 2))
        # snap_to_tick rounds to nearest tick
        assert nl.snap_to_tick(3) in (2, 4)
        assert nl.snap_to_tick(5) in (4, 6)

    def test_snap_to_tick_clamps(self):
        nl = NumberLine(x_range=(0, 10, 2))
        assert nl.snap_to_tick(-5) == 0
        assert nl.snap_to_tick(15) == 10

    def test_get_range(self):
        nl = NumberLine(x_range=(-3, 7, 1))
        assert nl.get_range() == (-3, 7)

    def test_get_range_length(self):
        nl = NumberLine(x_range=(-3, 7, 1))
        assert nl.get_range_length() == 10

    def test_point_to_number_roundtrip(self):
        nl = NumberLine(x_range=(0, 10, 1))
        px, py = nl.number_to_point(5)
        val = nl.point_to_number(px)
        assert abs(val - 5) < 0.5

    def test_no_arrows(self):
        nl = NumberLine(x_range=(-5, 5), include_arrows=False)
        svg = nl.to_svg(0)
        assert svg is not None

    def test_no_numbers(self):
        nl = NumberLine(x_range=(-5, 5), include_numbers=False)
        svg = nl.to_svg(0)
        assert svg is not None


# ── Table edge cases ──────────────────────────────────────────────────────

class TestTableEdgeCases:
    def test_1x1_table(self):
        t = Table([['A']])
        svg = t.to_svg(0)
        assert svg is not None

    def test_single_row(self):
        t = Table([['a', 'b', 'c']])
        svg = t.to_svg(0)
        assert svg is not None

    def test_single_column(self):
        t = Table([['a'], ['b'], ['c']])
        svg = t.to_svg(0)
        assert svg is not None


# ── Matrix edge cases ─────────────────────────────────────────────────────

class TestMatrixEdgeCases:
    def test_1x1_matrix(self):
        m = Matrix([[5]])
        svg = m.to_svg(0)
        assert svg is not None

    def test_identity_determinant(self):
        m = Matrix([[1, 0], [0, 1]])
        assert m.determinant() == pytest.approx(1.0)

    def test_trace(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.trace() == pytest.approx(5.0)

    def test_get_values(self):
        m = Matrix([[1, 2], [3, 4]])
        vals = m.get_values()
        assert vals == [[1.0, 2.0], [3.0, 4.0]]


# ── DecimalMatrix ─────────────────────────────────────────────────────────

class TestDecimalMatrixEdgeCases:
    def test_repr(self):
        m = DecimalMatrix([[1.5, 2.5], [3.5, 4.5]])
        assert '2x2' in repr(m)

    def test_zero_decimals(self):
        m = DecimalMatrix([[1.999, 2.001]], decimals=0)
        svg = m.to_svg(0)
        assert svg is not None

    def test_many_decimals(self):
        m = DecimalMatrix([[3.14159]], decimals=5)
        svg = m.to_svg(0)
        assert svg is not None


# ── IntegerMatrix ─────────────────────────────────────────────────────────

class TestIntegerMatrixEdgeCases:
    def test_repr(self):
        m = IntegerMatrix([[1, 2], [3, 4]])
        assert '2x2' in repr(m)

    def test_rounds_values(self):
        m = IntegerMatrix([[1.9, 2.1]])
        svg = m.to_svg(0)
        assert svg is not None


# ── DynamicObject ─────────────────────────────────────────────────────────

class TestDynamicObjectEdgeCases:
    def test_returns_circle(self):
        d = DynamicObject(lambda t: Circle(r=50, cx=500 + t * 100, cy=500))
        svg = d.to_svg(0.5)
        assert svg is not None

    def test_none_return(self):
        """If func returns None, to_svg should return empty string."""
        d = DynamicObject(lambda _t: None)
        svg = d.to_svg(0)
        assert svg == ''


# ── always_redraw ─────────────────────────────────────────────────────────

class TestAlwaysRedraw:
    def test_basic(self):
        d = always_redraw(lambda t: Circle(r=50, cx=500, cy=500))
        svg = d.to_svg(0)
        assert svg is not None

    def test_with_creation(self):
        d = always_redraw(lambda t: Circle(r=50, cx=500, cy=500), creation=1)
        assert d is not None


# ── succession ────────────────────────────────────────────────────────────

class TestSuccessionEdgeCases:
    def test_empty(self):
        """Empty succession should not crash."""
        succession()

    def test_single_step(self):
        c = Circle(r=50, cx=500, cy=500)
        succession((c, 'fadein'), start=0)

    def test_with_kwargs(self):
        c = Circle(r=50, cx=500, cy=500)
        r = Rectangle(100, 50, x=500, y=500)
        succession(
            (c, 'fadein', {}),
            (r, 'fadein', {}),
            start=0,
        )

    def test_lag_ratio(self):
        c = Circle(r=50, cx=500, cy=500)
        r = Rectangle(100, 50, x=600, y=600)
        succession(
            (c, 'fadein'),
            (r, 'fadein'),
            start=0, lag_ratio=0.3,
        )
