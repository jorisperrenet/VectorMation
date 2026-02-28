"""Showcase curve effects: passing_flash, get_subcurve, animated_tangent_line."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/curve_effects')

title = Text("Curve Effects", x=960, y=50, font_size=40, fill='#fff')
title.fadein(start=0, end=0.5)

# --- Passing Flash on a circle ---
c = Circle(r=120, cx=400, cy=350, stroke='#3498DB', stroke_width=3, fill_opacity=0)
c.fadein(start=0.5, end=1)
flash_c = Circle(r=120, cx=400, cy=350, stroke='#fff', stroke_width=4, fill_opacity=0)
flash_c.passing_flash(start=1, end=3, width=0.1)
flash_label = Text("passing_flash", x=400, y=510, font_size=20, fill='#888')
flash_label.fadein(start=0.5, end=1)

# --- get_subcurve on a polygon ---
poly = Lines((700, 250), (850, 250), (900, 350), (850, 450), (700, 450), (650, 350),
             stroke='#555', stroke_width=2, fill_opacity=0)
poly.fadein(start=2, end=3)
sub = poly.get_subcurve(0.2, 0.6, stroke='#E74C3C', stroke_width=4, fill_opacity=0)
sub.create(start=3, end=4.5)
sub_label = Text("get_subcurve(0.2, 0.6)", x=775, y=510, font_size=20, fill='#888')
sub_label.fadein(start=2, end=3)

# --- animated_tangent_line ---
ax = Axes(x_range=(-3, 3), y_range=(-1.5, 1.5),
          x=1060, y=200, plot_width=500, plot_height=350)
ax.fadein(start=4, end=5)
curve = ax.plot(math.sin, stroke='#2ECC71', stroke_width=2)
tangent = ax.animated_tangent_line(math.sin, -2.5, 2.5, start=5, end=8,
                                   length=150, stroke='#F39C12', stroke_width=2)
tangent.fadein(start=5, end=5.5)
tan_label = Text("animated_tangent_line", x=1310, y=600, font_size=20, fill='#888')
tan_label.fadein(start=4, end=5)

# Fade out
for obj in [title, c, flash_c, flash_label, poly, sub, sub_label, ax, tangent, tan_label]:
    obj.fadeout(start=9, end=9.8)

v.add(title, c, flash_c, flash_label, poly, sub, sub_label, ax, tangent, tan_label)
if not args.no_display:
    v.browser_display(end=args.duration or 10, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
