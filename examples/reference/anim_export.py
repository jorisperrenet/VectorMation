"""Static composed scene for frame export."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

# A composed static scene
circle = Circle(r=100, cx=480, cy=440, fill='#58C4DD', fill_opacity=0.8, stroke_width=3)
rect = Rectangle(200, 140, x=860, y=370, fill='#E74C3C', fill_opacity=0.8, stroke_width=3)
star = Star(n=5, outer_radius=100, inner_radius=50, cx=1440, cy=440,
            fill='#F39C12', fill_opacity=0.8, stroke_width=3)
title = Text('Static Frame Export', x=700, y=700, font_size=56, fill='WHITE')

v.add(circle, rect, star, title)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/anim_export.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=1)
