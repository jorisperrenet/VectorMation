"""Showcase data structure visualizations: Array, Stack, Queue, LinkedList."""
from vectormation.objects import *

v = VectorMathAnim(duration=12)

# Title
title = Text("Data Structures", x=960, y=60, font_size=48, fill='#fff')
title.fadein(start=0, end=0.5)

# --- Array with operations ---
arr = Array([3, 1, 4, 1, 5, 9], x=200, y=200, cell_width=60, cell_height=50,
            font_size=28, fill='#2C3E50', text_fill='#ECF0F1', stroke='#3498DB')
arr.fadein(start=0.5, end=1.5)
arr.highlight_cell(2, start=2, end=3, color='#E74C3C')  # Highlight index 2
arr.swap_cells(0, 3, start=3.5, end=4.5)  # Swap elements

# --- Stack ---
stack = StackViz(['A', 'B', 'C'], x=700, y=200, cell_width=80, cell_height=45,
                 font_size=24, fill='#2C3E50', text_fill='#ECF0F1', stroke='#2ECC71')
stack.fadein(start=1, end=2)
stack.push('D', start=4, end=5)
stack.pop(start=6, end=7)

# --- Queue ---
queue = QueueViz(['X', 'Y', 'Z'], x=1050, y=200, cell_width=60, cell_height=45,
                 font_size=24, fill='#2C3E50', text_fill='#ECF0F1', stroke='#F39C12')
queue.fadein(start=1.5, end=2.5)
queue.enqueue('W', start=5, end=6)
queue.dequeue(start=7, end=8)

# --- LinkedList ---
ll = LinkedListViz([10, 20, 30, 40], x=200, y=500, node_width=70, node_height=45,
                   font_size=22, fill='#2C3E50', text_fill='#ECF0F1', stroke='#9B59B6')
ll.fadein(start=2, end=3)

# Labels
for lbl, x in [("Array", 350), ("Stack", 740), ("Queue", 1200), ("LinkedList", 400)]:
    y = 150 if lbl != "LinkedList" else 460
    t = Text(lbl, x=x, y=y, font_size=20, fill='#888')
    t.fadein(start=0.5, end=1)
    v.add(t)

# Fade everything out
for obj in [arr, stack, queue, ll, title]:
    obj.fadeout(start=10, end=11)

v.add(title, arr, stack, queue, ll)
v.render()
