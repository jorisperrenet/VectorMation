"""Data structure visualizations: ArrayViz, StackViz, QueueViz, LinkedListViz."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    ArrayViz, StackViz, QueueViz, LinkedListViz,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/data_structures_visual')

# Title
title = Text(text='Data Structure Operations', x=ORIGIN[0], y=40,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Array: highlight, swap, pointer ───────────────────────────────────
label1 = Text(text='ArrayViz: highlight, swap, pointer', x=480, y=95,
              font_size=20, fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label1)

arr = ArrayViz([7, 3, 9, 1, 5], cell_size=70, y=130, creation=0.5)
arr.center_to_pos(480, 180, start=0.5)
arr.stagger('fadein', start=0.5, end=1.5)
canvas.add(arr)

# Highlight cells
arr.highlight(0, start=1.5, end=2.0, color='#FF6B6B')
arr.highlight(3, start=1.5, end=2.0, color='#FF6B6B')

# Swap elements
arr.swap(0, 3, start=2.0, end=3.0)

# Add pointer
ptr = arr.pointer(2, label='mid', start=3.0)
canvas.add(ptr)

# ── Stack: push and pop ──────────────────────────────────────────────
label2 = Text(text='StackViz: push & pop', x=1440, y=95,
              font_size=20, fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label2)

stack = StackViz([10, 20], cell_width=110, cell_height=45,
                 creation=0.5)
stack.center_to_pos(1440, 200, start=0.5)
stack.stagger('fadein', start=0.5, end=1.5)
canvas.add(stack)

# Push two values
stack.push(30, start=2.0, end=2.5)
stack.push(40, start=2.8, end=3.3)

# Pop top
stack.pop(start=3.8, end=4.3)

# ── Queue: enqueue and dequeue ────────────────────────────────────────
label3 = Text(text='QueueViz: enqueue & dequeue', x=480, y=380,
              font_size=20, fill='#888', text_anchor='middle', creation=4.5)
canvas.add(label3)

queue = QueueViz(['A', 'B', 'C'], cell_width=75, cell_height=55,
                 creation=4.5)
queue.center_to_pos(480, 480, start=4.5)
queue.stagger('fadein', start=4.5, end=5.5)
canvas.add(queue)

# Enqueue
queue.enqueue('D', start=5.5, end=6.0)
queue.enqueue('E', start=6.0, end=6.5)

# Dequeue
queue.dequeue(start=7.0, end=7.5)

# ── LinkedList: traverse and highlight ────────────────────────────────
label4 = Text(text='LinkedListViz: traverse', x=1200, y=380,
              font_size=20, fill='#888', text_anchor='middle', creation=4.5)
canvas.add(label4)

ll = LinkedListViz([10, 20, 30, 40], node_radius=30, spacing=130,
                   creation=4.5)
ll.center_to_pos(1200, 480, start=4.5)
ll.stagger('fadein', start=4.5, end=5.5)
canvas.add(ll)

# Traverse animation
ll.traverse(start=6.0, delay=0.6, color='#50FA7B')

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 9,
                           fps=args.fps, port=args.port)
