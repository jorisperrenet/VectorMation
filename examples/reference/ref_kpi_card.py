"""KPICard metric display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

card = KPICard(
    'Revenue', '$1.2M',
    subtitle='+12% MoM',
    trend_data=[10, 12, 11, 14, 13, 16, 15, 19, 18, 22],
    x=640, y=340, width=640, height=400,
    font_size=96,
)

v.add(card)

v.show(end=0)
