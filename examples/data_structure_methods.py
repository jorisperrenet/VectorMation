"""Animated 3x4 grid showcasing data structure methods."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 4
COL_W = 1920 // COLS
ROW_H = 350
TITLE_Y = 50
FIRST_ROW = 130
ROW_DUR = 5.0
ANIM_DUR = 2.5
STAGGER = 0.4
FADE_IN_BEFORE = 0.8
N_ROWS = 3

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/data_structure_methods')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 80
def row_t(r): return 0.5 + r * ROW_DUR

def make_lbl(name, c, r):
    a = row_t(r) + c * STAGGER
    lbl = Text(text=name, x=col_x(c), y=lbl_y(r),
               font_size=18, fill='#999', stroke_width=0, text_anchor='middle')
    lbl.fadein(a - FADE_IN_BEFORE, a)
    return lbl

title = Text(text='Data Structure Methods', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ---------------------------------------------------------------------------
# Row 0, Col 0: Stack push / pop
# ---------------------------------------------------------------------------
c, r = 0, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Stack.push / pop', c, r))

stack = Stack(['A', 'B', 'C'], x=col_x(c) - 50, y=obj_y(r) + 100,
              cell_width=100, cell_height=40, font_size=20)
stack.fadein(a - FADE_IN_BEFORE, a)
stack.push('D', start=a, end=a + 0.6)
stack.push('E', start=a + 0.8, end=a + 1.4)
stack.pop(start=a + 1.8, end=a + 2.2)
objs.append(stack)

# ---------------------------------------------------------------------------
# Row 0, Col 1: Queue enqueue / dequeue
# ---------------------------------------------------------------------------
c, r = 1, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Queue.enqueue / dequeue', c, r))

queue = Queue(['X', 'Y', 'Z'], x=col_x(c) - 110, y=obj_y(r) + 30,
              cell_width=65, cell_height=50, font_size=20)
queue.fadein(a - FADE_IN_BEFORE, a)
queue.enqueue('W', start=a, end=a + 0.6)
queue.dequeue(start=a + 1.0, end=a + 1.6)
objs.append(queue)

# ---------------------------------------------------------------------------
# Row 0, Col 2: LinkedList append / remove
# ---------------------------------------------------------------------------
c, r = 2, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('LinkedList.append / remove', c, r))

ll = LinkedList([10, 20, 30], x=col_x(c) - 180, y=obj_y(r) + 20,
                node_width=50, node_height=36, gap=55, font_size=16)
ll.fadein(a - FADE_IN_BEFORE, a)
ll.append_node(40, start=a, end=a + 0.6)
ll.remove_node(1, start=a + 1.0, end=a + 1.6)
objs.append(ll)

# ---------------------------------------------------------------------------
# Row 0, Col 3: LinkedList.highlight_node
# ---------------------------------------------------------------------------
c, r = 3, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('LinkedList.highlight_node', c, r))

ll2 = LinkedList([10, 20, 30, 40], x=col_x(c) - 210, y=obj_y(r) + 20,
                 node_width=50, node_height=36, gap=55, font_size=16)
ll2.fadein(a - FADE_IN_BEFORE, a)
ll2.highlight_node(0, start=a, end=a + 0.8, color='#E9C46A')
ll2.highlight_node(1, start=a + 0.8, end=a + 1.6, color='#E9C46A')
ll2.highlight_node(2, start=a + 1.6, end=a + 2.4, color='#E9C46A')
ll2.highlight_node(3, start=a + 2.4, end=a + 3.2, color='#FC6255')
objs.append(ll2)

# ---------------------------------------------------------------------------
# Row 1, Col 0: Array sort / reverse
# ---------------------------------------------------------------------------
c, r = 0, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Array.sort / reverse', c, r))

arr = Array([5, 2, 8, 1, 3], x=col_x(c) - 140, y=obj_y(r) + 20,
            cell_width=50, cell_height=45, font_size=20, show_indices=True)
arr.fadein(a - FADE_IN_BEFORE, a)
arr.sort(start=a, end=a + 1.5)
arr.reverse(start=a + 1.8, end=a + 2.5)
objs.append(arr)

# ---------------------------------------------------------------------------
# Row 1, Col 1: Array.highlight_cell / swap_cells
# ---------------------------------------------------------------------------
c, r = 1, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Array.highlight / swap', c, r))

arr2 = Array([4, 7, 1, 9, 3], x=col_x(c) - 140, y=obj_y(r) + 20,
             cell_width=50, cell_height=45, font_size=20, show_indices=True)
arr2.fadein(a - FADE_IN_BEFORE, a)
arr2.highlight_cell(1, start=a, end=a + 0.8, color='#E9C46A')
arr2.highlight_cell(3, start=a + 0.6, end=a + 1.4, color='#FC6255')
arr2.swap_cells(1, 3, start=a + 1.4, end=a + 2.4)
objs.append(arr2)

# ---------------------------------------------------------------------------
# Row 1, Col 2: Array.set_value / add_pointer
# ---------------------------------------------------------------------------
c, r = 2, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Array.set_value / pointer', c, r))

arr3 = Array([10, 20, 30, 40], x=col_x(c) - 110, y=obj_y(r) + 20,
             cell_width=50, cell_height=45, font_size=20)
arr3.fadein(a - FADE_IN_BEFORE, a)
ptr = arr3.add_pointer(2, label='i', color='#FC6255', creation=a)
arr3.set_value(2, 99, start=a + 0.8, end=a + 1.3)
arr3.set_value(0, 55, start=a + 1.6, end=a + 2.1)
objs += [arr3, ptr]

# ---------------------------------------------------------------------------
# Row 1, Col 3: BinaryTree.traverse
# ---------------------------------------------------------------------------
c, r = 3, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('BinaryTree.traverse', c, r))

tree_data = ('A',
             ('B', ('D', None, None), ('E', None, None)),
             ('C', None, ('F', None, None)))
bt = BinaryTree(tree_data, x=col_x(c), y=obj_y(r),
                h_spacing=100, v_spacing=65, node_radius=18, font_size=14)
bt.fadein(a - FADE_IN_BEFORE, a)
bt.traverse(start=a, delay=0.35, color='#E9C46A')
objs.append(bt)

# ---------------------------------------------------------------------------
# Row 2, Col 0: Matrix.swap_rows
# ---------------------------------------------------------------------------
c, r = 0, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Matrix.swap_rows', c, r))

dm = DecimalMatrix([[1.5, 2.7, 0.3], [3.1, 4.9, 1.2], [0.8, 5.6, 3.4]],
                   decimals=1, x=col_x(c) - 80, y=obj_y(r) + 20,
                   font_size=20, h_spacing=55, v_spacing=38)
dm.fadein(a - FADE_IN_BEFORE, a)
dm.swap_rows(0, 2, start=a + 0.2, end=a + 1.2)
objs.append(dm)

# ---------------------------------------------------------------------------
# Row 2, Col 1: Matrix.row_operation
# ---------------------------------------------------------------------------
c, r = 1, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Matrix.row_operation', c, r))

ro = IntegerMatrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                   x=col_x(c) - 80, y=obj_y(r) + 20,
                   font_size=20, h_spacing=55, v_spacing=38)
ro.fadein(a - FADE_IN_BEFORE, a)
ro.row_operation(1, 0, scalar=-4, start=a + 0.2, end=a + 1.5)
objs.append(ro)

# ---------------------------------------------------------------------------
# Row 2, Col 2: Matrix.augmented
# ---------------------------------------------------------------------------
c, r = 2, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Matrix.augmented', c, r))

aug = Matrix.augmented([[1, 0], [0, 1]], [[3], [7]],
                       x=col_x(c) - 80, y=obj_y(r) + 20,
                       font_size=20, h_spacing=55, v_spacing=38)
aug.fadein(a - FADE_IN_BEFORE, a)
aug.set_column_colors('#58C4DD', '#58C4DD', '#FC6255', start=a + 0.5)
objs.append(aug)

# ---------------------------------------------------------------------------
# Row 2, Col 3: Matrix.set_row/column_colors
# ---------------------------------------------------------------------------
c, r = 3, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('Matrix.set_row / column_colors', c, r))

im = IntegerMatrix([[7, 3, 1], [2, 9, 4], [5, 6, 8]],
                   x=col_x(c) - 80, y=obj_y(r) + 20,
                   font_size=20, h_spacing=55, v_spacing=38)
im.fadein(a - FADE_IN_BEFORE, a)
im.set_row_colors('#FF6B6B', '#83C167', '#58C4DD', start=a + 0.3)
im.set_column_colors('#F0AC5F', '#9A72AC', '#5CD0B3', start=a + 1.8)
objs.append(im)

# ---------------------------------------------------------------------------
# Assemble and render
# ---------------------------------------------------------------------------
canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/data_structure_methods.mp4',
                        fps=30, end=total_dur)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=total_dur)
