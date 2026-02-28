import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ripple')
canvas.set_background()

title = Text(text='Ripple Effect', x=960, y=80,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Click ripple on a circle
dot = Dot(cx=400, cy=450, fill='#FFFF00')
dot.fadein(0, 0.5)
ripple1 = dot.ripple(start=1, count=3, end=2.5, max_radius=150, color='#FFFF00')

# Ripple on a text
txt = Text(text='Click!', x=960, y=450, font_size=60, fill='#83C167',
           stroke_width=0, text_anchor='middle')
txt.fadein(0, 0.5)
ripple2 = txt.ripple(start=2, count=4, end=4, max_radius=200, color='#83C167')

# Ripple on a rectangle
rect = Rectangle(150, 100, x=1400, y=400, fill='#58C4DD', fill_opacity=0.7)
rect.fadein(0, 0.5)
ripple3 = rect.ripple(start=3, count=5, end=5, max_radius=180, color='#58C4DD')

canvas.add_objects(dot, ripple1, txt, ripple2, rect, ripple3, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
