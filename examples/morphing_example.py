"""1x2 animated grid showcasing MorphObject."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 2
COL_W = 1920 // COLS
ROW_H = 700
TITLE_Y = 50
FIRST_ROW = 120

canvas_h = FIRST_ROW + ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/morphing_example')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W

title = Text(text='MorphObject', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── (0) TeX morphing ─────────────────────────────────────────────────────

lbl = Text(text='TeX morph', x=col_x(0), y=FIRST_ROW - 10, font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(0, 0.5)

text_from = TexObject('Who is the best?', font_size=60,
                      x=col_x(0), y=FIRST_ROW + 250)
text_from.center_to_pos(col_x(0), FIRST_ROW + 300)
text_to = TexObject('You are the best!', font_size=60, fill='blue')
text_to.center_to_pos(col_x(0), FIRST_ROW + 300)

text_from.fadein(start=0.5, end=1.5)
morph1 = MorphObject(text_from, text_to, start=2, end=4)
objs.extend([lbl, text_from, morph1, text_to])

# ── (1) Shape morph with rotation ────────────────────────────────────────

lbl = Text(text='Shape morph + rotation', x=col_x(1), y=FIRST_ROW - 10, font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(0, 0.5)

circle = Circle(r=120, cx=col_x(1), cy=FIRST_ROW + 280,
                fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
square = Rectangle(200, 200, x=col_x(1) - 100, y=FIRST_ROW + 180,
                   fill='#FC6255', fill_opacity=0.8, stroke='#FC6255')

circle.fadein(start=0.5, end=1.5)
morph2 = MorphObject(circle, square, start=2, end=4.5, rotation_degrees=360)
objs.extend([lbl, circle, morph2, square])

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/morphing_example.mp4', fps=30, end=5)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
