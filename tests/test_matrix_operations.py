"""Tests for Matrix operations: determinant, row_operation, trace, augmented, etc."""
import pytest
from vectormation.objects import Matrix


class TestMatrixCreation:
    def test_basic(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.rows == 2
        assert m.cols == 2

    def test_3x3(self):
        m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert m.rows == 3
        assert m.cols == 3


class TestGetValues:
    def test_basic(self):
        m = Matrix([[1, 2], [3, 4]])
        vals = m.get_values(time=0)
        assert vals == [[1.0, 2.0], [3.0, 4.0]]


class TestDeterminant:
    def test_2x2(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.determinant() == pytest.approx(-2.0)

    def test_identity(self):
        m = Matrix([[1, 0], [0, 1]])
        assert m.determinant() == pytest.approx(1.0)

    def test_singular(self):
        m = Matrix([[1, 2], [2, 4]])
        assert m.determinant() == pytest.approx(0.0)

    def test_3x3(self):
        m = Matrix([[1, 2, 3], [0, 1, 4], [5, 6, 0]])
        assert m.determinant() == pytest.approx(1.0)

    def test_non_square_raises(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        with pytest.raises(ValueError, match='square matrix'):
            m.determinant()


class TestTrace:
    def test_2x2(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.trace() == pytest.approx(5.0)

    def test_identity_3x3(self):
        m = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        assert m.trace() == pytest.approx(3.0)

    def test_non_square_raises(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        with pytest.raises(ValueError, match='square matrix'):
            m.trace()


class TestRowOperation:
    def test_add_row(self):
        m = Matrix([[1, 2], [3, 4]])
        m.row_operation(0, 1, scalar=1, start=0, end=0)
        # R0 += 1 * R1 => [1+3, 2+4] = [4, 6]
        vals = m.get_values(time=0)
        assert vals[0] == [pytest.approx(4.0), pytest.approx(6.0)]

    def test_subtract_row(self):
        m = Matrix([[5, 6], [1, 2]])
        m.row_operation(0, 1, scalar=-1, start=0, end=0)
        # R0 -= R1 => [5-1, 6-2] = [4, 4]
        vals = m.get_values(time=0)
        assert vals[0] == [pytest.approx(4.0), pytest.approx(4.0)]


class TestSwapRows:
    def test_entries_swapped(self):
        m = Matrix([[1, 2], [3, 4]])
        e0 = m.entries[0]
        e1 = m.entries[1]
        m.swap_rows(0, 1)
        assert m.entries[0] is e1
        assert m.entries[1] is e0


class TestAugmented:
    def test_basic(self):
        m = Matrix.augmented([[1, 2], [3, 4]], [[5], [6]])
        assert m.rows == 2
        assert m.cols == 3


class TestSetEntryValue:
    def test_basic(self):
        m = Matrix([[1, 2], [3, 4]])
        m.set_entry_value(0, 0, 99, start=0)
        txt = m.entries[0][0].text.at_time(0)
        assert txt == '99'
