"""MatrixHeatmap with labeled rows and columns."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = MatrixHeatmap(
    data=[
        [1.0, 0.8, 0.2, 0.1],
        [0.8, 1.0, 0.5, 0.3],
        [0.2, 0.5, 1.0, 0.7],
        [0.1, 0.3, 0.7, 1.0],
    ],
    row_labels=['A', 'B', 'C', 'D'],
    col_labels=['A', 'B', 'C', 'D'],
    x=600, y=250, cell_size=80, font_size=18,
)

v.add(chart)

v.show(end=0)
