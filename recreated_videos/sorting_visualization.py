"""Sorting Visualization — Bubble Sort with colored bar feedback.

Animates ~16 bars being sorted via bubble sort. Each comparison highlights
the two bars in yellow, swaps animate bars sliding past each other (red),
and after each pass the last unsorted bar turns green (sorted).
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import random

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/sorting_visualization')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
N = 16
T = 15.0
random.seed(42)
values = list(range(1, N + 1))
random.shuffle(values)

# Colors
COLOR_DEFAULT  = '#4A90D9'   # blue
COLOR_COMPARE  = '#F5C542'   # yellow
COLOR_SWAP     = '#E84D4D'   # red
COLOR_SORTED   = '#5EC16A'   # green

# Layout
BAR_AREA_LEFT  = 260
BAR_AREA_RIGHT = 1660
BAR_AREA_TOP   = 200
BAR_AREA_BOTTOM = 900
BAR_GAP = 8
total_bar_width = (BAR_AREA_RIGHT - BAR_AREA_LEFT - BAR_GAP * (N - 1)) / N
max_bar_height = BAR_AREA_BOTTOM - BAR_AREA_TOP

# -- Create bars ---------------------------------------------------------------
bars = []
for i in range(N):
    h = (values[i] / N) * max_bar_height
    bx = BAR_AREA_LEFT + i * (total_bar_width + BAR_GAP)
    by = BAR_AREA_BOTTOM - h
    bar = Rectangle(
        width=total_bar_width, height=h,
        x=bx, y=by,
        fill=COLOR_DEFAULT, fill_opacity=0.85,
        stroke=COLOR_DEFAULT, stroke_width=1.5,
        creation=0,
    )
    bar.fadein(0.3, 1.0)
    bars.append(bar)

# -- Title and labels ----------------------------------------------------------
title = Text(
    text='Bubble Sort Visualization', x=960, y=70,
    font_size=48, fill='#FFFFFF', stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.8)

operation_label = Text(
    text='', x=960, y=130,
    font_size=28, fill='#CCCCCC', stroke_width=0, text_anchor='middle',
    creation=0,
)

# -- Pre-compute bubble sort steps --------------------------------------------
# Each step: (type, i, j) where type is 'compare' or 'swap'
steps = []
arr = values[:]
n = len(arr)
for end in range(n - 1, 0, -1):
    for j in range(end):
        steps.append(('compare', j, j + 1))
        if arr[j] > arr[j + 1]:
            steps.append(('swap', j, j + 1))
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
    steps.append(('sorted', end, end))

# Mark the last remaining bar as sorted at the very end
steps.append(('sorted', 0, 0))

total_comparisons = sum(1 for s in steps if s[0] == 'compare')

# -- Lay out steps over the timeline ------------------------------------------
SORT_START = 1.0
SORT_END   = 13.5
sort_duration = SORT_END - SORT_START

# Compute time per step (uniform distribution)
num_steps = len(steps)
step_dur = sort_duration / num_steps

# Track which bar index is at which visual position (for shifts)
# pos_of_bar[bar_index] = current visual slot
pos_of_bar = list(range(N))
# bar_at_pos[slot] = bar_index
bar_at_pos = list(range(N))

slot_width = total_bar_width + BAR_GAP

# Comparison counter (will be updated step by step)
comparison_count = 0

# We build a list of (time, comparison_count) milestones for the counter
counter_milestones = []

for step_idx, (stype, i, j) in enumerate(steps):
    t_start = SORT_START + step_idx * step_dur
    t_end = t_start + step_dur

    if stype == 'compare':
        comparison_count += 1
        counter_milestones.append((t_start, comparison_count))

        # The bars at visual position i and j
        bar_i = bar_at_pos[i]
        bar_j = bar_at_pos[j]

        # Flash yellow for the comparison duration
        # Turn yellow at t_start, revert at t_end
        bars[bar_i].set_fill(color=COLOR_COMPARE, start=t_start)
        bars[bar_i].set_fill(color=COLOR_DEFAULT, start=t_end)
        bars[bar_j].set_fill(color=COLOR_COMPARE, start=t_start)
        bars[bar_j].set_fill(color=COLOR_DEFAULT, start=t_end)

    elif stype == 'swap':
        bar_i = bar_at_pos[i]
        bar_j = bar_at_pos[j]

        # Flash red during the swap
        bars[bar_i].set_fill(color=COLOR_SWAP, start=t_start)
        bars[bar_j].set_fill(color=COLOR_SWAP, start=t_start)

        # Animate sliding: bar_i moves right by one slot, bar_j moves left
        anim_start = t_start
        anim_end = t_end - step_dur * 0.1  # leave a tiny gap

        bars[bar_i].shift(dx=slot_width, dy=0, start=anim_start, end=anim_end)
        bars[bar_j].shift(dx=-slot_width, dy=0, start=anim_start, end=anim_end)

        # Revert to default color after swap
        bars[bar_i].set_fill(color=COLOR_DEFAULT, start=t_end)
        bars[bar_j].set_fill(color=COLOR_DEFAULT, start=t_end)

        # Update tracking
        pos_of_bar[bar_i] = j
        pos_of_bar[bar_j] = i
        bar_at_pos[i] = bar_j
        bar_at_pos[j] = bar_i

    elif stype == 'sorted':
        # Mark this bar green permanently
        bar_idx = bar_at_pos[i]
        bars[bar_idx].set_fill(color=COLOR_SORTED, start=t_start)
        bars[bar_idx].set_stroke(color=COLOR_SORTED, start=t_start)

# -- Operation label updates ---------------------------------------------------
# Show pass number at the start of each pass
step_cursor = 0
arr_temp = values[:]
for end in range(N - 1, 0, -1):
    pass_num = N - end
    t_pass_start = SORT_START + step_cursor * step_dur
    operation_label.text.set_onward(t_pass_start, f'Pass {pass_num} of {N - 1}')
    # Count how many steps this pass uses
    for j in range(end):
        step_cursor += 1  # compare
        if arr_temp[j] > arr_temp[j + 1]:
            step_cursor += 1  # swap
            arr_temp[j], arr_temp[j + 1] = arr_temp[j + 1], arr_temp[j]
    step_cursor += 1  # sorted marker

operation_label.fadein(SORT_START, SORT_START + 0.3)

# -- Comparison counter --------------------------------------------------------
# Use a Text that we update at each comparison milestone
counter_label = Text(
    text='Comparisons: 0', x=960, y=170,
    font_size=24, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)
counter_label.fadein(SORT_START, SORT_START + 0.3)

for t_milestone, count in counter_milestones:
    counter_label.text.set_onward(t_milestone, f'Comparisons: {count}')

# -- Final: all bars green, "Sorted!" label ------------------------------------
# At SORT_END, make sure all bars are green
for bar_idx in range(N):
    bars[bar_idx].set_fill(color=COLOR_SORTED, start=SORT_END)
    bars[bar_idx].set_stroke(color=COLOR_SORTED, start=SORT_END)

sorted_label = Text(
    text='Sorted!', x=960, y=980,
    font_size=56, fill=COLOR_SORTED, stroke_width=0, text_anchor='middle',
    creation=SORT_END,
)
sorted_label.fadein(SORT_END, SORT_END + 0.5)

operation_label.text.set_onward(SORT_END, 'Complete!')
operation_label.set_fill(color=COLOR_SORTED, start=SORT_END)

# -- Value labels on top of each bar -------------------------------------------
value_labels = []
for i in range(N):
    h = (values[i] / N) * max_bar_height
    bx = BAR_AREA_LEFT + i * (total_bar_width + BAR_GAP) + total_bar_width / 2
    by = BAR_AREA_BOTTOM - h - 12
    label = Text(
        text=str(values[i]), x=bx, y=by,
        font_size=16, fill='#FFFFFF', stroke_width=0, text_anchor='middle',
        creation=0,
    )
    label.fadein(0.5, 1.0)
    value_labels.append(label)

# Animate value labels to move with their bars
# Re-run the simulation to apply shifts to labels
pos_of_label = list(range(N))
label_at_pos = list(range(N))

for step_idx, (stype, i, j) in enumerate(steps):
    t_start = SORT_START + step_idx * step_dur
    t_end = t_start + step_dur

    if stype == 'swap':
        label_i = label_at_pos[i]
        label_j = label_at_pos[j]

        anim_start = t_start
        anim_end = t_end - step_dur * 0.1

        value_labels[label_i].shift(dx=slot_width, dy=0, start=anim_start, end=anim_end)
        value_labels[label_j].shift(dx=-slot_width, dy=0, start=anim_start, end=anim_end)

        pos_of_label[label_i] = j
        pos_of_label[label_j] = i
        label_at_pos[i] = label_j
        label_at_pos[j] = label_i

# -- Add everything to canvas --------------------------------------------------
canvas.add(title, operation_label, counter_label, sorted_label)
for bar in bars:
    canvas.add(bar)
for label in value_labels:
    canvas.add(label)

if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
