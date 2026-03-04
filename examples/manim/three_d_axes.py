"""Manim equivalent: FixedInFrameMObjectTest -- labeled 3D axes."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

axes = ThreeDAxes()

title = Text('3D Axes', font_size=48, fill='#fff', stroke_width=0)
title.to_corner('UL')

canvas.add_objects(axes, title)

canvas.show()
