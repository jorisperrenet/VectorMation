import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/complex_plane')
canvas.set_background()

# Create a complex plane and plot roots of unity
plane = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3), show_grid=True)
plane.fadein(0, 1)

# Plot 5th roots of unity as dots connected by lines
n = 5
roots = []
for k in range(n):
    angle = 2 * math.pi * k / n
    z = complex(math.cos(angle), math.sin(angle))
    px, py = plane.number_to_point(z)
    dot = Dot(cx=px, cy=py, r=8, fill='#FF6666', stroke_width=0)
    dot.fadein(1, 1.5)
    roots.append((px, py, dot))

# Connect them with lines to form a pentagon
lines = []
for i in range(n):
    x1, y1, _ = roots[i]
    x2, y2, _ = roots[(i + 1) % n]
    line = Line(x1=x1, y1=y1, x2=x2, y2=y2,
                stroke='#FFFF00', stroke_width=2)
    line.create(1.5, 2.5)
    lines.append(line)

title = Text(text='5th Roots of Unity', x=960, y=60,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(plane, *[d for _, _, d in roots], *lines, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
