from vectormation.objects import *
import math

COLS = 3
ROW_H = 300
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 3

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 30

title = Text(text='Axes Tick Formatters', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

PW, PH = 440, 200

# ---------- Row 0 ----------

# pi_format
r, c = 0, 0
lbl = Text(text='pi_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(-math.pi, math.pi, math.pi / 2), y_range=(-1, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=pi_format)
ax.add_coordinates(font_size=14)
ax.plot(lambda x: math.sin(x), color='#58C4DD')
objs += [lbl, ax]

# pi_tex_format
r, c = 0, 1
lbl = Text(text='pi_tex_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(-2 * math.pi, 2 * math.pi, math.pi), y_range=(-1, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=pi_tex_format)
ax.add_coordinates(font_size=14, tex=True)
ax.plot(lambda x: math.cos(x), color='#FCBA03')
objs += [lbl, ax]

# log_tex_format
r, c = 0, 2
lbl = Text(text='log_tex_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(1, 10000), y_range=(0, 4, 1),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=log_tex_format, x_scale='log',
          x_ticks=[1, 10, 100, 1000, 10000])
ax.add_coordinates(font_size=14, tex=True)
ax.plot(lambda x: math.log10(x) if x > 0 else 0, color='#83C167')
objs += [lbl, ax]

# ---------- Row 1 ----------

# scientific_format
r, c = 1, 0
lbl = Text(text='scientific_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(0, 50000, 10000), y_range=(0, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=scientific_format)
ax.add_coordinates(font_size=12)
ax.plot(lambda x: 1 - math.exp(-x / 15000), color='#FC6255')
objs += [lbl, ax]

# engineering_format
r, c = 1, 1
lbl = Text(text='engineering_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(0, 5000, 1000), y_range=(0, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=engineering_format)
ax.add_coordinates(font_size=14)
ax.plot(lambda x: math.sin(x / 800) ** 2, color='#FF862F')
objs += [lbl, ax]

# percent_format
r, c = 1, 2
lbl = Text(text='percent_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(0, 1, 0.25), y_range=(0, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=percent_format)
ax.add_coordinates(font_size=14)
ax.plot(lambda x: x ** 2, color='#A55FEF')
objs += [lbl, ax]

# ---------- Row 2 ----------

# degree_format
r, c = 2, 0
lbl = Text(text='degree_format', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(0, 360, 90), y_range=(-1, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=degree_format)
ax.add_coordinates(font_size=14)
ax.plot(lambda x: math.sin(math.radians(x)), color='#58C4DD')
objs += [lbl, ax]

# custom formatter (lambda)
r, c = 2, 1
lbl = Text(text='custom formatter', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(0, 24, 6), y_range=(0, 100, 25),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r),
          x_tick_format=lambda v: f'{int(v):02d}:00',
          y_tick_format=lambda v: f'{v:.0f}%')
ax.add_coordinates(font_size=14)
ax.plot(lambda x: 50 + 40 * math.sin((x - 6) * math.pi / 12), color='#F0AC5F')
objs += [lbl, ax]

# default (no formatter)
r, c = 2, 2
lbl = Text(text='default (no formatter)', x=col_x(c), y=lbl_y(r), font_size=24,
           fill='white', stroke_width=0, text_anchor='middle')
ax = Axes(x_range=(-2, 2, 1), y_range=(-1, 1, 0.5),
          plot_width=PW, plot_height=PH, x=col_x(c) - PW // 2, y=obj_y(r))
ax.add_coordinates(font_size=14)
ax.plot(lambda x: x ** 3 / 4, color='#888888')
objs += [lbl, ax]

# ---------- render ----------

canvas.add_objects(*objs)

canvas.show()
