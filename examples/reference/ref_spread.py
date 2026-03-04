"""VCollection.spread() distributing shapes between two points."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

group = VCollection(
    Circle(r=40, fill='#58C4DD', fill_opacity=0.8),
    Rectangle(70, 70, fill='#E74C3C', fill_opacity=0.8),
    RegularPolygon(3, radius=40, fill='#2ECC71', fill_opacity=0.8),
    RegularPolygon(5, radius=40, fill='#F39C12', fill_opacity=0.8),
    Circle(r=40, fill='#9B59B6', fill_opacity=0.8),
)
group.spread(260, 540, 1660, 540)

v.add(group)

v.show(end=0)
