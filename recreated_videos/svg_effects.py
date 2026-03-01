"""SVG Effects Demo — Boolean Ops, Spotlight, AnimatedBoundary, ZoomedInset."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/svg_effects')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0–3s): Title + Boolean Shape Operations
# =============================================================================

title = Text(
    text='SVG Effects', x=960, y=80, font_size=56,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
title.fadein(0.0, 0.5)
title.fadeout(2.5, 3.0)
canvas.add(title)

# Two overlapping circles as reference (faded background)
circle_a = Circle(r=100, cx=500, cy=450, fill='#58C4DD', fill_opacity=0.3, stroke='#58C4DD', stroke_width=2)
circle_b = Circle(r=100, cx=600, cy=450, fill='#E84D60', fill_opacity=0.3, stroke='#E84D60', stroke_width=2)
circle_a.fadein(0.2, 0.6)
circle_b.fadein(0.2, 0.6)
circle_a.fadeout(2.5, 3.0)
circle_b.fadeout(2.5, 3.0)
canvas.add(circle_a)
canvas.add(circle_b)

# Union
union_shape = Union(
    Circle(r=100, cx=500, cy=450), Circle(r=100, cx=600, cy=450),
    fill='#4ECDC4', fill_opacity=0.7, stroke='#FFFFFF', stroke_width=2,
)
union_shape.fadein(0.8, 1.2)
union_shape.fadeout(2.5, 3.0)
canvas.add(union_shape)

union_label = Text(
    text='Union', x=550, y=600, font_size=30,
    fill='#4ECDC4', stroke_width=0, text_anchor='middle',
)
union_label.fadein(1.0, 1.3)
union_label.fadeout(2.5, 3.0)
canvas.add(union_label)

# Difference
diff_shape = Difference(
    Circle(r=100, cx=960, cy=450), Circle(r=100, cx=1060, cy=450),
    fill='#F5A623', fill_opacity=0.7, stroke='#FFFFFF', stroke_width=2,
)
diff_shape.fadein(1.2, 1.6)
diff_shape.fadeout(2.5, 3.0)
canvas.add(diff_shape)

diff_ref_a = Circle(r=100, cx=960, cy=450, fill_opacity=0, stroke='#F5A623', stroke_width=1, stroke_dasharray='6 4')
diff_ref_b = Circle(r=100, cx=1060, cy=450, fill_opacity=0, stroke='#F5A623', stroke_width=1, stroke_dasharray='6 4')
diff_ref_a.fadein(1.2, 1.6)
diff_ref_b.fadein(1.2, 1.6)
diff_ref_a.fadeout(2.5, 3.0)
diff_ref_b.fadeout(2.5, 3.0)
canvas.add(diff_ref_a)
canvas.add(diff_ref_b)

diff_label = Text(
    text='Difference', x=1010, y=600, font_size=30,
    fill='#F5A623', stroke_width=0, text_anchor='middle',
)
diff_label.fadein(1.4, 1.7)
diff_label.fadeout(2.5, 3.0)
canvas.add(diff_label)

# Intersection
inter_shape = Intersection(
    Circle(r=100, cx=1420, cy=450), Circle(r=100, cx=1520, cy=450),
    fill='#9B59B6', fill_opacity=0.7, stroke='#FFFFFF', stroke_width=2,
)
inter_shape.fadein(1.6, 2.0)
inter_shape.fadeout(2.5, 3.0)
canvas.add(inter_shape)

inter_ref_a = Circle(r=100, cx=1420, cy=450, fill_opacity=0, stroke='#9B59B6', stroke_width=1, stroke_dasharray='6 4')
inter_ref_b = Circle(r=100, cx=1520, cy=450, fill_opacity=0, stroke='#9B59B6', stroke_width=1, stroke_dasharray='6 4')
inter_ref_a.fadein(1.6, 2.0)
inter_ref_b.fadein(1.6, 2.0)
inter_ref_a.fadeout(2.5, 3.0)
inter_ref_b.fadeout(2.5, 3.0)
canvas.add(inter_ref_a)
canvas.add(inter_ref_b)

inter_label = Text(
    text='Intersection', x=1470, y=600, font_size=30,
    fill='#9B59B6', stroke_width=0, text_anchor='middle',
)
inter_label.fadein(1.8, 2.1)
inter_label.fadeout(2.5, 3.0)
canvas.add(inter_label)

# =============================================================================
# Phase 2 (3–6s): Spotlight
# =============================================================================

phase2_title = Text(
    text='Spotlight Effect', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase2_title.fadein(3.0, 3.5)
phase2_title.fadeout(5.5, 6.0)
canvas.add(phase2_title)

# Three shapes to spotlight
star_shape = Star(n=5, outer_radius=90, inner_radius=40, cx=400, cy=500,
                  fill='#E84D60', stroke='#E84D60', stroke_width=2, creation=3.0)
star_shape.fadein(3.0, 3.5)
star_shape.fadeout(5.5, 6.0)
canvas.add(star_shape)

hex_shape = RegularPolygon(n=6, radius=90, cx=960, cy=500,
                           fill='#58C4DD', stroke='#58C4DD', stroke_width=2, creation=3.0)
hex_shape.fadein(3.0, 3.5)
hex_shape.fadeout(5.5, 6.0)
canvas.add(hex_shape)

diamond_shape = RegularPolygon(n=4, radius=90, cx=1520, cy=500,
                               fill='#83C167', stroke='#83C167', stroke_width=2, creation=3.0)
diamond_shape.fadein(3.0, 3.5)
diamond_shape.fadeout(5.5, 6.0)
canvas.add(diamond_shape)

# Shape labels
star_label = Text(text='Star', x=400, y=630, font_size=24,
                  fill='#E84D60', stroke_width=0, text_anchor='middle', creation=3.0)
star_label.fadein(3.2, 3.5)
star_label.fadeout(5.5, 6.0)
canvas.add(star_label)

hex_label = Text(text='Hexagon', x=960, y=630, font_size=24,
                 fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=3.0)
hex_label.fadein(3.2, 3.5)
hex_label.fadeout(5.5, 6.0)
canvas.add(hex_label)

diamond_label = Text(text='Diamond', x=1520, y=630, font_size=24,
                     fill='#83C167', stroke_width=0, text_anchor='middle', creation=3.0)
diamond_label.fadein(3.2, 3.5)
diamond_label.fadeout(5.5, 6.0)
canvas.add(diamond_label)

# Spotlight that moves between shapes
spotlight = Spotlight(
    target=star_shape, radius=140, color='#000000', opacity=0.0,
    creation=3.0, z=50,
)
spotlight.set_overlay_opacity(0.75, start=3.3, end=3.8)
spotlight.set_target(hex_shape, start=4.0, end=4.5)
spotlight.set_target(diamond_shape, start=4.8, end=5.3)
spotlight.set_overlay_opacity(0.0, start=5.5, end=6.0)
spotlight.show.set_onward(6.0, False)
canvas.add(spotlight)

# =============================================================================
# Phase 3 (6–9s): AnimatedBoundary + DropShadow
# =============================================================================

phase3_title = Text(
    text='Boundary & Shadow', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase3_title.fadein(6.0, 6.5)
phase3_title.fadeout(8.5, 9.0)
canvas.add(phase3_title)

# Shapes with drop shadow (using the VObject.drop_shadow method)
shadow_rect = RoundedRectangle(
    width=250, height=160, corner_radius=15,
    x=960 - 125, y=500 - 80,
    fill='#4ECDC4', stroke='#FFFFFF', stroke_width=2, creation=6.0,
)
shadow_rect.drop_shadow(color='#000000', dx=6, dy=6, blur=6, start=6.0)
shadow_rect.fadein(6.0, 6.5)
shadow_rect.fadeout(8.5, 9.0)
canvas.add(shadow_rect)

shadow_circle = Circle(
    r=90, cx=400, cy=500,
    fill='#F5A623', stroke='#FFFFFF', stroke_width=2, creation=6.0,
)
shadow_circle.drop_shadow(color='#000000', dx=6, dy=6, blur=6, start=6.0)
shadow_circle.fadein(6.2, 6.7)
shadow_circle.fadeout(8.5, 9.0)
canvas.add(shadow_circle)

shadow_star = Star(
    n=6, outer_radius=90, inner_radius=50, cx=1520, cy=500,
    fill='#E84D60', stroke='#FFFFFF', stroke_width=2, creation=6.0,
)
shadow_star.drop_shadow(color='#000000', dx=6, dy=6, blur=6, start=6.0)
shadow_star.fadein(6.4, 6.9)
shadow_star.fadeout(8.5, 9.0)
canvas.add(shadow_star)

# Labels under shadowed shapes
shadow_label_l = Text(text='DropShadow', x=400, y=640, font_size=24,
                      fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
shadow_label_l.fadein(6.3, 6.7)
shadow_label_l.fadeout(8.5, 9.0)
canvas.add(shadow_label_l)

shadow_label_r = Text(text='DropShadow', x=1520, y=640, font_size=24,
                      fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
shadow_label_r.fadein(6.5, 6.9)
shadow_label_r.fadeout(8.5, 9.0)
canvas.add(shadow_label_r)

# Animated boundary around the central rectangle
boundary = AnimatedBoundary(
    shadow_rect,
    colors=['#58C4DD', '#FF6B6B', '#83C167', '#FFFF00'],
    cycle_rate=1.5, buff=12, stroke_width=3,
    creation=6.0,
)
boundary.show.set_onward(6.5, True)
boundary.show.set_onward(8.5, False)
canvas.add(boundary)

boundary_label = Text(
    text='AnimatedBoundary', x=960, y=680, font_size=24,
    fill='#888888', stroke_width=0, text_anchor='middle', creation=6.0,
)
boundary_label.fadein(6.8, 7.2)
boundary_label.fadeout(8.5, 9.0)
canvas.add(boundary_label)

# =============================================================================
# Phase 4 (9–12s): ZoomedInset
# =============================================================================

phase4_title = Text(
    text='Zoomed Inset', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
phase4_title.fadein(9.0, 9.5)
phase4_title.fadeout(11.5, 12.0)
canvas.add(phase4_title)

# Small scene to magnify — a cluster of small dots and a tiny triangle
small_dot1 = Dot(cx=300, cy=600, r=8, fill='#E84D60', stroke_width=0, creation=9.0)
small_dot2 = Dot(cx=330, cy=580, r=6, fill='#58C4DD', stroke_width=0, creation=9.0)
small_dot3 = Dot(cx=310, cy=620, r=10, fill='#83C167', stroke_width=0, creation=9.0)
small_dot4 = Dot(cx=340, cy=610, r=7, fill='#F5A623', stroke_width=0, creation=9.0)
small_dot5 = Dot(cx=280, cy=590, r=9, fill='#9B59B6', stroke_width=0, creation=9.0)

small_tri = EquilateralTriangle(side_length=40, cx=320, cy=560, fill='#FFFF00',
                                fill_opacity=0.5, stroke='#FFFF00', stroke_width=1, creation=9.0)

small_label = Text(text='Detail', x=310, y=660, font_size=16,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0)

small_objects = [small_dot1, small_dot2, small_dot3, small_dot4, small_dot5, small_tri, small_label]
for obj in small_objects:
    obj.fadein(9.0, 9.5)
    obj.fadeout(11.5, 12.0)
    canvas.add(obj)

# Source indicator line from source region to display region
src_line = DashedLine(x1=370, y1=540, x2=700, y2=250,
                      stroke='#FFFF00', stroke_width=1, stroke_opacity=0.5, creation=9.0)
src_line.fadein(9.3, 9.8)
src_line.fadeout(11.5, 12.0)
canvas.add(src_line)

# ZoomedInset: source region is the small cluster, display region is large on the right
zoomed = ZoomedInset(
    canvas,
    source=(250, 540, 130, 110),
    display=(700, 200, 600, 500),
    creation=9.0, z=100,
    frame_color='#FFFF00', display_color='#FFFF00', frame_width=3,
)
zoomed.fadein(9.3, 9.8)
zoomed.fadeout(11.5, 12.0)
canvas.add(zoomed)

zoom_label = Text(
    text='ZoomedInset — Magnified View', x=1000, y=760, font_size=28,
    fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0,
)
zoom_label.fadein(9.5, 10.0)
zoom_label.fadeout(11.5, 12.0)
canvas.add(zoom_label)

# =============================================================================
# Render
# =============================================================================

if not args.no_display:
    canvas.browser_display(0, T, fps=args.fps, port=args.port, hot_reload=args.hot_reload)

