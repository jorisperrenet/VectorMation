"""Showcase of extended shape primitives: CubicBezier, ArcBetweenPoints, Elbow,
AnnularSector, ArcPolygon, Wedge, Spiral, and DashedLine."""
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Dot, VCollection,
    CubicBezier, ArcBetweenPoints, Elbow, AnnularSector, ArcPolygon,
    Wedge, Spiral, DashedLine, Annulus,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/curves_and_shapes_ext')

# Title
title = Text(text='Extended Shapes & Curves', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: CubicBezier ────────────────────────────────────────────────
label1 = Text(text='Cubic Bezier', x=300, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

# Control points
cp = [(120, 350), (200, 150), (400, 500), (480, 250)]
bezier = CubicBezier(p0=cp[0], p1=cp[1], p2=cp[2], p3=cp[3],
                     stroke='#FF6B6B', stroke_width=3, creation=0.5)
bezier.create(0.5, 1.5)
canvas.add(bezier)

# Show control points and lines
for i, (px, py) in enumerate(cp):
    d = Dot(cx=px, cy=py, r=5, fill='#FFFF00', creation=1)
    d.fadein(1, 1.3)
    canvas.add(d)

control_line1 = DashedLine(cp[0][0], cp[0][1], cp[1][0], cp[1][1],
                           stroke='#555', stroke_width=1, creation=1)
control_line2 = DashedLine(cp[2][0], cp[2][1], cp[3][0], cp[3][1],
                           stroke='#555', stroke_width=1, creation=1)
control_line1.fadein(1, 1.3)
control_line2.fadein(1, 1.3)
canvas.add(control_line1)
canvas.add(control_line2)

# ── Section 2: ArcBetweenPoints ───────────────────────────────────────────
label2 = Text(text='Arc Between Points', x=780, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=1.5)
canvas.add(label2)

dot_a = Dot(cx=620, cy=350, r=6, fill='#FF6B6B', creation=1.5)
dot_b = Dot(cx=940, cy=350, r=6, fill='#83C167', creation=1.5)
canvas.add(dot_a)
canvas.add(dot_b)

# Multiple arcs with different angles
for angle, color, opacity in [(30, '#FFFF00', 0.8), (60, '#FF6B6B', 0.6),
                                (90, '#58C4DD', 0.5), (120, '#83C167', 0.4)]:
    arc = ArcBetweenPoints((620, 350), (940, 350), angle=angle,
                           stroke=color, stroke_width=2, fill_opacity=0,
                           stroke_opacity=opacity, creation=1.5)
    arc.create(1.8, 2.5)
    canvas.add(arc)

# Negative angle arcs below
for angle, color, opacity in [(-30, '#FFFF00', 0.8), (-60, '#FF6B6B', 0.6),
                                (-90, '#58C4DD', 0.5)]:
    arc = ArcBetweenPoints((620, 350), (940, 350), angle=angle,
                           stroke=color, stroke_width=2, fill_opacity=0,
                           stroke_opacity=opacity, creation=1.5)
    arc.create(1.8, 2.5)
    canvas.add(arc)

angle_labels = VCollection(
    Text(text='30', x=780, y=285, font_size=14, fill='#FFFF00', text_anchor='middle', creation=2.5),
    Text(text='60', x=780, y=245, font_size=14, fill='#FF6B6B', text_anchor='middle', creation=2.5),
    Text(text='90', x=780, y=200, font_size=14, fill='#58C4DD', text_anchor='middle', creation=2.5),
    Text(text='120', x=780, y=155, font_size=14, fill='#83C167', text_anchor='middle', creation=2.5),
)
angle_labels.stagger_fadein(start=2.5, end=3.2)
canvas.add(angle_labels)

# ── Section 3: Elbow ─────────────────────────────────────────────────────
label3 = Text(text='Elbow Connector', x=1200, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=2.5)
canvas.add(label3)

elbow1 = Elbow(cx=1100, cy=250, width=80, height=80,
               stroke='#58C4DD', stroke_width=3, creation=2.5)
elbow2 = Elbow(cx=1200, cy=250, width=60, height=120,
               stroke='#FF6B6B', stroke_width=3, creation=2.5)
elbow3 = Elbow(cx=1300, cy=250, width=100, height=50,
               stroke='#83C167', stroke_width=3, creation=2.5)
for e in [elbow1, elbow2, elbow3]:
    e.create(2.8, 3.5)
    canvas.add(e)

# ── Section 4: AnnularSector ─────────────────────────────────────────────
label4 = Text(text='Annular Sectors', x=1600, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3)
canvas.add(label4)

sectors = [
    AnnularSector(inner_radius=40, outer_radius=120, cx=1600, cy=300,
                  start_angle=0, end_angle=90, fill='#FF6B6B', creation=3),
    AnnularSector(inner_radius=40, outer_radius=120, cx=1600, cy=300,
                  start_angle=90, end_angle=180, fill='#58C4DD', creation=3),
    AnnularSector(inner_radius=40, outer_radius=120, cx=1600, cy=300,
                  start_angle=180, end_angle=270, fill='#83C167', creation=3),
    AnnularSector(inner_radius=40, outer_radius=120, cx=1600, cy=300,
                  start_angle=270, end_angle=360, fill='#FFFF00', creation=3),
]
for i, s in enumerate(sectors):
    s.fadein(3 + i * 0.2, 3.3 + i * 0.2)
    canvas.add(s)

# ── Section 5: ArcPolygon ────────────────────────────────────────────────
label5 = Text(text='Arc Polygon', x=300, y=560,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3.5)
canvas.add(label5)

# Triangle with curved edges
arc_tri = ArcPolygon(
    (200, 700), (400, 700), (300, 580),
    arc_angles=30,
    stroke='#FF6B6B', stroke_width=3, fill='#FF6B6B', fill_opacity=0.2,
    creation=3.5)
arc_tri.create(3.5, 4.2)
canvas.add(arc_tri)

# Pentagon with larger arcs
import math
pent_pts = []
for i in range(5):
    a = math.radians(90 + i * 72)
    pent_pts.append((300 + 80 * math.cos(a), 900 + 80 * math.sin(a)))

arc_pent = ArcPolygon(*pent_pts, arc_angles=40,
                      stroke='#58C4DD', stroke_width=2, fill='#58C4DD',
                      fill_opacity=0.2, creation=4)
arc_pent.create(4, 4.7)
canvas.add(arc_pent)

# ── Section 6: Wedge / Sector ────────────────────────────────────────────
label6 = Text(text='Wedge (Sector)', x=780, y=560,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label6)

wedge1 = Wedge(r=120, start_angle=0, end_angle=60, cx=700, cy=750,
               fill='#FF6B6B', fill_opacity=0.7, creation=4.5)
wedge2 = Wedge(r=120, start_angle=60, end_angle=150, cx=700, cy=750,
               fill='#58C4DD', fill_opacity=0.7, creation=4.5)
wedge3 = Wedge(r=120, start_angle=150, end_angle=270, cx=700, cy=750,
               fill='#83C167', fill_opacity=0.7, creation=4.5)
for w in [wedge1, wedge2, wedge3]:
    w.fadein(4.5, 5)
    canvas.add(w)

# ── Section 7: Spiral ────────────────────────────────────────────────────
label7 = Text(text='Spirals', x=1200, y=560,
              font_size=22, fill='#aaa', text_anchor='middle', creation=5)
canvas.add(label7)

# Archimedean spiral
spiral1 = Spiral(a=0, b=12, turns=4, cx=1100, cy=780,
                 stroke='#FFFF00', stroke_width=2, creation=5)
spiral1.create(5, 6)
canvas.add(spiral1)

spiral1_label = Text(text='Archimedean', x=1100, y=920,
                     font_size=14, fill='#FFFF00', text_anchor='middle', creation=5.5)
canvas.add(spiral1_label)

# Logarithmic spiral
spiral2 = Spiral(a=5, b=0.15, turns=3, log_spiral=True, cx=1300, cy=780,
                 stroke='#FF6B6B', stroke_width=2, creation=5)
spiral2.create(5.5, 6.5)
canvas.add(spiral2)

spiral2_label = Text(text='Logarithmic', x=1300, y=920,
                     font_size=14, fill='#FF6B6B', text_anchor='middle', creation=5.5)
canvas.add(spiral2_label)

# ── Section 8: Annulus ───────────────────────────────────────────────────
label8 = Text(text='Annulus (Ring)', x=1600, y=560,
              font_size=22, fill='#aaa', text_anchor='middle', creation=5.5)
canvas.add(label8)

annulus = Annulus(inner_radius=50, outer_radius=120, cx=1600, cy=780,
                 fill='#58C4DD', fill_opacity=0.5, stroke='#58C4DD',
                 stroke_width=2, creation=5.5)
annulus.fadein(5.5, 6)
canvas.add(annulus)

# DashedLine decoration
dashed = DashedLine(1500, 780, 1700, 780,
                    stroke='#83C167', stroke_width=2, creation=6)
dashed.create(6, 6.5)
canvas.add(dashed)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 7,
                           fps=args.fps, port=args.port)
