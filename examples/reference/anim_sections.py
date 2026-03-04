"""Sections demo -- objects appear in phases."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

# Phase 1: circle fades in
circle = Circle(r=80, cx=480, cy=540, fill='#58C4DD', fill_opacity=0.8)
circle.fadein(start=0, end=1)

# Section break at t=2
v.add_section(2)

# Phase 2: rectangle fades in
rect = Rectangle(160, 160, x=880, y=460, fill='#E74C3C', fill_opacity=0.8)
rect.fadein(start=2, end=3)

# Section break at t=4
v.add_section(4)

# Phase 3: text fades in
txt = Text('VectorMation', x=1300, y=540, font_size=48, fill='WHITE')
txt.fadein(start=4, end=5)

v.add(circle, rect, txt)
if args.for_docs:
    v.export_video('docs/source/_static/videos/anim_sections.mp4', fps=30, end=6)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=6)
