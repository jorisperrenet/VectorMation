"""RadarChart with sample data."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = RadarChart(
    values=[85, 70, 90, 60, 75, 80],
    labels=['Speed', 'Power', 'Accuracy', 'Defense', 'Stamina', 'Agility'],
    max_val=100,
    colors=['#58C4DD'],
)

v.add(chart)

v.show(end=0)
