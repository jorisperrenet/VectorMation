"""Matrix with bracket delimiters."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

matrix = Matrix(
    data=[
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ],
    font_size=40,
)

v.add(matrix)

v.show(end=0)
