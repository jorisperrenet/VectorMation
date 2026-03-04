"""Labelled complex numbers on ComplexPlane."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
cp.add_coordinates()
cp.add_complex_label(1 + 2j, 'z\u2081')
cp.add_complex_label(-1 + 1j, 'z\u2082')
cp.add_complex_label(2 - 1j, 'z\u2083')

v.add(cp)

v.show(end=0)
