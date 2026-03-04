"""BoxPlot with multiple data groups."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = BoxPlot(
    data_groups=[
        [2, 5, 7, 8, 9, 10, 12, 14, 15],
        [1, 3, 4, 6, 7, 8, 10, 11, 18],
        [5, 6, 7, 8, 9, 10, 11, 12, 13],
    ],
    x=500, y=200, plot_width=600, plot_height=500,
    box_color='#58C4DD', median_color='#E74C3C',
)

v.add(chart)

v.show(end=0)
