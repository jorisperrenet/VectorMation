"""Diagrams Demo — Automaton, FlowChart, VennDiagram, NetworkGraph."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/diagrams_showcase')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1: Title + Automaton (0 – 3s)
# =============================================================================
title = Text(
    text='Diagrams', x=960, y=70, font_size=52,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
title.fadein(0.0, 0.5)
title.fadeout(2.5, 3.0)
canvas.add(title)

# Finite state machine: 3 states with transitions
automaton = Automaton(
    states=['q0', 'q1', 'q2'],
    transitions=[
        ('q0', 'q1', 'a'),
        ('q1', 'q2', 'b'),
        ('q2', 'q0', 'c'),
        ('q1', 'q1', 'a'),
    ],
    accept_states={'q2'},
    initial_state='q0',
    cx=960, cy=500, radius=200, state_r=40, font_size=22,
)
automaton.fadein(0.3, 1.0)
automaton.highlight_state('q0', start=1.2, end=1.8)
automaton.highlight_transition('q0', 'q1', start=1.8, end=2.4)
automaton.fadeout(2.5, 3.0)
canvas.add(automaton)

sub1 = Text(
    text='Automaton — Finite State Machine', x=960, y=860, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
)
sub1.fadein(0.5, 1.0)
sub1.fadeout(2.5, 3.0)
canvas.add(sub1)

# =============================================================================
# Phase 2: FlowChart (3 – 6s)
# =============================================================================
flow_title = Text(
    text='FlowChart', x=960, y=70, font_size=48,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=3.0,
)
flow_title.fadein(3.0, 3.5)
flow_title.fadeout(5.5, 6.0)
canvas.add(flow_title)

flow = FlowChart(
    steps=['Start', 'Input', 'Process', 'Output', 'End'],
    direction='right',
    x=130, y=440,
    box_width=240, box_height=70, spacing=100,
    box_color='#4ECDC4', text_color='#fff', arrow_color='#888',
    font_size=22, corner_radius=10,
    creation=3.0,
)
flow.fadein(3.0, 3.8)
flow.fadeout(5.5, 6.0)
canvas.add(flow)

sub2 = Text(
    text='Simple Algorithm Flow', x=960, y=860, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle', creation=3.0,
)
sub2.fadein(3.3, 3.8)
sub2.fadeout(5.5, 6.0)
canvas.add(sub2)

# =============================================================================
# Phase 3: VennDiagram (6 – 9s)
# =============================================================================
venn_title = Text(
    text='VennDiagram', x=960, y=70, font_size=48,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=6.0,
)
venn_title.fadein(6.0, 6.5)
venn_title.fadeout(8.5, 9.0)
canvas.add(venn_title)

venn = VennDiagram(
    labels=['Python', 'Math', 'Art'],
    radius=170,
    x=960, y=480,
    colors=['#58C4DD', '#FF6B6B', '#83C167'],
    font_size=26,
    creation=6.0,
)
venn.fadein(6.0, 6.8)
venn.fadeout(8.5, 9.0)
canvas.add(venn)

sub3 = Text(
    text='Overlapping Sets', x=960, y=860, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle', creation=6.0,
)
sub3.fadein(6.3, 6.8)
sub3.fadeout(8.5, 9.0)
canvas.add(sub3)

# =============================================================================
# Phase 4: NetworkGraph (9 – 12s)
# =============================================================================
net_title = Text(
    text='NetworkGraph', x=960, y=70, font_size=48,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=9.0,
)
net_title.fadein(9.0, 9.5)
net_title.fadeout(11.0, 11.5)
canvas.add(net_title)

nodes = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F'}
edges = [
    (0, 1), (0, 2), (1, 3), (2, 3),
    (2, 4), (3, 5), (4, 5), (1, 4),
]

net = NetworkGraph(
    nodes=nodes, edges=edges,
    cx=960, cy=500, radius=250, node_r=35, font_size=22,
    layout='circular', directed=False,
    creation=9.0,
)
net.fadein(9.0, 9.8)
net.highlight_node(0, start=10.0, end=10.6)
net.highlight_node(3, start=10.3, end=10.9)
net.fadeout(11.0, 11.8)
canvas.add(net)

sub4 = Text(
    text='Graph with 6 Nodes and 8 Edges', x=960, y=860, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle', creation=9.0,
)
sub4.fadein(9.3, 9.8)
sub4.fadeout(11.0, 11.5)
canvas.add(sub4)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
