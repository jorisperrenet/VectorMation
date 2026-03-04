"""Animated 3x4 grid showcasing PieChart and BarChart methods."""
from vectormation.objects import *

COLS = 4
COL_W = 1920 // COLS
ROW_H = 350
TITLE_Y = 50
FIRST_ROW = 130
ROW_DUR = 3.5
ANIM_DUR = 2.0
STAGGER = 0.4
FADE_IN_BEFORE = 0.6
N_ROWS = 3

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 100
def row_t(r): return 0.5 + r * ROW_DUR

def make_lbl(name, c, r):
    a = row_t(r) + c * STAGGER
    lbl = Text(text=name, x=col_x(c), y=lbl_y(r),
               font_size=18, fill='#999', stroke_width=0, text_anchor='middle')
    lbl.fadein(a - FADE_IN_BEFORE, a)
    return lbl

title = Text(text='Chart Methods', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

pie_vals = [35, 25, 20, 20]
pie_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

# ── Row 0: PieChart methods ──────────────────────────────────────────────

# Col 0: sweep_in
r, c = 0, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.sweep_in', c, r))
pie0 = PieChart(pie_vals, colors=pie_colors, cx=col_x(c), cy=obj_y(r), r=90)
pie0.sweep_in(start=a, end=a + ANIM_DUR)
objs.append(pie0)

# Col 1: add_percentage_labels
r, c = 0, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.add_percentage_labels', c, r))
pie1 = PieChart(pie_vals, colors=pie_colors, cx=col_x(c), cy=obj_y(r), r=90)
pie1.sweep_in(start=a, end=a + 0.8)
pie1.add_percentage_labels(font_size=14, color='#fff', creation=a + 0.8)
objs.append(pie1)

# Col 2: explode
r, c = 0, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.explode', c, r))
pie2 = PieChart(pie_vals, colors=pie_colors, cx=col_x(c), cy=obj_y(r), r=90)
pie2.sweep_in(start=a, end=a + 0.8)
pie2.explode([0, 2], distance=15, start=a + 1.0, end=a + ANIM_DUR)
objs.append(pie2)

# Col 3: highlight_sector
r, c = 0, 3
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.highlight_sector', c, r))
pie3 = PieChart(pie_vals, colors=pie_colors, cx=col_x(c), cy=obj_y(r), r=90)
pie3.sweep_in(start=a, end=a + 0.8)
pie3.highlight_sector(1, start=a + 1.0, end=a + ANIM_DUR, pull_distance=25)
objs.append(pie3)

# ── Row 1: BarChart methods ──────────────────────────────────────────────

bar_vals = [60, 40, 80, 50]
bar_labels = ['A', 'B', 'C', 'D']
bar_colors = ['#9B59B6', '#1ABC9C', '#E67E22', '#3498DB']

def bar_x(c): return col_x(c) - 175
def bar_y(r): return obj_y(r) - 60

# Col 0: grow_from_zero
r, c = 1, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.grow_from_zero', c, r))
bc0 = BarChart(bar_vals, labels=bar_labels, colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc0.grow_from_zero(start=a, end=a + ANIM_DUR, stagger=True, delay=0.15)
objs.append(bc0)

# Col 1: add_bar / remove_bar
r, c = 1, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.add_bar / .remove_bar', c, r))
bc1 = BarChart([50, 70, 40], labels=['X', 'Y', 'Z'], colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc1.grow_from_zero(start=a, end=a + 0.6, stagger=False)
bc1.add_bar(90, label='W', start=a + 0.8, end=a + 1.4)
bc1.remove_bar(1, start=a + 1.6, end=a + ANIM_DUR)
objs.append(bc1)

# Col 2: animate_sort
r, c = 1, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.animate_sort', c, r))
bc2 = BarChart([30, 80, 10, 60], labels=['P', 'Q', 'R', 'S'], colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc2.grow_from_zero(start=a, end=a + 0.8, stagger=True, delay=0.1)
bc2.animate_sort(reverse=True, start=a + 1.0, end=a + ANIM_DUR)
objs.append(bc2)

# Col 3: add_value_labels
r, c = 1, 3
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.add_value_labels', c, r))
bc3 = BarChart(bar_vals, labels=bar_labels, colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc3.grow_from_zero(start=a, end=a + 1.0, stagger=True, delay=0.1)
bc3.add_value_labels(fmt='{:.0f}', offset=8, font_size=16, creation=a + 1.0)
objs.append(bc3)

# ── Row 2: BarChart color & value animation ────────────────────────────

# Col 0: set_bar_color
r, c = 2, 0
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.set_bar_color', c, r))
bc4 = BarChart([70, 45, 90, 60], labels=bar_labels, colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc4.grow_from_zero(start=a, end=a + 0.6, stagger=False)
bc4.set_bar_color(2, '#FF6B6B', start=a + 0.8, end=a + ANIM_DUR)
objs.append(bc4)

# Col 1: animate_values
r, c = 2, 1
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.animate_values', c, r))
bc5 = BarChart([70, 45, 90, 60], labels=bar_labels, colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc5.grow_from_zero(start=a, end=a + 0.6, stagger=False)
bc5.animate_values([50, 80, 40, 95], start=a + 0.8, end=a + ANIM_DUR)
objs.append(bc5)

# Col 2: set_bar_colors
r, c = 2, 2
a = row_t(r) + c * STAGGER
objs.append(make_lbl('.set_bar_colors', c, r))
bc6 = BarChart([70, 45, 90, 60], labels=bar_labels, colors=bar_colors,
               x=bar_x(c), y=bar_y(r), width=350, height=200)
bc6.grow_from_zero(start=a, end=a + 0.6, stagger=False)
bc6.set_bar_colors(['#FF6B6B', '#FFFF00', '#83C167', '#58C4DD'], start=a + 0.8)
objs.append(bc6)

# ── Finalize ─────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0

canvas.show(end=total_dur)
