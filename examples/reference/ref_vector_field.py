"""Arrow vector field (ArrowVectorField)."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

def field(x, y):
    return (y - 540, -(x - 960))

vf = ArrowVectorField(field, x_range=(100, 1820, 150),
                       y_range=(100, 980, 150),
                       max_length=70, stroke='#58C4DD')
v.add(vf)

v.show(end=0)
