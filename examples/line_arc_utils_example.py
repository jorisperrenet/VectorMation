"""Example: Line and Arc utility methods."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import tempfile
from vectormation.objects import VectorMathAnim, Line, Arc, Text, Dot, parse_args

anim = VectorMathAnim(tempfile.mkdtemp())

# A diagonal line
line = Line(x1=300, y1=200, x2=900, y2=600, stroke='#58C4DD', stroke_width=3)
anim.add(line)

# Show line properties
length = line.get_length()
angle = line.get_angle()
sx, sy = line.get_start()
ex, ey = line.get_end()
ux, uy = line.get_unit_vector()

anim.add(Dot(cx=sx, cy=sy, fill='#83C167'))
anim.add(Dot(cx=ex, cy=ey, fill='#FF6B6B'))
anim.add(Text(f'length={length:.0f}  angle={angle:.1f}°', x=600, y=150,
              font_size=28, text_anchor='middle'))
anim.add(Text(f'unit=({ux:.2f}, {uy:.2f})', x=600, y=185,
              font_size=24, text_anchor='middle', fill='#aaa'))

# An arc
arc = Arc(cx=1400, cy=400, r=150, start_angle=30, end_angle=150,
          stroke='#FF79C6', stroke_width=3)
anim.add(arc)

# Show arc properties
sp = arc.get_start_point()
ep = arc.get_end_point()
arc_len = arc.get_arc_length()

anim.add(Dot(cx=sp[0], cy=sp[1], fill='#83C167'))
anim.add(Dot(cx=ep[0], cy=ep[1], fill='#FF6B6B'))
anim.add(Text(f'arc length={arc_len:.0f}', x=1400, y=600,
              font_size=24, text_anchor='middle'))

# Animate line length changing
line.p2.set(1, 3, lambda t: (900 + 200 * (t - 1) / 2, 600))
anim.add(Text(f'Animated: length changes over time',
              x=600, y=750, font_size=24, text_anchor='middle', fill='#888'))

args = parse_args()
if not args.no_display:
    anim.browser_display(0, 4, fps=args.fps, port=args.port)
