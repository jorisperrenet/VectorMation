"""TexCountAnimation: LaTeX-styled animated counter."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

counter = TexCountAnimation(0, 100, start=0, end=3, font_size=72)
counter.center_to_pos()

v.add(counter)

v.show(end=3.5)
