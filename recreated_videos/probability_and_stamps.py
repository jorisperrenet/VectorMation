"""Showcase of SampleSpace, Stamp, and RoundedCornerPolygon."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Star, SampleSpace, Stamp, RoundedCornerPolygon, VCollection,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/probability_and_stamps')

# Title
title = Text(text='SampleSpace, Stamps & Rounded Polygons', x=ORIGIN[0], y=40,
             font_size=36, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: SampleSpace ──────────────────────────────────────────────
label1 = Text(text='Probability Sample Space', x=380, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

ss = SampleSpace(width=400, height=300, x=180, y=140, creation=0.5)
ss.fadein(0.5, 1.5)
canvas.add(ss)

# Divide horizontally: P(A) = 0.6
ss.divide_horizontally(0.6, colors=('#58C4DD', '#FF6B6B'),
                        labels=('P(A)=0.6', "P(A')=0.4"), creation=1.5)

lbl_a = Text(text='Event A', x=330, y=290, font_size=16,
             fill='#58C4DD', text_anchor='middle', creation=2)
lbl_a.fadein(2, 2.5)
canvas.add(lbl_a)

lbl_b = Text(text="Complement A'", x=510, y=290, font_size=16,
             fill='#FF6B6B', text_anchor='middle', creation=2)
lbl_b.fadein(2, 2.5)
canvas.add(lbl_b)

# ── Section 2: Stamp ───────────────────────────────────────────────────
label2 = Text(text='Stamp Pattern', x=380, y=520,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3)
canvas.add(label2)

# Create a template shape and stamp it at multiple positions
template = Star(n=5, outer_radius=25, inner_radius=12, cx=0, cy=0,
                fill='#FFFF00', stroke='#FF6B6B', stroke_width=2)

positions = [
    (200, 650), (300, 620), (400, 680), (500, 640),
    (250, 730), (350, 750), (450, 720),
]
stamps = Stamp(template, positions, creation=3)
stamps.stagger_fadein(start=3.2, end=4.2)
canvas.add(stamps)

# ── Section 3: RoundedCornerPolygon ─────────────────────────────────────
label3 = Text(text='Rounded Corner Polygons', x=1100, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label3)

# Triangle with rounded corners
tri = RoundedCornerPolygon(
    (900, 400), (1050, 180), (1200, 400),
    radius=20, fill='#FF6B6B', fill_opacity=0.6,
    stroke='#FF6B6B', stroke_width=3, creation=4)
tri.fadein(4, 4.5)
canvas.add(tri)

tri_label = Text(text='r=20', x=1050, y=420,
                 font_size=14, fill='#FF6B6B', text_anchor='middle', creation=4.5)
canvas.add(tri_label)

# Pentagon with larger radius
import math
pent_pts = []
for i in range(5):
    a = math.radians(-90 + i * 72)
    pent_pts.append((1450 + 100 * math.cos(a), 300 + 100 * math.sin(a)))

pent = RoundedCornerPolygon(
    *pent_pts, radius=30, fill='#83C167', fill_opacity=0.5,
    stroke='#83C167', stroke_width=3, creation=4.5)
pent.fadein(4.5, 5)
canvas.add(pent)

pent_label = Text(text='r=30', x=1450, y=420,
                  font_size=14, fill='#83C167', text_anchor='middle', creation=5)
canvas.add(pent_label)

# Hexagon with small radius
hex_pts = []
for i in range(6):
    a = math.radians(i * 60)
    hex_pts.append((1100, 650) if i == 0 else
                   (1100 + 90 * math.cos(a), 650 + 90 * math.sin(a)))

# Proper hexagon
hex_pts = [(1100 + 90 * math.cos(math.radians(i * 60)),
            650 + 90 * math.sin(math.radians(i * 60))) for i in range(6)]
hexa = RoundedCornerPolygon(
    *hex_pts, radius=10, fill='#58C4DD', fill_opacity=0.5,
    stroke='#58C4DD', stroke_width=3, creation=5)
hexa.fadein(5, 5.5)
canvas.add(hexa)

hex_label = Text(text='r=10', x=1100, y=760,
                 font_size=14, fill='#58C4DD', text_anchor='middle', creation=5.5)
canvas.add(hex_label)

# Comparison: varying radius on same shape
label4 = Text(text='Radius Comparison', x=1500, y=520,
              font_size=18, fill='#aaa', text_anchor='middle', creation=5.5)
canvas.add(label4)

base_pts = [(1400, 600), (1600, 600), (1600, 780), (1400, 780)]
for r, color, yoff in [(5, '#FF6B6B', 0), (20, '#FFFF00', 0), (40, '#83C167', 0)]:
    shifted = [(x, y + yoff) for x, y in base_pts]
    p = RoundedCornerPolygon(*shifted, radius=r, fill=color, fill_opacity=0.15,
                             stroke=color, stroke_width=2, creation=5.5)
    p.fadein(5.5, 6)
    canvas.add(p)

radius_labels = VCollection(
    Text(text='r=5', x=1500, y=595, font_size=12, fill='#FF6B6B', text_anchor='middle', creation=6),
    Text(text='r=20', x=1500, y=700, font_size=12, fill='#FFFF00', text_anchor='middle', creation=6),
    Text(text='r=40', x=1500, y=790, font_size=12, fill='#83C167', text_anchor='middle', creation=6),
)
radius_labels.stagger_fadein(start=6, end=6.5)
canvas.add(radius_labels)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 7,
                           fps=args.fps, port=args.port)
