"""WaterfallChart showing cumulative values."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = WaterfallChart(
    values=[100, 30, -20, 50, -15, -10],
    labels=['Revenue', 'Sales', 'Returns', 'Services', 'Tax', 'Costs', 'Net'],
    x=460, y=240, width=1000, height=500,
)

v.add(chart)

v.show(end=0)
