"""MorphObject: star morphing into a circle with rotation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

star = Star(5, outer_radius=140, inner_radius=60, fill='#F1C40F', fill_opacity=0.9, stroke='#F1C40F')
circle = Circle(r=120, fill='#9B59B6', fill_opacity=0.9, stroke='#9B59B6')

morph = MorphObject(star, circle, start=0.3, end=2.3, rotation_degrees=180)

v.add(morph)

v.show(end=3)
