"""Arrange and arrange_in_grid layout."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Row arrangement
row = VCollection(
    Circle(r=30, fill='#58C4DD'),
    Rectangle(60, 60, fill='#FF6B6B'),
    RegularPolygon(3, radius=30, fill='#83C167'),
    RegularPolygon(5, radius=30, fill='#F1C40F'),
)
row.center_to_pos(posy=300)
row.arrange(direction='right', buff=30)
row.stagger('fadein', start=0, end=1.5, overlap=0.5)

# Grid arrangement
grid = VCollection(
    *[Rectangle(50, 50, fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71', '#1ABC9C',
                              '#3498DB', '#9B59B6', '#E91E63', '#795548'][i]) for i in range(9)]
)
grid.arrange_in_grid(rows=3, cols=3, buff=10)
grid.center_to_pos(posy=650)
grid.stagger('fadein', start=1, end=2.5, overlap=0.5)

v.add(row, grid)

v.show(end=3)
