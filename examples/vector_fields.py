"""1x3 static grid showcasing vector field visualizations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 3
ROW_H = 600
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120

canvas_h = FIRST_ROW + ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/vector_fields')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(): return FIRST_ROW - 10
def obj_y(): return FIRST_ROW + 30

title = Text(text='Vector Fields', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# ── (0) ArrowVectorField ─────────────────────────────────────────────────

lbl = Text(text='ArrowVectorField', x=col_x(0), y=lbl_y(), font_size=18,
           fill='#ccc', stroke_width=0, text_anchor='middle')

vf = ArrowVectorField(
    lambda x, y: (-y + x * 0.3, x + y * 0.3),
    x_range=(col_x(0) - 220, col_x(0) + 220, 90),
    y_range=(obj_y() + 40, obj_y() + 480, 90),
    max_length=55, stroke='#58C4DD', stroke_width=2,
)
objs.extend([lbl, vf])

# ── (1) Axes plot_vector_field ───────────────────────────────────────────

lbl = Text(text='Axes.plot_vector_field', x=col_x(1), y=lbl_y(), font_size=18,
           fill='#ccc', stroke_width=0, text_anchor='middle')

ax = Axes(x_range=(-3, 3), y_range=(-3, 3), plot_width=420, plot_height=420,
          x=col_x(1) - 210, y=obj_y() + 50)
ax.add_coordinates()
ax.plot_vector_field(lambda x, y: (-y, x), x_step=0.7, y_step=0.7,
                     max_length=50, stroke='#83C167', fill='#83C167')
objs.extend([lbl, ax])

# ── (2) StreamLines (dipole) ─────────────────────────────────────────────

lbl = Text(text='StreamLines (dipole)', x=col_x(2), y=lbl_y(), font_size=18,
           fill='#ccc', stroke_width=0, text_anchor='middle')

cx_left = col_x(2) - 100
cx_right = col_x(2) + 100
cy_mid = obj_y() + 280

def dipole_field(x, y):
    dx1, dy1 = x - cx_left, y - cy_mid
    r1_sq = dx1**2 + dy1**2 + 100
    dx2, dy2 = x - cx_right, y - cy_mid
    r2_sq = dx2**2 + dy2**2 + 100
    return (dx1 / r1_sq - dx2 / r2_sq) * 5000, (dy1 / r1_sq - dy2 / r2_sq) * 5000

sl = StreamLines(
    dipole_field,
    x_range=(col_x(2) - 250, col_x(2) + 250, 70),
    y_range=(obj_y() + 40, obj_y() + 520, 60),
    n_steps=60, step_size=8,
    stroke='#58C4DD', stroke_width=1.5,
)
source = Dot(cx=cx_left, cy=cy_mid, r=8, fill='#FF6666', stroke_width=0)
sink = Dot(cx=cx_right, cy=cy_mid, r=8, fill='#6666FF', stroke_width=0)
src_label = Text(text='+', x=cx_left, y=cy_mid - 22, font_size=24,
                 fill='#FF6666', stroke_width=0, text_anchor='middle')
snk_label = Text(text='\u2013', x=cx_right, y=cy_mid - 22, font_size=24,
                 fill='#6666FF', stroke_width=0, text_anchor='middle')
objs.extend([lbl, sl, source, sink, src_label, snk_label])

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/vector_fields.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
