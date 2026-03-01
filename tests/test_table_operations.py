"""Tests for Table operations: sort, swap, add/remove rows/cols, transpose, etc."""
import pytest
from vectormation.objects import Table


class TestTableCreation:
    def test_basic(self):
        t = Table([['a', 'b'], ['c', 'd']])
        assert t.rows == 2
        assert t.cols == 2

    def test_with_labels(self):
        t = Table([['1', '2'], ['3', '4']], col_labels=['X', 'Y'])
        assert t.rows == 2
        assert t.cols == 2

    def test_from_dict(self):
        t = Table.from_dict({'Name': ['Alice', 'Bob'], 'Age': [25, 30]})
        assert t.rows == 2
        assert t.cols == 2


class TestTranspose:
    def test_basic(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.transpose(start=0)
        assert result is t
        assert t.rows == 2
        assert t.cols == 2

    def test_nonsquare(self):
        t = Table([['a', 'b', 'c'], ['d', 'e', 'f']])
        assert t.rows == 2
        assert t.cols == 3
        t.transpose(start=0)
        assert t.rows == 3
        assert t.cols == 2


class TestSortByColumn:
    def test_returns_self(self):
        t = Table([['b', '2'], ['a', '1']])
        result = t.sort_by_column(0, start=0, end=1)
        assert result is t

    def test_reverse(self):
        t = Table([['a', '1'], ['b', '2']])
        result = t.sort_by_column(0, reverse=True)
        assert result is t


class TestSwapRows:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd'], ['e', 'f']])
        result = t.swap_rows(0, 2)
        assert result is t

    def test_same_row_noop(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.swap_rows(0, 0)
        assert result is t

    def test_entries_swapped(self):
        t = Table([['a', 'b'], ['c', 'd']])
        e0_before = t.entries[0]
        e1_before = t.entries[1]
        t.swap_rows(0, 1)
        assert t.entries[0] is e1_before
        assert t.entries[1] is e0_before


class TestSwapColumns:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.swap_columns(0, 1)
        assert result is t

    def test_same_column_noop(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.swap_columns(1, 1)
        assert result is t


class TestAddRow:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.add_row(['e', 'f'], start=0)
        assert result is t

    def test_row_count_increases(self):
        t = Table([['a', 'b']])
        assert t.rows == 1
        t.add_row(['c', 'd'])
        assert t.rows == 2

    def test_no_animate(self):
        t = Table([['a', 'b']])
        t.add_row(['c', 'd'], animate=False)
        assert t.rows == 2


class TestAddColumn:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.add_column(['e', 'f'], start=0)
        assert result is t

    def test_col_count_increases(self):
        t = Table([['a'], ['b']])
        assert t.cols == 1
        t.add_column(['c', 'd'])
        assert t.cols == 2


class TestRemoveRow:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd'], ['e', 'f']])
        result = t.remove_row(1)
        assert result is t
        assert t.rows == 2

    def test_invalid_index(self):
        t = Table([['a', 'b']])
        with pytest.raises(IndexError):
            t.remove_row(5)

    def test_no_animate(self):
        t = Table([['a', 'b'], ['c', 'd']])
        t.remove_row(0, animate=False)
        assert t.rows == 1


class TestRemoveColumn:
    def test_returns_self(self):
        t = Table([['a', 'b', 'c'], ['d', 'e', 'f']])
        result = t.remove_column(1)
        assert result is t
        assert t.cols == 2

    def test_invalid_index(self):
        t = Table([['a', 'b']])
        with pytest.raises(IndexError):
            t.remove_column(5)


class TestHighlightWhere:
    def test_returns_self(self):
        t = Table([['1', '2'], ['3', '4']])
        result = t.highlight_where(lambda x: int(x) > 2)
        assert result is t

    def test_no_matches(self):
        t = Table([['1', '2']])
        result = t.highlight_where(lambda x: False)
        assert result is t


class TestAnimateCellValues:
    def test_returns_self(self):
        t = Table([['1', '2'], ['3', '4']])
        result = t.animate_cell_values([['5', '6'], ['7', '8']], start=0, end=1)
        assert result is t

    def test_zero_duration(self):
        t = Table([['1', '2'], ['3', '4']])
        result = t.animate_cell_values([['5', '6'], ['7', '8']], start=1, end=1)
        assert result is t

    def test_non_numeric(self):
        t = Table([['hello', 'world']])
        result = t.animate_cell_values([['foo', 'bar']], start=0, end=1)
        assert result is t


class TestAnimateCells:
    def test_returns_self(self):
        t = Table([['a', 'b'], ['c', 'd']])
        result = t.animate_cells([(0, 0), (1, 1)], method_name='flash', start=0, end=1)
        assert result is t


class TestSetCellValue:
    def test_basic(self):
        t = Table([['old', 'val']])
        t.set_cell_value(0, 0, 'new', start=0)
        txt = t.entries[0][0].text.at_time(0)
        assert txt == 'new'


class TestSetCellValues:
    def test_batch_update(self):
        t = Table([['a', 'b'], ['c', 'd']])
        t.set_cell_values({(0, 0): 'X', (1, 1): 'Y'}, start=0)
        assert t.entries[0][0].text.at_time(0) == 'X'
        assert t.entries[1][1].text.at_time(0) == 'Y'
