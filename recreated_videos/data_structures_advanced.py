"""Data Structures Advanced Demo — BinaryTree, ArrayViz, StackViz, QueueViz, LinkedListViz."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ds_advanced')
canvas.set_background()
T = 12.0

# -- Colors -------------------------------------------------------------------
TEAL      = '#58C4DD'
GREEN     = '#50FA7B'
YELLOW    = '#E9C46A'
RED       = '#FC6255'
ORANGE    = '#F5A623'
PURPLE    = '#BD93F9'
DARK      = '#264653'

# =============================================================================
# Phase 1 (0-4s): Binary Tree — build, traverse, highlight specific nodes
# =============================================================================
p1_title = Text(text='Binary Tree', x=960, y=60, font_size=44,
                fill='#fff', stroke_width=0, text_anchor='middle')
p1_title.fadein(0.0, 0.3)
p1_title.fadeout(3.4, 3.8)
canvas.add(p1_title)

p1_sub = Text(text='depth-first traversal with node highlighting', x=960, y=110,
              font_size=22, fill='#888', stroke_width=0, text_anchor='middle')
p1_sub.fadein(0.1, 0.4)
p1_sub.fadeout(3.4, 3.8)
canvas.add(p1_sub)

# Build a balanced binary tree:  (8, (4, (2), (6)), (12, (10), (14)))
tree_data = (8,
             (4, (2,), (6,)),
             (12, (10,), (14,)))

tree = BinaryTree(tree_data, x=960, y=170, h_spacing=260, v_spacing=120,
                  node_radius=30, font_size=22, fill='#1e1e2e',
                  border_color=TEAL, edge_color='#555', creation=0)
tree.fadein(0.3, 0.8)

# Animate a full depth-first traversal (nodes flash in order)
tree.traverse(start=1.0, delay=0.3, color=YELLOW)

# After traversal, highlight the root and a leaf specifically
tree.highlight_node(6, start=3.0, end=3.5, color=RED)     # root (last in DFS)
tree.highlight_node(0, start=3.0, end=3.5, color=GREEN)   # leftmost leaf

tree.fadeout(3.5, 3.9)
canvas.add(tree)

# =============================================================================
# Phase 2 (4-8s): Linear structures side by side
#   Left:  ArrayViz with pointer and swap
#   Center: StackViz with push/pop
#   Right: QueueViz with enqueue/dequeue/highlight
# =============================================================================
p2_title = Text(text='Linear Structures', x=960, y=55, font_size=44,
                fill='#fff', stroke_width=0, text_anchor='middle', creation=4.0)
p2_title.fadein(4.0, 4.3)
p2_title.fadeout(7.5, 7.9)
canvas.add(p2_title)

# -- ArrayViz (left side) --
arr_label = Text(text='ArrayViz — pointer + swap', x=380, y=120, font_size=20,
                 fill='#888', stroke_width=0, text_anchor='middle', creation=4.0)
arr_label.fadein(4.1, 4.4)
arr_label.fadeout(7.5, 7.9)
canvas.add(arr_label)

arr = ArrayViz([7, 3, 9, 1, 5], cell_size=65, x=140, y=180,
               default_fill=DARK, font_size=28, creation=4.0)
arr.fadein(4.2, 4.5)

# Add a pointer labeled "i" at index 1
arr.pointer(1, label='i', start=4.5, color=RED)
# Highlight index 3
arr.highlight(3, start=4.8, end=5.3, color=YELLOW)
# Swap indices 1 and 3 with arc animation
arr.swap(1, 3, start=5.3, end=6.0)
# Update value at index 0
arr.set_value(0, 42, start=6.0, end=6.5)
# Add another pointer
arr.pointer(4, label='j', start=6.5, color=GREEN)

arr.fadeout(7.5, 7.9)
canvas.add(arr)

# -- StackViz (center) --
stk_label = Text(text='StackViz — push + pop', x=780, y=120, font_size=20,
                 fill='#888', stroke_width=0, text_anchor='middle', creation=4.0)
stk_label.fadein(4.1, 4.4)
stk_label.fadeout(7.5, 7.9)
canvas.add(stk_label)

stk = StackViz(['A', 'B'], cell_width=100, cell_height=45,
               x=730, y=410, fill=DARK, font_size=24, creation=4.0)
stk.fadein(4.2, 4.5)

stk.push('C', start=4.6, end=5.0)
stk.push('D', start=5.0, end=5.4)
stk.push('E', start=5.4, end=5.8)
stk.pop(start=6.0, end=6.4)
stk.pop(start=6.4, end=6.8)
stk.push('F', start=6.8, end=7.2)

stk.fadeout(7.5, 7.9)
canvas.add(stk)

# -- QueueViz (right side / bottom) --
q_label = Text(text='QueueViz — enqueue + dequeue + highlight', x=1360, y=120,
               font_size=20, fill='#888', stroke_width=0, text_anchor='middle',
               creation=4.0)
q_label.fadein(4.1, 4.4)
q_label.fadeout(7.5, 7.9)
canvas.add(q_label)

q = QueueViz([1, 2, 3], cell_width=70, cell_height=55,
             x=1170, y=180, fill=DARK, font_size=24, creation=4.0)
q.fadein(4.2, 4.5)

q.enqueue(4, start=4.6, end=5.0)
q.enqueue(5, start=5.0, end=5.4)
q.highlight(0, start=5.4, end=5.9, color=YELLOW)
q.dequeue(start=5.9, end=6.3)
q.highlight(1, start=6.3, end=6.8, color=PURPLE)
q.dequeue(start=6.8, end=7.2)

q.fadeout(7.5, 7.9)
canvas.add(q)

# =============================================================================
# Phase 3 (8-12s): Linked list — traverse, append, remove
# =============================================================================
p3_title = Text(text='Linked List Operations', x=960, y=60, font_size=44,
                fill='#fff', stroke_width=0, text_anchor='middle', creation=8.0)
p3_title.fadein(8.0, 8.3)
p3_title.fadeout(11.5, 11.9)
canvas.add(p3_title)

p3_sub = Text(text='traverse, append, and remove nodes', x=960, y=110,
              font_size=22, fill='#888', stroke_width=0, text_anchor='middle',
              creation=8.0)
p3_sub.fadein(8.1, 8.4)
p3_sub.fadeout(11.5, 11.9)
canvas.add(p3_sub)

# -- LinkedListViz with traversal (top) --
llv_label = Text(text='LinkedListViz — traverse', x=960, y=185, font_size=20,
                 fill='#888', stroke_width=0, text_anchor='middle', creation=8.0)
llv_label.fadein(8.1, 8.4)
llv_label.fadeout(11.5, 11.9)
canvas.add(llv_label)

llv = LinkedListViz([10, 20, 30, 40, 50], node_radius=30, spacing=130,
                    x=None, y=280, node_fill=DARK, font_size=24, creation=8.0)
llv.fadein(8.2, 8.6)

# Traverse all nodes sequentially
llv.traverse(start=8.7, delay=0.4, color=YELLOW)

llv.fadeout(11.5, 11.9)
canvas.add(llv)

# -- LinkedList with append and remove (bottom) --
ll_label = Text(text='LinkedList — append + remove', x=960, y=450, font_size=20,
                fill='#888', stroke_width=0, text_anchor='middle', creation=8.0)
ll_label.fadein(8.1, 8.4)
ll_label.fadeout(11.5, 11.9)
canvas.add(ll_label)

ll = LinkedList(values=['A', 'B', 'C'], x=340, y=510,
                node_width=80, node_height=50, gap=50, font_size=22,
                fill='#1e1e2e', border_color=TEAL, arrow_color='#fff',
                creation=8.0)
ll.fadein(8.2, 8.6)

# Highlight individual nodes
ll.highlight_node(0, start=8.7, end=9.2, color=ORANGE)
ll.highlight_node(1, start=9.0, end=9.5, color=ORANGE)

# Append new nodes
ll.append_node('D', start=9.5, end=10.0)
ll.append_node('E', start=10.0, end=10.5)

# Remove node at index 1 (second node)
ll.remove_node(1, start=10.5, end=11.0)

# Highlight remaining first node
ll.highlight_node(0, start=11.0, end=11.4, color=GREEN)

ll.fadeout(11.5, 11.9)
canvas.add(ll)

# -- Render -------------------------------------------------------------------
if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
