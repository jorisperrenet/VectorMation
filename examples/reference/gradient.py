"""Linear and radial gradients on shapes."""
from vectormation.objects import *
from vectormation.colors import LinearGradient, RadialGradient

v = VectorMathAnim()
v.set_background()

lg = LinearGradient([('0%', '#ff0000'), ('50%', '#ffff00'), ('100%', '#0000ff')])
v.add_def(lg)

rg = RadialGradient([('0%', '#ffffff'), ('100%', '#58C4DD')])
v.add_def(rg)

rect = Rectangle(300, 200, x=330, y=440, fill=lg, fill_opacity=1, stroke_opacity=0)
circ = Circle(r=100, cx=1320, cy=540, fill=rg, fill_opacity=1, stroke_opacity=0)

l1 = Text('LinearGradient', x=480, y=700, font_size=24, fill='#aaa', text_anchor='middle')
l2 = Text('RadialGradient', x=1320, y=700, font_size=24, fill='#aaa', text_anchor='middle')

v.add(rect, circ, l1, l2)

v.show(end=2)
