"""Tests for diagram classes with minimal test coverage."""
from vectormation.objects import (
    FlowChart, VennDiagram, ChessBoard, TimelineBar, Stamp,
    PeriodicTable, Automaton, NetworkGraph, Tree, MindMap, OrgChart,
    Circle, Dot, VectorMathAnim,
)


class TestFlowChart:
    def test_creates_horizontal(self):
        fc = FlowChart(['A', 'B', 'C'], direction='right', creation=0)
        assert len(fc.objects) > 0

    def test_creates_vertical(self):
        fc = FlowChart(['A', 'B', 'C'], direction='down', creation=0)
        assert len(fc.objects) > 0

    def test_repr(self):
        fc = FlowChart(['A', 'B', 'C'], creation=0)
        assert '3' in repr(fc)

    def test_single_step(self):
        fc = FlowChart(['A'], creation=0)
        assert len(fc._boxes) == 1

    def test_has_boxes_and_labels(self):
        fc = FlowChart(['Start', 'End'], creation=0)
        assert len(fc._boxes) == 2
        assert len(fc._labels) == 2

    def test_renders(self):
        fc = FlowChart(['A', 'B'], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(fc)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestVennDiagram:
    def test_two_circles(self):
        vd = VennDiagram(['A', 'B'], creation=0)
        assert len(vd.objects) > 0

    def test_three_circles(self):
        vd = VennDiagram(['A', 'B', 'C'], creation=0)
        assert len(vd.objects) > 0

    def test_repr(self):
        vd = VennDiagram(['A', 'B'], creation=0)
        assert 'VennDiagram' in repr(vd)

    def test_invalid_count_returns_empty(self):
        vd = VennDiagram(['A'], creation=0)
        assert len(vd.objects) == 0

    def test_custom_colors(self):
        vd = VennDiagram(['A', 'B'], colors=['#FF0000', '#00FF00'], creation=0)
        assert len(vd.objects) > 0

    def test_renders(self):
        vd = VennDiagram(['A', 'B'], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(vd)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestChessBoard:
    def test_default_position(self):
        cb = ChessBoard(creation=0)
        assert len(cb.objects) > 0

    def test_custom_fen(self):
        cb = ChessBoard(fen='8/8/8/8/8/8/8/8', creation=0)
        assert len(cb.objects) > 0

    def test_renders(self):
        cb = ChessBoard(creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(cb)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestTimelineBar:
    def test_creates(self):
        tb = TimelineBar(markers={0: 'Start', 5: 'Middle', 10: 'End'}, creation=0)
        assert len(tb.objects) > 0

    def test_renders(self):
        tb = TimelineBar(markers={0: 'Start', 10: 'End'}, creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(tb)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestStamp:
    def test_creates_copies(self):
        template = Dot(cx=0, cy=0, creation=0)
        s = Stamp(template, [(100, 100), (200, 200), (300, 300)], creation=0)
        assert len(s.objects) == 3

    def test_repr(self):
        template = Dot(cx=0, cy=0, creation=0)
        s = Stamp(template, [(100, 100), (200, 200)], creation=0)
        assert '2' in repr(s)

    def test_single_point(self):
        template = Circle(r=20, creation=0)
        s = Stamp(template, [(500, 500)], creation=0)
        assert len(s.objects) == 1

    def test_renders(self):
        template = Dot(cx=0, cy=0, creation=0)
        s = Stamp(template, [(100, 100), (200, 200)], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(s)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestPeriodicTable:
    def test_creates(self):
        pt = PeriodicTable(creation=0)
        assert len(pt.objects) > 0

    def test_renders(self):
        pt = PeriodicTable(creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(pt)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestAutomaton:
    def test_creates(self):
        a = Automaton(
            states=['q0', 'q1', 'q2'],
            transitions=[('q0', 'q1', 'a'), ('q1', 'q2', 'b')],
            accept_states={'q2'},
            initial_state='q0',
            creation=0,
        )
        assert len(a.objects) > 0

    def test_repr(self):
        a = Automaton(states=['q0', 'q1'], transitions=[], creation=0)
        r = repr(a)
        assert 'Automaton' in r

    def test_empty_states(self):
        a = Automaton(states=[], transitions=[], creation=0)
        assert len(a.objects) == 0

    def test_renders(self):
        a = Automaton(
            states=['A', 'B'],
            transitions=[('A', 'B', 'x')],
            creation=0,
        )
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(a)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestNetworkGraph:
    def test_creates_from_list(self):
        ng = NetworkGraph(
            nodes=['A', 'B', 'C'],
            edges=[(0, 1), (1, 2)],
            creation=0,
        )
        assert len(ng.objects) > 0

    def test_creates_directed(self):
        ng = NetworkGraph(
            nodes=['A', 'B'],
            edges=[(0, 1)],
            directed=True,
            creation=0,
        )
        assert len(ng.objects) > 0

    def test_repr(self):
        ng = NetworkGraph(nodes=['A', 'B'], creation=0)
        r = repr(ng)
        assert 'NetworkGraph' in r or 'Network' in r

    def test_renders(self):
        ng = NetworkGraph(
            nodes=['A', 'B', 'C'],
            edges=[(0, 1), (1, 2), (0, 2)],
            creation=0,
        )
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(ng)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestTree:
    def test_creates_from_tuple(self):
        tree_data = ('root', [('child1', []), ('child2', [('grandchild', [])])])
        t = Tree(tree_data, creation=0)
        assert len(t.objects) > 0

    def test_creates_from_dict(self):
        tree_data = {'root': {'child1': {}, 'child2': {'grandchild': {}}}}
        t = Tree(tree_data, creation=0)
        assert len(t.objects) > 0

    def test_repr(self):
        t = Tree(('A', [('B', [])]), creation=0)
        r = repr(t)
        assert 'Tree' in r

    def test_renders(self):
        t = Tree(('A', [('B', []), ('C', [])]), creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(t)
        svg = v.generate_frame_svg(time=0)
        assert svg

    def test_single_node(self):
        t = Tree(('root', []), creation=0)
        assert len(t.objects) > 0


class TestOrgChart:
    def test_creates(self):
        root = ('CEO', [('CTO', [('Dev1', []), ('Dev2', [])]), ('CFO', [])])
        oc = OrgChart(root, creation=0)
        assert len(oc.objects) > 0

    def test_repr(self):
        root = ('Boss', [('Worker', [])])
        oc = OrgChart(root, creation=0)
        r = repr(oc)
        assert 'OrgChart' in r

    def test_renders(self):
        root = ('CEO', [('CTO', []), ('CFO', [])])
        oc = OrgChart(root, creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(oc)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestMindMap:
    def test_creates(self):
        root = ('Central', [('Branch1', []), ('Branch2', [('Leaf', [])])])
        mm = MindMap(root, creation=0)
        assert len(mm.objects) > 0

    def test_repr(self):
        root = ('Main', [('Sub', [])])
        mm = MindMap(root, creation=0)
        r = repr(mm)
        assert 'MindMap' in r

    def test_no_children(self):
        root = ('Alone', [])
        mm = MindMap(root, creation=0)
        assert len(mm.objects) > 0

    def test_renders(self):
        root = ('Main', [('A', []), ('B', []), ('C', [])])
        mm = MindMap(root, creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_diagrams')
        v.add(mm)
        svg = v.generate_frame_svg(time=0)
        assert svg
