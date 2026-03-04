"""SankeyDiagram flow visualization."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = SankeyDiagram(
    flows=[
        ('Budget', 'Engineering', 400),
        ('Budget', 'Marketing', 250),
        ('Budget', 'Sales', 200),
        ('Engineering', 'Product', 300),
        ('Engineering', 'Infra', 100),
        ('Marketing', 'Ads', 150),
        ('Marketing', 'Content', 100),
        ('Sales', 'Direct', 120),
        ('Sales', 'Partners', 80),
    ],
    x=160, y=140, width=1600, height=700,
    font_size=18,
)

v.add(chart)

v.show(end=0)
