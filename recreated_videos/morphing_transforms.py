"""Morphing and transformation showcase: become, fade_transform, swap, reflect,
apply_matrix, homotopy, cross_out, trail."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Text, Circle, Square, Rectangle, Star, Dot,
    ORIGIN, parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/morphing_transforms')

# Title
title = Text(text='Morphing & Transformations', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: fade_transform ──────────────────────────────────────────
label1 = Text(text='fade_transform', x=300, y=120, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label1)

src1 = Circle(r=60, cx=300, cy=250, fill='#58C4DD', creation=0.5)
src1.fadein(0.5, 1.0)
canvas.add(src1)

dst1 = Star(n=5, outer_radius=70, inner_radius=30, cx=300, cy=250,
            fill='#FF6B6B', creation=0.5)
dst1.show.set_onward(0, False)
canvas.add(dst1)

src1.fade_transform(src1, dst1, start=1.5, end=2.5)

# ── Section 2: swap ───────────────────────────────────────────────────
label2 = Text(text='swap', x=700, y=120, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label2)

swap_a = Circle(r=40, cx=600, cy=250, fill='#83C167', creation=0.5)
swap_b = Square(70, x=730, y=215, fill='#FF79C6', creation=0.5)
swap_a.fadein(0.5, 1.0)
swap_b.fadein(0.5, 1.0)
canvas.add(swap_a)
canvas.add(swap_b)

swap_a.swap(swap_a, swap_b, start=1.5, end=2.5)

# ── Section 3: reflect ────────────────────────────────────────────────
label3 = Text(text='reflect', x=1100, y=120, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label3)

ref_shape = Text(text='Hello', x=1060, y=240, font_size=36, fill='#FFFF00',
                 creation=0.5)
ref_shape.fadein(0.5, 1.0)
canvas.add(ref_shape)

ref_shape.reflect(axis='vertical', start=2.0)

# ── Section 4: apply_matrix (shear) ──────────────────────────────────
label4 = Text(text='apply_matrix (shear)', x=1550, y=120, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label4)

shear_rect = Rectangle(width=80, height=80, x=1510, y=200, fill='#BD93F9',
                        fill_opacity=0.7, creation=0.5)
shear_rect.fadein(0.5, 1.0)
canvas.add(shear_rect)

shear_rect.apply_matrix([[1, 0.4], [0, 1]], start=2.0)

# ── Section 5: homotopy ──────────────────────────────────────────────
label5 = Text(text='homotopy (wave warp)', x=300, y=380, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label5)

wave_line = Rectangle(width=300, height=10, x=150, y=470,
                      fill='#50FA7B', fill_opacity=0.8, creation=3)
wave_line.fadein(3.0, 3.5)
canvas.add(wave_line)

wave_line.homotopy(
    lambda x, y, t: (x, y + 30 * math.sin(x / 30 + t * math.tau)),
    start=3.5, end=5.5,
)

# ── Section 6: cross_out ─────────────────────────────────────────────
label6 = Text(text='cross_out', x=700, y=380, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label6)

cross_target = Text(text='Error!', x=650, y=460, font_size=32, fill='#fff',
                    creation=3)
cross_target.fadein(3.0, 3.5)
canvas.add(cross_target)

cross_mark = cross_target.cross_out(start=4.0, end=4.5, color='#FC6255')
canvas.add(cross_mark)

# ── Section 7: trail ─────────────────────────────────────────────────
label7 = Text(text='trail', x=1100, y=380, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label7)

trail_dot = Dot(cx=980, cy=500, r=15, fill='#FF6B6B', creation=3)
trail_dot.fadein(3.0, 3.5)
trail_dot.shift(dx=240, dy=0, start=3.5, end=5.5)
canvas.add(trail_dot)

ghosts = trail_dot.trail(start=3.5, end=5.5, n_copies=6, fade=True)
for g in ghosts:
    canvas.add(g)

# ── Section 8: become ────────────────────────────────────────────────
label8 = Text(text='become (style copy)', x=1550, y=380, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label8)

original = Circle(r=45, cx=1500, cy=500, fill='#666', stroke='#999',
                  creation=3)
original.fadein(3.0, 3.5)
canvas.add(original)

style_source = Circle(r=45, cx=1600, cy=500, fill='#FF79C6',
                      stroke='#FFB86C', stroke_width=4, creation=3)
style_source.fadein(3.0, 3.5)
canvas.add(style_source)

original.become(style_source, time=4.5)

# ── Section 9: transform_from_copy ────────────────────────────────────
label9 = Text(text='transform_from_copy', x=ORIGIN[0], y=600, font_size=20,
              fill='#888', text_anchor='middle', creation=6)
canvas.add(label9)

t_src = Circle(r=50, cx=860, cy=750, fill='#58C4DD', creation=6)
t_src.fadein(6.0, 6.5)
canvas.add(t_src)

t_dst = Square(90, x=1015, y=705, fill='#FF6B6B', creation=6)
t_dst.fadein(6.0, 6.5)
canvas.add(t_dst)

ghost_copy = t_src.transform_from_copy(t_dst, start=7.0, end=8.0)
canvas.add(ghost_copy)

canvas.browser_display(start=args.start or 0, end=args.end or 9,
                           fps=args.fps, port=args.port)
