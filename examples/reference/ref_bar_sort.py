"""Bar chart with sorting animation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bc = BarChart([3, 7, 2, 5], labels=['Q1', 'Q2', 'Q3', 'Q4'],
              colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12'])
bc.fadein(start=0, end=1)
bc.animate_sort(start=2, end=3)

v.add(bc)

v.show(end=4)
