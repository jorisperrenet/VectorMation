"""DecimalNumber tracking a ValueTracker."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

vt = ValueTracker(0)
vt.animate_value(3.14159, start=0, end=2)

label = DecimalNumber(vt, fmt='{:.4f}', font_size=72)
label.center_to_pos()

v.add(label)

v.show(end=2.5)
