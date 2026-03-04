"""TexObject with colored parts."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

eq = TexObject(r'$$E = mc^2$$', font_size=80,
               t2c={'E': '#FF6666', 'm': '#66FF66', 'c': '#6666FF'})
eq.center_to_pos()
eq.write(start=0, end=2)

v.add(eq)

v.show(end=3)
