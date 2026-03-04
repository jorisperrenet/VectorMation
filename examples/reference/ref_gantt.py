"""GanttChart for project timelines."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = GanttChart(
    tasks=[
        ('Research', 0, 3, '#58C4DD'),
        ('Design', 2, 5, '#E74C3C'),
        ('Develop', 4, 9, '#2ECC71'),
        ('Testing', 7, 10, '#F39C12'),
        ('Deploy', 9, 11, '#9B59B6'),
    ],
    x=100, y=200, width=1600,
)

v.add(chart)

v.show(end=0)
