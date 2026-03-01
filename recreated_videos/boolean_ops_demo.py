"""Boolean Ops & Special Effects Demo — Union, Intersection, Difference, Exclusion, Cutout, ConvexHull, StreamLines."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/boolean_ops')
canvas.set_background()
T = 12.0

# =============================================================================
# Phase 1 (0–4s): Boolean Operations
# =============================================================================

phase1_title = Text(
    text='Boolean Operations', x=960, y=70, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.5)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# --- Reference circles (faded, shown briefly) ---
ref_a = Circle(r=80, cx=250, cy=350, fill='#58C4DD', fill_opacity=0.25,
               stroke='#58C4DD', stroke_width=1.5, stroke_dasharray='6 4')
ref_b = Circle(r=80, cx=340, cy=350, fill='#E84D60', fill_opacity=0.25,
               stroke='#E84D60', stroke_width=1.5, stroke_dasharray='6 4')
for obj in [ref_a, ref_b]:
    obj.fadein(0.2, 0.6)
    obj.fadeout(1.0, 1.3)
    canvas.add(obj)

ref_label = Text(text='A + B', x=295, y=470, font_size=24,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ref_label.fadein(0.3, 0.6)
ref_label.fadeout(1.0, 1.3)
canvas.add(ref_label)

# Column positions for the four operations
cols = [270, 690, 1110, 1530]
row_y = 450
label_y = 620

# --- Union ---
union_shape = Union(
    Circle(r=80, cx=cols[0] - 45, cy=row_y),
    Circle(r=80, cx=cols[0] + 45, cy=row_y),
    fill='#4ECDC4', fill_opacity=0.75, stroke='#FFFFFF', stroke_width=2,
)
union_shape.fadein(0.8, 1.3)
union_shape.fadeout(3.5, 4.0)
canvas.add(union_shape)

union_ref_a = Circle(r=80, cx=cols[0] - 45, cy=row_y, fill_opacity=0,
                     stroke='#4ECDC4', stroke_width=1, stroke_dasharray='5 3')
union_ref_b = Circle(r=80, cx=cols[0] + 45, cy=row_y, fill_opacity=0,
                     stroke='#4ECDC4', stroke_width=1, stroke_dasharray='5 3')
for obj in [union_ref_a, union_ref_b]:
    obj.fadein(0.8, 1.3)
    obj.fadeout(3.5, 4.0)
    canvas.add(obj)

union_label = Text(text='Union', x=cols[0], y=label_y, font_size=30,
                   fill='#4ECDC4', stroke_width=0, text_anchor='middle')
union_label.fadein(1.0, 1.4)
union_label.fadeout(3.5, 4.0)
canvas.add(union_label)

# --- Intersection ---
inter_shape = Intersection(
    Circle(r=80, cx=cols[1] - 45, cy=row_y),
    Circle(r=80, cx=cols[1] + 45, cy=row_y),
    fill='#9B59B6', fill_opacity=0.75, stroke='#FFFFFF', stroke_width=2,
)
inter_shape.fadein(1.3, 1.8)
inter_shape.fadeout(3.5, 4.0)
canvas.add(inter_shape)

inter_ref_a = Circle(r=80, cx=cols[1] - 45, cy=row_y, fill_opacity=0,
                     stroke='#9B59B6', stroke_width=1, stroke_dasharray='5 3')
inter_ref_b = Circle(r=80, cx=cols[1] + 45, cy=row_y, fill_opacity=0,
                     stroke='#9B59B6', stroke_width=1, stroke_dasharray='5 3')
for obj in [inter_ref_a, inter_ref_b]:
    obj.fadein(1.3, 1.8)
    obj.fadeout(3.5, 4.0)
    canvas.add(obj)

inter_label = Text(text='Intersection', x=cols[1], y=label_y, font_size=30,
                   fill='#9B59B6', stroke_width=0, text_anchor='middle')
inter_label.fadein(1.5, 1.9)
inter_label.fadeout(3.5, 4.0)
canvas.add(inter_label)

# --- Difference ---
diff_shape = Difference(
    Circle(r=80, cx=cols[2] - 45, cy=row_y),
    Circle(r=80, cx=cols[2] + 45, cy=row_y),
    fill='#F5A623', fill_opacity=0.75, stroke='#FFFFFF', stroke_width=2,
)
diff_shape.fadein(1.8, 2.3)
diff_shape.fadeout(3.5, 4.0)
canvas.add(diff_shape)

diff_ref_a = Circle(r=80, cx=cols[2] - 45, cy=row_y, fill_opacity=0,
                    stroke='#F5A623', stroke_width=1, stroke_dasharray='5 3')
diff_ref_b = Circle(r=80, cx=cols[2] + 45, cy=row_y, fill_opacity=0,
                    stroke='#F5A623', stroke_width=1, stroke_dasharray='5 3')
for obj in [diff_ref_a, diff_ref_b]:
    obj.fadein(1.8, 2.3)
    obj.fadeout(3.5, 4.0)
    canvas.add(obj)

diff_label = Text(text='Difference', x=cols[2], y=label_y, font_size=30,
                  fill='#F5A623', stroke_width=0, text_anchor='middle')
diff_label.fadein(2.0, 2.4)
diff_label.fadeout(3.5, 4.0)
canvas.add(diff_label)

# --- Exclusion ---
excl_shape = Exclusion(
    Circle(r=80, cx=cols[3] - 45, cy=row_y),
    Circle(r=80, cx=cols[3] + 45, cy=row_y),
    fill='#E84D60', fill_opacity=0.75, stroke='#FFFFFF', stroke_width=2,
)
excl_shape.fadein(2.3, 2.8)
excl_shape.fadeout(3.5, 4.0)
canvas.add(excl_shape)

excl_ref_a = Circle(r=80, cx=cols[3] - 45, cy=row_y, fill_opacity=0,
                    stroke='#E84D60', stroke_width=1, stroke_dasharray='5 3')
excl_ref_b = Circle(r=80, cx=cols[3] + 45, cy=row_y, fill_opacity=0,
                    stroke='#E84D60', stroke_width=1, stroke_dasharray='5 3')
for obj in [excl_ref_a, excl_ref_b]:
    obj.fadein(2.3, 2.8)
    obj.fadeout(3.5, 4.0)
    canvas.add(obj)

excl_label = Text(text='Exclusion', x=cols[3], y=label_y, font_size=30,
                  fill='#E84D60', stroke_width=0, text_anchor='middle')
excl_label.fadein(2.5, 2.9)
excl_label.fadeout(3.5, 4.0)
canvas.add(excl_label)

# =============================================================================
# Phase 2 (4–8s): Cutout and ConvexHull
# =============================================================================

phase2_title = Text(
    text='Cutout & ConvexHull', x=960, y=70, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase2_title.fadein(4.0, 4.5)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# --- Cutout (spotlight effect, left half of screen) ---
cutout_sub_title = Text(text='Cutout (spotlight)', x=440, y=170, font_size=28,
                        fill='#AAAAAA', stroke_width=0, text_anchor='middle')
cutout_sub_title.fadein(4.2, 4.6)
cutout_sub_title.fadeout(7.5, 8.0)
canvas.add(cutout_sub_title)

# Background content behind the cutout
bg_star = Star(n=5, outer_radius=100, inner_radius=45, cx=350, cy=430,
               fill='#E84D60', stroke='#E84D60', stroke_width=2, creation=4.0)
bg_star.fadein(4.0, 4.5)
bg_star.fadeout(7.5, 8.0)
canvas.add(bg_star)

bg_hex = RegularPolygon(n=6, radius=70, cx=530, cy=500,
                        fill='#58C4DD', stroke='#58C4DD', stroke_width=2, creation=4.0)
bg_hex.fadein(4.0, 4.5)
bg_hex.fadeout(7.5, 8.0)
canvas.add(bg_hex)

bg_circle = Circle(r=50, cx=400, cy=600, fill='#83C167',
                   stroke='#83C167', stroke_width=2, creation=4.0)
bg_circle.fadein(4.0, 4.5)
bg_circle.fadeout(7.5, 8.0)
canvas.add(bg_circle)

# The cutout overlay — starts covering everything, then reveals shapes
cutout = Cutout(
    hole_x=300, hole_y=350, hole_w=200, hole_h=200,
    color='#111122', opacity=0.85, rx=15, ry=15,
    creation=4.0, z=50,
)
cutout.fadein(4.3, 4.8)
# Animate the hole to grow and sweep across the shapes
cutout.set_hole(x=230, y=320, w=350, h=330, start=5.0, end=6.0)
cutout.set_hole(x=180, y=280, w=500, h=420, start=6.0, end=7.0)
cutout.fadeout(7.5, 8.0)
canvas.add(cutout)

# --- ConvexHull (right half of screen) ---
hull_sub_title = Text(text='ConvexHull', x=1350, y=170, font_size=28,
                      fill='#AAAAAA', stroke_width=0, text_anchor='middle')
hull_sub_title.fadein(4.2, 4.6)
hull_sub_title.fadeout(7.5, 8.0)
canvas.add(hull_sub_title)

# Scattered dots
import random
random.seed(42)
dot_positions = []
dots = []
for i in range(14):
    dx = random.uniform(1050, 1650)
    dy = random.uniform(250, 700)
    dot_positions.append((dx, dy))
    colors = ['#E84D60', '#58C4DD', '#83C167', '#F5A623', '#9B59B6', '#4ECDC4']
    d = Dot(cx=dx, cy=dy, r=8, fill=colors[i % len(colors)],
            stroke_width=0, creation=4.0)
    d.fadein(4.3 + i * 0.08, 4.6 + i * 0.08)
    d.fadeout(7.5, 8.0)
    dots.append(d)
    canvas.add(d)

# ConvexHull polygon wrapping all dots
hull = ConvexHull(
    *dot_positions,
    fill='#58C4DD', fill_opacity=0.12, stroke='#58C4DD', stroke_width=2.5,
    creation=4.0,
)
hull.fadein(5.5, 6.0)
hull.fadeout(7.5, 8.0)
canvas.add(hull)

hull_label = Text(text='hull wraps all points', x=1350, y=760, font_size=22,
                  fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=4.0)
hull_label.fadein(6.0, 6.4)
hull_label.fadeout(7.5, 8.0)
canvas.add(hull_label)

# =============================================================================
# Phase 3 (8–12s): ZoomedInset + StreamLines
# =============================================================================

phase3_title = Text(
    text='ZoomedInset & StreamLines', x=960, y=70, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase3_title.fadein(8.0, 8.5)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

# --- ZoomedInset (left side) ---
zoom_sub_title = Text(text='ZoomedInset', x=430, y=170, font_size=28,
                      fill='#AAAAAA', stroke_width=0, text_anchor='middle')
zoom_sub_title.fadein(8.2, 8.6)
zoom_sub_title.fadeout(11.5, 12.0)
canvas.add(zoom_sub_title)

# Small detailed scene to magnify
tiny_sq = Square(side=30, x=230, y=595, fill='#4ECDC4',
                 stroke='#FFFFFF', stroke_width=1, creation=8.0)
tiny_sq.fadein(8.0, 8.4)
tiny_sq.fadeout(11.5, 12.0)
canvas.add(tiny_sq)

tiny_circle = Circle(r=12, cx=270, cy=610, fill='#E84D60',
                     stroke='#FFFFFF', stroke_width=1, creation=8.0)
tiny_circle.fadein(8.0, 8.4)
tiny_circle.fadeout(11.5, 12.0)
canvas.add(tiny_circle)

tiny_tri = EquilateralTriangle(side_length=25, cx=250, cy=570,
                               fill='#FFFF00', fill_opacity=0.6,
                               stroke='#FFFF00', stroke_width=1, creation=8.0)
tiny_tri.fadein(8.0, 8.4)
tiny_tri.fadeout(11.5, 12.0)
canvas.add(tiny_tri)

tiny_dot1 = Dot(cx=235, cy=555, r=5, fill='#9B59B6', stroke_width=0, creation=8.0)
tiny_dot2 = Dot(cx=280, cy=585, r=4, fill='#83C167', stroke_width=0, creation=8.0)
tiny_dot3 = Dot(cx=225, cy=625, r=6, fill='#F5A623', stroke_width=0, creation=8.0)
for d in [tiny_dot1, tiny_dot2, tiny_dot3]:
    d.fadein(8.0, 8.4)
    d.fadeout(11.5, 12.0)
    canvas.add(d)

# Connector line from source to display
connect_line = DashedLine(x1=310, y1=560, x2=380, y2=300,
                          stroke='#FFFF00', stroke_width=1, stroke_opacity=0.5,
                          creation=8.0)
connect_line.fadein(8.4, 8.8)
connect_line.fadeout(11.5, 12.0)
canvas.add(connect_line)

# ZoomedInset: magnify the tiny scene
zoomed_inset = ZoomedInset(
    canvas,
    source=(200, 545, 110, 100),
    display=(380, 230, 450, 400),
    creation=8.0, z=100,
    frame_color='#FFFF00', display_color='#FFFF00', frame_width=2,
)
zoomed_inset.fadein(8.4, 8.9)
zoomed_inset.fadeout(11.5, 12.0)
canvas.add(zoomed_inset)

zoom_label = Text(text='magnified detail', x=605, y=660, font_size=20,
                  fill='#FFFF00', stroke_width=0, text_anchor='middle', creation=8.0)
zoom_label.fadein(8.6, 9.0)
zoom_label.fadeout(11.5, 12.0)
canvas.add(zoom_label)

# --- StreamLines (right side) ---
stream_sub_title = Text(text='StreamLines', x=1350, y=170, font_size=28,
                        fill='#AAAAAA', stroke_width=0, text_anchor='middle')
stream_sub_title.fadein(8.2, 8.6)
stream_sub_title.fadeout(11.5, 12.0)
canvas.add(stream_sub_title)

import math

# Swirl vector field
def swirl_field(x, y):
    cx, cy = 1350, 500
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy) + 1e-9
    # Tangential + slight inward pull
    return (-dy / r * 60 - dx / r * 10,
             dx / r * 60 - dy / r * 10)

stream = StreamLines(
    swirl_field,
    x_range=(950, 1750, 120),
    y_range=(220, 780, 120),
    n_steps=50, step_size=6,
    stroke='#58C4DD', stroke_width=1.5, stroke_opacity=0.7,
    creation=8.0,
)
stream.stagger_fadein(start=8.5, end=10.0)
stream.fadeout(11.5, 12.0)
canvas.add(stream)

# Center dot of the swirl field
swirl_center = Dot(cx=1350, cy=500, r=8, fill='#FFFF00', stroke_width=0, creation=8.0)
swirl_center.fadein(9.0, 9.3)
swirl_center.fadeout(11.5, 12.0)
canvas.add(swirl_center)

stream_label = Text(text='swirl vector field', x=1350, y=790, font_size=20,
                    fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=8.0)
stream_label.fadein(9.5, 9.8)
stream_label.fadeout(11.5, 12.0)
canvas.add(stream_label)

# =============================================================================
# Render
# =============================================================================

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
