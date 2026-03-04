"""CalendarHeatmap contribution-style grid."""
import random
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

random.seed(42)
data = {(r, c): random.randint(0, 10) for r in range(7) for c in range(52)}

chart = CalendarHeatmap(
    data=data,
    rows=7, cols=52,
    x=120, y=300, cell_size=28, gap=4,
)

v.add(chart)

v.show(end=0)
