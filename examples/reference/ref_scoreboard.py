"""Scoreboard metric panel."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = Scoreboard(
    entries=[
        ('Users', '12.4K'),
        ('Revenue', '$84K'),
        ('Growth', '+18%'),
        ('Uptime', '99.9%'),
    ],
    x=360, y=420, col_width=300, row_height=200,
    font_size=56,
)

v.add(chart)

v.show(end=0)
