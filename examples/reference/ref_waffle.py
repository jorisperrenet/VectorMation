"""WaffleChart showing category proportions."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = WaffleChart(
    categories=[
        ('Python', 45, '#3776AB'),
        ('JavaScript', 30, '#F7DF1E'),
        ('Rust', 15, '#DEA584'),
        ('Other', 10, '#888888'),
    ],
    x=560, y=290, grid_size=10, cell_size=40, gap=5,
    font_size=18,
)

v.add(chart)

v.show(end=0)
