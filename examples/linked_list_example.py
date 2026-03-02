import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/linked_list')
canvas.set_background()

# Create a linked list
ll = LinkedListViz([10, 20, 30, 40, 50], node_radius=40, spacing=160)
ll.fadein(0, 1)

title = Text(text='Linked List Traversal', x=960, y=120,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Traverse the list with highlighted nodes
ll.traverse(start=1.5, delay=0.8, color='#FFFF00')

canvas.add_objects(ll, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/linked_list_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
