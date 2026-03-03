"""Sorting Algorithm Comparison — Bubble Sort vs Merge Sort side by side.

Split-screen visualization comparing two sorting algorithms on the same
shuffled array. Each side shows bars being sorted with color-coded feedback,
a step counter, and a comparison counter. A final summary compares the
algorithm performance.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import random

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/sorting_comparison')
canvas.set_background(fill='#1a1a2e')

# -- Parameters ---------------------------------------------------------------
N = 12
T = 20.0
random.seed(42)
values = list(range(1, N + 1))
random.shuffle(values)

# -- Color palette -------------------------------------------------------------
COLOR_BG_PANEL   = '#16213e'
COLOR_PANEL_EDGE = '#0f3460'
COLOR_DEFAULT    = '#4A90D9'
COLOR_COMPARE    = '#F5C542'
COLOR_SWAP       = '#E84D4D'
COLOR_SORTED     = '#2ecc71'
COLOR_MERGE_SRC  = '#9B59B6'
COLOR_MERGE_DST  = '#E67E22'
COLOR_DIVIDER    = '#0f3460'
COLOR_TEXT       = '#FFFFFF'
COLOR_DIM_TEXT   = '#8899aa'
COLOR_ACCENT     = '#e94560'

# -- Layout constants ----------------------------------------------------------
CANVAS_W = 1920
CANVAS_H = 1080
HALF_W = CANVAS_W // 2
PANEL_MARGIN = 30
PANEL_TOP = 180
PANEL_BOTTOM = 880

# Bar area within each panel
BAR_TOP = 320
BAR_BOTTOM = 830
BAR_GAP = 5
BAR_AREA_W = HALF_W - 2 * PANEL_MARGIN - 80

# Per-panel horizontal offsets
LEFT_BAR_LEFT = PANEL_MARGIN + 40
RIGHT_BAR_LEFT = HALF_W + PANEL_MARGIN + 40

bar_width = (BAR_AREA_W - BAR_GAP * (N - 1)) / N
max_bar_height = BAR_BOTTOM - BAR_TOP

SORT_START = 1.5
SORT_END = 17.5
sort_duration = SORT_END - SORT_START

# ==============================================================================
# Title and divider
# ==============================================================================
title = Text(
    text='Sorting Algorithm Comparison',
    x=CANVAS_W // 2, y=50,
    font_size=44, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.8)

subtitle = Text(
    text='Bubble Sort vs Merge Sort on the same shuffled array',
    x=CANVAS_W // 2, y=100,
    font_size=22, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
subtitle.fadein(0.2, 0.9)

# Vertical divider line
divider = Line(
    x1=HALF_W, y1=PANEL_TOP - 30, x2=HALF_W, y2=PANEL_BOTTOM + 40,
    stroke=COLOR_DIVIDER, stroke_width=2, creation=0,
)
divider.fadein(0.3, 1.0)

# Panel backgrounds
left_panel = Rectangle(
    width=HALF_W - 2 * PANEL_MARGIN, height=PANEL_BOTTOM - PANEL_TOP + 60,
    x=PANEL_MARGIN, y=PANEL_TOP - 30,
    fill=COLOR_BG_PANEL, fill_opacity=0.5,
    stroke=COLOR_PANEL_EDGE, stroke_width=1.5,
    rx=10, creation=0, z=-0.5,
)
left_panel.fadein(0.2, 0.9)

right_panel = Rectangle(
    width=HALF_W - 2 * PANEL_MARGIN, height=PANEL_BOTTOM - PANEL_TOP + 60,
    x=HALF_W + PANEL_MARGIN, y=PANEL_TOP - 30,
    fill=COLOR_BG_PANEL, fill_opacity=0.5,
    stroke=COLOR_PANEL_EDGE, stroke_width=1.5,
    rx=10, creation=0, z=-0.5,
)
right_panel.fadein(0.2, 0.9)

# Algorithm titles
bubble_title = Text(
    text='Bubble Sort',
    x=HALF_W // 2, y=PANEL_TOP,
    font_size=32, fill=COLOR_ACCENT, stroke_width=0, text_anchor='middle',
    creation=0,
)
bubble_title.fadein(0.3, 1.0)

merge_title = Text(
    text='Merge Sort',
    x=HALF_W + HALF_W // 2, y=PANEL_TOP,
    font_size=32, fill=COLOR_ACCENT, stroke_width=0, text_anchor='middle',
    creation=0,
)
merge_title.fadein(0.3, 1.0)

# Complexity labels
bubble_complexity = Text(
    text='O(n\u00b2)',
    x=HALF_W // 2, y=PANEL_TOP + 35,
    font_size=20, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
bubble_complexity.fadein(0.4, 1.0)

merge_complexity = Text(
    text='O(n log n)',
    x=HALF_W + HALF_W // 2, y=PANEL_TOP + 35,
    font_size=20, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
merge_complexity.fadein(0.4, 1.0)

# Step and comparison counters
bubble_step_label = Text(
    text='Steps: 0', x=HALF_W // 2 - 100, y=PANEL_TOP + 68,
    font_size=18, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
bubble_step_label.fadein(SORT_START - 0.2, SORT_START)

bubble_comp_label = Text(
    text='Comparisons: 0', x=HALF_W // 2 + 100, y=PANEL_TOP + 68,
    font_size=18, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
bubble_comp_label.fadein(SORT_START - 0.2, SORT_START)

merge_step_label = Text(
    text='Steps: 0', x=HALF_W + HALF_W // 2 - 100, y=PANEL_TOP + 68,
    font_size=18, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
merge_step_label.fadein(SORT_START - 0.2, SORT_START)

merge_comp_label = Text(
    text='Comparisons: 0', x=HALF_W + HALF_W // 2 + 100, y=PANEL_TOP + 68,
    font_size=18, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
merge_comp_label.fadein(SORT_START - 0.2, SORT_START)

# Status labels
bubble_status = Text(
    text='', x=HALF_W // 2, y=PANEL_TOP + 95,
    font_size=16, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)

merge_status = Text(
    text='', x=HALF_W + HALF_W // 2, y=PANEL_TOP + 95,
    font_size=16, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)

# ==============================================================================
# Helper: create bars for one panel
# ==============================================================================
def create_bars(values, bar_left, bar_top, bar_bottom, bar_w, gap, max_h, n):
    """Create bar rectangles and value labels for one sorting panel."""
    bars = []
    labels = []
    for i in range(n):
        h = (values[i] / n) * max_h
        bx = bar_left + i * (bar_w + gap)
        by = bar_bottom - h
        bar = Rectangle(
            width=bar_w, height=h,
            x=bx, y=by,
            fill=COLOR_DEFAULT, fill_opacity=0.88,
            stroke=COLOR_DEFAULT, stroke_width=1,
            rx=3, creation=0,
        )
        bar.fadein(0.4, 1.2)
        bars.append(bar)

        label = Text(
            text=str(values[i]),
            x=bx + bar_w / 2, y=by - 10,
            font_size=13, fill='#CCCCCC', stroke_width=0, text_anchor='middle',
            creation=0,
        )
        label.fadein(0.5, 1.2)
        labels.append(label)
    return bars, labels


bubble_bars, bubble_labels = create_bars(
    values, LEFT_BAR_LEFT, BAR_TOP, BAR_BOTTOM, bar_width, BAR_GAP, max_bar_height, N
)
merge_bars, merge_labels = create_bars(
    values, RIGHT_BAR_LEFT, BAR_TOP, BAR_BOTTOM, bar_width, BAR_GAP, max_bar_height, N
)

slot_width = bar_width + BAR_GAP

# ==============================================================================
# Pre-compute BUBBLE SORT steps
# ==============================================================================
bubble_steps = []
arr_b = values[:]
for end in range(N - 1, 0, -1):
    for j in range(end):
        bubble_steps.append(('compare', j, j + 1))
        if arr_b[j] > arr_b[j + 1]:
            bubble_steps.append(('swap', j, j + 1))
            arr_b[j], arr_b[j + 1] = arr_b[j + 1], arr_b[j]
    bubble_steps.append(('sorted', end, end))
bubble_steps.append(('sorted', 0, 0))

# ==============================================================================
# Pre-compute MERGE SORT steps
# ==============================================================================
# Steps: ('compare', i, j) -- comparing positions i and j
#         ('place', src_pos, dst_pos, value) -- moving bar from src to dst
#         ('sorted', pos) -- mark as sorted
merge_steps = []
arr_m = values[:]

def merge_sort_steps(arr, left, right):
    """Record merge sort operations."""
    if right - left <= 1:
        return
    mid = (left + right) // 2
    merge_sort_steps(arr, left, mid)
    merge_sort_steps(arr, mid, right)
    # Merge
    merged = []
    i, j = left, mid
    while i < mid and j < right:
        merge_steps.append(('compare', i, j))
        if arr[i] <= arr[j]:
            merged.append(arr[i])
            merge_steps.append(('pick', i, 'left'))
            i += 1
        else:
            merged.append(arr[j])
            merge_steps.append(('pick', j, 'right'))
            j += 1
    while i < mid:
        merged.append(arr[i])
        merge_steps.append(('pick', i, 'left'))
        i += 1
    while j < right:
        merged.append(arr[j])
        merge_steps.append(('pick', j, 'right'))
        j += 1
    # Write back
    for k, val in enumerate(merged):
        arr[left + k] = val
        merge_steps.append(('write_back', left + k, val))
    # Mark subsection as merged
    merge_steps.append(('merged', left, right))

merge_sort_steps(arr_m, 0, N)
# Final sorted marker
merge_steps.append(('done',))

# ==============================================================================
# Animate BUBBLE SORT
# ==============================================================================
num_bubble_steps = len(bubble_steps)
bubble_step_dur = sort_duration / num_bubble_steps

pos_of_bar_b = list(range(N))
bar_at_pos_b = list(range(N))

pos_of_label_b = list(range(N))
label_at_pos_b = list(range(N))

bubble_comp_count = 0
bubble_step_count = 0

bubble_status.fadein(SORT_START, SORT_START + 0.3)

for step_idx, step in enumerate(bubble_steps):
    stype = step[0]
    t_start = SORT_START + step_idx * bubble_step_dur
    t_end = t_start + bubble_step_dur

    if stype == 'compare':
        i, j = step[1], step[2]
        bubble_comp_count += 1
        bubble_step_count += 1

        bubble_comp_label.text.set_onward(t_start, f'Comparisons: {bubble_comp_count}')
        bubble_step_label.text.set_onward(t_start, f'Steps: {bubble_step_count}')

        bar_i = bar_at_pos_b[i]
        bar_j = bar_at_pos_b[j]
        bubble_bars[bar_i].set_fill(color=COLOR_COMPARE, start=t_start)
        bubble_bars[bar_i].set_fill(color=COLOR_DEFAULT, start=t_end)
        bubble_bars[bar_j].set_fill(color=COLOR_COMPARE, start=t_start)
        bubble_bars[bar_j].set_fill(color=COLOR_DEFAULT, start=t_end)

    elif stype == 'swap':
        i, j = step[1], step[2]
        bubble_step_count += 1
        bubble_step_label.text.set_onward(t_start, f'Steps: {bubble_step_count}')

        bar_i = bar_at_pos_b[i]
        bar_j = bar_at_pos_b[j]

        bubble_bars[bar_i].set_fill(color=COLOR_SWAP, start=t_start)
        bubble_bars[bar_j].set_fill(color=COLOR_SWAP, start=t_start)

        anim_end = t_end - bubble_step_dur * 0.1
        bubble_bars[bar_i].shift(dx=slot_width, dy=0, start=t_start, end=anim_end)
        bubble_bars[bar_j].shift(dx=-slot_width, dy=0, start=t_start, end=anim_end)
        bubble_labels[bar_i].shift(dx=slot_width, dy=0, start=t_start, end=anim_end)
        bubble_labels[bar_j].shift(dx=-slot_width, dy=0, start=t_start, end=anim_end)

        bubble_bars[bar_i].set_fill(color=COLOR_DEFAULT, start=t_end)
        bubble_bars[bar_j].set_fill(color=COLOR_DEFAULT, start=t_end)

        pos_of_bar_b[bar_i] = j
        pos_of_bar_b[bar_j] = i
        bar_at_pos_b[i] = bar_j
        bar_at_pos_b[j] = bar_i
        pos_of_label_b[bar_i] = j
        pos_of_label_b[bar_j] = i
        label_at_pos_b[i] = bar_j
        label_at_pos_b[j] = bar_i

    elif stype == 'sorted':
        i = step[1]
        bar_idx = bar_at_pos_b[i]
        bubble_bars[bar_idx].set_fill(color=COLOR_SORTED, start=t_start)
        bubble_bars[bar_idx].set_stroke(color=COLOR_SORTED, start=t_start)

# Update bubble status with pass info
step_cursor_b = 0
arr_temp_b = values[:]
for end in range(N - 1, 0, -1):
    pass_num = N - end
    t_pass = SORT_START + step_cursor_b * bubble_step_dur
    bubble_status.text.set_onward(t_pass, f'Pass {pass_num} of {N - 1}')
    for j in range(end):
        step_cursor_b += 1
        if arr_temp_b[j] > arr_temp_b[j + 1]:
            step_cursor_b += 1
            arr_temp_b[j], arr_temp_b[j + 1] = arr_temp_b[j + 1], arr_temp_b[j]
    step_cursor_b += 1

# ==============================================================================
# Animate MERGE SORT
# ==============================================================================
# Merge sort is trickier because bars change positions non-locally.
# We track the position of each original bar and animate moves.
# For simplicity, we animate comparisons as color flashes and
# write-backs as bars moving to their new positions.
num_merge_steps = len(merge_steps)
merge_step_dur = sort_duration / num_merge_steps

# Track which original bar index is at each visual position
merge_bar_positions = list(range(N))  # merge_bar_positions[i] = current visual slot for bar i
merge_pos_to_bar = list(range(N))     # merge_pos_to_bar[slot] = bar index

merge_comp_count = 0
merge_step_count = 0

merge_status.fadein(SORT_START, SORT_START + 0.3)

# We need a different approach for merge sort animation:
# Instead of tracking per-step, we animate at key moments.
# When a 'compare' happens, flash both bars yellow.
# When a 'write_back' happens, we move the bar to its new position.
# After a 'merged' event, we briefly flash the merged range green.

# First, let's figure out which bar (by original index) has which value.
# values[i] = the value at original bar index i
# We need to track: after each merge step, which original bars are at which positions.

# Simpler approach: replay the merge sort, tracking position changes,
# and animate those position changes.

arr_replay = values[:]
bar_at_slot = list(range(N))   # bar_at_slot[visual_slot] = original_bar_index
slot_of_bar = list(range(N))   # slot_of_bar[original_bar_index] = visual_slot

for step_idx, step in enumerate(merge_steps):
    stype = step[0]
    t_start = SORT_START + step_idx * merge_step_dur
    t_end = t_start + merge_step_dur

    if stype == 'compare':
        i, j = step[1], step[2]
        merge_comp_count += 1
        merge_step_count += 1
        merge_comp_label.text.set_onward(t_start, f'Comparisons: {merge_comp_count}')
        merge_step_label.text.set_onward(t_start, f'Steps: {merge_step_count}')

        # Flash the bars at positions i and j
        bar_i = bar_at_slot[i]
        bar_j = bar_at_slot[j]
        merge_bars[bar_i].set_fill(color=COLOR_COMPARE, start=t_start)
        merge_bars[bar_i].set_fill(color=COLOR_DEFAULT, start=t_end)
        merge_bars[bar_j].set_fill(color=COLOR_COMPARE, start=t_start)
        merge_bars[bar_j].set_fill(color=COLOR_DEFAULT, start=t_end)

    elif stype == 'pick':
        pos = step[1]
        side = step[2]
        merge_step_count += 1
        merge_step_label.text.set_onward(t_start, f'Steps: {merge_step_count}')
        # Brief highlight of the picked bar
        bar_idx = bar_at_slot[pos]
        pick_color = COLOR_MERGE_SRC if side == 'left' else COLOR_MERGE_DST
        merge_bars[bar_idx].set_fill(color=pick_color, start=t_start)
        merge_bars[bar_idx].set_fill(color=COLOR_DEFAULT, start=t_end)

    elif stype == 'write_back':
        target_pos, val = step[1], step[2]
        merge_step_count += 1
        merge_step_label.text.set_onward(t_start, f'Steps: {merge_step_count}')

        # Find which original bar has this value and is currently not yet placed
        # in this write_back cycle. We find it by value in arr_replay vs the
        # original values list.
        # Since we replay in order, arr_replay tracks current state.
        # The bar that needs to move to target_pos is the one whose value == val
        # and is in the current merge range.
        # For animation simplicity, find the bar with this value.
        source_bar = None
        for bi in range(N):
            if values[bi] == val and slot_of_bar[bi] != target_pos:
                # Could be this one -- but multiple bars won't have same value
                # since values are 1..N unique
                source_bar = bi
                break
        if source_bar is None:
            # Bar is already at correct position
            for bi in range(N):
                if values[bi] == val:
                    source_bar = bi
                    break

        old_slot = slot_of_bar[source_bar]
        if old_slot != target_pos:
            # Need to swap positions in our tracking
            # The bar currently at target_pos needs to go to old_slot
            displaced_bar = bar_at_slot[target_pos]

            dx_source = (target_pos - old_slot) * slot_width
            dx_displaced = (old_slot - target_pos) * slot_width

            anim_end = t_end - merge_step_dur * 0.1
            merge_bars[source_bar].shift(dx=dx_source, dy=0, start=t_start, end=anim_end)
            merge_labels[source_bar].shift(dx=dx_source, dy=0, start=t_start, end=anim_end)
            merge_bars[displaced_bar].shift(dx=dx_displaced, dy=0, start=t_start, end=anim_end)
            merge_labels[displaced_bar].shift(dx=dx_displaced, dy=0, start=t_start, end=anim_end)

            # Flash the moving bar
            merge_bars[source_bar].set_fill(color=COLOR_MERGE_DST, start=t_start)
            merge_bars[source_bar].set_fill(color=COLOR_DEFAULT, start=t_end)

            # Update tracking
            bar_at_slot[old_slot] = displaced_bar
            bar_at_slot[target_pos] = source_bar
            slot_of_bar[source_bar] = target_pos
            slot_of_bar[displaced_bar] = old_slot

        arr_replay[target_pos] = val

    elif stype == 'merged':
        left, right = step[1], step[2]
        merge_status.text.set_onward(t_start, f'Merged [{left}..{right - 1}]')
        # Brief green flash for merged range
        for pos in range(left, right):
            bi = bar_at_slot[pos]
            merge_bars[bi].set_fill(color='#27ae60', start=t_start)
            merge_bars[bi].set_fill(color=COLOR_DEFAULT, start=t_end)

    elif stype == 'done':
        pass

# Mark all merge bars as sorted at the end
bubble_end_t = SORT_START + num_bubble_steps * bubble_step_dur
merge_end_t = SORT_START + num_merge_steps * merge_step_dur

# Use whichever finishes later (they use same sort_duration)
for i in range(N):
    merge_bars[i].set_fill(color=COLOR_SORTED, start=SORT_END)
    merge_bars[i].set_stroke(color=COLOR_SORTED, start=SORT_END)

for i in range(N):
    bi = bar_at_pos_b[i]
    bubble_bars[bi].set_fill(color=COLOR_SORTED, start=SORT_END)
    bubble_bars[bi].set_stroke(color=COLOR_SORTED, start=SORT_END)

# ==============================================================================
# Final summary
# ==============================================================================
SUMMARY_START = SORT_END + 0.3

bubble_status.text.set_onward(SORT_END, 'Complete!')
bubble_status.set_fill(color=COLOR_SORTED, start=SORT_END)
merge_status.text.set_onward(SORT_END, 'Complete!')
merge_status.set_fill(color=COLOR_SORTED, start=SORT_END)

# Count totals for final display
total_bubble_comps = sum(1 for s in bubble_steps if s[0] == 'compare')
total_bubble_swaps = sum(1 for s in bubble_steps if s[0] == 'swap')
total_merge_comps = sum(1 for s in merge_steps if s[0] == 'compare')
total_merge_writes = sum(1 for s in merge_steps if s[0] == 'write_back')

# Summary line at bottom
summary_bubble = Text(
    text=f'Bubble: {total_bubble_comps} comparisons, {total_bubble_swaps} swaps',
    x=HALF_W // 2, y=PANEL_BOTTOM + 25,
    font_size=20, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=SUMMARY_START,
)
summary_bubble.fadein(SUMMARY_START, SUMMARY_START + 0.5)

summary_merge = Text(
    text=f'Merge: {total_merge_comps} comparisons, {total_merge_writes} writes',
    x=HALF_W + HALF_W // 2, y=PANEL_BOTTOM + 25,
    font_size=20, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=SUMMARY_START,
)
summary_merge.fadein(SUMMARY_START, SUMMARY_START + 0.5)

# Winner announcement
if total_merge_comps < total_bubble_comps:
    winner_text = 'Merge Sort wins with fewer comparisons!'
    winner_color = '#2ecc71'
else:
    winner_text = 'Both algorithms sorted successfully!'
    winner_color = COLOR_TEXT

winner_label = Text(
    text=winner_text,
    x=CANVAS_W // 2, y=PANEL_BOTTOM + 70,
    font_size=36, fill=winner_color, stroke_width=0, text_anchor='middle',
    creation=SUMMARY_START + 0.5,
)
winner_label.fadein(SUMMARY_START + 0.5, SUMMARY_START + 1.0)

# Array size note
array_note = Text(
    text=f'Array size: {N} elements',
    x=CANVAS_W // 2, y=PANEL_BOTTOM + 110,
    font_size=18, fill=COLOR_DIM_TEXT, stroke_width=0, text_anchor='middle',
    creation=SUMMARY_START + 0.5,
)
array_note.fadein(SUMMARY_START + 0.5, SUMMARY_START + 1.0)

# ==============================================================================
# Color legend at top-right area (between title and panels)
# ==============================================================================
LEGEND_Y = 140
LEGEND_X = 60
LEGEND_SPACING = 160
LEGEND_SWATCH = 12

legend_items = [
    (COLOR_COMPARE, 'Compare'),
    (COLOR_SWAP, 'Swap'),
    (COLOR_SORTED, 'Sorted'),
    (COLOR_MERGE_SRC, 'Pick Left'),
    (COLOR_MERGE_DST, 'Pick Right'),
]

legend_objects = []
for i, (color, label_text) in enumerate(legend_items):
    lx = LEGEND_X + i * LEGEND_SPACING
    swatch = Rectangle(
        width=LEGEND_SWATCH, height=LEGEND_SWATCH,
        x=lx, y=LEGEND_Y - LEGEND_SWATCH // 2,
        fill=color, fill_opacity=0.9,
        stroke=color, stroke_width=1,
        creation=0,
    )
    swatch.fadein(0.5, 1.1)
    legend_objects.append(swatch)

    lbl = Text(
        text=label_text,
        x=lx + LEGEND_SWATCH + 6, y=LEGEND_Y + 4,
        font_size=14, fill=color, stroke_width=0, text_anchor='start',
        creation=0,
    )
    lbl.fadein(0.5, 1.1)
    legend_objects.append(lbl)

# ==============================================================================
# Add everything to canvas
# ==============================================================================
canvas.add(title, subtitle, divider, left_panel, right_panel)
canvas.add(bubble_title, merge_title, bubble_complexity, merge_complexity)
canvas.add(bubble_step_label, bubble_comp_label, merge_step_label, merge_comp_label)
canvas.add(bubble_status, merge_status)
canvas.add(summary_bubble, summary_merge, winner_label, array_note)

for bar in bubble_bars:
    canvas.add(bar)
for label in bubble_labels:
    canvas.add(label)
for bar in merge_bars:
    canvas.add(bar)
for label in merge_labels:
    canvas.add(label)
for obj in legend_objects:
    canvas.add(obj)

canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
