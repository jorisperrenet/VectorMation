"""SplitTexObject: multi-line LaTeX derivation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

equations = SplitTexObject(
    r'$$\Delta = b^2 - 4ac$$',
    r'$$x = \frac{-b \pm \sqrt{\Delta}}{2a}$$',
    line_spacing=80, font_size=48,
)
for i, line in enumerate(equations):
    line.center_to_pos(posy=440 + i * 120)
    v.add(line)

v.show(end=0)
