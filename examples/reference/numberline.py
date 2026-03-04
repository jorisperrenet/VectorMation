"""Number line with pointer and segment."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

nl = NumberLine(x_range=(-5, 5, 1), length=1200)
nl.center_to_pos()
nl.add_pointer(2, label='x')
nl.add_segment(-1, 3, color='#3498DB')

v.add(nl)

v.show(end=2)
