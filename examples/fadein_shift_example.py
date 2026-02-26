import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/fadein_shift')
canvas.set_background()

title = Text(text='FadeIn with Shift Directions', x=960, y=80,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Fade in from different directions
t1 = Text(text='From UP', x=480, y=350, font_size=36, fill='#fff',
          stroke_width=0, text_anchor='middle')
t1.fadein(1, 2, shift_dir=UP, shift_amount=80)

t2 = Text(text='From DOWN', x=960, y=350, font_size=36, fill='#fff',
          stroke_width=0, text_anchor='middle')
t2.fadein(1.5, 2.5, shift_dir=DOWN, shift_amount=80)

t3 = Text(text='From LEFT', x=1440, y=350, font_size=36, fill='#fff',
          stroke_width=0, text_anchor='middle')
t3.fadein(2, 3, shift_dir=LEFT, shift_amount=80)

# Fade out with shift
c1 = Circle(r=60, cx=480, cy=600, fill='#83C167', fill_opacity=0.7)
c1.fadein(0, 1)
c1.fadeout(3, 4, shift_dir=DOWN, shift_amount=100)

c2 = Circle(r=60, cx=960, cy=600, fill='#FC6255', fill_opacity=0.7)
c2.fadein(0, 1)
c2.fadeout(3.5, 4.5, shift_dir=RIGHT, shift_amount=100)

c3 = Circle(r=60, cx=1440, cy=600, fill='#FFFF00', fill_opacity=0.7)
c3.fadein(0, 1)
c3.fadeout(4, 5, shift_dir=UP, shift_amount=100)

lbl1 = Text(text='fadeout + DOWN', x=480, y=720, font_size=20, fill='#aaa',
            stroke_width=0, text_anchor='middle')
lbl2 = Text(text='fadeout + RIGHT', x=960, y=720, font_size=20, fill='#aaa',
            stroke_width=0, text_anchor='middle')
lbl3 = Text(text='fadeout + UP', x=1440, y=720, font_size=20, fill='#aaa',
            stroke_width=0, text_anchor='middle')
lbl1.fadein(0, 1)
lbl2.fadein(0, 1)
lbl3.fadein(0, 1)

canvas.add_objects(title, t1, t2, t3, c1, c2, c3, lbl1, lbl2, lbl3)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
