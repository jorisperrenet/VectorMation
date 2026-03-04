"""FunnelChart showing conversion stages."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = FunnelChart(
    stages=[
        ('Visitors', 10000),
        ('Signups', 5000),
        ('Active', 2500),
        ('Paid', 1200),
        ('Enterprise', 400),
    ],
    x=460, y=140, width=1000, height=800,
    font_size=20,
)

v.add(chart)

v.show(end=0)
