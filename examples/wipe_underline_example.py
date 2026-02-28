import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/wipe_underline')
canvas.set_background()

title = Text(text='Wipe & Underline Animations', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Wipe in from right
rect1 = Rectangle(width=300, height=150, x=100, y=200, fill='#FF6B6B', fill_opacity=0.8,
                   stroke_width=0)
rect1.wipe(direction='right', start=0.5, end=1.5)
label1 = Text(text='Wipe Right', x=250, y=290, font_size=24, fill='#fff',
              stroke_width=0, text_anchor='middle')
label1.wipe(direction='right', start=0.7, end=1.5)

# Wipe in from left
rect2 = Rectangle(width=300, height=150, x=500, y=200, fill='#83C167', fill_opacity=0.8,
                   stroke_width=0)
rect2.wipe(direction='left', start=1, end=2)

# Wipe down
rect3 = Rectangle(width=300, height=150, x=900, y=200, fill='#58C4DD', fill_opacity=0.8,
                   stroke_width=0)
rect3.wipe(direction='down', start=1.5, end=2.5)

# Wipe out (reverse)
rect1.wipe(direction='right', start=5, end=6, reverse=True)

# Underline animation
txt = Text(text='Animated Underline', x=300, y=550, font_size=48,
           fill='#FFFF00', stroke_width=0)
txt.fadein(1, 2)
underline = Underline(txt, creation=2.5, stroke='#FFFF00', stroke_width=3)
underline.write(2.5, 3.5)

# Highlight border demo
circle = Circle(r=80, cx=1200, cy=550, fill='#9B59B6', fill_opacity=0.7)
circle.fadein(1, 2)
circle.highlight_border(start=3, end=4, color='#FFFF00', width=6)
circle.highlight_border(start=4.5, end=5.3, color='#FF6B6B', width=8)

canvas.add_objects(rect1, rect2, rect3, label1, txt, underline, circle, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
