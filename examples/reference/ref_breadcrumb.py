"""Breadcrumb navigation trail."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bc = Breadcrumb('Home', 'Products', 'Electronics', 'Laptops',
                x=750, y=530, active_color='#58C4DD')

v.add(bc)

v.show(end=0)
