"""Edge case tests for _composites.py and _data_structures.py."""
import pytest
from vectormation.objects import (
    Circle, MorphObject, NumberLine, Matrix, DynamicObject,
)


# -- MorphObject ---------------------------------------------------------------

class TestMorphObjectEdgeCases:
    def test_type_error_on_wrong_from(self):
        with pytest.raises(TypeError, match='morph_from'):
            MorphObject("not_a_vobject", Circle(r=50))

    def test_type_error_on_wrong_to(self):
        with pytest.raises(TypeError, match='morph_to'):
            MorphObject(Circle(r=50), "not_a_vobject")


# -- Matrix edge cases ---------------------------------------------------------

class TestMatrixEdgeCases:
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


# -- NumberLine edge cases -----------------------------------------------------

class TestNumberLineExtended:
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


# -- DynamicObject -------------------------------------------------------------

class TestDynamicObjectEdgeCases:
    def test_none_return(self):
        """If func returns None, to_svg should return empty string."""
        d = DynamicObject(lambda _t: None)
        svg = d.to_svg(0)
        assert svg == ''
