"""5x5 grid showcasing Axes annotation methods (static SVG output)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

COLS = 5
ROW_H = 260
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 5

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/axes_annotations')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 30

title = Text(text='Axes Annotations', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

def make_cell(r, c, label_text):
    lbl = Text(text=label_text, x=col_x(c), y=lbl_y(r), font_size=14,
               fill='#cccccc', stroke_width=0, text_anchor='middle')
    objs.append(lbl)

def make_axes(r, c, x_range=(-3, 3), y_range=(-1.5, 1.5)):
    ax = Axes(x_range=x_range, y_range=y_range, plot_width=260, plot_height=160,
              x=col_x(c) - 130, y=obj_y(r))
    return ax

sin_func = lambda x: math.sin(x)
cos_func = lambda x: math.cos(x)

# ── Row 0 ────────────────────────────────────────────────────────────────

make_cell(0, 0, 'add_legend')
ax = make_axes(0, 0)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.plot(cos_func, stroke='#FC6255', stroke_width=2)
ax.add_legend(entries=[('sin(x)', '#58C4DD'), ('cos(x)', '#FC6255')],
              position='upper right', font_size=10)
objs.append(ax)

make_cell(0, 1, 'add_cursor')
ax = make_axes(0, 1)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_cursor(sin_func, x_start=-2, x_end=2, start=0, end=0,
              r=4, fill='#FC6255')
objs.append(ax)

make_cell(0, 2, 'add_title')
ax = make_axes(0, 2)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_title('My Title', font_size=14, buff=8)
objs.append(ax)

make_cell(0, 3, 'add_color_bar')
ax = make_axes(0, 3, x_range=(0, 4), y_range=(0, 4))
data = [[math.sin(r * 0.8 + c * 0.6) for c in range(4)] for r in range(4)]
ax.plot_heatmap(data)
ax.add_color_bar(vmin=-1, vmax=1, label='val', width=10, font_size=8)
objs.append(ax)

make_cell(0, 4, 'add_crosshair')
ax = make_axes(0, 4)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_crosshair(sin_func, x_start=1, x_end=1, start=0, end=0,
                 stroke='#FC6255')
objs.append(ax)

# ── Row 1 ────────────────────────────────────────────────────────────────

make_cell(1, 0, 'add_zero_line')
ax = make_axes(1, 0)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_zero_line(axis='x', stroke='#FC6255', stroke_width=1.5)
objs.append(ax)

make_cell(1, 1, 'add_dot_label')
ax = make_axes(1, 1)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_dot_label(1.57, 1.0, label='peak', dot_color='#FC6255',
                 dot_radius=4, font_size=10)
objs.append(ax)

make_cell(1, 2, 'add_arrow_annotation')
ax = make_axes(1, 2)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_arrow_annotation(0, 0, 'zero', direction='up', length=40,
                        font_size=10)
objs.append(ax)

make_cell(1, 3, 'add_text_annotation')
ax = make_axes(1, 3)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_text_annotation(1.57, 1.0, 'max', font_size=10, dx=25, dy=-25)
objs.append(ax)

make_cell(1, 4, 'add_annotation_box')
ax = make_axes(1, 4)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_annotation_box(0, 0, 'origin', box_width=60, box_height=22,
                      offset=(40, -40), font_size=9)
objs.append(ax)

# ── Row 2 ────────────────────────────────────────────────────────────────

make_cell(2, 0, 'add_area_label')
ax = make_axes(2, 0, y_range=(-0.5, 1.5))
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.get_area(sin_func, x_range=(0, 3.14), fill='#58C4DD', fill_opacity=0.25)
ax.add_area_label(sin_func, x_range=(0, 3.14), font_size=10)
objs.append(ax)

make_cell(2, 1, 'add_data_labels')
ax = make_axes(2, 1, x_range=(0, 5), y_range=(0, 6))
x_data, y_data = [1, 2, 3, 4], [2.1, 4.5, 3.2, 5.0]
ax.plot_scatter(x_data, y_data, r=3, fill='#58C4DD')
ax.add_data_labels(x_data, y_data, fmt='{:.1f}', font_size=8, offset_y=-10)
objs.append(ax)

make_cell(2, 2, 'add_data_table')
ax = make_axes(2, 2, x_range=(0, 4), y_range=(0, 6))
ax.plot(lambda x: x * 1.2 + 0.5, stroke='#58C4DD', stroke_width=2)
ax.add_data_table(headers=['x', 'y'], rows=[['1', '1.7'], ['2', '2.9'], ['3', '4.1']],
                  font_size=8, cell_width=40, cell_height=14)
objs.append(ax)

make_cell(2, 3, 'add_min_max_labels')
ax = make_axes(2, 3)
wave = lambda x: math.sin(x * 1.5) * 0.8
ax.plot(wave, stroke='#58C4DD', stroke_width=2)
ax.add_min_max_labels(wave, font_size=8, dot_radius=3)
objs.append(ax)

make_cell(2, 4, 'add_moving_label')
ax = make_axes(2, 4)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_moving_label(sin_func, text='here', x_start=1, x_end=1,
                    start=0, end=0, font_size=10, offset_y=-12)
objs.append(ax)

# ── Row 3 ────────────────────────────────────────────────────────────────

make_cell(3, 0, 'add_moving_tangent')
ax = make_axes(3, 0)
ax.plot(sin_func, stroke='#58C4DD', stroke_width=2)
ax.add_moving_tangent(sin_func, x_start=1, x_end=1, start=0, end=0,
                      length=2, stroke='#FFFF00', stroke_width=1.5)
objs.append(ax)

make_cell(3, 1, 'add_horizontal_label')
ax = make_axes(3, 1, x_range=(0, 6), y_range=(0, 10))
ax.plot(lambda x: x * 1.5, stroke='#58C4DD', stroke_width=2)
ax.add_horizontal_label(5, 'target', side='right', font_size=9, fill='#FC6255')
objs.append(ax)

make_cell(3, 2, 'add_vertical_label')
ax = make_axes(3, 2, x_range=(0, 6), y_range=(0, 10))
ax.plot(lambda x: x * 1.5, stroke='#58C4DD', stroke_width=2)
ax.add_vertical_label(3, 'x=3', side='top', font_size=9, fill='#83C167')
objs.append(ax)

make_cell(3, 3, 'add_asymptote (v)')
ax = make_axes(3, 3, x_range=(-4, 6), y_range=(-5, 10))
f_rat = lambda x: 1 / (x - 2) + 3 if abs(x - 2) > 0.05 else float('nan')
ax.plot(f_rat, x_range=(-4, 1.8), stroke='#58C4DD', stroke_width=2)
ax.plot(f_rat, x_range=(2.2, 6), stroke='#58C4DD', stroke_width=2)
ax.add_asymptote(2, direction='vertical', stroke='#FF6B6B')
objs.append(ax)

make_cell(3, 4, 'add_asymptote (h)')
ax = make_axes(3, 4, x_range=(-4, 6), y_range=(-5, 10))
ax.plot(f_rat, x_range=(-4, 1.8), stroke='#58C4DD', stroke_width=2)
ax.plot(f_rat, x_range=(2.2, 6), stroke='#58C4DD', stroke_width=2)
ax.add_asymptote(3, direction='horizontal', stroke='#83C167')
objs.append(ax)

# ── Row 4 ────────────────────────────────────────────────────────────────

make_cell(4, 0, 'coords_label')
ax = make_axes(4, 0, x_range=(-1, 5), y_range=(-1, 10))
f_quad = lambda x: 0.5 * x ** 2
ax.plot(f_quad, stroke='#58C4DD', stroke_width=2)
ax.coords_label(3, f_quad(3), fill='#FFFF00')
objs.append(ax)

make_cell(4, 1, 'add_trace')
ax = make_axes(4, 1, x_range=(-1, 5), y_range=(-1, 10))
ax.plot(f_quad, stroke='#58C4DD', stroke_width=2)
ax.add_trace(f_quad, 0, 4, start=0, end=0, r=4, trail_width=1.5,
             fill='#FF6B6B', stroke='#FF6B6B')
objs.append(ax)

make_cell(4, 2, 'add_secant_fade')
ax = make_axes(4, 2, x_range=(-1, 5), y_range=(-1, 10))
ax.plot(f_quad, stroke='#58C4DD', stroke_width=2)
ax.add_secant_fade(f_quad, x=2, dx_start=1, dx_end=1, start=0, end=0,
                   stroke='#83C167')
objs.append(ax)

make_cell(4, 3, 'add_vector')
ax = make_axes(4, 3, x_range=(-3, 4), y_range=(-2, 4))
ax.add_vector(2, 3, stroke='#FF6B6B', fill='#FF6B6B')
ax.add_vector(-1, 2, stroke='#83C167', fill='#83C167')
objs.append(ax)

make_cell(4, 4, 'add_interval')
ax = make_axes(4, 4, x_range=(-1, 5), y_range=(-1, 5))
ax.plot(lambda x: 0.4 * x ** 2, stroke='#58C4DD', stroke_width=2)
ax.add_interval(1, 3, stroke='#FF6B6B', stroke_width=3)
objs.append(ax)

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/axes_annotations.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
