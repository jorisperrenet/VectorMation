"""Data Structures Demo — Array, Stack, Queue, and LinkedList animations.

Demonstrates array operations (highlight, sort), stack push/pop,
queue enqueue/dequeue, and linked list traversal with color highlighting.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/data_structures_demo')
canvas.set_background()

T = 12.0

# -- Colors -------------------------------------------------------------------
ACCENT    = '#58C4DD'
GREEN     = '#83C167'
ORANGE    = '#F5A623'
PINK      = '#FF6B6B'
YELLOW    = '#F5C542'
PURPLE    = '#9B59B6'

# =============================================================================
# Phase 1: Array — highlight cells, then animate sort (0 – 3s)
# =============================================================================
phase1_label = Text(
    text='Array', x=960, y=80, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
phase1_label.fadein(0.0, 0.3)
phase1_label.fadeout(2.6, 3.0)
canvas.add(phase1_label)

phase1_sub = Text(
    text='highlight cells, then sort', x=960, y=130, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
)
phase1_sub.fadein(0.1, 0.4)
phase1_sub.fadeout(2.6, 3.0)
canvas.add(phase1_sub)

arr = Array(
    values=[5, 2, 8, 1, 9, 3],
    x=560, y=400,
    cell_width=100, cell_height=70,
    font_size=30, fill='#1e1e2e', border_color=ACCENT,
    creation=0,
)
arr.fadein(0.2, 0.6)

# Highlight individual cells one by one
arr.highlight_cell(0, start=0.6, end=1.0, color=YELLOW)
arr.highlight_cell(2, start=0.8, end=1.2, color=ORANGE)
arr.highlight_cell(4, start=1.0, end=1.4, color=PINK)

# Animate bubble sort
arr.sort(start=1.5, end=2.8, delay=0.18)

arr.fadeout(2.7, 3.0)
canvas.add(arr)

# =============================================================================
# Phase 2: Stack — push values, then pop a few (3 – 6s)
# =============================================================================
phase2_label = Text(
    text='Stack (LIFO)', x=960, y=80, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
    creation=3.0,
)
phase2_label.fadein(3.0, 3.3)
phase2_label.fadeout(5.6, 6.0)
canvas.add(phase2_label)

phase2_sub = Text(
    text='push values, then pop', x=960, y=130, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
    creation=3.0,
)
phase2_sub.fadein(3.1, 3.4)
phase2_sub.fadeout(5.6, 6.0)
canvas.add(phase2_sub)

stack = Stack(
    x=860, y=650,
    cell_width=120, cell_height=55,
    font_size=26, fill='#1e1e2e', border_color=PURPLE,
    creation=3.0,
)
stack.fadein(3.2, 3.5)

# Push values one by one
stack.push(42, start=3.4, end=3.8)
stack.push(17, start=3.8, end=4.2)
stack.push(85, start=4.2, end=4.6)
stack.push(33, start=4.6, end=5.0)

# Pop a couple of values
stack.pop(start=5.0, end=5.3)
stack.pop(start=5.3, end=5.6)

stack.fadeout(5.7, 6.0)
canvas.add(stack)

# =============================================================================
# Phase 3: Queue — enqueue values, then dequeue (6 – 9s)
# =============================================================================
phase3_label = Text(
    text='Queue (FIFO)', x=960, y=80, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
    creation=6.0,
)
phase3_label.fadein(6.0, 6.3)
phase3_label.fadeout(8.6, 9.0)
canvas.add(phase3_label)

phase3_sub = Text(
    text='enqueue values, then dequeue', x=960, y=130, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
    creation=6.0,
)
phase3_sub.fadein(6.1, 6.4)
phase3_sub.fadeout(8.6, 9.0)
canvas.add(phase3_sub)

queue = Queue(
    x=460, y=440,
    cell_width=90, cell_height=65,
    font_size=26, fill='#1e1e2e', border_color=GREEN,
    creation=6.0,
)
queue.fadein(6.2, 6.5)

# Enqueue values
queue.enqueue(10, start=6.4, end=6.8)
queue.enqueue(20, start=6.8, end=7.2)
queue.enqueue(30, start=7.2, end=7.6)
queue.enqueue(40, start=7.6, end=8.0)

# Dequeue from front
queue.dequeue(start=8.0, end=8.4)
queue.dequeue(start=8.4, end=8.8)

queue.fadeout(8.7, 9.0)
canvas.add(queue)

# =============================================================================
# Phase 4: LinkedList — create and traverse with highlighting (9 – 12s)
# =============================================================================
phase4_label = Text(
    text='Linked List', x=960, y=80, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
    creation=9.0,
)
phase4_label.fadein(9.0, 9.3)
phase4_label.fadeout(11.6, 12.0)
canvas.add(phase4_label)

phase4_sub = Text(
    text='traverse with node highlighting', x=960, y=130, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
    creation=9.0,
)
phase4_sub.fadein(9.1, 9.4)
phase4_sub.fadeout(11.6, 12.0)
canvas.add(phase4_sub)

ll = LinkedList(
    values=['A', 'B', 'C', 'D', 'E'],
    x=260, y=420,
    node_width=90, node_height=55,
    gap=50, font_size=26,
    fill='#1e1e2e', border_color=ACCENT, arrow_color='#fff',
    creation=9.0,
)
ll.fadein(9.2, 9.6)

# Traverse: highlight each node sequentially
delay = 0.4
for i in range(5):
    t = 9.7 + i * delay
    ll.highlight_node(i, start=t, end=t + delay, color=YELLOW)

ll.fadeout(11.6, 12.0)
canvas.add(ll)

# -- Render -------------------------------------------------------------------
canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
