"""5x5 grid showcasing Axes plot types (static SVG output)."""
from vectormation.objects import *
import random, math
random.seed(42)

COLS = 5
ROW_H = 270
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 5

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 30

title = Text(text='Axes Plot Types', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# Helper to make a label and axes pair
def make_cell(r, c, label_text):
    lbl = Text(text=label_text, x=col_x(c), y=lbl_y(r), font_size=18,
               fill='#cccccc', stroke_width=0, text_anchor='middle')
    objs.append(lbl)

# ── Row 0 ────────────────────────────────────────────────────────────────

# plot_bar
make_cell(0, 0, 'plot_bar')
ax = Axes(x_range=(0, 7), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(0) - 140, y=obj_y(0))
xs = [1, 2, 3, 4, 5, 6]
ys = [random.uniform(2, 9) for _ in xs]
ax.plot_bar(xs, ys, bar_width=0.6, fill='#58C4DD', fill_opacity=0.7)
objs.append(ax)

# plot_scatter
make_cell(0, 1, 'plot_scatter')
ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(1) - 140, y=obj_y(0))
sx = [random.uniform(0.5, 9.5) for _ in range(30)]
sy = [random.uniform(0.5, 9.5) for _ in range(30)]
ax.plot_scatter(sx, sy, r=3, fill='#FC6255')
objs.append(ax)

# plot_histogram
make_cell(0, 2, 'plot_histogram')
ax = Axes(x_range=(0, 10), y_range=(0, 12), plot_width=280, plot_height=180,
          x=col_x(2) - 140, y=obj_y(0))
hist_data = [random.gauss(5, 1.5) for _ in range(50)]
ax.plot_histogram(hist_data, bins=8, fill='#83C167', fill_opacity=0.6)
objs.append(ax)

# plot_stem
make_cell(0, 3, 'plot_stem')
ax = Axes(x_range=(0, 8), y_range=(-1, 1), plot_width=280, plot_height=180,
          x=col_x(3) - 140, y=obj_y(0))
stem_x = [i for i in range(1, 8)]
stem_y = [math.sin(i * 0.8) for i in stem_x]
ax.plot_stem(stem_x, stem_y, stroke='#F0AC5F', dot_fill='#F0AC5F')
objs.append(ax)

# plot_grouped_bar
make_cell(0, 4, 'plot_grouped_bar')
ax = Axes(x_range=(0, 5), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(4) - 140, y=obj_y(0))
grouped_data = [[random.uniform(3, 8) for _ in range(4)],
                [random.uniform(2, 7) for _ in range(4)],
                [random.uniform(1, 6) for _ in range(4)]]
ax.plot_grouped_bar(grouped_data, bar_width=0.2,
                    colors=['#58C4DD', '#FC6255', '#83C167'])
objs.append(ax)

# ── Row 1 ────────────────────────────────────────────────────────────────

# plot_lollipop
make_cell(1, 0, 'plot_lollipop')
ax = Axes(x_range=(0, 8), y_range=(0, 6), plot_width=280, plot_height=180,
          x=col_x(0) - 140, y=obj_y(1))
lollipop_y = [1, 2, 3, 4, 5]
lollipop_v = [random.uniform(1, 7) for _ in lollipop_y]
ax.plot_lollipop(lollipop_y, lollipop_v, r=4, fill='#9A72AC')
objs.append(ax)

# plot_bubble
make_cell(1, 1, 'plot_bubble')
ax = Axes(x_range=(0, 10), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(1) - 140, y=obj_y(1))
bx = [random.uniform(1, 9) for _ in range(12)]
by = [random.uniform(1, 9) for _ in range(12)]
bsizes = [random.uniform(5, 40) for _ in range(12)]
ax.plot_bubble(bx, by, bsizes, max_radius=12, fill='#58C4DD', fill_opacity=0.5)
objs.append(ax)

# plot_dot_plot
make_cell(1, 2, 'plot_dot_plot')
ax = Axes(x_range=(0, 8), y_range=(0, 6), plot_width=280, plot_height=180,
          x=col_x(2) - 140, y=obj_y(1))
dot_vals = [random.randint(1, 7) for _ in range(25)]
ax.plot_dot_plot(dot_vals, stack_spacing=0.3, r=3, fill='#5CD0B3')
objs.append(ax)

# plot_candlestick
make_cell(1, 3, 'plot_candlestick')
ax = Axes(x_range=(0, 7), y_range=(0, 20), plot_width=280, plot_height=180,
          x=col_x(3) - 140, y=obj_y(1))
candle_data = []
price = 10
for i in range(6):
    o = price
    c = o + random.uniform(-3, 3)
    h = max(o, c) + random.uniform(0, 2)
    l = min(o, c) - random.uniform(0, 2)
    candle_data.append((i + 1, o, h, max(l, 0.5), c))
    price = c
ax.plot_candlestick(candle_data, bar_width=0.5)
objs.append(ax)

# plot_dumbbell
make_cell(1, 4, 'plot_dumbbell')
ax = Axes(x_range=(0, 10), y_range=(0, 6), plot_width=280, plot_height=180,
          x=col_x(4) - 140, y=obj_y(1))
db_y = [1, 2, 3, 4, 5]
db_start = [random.uniform(1, 4) for _ in db_y]
db_end = [s + random.uniform(1, 4) for s in db_start]
ax.plot_dumbbell(db_y, db_start, db_end)
objs.append(ax)

# ── Row 2 ────────────────────────────────────────────────────────────────

# plot_population_pyramid
make_cell(2, 0, 'plot_population_pyramid')
ax = Axes(x_range=(-10, 10), y_range=(0, 6), plot_width=280, plot_height=180,
          x=col_x(0) - 140, y=obj_y(2))
cats = [1, 2, 3, 4, 5]
left_vals = [random.uniform(3, 9) for _ in cats]
right_vals = [random.uniform(3, 9) for _ in cats]
ax.plot_population_pyramid(cats, left_vals, right_vals)
objs.append(ax)

# plot_stacked_area
make_cell(2, 1, 'plot_stacked_area')
ax = Axes(x_range=(0, 8), y_range=(0, 20), plot_width=280, plot_height=180,
          x=col_x(1) - 140, y=obj_y(2))
stacked = [[random.uniform(1, 4) for _ in range(8)],
           [random.uniform(1, 4) for _ in range(8)],
           [random.uniform(1, 4) for _ in range(8)]]
ax.plot_stacked_area(stacked, colors=['#58C4DD', '#83C167', '#FC6255'])
objs.append(ax)

# plot_filled_step
make_cell(2, 2, 'plot_filled_step')
ax = Axes(x_range=(0, 8), y_range=(0, 8), plot_width=280, plot_height=180,
          x=col_x(2) - 140, y=obj_y(2))
fsx = list(range(1, 8))
fsy = [random.uniform(1, 7) for _ in fsx]
ax.plot_filled_step(fsx, fsy, fill='#F0AC5F', fill_opacity=0.4)
objs.append(ax)

# plot_area
make_cell(2, 3, 'plot_area')
ax = Axes(x_range=(0, 6), y_range=(-1, 1), plot_width=280, plot_height=180,
          x=col_x(3) - 140, y=obj_y(2))
ax.plot_area(lambda x: math.sin(x * 1.2), fill='#9A72AC', fill_opacity=0.3,
             stroke='#9A72AC')
objs.append(ax)

# plot_density
make_cell(2, 4, 'plot_density')
ax = Axes(x_range=(0, 10), y_range=(0, 0.5), plot_width=280, plot_height=180,
          x=col_x(4) - 140, y=obj_y(2))
density_data = [random.gauss(5, 1.2) for _ in range(40)]
ax.plot_density(density_data, fill='#5CD0B3', fill_opacity=0.3, stroke='#5CD0B3')
objs.append(ax)

# ── Row 3 ────────────────────────────────────────────────────────────────

# plot_ribbon
make_cell(3, 0, 'plot_ribbon')
ax = Axes(x_range=(0, 8), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(0) - 140, y=obj_y(3))
rib_x = list(range(1, 8))
rib_mid = [random.uniform(3, 7) for _ in rib_x]
rib_lo = [m - random.uniform(0.5, 1.5) for m in rib_mid]
rib_hi = [m + random.uniform(0.5, 1.5) for m in rib_mid]
ax.plot_ribbon(rib_x, rib_lo, rib_hi, fill='#58C4DD', fill_opacity=0.3)
objs.append(ax)

# plot_swarm
make_cell(3, 1, 'plot_swarm')
ax = Axes(x_range=(0, 4), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(1) - 140, y=obj_y(3))
swarm_x = [1, 2, 3]
swarm_groups = [[random.gauss(5, 1.5) for _ in range(15)] for _ in swarm_x]
ax.plot_swarm(swarm_x, swarm_groups, r=2, fill='#FC6255')
objs.append(ax)

# plot_error_bar
make_cell(3, 2, 'plot_error_bar')
ax = Axes(x_range=(0, 8), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(2) - 140, y=obj_y(3))
eb_x = list(range(1, 7))
eb_y = [random.uniform(3, 8) for _ in eb_x]
eb_err = [random.uniform(0.5, 1.5) for _ in eb_x]
ax.plot_error_bar(eb_x, eb_y, eb_err, r=3, fill='#83C167', stroke='#83C167')
objs.append(ax)

# plot_contour
make_cell(3, 3, 'plot_contour')
ax = Axes(x_range=(-3, 3), y_range=(-3, 3), plot_width=280, plot_height=180,
          x=col_x(3) - 140, y=obj_y(3))
ax.plot_contour(lambda x, y: math.sin(x) * math.cos(y), levels=6)
objs.append(ax)

# plot_quiver
make_cell(3, 4, 'plot_quiver')
ax = Axes(x_range=(-3, 3), y_range=(-3, 3), plot_width=280, plot_height=180,
          x=col_x(4) - 140, y=obj_y(3))
ax.plot_quiver(lambda x, y: (-y, x), x_step=0.8, y_step=0.8,
               scale=0.2, stroke='#F0AC5F')
objs.append(ax)

# ── Row 4 ────────────────────────────────────────────────────────────────

# plot_step
make_cell(4, 0, 'plot_step')
ax = Axes(x_range=(0, 8), y_range=(0, 10), plot_width=280, plot_height=180,
          x=col_x(0) - 140, y=obj_y(4))
ax.plot_step([0, 1, 2, 3, 4, 5, 6, 7], [2, 2, 5, 5, 3, 7, 7, 4],
             stroke='#83C167', stroke_width=2)
objs.append(ax)

# plot_implicit
make_cell(4, 1, 'plot_implicit')
ax = Axes(x_range=(-3, 3), y_range=(-3, 3), plot_width=280, plot_height=180,
          x=col_x(1) - 140, y=obj_y(4))
ax.plot_implicit(lambda x, y: x**2 + y**2 - 4, num_points=80,
                 stroke='#FC6255', stroke_width=2)
ax.plot_implicit(lambda x, y: (x**2 + y**2)**2 - 8 * (x**2 - y**2),
                 num_points=120, stroke='#58C4DD', stroke_width=2)
objs.append(ax)

# plot_polar
make_cell(4, 2, 'plot_polar')
ax = Axes(x_range=(-3, 3), y_range=(-3, 3), plot_width=280, plot_height=180,
          x=col_x(2) - 140, y=obj_y(4))
ax.plot_polar(lambda t: 1 + math.cos(t), stroke='#F0AC5F', stroke_width=2)
objs.append(ax)

# plot_heatmap
make_cell(4, 3, 'plot_heatmap')
ax = Axes(x_range=(0, 6), y_range=(0, 6), plot_width=280, plot_height=180,
          x=col_x(3) - 140, y=obj_y(4))
hm = [[math.sin(r * 0.5 + c * 0.4) for c in range(6)] for r in range(6)]
ax.plot_heatmap(hm)
objs.append(ax)

# plot (function graph)
make_cell(4, 4, 'plot (function)')
ax = Axes(x_range=(-3, 3), y_range=(-1.5, 1.5), plot_width=280, plot_height=180,
          x=col_x(4) - 140, y=obj_y(4))
ax.plot(lambda x: math.sin(x), stroke='#9A72AC', stroke_width=2)
ax.plot(lambda x: math.cos(x), stroke='#5CD0B3', stroke_width=2)
objs.append(ax)

# ── Render ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

canvas.show()
