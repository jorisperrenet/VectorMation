"""Animated pendulum with a bob tracing its path."""
from vectormation.objects import *

canvas = VectorMathAnim(save_dir='svgs/pendulum')
canvas.set_background()

p = Pendulum(pivot_x=960, pivot_y=200, length=350, angle=40,
             bob_radius=22, period=2.5, damping=0.05,
             start=0, end=10)
p.fadein(start=0, end=0.5)

trace = Trace(p.bob.c, start=0, end=10, stroke='#58C4DD',
              stroke_width=2, stroke_opacity=0.4)

title = Text('Damped Pendulum', x=960, y=80, font_size=36,
             text_anchor='middle', fill='#fff')
title.fadein(start=0, end=1)

canvas.add_objects(trace, p, title)
args = parse_args()
if not args.no_display:
    canvas.browser_display(start=0, end=10, fps=args.fps, port=args.port,
                           hot_reload=True)
