"""Shapes & Transforms Demo — Basic shapes, animations, fractals, and morphing."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/shapes_transforms')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0-3s): Basic Shapes — grid of 8 shapes with labels
# =============================================================================

# Layout: 2 rows x 4 columns
# Row 1 y=280, Row 2 y=620
# Columns at x = 270, 570, 870, 1170 (but shifted slightly for 8 items)
# Actually use: 4 columns spread across 1920
col_xs = [300, 660, 1020, 1380]
row_ys = [300, 660]

shape_info = []  # (shape, label_text)

# Row 1, Col 1: Circle
circ = Circle(r=80, cx=col_xs[0], cy=row_ys[0],
              fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
circ_label = Text(text='Circle', x=col_xs[0], y=row_ys[0] + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((circ, circ_label))

# Row 1, Col 2: Rectangle
rect = Rectangle(200, 120, x=col_xs[1] - 100, y=row_ys[0] - 60,
                 fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
rect_label = Text(text='Rectangle', x=col_xs[1], y=row_ys[0] + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((rect, rect_label))

# Row 1, Col 3: Square
sq = Square(side=140, x=col_xs[2], y=row_ys[0],
            fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
sq_label = Text(text='Square', x=col_xs[2], y=row_ys[0] + 110, font_size=24,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((sq, sq_label))

# Row 1, Col 4: RegularPolygon (hexagon)
hex_poly = RegularPolygon(6, radius=80, cx=col_xs[3], cy=row_ys[0],
                          fill='#FFFF00', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
hex_label = Text(text='Hexagon', x=col_xs[3], y=row_ys[0] + 110, font_size=24,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((hex_poly, hex_label))

# Row 2, Col 1: EquilateralTriangle
tri = EquilateralTriangle(side_length=160, cx=col_xs[0], cy=row_ys[1],
                          fill='#9A72AC', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
tri_label = Text(text='Triangle', x=col_xs[0], y=row_ys[1] + 110, font_size=24,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((tri, tri_label))

# Row 2, Col 2: Star
star = Star(n=5, outer_radius=80, cx=col_xs[1], cy=row_ys[1],
            fill='#FF862F', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
star_label = Text(text='Star', x=col_xs[1], y=row_ys[1] + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((star, star_label))

# Row 2, Col 3: Ellipse
ell = Ellipse(rx=100, ry=55, cx=col_xs[2], cy=row_ys[1],
              fill='#FF6B9D', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
ell_label = Text(text='Ellipse', x=col_xs[2], y=row_ys[1] + 110, font_size=24,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((ell, ell_label))

# Row 2, Col 4: Polygon (pentagon)
pent = RegularPolygon(5, radius=80, cx=col_xs[3], cy=row_ys[1],
                      fill='#E0E0E0', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
pent_label = Text(text='Pentagon', x=col_xs[3], y=row_ys[1] + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shape_info.append((pent, pent_label))

# Phase 1 title
title1 = Text(text='Basic Shapes', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0.0, 0.8)
title1.fadeout(2.5, 3.0)
canvas.add(title1)

# Stagger fadein for all shapes and labels
for i, (shape, label) in enumerate(shape_info):
    delay = i * 0.15
    shape.grow_from_center(start=0.3 + delay, end=0.8 + delay)
    shape.fadeout(2.5, 3.0)
    label.fadein(start=0.5 + delay, end=0.9 + delay)
    label.fadeout(2.5, 3.0)
    canvas.add(shape)
    canvas.add(label)

# =============================================================================
# Phase 2 (3-6s): Shape Animations — grow, rotate, scale, flip
# =============================================================================

title2 = Text(text='Shape Animations', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(3.0, 3.8)
title2.fadeout(5.5, 6.0)
canvas.add(title2)

# Grow from center demo
grow_circ = Circle(r=90, cx=300, cy=350,
                   fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
grow_circ.grow_from_center(start=3.2, end=4.0)
grow_circ.fadeout(5.5, 6.0)
grow_label = Text(text='grow_from_center', x=300, y=480, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
grow_label.fadein(3.5, 4.0)
grow_label.fadeout(5.5, 6.0)
canvas.add(grow_circ)
canvas.add(grow_label)

# Rotate by demo
rot_sq = Square(side=140, x=720, y=350,
                fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
rot_sq.fadein(3.2, 3.5)
rot_sq.rotate_by(start=3.5, end=5.0, degrees=360)
rot_sq.fadeout(5.5, 6.0)
rot_label = Text(text='rotate_by(360)', x=720, y=480, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
rot_label.fadein(3.5, 4.0)
rot_label.fadeout(5.5, 6.0)
canvas.add(rot_sq)
canvas.add(rot_label)

# Scale demo
scale_star = Star(n=5, outer_radius=60, cx=1140, cy=350,
                  fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
scale_star.grow_from_center(start=3.2, end=3.8)
scale_star.scale(1.8, start=3.8, end=4.5)
scale_star.scale(0.6, start=4.5, end=5.2)
scale_star.fadeout(5.5, 6.0)
scale_label = Text(text='scale()', x=1140, y=480, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
scale_label.fadein(3.5, 4.0)
scale_label.fadeout(5.5, 6.0)
canvas.add(scale_star)
canvas.add(scale_label)

# Flip demo
flip_rect = Rectangle(160, 100, x=1560 - 80, y=350 - 50,
                       fill='#FFFF00', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
flip_rect.fadein(3.2, 3.5)
flip_rect.flip(axis='horizontal', start=3.8, end=4.3)
flip_rect.flip(axis='vertical', start=4.5, end=5.0)
flip_rect.fadeout(5.5, 6.0)
flip_label = Text(text='flip()', x=1560, y=480, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
flip_label.fadein(3.5, 4.0)
flip_label.fadeout(5.5, 6.0)
canvas.add(flip_rect)
canvas.add(flip_label)

# Additional row: wiggle, bounce, pulsate, rubber_band
wiggle_tri = EquilateralTriangle(side_length=120, cx=300, cy=720,
                                 fill='#9A72AC', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
wiggle_tri.fadein(3.3, 3.6)
wiggle_tri.wiggle(start=3.8, end=5.3)
wiggle_tri.fadeout(5.5, 6.0)
wiggle_label = Text(text='wiggle()', x=300, y=820, font_size=22,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
wiggle_label.fadein(3.5, 4.0)
wiggle_label.fadeout(5.5, 6.0)
canvas.add(wiggle_tri)
canvas.add(wiggle_label)

bounce_hex = RegularPolygon(6, radius=60, cx=720, cy=720,
                            fill='#FF862F', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
bounce_hex.fadein(3.3, 3.6)
bounce_hex.bounce(start=3.8, end=5.3)
bounce_hex.fadeout(5.5, 6.0)
bounce_label = Text(text='bounce()', x=720, y=820, font_size=22,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
bounce_label.fadein(3.5, 4.0)
bounce_label.fadeout(5.5, 6.0)
canvas.add(bounce_hex)
canvas.add(bounce_label)

pulse_ell = Ellipse(rx=80, ry=45, cx=1140, cy=720,
                    fill='#FF6B9D', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
pulse_ell.fadein(3.3, 3.6)
pulse_ell.pulsate(start=3.8, end=5.3)
pulse_ell.fadeout(5.5, 6.0)
pulse_label = Text(text='pulsate()', x=1140, y=820, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
pulse_label.fadein(3.5, 4.0)
pulse_label.fadeout(5.5, 6.0)
canvas.add(pulse_ell)
canvas.add(pulse_label)

rubber_dot = Circle(r=50, cx=1560, cy=720,
                    fill='#E0E0E0', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
rubber_dot.fadein(3.3, 3.6)
rubber_dot.rubber_band(start=3.8, end=5.3)
rubber_dot.fadeout(5.5, 6.0)
rubber_label = Text(text='rubber_band()', x=1560, y=820, font_size=22,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
rubber_label.fadein(3.5, 4.0)
rubber_label.fadeout(5.5, 6.0)
canvas.add(rubber_dot)
canvas.add(rubber_label)

# =============================================================================
# Phase 3 (6-9s): Fractal Shapes — Koch Snowflake and Sierpinski Triangle
# =============================================================================

title3 = Text(text='Fractal Shapes', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(6.0, 6.8)
title3.fadeout(8.5, 9.0)
canvas.add(title3)

# Koch Snowflake on the left
koch = KochSnowflake(cx=480, cy=480, size=350, depth=3,
                     fill='#58C4DD', fill_opacity=0.6, stroke='#58C4DD', stroke_width=2)
koch.grow_from_center(start=6.3, end=7.2)
koch.rotate_by(start=7.2, end=8.5, degrees=180)
koch.fadeout(8.5, 9.0)
canvas.add(koch)

koch_label = Text(text='Koch Snowflake (depth=3)', x=480, y=780, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
koch_label.fadein(6.5, 7.0)
koch_label.fadeout(8.5, 9.0)
canvas.add(koch_label)

# Sierpinski Triangle on the right
sierp = SierpinskiTriangle(cx=1440, cy=480, size=400, depth=4,
                           fill='#9A72AC', fill_opacity=0.8, stroke='#9A72AC', stroke_width=1)
sierp.stagger_fadein(start=6.5, end=7.8)
sierp.stagger_fadeout(start=8.3, end=9.0)
canvas.add(sierp)

sierp_label = Text(text='Sierpinski Triangle (depth=4)', x=1440, y=780, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
sierp_label.fadein(6.5, 7.0)
sierp_label.fadeout(8.5, 9.0)
canvas.add(sierp_label)

# Spiral in the center
spiral = Spiral(cx=960, cy=480, a=5, b=15, turns=4, num_points=200,
                stroke='#83C167', stroke_width=3, fill_opacity=0)
spiral.draw_along(start=6.5, end=8.0)
spiral.fadeout(8.5, 9.0)
canvas.add(spiral)

spiral_label = Text(text='Spiral', x=960, y=780, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
spiral_label.fadein(6.5, 7.0)
spiral_label.fadeout(8.5, 9.0)
canvas.add(spiral_label)

# =============================================================================
# Phase 4 (9-12s): Transform Effects — fade_transform, path_arc, color morphing
# =============================================================================

title4 = Text(text='Transform Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(9.0, 9.8)
title4.fadeout(11.5, 12.0)
canvas.add(title4)

# Left side: fade_transform from circle to star
morph_src = Circle(r=80, cx=350, cy=450,
                   fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
morph_src.fadein(9.2, 9.5)
canvas.add(morph_src)

morph_dst = Star(n=6, outer_radius=90, cx=350, cy=450,
                 fill='#FFFF00', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
canvas.add(morph_dst)
VObject.fade_transform(morph_src, morph_dst, start=9.8, end=10.8)
morph_dst.fadeout(11.5, 12.0)

morph_label = Text(text='fade_transform()', x=350, y=600, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
morph_label.fadein(9.5, 10.0)
morph_label.fadeout(11.5, 12.0)
canvas.add(morph_label)

# Center: path_arc movement
arc_circ = Circle(r=50, cx=750, cy=350,
                  fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
arc_circ.fadein(9.2, 9.5)
arc_circ.path_arc(1170, 350, start=9.8, end=11.0, angle=3.14159)
arc_circ.fadeout(11.5, 12.0)
canvas.add(arc_circ)

arc_label = Text(text='path_arc()', x=960, y=500, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
arc_label.fadein(9.5, 10.0)
arc_label.fadeout(11.5, 12.0)
canvas.add(arc_label)

# Right side: color_cycle
color_sq = Square(side=140, x=1560, y=450,
                  fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
color_sq.fadein(9.2, 9.5)
color_sq.color_cycle(colors=['#83C167', '#FC6255', '#58C4DD', '#FFFF00', '#9A72AC'],
                     start=9.8, end=11.5)
color_sq.fadeout(11.5, 12.0)
canvas.add(color_sq)

color_label = Text(text='color_cycle()', x=1560, y=600, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
color_label.fadein(9.5, 10.0)
color_label.fadeout(11.5, 12.0)
canvas.add(color_label)

# Bottom row: swap two shapes, indicate, and circumscribe
swap_a = EquilateralTriangle(side_length=100, cx=400, cy=800,
                             fill='#FF862F', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
swap_b = RegularPolygon(5, radius=55, cx=700, cy=800,
                        fill='#FF6B9D', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
swap_a.fadein(9.3, 9.6)
swap_b.fadein(9.3, 9.6)
VObject.swap(swap_a, swap_b, start=10.0, end=11.0)
swap_a.fadeout(11.5, 12.0)
swap_b.fadeout(11.5, 12.0)
canvas.add(swap_a)
canvas.add(swap_b)

swap_label = Text(text='swap()', x=550, y=900, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
swap_label.fadein(9.5, 10.0)
swap_label.fadeout(11.5, 12.0)
canvas.add(swap_label)

# Indicate effect
ind_circ = Circle(r=50, cx=1000, cy=800,
                  fill='#E0E0E0', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
ind_circ.fadein(9.3, 9.6)
ind_circ.indicate(start=10.0, end=10.8)
ind_circ.fadeout(11.5, 12.0)
canvas.add(ind_circ)

ind_label = Text(text='indicate()', x=1000, y=900, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ind_label.fadein(9.5, 10.0)
ind_label.fadeout(11.5, 12.0)
canvas.add(ind_label)

# Circumscribe effect
circ_rect = Rectangle(120, 80, x=1300 - 60, y=800 - 40,
                      fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
circ_rect.fadein(9.3, 9.6)
circ_rect.circumscribe(start=10.0, end=10.8)
circ_rect.fadeout(11.5, 12.0)
canvas.add(circ_rect)

circum_label = Text(text='circumscribe()', x=1300, y=900, font_size=22,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
circum_label.fadein(9.5, 10.0)
circum_label.fadeout(11.5, 12.0)
canvas.add(circum_label)

# Spin effect
spin_star = Star(n=4, outer_radius=45, cx=1560, cy=800,
                 fill='#9A72AC', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
spin_star.fadein(9.3, 9.6)
spin_star.spin(start=9.8, end=11.5, degrees=720)
spin_star.fadeout(11.5, 12.0)
canvas.add(spin_star)

spin_label = Text(text='spin()', x=1560, y=900, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
spin_label.fadein(9.5, 10.0)
spin_label.fadeout(11.5, 12.0)
canvas.add(spin_label)

# =============================================================================
# Display
# =============================================================================
canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
