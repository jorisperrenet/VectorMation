import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/tree')
canvas.set_background()

# Binary search tree
tree = Tree(
    ('8', [
        ('3', [
            ('1', []),
            ('6', [
                ('4', []),
                ('7', []),
            ]),
        ]),
        ('10', [
            ('', []),
            ('14', [
                ('13', []),
                ('', []),
            ]),
        ]),
    ]),
    cx=960, cy=120, h_spacing=100, v_spacing=120, node_r=25, font_size=20,
)
tree.fadein(0, 1)

# Highlight search path: 8 -> 3 -> 6 -> 4
tree.highlight_node('8', 1.5, 2.5, color='#83C167')
tree.highlight_node('3', 2.0, 3.0, color='#83C167')
tree.highlight_node('6', 2.5, 3.5, color='#83C167')
tree.highlight_node('4', 3.0, 4.0, color='#FFFF00')

title = Text(text='Binary Search Tree', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(tree, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
