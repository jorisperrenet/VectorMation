"""Static 4x4 grid showing Axes overlay methods."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math, random
random.seed(42)
args = parse_args()

COLS = 4
ROW_H = 280
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 4

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/axes_overlays')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 30

title = Text(text='Axes Overlays', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

def add_label(c, r, text):
    lbl = Text(text=text, x=col_x(c), y=lbl_y(r), font_size=14,
               fill='#ccc', stroke_width=0, text_anchor='middle')
    objs.append(lbl)

def make_axes(c, r, x_range=(-3, 3), y_range=(-2, 2)):
    return Axes(x_range=x_range, y_range=y_range,
                x=col_x(c) - 160, y=obj_y(r),
                plot_width=320, plot_height=180)

# ── Row 0 ────────────────────────────────────────────────────────────────

add_label(0, 0, 'add_reference_band')
ax = make_axes(0, 0)
ax.plot(lambda x: math.sin(x), stroke='#58C4DD')
ax.add_reference_band(-0.5, 0.5, axis='y', fill='#58C4DD', fill_opacity=0.15)
objs.append(ax)

add_label(1, 0, 'add_confidence_band')
ax = make_axes(1, 0)
ax.plot(lambda x: 0.3 * x, stroke='#58C4DD')
ax.add_confidence_band(lambda x: 0.3 * x - 0.5, lambda x: 0.3 * x + 0.5,
                       fill='#83C167', fill_opacity=0.15)
objs.append(ax)

add_label(2, 0, 'add_shaded_inequality')
ax = make_axes(2, 0)
ax.plot(lambda x: 0.5 * math.sin(x), stroke='#58C4DD')
ax.add_shaded_inequality(lambda x: 0.5 * math.sin(x), direction='below',
                         fill='#FC6255', fill_opacity=0.15)
objs.append(ax)

add_label(3, 0, 'add_vertical_span')
ax = make_axes(3, 0)
ax.plot(lambda x: math.cos(x), stroke='#58C4DD')
ax.add_vertical_span(-1, 1, fill='#F0AC5F', fill_opacity=0.2)
objs.append(ax)

# ── Row 1 ────────────────────────────────────────────────────────────────

add_label(0, 1, 'add_horizontal_span')
ax = make_axes(0, 1)
ax.plot(lambda x: 0.5 * x, stroke='#58C4DD')
ax.add_horizontal_span(-0.5, 0.5, fill='#9A72AC', fill_opacity=0.2)
objs.append(ax)

add_label(1, 1, 'add_threshold_line')
ax = make_axes(1, 1)
ax.plot(lambda x: 0.3 * x ** 2 - 1, stroke='#58C4DD')
ax.add_threshold_line(0.5, label='threshold', font_size=12, stroke='#FC6255')
objs.append(ax)

add_label(2, 1, 'add_axis_break')
ax = make_axes(2, 1, x_range=(0, 5), y_range=(0, 100))
ax.plot_bar([1, 2, 3, 4], [10, 15, 12, 90], bar_width=0.6,
            fill='#58C4DD', fill_opacity=0.7)
ax.add_axis_break(40, axis='y', size=10)
objs.append(ax)

add_label(3, 1, 'add_boxplot')
ax = make_axes(3, 1, x_range=(0, 4), y_range=(-3, 3))
groups = [[random.gauss(0, 1) for _ in range(20)] for _ in range(3)]
ax.add_boxplot(groups, x_positions=[1, 2, 3], width=0.5, stroke='#58C4DD')
objs.append(ax)

# ── Row 2 ────────────────────────────────────────────────────────────────

add_label(0, 2, 'add_violin_plot')
ax = make_axes(0, 2, x_range=(0, 4), y_range=(-3, 3))
v_groups = [[random.gauss(0, 1) for _ in range(20)] for _ in range(3)]
ax.add_violin_plot(v_groups, x_positions=[1, 2, 3], width=0.6,
                   fill='#83C167', fill_opacity=0.5)
objs.append(ax)

add_label(1, 2, 'add_error_bars')
ax = make_axes(1, 2, x_range=(0, 6), y_range=(-1, 4))
xd, yd = [1, 2, 3, 4, 5], [1.2, 2.0, 1.8, 3.1, 2.5]
yerr = [0.3, 0.5, 0.4, 0.6, 0.35]
ax.plot_scatter(xd, yd, r=4, fill='#58C4DD')
ax.add_error_bars(xd, yd, yerr, stroke='#aaa', cap_width=4)
objs.append(ax)

add_label(2, 2, 'add_regression_line')
ax = make_axes(2, 2, x_range=(0, 6), y_range=(-1, 4))
xr, yr = [1, 2, 3, 4, 5], [0.8, 1.5, 2.3, 2.9, 3.8]
ax.plot_scatter(xr, yr, r=4, fill='#58C4DD')
ax.add_regression_line(xr, yr, stroke='#83C167')
objs.append(ax)

add_label(3, 2, 'get_dashed_line')
ax = make_axes(3, 2)
ax.plot(lambda x: 0.5 * x, stroke='#58C4DD')
ax.get_dashed_line(-2, -1, 2, 1, stroke='#FC6255')
objs.append(ax)

# ── Row 3 ────────────────────────────────────────────────────────────────

add_label(0, 3, 'get_area')
ax = make_axes(0, 3)
ax.plot(lambda x: math.sin(x) + 0.5, stroke='#58C4DD')
ax.get_area(lambda x: math.sin(x) + 0.5, x_range=(-2, 2),
            fill='#58C4DD', fill_opacity=0.2)
objs.append(ax)

add_label(1, 3, 'get_area_between')
ax = make_axes(1, 3)
ax.plot(lambda x: 0.5 * math.sin(x) + 0.5, stroke='#58C4DD')
ax.plot(lambda x: -0.5 * math.sin(x) - 0.5, stroke='#FC6255')
ax.get_area_between(lambda x: 0.5 * math.sin(x) + 0.5,
                    lambda x: -0.5 * math.sin(x) - 0.5,
                    x_range=(-2, 2), fill='#83C167', fill_opacity=0.2)
objs.append(ax)

add_label(2, 3, 'get_slope_field')
ax = make_axes(2, 3)
ax.get_slope_field(lambda x, y: -x / max(abs(y), 0.1),
                   x_step=0.5, y_step=0.5, length=0.3, stroke='#58C4DD')
objs.append(ax)

add_label(3, 3, 'highlight_y_range')
ax = make_axes(3, 3, x_range=(0, 8), y_range=(0, 10))
ax.plot_step([0, 1, 2, 3, 4, 5, 6, 7], [2, 2, 5, 5, 3, 7, 7, 4],
             stroke='#83C167', stroke_width=2)
ax.highlight_y_range(4, 6, fill='#FF6B6B', fill_opacity=0.1)
objs.append(ax)

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/axes_overlays.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
