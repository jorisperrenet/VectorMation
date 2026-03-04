"""DropShadowFilter applied to shapes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

rect = Rectangle(300, 200, fill='#58C4DD', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)
rect.center_to_pos(posx=700, posy=540)
rect.drop_shadow(dx=8, dy=8, blur=6)

circ = Circle(r=100, cx=1220, cy=540, fill='#FF6B6B', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)
circ.drop_shadow(dx=8, dy=8, blur=6)

v.add(rect, circ)

v.show(end=0)
