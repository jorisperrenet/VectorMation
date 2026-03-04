"""GaugeChart speedometer display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = GaugeChart(
    value=72,
    min_val=0,
    max_val=100,
    label='Performance',
)

v.add(chart)

v.show(end=0)
