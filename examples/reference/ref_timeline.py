"""TimelineBar with labeled markers."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

timeline = TimelineBar(
    markers={0: 'Start', 2: 'Design', 5: 'Build', 8: 'Test', 10: 'Launch'},
    total_duration=10,
    x=200, y=540, width=1520,
)

v.add(timeline)

v.show(end=0)
