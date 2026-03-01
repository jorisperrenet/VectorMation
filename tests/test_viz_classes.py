"""Tests for ArrayViz, LinkedListViz, StackViz, QueueViz, and BohrAtom."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ── ArrayViz ─────────────────────────────────────────────────────

class TestArrayViz:
    def test_basic_creation(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        assert len(a.values) == 3
        assert a.values == [10, 20, 30]

    def test_renders(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([1, 2, 3])
        svg = a.to_svg(0)
        assert svg is not None

    def test_repr(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([1, 2])
        assert 'ArrayViz' in repr(a)

    def test_highlight(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        result = a.highlight(1, start=0, end=1)
        assert result is a

    def test_highlight_out_of_range(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20])
        result = a.highlight(5, start=0, end=1)
        assert result is a  # should not crash

    def test_swap(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        result = a.swap(0, 2, start=0, end=1)
        assert result is a
        assert a.values == [30, 20, 10]

    def test_swap_same_index(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20])
        result = a.swap(0, 0)
        assert result is a
        assert a.values == [10, 20]

    def test_set_value(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        result = a.set_value(1, 99, start=0)
        assert result is a
        assert a.values[1] == 99

    def test_set_value_animated(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        a.set_value(0, 42, start=0, end=1)
        assert a.values[0] == 42

    def test_pointer(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10, 20, 30])
        result = a.pointer(1, label='i', start=0)
        assert result is not None

    def test_pointer_out_of_range(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([10])
        result = a.pointer(5)
        assert result is a

    def test_no_indices(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([1, 2], show_indices=False)
        assert len(a._index_labels) == 0

    def test_custom_colors(self):
        from vectormation.objects import ArrayViz
        a = ArrayViz([1, 2, 3], colors=['#f00', '#0f0', '#00f'])
        assert a is not None


# ── LinkedListViz ────────────────────────────────────────────────

class TestLinkedListViz:
    def test_basic_creation(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([1, 2, 3])
        assert len(ll.values) == 3

    def test_renders(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([10, 20])
        svg = ll.to_svg(0)
        assert svg is not None

    def test_repr(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([1])
        assert 'LinkedListViz' in repr(ll)

    def test_highlight(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([10, 20, 30])
        result = ll.highlight(1, start=0, end=1)
        assert result is ll

    def test_highlight_out_of_range(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([10, 20])
        result = ll.highlight(5)
        assert result is ll

    def test_traverse(self):
        from vectormation.objects import LinkedListViz
        ll = LinkedListViz([1, 2, 3])
        result = ll.traverse(start=0, delay=0.3)
        assert result is ll


# ── StackViz ─────────────────────────────────────────────────────

class TestStackViz:
    def test_basic_creation(self):
        from vectormation.objects import StackViz
        s = StackViz([1, 2, 3])
        assert len(s.values) == 3

    def test_renders(self):
        from vectormation.objects import StackViz
        s = StackViz([10, 20])
        svg = s.to_svg(0)
        assert svg is not None

    def test_repr(self):
        from vectormation.objects import StackViz
        s = StackViz([1])
        assert 'StackViz' in repr(s)

    def test_push(self):
        from vectormation.objects import StackViz
        s = StackViz([1, 2])
        result = s.push(3, start=0, end=0.5)
        assert result is s
        assert s.values == [1, 2, 3]

    def test_pop(self):
        from vectormation.objects import StackViz
        s = StackViz([1, 2, 3])
        result = s.pop(start=0, end=0.5)
        assert result is s
        assert s.values == [1, 2]

    def test_pop_empty(self):
        from vectormation.objects import StackViz
        s = StackViz([])
        result = s.pop()
        assert result is s

    def test_push_then_pop(self):
        from vectormation.objects import StackViz
        s = StackViz([10])
        s.push(20, start=0, end=0.5)
        s.pop(start=1, end=1.5)
        assert s.values == [10]


# ── QueueViz ─────────────────────────────────────────────────────

class TestQueueViz:
    def test_basic_creation(self):
        from vectormation.objects import QueueViz
        q = QueueViz([1, 2, 3])
        assert len(q.values) == 3

    def test_renders(self):
        from vectormation.objects import QueueViz
        q = QueueViz([10, 20])
        svg = q.to_svg(0)
        assert svg is not None

    def test_repr(self):
        from vectormation.objects import QueueViz
        q = QueueViz([1])
        assert 'QueueViz' in repr(q)

    def test_enqueue(self):
        from vectormation.objects import QueueViz
        q = QueueViz([1, 2])
        result = q.enqueue(3, start=0, end=0.5)
        assert result is q
        assert q.values == [1, 2, 3]

    def test_dequeue(self):
        from vectormation.objects import QueueViz
        q = QueueViz([1, 2, 3])
        result = q.dequeue(start=0, end=0.5)
        assert result is q
        assert q.values == [2, 3]

    def test_dequeue_empty(self):
        from vectormation.objects import QueueViz
        q = QueueViz([])
        result = q.dequeue()
        assert result is q

    def test_highlight(self):
        from vectormation.objects import QueueViz
        q = QueueViz([10, 20, 30])
        result = q.highlight(1, start=0, end=0.5)
        assert result is q

    def test_highlight_out_of_range(self):
        from vectormation.objects import QueueViz
        q = QueueViz([10])
        result = q.highlight(5)
        assert result is q

    def test_enqueue_then_dequeue(self):
        from vectormation.objects import QueueViz
        q = QueueViz([10])
        q.enqueue(20, start=0, end=0.5)
        q.dequeue(start=1, end=1.5)
        assert q.values == [20]


# ── BohrAtom ─────────────────────────────────────────────────────

class TestBohrAtom:
    def test_basic_creation(self):
        from vectormation.objects import BohrAtom
        atom = BohrAtom(electrons=[2, 8])
        assert atom is not None

    def test_renders(self):
        from vectormation.objects import BohrAtom
        atom = BohrAtom(electrons=[2, 8])
        svg = atom.to_svg(0)
        assert svg is not None

    def test_repr(self):
        from vectormation.objects import BohrAtom
        atom = BohrAtom(electrons=[2])
        assert 'BohrAtom' in repr(atom)

    def test_with_protons_and_neutrons(self):
        from vectormation.objects import BohrAtom
        atom = BohrAtom(electrons=[2, 8], protons=10, neutrons=10)
        assert atom is not None

    def test_single_shell(self):
        from vectormation.objects import BohrAtom
        atom = BohrAtom(electrons=[1])
        svg = atom.to_svg(0)
        assert svg is not None


# ── UnitInterval ─────────────────────────────────────────────────

class TestUnitInterval:
    def test_basic_creation(self):
        from vectormation.objects import UnitInterval
        ui = UnitInterval()
        assert ui is not None

    def test_renders(self):
        from vectormation.objects import UnitInterval
        ui = UnitInterval()
        svg = ui.to_svg(0)
        assert svg is not None

    def test_custom_tick_step(self):
        from vectormation.objects import UnitInterval
        ui = UnitInterval(tick_step=0.25)
        assert ui is not None


# ── NeuralNetwork methods ────────────────────────────────────────

class TestNeuralNetworkMethods:
    def test_activate(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 4, 2])
        result = nn.activate(0, 1, start=0, end=1)
        assert result is nn

    def test_propagate(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 4, 2])
        result = nn.propagate(start=0, end=2)
        assert result is nn

    def test_highlight_path(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 4, 2])
        result = nn.highlight_path([0, 1, 0], start=0)
        assert result is nn

    def test_label_input(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 2])
        result = nn.label_input(['a', 'b', 'c'])
        assert result is nn

    def test_label_output(self):
        from vectormation.objects import NeuralNetwork
        nn = NeuralNetwork([3, 2])
        result = nn.label_output(['x', 'y'])
        assert result is nn
