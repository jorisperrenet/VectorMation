"""StatusIndicator with different states."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

s1 = StatusIndicator('API Server', status='online', x=830, y=470)
s2 = StatusIndicator('Database', status='warning', x=830, y=510)
s3 = StatusIndicator('Cache', status='offline', x=830, y=550)

v.add(s1, s2, s3)

v.show(end=0)
