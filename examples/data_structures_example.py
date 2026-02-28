"""Showcase data structure visualizations: Array, Stack, Queue, LinkedList."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/data_structures')

# Title
title = Text("Data Structures", x=960, y=60, font_size=48, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(start=0, end=0.5)

# --- Array with operations ---
arr = Array([3, 1, 4, 1, 5, 9], x=200, y=200, cell_width=60, cell_height=50,
            font_size=28, fill='#2C3E50', text_color='#ECF0F1', border_color='#3498DB')
arr.fadein(start=0.5, end=1.5)
arr.highlight_cell(2, start=2, end=3, color='#E74C3C')  # Highlight index 2
arr.swap_cells(0, 3, start=3.5, end=4.5)  # Swap elements

# --- Stack ---
stack = StackViz(['A', 'B', 'C'], x=700, y=200, cell_width=80, cell_height=45,
                 font_size=24, fill='#2C3E50')
stack.fadein(start=1, end=2)
stack.push('D', start=4, end=5)
stack.pop(start=6, end=7)

# --- Queue ---
queue = QueueViz(['X', 'Y', 'Z'], x=1050, y=200, cell_width=60, cell_height=45,
                 font_size=24, fill='#2C3E50')
queue.fadein(start=1.5, end=2.5)
queue.enqueue('W', start=5, end=6)
queue.dequeue(start=7, end=8)

# --- LinkedList ---
ll = LinkedListViz([10, 20, 30, 40], x=200, y=500,
                   font_size=22, node_fill='#2C3E50')
ll.fadein(start=2, end=3)

# Labels
for lbl, lx in [("Array", 350), ("Stack", 740), ("Queue", 1200), ("LinkedList", 400)]:
    ly = 150 if lbl != "LinkedList" else 460
    t = Text(lbl, x=lx, y=ly, font_size=20, fill='#888', stroke_width=0, creation=0)
    t.fadein(start=0.5, end=1)
    v.add(t)

# Fade everything out
for obj in [arr, stack, queue, ll, title]:
    obj.fadeout(start=10, end=11)

v.add(title, arr, stack, queue, ll)
if not args.no_display:
    v.browser_display(end=args.end or 12, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
