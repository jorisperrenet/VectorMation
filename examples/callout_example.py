import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/callout')
canvas.set_background()

title = Text(text='Callouts & Dimension Lines', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Draw some shapes with callouts
circle = Circle(r=80, cx=400, cy=400, fill='#58C4DD', fill_opacity=0.7)
circle.fadein(0, 1)

callout1 = Callout('Radius = 80px', circle, direction='up', distance=120, font_size=20)
callout1.fadein(1, 2)

rect = Rectangle(200, 120, x=800, y=340, fill='#83C167', fill_opacity=0.7)
rect.fadein(0, 1)

callout2 = Callout('200 x 120', rect, direction='right', distance=140, font_size=20)
callout2.fadein(1.5, 2.5)

# Dimension line between two points
dim = DimensionLine((400, 600), (1000, 600), label='600px', offset=40, font_size=18)
dim.fadein(2, 3)

# Tooltip example
star = Star(n=5, outer_radius=50, inner_radius=25, cx=1400, cy=400,
            fill='#FFFF00', fill_opacity=0.8)
star.fadein(0, 1)

tip = Tooltip('Click me!', star, start=2, duration=2, font_size=16)

canvas.add_objects(circle, callout1, rect, callout2, dim, star, tip, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
