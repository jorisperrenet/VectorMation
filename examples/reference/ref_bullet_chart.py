"""BulletChart comparing actual vs target."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = BulletChart(
    actual=270,
    target=300,
    ranges=[(150, '#2a2a3a'), (250, '#3a3a4a'), (350, '#4a4a5a')],
    label='Revenue',
    x=460, y=490, width=1000, height=100,
    font_size=24,
    max_val=350,
)

v.add(chart)

v.show(end=0)
