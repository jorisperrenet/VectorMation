"""Stack Operations (LIFO) — Push and Pop visualization.

Animates push and pop operations on a vertical stack. Each push slides a
colored cell in from the right and settles into position; each pop slides
the top cell out to the right and fades it away. Labels track the current
operation and stack contents.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/stack_operations')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
T = 12.0

# Colors (from DEFAULT_CHART_COLORS)
COLORS = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00', '#FF79C6']
COLOR_TEXT     = '#FFFFFF'
COLOR_LABEL    = '#CCCCCC'
COLOR_FRAME    = '#555577'

# Layout
CELL_WIDTH  = 200
CELL_HEIGHT = 60
CELL_GAP    = 6
STACK_X     = 860                         # left edge of stack cells
STACK_BOTTOM = 700                        # bottom-y of the lowest cell slot
MAX_SLOTS   = 5
OFFSCREEN_X = 1500                        # start x for slide-in

# -- Stack frame (visual container) -------------------------------------------
FRAME_PAD = 14
frame_x = STACK_X - FRAME_PAD
frame_y = STACK_BOTTOM - (MAX_SLOTS * (CELL_HEIGHT + CELL_GAP)) - FRAME_PAD + CELL_GAP
frame_w = CELL_WIDTH + 2 * FRAME_PAD
frame_h = MAX_SLOTS * (CELL_HEIGHT + CELL_GAP) - CELL_GAP + 2 * FRAME_PAD

stack_frame = Rectangle(
    width=frame_w, height=frame_h,
    x=frame_x, y=frame_y,
    fill='#1A1A2E', fill_opacity=0.5,
    stroke=COLOR_FRAME, stroke_width=2,
    rx=8, ry=8,
    creation=0,
)
stack_frame.fadein(0.2, 0.9)

# "Bottom" label under the frame
bottom_label = Text(
    text='bottom', x=STACK_X + CELL_WIDTH / 2, y=STACK_BOTTOM + CELL_HEIGHT / 2 + 30,
    font_size=18, fill='#888888', stroke_width=0, text_anchor='middle',
    creation=0,
)
bottom_label.fadein(0.3, 0.9)

# -- Title and info labels ----------------------------------------------------
title = Text(
    text='Stack Operations (LIFO)', x=960, y=70,
    font_size=48, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.8)

operation_label = Text(
    text='', x=960, y=140,
    font_size=30, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)

state_label = Text(
    text='Stack: []', x=960, y=920,
    font_size=26, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)
state_label.fadein(0.5, 1.0)

# "top →" pointer label (moves with the top of the stack)
top_pointer = Text(
    text='', x=STACK_X - 60, y=0,
    font_size=20, fill='#F5C542', stroke_width=0, text_anchor='end',
    creation=0,
)

# -- Helper: compute cell position for a given stack index (0 = bottom) ------
def cell_y(slot):
    """Top-y of the cell at the given slot (0 = bottom)."""
    return STACK_BOTTOM - slot * (CELL_HEIGHT + CELL_GAP)


# -- Operations timeline ------------------------------------------------------
# Each op: ('push', value) or ('pop',)
operations = [
    ('push', 42),
    ('push', 17),
    ('push', 85),
    ('pop',),
    ('push', 33),
    ('pop',),
]

# Timeline windows for each operation
#   0-1:     Title + frame fade in
#   1-3:     Push(42)
#   3-4.5:   Push(17)
#   4.5-6:   Push(85)
#   6-7.5:   Pop() → 85
#   7.5-9:   Push(33)
#   9-10.5:  Pop() → 33
#   10.5-12: Final state
OP_TIMES = [
    (1.0, 3.0),
    (3.0, 4.5),
    (4.5, 6.0),
    (6.0, 7.5),
    (7.5, 9.0),
    (9.0, 10.5),
]

# -- Build and animate --------------------------------------------------------
# We'll store created cell/label objects and the logical stack contents
all_cells = []       # list of (rect, text) for every pushed element
all_objects = []     # flat list of objects to add to canvas
stack = []           # current logical stack: list of indices into all_cells
stack_values = []    # current logical stack values (for state label)
color_idx = 0

operation_label.fadein(1.0, 1.3)

# Popped-value label (appears briefly on pop)
popped_label = Text(
    text='', x=1300, y=400,
    font_size=34, fill='#FF6B6B', stroke_width=0, text_anchor='middle',
    creation=0,
)

for op_idx, op in enumerate(operations):
    t_start, t_end = OP_TIMES[op_idx]
    dur = t_end - t_start

    if op[0] == 'push':
        value = op[1]
        slot = len(stack)  # slot index (0 = bottom)
        target_y = cell_y(slot)

        color = COLORS[color_idx % len(COLORS)]
        color_idx += 1

        # Create cell off-screen to the right, at the correct height
        cell = Rectangle(
            width=CELL_WIDTH, height=CELL_HEIGHT,
            x=OFFSCREEN_X, y=target_y,
            fill=color, fill_opacity=0.85,
            stroke='#FFFFFF', stroke_width=2,
            rx=4, ry=4,
            creation=t_start,
        )
        cell.fadein(t_start, t_start + 0.15)

        label = Text(
            text=str(value),
            x=OFFSCREEN_X + CELL_WIDTH / 2, y=target_y + CELL_HEIGHT / 2 + 6,
            font_size=24, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
            creation=t_start,
        )
        label.fadein(t_start, t_start + 0.15)

        # Slide in from right to stack position
        slide_dx = STACK_X - OFFSCREEN_X
        slide_start = t_start + 0.1
        slide_end = t_start + dur * 0.7
        cell.shift(dx=slide_dx, dy=0, start=slide_start, end=slide_end)
        label.shift(dx=slide_dx, dy=0, start=slide_start, end=slide_end)

        cell_idx = len(all_cells)
        all_cells.append((cell, label))
        all_objects.extend([cell, label])
        stack.append(cell_idx)
        stack_values.append(value)

        # Update operation label
        operation_label.text.set_onward(t_start, f'push({value})')
        operation_label.set_fill(color=color, start=t_start)

        # Update state label (after slide completes)
        state_label.text.set_onward(slide_end, f'Stack: {stack_values[:]}')

        # Update top pointer
        top_pointer.text.set_onward(slide_end, 'top →')
        top_pointer.y.set_onward(slide_end, target_y + CELL_HEIGHT / 2 + 5)

    elif op[0] == 'pop':
        if not stack:
            continue
        cell_idx = stack.pop()
        popped_value = stack_values.pop()
        cell, label = all_cells[cell_idx]

        slot = len(stack)  # slot the element was at (now the top)

        # Update operation label
        operation_label.text.set_onward(t_start, f'pop() → {popped_value}')
        operation_label.set_fill(color='#FF6B6B', start=t_start)

        # Show popped value label
        popped_label.text.set_onward(t_start, f'Popped: {popped_value}')
        popped_label.set_opacity(1.0, start=t_start, end=t_start + 0.2)
        popped_label.y.set_onward(t_start, cell_y(slot) + CELL_HEIGHT / 2 + 6)

        # Slide cell out to the right
        slide_dx = OFFSCREEN_X - STACK_X
        slide_start = t_start + 0.15
        slide_end = t_start + dur * 0.6
        cell.shift(dx=slide_dx, dy=0, start=slide_start, end=slide_end)
        label.shift(dx=slide_dx, dy=0, start=slide_start, end=slide_end)

        # Fade out cell and label
        cell.fadeout(slide_end, slide_end + 0.3)
        label.fadeout(slide_end, slide_end + 0.3)

        # Fade out popped label
        popped_label.set_opacity(0.0, start=t_end - 0.4, end=t_end - 0.1)

        # Update state label
        state_label.text.set_onward(slide_end, f'Stack: {stack_values[:]}')

        # Update top pointer
        if stack:
            new_top_slot = len(stack) - 1
            top_pointer.y.set_onward(slide_end, cell_y(new_top_slot) + CELL_HEIGHT / 2 + 5)
        else:
            top_pointer.text.set_onward(slide_end, '')

# -- Final state (10.5 - 12) --------------------------------------------------
FINAL_START = 10.5
operation_label.text.set_onward(FINAL_START, 'Final State')
operation_label.set_fill(color='#5EC16A', start=FINAL_START)
state_label.text.set_onward(FINAL_START, f'Stack: {stack_values[:]}')

# Pulse the remaining stack cells
for cell_idx in stack:
    cell, label = all_cells[cell_idx]
    cell.pulsate(start=FINAL_START, end=T, scale_factor=1.04)

# -- Add everything to canvas --------------------------------------------------
canvas.add(title, operation_label, state_label, popped_label, top_pointer)
canvas.add(stack_frame, bottom_label)
for obj in all_objects:
    canvas.add(obj)

canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
