"""Showcase of SVG effects: Spotlight, AnimatedBoundary, Cutout,
ConvexHull, and drop shadows."""
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Circle, Dot, Rectangle,
    Spotlight, AnimatedBoundary, Cutout, ConvexHull,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/svg_effects_showcase')

# Title
title = Text(text='SVG Effects & Utilities', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: BlurFilter & DropShadowFilter ─────────────────────────────
label1 = Text(text='SVG Filters', x=350, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

# ── Drop Shadow effect ────────────────────────────────────────────────────
# Circle with drop shadow
shadow_circle = Circle(r=60, cx=200, cy=280, fill='#FF6B6B',
                       fill_opacity=0.9, creation=0.5)
shadow_circle.drop_shadow(dx=6, dy=6, blur=4, color='#000')
shadow_circle.fadein(0.5, 1)
canvas.add(shadow_circle)

shadow_label1 = Text(text='Drop Shadow', x=200, y=360,
                     font_size=16, fill='#FF6B6B', text_anchor='middle', creation=1)
canvas.add(shadow_label1)

# Rectangle with drop shadow
shadow_rect = Rectangle(width=120, height=80, x=390, y=240,
                        fill='#58C4DD', fill_opacity=0.9, creation=0.5)
shadow_rect.drop_shadow(dx=4, dy=4, color='#333')
shadow_rect.fadein(0.5, 1)
canvas.add(shadow_rect)

shadow_label2 = Text(text='Drop Shadow', x=450, y=360,
                     font_size=16, fill='#58C4DD', text_anchor='middle', creation=1)
canvas.add(shadow_label2)

# Normal circle for comparison
normal_circle = Circle(r=60, cx=200, cy=460, fill='#83C167',
                       fill_opacity=0.9, creation=1)
normal_circle.fadein(1, 1.5)
canvas.add(normal_circle)

normal_label = Text(text='No Shadow', x=200, y=540,
                    font_size=16, fill='#83C167', text_anchor='middle', creation=1.5)
canvas.add(normal_label)

# ── Section 2: ConvexHull ─────────────────────────────────────────────────
label2 = Text(text='Convex Hull', x=800, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=1.5)
canvas.add(label2)

# Scatter some dots
dots_points = [
    (680, 200), (750, 350), (700, 450), (850, 180),
    (900, 400), (800, 300), (950, 280), (720, 280),
]
dots = []
for i, (px, py) in enumerate(dots_points):
    d = Dot(cx=px, cy=py, r=6, fill='#FFFF00', creation=1.8)
    d.fadein(1.8 + i * 0.1, 2.0 + i * 0.1)
    canvas.add(d)
    dots.append(d)

# Convex hull around the points
hull = ConvexHull(*dots_points, stroke='#FF6B6B', stroke_width=2,
                 fill='#FF6B6B', fill_opacity=0.1, creation=2.5)
hull.create(2.5, 3.5)
canvas.add(hull)

# ── Section 3: Cutout ────────────────────────────────────────────────────
label3 = Text(text='Cutout (Spotlight Overlay)', x=1400, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3)
canvas.add(label3)

# Some background content
bg_rect = Rectangle(width=400, height=300, x=1200, y=180,
                    fill='#264653', fill_opacity=0.8, creation=3)
bg_rect.fadein(3, 3.5)
canvas.add(bg_rect)

bg_text = Text(text='Hidden Content', x=1400, y=330,
               font_size=28, fill='#fff', text_anchor='middle', creation=3)
bg_text.fadein(3, 3.5)
canvas.add(bg_text)

# Cutout revealing a window
cutout = Cutout(hole_x=1250, hole_y=250, hole_w=300, hole_h=160,
                color='#000', opacity=0.8, creation=3.5)
cutout.fadein(3.5, 4)
canvas.add(cutout)

# ── Section 4: Spotlight ─────────────────────────────────────────────────
label4 = Text(text='Spotlight', x=350, y=600,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label4)

# Content behind spotlight
target_dot = Dot(cx=350, cy=780, r=20, fill='#FF6B6B', creation=4)
target_dot.fadein(4, 4.5)
canvas.add(target_dot)

target_label = Text(text='Focus here', x=350, y=830,
                    font_size=18, fill='#fff', text_anchor='middle', creation=4)
canvas.add(target_label)

spot = Spotlight(target=(350, 780), radius=80, color='#000000',
                 opacity=0.7, creation=4.5)
canvas.add(spot)

# Animate spotlight moving
spot.set_target((500, 780), start=5.5, end=6.5)
spot.set_radius(120, start=5.5, end=6.5)

# ── Section 5: AnimatedBoundary ──────────────────────────────────────────
label5 = Text(text='Animated Boundary', x=1000, y=600,
              font_size=22, fill='#aaa', text_anchor='middle', creation=5)
canvas.add(label5)

target_box = Rectangle(width=200, height=120, x=900, y=720,
                       fill='#264653', fill_opacity=0.8, stroke='#444',
                       creation=5)
target_box.fadein(5, 5.5)
canvas.add(target_box)

box_text = Text(text='Important!', x=1000, y=785,
                font_size=24, fill='#fff', text_anchor='middle', creation=5)
box_text.fadein(5, 5.5)
canvas.add(box_text)

boundary = AnimatedBoundary(target_box,
                            colors=['#FF6B6B', '#FFFF00', '#58C4DD', '#83C167'],
                            cycle_rate=0.5, buff=10, stroke_width=3,
                            creation=5.5)
canvas.add(boundary)

# ── Section 6: Multiple overlapping effects ──────────────────────────────
label6 = Text(text='Combined Effects', x=1500, y=600,
              font_size=22, fill='#aaa', text_anchor='middle', creation=6)
canvas.add(label6)

combo_circle = Circle(r=70, cx=1500, cy=780, fill='#83C167',
                      fill_opacity=0.7, creation=6)
combo_circle.fadein(6, 6.5)
canvas.add(combo_circle)

combo_boundary = AnimatedBoundary(combo_circle,
                                  colors=['#FFFF00', '#FF6B6B'],
                                  cycle_rate=1, creation=6.5)
canvas.add(combo_boundary)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
