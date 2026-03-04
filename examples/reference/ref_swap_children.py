"""VCollection.swap_children() animating two shapes swapping positions."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

group = VCollection(
    Circle(r=50, fill='#58C4DD', fill_opacity=0.8),
    Rectangle(90, 90, fill='#E74C3C', fill_opacity=0.8),
    RegularPolygon(3, radius=50, fill='#2ECC71', fill_opacity=0.8),
)
group.arrange(direction='right', buff=80)
group.center_to_pos()

group.swap_children(0, 2, start=0.5, end=2)

v.add(group)

v.show(end=2.5)
