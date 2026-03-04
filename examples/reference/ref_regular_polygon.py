"""RegularPolygon shapes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

colors = ['#E74C3C', '#F39C12', '#2ECC71', '#3498DB', '#9B59B6']
for i, (n, color) in enumerate(zip([3, 5, 6, 7, 8], colors)):
    cx = 300 + i * 330
    p = RegularPolygon(n, radius=100, cx=cx, cy=540, fill=color, fill_opacity=0.5, stroke=color)
    v.add(p)

v.show(end=0)
