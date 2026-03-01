"""Showcase of ComplexPlane: complex numbers, operations, and function transforms."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    ComplexPlane, Dot, Line,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/complex_plane_demo')

# Title
title = Text(text='Complex Plane & Transformations', x=ORIGIN[0], y=40,
             font_size=36, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Complex plane with labeled points ──────────────────────────
plane = ComplexPlane(x_range=(-4, 4), y_range=(-3, 3), show_grid=True,
                    creation=0.5)
plane.fadein(0.5, 1.5)
canvas.add(plane)

# Plot some complex numbers
points = [
    (2+1j, '#FF6B6B', 'z₁=2+i'),
    (-1+2j, '#83C167', 'z₂=-1+2i'),
    (-2-1j, '#FFFF00', 'z₃=-2-i'),
    (1-2j, '#58C4DD', 'z₄=1-2i'),
]

for i, (z, color, label) in enumerate(points):
    px, py = plane.number_to_point(z)
    d = Dot(cx=px, cy=py, r=8, fill=color, creation=2 + i * 0.3)
    d.fadein(2 + i * 0.3, 2.3 + i * 0.3)
    canvas.add(d)

    lbl = Text(text=label, x=px + 15, y=py - 15,
               font_size=18, fill=color, creation=2 + i * 0.3)
    lbl.fadein(2 + i * 0.3, 2.3 + i * 0.3)
    canvas.add(lbl)

    # Line from origin to point
    ox, oy = plane.number_to_point(0)
    ln = Line(x1=ox, y1=oy, x2=px, y2=py,
              stroke=color, stroke_width=1, stroke_opacity=0.5,
              creation=2 + i * 0.3)
    ln.fadein(2 + i * 0.3, 2.3 + i * 0.3)
    canvas.add(ln)

# ── Section 2: Complex function transformation ───────────────────────────
transform_label = Text(text='f(z) = z²', x=ORIGIN[0], y=ORIGIN[1] + 380,
                       font_size=32, fill='#83C167', text_anchor='middle',
                       creation=4)
transform_label.write(4, 5)
canvas.add(transform_label)

# Apply z^2 transformation to the grid
plane.apply_complex_function(lambda z: z**2, start=5, end=7)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
