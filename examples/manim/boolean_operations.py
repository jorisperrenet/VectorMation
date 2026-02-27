"""Manim equivalent: BooleanOperations -- boolean ops on overlapping ellipses."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/boolean_operations')
canvas.set_background(fill='#1a1a2e')

ellipse1 = Ellipse(rx=270, ry=338, cx=825, cy=540,
                   fill=BLUE, fill_opacity=0.5, stroke=BLUE, stroke_width=10)
ellipse2 = Ellipse(rx=270, ry=338, cx=1095, cy=540,
                   fill=RED, fill_opacity=0.5, stroke=RED, stroke_width=10)

title = Text('Boolean Operations', x=960, y=120, font_size=72, fill='#fff',
             stroke_width=0, text_anchor='middle')

canvas.add_objects(ellipse1, ellipse2, title)
ellipse1.fadein(start=0, end=0.5)
ellipse2.fadein(start=0, end=0.5)
title.fadein(start=0, end=0.5)

# Each boolean op: appears at ellipse overlap, then scales down and moves under its label.
# Staggered like Manim: one at a time, label fades in after move.
ops = [
    ('Intersection', Intersection, GREEN, 1600, 250),
    ('Union',        Union,        ORANGE, 1600, 700),
    ('Exclusion',    Exclusion,    YELLOW, 300, 250),
    ('Difference',   Difference,   PINK, 300, 700),
]

t = 1.0
for name, cls, color, tx, ty in ops:
    op = cls(ellipse1, ellipse2, fill=color, fill_opacity=0.5, creation=t, stroke_width=10)
    canvas.add_objects(op)
    op.scale(0.4, start=t + 0.5, end=t + 1.3)
    op.center_to_pos(posx=tx, posy=ty + 100, start=t + 0.5, end=t + 1.3)
    label = Text(name, x=tx, y=ty - 70, font_size=48, fill='#ddd',
                 stroke_width=0, text_anchor='middle')
    canvas.add_objects(label)
    label.fadein(start=t, end=t + 0.5)
    t += 1.5

if args.verbose:
    canvas.export_video('docs/source/_static/videos/boolean_operations.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(start=0, end=t + 0.5, fps=args.fps, port=args.port, hot_reload=True)
