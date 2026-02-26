import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/slide')
canvas.set_background()

title = Text(text='Slide In/Out Animations', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.slide_in(direction='up', start=0, end=0.8)

# Slide in from different directions
r1 = Rectangle(width=200, height=120, x=200, y=300, fill='#FF6B6B', fill_opacity=0.8,
               stroke_width=0)
r1.slide_in(direction='left', start=0.5, end=1.5)

r2 = Rectangle(width=200, height=120, x=600, y=300, fill='#83C167', fill_opacity=0.8,
               stroke_width=0)
r2.slide_in(direction='up', start=1, end=2)

r3 = Rectangle(width=200, height=120, x=1000, y=300, fill='#58C4DD', fill_opacity=0.8,
               stroke_width=0)
r3.slide_in(direction='right', start=1.5, end=2.5)

r4 = Rectangle(width=200, height=120, x=1400, y=300, fill='#FFFF00', fill_opacity=0.8,
               stroke_width=0)
r4.slide_in(direction='down', start=2, end=3)

# Slide out
r1.slide_out(direction='left', start=5, end=6)
r2.slide_out(direction='down', start=5.5, end=6.5)
r3.slide_out(direction='right', start=6, end=7)
r4.slide_out(direction='up', start=6.5, end=7.5)

# Grow from point demo
circle = Circle(r=80, cx=960, cy=700, fill='#9B59B6', stroke_width=0)
circle.grow_from_point(960, 540, start=2, end=3)

canvas.add_objects(r1, r2, r3, r4, circle, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
