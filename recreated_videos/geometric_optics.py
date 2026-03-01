"""Geometric optics demo: lenses, rays, and image formation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Lens, Ray, Dot, Line,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/geometric_optics')

# Title
title = Text(text='Geometric Optics', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Convex lens with parallel rays ──────────────────────────
label1 = Text(text='Convex Lens — Parallel Rays Focus', x=480, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

lens1 = Lens(cx=480, cy=320, height=300, focal_length=200,
             color='#58C4DD', creation=0.5)
lens1.fadein(0.5, 1.0)
canvas.add(lens1)

# Parallel rays converging at focal point
for offset in [-100, -50, 0, 50, 100]:
    ray = Ray(x1=100, y1=320 + offset, angle=0, length=800,
              lenses=[lens1], color='#FFFF00', stroke_width=1.5,
              creation=1.0)
    ray.fadein(1.0, 1.5)
    canvas.add(ray)

# ── Section 2: Concave lens with diverging rays ───────────────────────
label2 = Text(text='Concave Lens — Diverging Rays', x=1440, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label2)

lens2 = Lens(cx=1440, cy=320, height=300, focal_length=-200,
             color='#FF6B6B', creation=0.5)
lens2.fadein(0.5, 1.0)
canvas.add(lens2)

for offset in [-100, -50, 0, 50, 100]:
    ray = Ray(x1=1060, y1=320 + offset, angle=0, length=800,
              lenses=[lens2], color='#FFFF00', stroke_width=1.5,
              creation=1.5)
    ray.fadein(1.5, 2.0)
    canvas.add(ray)

# ── Section 3: Image formation ─────────────────────────────────────────
label3 = Text(text='Image Formation (Thin-Lens Equation)', x=ORIGIN[0], y=590,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3)
canvas.add(label3)

lens3 = Lens(cx=960, cy=780, height=250, focal_length=180,
             color='#83C167', show_axis=True, creation=3)
lens3.fadein(3, 3.5)
canvas.add(lens3)

# Object: small arrow at 2f
obj_x = 960 - 360  # 2x focal length
obj_top = 720
obj_bottom = 780
obj_arrow = Line(obj_x, obj_bottom, obj_x, obj_top,
                 stroke='#FF6B6B', stroke_width=3, creation=3.5)
obj_arrow.fadein(3.5, 4.0)
canvas.add(obj_arrow)
obj_tip = Dot(cx=obj_x, cy=obj_top, r=4, fill='#FF6B6B', creation=3.5)
obj_tip.fadein(3.5, 4.0)
canvas.add(obj_tip)

obj_label = Text(text='Object', x=obj_x, y=obj_bottom + 25,
                 font_size=16, fill='#FF6B6B', text_anchor='middle', creation=3.5)
canvas.add(obj_label)

# Compute image position using thin-lens equation
img_point = lens3.image_point(obj_x, obj_top)
if img_point:
    img_x, img_y = img_point
    img_arrow = Line(img_x, 780, img_x, img_y,
                     stroke='#58C4DD', stroke_width=3, creation=4.5)
    img_arrow.fadein(4.5, 5.0)
    canvas.add(img_arrow)
    img_tip = Dot(cx=img_x, cy=img_y, r=4, fill='#58C4DD', creation=4.5)
    img_tip.fadein(4.5, 5.0)
    canvas.add(img_tip)
    img_label = Text(text='Image', x=img_x, y=790,
                     font_size=16, fill='#58C4DD', text_anchor='middle', creation=4.5)
    canvas.add(img_label)

# Three principal rays for image construction
# Ray 1: parallel to axis → through focal point
ray1 = Ray(x1=obj_x, y1=obj_top, angle=0, length=1200,
           lenses=[lens3], color='#FFFF00', stroke_width=1, creation=4)
ray1.fadein(4, 4.5)
canvas.add(ray1)

# Formula
formula = Text(text='1/f = 1/dₒ + 1/dᵢ', x=ORIGIN[0], y=940,
               font_size=28, fill='#83C167', text_anchor='middle', creation=5)
formula.write(5, 6)
canvas.add(formula)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 7,
                           fps=args.fps, port=args.port)
