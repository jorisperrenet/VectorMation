"""Boolean operations: union, difference, intersection."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Union
c1a = Circle(r=70, cx=320, cy=540)
c1b = Circle(r=70, cx=420, cy=540)
u = Union(c1a, c1b, fill='#83C167', fill_opacity=0.8)
l1 = Text('Union', x=370, y=680, font_size=24, fill='#aaa', text_anchor='middle')

# Difference
c2a = Circle(r=70, cx=750, cy=540)
c2b = Circle(r=70, cx=850, cy=540)
d = Difference(c2a, c2b, fill='#FF8C00', fill_opacity=0.8)
l2 = Text('Difference', x=800, y=680, font_size=24, fill='#aaa', text_anchor='middle')

# Intersection
c3a = Circle(r=70, cx=1180, cy=540)
c3b = Circle(r=70, cx=1280, cy=540)
inter = Intersection(c3a, c3b, fill='#FFFF00', fill_opacity=0.9)
l3 = Text('Intersection', x=1230, y=680, font_size=24, fill='#aaa', text_anchor='middle')

# Exclusion
c4a = Circle(r=70, cx=1560, cy=540)
c4b = Circle(r=70, cx=1660, cy=540)
ex = Exclusion(c4a, c4b, fill='#A855F7', fill_opacity=0.8)
l4 = Text('Exclusion', x=1610, y=680, font_size=24, fill='#aaa', text_anchor='middle')

v.add(u, d, inter, ex, l1, l2, l3, l4)

v.show(end=2)
