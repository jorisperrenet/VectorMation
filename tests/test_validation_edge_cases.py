"""Tests for input validation, error handling, and edge cases across modules."""
import math
import pytest
from vectormation.objects import (
    Circle, Rectangle, Text, VCollection,
    Pendulum, StandingWave, NeuralNetwork, Resistor, Capacitor, Inductor,
    Diode, Molecule2D, Charge, ElectricField, Lens, Ray,
    RadarChart, DonutChart,
    ChessBoard, Automaton, NetworkGraph, Tree, FlowChart, VennDiagram,
    OrgChart, MindMap, BohrAtom, PeriodicTable,
    Stamp, TimelineBar,
    Code, Variable, TagCloud, StatusIndicator, Meter, Breadcrumb,
    SpeechBubble, Stepper, Checklist, Filmstrip, IconGrid,
    Array, Stack, Queue, LinkedList, BinaryTree,
    ArrayViz, LinkedListViz, StackViz, QueueViz,
)


# ── Pendulum ────────────────────────────────────────────────────────────

class TestPendulumValidation:
    def test_zero_period_raises(self):
        with pytest.raises(ValueError, match="period must be > 0"):
            Pendulum(period=0)

    def test_negative_period_raises(self):
        with pytest.raises(ValueError, match="period must be > 0"):
            Pendulum(period=-1)

    def test_valid_period(self):
        p = Pendulum(period=2)
        assert p is not None

    def test_small_period(self):
        p = Pendulum(period=0.01)
        svg = p.to_svg(0)
        assert svg is not None

    def test_custom_params(self):
        p = Pendulum(pivot_x=500, pivot_y=100, length=200,
                     angle=30, period=1.5, damping=0.5,
                     bob_radius=20, start=0, end=5)
        svg = p.to_svg(1)
        assert svg is not None


# ── RadarChart ──────────────────────────────────────────────────────────

class TestRadarChartValidation:
    def test_add_dataset_wrong_length_raises(self):
        rc = RadarChart([1, 2, 3], labels=['A', 'B', 'C'])
        with pytest.raises(ValueError, match="expects 3 values"):
            rc.add_dataset([1, 2])

    def test_add_dataset_correct_length(self):
        rc = RadarChart([1, 2, 3], labels=['A', 'B', 'C'])
        result = rc.add_dataset([3, 2, 1])
        assert result is rc


# ── PhysicsSpace ────────────────────────────────────────────────────────

class TestPhysicsSpaceValidation:
    def test_zero_dt_raises(self):
        from vectormation.objects import PhysicsSpace
        with pytest.raises(ValueError, match="dt must be > 0"):
            PhysicsSpace(dt=0)

    def test_negative_dt_raises(self):
        from vectormation.objects import PhysicsSpace
        with pytest.raises(ValueError, match="dt must be > 0"):
            PhysicsSpace(dt=-0.01)

    def test_valid_dt(self):
        from vectormation.objects import PhysicsSpace
        ps = PhysicsSpace(dt=1/60)
        assert ps.dt == pytest.approx(1/60)


# ── NeuralNetwork ───────────────────────────────────────────────────────

class TestNeuralNetworkEdgeCases:
    def test_single_layer_empty(self):
        nn = NeuralNetwork([3])
        assert len(nn) == 0

    def test_two_layers(self):
        nn = NeuralNetwork([2, 3])
        assert len(nn) > 0

    def test_activate_valid(self):
        nn = NeuralNetwork([2, 3])
        result = nn.activate(0, 0, start=0, end=1)
        assert result is nn

    def test_activate_out_of_bounds(self):
        nn = NeuralNetwork([2, 3])
        result = nn.activate(5, 0)
        assert result is nn  # silent no-op

    def test_propagate(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.propagate(start=0, end=1)
        assert result is nn

    def test_highlight_path_valid(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.highlight_path([0, 1, 0])
        assert result is nn

    def test_highlight_path_wrong_length(self):
        nn = NeuralNetwork([2, 3, 1])
        result = nn.highlight_path([0, 1])
        assert result is nn  # silent no-op

    def test_label_input(self):
        nn = NeuralNetwork([2, 3])
        result = nn.label_input(['a', 'b'])
        assert result is nn

    def test_label_output(self):
        nn = NeuralNetwork([2, 3])
        result = nn.label_output(['x', 'y', 'z'])
        assert result is nn

    def test_repr(self):
        nn = NeuralNetwork([3, 4, 2])
        assert '3' in repr(nn)
        assert '4' in repr(nn)
        assert '2' in repr(nn)

    def test_renders(self):
        nn = NeuralNetwork([2, 3, 1])
        svg = nn.to_svg(0)
        assert 'circle' in svg


# ── Electronic Components ──────────────────────────────────────────────

class TestElectronicComponents:
    def test_resistor_basic(self):
        r = Resistor()
        svg = r.to_svg(0)
        assert svg is not None

    def test_resistor_custom_pos(self):
        r = Resistor(x1=100, y1=200, x2=300, y2=200, label='R1')
        svg = r.to_svg(0)
        assert svg is not None

    def test_capacitor_basic(self):
        c = Capacitor()
        svg = c.to_svg(0)
        assert svg is not None

    def test_inductor_basic(self):
        i = Inductor()
        svg = i.to_svg(0)
        assert svg is not None

    def test_inductor_custom_loops(self):
        i = Inductor(n_loops=6)
        svg = i.to_svg(0)
        assert svg is not None

    def test_diode_basic(self):
        d = Diode()
        svg = d.to_svg(0)
        assert svg is not None

    def test_diode_custom_pos(self):
        d = Diode(x1=100, y1=300, x2=400, y2=300, label='D1')
        svg = d.to_svg(0)
        assert svg is not None


# ── Molecule2D ──────────────────────────────────────────────────────────

class TestMolecule2DEdgeCases:
    def test_single_atom(self):
        m = Molecule2D([('H', 500, 500)])
        svg = m.to_svg(0)
        assert svg is not None

    def test_with_bonds(self):
        m = Molecule2D(
            [('O', 500, 500), ('H', 400, 450), ('H', 600, 450)],
            bonds=[(0, 1), (0, 2)]
        )
        svg = m.to_svg(0)
        assert svg is not None

    def test_invalid_bond_skipped(self):
        m = Molecule2D(
            [('H', 500, 500)],
            bonds=[(0, 5)]  # index 5 doesn't exist
        )
        svg = m.to_svg(0)
        assert svg is not None

    def test_double_bond(self):
        m = Molecule2D(
            [('O', 500, 500), ('O', 650, 500)],
            bonds=[(0, 1, 2)]  # double bond
        )
        svg = m.to_svg(0)
        assert svg is not None


# ── StandingWave ────────────────────────────────────────────────────────

class TestStandingWaveEdgeCases:
    def test_basic(self):
        sw = StandingWave(x1=200, y1=540, x2=1720, y2=540)
        svg = sw.to_svg(0)
        assert svg is not None

    def test_custom_harmonics(self):
        sw = StandingWave(harmonics=3)
        svg = sw.to_svg(0)
        assert svg is not None

    def test_vertical_wave(self):
        sw = StandingWave(x1=500, y1=100, x2=500, y2=900)
        svg = sw.to_svg(0)
        assert svg is not None


# ── Charge & ElectricField ──────────────────────────────────────────────

class TestChargeEdgeCases:
    def test_positive(self):
        c = Charge(1, cx=500, cy=500)
        svg = c.to_svg(0)
        assert svg is not None

    def test_negative(self):
        c = Charge(-1, cx=500, cy=500)
        svg = c.to_svg(0)
        assert svg is not None

    def test_large_magnitude(self):
        c = Charge(10, cx=500, cy=500)
        svg = c.to_svg(0)
        assert svg is not None

    def test_small_magnitude(self):
        c = Charge(0.1, cx=500, cy=500)
        svg = c.to_svg(0)
        assert svg is not None


class TestElectricFieldEdgeCases:
    def test_single_charge(self):
        c = Charge(1, cx=500, cy=500)
        ef = ElectricField(c)  # positional arg, not list
        svg = ef.to_svg(0)
        assert svg is not None

    def test_two_charges(self):
        c1 = Charge(1, cx=400, cy=500)
        c2 = Charge(-1, cx=600, cy=500)
        ef = ElectricField(c1, c2)  # positional args
        assert len(ef) > 0


# ── Lens & Ray ──────────────────────────────────────────────────────────

class TestLensEdgeCases:
    def test_converging(self):
        l = Lens(focal_length=200)
        svg = l.to_svg(0)
        assert svg is not None

    def test_diverging(self):
        l = Lens(focal_length=-200)
        svg = l.to_svg(0)
        assert svg is not None

    def test_image_point(self):
        l = Lens(focal_length=200, cx=500)
        pt = l.image_point(200, 400)  # obj_x, obj_y
        assert pt is not None


class TestRayEdgeCases:
    def test_basic(self):
        r = Ray(x1=100, y1=500, angle=0)
        svg = r.to_svg(0)
        assert svg is not None

    def test_angled(self):
        r = Ray(x1=100, y1=300, angle=15)
        svg = r.to_svg(0)
        assert svg is not None

    def test_with_lens(self):
        l = Lens(focal_length=200, cx=500)
        r = Ray(x1=100, y1=500, angle=0, lenses=[l])
        svg = r.to_svg(0)
        assert svg is not None


# ── DonutChart ──────────────────────────────────────────────────────────

class TestDonutChartEdgeCases:
    def test_inner_radius_larger_than_outer(self):
        # Should still create without crashing
        d = DonutChart([50, 50], r=100, inner_radius=150)
        svg = d.to_svg(0)
        assert svg is not None


# ── Diagrams ────────────────────────────────────────────────────────────

class TestFlowChartEdgeCases:
    def test_basic(self):
        fc = FlowChart([
            ('Start', 'start'),
            ('Process', 'process'),
            ('End', 'end'),
        ])
        svg = fc.to_svg(0)
        assert svg is not None

    def test_with_decision(self):
        fc = FlowChart([
            ('Start', 'start'),
            ('Check?', 'decision'),
            ('Done', 'end'),
        ])
        svg = fc.to_svg(0)
        assert svg is not None

    def test_empty(self):
        fc = FlowChart([])
        assert len(fc) == 0


class TestVennDiagramEdgeCases:
    def test_two_sets(self):
        vd = VennDiagram(['A', 'B'])
        svg = vd.to_svg(0)
        assert svg is not None

    def test_three_sets(self):
        vd = VennDiagram(['A', 'B', 'C'])
        svg = vd.to_svg(0)
        assert svg is not None

    def test_single_set_empty(self):
        vd = VennDiagram(['A'])
        assert len(vd) == 0


class TestOrgChartEdgeCases:
    def test_basic(self):
        oc = OrgChart(('CEO', [('CTO', []), ('CFO', [])]))
        svg = oc.to_svg(0)
        assert svg is not None

    def test_deep(self):
        oc = OrgChart(('A', [('B', [('C', [('D', [])])])]))
        svg = oc.to_svg(0)
        assert svg is not None

    def test_leaf_only(self):
        oc = OrgChart(('Boss', []))
        svg = oc.to_svg(0)
        assert svg is not None


class TestMindMapEdgeCases:
    def test_basic(self):
        mm = MindMap(('Root', [('A', []), ('B', []), ('C', [])]))
        svg = mm.to_svg(0)
        assert svg is not None

    def test_nested(self):
        mm = MindMap(('Root', [('A', [('A1', []), ('A2', [])]), ('B', [])]))
        svg = mm.to_svg(0)
        assert svg is not None

    def test_leaf_only(self):
        mm = MindMap(('Center', []))
        svg = mm.to_svg(0)
        assert svg is not None


class TestTreeEdgeCases:
    def test_basic(self):
        t = Tree(('Root', [('A', []), ('B', [])]))
        svg = t.to_svg(0)
        assert svg is not None

    def test_highlight_node(self):
        t = Tree(('Root', [('A', []), ('B', [])]))
        result = t.highlight_node('Root', start=0, end=1)
        assert result is t

    def test_get_node_position(self):
        t = Tree(('Root', [('A', [])]))
        pos = t.get_node_position('Root')
        assert pos is not None


class TestStampEdgeCases:
    def test_basic(self):
        template = Circle(r=20)
        s = Stamp(template, [(100, 100), (200, 200)])
        svg = s.to_svg(0)
        assert svg is not None

    def test_single_point(self):
        template = Rectangle(50, 50)
        s = Stamp(template, [(500, 500)])
        assert len(s) == 1

    def test_empty_points(self):
        template = Circle(r=10)
        s = Stamp(template, [])
        assert len(s) == 0


class TestTimelineBarEdgeCases:
    def test_basic(self):
        tb = TimelineBar({1: 'Event 1', 3: 'Event 2', 5: 'Event 3'})
        svg = tb.to_svg(0)
        assert svg is not None

    def test_single_event(self):
        tb = TimelineBar({0: 'Only'})
        svg = tb.to_svg(0)
        assert svg is not None

    def test_empty(self):
        tb = TimelineBar({})
        svg = tb.to_svg(0)
        assert svg is not None


class TestChessBoardEdgeCases:
    def test_basic(self):
        cb = ChessBoard()
        svg = cb.to_svg(0)
        assert 'rect' in svg

    def test_move_piece(self):
        cb = ChessBoard()
        result = cb.move_piece('e2', 'e4', start=0, end=1)
        assert result is cb


class TestAutomatonEdgeCases:
    def test_basic(self):
        a = Automaton(
            states=['q0', 'q1'],
            transitions=[('q0', 'q1', 'a')],
            initial_state='q0',
            accept_states=['q1'],
        )
        svg = a.to_svg(0)
        assert svg is not None

    def test_highlight_state(self):
        a = Automaton(
            states=['q0', 'q1'],
            transitions=[('q0', 'q1', 'a')],
            initial_state='q0',
            accept_states=['q1'],
        )
        result = a.highlight_state('q0', start=0, end=1)
        assert result is a

    def test_simulate_input(self):
        a = Automaton(
            states=['q0', 'q1'],
            transitions=[('q0', 'q1', 'a')],
            initial_state='q0',
            accept_states=['q1'],
        )
        result = a.simulate_input('a', start=0, delay=0.5)
        assert result is a


class TestNetworkGraphEdgeCases:
    def test_basic(self):
        ng = NetworkGraph(
            nodes=['A', 'B', 'C'],
            edges=[('A', 'B'), ('B', 'C')],
        )
        svg = ng.to_svg(0)
        assert svg is not None

    def test_highlight_node(self):
        ng = NetworkGraph(
            nodes=['A', 'B'],
            edges=[('A', 'B')],
        )
        result = ng.highlight_node('A', start=0, end=1)
        assert result is ng

    def test_get_node_position(self):
        ng = NetworkGraph(
            nodes=['A', 'B'],
            edges=[('A', 'B')],
        )
        pos = ng.get_node_position('A')
        assert pos is not None


class TestPeriodicTableEdgeCases:
    def test_basic(self):
        pt = PeriodicTable()
        svg = pt.to_svg(0)
        assert svg is not None

    def test_highlight(self):
        pt = PeriodicTable()
        result = pt.highlight('Fe', start=0, end=1)
        assert result is pt

    def test_highlight_nonexistent(self):
        pt = PeriodicTable()
        result = pt.highlight('Xx', start=0, end=1)
        assert result is pt  # silent no-op


class TestBohrAtomEdgeCases:
    def test_basic(self):
        ba = BohrAtom(protons=6, electrons=[2, 4])
        svg = ba.to_svg(0)
        assert svg is not None

    def test_hydrogen(self):
        ba = BohrAtom(protons=1, electrons=[1])
        svg = ba.to_svg(0)
        assert svg is not None


# ── UI Components ───────────────────────────────────────────────────────

class TestCodeEdgeCases:
    def test_basic(self):
        c = Code('def hello():\n    print("hi")', language='python')
        svg = c.to_svg(0)
        assert svg is not None

    def test_empty(self):
        c = Code('')
        svg = c.to_svg(0)
        assert svg is not None

    def test_highlight_lines(self):
        c = Code('line1\nline2\nline3')
        result = c.highlight_lines([1, 2], start=0, end=1)
        assert isinstance(result, VCollection)


class TestVariableEdgeCases:
    def test_basic(self):
        v = Variable('x', 42)
        svg = v.to_svg(0)
        assert svg is not None

    def test_set_value(self):
        v = Variable('x', 0)
        result = v.set_value(100, start=0)
        assert result is v

    def test_animate_value(self):
        v = Variable('x', 0)
        result = v.animate_value(100, start=0, end=1)
        assert result is v

    def test_tracker(self):
        v = Variable('x', 10)
        assert v.tracker is not None


class TestTagCloudEdgeCases:
    def test_basic(self):
        tc = TagCloud([('python', 10), ('java', 8), ('rust', 5)])
        svg = tc.to_svg(0)
        assert svg is not None

    def test_empty(self):
        tc = TagCloud([])
        assert len(tc) == 0

    def test_same_weights(self):
        tc = TagCloud([('a', 5), ('b', 5), ('c', 5)])
        svg = tc.to_svg(0)
        assert svg is not None


class TestStatusIndicatorEdgeCases:
    def test_online(self):
        si = StatusIndicator('Server', 'online')
        svg = si.to_svg(0)
        assert svg is not None

    def test_offline(self):
        si = StatusIndicator('Server', 'offline')
        svg = si.to_svg(0)
        assert svg is not None

    def test_custom_status(self):
        si = StatusIndicator('Custom', '#FF00FF')
        svg = si.to_svg(0)
        assert svg is not None


class TestMeterEdgeCases:
    def test_basic(self):
        m = Meter(0.75)
        svg = m.to_svg(0)
        assert svg is not None

    def test_zero(self):
        m = Meter(0)
        svg = m.to_svg(0)
        assert svg is not None

    def test_full(self):
        m = Meter(1.0)
        svg = m.to_svg(0)
        assert svg is not None


class TestBreadcrumbEdgeCases:
    def test_basic(self):
        bc = Breadcrumb(['Home', 'Products', 'Item'])
        svg = bc.to_svg(0)
        assert svg is not None

    def test_single(self):
        bc = Breadcrumb(['Home'])
        svg = bc.to_svg(0)
        assert svg is not None


class TestSpeechBubbleEdgeCases:
    def test_basic(self):
        sb = SpeechBubble('Hello world!')
        svg = sb.to_svg(0)
        assert svg is not None

    def test_down_tail(self):
        sb = SpeechBubble('Hi', tail_direction='down')
        svg = sb.to_svg(0)
        assert svg is not None

    def test_up_tail(self):
        sb = SpeechBubble('Hi', tail_direction='up')
        svg = sb.to_svg(0)
        assert svg is not None

    def test_left_tail(self):
        sb = SpeechBubble('Hi', tail_direction='left')
        svg = sb.to_svg(0)
        assert svg is not None


class TestStepperEdgeCases:
    def test_basic(self):
        s = Stepper(['Step 1', 'Step 2', 'Step 3'])
        svg = s.to_svg(0)
        assert svg is not None

    def test_advance(self):
        s = Stepper(['A', 'B', 'C'])
        result = s.advance(0, 1, start=0, end=1)
        assert result is s


class TestChecklistEdgeCases:
    def test_basic(self):
        cl = Checklist(('Item 1', False), ('Item 2', True), ('Item 3', False))
        svg = cl.to_svg(0)
        assert svg is not None

    def test_check_item(self):
        cl = Checklist(('A', False), ('B', False))
        result = cl.check_item(0, start=0)
        assert result is cl

    def test_check_out_of_bounds(self):
        cl = Checklist(('A', False))
        result = cl.check_item(5)
        assert result is cl  # silent no-op

    def test_reveal_items(self):
        cl = Checklist(('A', False), ('B', False), ('C', False))
        result = cl.reveal_items(start=0, end=2)
        assert result is cl

    def test_string_items(self):
        cl = Checklist('A', 'B', 'C')
        svg = cl.to_svg(0)
        assert svg is not None


class TestFilmstripEdgeCases:
    def test_basic(self):
        circles = [Circle(r=30) for _ in range(4)]
        f = Filmstrip(circles)
        svg = f.to_svg(0)
        assert svg is not None

    def test_highlight_frame(self):
        circles = [Circle(r=30) for _ in range(3)]
        f = Filmstrip(circles)
        result = f.highlight_frame(1, start=0, end=1)
        assert result is f


class TestIconGridEdgeCases:
    def test_basic(self):
        data = [(3, '#FF0000'), (4, '#00FF00'), (3, '#0000FF')]
        ig = IconGrid(data, cols=5)
        svg = ig.to_svg(0)
        assert svg is not None

    def test_single_color(self):
        data = [(10, '#58C4DD')]
        ig = IconGrid(data, cols=5)
        svg = ig.to_svg(0)
        assert svg is not None


# ── Data Structure Edge Cases ───────────────────────────────────────────

class TestArrayEdgeCases:
    def test_highlight_out_of_bounds(self):
        arr = Array([1, 2, 3])
        with pytest.raises(IndexError):
            arr.highlight_cell(5)

    def test_set_value_out_of_bounds(self):
        arr = Array([1, 2])
        with pytest.raises(IndexError):
            arr.set_value(5, 99)

    def test_swap_cells(self):
        arr = Array([1, 2, 3])
        result = arr.swap_cells(0, 2, start=0, end=1)
        assert result is arr

    def test_sort(self):
        arr = Array([3, 1, 2])
        result = arr.sort(start=0, end=2)
        assert result is arr

    def test_reverse(self):
        arr = Array([1, 2, 3])
        result = arr.reverse(start=0, end=2)
        assert result is arr

    def test_add_pointer(self):
        arr = Array([10, 20])
        result = arr.add_pointer(0, label='ptr')
        assert result is not None

    def test_add_pointer_out_of_bounds(self):
        arr = Array([10, 20])
        result = arr.add_pointer(5)
        assert result is arr  # returns self for invalid index


class TestStackEdgeCases:
    def test_pop_empty(self):
        s = Stack()
        result = s.pop()
        assert result is s

    def test_peek_empty(self):
        s = Stack()
        assert s.peek() is None

    def test_is_empty(self):
        s = Stack()
        assert s.is_empty()
        s.push(42)
        assert not s.is_empty()


class TestQueueEdgeCases:
    def test_dequeue_empty(self):
        q = Queue()
        result = q.dequeue()
        assert result is q

    def test_peek_empty(self):
        q = Queue()
        assert q.peek() is None

    def test_is_empty(self):
        q = Queue()
        assert q.is_empty()
        q.enqueue(42)
        assert not q.is_empty()


class TestLinkedListEdgeCases:
    def test_highlight_out_of_bounds(self):
        ll = LinkedList([1, 2, 3])
        result = ll.highlight_node(10)
        assert result is ll  # silent no-op

    def test_remove_node_out_of_bounds(self):
        ll = LinkedList([1, 2])
        result = ll.remove_node(5)
        assert result is ll  # silent no-op

    def test_append_and_remove(self):
        ll = LinkedList([1])
        ll.append_node(2, start=0, end=0.5)
        assert len(ll._nodes) == 2
        ll.remove_node(0, start=1, end=1.5)
        assert len(ll._nodes) == 1


class TestBinaryTreeEdgeCases:
    def test_basic(self):
        bt = BinaryTree((1, (2, 4, 5), (3, 6, 7)))
        svg = bt.to_svg(0)
        assert svg is not None

    def test_leaf(self):
        bt = BinaryTree(42)
        svg = bt.to_svg(0)
        assert svg is not None

    def test_highlight_node(self):
        bt = BinaryTree((1, 2, 3))
        result = bt.highlight_node(0, start=0, end=0.5)
        assert result is bt

    def test_traverse(self):
        bt = BinaryTree((1, 2, 3))
        result = bt.traverse(start=0, delay=0.2)
        assert result is bt


class TestArrayVizEdgeCases:
    def test_swap_same_index(self):
        av = ArrayViz([1, 2, 3])
        result = av.swap(0, 0)
        assert result is av

    def test_swap_out_of_bounds(self):
        av = ArrayViz([1, 2])
        result = av.swap(0, 5)
        assert result is av

    def test_set_value_out_of_bounds(self):
        av = ArrayViz([1, 2])
        result = av.set_value(5, 99)
        assert result is av


class TestStackVizEdgeCases:
    def test_pop_empty(self):
        sv = StackViz([])
        result = sv.pop()
        assert result is sv

    def test_push_and_pop(self):
        sv = StackViz([1])
        sv.push(2, start=0, end=0.5)
        assert len(sv.values) == 2
        sv.pop(start=1, end=1.5)
        assert len(sv.values) == 1


class TestQueueVizEdgeCases:
    def test_dequeue_empty(self):
        qv = QueueViz([])
        result = qv.dequeue()
        assert result is qv

    def test_enqueue_and_dequeue(self):
        qv = QueueViz([1])
        qv.enqueue(2, start=0, end=0.5)
        assert len(qv.values) == 2
        qv.dequeue(start=1, end=1.5)
        assert len(qv.values) == 1

    def test_highlight(self):
        qv = QueueViz([1, 2, 3])
        result = qv.highlight(1, start=0, end=0.5)
        assert result is qv

    def test_highlight_out_of_bounds(self):
        qv = QueueViz([1])
        result = qv.highlight(5)
        assert result is qv


class TestLinkedListVizEdgeCases:
    def test_highlight_out_of_bounds(self):
        llv = LinkedListViz([1, 2])
        result = llv.highlight(5)
        assert result is llv

    def test_traverse(self):
        llv = LinkedListViz([1, 2, 3])
        result = llv.traverse(start=0, delay=0.3)
        assert result is llv
