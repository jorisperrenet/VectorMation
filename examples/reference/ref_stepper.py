"""Stepper progress indicator."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

stepper = Stepper(
    steps=['Plan', 'Design', 'Build', 'Test', 'Ship'],
    x=310, y=520, spacing=280, active=2,
    active_color='#58C4DD',
)

v.add(stepper)

v.show(end=0)
