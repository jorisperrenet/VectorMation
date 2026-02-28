"""Binary Search Visualization — searching for a target in a sorted array.

Animates binary search on a sorted 16-element array. Each step highlights
the low, mid, and high pointers with distinct colors. Eliminated elements
are dimmed; the found element turns green.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/binary_search')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
N = 16
T = 12.0
sorted_array = [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 42, 48, 53, 61, 72, 88]
TARGET = 42

# Colors
COLOR_DEFAULT  = '#4A90D9'   # blue — default cell
COLOR_LOW      = '#F5A623'   # orange — low pointer
COLOR_HIGH     = '#9B59B6'   # purple — high pointer
COLOR_MID      = '#F5C542'   # yellow — mid pointer
COLOR_FOUND    = '#5EC16A'   # green — found
COLOR_DIMMED   = '#3A3A5C'   # dark grey-blue — eliminated
COLOR_TEXT     = '#FFFFFF'
COLOR_LABEL    = '#CCCCCC'

# Layout
CELL_WIDTH  = 82
CELL_HEIGHT = 60
CELL_GAP    = 6
ARRAY_Y     = 420  # top-y of the cell row
TOTAL_WIDTH = N * CELL_WIDTH + (N - 1) * CELL_GAP
ARRAY_LEFT  = (1920 - TOTAL_WIDTH) / 2  # center horizontally

# Pointer label positions (below array)
PTR_LABEL_Y = ARRAY_Y + CELL_HEIGHT + 50
PTR_ARROW_Y1 = ARRAY_Y + CELL_HEIGHT + 8
PTR_ARROW_Y2 = ARRAY_Y + CELL_HEIGHT + 35

# -- Create array cells and value labels --------------------------------------
cells = []
value_labels = []
index_labels = []

for i in range(N):
    cx = ARRAY_LEFT + i * (CELL_WIDTH + CELL_GAP)
    cy = ARRAY_Y

    cell = Rectangle(
        width=CELL_WIDTH, height=CELL_HEIGHT,
        x=cx, y=cy,
        fill=COLOR_DEFAULT, fill_opacity=0.85,
        stroke='#FFFFFF', stroke_width=2,
        creation=0,
    )
    cell.fadein(0.2, 0.8)
    cells.append(cell)

    # Value inside the cell
    label = Text(
        text=str(sorted_array[i]),
        x=cx + CELL_WIDTH / 2, y=cy + CELL_HEIGHT / 2 + 6,
        font_size=24, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    label.fadein(0.3, 0.9)
    value_labels.append(label)

    # Index below the cell (small)
    idx_label = Text(
        text=str(i),
        x=cx + CELL_WIDTH / 2, y=cy - 14,
        font_size=14, fill='#888888', stroke_width=0, text_anchor='middle',
        creation=0,
    )
    idx_label.fadein(0.3, 0.9)
    index_labels.append(idx_label)

# -- Title and info labels ----------------------------------------------------
title = Text(
    text='Binary Search', x=960, y=80,
    font_size=52, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.7)

target_label = Text(
    text=f'Target: {TARGET}', x=960, y=150,
    font_size=32, fill='#F5C542', stroke_width=0, text_anchor='middle',
    creation=0,
)
target_label.fadein(0.1, 0.8)

step_label = Text(
    text='', x=960, y=220,
    font_size=28, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)

# Comparison detail label (shows what's being compared)
detail_label = Text(
    text='', x=960, y=270,
    font_size=24, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)

# -- Pointer labels (below the array) ----------------------------------------
low_label = Text(
    text='', x=0, y=PTR_LABEL_Y,
    font_size=22, fill=COLOR_LOW, stroke_width=0, text_anchor='middle',
    creation=0,
)

mid_label = Text(
    text='', x=0, y=PTR_LABEL_Y,
    font_size=22, fill=COLOR_MID, stroke_width=0, text_anchor='middle',
    creation=0,
)

high_label = Text(
    text='', x=0, y=PTR_LABEL_Y,
    font_size=22, fill=COLOR_HIGH, stroke_width=0, text_anchor='middle',
    creation=0,
)

# Pointer arrows (small lines pointing up to the cells)
low_arrow = Line(
    x1=0, y1=PTR_ARROW_Y2, x2=0, y2=PTR_ARROW_Y1,
    stroke=COLOR_LOW, stroke_width=3, creation=0,
)
mid_arrow = Line(
    x1=0, y1=PTR_ARROW_Y2, x2=0, y2=PTR_ARROW_Y1,
    stroke=COLOR_MID, stroke_width=3, creation=0,
)
high_arrow = Line(
    x1=0, y1=PTR_ARROW_Y2, x2=0, y2=PTR_ARROW_Y1,
    stroke=COLOR_HIGH, stroke_width=3, creation=0,
)

def cell_center_x(idx):
    """X center of cell at index idx."""
    return ARRAY_LEFT + idx * (CELL_WIDTH + CELL_GAP) + CELL_WIDTH / 2

def move_pointer(label_obj, arrow_obj, idx, text, t):
    """Move a pointer label and arrow to point at cell idx at time t."""
    cx = cell_center_x(idx)
    label_obj.text.set_onward(t, text)
    # Position label (Text has x/y as attributes.Real on the object itself)
    label_obj.x.set_onward(t, cx)
    # Position arrow endpoints
    arrow_obj.p1.set_onward(t, (cx, PTR_ARROW_Y2))
    arrow_obj.p2.set_onward(t, (cx, PTR_ARROW_Y1))

# -- Pre-compute binary search steps -----------------------------------------
steps = []
lo, hi = 0, N - 1
while lo <= hi:
    mid = (lo + hi) // 2
    steps.append((lo, hi, mid, sorted_array[mid]))
    if sorted_array[mid] == TARGET:
        break
    elif sorted_array[mid] < TARGET:
        lo = mid + 1
    else:
        hi = mid - 1

# -- Animate search steps ----------------------------------------------------
SEARCH_START = 1.0
SEARCH_END   = 11.0
search_duration = SEARCH_END - SEARCH_START
num_steps = len(steps)
step_dur = search_duration / num_steps

# Track which cells have been eliminated (so we don't re-color them)
eliminated = set()
# Track the previous step's lo/hi/mid to revert their colors
prev_lo = prev_hi = prev_mid = None

step_label.fadein(SEARCH_START, SEARCH_START + 0.3)
detail_label.fadein(SEARCH_START, SEARCH_START + 0.3)

for step_idx, (lo, hi, mid, mid_val) in enumerate(steps):
    t_start = SEARCH_START + step_idx * step_dur
    t_highlight = t_start + 0.15  # small delay for color transitions
    t_result = t_start + step_dur * 0.5  # when we show comparison result
    t_end = t_start + step_dur

    is_last = (step_idx == num_steps - 1)
    found = (mid_val == TARGET)

    # Update step counter
    step_label.text.set_onward(t_start, f'Step {step_idx + 1} of {num_steps}')

    # Revert previous step's highlighted cells to default (if not eliminated)
    if prev_lo is not None:
        for idx in (prev_lo, prev_mid, prev_hi):
            if idx not in eliminated:
                cells[idx].set_fill(color=COLOR_DEFAULT, start=t_start)
                cells[idx].set_stroke(color='#FFFFFF', start=t_start)

    # Show comparison info
    detail_label.text.set_onward(t_start, f'low={lo}  mid={mid}  high={hi}  |  arr[{mid}] = {mid_val}')

    # Highlight low, mid, high cells
    # Low pointer
    if lo != mid:
        cells[lo].set_fill(color=COLOR_LOW, start=t_highlight)
        cells[lo].set_stroke(color=COLOR_LOW, start=t_highlight)
    # High pointer
    if hi != mid and hi != lo:
        cells[hi].set_fill(color=COLOR_HIGH, start=t_highlight)
        cells[hi].set_stroke(color=COLOR_HIGH, start=t_highlight)
    # Mid pointer (takes priority if overlapping)
    cells[mid].set_fill(color=COLOR_MID, start=t_highlight)
    cells[mid].set_stroke(color=COLOR_MID, start=t_highlight)

    # Move pointer labels and arrows
    move_pointer(low_label, low_arrow, lo, 'low', t_start)
    move_pointer(mid_label, mid_arrow, mid, 'mid', t_start)
    move_pointer(high_label, high_arrow, hi, 'high', t_start)

    # Show comparison result
    if found:
        detail_label.text.set_onward(t_result, f'arr[{mid}] = {mid_val} == {TARGET}  FOUND!')
        # Turn found cell green
        cells[mid].set_fill(color=COLOR_FOUND, start=t_result)
        cells[mid].set_stroke(color=COLOR_FOUND, start=t_result)
    elif mid_val < TARGET:
        detail_label.text.set_onward(t_result, f'arr[{mid}] = {mid_val} < {TARGET}  →  search right half')
        # Dim eliminated cells (lo..mid)
        for i in range(lo, mid + 1):
            if i not in eliminated:
                cells[i].set_fill(color=COLOR_DIMMED, start=t_result)
                cells[i].set_stroke(color=COLOR_DIMMED, start=t_result)
                cells[i].set_opacity(0.4, start=t_result, end=t_result + 0.3)
                value_labels[i].set_opacity(0.3, start=t_result, end=t_result + 0.3)
                eliminated.add(i)
    else:
        detail_label.text.set_onward(t_result, f'arr[{mid}] = {mid_val} > {TARGET}  →  search left half')
        # Dim eliminated cells (mid..hi)
        for i in range(mid, hi + 1):
            if i not in eliminated:
                cells[i].set_fill(color=COLOR_DIMMED, start=t_result)
                cells[i].set_stroke(color=COLOR_DIMMED, start=t_result)
                cells[i].set_opacity(0.4, start=t_result, end=t_result + 0.3)
                value_labels[i].set_opacity(0.3, start=t_result, end=t_result + 0.3)
                eliminated.add(i)

    prev_lo, prev_hi, prev_mid = lo, hi, mid

# -- Found! message at the end ------------------------------------------------
found_idx = None
for lo, hi, mid, mid_val in steps:
    if mid_val == TARGET:
        found_idx = mid
        break

found_label = Text(
    text=f'Found {TARGET} at index {found_idx}!', x=960, y=700,
    font_size=56, fill=COLOR_FOUND, stroke_width=0, text_anchor='middle',
    creation=SEARCH_END,
)
found_label.fadein(SEARCH_END, SEARCH_END + 0.5)

# Final state: keep the found cell bright green, pulse it
if found_idx is not None:
    cells[found_idx].set_fill(color=COLOR_FOUND, start=SEARCH_END)
    cells[found_idx].set_stroke(color=COLOR_FOUND, start=SEARCH_END)
    cells[found_idx].pulsate(start=SEARCH_END, end=T, scale_factor=1.08)

step_label.text.set_onward(SEARCH_END, 'Search Complete!')
step_label.set_fill(color=COLOR_FOUND, start=SEARCH_END)
detail_label.text.set_onward(SEARCH_END, f'O(log n) = {num_steps} steps for {N} elements')

# -- Legend (color key) -------------------------------------------------------
LEGEND_Y = 850
LEGEND_X_START = 480
LEGEND_SPACING = 260
LEGEND_SWATCH = 18

legend_items = [
    (COLOR_LOW, 'Low'),
    (COLOR_MID, 'Mid'),
    (COLOR_HIGH, 'High'),
    (COLOR_FOUND, 'Found'),
]

legend_objects = []
for i, (color, label_text) in enumerate(legend_items):
    lx = LEGEND_X_START + i * LEGEND_SPACING
    swatch = Rectangle(
        width=LEGEND_SWATCH, height=LEGEND_SWATCH,
        x=lx, y=LEGEND_Y - LEGEND_SWATCH / 2,
        fill=color, fill_opacity=0.9,
        stroke=color, stroke_width=1,
        creation=0,
    )
    swatch.fadein(0.5, 1.0)
    legend_objects.append(swatch)

    lbl = Text(
        text=label_text,
        x=lx + LEGEND_SWATCH + 10, y=LEGEND_Y + 5,
        font_size=20, fill=color, stroke_width=0, text_anchor='start',
        creation=0,
    )
    lbl.fadein(0.5, 1.0)
    legend_objects.append(lbl)

# -- Add everything to canvas --------------------------------------------------
canvas.add(title, target_label, step_label, detail_label, found_label)
canvas.add(low_label, mid_label, high_label)
canvas.add(low_arrow, mid_arrow, high_arrow)
for cell in cells:
    canvas.add(cell)
for label in value_labels:
    canvas.add(label)
for label in index_labels:
    canvas.add(label)
for obj in legend_objects:
    canvas.add(obj)

if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
