"""Array highlight and swap."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

arr = Array([5, 3, 8, 1, 9, 2])
arr.center_to_pos()
arr.fadein(start=0, end=0.5)
arr.highlight_cell(2, start=1, end=2, color='#58C4DD')
arr.swap_cells(0, 4, start=2.5, end=3.5)

v.add(arr)

v.show(end=4)
