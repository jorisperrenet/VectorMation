"""Data structure operations demo: push, pop, enqueue, dequeue, sort, traverse."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN,
    Array, Stack, Queue, LinkedList,
    parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/data_structures_ops')

# Title
title = Text(text='Data Structure Operations', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Array with bubble sort ────────────────────────────────────────────
arr_label = Text(text='Array — Bubble Sort', x=ORIGIN[0], y=120,
                 font_size=24, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(arr_label)

arr = Array([5, 2, 8, 1, 9, 3], y=200, creation=0.5)
canvas.add(arr)
arr.sort(start=1, end=4.5, delay=0.2)

# ── Stack with push/pop ──────────────────────────────────────────────
stack_label = Text(text='Stack — Push & Pop', x=350, y=370,
                   font_size=24, fill='#aaa', text_anchor='middle', creation=5)
canvas.add(stack_label)

stack = Stack([10, 20], x=300, y=600, creation=5)
canvas.add(stack)

# Push three items
t = 5.5
for val in [30, 40, 50]:
    stack.push(val, start=t, end=t + 0.4)
    t += 0.6

# Pop two items
t += 0.3
for _ in range(2):
    stack.pop(start=t, end=t + 0.4)
    t += 0.6

# ── Queue with enqueue/dequeue ────────────────────────────────────────
q_label = Text(text='Queue — Enqueue & Dequeue', x=1300, y=370,
               font_size=24, fill='#aaa', text_anchor='middle', creation=5)
canvas.add(q_label)

queue = Queue(['A', 'B'], x=1050, y=500, creation=5)
canvas.add(queue)

t = 5.5
for val in ['C', 'D', 'E']:
    queue.enqueue(val, start=t, end=t + 0.4)
    t += 0.6

t += 0.3
for _ in range(2):
    queue.dequeue(start=t, end=t + 0.4)
    t += 0.6

# ── Linked list with append/traverse ──────────────────────────────────
ll_label = Text(text='Linked List — Append & Traverse', x=ORIGIN[0], y=700,
                font_size=24, fill='#aaa', text_anchor='middle', creation=9)
canvas.add(ll_label)

ll = LinkedList([1, 2, 3], y=780, creation=9)
canvas.add(ll)

ll.append_node(4, start=9.5, end=10)
ll.append_node(5, start=10.2, end=10.7)
# Highlight nodes one by one to simulate traversal
for i in range(5):
    ll.highlight_node(i, start=11 + i * 0.4, end=11 + i * 0.4 + 0.35, color='#E9C46A')

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 13,
                           fps=args.fps, port=args.port)
