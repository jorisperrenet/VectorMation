"""Bar chart grow and sort."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bc = BarChart([40, 70, 25, 55, 90], labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
              colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6'])
bc.grow_from_zero(start=0, end=1.5)
bc.animate_sort(start=2, end=3.5)

v.add(bc)

v.show(end=4)
