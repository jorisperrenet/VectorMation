import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/save_restore')
canvas.set_background()

title = Text(text='Save/Restore State & Matrix Transform', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Save/Restore demo
circle = Circle(r=60, cx=300, cy=350, fill='#83C167', stroke_width=2, stroke='#fff')
circle.fadein(0.5, 1)
circle.save_state(time=1)

# Modify the circle
circle.dim(start=2, end=2.5, opacity=0.2)
circle.scale(0.5, start=2, end=2.5)

# Restore to saved state
label_mod = Text(text='Modified', x=300, y=440, font_size=20,
                 fill='#aaa', stroke_width=0, text_anchor='middle')
label_mod.fadein(2.5, 3)

label_restore = Text(text='Restored!', x=300, y=440, font_size=20,
                     fill='#83C167', stroke_width=0, text_anchor='middle')
label_restore.fadein(4.5, 5)

circle.restore(start=4, end=4.5)

# Matrix transform demo: shear
r1 = Rectangle(width=120, height=80, x=650, y=250, fill='#FF6B6B',
               fill_opacity=0.7, stroke_width=2, stroke='#fff')
r1.fadein(0.5, 1)

shear_label = Text(text='Shear Transform', x=710, y=370, font_size=20,
                   fill='#aaa', stroke_width=0, text_anchor='middle')
shear_label.fadein(1.5, 2)
r1.apply_matrix([[1, 0.4], [0, 1]], start=2.5)

# Second matrix: rotation-like
r2 = Rectangle(width=120, height=80, x=1000, y=250, fill='#58C4DD',
               fill_opacity=0.7, stroke_width=2, stroke='#fff')
r2.fadein(0.5, 1)

skew_label = Text(text='Skew + Scale', x=1060, y=370, font_size=20,
                  fill='#aaa', stroke_width=0, text_anchor='middle')
skew_label.fadein(1.5, 2)
r2.apply_matrix([[1.2, 0], [0.3, 0.8]], start=3)

canvas.add_objects(circle, r1, r2, label_mod, label_restore,
                   shear_label, skew_label, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
