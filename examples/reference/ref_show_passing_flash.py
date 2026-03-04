"""Passing flash along stroke."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill_opacity=0, stroke='#58C4DD', stroke_width=4)
c.fadein(start=0, end=0.3)
flash = c.show_passing_flash(start=0.3, end=1.5, flash_width=0.2, color='#FFFF00', stroke_width=6)
v.add(c)
v.add(flash)

v.show(end=2)
