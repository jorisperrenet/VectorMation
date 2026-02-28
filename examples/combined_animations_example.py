"""Showcase combined animation methods: create_then_fadeout, fadein_then_fadeout, etc."""
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/combined_animations')

# Title
title = Text("Combined Animations", x=960, y=100, font_size=48, fill='#fff')
title.fadein(start=0, end=0.5)

# create_then_fadeout: draw the stroke, hold, then fade out
c1 = Circle(r=80, cx=320, cy=350, stroke='#3498DB', stroke_width=4, fill='#3498DB', fill_opacity=0.3)
label1 = Text("create_then_fadeout", x=320, y=480, font_size=20, fill='#888')
c1.create_then_fadeout(start=1, end=4)
label1.fadein_then_fadeout(start=1, end=4)

# write_then_fadeout
t1 = Text("Hello World", x=960, y=350, font_size=40, fill='#E74C3C')
label2 = Text("write_then_fadeout", x=960, y=480, font_size=20, fill='#888')
t1.write_then_fadeout(start=4, end=7)
label2.fadein_then_fadeout(start=4, end=7)

# fadein_then_fadeout
star = Star(5, outer_r=70, inner_r=30, cx=1600, cy=350,
            fill='#F1C40F', fill_opacity=0.9, stroke='#DAA520', stroke_width=3)
label3 = Text("fadein_then_fadeout", x=1600, y=480, font_size=20, fill='#888')
star.fadein_then_fadeout(start=7, end=10)
label3.fadein_then_fadeout(start=7, end=10)

# All together at the end
c2 = Circle(r=60, cx=480, cy=700, fill='#9B59B6', fill_opacity=0.7)
r2 = Rectangle(120, 80, x=960, y=700, fill='#2ECC71', fill_opacity=0.7)
s2 = Star(6, outer_r=50, inner_r=25, cx=1440, cy=700, fill='#E67E22', fill_opacity=0.7)
for obj in [c2, r2, s2]:
    obj.fadein_then_fadeout(start=10, end=12)

v.add(title, c1, t1, star, c2, r2, s2, label1, label2, label3)
v.browser_display(end=args.duration or 12, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
