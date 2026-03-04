"""DonutChart and RadarChart side by side."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

donut = DonutChart([40, 25, 20, 15],
                   labels=['Python', 'JS', 'Rust', 'Go'],
                   cx=480, cy=540, r=220, inner_radius=110)

radar = RadarChart(values=[0.9, 0.6, 0.8, 0.4, 0.7],
                   labels=['Speed', 'Power', 'Defense', 'Magic', 'HP'],
                   cx=1440, cy=540, radius=220)

v.add(donut, radar)

v.show(end=1)
