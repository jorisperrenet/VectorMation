import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/network_graph')
canvas.set_background()

# Create a directed graph with spring layout
graph = NetworkGraph(
    nodes={'s': 'S', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 't': 'T'},
    edges=[
        ('s', 'a', '10'), ('s', 'b', '8'),
        ('a', 'c', '5'), ('a', 'd', '7'),
        ('b', 'c', '3'), ('b', 'd', '6'),
        ('c', 't', '4'), ('d', 't', '9'),
    ],
    layout='spring',
    directed=True,
    node_r=35,
)
graph.fadein(0, 1)

# Highlight a path through the network
graph.highlight_node('s', 1.5, 2.5, color='#83C167')
graph.highlight_node('a', 2.0, 3.0, color='#83C167')
graph.highlight_node('d', 2.5, 3.5, color='#83C167')
graph.highlight_node('t', 3.0, 4.0, color='#83C167')

title = Text(text='Network Flow Graph', x=960, y=60,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(graph, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
