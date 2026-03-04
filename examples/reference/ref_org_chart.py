"""OrgChart tree structure."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

tree = ('CEO', [
    ('CTO', [
        ('Dev Lead', []),
        ('QA Lead', []),
    ]),
    ('CFO', [
        ('Accounting', []),
    ]),
    ('COO', [
        ('Operations', []),
        ('HR', []),
    ]),
])

chart = OrgChart(tree, y=100, h_spacing=200, v_spacing=120)

v.add(chart)

v.show(end=0)
