"""Showcase of advanced animation effects: telegraph, slingshot, elastic_bounce, etc."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Circle, Rectangle, Text, Dot, Square,
    ORIGIN, parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animation_effects_showcase')

# Title
title = Text(text='Animation Effects Showcase', x=ORIGIN[0], y=80,
             font_size=42, fill='#58C4DD', text_anchor='middle')
title.write(0, 1)
canvas.add(title)

t = 0.5  # start offset

# --- Row 1: Telegraph, Flicker, Strobe ---
label1 = Text(text='telegraph', x=250, y=200, font_size=20, fill='#888',
              text_anchor='middle', creation=t)
c1 = Circle(r=40, cx=250, cy=300, fill='#58C4DD', creation=t)
c1.telegraph(start=t + 0.5, end=t + 1.5)
canvas.add(label1, c1)

label2 = Text(text='flicker', x=640, y=200, font_size=20, fill='#888',
              text_anchor='middle', creation=t)
c2 = Circle(r=40, cx=640, cy=300, fill='#83C167', creation=t)
c2.flicker(start=t + 0.5, end=t + 2.5, frequency=6)
canvas.add(label2, c2)

label3 = Text(text='strobe', x=1030, y=200, font_size=20, fill='#888',
              text_anchor='middle', creation=t)
c3 = Circle(r=40, cx=1030, cy=300, fill='#FF6B6B', creation=t)
c3.strobe(start=t + 0.5, end=t + 2.5, n_flashes=8)
canvas.add(label3, c3)

label4 = Text(text='elastic_bounce', x=1420, y=200, font_size=20, fill='#888',
              text_anchor='middle', creation=t)
c4 = Circle(r=40, cx=1420, cy=300, fill='#FFFF00', creation=t)
c4.elastic_bounce(start=t + 0.5, end=t + 2.5, height=120, n_bounces=4)
canvas.add(label4, c4)

# --- Row 2: Slingshot, Skate, Domino, Wave Through ---
t2 = 3.5

label5 = Text(text='slingshot', x=250, y=500, font_size=20, fill='#888',
              text_anchor='middle', creation=t2)
c5 = Dot(r=20, cx=150, cy=600, creation=t2)
c5.slingshot(350, 600, start=t2 + 0.3, end=t2 + 1.5)
canvas.add(label5, c5)

label6 = Text(text='skate', x=640, y=500, font_size=20, fill='#888',
              text_anchor='middle', creation=t2)
c6 = Square(60, fill='#BD93F9', creation=t2)
c6.center_to_pos(540, 600, start=t2)
c6.skate(740, 600, start=t2 + 0.3, end=t2 + 1.5, degrees=720)
canvas.add(label6, c6)

label7 = Text(text='domino', x=1030, y=500, font_size=20, fill='#888',
              text_anchor='middle', creation=t2)
r7 = Rectangle(50, 120, fill='#FFB86C', creation=t2)
r7.center_to_pos(1030, 620, start=t2)
r7.domino(start=t2 + 0.5, end=t2 + 1.2, direction='right')
canvas.add(label7, r7)

label8 = Text(text='wave_through', x=1420, y=500, font_size=20, fill='#888',
              text_anchor='middle', creation=t2)
c8 = Circle(r=40, cx=1420, cy=600, fill='#FF79C6', creation=t2)
c8.wave_through(start=t2 + 0.3, end=t2 + 2.0, amplitude=40, frequency=3)
canvas.add(label8, c8)

# --- Row 3: Morph Scale, Elastic Scale, Squeeze, Glitch Shift ---
t3 = 6.0

label9 = Text(text='morph_scale', x=250, y=750, font_size=20, fill='#888',
              text_anchor='middle', creation=t3)
c9 = Circle(r=35, cx=250, cy=860, fill='#B8BB26', creation=t3)
c9.morph_scale(target_scale=2.0, start=t3 + 0.3, end=t3 + 1.5)
canvas.add(label9, c9)

label10 = Text(text='elastic_scale', x=640, y=750, font_size=20, fill='#888',
               text_anchor='middle', creation=t3)
c10 = Circle(r=35, cx=640, cy=860, fill='#58C4DD', creation=t3)
c10.elastic_scale(start=t3 + 0.3, end=t3 + 1.5, factor=1.8)
canvas.add(label10, c10)

label11 = Text(text='squeeze', x=1030, y=750, font_size=20, fill='#888',
               text_anchor='middle', creation=t3)
c11 = Circle(r=35, cx=1030, cy=860, fill='#FF6B6B', creation=t3)
c11.squeeze(start=t3 + 0.3, end=t3 + 1.5, axis='x', factor=0.4)
canvas.add(label11, c11)

label12 = Text(text='glitch_shift', x=1420, y=750, font_size=20, fill='#888',
               text_anchor='middle', creation=t3)
c12 = Rectangle(70, 50, fill='#83C167', creation=t3)
c12.center_to_pos(1420, 860, start=t3)
c12.glitch_shift(start=t3 + 0.3, end=t3 + 2.0, intensity=30, seed=42)
canvas.add(label12, c12)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8.5,
                           fps=args.fps, port=args.port)
