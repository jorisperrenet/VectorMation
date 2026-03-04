"""VCollection.write: staggered write animation across children."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

shapes = VCollection(
    Circle(r=60, stroke='#E74C3C', fill='#E74C3C', fill_opacity=0.6),
    Rectangle(110, 110, stroke='#3498DB', fill='#3498DB', fill_opacity=0.6),
    RegularPolygon(6, radius=60, stroke='#2ECC71', fill='#2ECC71', fill_opacity=0.6),
)
shapes.arrange(direction='right', buff=60)
shapes.center_to_pos()
shapes.write(start=0.2, end=2.5)

v.add(shapes)

v.show(end=3)
