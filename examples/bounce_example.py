import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/bounce')
canvas.set_background()

title = Text(text='Bounce & Style Animations', x=960, y=80,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Bouncing ball
ball = Circle(r=30, cx=300, cy=700, fill='#FFFF00', fill_opacity=0.9)
ball.fadein(0, 0.5)
ball.bounce(start=0.5, end=4, height=200, n_bounces=5)

# Bouncing text
txt = Text(text='Boing!', x=700, y=700, font_size=48, fill='#83C167', stroke_width=0)
txt.fadein(0, 0.5)
txt.bounce(start=1, end=4, height=100, n_bounces=3)

# Animate style (color transition)
rect = Rectangle(200, 120, x=1100, y=400, fill='#58C4DD', fill_opacity=0.8, stroke='#fff')
rect.fadein(0, 0.5)
rect.animate_style(1, 3, fill='#FF6B6B', stroke='#FFFF00', stroke_width=6)
rect.animate_style(3.5, 5, fill='#83C167', stroke='#58C4DD', stroke_width=2)

canvas.add_objects(title, ball, txt, rect)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
