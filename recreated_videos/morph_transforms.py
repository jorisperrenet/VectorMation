"""Morph & Transforms Demo — morphing, geometric transforms, path animations, state management."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/morph_transforms')
canvas.set_background()
T = 20.0

# Colors
BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#FFFF00'
PURPLE = '#9A72AC'
ORANGE = '#FF862F'

# =============================================================================
# Phase 1 (0-5s): Object Transformations
# =============================================================================

title1 = Text(text='Object Transformations', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0.0, 0.8)
title1.fadeout(4.5, 5.0)
canvas.add(title1)

# --- MorphObject: Circle -> Rectangle ---
morph_circ = Circle(r=80, cx=400, cy=400,
                    fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
morph_circ.fadein(0.3, 0.7)
canvas.add(morph_circ)

morph_rect = Rectangle(200, 140, x=400 - 100, y=400 - 70,
                        fill=RED, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
canvas.add(morph_rect)

morph_obj = MorphObject(morph_circ, morph_rect, start=1.2, end=3.0)
canvas.add(morph_obj)
morph_rect.fadeout(4.5, 5.0)

morph_label = Text(text='MorphObject', x=400, y=560, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
morph_label.fadein(0.5, 1.0)
morph_label.fadeout(4.5, 5.0)
canvas.add(morph_label)

morph_sub = Text(text='Circle -> Rectangle', x=400, y=595, font_size=20,
                 fill='#777777', stroke_width=0, text_anchor='middle')
morph_sub.fadein(0.5, 1.0)
morph_sub.fadeout(4.5, 5.0)
canvas.add(morph_sub)

# --- fade_transform: Text -> Text ---
text_src = Text(text='Hello World', x=960, y=400, font_size=52,
                fill=GREEN, stroke_width=0, text_anchor='middle')
text_src.fadein(0.5, 1.0)
canvas.add(text_src)

text_dst = Text(text='Goodbye World', x=960, y=400, font_size=52,
                fill=YELLOW, stroke_width=0, text_anchor='middle')
canvas.add(text_dst)

VObject.fade_transform(text_src, text_dst, start=1.5, end=3.0)
text_dst.fadeout(4.5, 5.0)

ft_label = Text(text='fade_transform()', x=960, y=560, font_size=24,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ft_label.fadein(0.5, 1.0)
ft_label.fadeout(4.5, 5.0)
canvas.add(ft_label)

ft_sub = Text(text='Text -> Text', x=960, y=595, font_size=20,
              fill='#777777', stroke_width=0, text_anchor='middle')
ft_sub.fadein(0.5, 1.0)
ft_sub.fadeout(4.5, 5.0)
canvas.add(ft_sub)

# --- become: copy styling ---
become_src = Circle(r=70, cx=1500, cy=350,
                    fill=PURPLE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
become_src.fadein(0.5, 0.9)
canvas.add(become_src)

become_ref = Circle(r=70, cx=1500, cy=350,
                    fill=ORANGE, fill_opacity=0.85, stroke=YELLOW, stroke_width=3)

become_src.become(become_ref, time=2.5)

become_label = Text(text='become()', x=1500, y=560, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
become_label.fadein(0.5, 1.0)
become_label.fadeout(4.5, 5.0)
canvas.add(become_label)

become_sub = Text(text='Copy styling at t=2.5', x=1500, y=595, font_size=20,
                  fill='#777777', stroke_width=0, text_anchor='middle')
become_sub.fadein(0.5, 1.0)
become_sub.fadeout(4.5, 5.0)
canvas.add(become_sub)

become_src.fadeout(4.5, 5.0)

# =============================================================================
# Phase 2 (5-10s): Geometric Transforms
# =============================================================================

title2 = Text(text='Geometric Transforms', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(5.0, 5.8)
title2.fadeout(9.5, 10.0)
canvas.add(title2)

# --- reflect() on a triangle ---
refl_tri = EquilateralTriangle(side_length=140, cx=320, cy=380,
                                fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
refl_tri.fadein(5.2, 5.6)
refl_tri.reflect(axis='vertical', start=6.5)
refl_tri.fadeout(9.5, 10.0)
canvas.add(refl_tri)

# Dashed vertical midline as visual guide
refl_guide = Line(x1=320, y1=280, x2=320, y2=480,
                  stroke='#555555', stroke_width=1, stroke_dasharray='6,4')
refl_guide.fadein(5.3, 5.6)
refl_guide.fadeout(9.5, 10.0)
canvas.add(refl_guide)

refl_label = Text(text='reflect()', x=320, y=530, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
refl_label.fadein(5.4, 5.8)
refl_label.fadeout(9.5, 10.0)
canvas.add(refl_label)

# --- apply_matrix() with shear ---
matrix_rect = Rectangle(140, 100, x=700 - 70, y=380 - 50,
                         fill=RED, fill_opacity=0.75, stroke='#FFFFFF', stroke_width=3)
matrix_rect.fadein(5.2, 5.6)
matrix_rect.apply_matrix([[1, 0.5], [0, 1]], start=7.0)
matrix_rect.fadeout(9.5, 10.0)
canvas.add(matrix_rect)

matrix_label = Text(text='apply_matrix()', x=700, y=530, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
matrix_label.fadein(5.4, 5.8)
matrix_label.fadeout(9.5, 10.0)
canvas.add(matrix_label)

matrix_sub = Text(text='Shear [[1,0.5],[0,1]]', x=700, y=565, font_size=18,
                  fill='#777777', stroke_width=0, text_anchor='middle')
matrix_sub.fadein(5.4, 5.8)
matrix_sub.fadeout(9.5, 10.0)
canvas.add(matrix_sub)

# --- scale() ---
scale_star = Star(n=5, outer_radius=60, cx=1080, cy=380,
                  fill=GREEN, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
scale_star.grow_from_center(start=5.3, end=5.8)
scale_star.scale(1.8, start=6.5, end=7.5)
scale_star.scale(0.4, start=7.5, end=8.5)
scale_star.fadeout(9.5, 10.0)
canvas.add(scale_star)

scale_label = Text(text='scale()', x=1080, y=530, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
scale_label.fadein(5.4, 5.8)
scale_label.fadeout(9.5, 10.0)
canvas.add(scale_label)

# --- stretch() ---
stretch_ell = Ellipse(rx=70, ry=50, cx=1500, cy=380,
                      fill=YELLOW, fill_opacity=0.75, stroke='#FFFFFF', stroke_width=3)
stretch_ell.fadein(5.2, 5.6)
stretch_ell.stretch(x_factor=1.6, y_factor=0.6, start=6.5, end=7.5)
stretch_ell.stretch(x_factor=0.5, y_factor=1.8, start=7.8, end=8.8)
stretch_ell.fadeout(9.5, 10.0)
canvas.add(stretch_ell)

stretch_label = Text(text='stretch()', x=1500, y=530, font_size=24,
                     fill='#AAAAAA', stroke_width=0, text_anchor='middle')
stretch_label.fadein(5.4, 5.8)
stretch_label.fadeout(9.5, 10.0)
canvas.add(stretch_label)

# --- Bottom row: rotate_by and flip ---
rot_hex = RegularPolygon(6, radius=70, cx=500, cy=780,
                         fill=PURPLE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
rot_hex.fadein(5.5, 5.9)
rot_hex.rotate_by(start=6.5, end=9.0, degrees=540)
rot_hex.fadeout(9.5, 10.0)
canvas.add(rot_hex)

rot_label = Text(text='rotate_by(540)', x=500, y=900, font_size=24,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
rot_label.fadein(5.5, 5.9)
rot_label.fadeout(9.5, 10.0)
canvas.add(rot_label)

flip_sq = Square(side=120, x=1100, y=780,
                 fill=ORANGE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
flip_sq.fadein(5.5, 5.9)
flip_sq.flip(axis='horizontal', start=6.8, end=7.5)
flip_sq.flip(axis='vertical', start=8.0, end=8.7)
flip_sq.fadeout(9.5, 10.0)
canvas.add(flip_sq)

flip_label = Text(text='flip()', x=1100, y=900, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
flip_label.fadein(5.5, 5.9)
flip_label.fadeout(9.5, 10.0)
canvas.add(flip_label)

# =============================================================================
# Phase 3 (10-15s): Path Animations
# =============================================================================

title3 = Text(text='Path Animations', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(10.0, 10.8)
title3.fadeout(14.5, 15.0)
canvas.add(title3)

# --- along_path: dot follows a curved SVG path ---
ap_x0, ap_y0 = 250, 400
ap_path_d = (f'M{ap_x0},{ap_y0} '
             f'C{ap_x0},{ap_y0 - 180} {ap_x0 + 300},{ap_y0 - 180} {ap_x0 + 300},{ap_y0} '
             f'S{ap_x0 + 600},{ap_y0 + 180} {ap_x0 + 600},{ap_y0}')

ap_guide = Path(ap_path_d, stroke='#555555', stroke_width=1.5, fill_opacity=0,
                stroke_dasharray='8,4')
ap_guide.fadein(10.3, 10.7)
ap_guide.fadeout(14.5, 15.0)
canvas.add(ap_guide)

ap_dot = Dot(r=12, cx=ap_x0, cy=ap_y0, fill=RED)
ap_dot.fadein(10.3, 10.7)
ap_dot.along_path(start=11.0, end=13.5, path_d=ap_path_d)
ap_dot.fadeout(14.5, 15.0)
canvas.add(ap_dot)

ap_label = Text(text='along_path()', x=550, y=560, font_size=24,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ap_label.fadein(10.4, 10.8)
ap_label.fadeout(14.5, 15.0)
canvas.add(ap_label)

# --- trace_path: orbiting dot leaves a trail ---
trace_dot = Circle(r=14, cx=1200, cy=400, fill=GREEN, stroke_width=0)
trace_dot.fadein(10.3, 10.7)
trace_dot.orbit(cx=1400, cy=400, radius=130, start=11.0, end=14.0, degrees=720)
trace_dot.fadeout(14.5, 15.0)
canvas.add(trace_dot)

trace = trace_dot.trace_path(start=11.0, end=14.0, stroke=GREEN,
                              stroke_width=2.5, stroke_opacity=0.5)
trace.fadeout(14.5, 15.0)
canvas.add(trace)

trace_label = Text(text='trace_path()', x=1400, y=580, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
trace_label.fadein(10.4, 10.8)
trace_label.fadeout(14.5, 15.0)
canvas.add(trace_label)

# --- draw_along: star outline drawn progressively ---
da_star = Star(n=6, outer_radius=90, cx=500, cy=820,
               fill=PURPLE, fill_opacity=0.3, stroke=PURPLE, stroke_width=3)
da_star.draw_along(start=11.0, end=13.5)
da_star.fadeout(14.5, 15.0)
canvas.add(da_star)

da_label = Text(text='draw_along()', x=500, y=950, font_size=24,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
da_label.fadein(10.4, 10.8)
da_label.fadeout(14.5, 15.0)
canvas.add(da_label)

# --- Spiral draw_along ---
da_spiral = Spiral(cx=1100, cy=820, a=5, b=12, turns=3, num_points=150,
                   stroke=ORANGE, stroke_width=2.5, fill_opacity=0)
da_spiral.draw_along(start=11.0, end=13.5)
da_spiral.fadeout(14.5, 15.0)
canvas.add(da_spiral)

da_spiral_label = Text(text='draw_along() spiral', x=1100, y=950, font_size=24,
                       fill='#AAAAAA', stroke_width=0, text_anchor='middle')
da_spiral_label.fadein(10.4, 10.8)
da_spiral_label.fadeout(14.5, 15.0)
canvas.add(da_spiral_label)

# =============================================================================
# Phase 4 (15-20s): State & Advanced
# =============================================================================

title4 = Text(text='State & Advanced', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(15.0, 15.8)
title4.fadeout(19.5, 20.0)
canvas.add(title4)

# --- save_state / restore ---
state_circ = Circle(r=70, cx=300, cy=400,
                    fill=BLUE, fill_opacity=0.85, stroke='#FFFFFF', stroke_width=3)
state_circ.fadein(15.2, 15.6)
state_circ.save_state(time=15.6)

# Modify: scale down, dim, change color
state_circ.scale(0.4, start=16.2, end=16.8)
state_circ.dim(start=16.2, end=16.8, opacity=0.2)

# Restore
state_circ.restore(start=17.5, end=18.2)
state_circ.fadeout(19.5, 20.0)
canvas.add(state_circ)

state_label = Text(text='save_state() / restore()', x=300, y=530, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
state_label.fadein(15.3, 15.7)
state_label.fadeout(19.5, 20.0)
canvas.add(state_label)

mod_label = Text(text='Modified', x=300, y=560, font_size=18,
                 fill='#777777', stroke_width=0, text_anchor='middle')
mod_label.fadein(16.8, 17.1)
mod_label.fadeout(17.4, 17.6)
canvas.add(mod_label)

rest_label = Text(text='Restored!', x=300, y=560, font_size=18,
                  fill=GREEN, stroke_width=0, text_anchor='middle')
rest_label.fadein(18.2, 18.5)
rest_label.fadeout(19.5, 20.0)
canvas.add(rest_label)

# --- swap() between two objects ---
swap_a = EquilateralTriangle(side_length=110, cx=750, cy=380,
                              fill=RED, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
swap_b = RegularPolygon(5, radius=60, cx=1050, cy=380,
                        fill=YELLOW, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
swap_a.fadein(15.3, 15.7)
swap_b.fadein(15.3, 15.7)
VObject.swap(swap_a, swap_b, start=16.5, end=17.5)
swap_a.fadeout(19.5, 20.0)
swap_b.fadeout(19.5, 20.0)
canvas.add(swap_a)
canvas.add(swap_b)

swap_label_a = Text(text='A', x=750, y=330, font_size=20,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
swap_label_b = Text(text='B', x=1050, y=330, font_size=20,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
swap_label_a.fadein(15.4, 15.8)
swap_label_b.fadein(15.4, 15.8)
swap_label_a.fadeout(19.5, 20.0)
swap_label_b.fadeout(19.5, 20.0)
canvas.add(swap_label_a)
canvas.add(swap_label_b)

swap_label = Text(text='swap()', x=900, y=530, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
swap_label.fadein(15.4, 15.8)
swap_label.fadeout(19.5, 20.0)
canvas.add(swap_label)

# --- surround() creating a surrounding rectangle ---
surr_target = Square(side=110, x=1450, y=380,
                     fill=PURPLE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
surr_target.fadein(15.3, 15.7)
surr_target.fadeout(19.5, 20.0)
canvas.add(surr_target)

surr_rect = VObject.surround(surr_target, buff=20, start=16.5)
surr_rect.set_stroke(color=YELLOW, start=16.5)
surr_rect.fadeout(19.5, 20.0)
canvas.add(surr_rect)

surr_label = Text(text='surround()', x=1450, y=530, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
surr_label.fadein(15.4, 15.8)
surr_label.fadeout(19.5, 20.0)
canvas.add(surr_label)

# --- Bottom row: MorphObject Star -> Hexagon ---
morph2_star = Star(n=5, outer_radius=70, cx=400, cy=800,
                   fill=ORANGE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
morph2_star.fadein(15.5, 15.9)
canvas.add(morph2_star)

morph2_hex = RegularPolygon(6, radius=70, cx=400, cy=800,
                            fill=GREEN, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
canvas.add(morph2_hex)

morph2 = MorphObject(morph2_star, morph2_hex, start=16.5, end=18.5)
canvas.add(morph2)
morph2_hex.fadeout(19.5, 20.0)

morph2_label = Text(text='MorphObject', x=400, y=920, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
morph2_label.fadein(15.5, 15.9)
morph2_label.fadeout(19.5, 20.0)
canvas.add(morph2_label)

morph2_sub = Text(text='Star -> Hexagon', x=400, y=955, font_size=18,
                  fill='#777777', stroke_width=0, text_anchor='middle')
morph2_sub.fadein(15.5, 15.9)
morph2_sub.fadeout(19.5, 20.0)
canvas.add(morph2_sub)

# --- Bottom right: circumscribe + indicate ---
circ_obj = Circle(r=60, cx=1100, cy=800,
                  fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
circ_obj.fadein(15.5, 15.9)
circ_obj.circumscribe(start=16.5, end=17.5)
circ_obj.indicate(start=18.0, end=18.8)
circ_obj.fadeout(19.5, 20.0)
canvas.add(circ_obj)

circ_obj_label = Text(text='circumscribe + indicate', x=1100, y=920, font_size=22,
                      fill='#AAAAAA', stroke_width=0, text_anchor='middle')
circ_obj_label.fadein(15.5, 15.9)
circ_obj_label.fadeout(19.5, 20.0)
canvas.add(circ_obj_label)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
        hot_reload=args.hot_reload,
    )
