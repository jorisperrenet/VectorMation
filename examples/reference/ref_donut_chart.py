"""DonutChart with sample data."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = DonutChart(
    values=[35, 25, 20, 15, 5],
    labels=['Python', 'JS', 'Rust', 'Go', 'Other'],
    colors=['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6'],
    center_text='Languages',
)

v.add(chart)

v.show(end=0)
