"""IconGrid infographic display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

grid = IconGrid(
    data=[(30, '#58C4DD'), (20, '#E74C3C'), (15, '#2ECC71'), (35, '#F39C12')],
    x=710, y=400, cols=10, size=18, gap=5,
)

v.add(grid)

v.show(end=0)
