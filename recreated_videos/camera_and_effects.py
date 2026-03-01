"""Camera & Effects Demo — camera_shift, camera_zoom, camera_follow, camera_reset,
wipe, slide_out, float_anim, animate_dash, ripple, highlight_border, spiral_out,
homotopy, warp, swirl."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/camera_and_effects')
canvas.set_background()
T = 28.0

# Colors
BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#FFFF00'
PURPLE = '#9A72AC'
ORANGE = '#FF862F'
CYAN   = '#00CED1'

# =============================================================================
# Phase 1 (0-7s): Camera Features
# =============================================================================

title1 = Text(text='Camera Features', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0.0, 0.8)
title1.fadeout(6.0, 7.0)
canvas.add(title1)

# Place some objects on the canvas to observe camera movement
cam_circ = Circle(r=60, cx=400, cy=400,
                  fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
cam_circ.fadein(0.3, 0.6)
cam_circ.fadeout(6.0, 7.0)
canvas.add(cam_circ)

cam_rect = Rectangle(140, 100, x=890, y=350,
                      fill=RED, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
cam_rect.fadein(0.3, 0.6)
cam_rect.fadeout(6.0, 7.0)
canvas.add(cam_rect)

cam_star = Star(n=5, outer_radius=60, cx=1500, cy=400,
                fill=GREEN, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
cam_star.fadein(0.3, 0.6)
cam_star.fadeout(6.0, 7.0)
canvas.add(cam_star)

# --- camera_shift: pan the view right ---
shift_label = Text(text='camera_shift()', x=960, y=700, font_size=28,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shift_label.fadein(0.8, 1.0)
shift_label.fadeout(2.0, 2.3)
canvas.add(shift_label)

canvas.camera_shift(dx=200, dy=0, start=1.0, end=2.0)

# --- camera_zoom: zoom in ---
zoom_label = Text(text='camera_zoom()', x=960, y=700, font_size=28,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
zoom_label.fadein(2.3, 2.5)
zoom_label.fadeout(3.8, 4.0)
canvas.add(zoom_label)

canvas.camera_zoom(factor=1.8, start=2.5, end=3.5)

# --- camera_reset: back to normal ---
reset_label = Text(text='camera_reset()', x=960, y=700, font_size=28,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
reset_label.fadein(3.8, 4.0)
reset_label.fadeout(5.0, 5.2)
canvas.add(reset_label)

canvas.camera_reset(start=4.0, end=5.0)

# --- camera_follow: follow a moving dot ---
follow_label = Text(text='camera_follow()', x=960, y=700, font_size=28,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
follow_label.fadein(5.0, 5.2)
follow_label.fadeout(6.5, 7.0)
canvas.add(follow_label)

follow_dot = Dot(r=18, cx=200, cy=540, fill=YELLOW)
follow_dot.fadein(5.0, 5.2)
follow_dot.shift(dx=1500, dy=0, start=5.2, end=6.5)
follow_dot.fadeout(6.5, 7.0)
canvas.add(follow_dot)

canvas.camera_zoom(factor=2.0, start=5.0, end=5.2)
canvas.camera_follow(follow_dot, start=5.2, end=6.5)
canvas.camera_reset(start=6.5, end=7.0)

# =============================================================================
# Phase 2 (7-14s): Clip & Transition Effects
# =============================================================================

title2 = Text(text='Clip & Transition Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(7.0, 7.8)
title2.fadeout(13.0, 14.0)
canvas.add(title2)

col_xs = [320, 700, 1080, 1460]
shape_y = 420

# --- wipe ---
wipe_rect = Rectangle(160, 110, x=col_xs[0] - 80, y=shape_y - 55,
                       fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
wipe_rect.wipe(direction='right', start=7.5, end=8.5)
wipe_rect.wipe(direction='left', start=10.0, end=11.0, reverse=True)
canvas.add(wipe_rect)

wipe_label = Text(text='wipe()', x=col_xs[0], y=shape_y + 95, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
wipe_label.fadein(7.6, 7.9)
wipe_label.fadeout(13.0, 14.0)
canvas.add(wipe_label)

# --- slide_out ---
slide_rect = Rectangle(160, 110, x=col_xs[1] - 80, y=shape_y - 55,
                        fill=RED, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
slide_rect.fadein(7.5, 8.0)
slide_rect.slide_out(direction='down', start=10.0, end=11.0)
canvas.add(slide_rect)

slide_label = Text(text='slide_out()', x=col_xs[1], y=shape_y + 95, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
slide_label.fadein(7.7, 8.0)
slide_label.fadeout(13.0, 14.0)
canvas.add(slide_label)

# --- highlight_border ---
hl_circ = Circle(r=65, cx=col_xs[2], cy=shape_y,
                 fill=GREEN, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
hl_circ.fadein(7.5, 8.0)
hl_circ.highlight_border(start=8.5, end=9.5, color=YELLOW, width=6)
hl_circ.highlight_border(start=10.5, end=11.5, color=CYAN, width=8)
hl_circ.fadeout(13.0, 14.0)
canvas.add(hl_circ)

hl_label = Text(text='highlight_border()', x=col_xs[2], y=shape_y + 95, font_size=24,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
hl_label.fadein(7.8, 8.1)
hl_label.fadeout(13.0, 14.0)
canvas.add(hl_label)

# --- spiral_out ---
spiral_star = Star(n=6, outer_radius=60, cx=col_xs[3], cy=shape_y,
                   fill=PURPLE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
spiral_star.fadein(7.5, 8.0)
spiral_star.spiral_out(start=10.0, end=11.5, n_turns=2)
canvas.add(spiral_star)

spiral_label = Text(text='spiral_out()', x=col_xs[3], y=shape_y + 95, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
spiral_label.fadein(7.9, 8.2)
spiral_label.fadeout(13.0, 14.0)
canvas.add(spiral_label)

# =============================================================================
# Phase 3 (14-21s): Continuous Effects
# =============================================================================

title3 = Text(text='Continuous Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(14.0, 14.8)
title3.fadeout(20.0, 21.0)
canvas.add(title3)

col_xs3 = [400, 960, 1520]
shape_y3 = 400

# --- float_anim ---
float_circ = Circle(r=60, cx=col_xs3[0], cy=shape_y3,
                    fill=ORANGE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
float_circ.fadein(14.3, 14.6)
float_circ.float_anim(start=14.6, end=19.0, amplitude=25, speed=0.8)
float_circ.fadeout(20.0, 21.0)
canvas.add(float_circ)

float_label = Text(text='float_anim()', x=col_xs3[0], y=shape_y3 + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
float_label.fadein(14.4, 14.7)
float_label.fadeout(20.0, 21.0)
canvas.add(float_label)

# --- animate_dash ---
dash_rect = Rectangle(160, 110, x=col_xs3[1] - 80, y=shape_y3 - 55,
                       fill_opacity=0, stroke=CYAN, stroke_width=4)
dash_rect.fadein(14.3, 14.6)
dash_rect.animate_dash(start=14.6, end=19.0, dash_length=15, gap=10)
dash_rect.fadeout(20.0, 21.0)
canvas.add(dash_rect)

dash_label = Text(text='animate_dash()', x=col_xs3[1], y=shape_y3 + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
dash_label.fadein(14.4, 14.7)
dash_label.fadeout(20.0, 21.0)
canvas.add(dash_label)

# --- ripple ---
ripple_dot = Dot(r=14, cx=col_xs3[2], cy=shape_y3, fill=RED)
ripple_dot.fadein(14.3, 14.6)
ripple_dot.fadeout(20.0, 21.0)
canvas.add(ripple_dot)

# ripple() returns a VCollection of ring objects -- add them to the canvas
rings1 = ripple_dot.ripple(start=15.0, end=16.5, count=3, max_radius=120, color=RED)
canvas.add(rings1)
rings2 = ripple_dot.ripple(start=17.0, end=18.5, count=3, max_radius=120, color=BLUE)
canvas.add(rings2)

ripple_label = Text(text='ripple()', x=col_xs3[2], y=shape_y3 + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ripple_label.fadein(14.4, 14.7)
ripple_label.fadeout(20.0, 21.0)
canvas.add(ripple_label)

# =============================================================================
# Phase 4 (21-28s): Deformation Effects
# =============================================================================

title4 = Text(text='Deformation Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(21.0, 21.8)
title4.fadeout(27.0, 28.0)
canvas.add(title4)

col_xs4 = [320, 700, 1080, 1460]
shape_y4 = 420

# --- warp ---
warp_rect = Rectangle(140, 100, x=col_xs4[0] - 70, y=shape_y4 - 50,
                       fill=BLUE, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
warp_rect.fadein(21.3, 21.6)
warp_rect.warp(start=22.0, end=24.0, amplitude=0.2, frequency=3)
warp_rect.fadeout(27.0, 28.0)
canvas.add(warp_rect)

warp_label = Text(text='warp()', x=col_xs4[0], y=shape_y4 + 95, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
warp_label.fadein(21.4, 21.7)
warp_label.fadeout(27.0, 28.0)
canvas.add(warp_label)

# --- swirl ---
swirl_circ = Circle(r=60, cx=col_xs4[1], cy=shape_y4,
                    fill=RED, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
swirl_circ.fadein(21.3, 21.6)
swirl_circ.swirl(start=22.0, end=24.0, turns=2, shrink=True)
swirl_circ.fadeout(27.0, 28.0)
canvas.add(swirl_circ)

swirl_label = Text(text='swirl()', x=col_xs4[1], y=shape_y4 + 95, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
swirl_label.fadein(21.4, 21.7)
swirl_label.fadeout(27.0, 28.0)
canvas.add(swirl_label)

# --- homotopy ---
# Homotopy deforms point positions: (x, y, t) -> (x', y')
# We'll use a wave-like deformation on a grid of dots
homo_sq = Square(side=120, x=col_xs4[2], y=shape_y4,
                 fill=GREEN, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
homo_sq.fadein(21.3, 21.6)

def wave_homotopy(x, y, t):
    """Wave deformation that bends points horizontally based on y."""
    return (x + 40 * math.sin(math.pi * t) * math.sin((y - shape_y4) / 50), y)

homo_sq.homotopy(wave_homotopy, start=22.0, end=24.5)
homo_sq.fadeout(27.0, 28.0)
canvas.add(homo_sq)

homo_label = Text(text='homotopy()', x=col_xs4[2], y=shape_y4 + 95, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
homo_label.fadein(21.4, 21.7)
homo_label.fadeout(27.0, 28.0)
canvas.add(homo_label)

# --- Combined: warp + swirl on a second row ---
combo_star = Star(n=5, outer_radius=60, cx=col_xs4[3], cy=shape_y4,
                  fill=YELLOW, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
combo_star.fadein(21.3, 21.6)
combo_star.warp(start=22.0, end=23.5, amplitude=0.25, frequency=4)
combo_star.swirl(start=24.0, end=26.0, turns=1.5, shrink=True)
combo_star.fadeout(27.0, 28.0)
canvas.add(combo_star)

combo_label = Text(text='warp + swirl', x=col_xs4[3], y=shape_y4 + 95, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
combo_label.fadein(21.4, 21.7)
combo_label.fadeout(27.0, 28.0)
canvas.add(combo_label)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
