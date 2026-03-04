"""Dot following a Bezier path."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

path_d = 'M 200,540 C 500,200 1400,200 1700,540'
guide = Path(path_d, stroke='#444', stroke_width=6, fill_opacity=0)
guide.fadein(start=0, end=0.5)

dot = Dot(cx=200, cy=540, r=12, fill='#FF6B6B')
dot.fadein(start=0, end=0.3)
dot.along_path(0.5, 3.5, path_d)

trail = dot.trace_path(start=0.5, end=3.5, stroke='#FF6B6B',
                       stroke_width=2, stroke_opacity=0.5)

v.add(guide, trail, dot)

v.show(end=4)
