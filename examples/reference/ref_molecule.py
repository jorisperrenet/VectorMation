"""Molecule2D: caffeine molecule."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Caffeine (C8H10N4O2) - approximate 2D layout
caffeine = Molecule2D(
    atoms=[
        ('N', -1.2,  0.7),   # 0  N1
        ('C',  0.0,  1.2),   # 1  C2
        ('N',  1.2,  0.7),   # 2  N3
        ('C',  1.2, -0.5),   # 3  C4
        ('C',  0.0, -1.0),   # 4  C5
        ('C', -1.2, -0.5),   # 5  C6
        ('N',  0.0, -2.2),   # 6  N7
        ('C',  1.2, -1.8),   # 7  C8
        ('N',  2.2, -1.0),   # 8  N9
        ('O', -2.3, -1.0),   # 9  O (on C6)
        ('O',  0.0,  2.4),   # 10 O (on C2)
    ],
    bonds=[
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),  # six-membered ring
        (4, 6), (6, 7), (7, 8), (8, 3),                    # five-membered ring
        (5, 9, 2),                                          # C6=O double bond
        (1, 10, 2),                                         # C2=O double bond
        (6, 7, 2),                                          # C8=N7 double bond
    ],
    scale=80, cx=960, cy=540, atom_radius=22, font_size=16,
)

v.add(caffeine)

v.show(end=0)
