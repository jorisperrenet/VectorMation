"""Animation Effects Showcase — wiggle, shake, spring, orbit, bounce, rubber_band, jiggle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animation_effects')
canvas.set_background()
T = 20.0

# =============================================================================
# Phase 1 (0-5s): Movement Effects
# =============================================================================

title1 = Text(text='Movement Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0.0, 0.8)
title1.fadeout(4.0, 5.0)
canvas.add(title1)

# Layout: 4 columns centered vertically
col_xs = [300, 660, 1020, 1380]
shape_y = 420

# --- wiggle ---
wiggle_circ = Circle(r=70, cx=col_xs[0], cy=shape_y,
                     fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
wiggle_circ.grow_from_center(start=0.2, end=0.5)
wiggle_circ.wiggle(start=0.5, end=2.5)
wiggle_circ.fadeout(4.0, 5.0)
canvas.add(wiggle_circ)

wiggle_label = Text(text='wiggle()', x=col_xs[0], y=shape_y + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
wiggle_label.fadein(0.3, 0.6)
wiggle_label.fadeout(4.0, 5.0)
canvas.add(wiggle_label)

# --- shake ---
shake_rect = Rectangle(140, 100, x=col_xs[1] - 70, y=shape_y - 50,
                       fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
shake_rect.grow_from_center(start=0.3, end=0.6)
shake_rect.shake(start=0.5, end=2.5)
shake_rect.fadeout(4.0, 5.0)
canvas.add(shake_rect)

shake_label = Text(text='shake()', x=col_xs[1], y=shape_y + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
shake_label.fadein(0.4, 0.7)
shake_label.fadeout(4.0, 5.0)
canvas.add(shake_label)

# --- bounce ---
bounce_star = Star(n=5, outer_radius=70, cx=col_xs[2], cy=shape_y,
                   fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
bounce_star.grow_from_center(start=0.4, end=0.7)
bounce_star.bounce(start=0.5, end=2.5, height=60, n_bounces=4)
bounce_star.fadeout(4.0, 5.0)
canvas.add(bounce_star)

bounce_label = Text(text='bounce()', x=col_xs[2], y=shape_y + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
bounce_label.fadein(0.5, 0.8)
bounce_label.fadeout(4.0, 5.0)
canvas.add(bounce_label)

# --- wave ---
wave_text = Text(text='Hello', x=col_xs[3], y=shape_y + 10, font_size=64,
                 fill='#FFFF00', stroke_width=0, text_anchor='middle')
wave_text.fadein(0.3, 0.6)
wave_text.wave(start=0.5, end=2.5, amplitude=15)
wave_text.fadeout(4.0, 5.0)
canvas.add(wave_text)

wave_label = Text(text='wave()', x=col_xs[3], y=shape_y + 110, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
wave_label.fadein(0.6, 0.9)
wave_label.fadeout(4.0, 5.0)
canvas.add(wave_label)

# =============================================================================
# Phase 2 (5-10s): Physics Effects
# =============================================================================

title2 = Text(text='Physics Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(5.0, 5.8)
title2.fadeout(9.0, 10.0)
canvas.add(title2)

# --- spring ---
spring_circ = Circle(r=70, cx=col_xs[0], cy=shape_y,
                     fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
spring_circ.grow_from_center(start=5.2, end=5.5)
spring_circ.spring(start=5.5, end=8.0, amplitude=40, frequency=3, axis='y')
spring_circ.fadeout(9.0, 10.0)
canvas.add(spring_circ)

spring_label = Text(text='spring()', x=col_xs[0], y=shape_y + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
spring_label.fadein(5.3, 5.6)
spring_label.fadeout(9.0, 10.0)
canvas.add(spring_label)

# --- rubber_band ---
rubber_rect = Rectangle(140, 100, x=col_xs[1] - 70, y=shape_y - 50,
                        fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
rubber_rect.grow_from_center(start=5.3, end=5.6)
rubber_rect.rubber_band(start=5.5, end=7.5)
rubber_rect.fadeout(9.0, 10.0)
canvas.add(rubber_rect)

rubber_label = Text(text='rubber_band()', x=col_xs[1], y=shape_y + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
rubber_label.fadein(5.4, 5.7)
rubber_label.fadeout(9.0, 10.0)
canvas.add(rubber_label)

# --- jiggle ---
jiggle_star = Star(n=5, outer_radius=70, cx=col_xs[2], cy=shape_y,
                   fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
jiggle_star.grow_from_center(start=5.4, end=5.7)
jiggle_star.jiggle(start=5.5, end=8.0, amplitude=8)
jiggle_star.fadeout(9.0, 10.0)
canvas.add(jiggle_star)

jiggle_label = Text(text='jiggle()', x=col_xs[2], y=shape_y + 110, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle')
jiggle_label.fadein(5.5, 5.8)
jiggle_label.fadeout(9.0, 10.0)
canvas.add(jiggle_label)

# --- orbit ---
orbit_center_x, orbit_center_y = col_xs[3], shape_y
orbit_center_dot = Dot(r=6, cx=orbit_center_x, cy=orbit_center_y,
                       fill='#AAAAAA')
orbit_center_dot.fadein(5.3, 5.6)
orbit_center_dot.fadeout(9.0, 10.0)
canvas.add(orbit_center_dot)

orbit_dot = Dot(r=18, cx=orbit_center_x + 80, cy=orbit_center_y,
                fill='#FFFF00')
orbit_dot.fadein(5.3, 5.6)
orbit_dot.orbit(orbit_center_x, orbit_center_y, radius=80, start=5.5, end=9.5)
orbit_dot.fadeout(9.5, 10.0)
canvas.add(orbit_dot)

orbit_label = Text(text='orbit()', x=col_xs[3], y=shape_y + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
orbit_label.fadein(5.6, 5.9)
orbit_label.fadeout(9.0, 10.0)
canvas.add(orbit_label)

# =============================================================================
# Phase 3 (10-15s): Scale Effects
# =============================================================================

title3 = Text(text='Scale Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(10.0, 10.8)
title3.fadeout(14.0, 15.0)
canvas.add(title3)

# --- pulsate ---
pulse_circ = Circle(r=70, cx=400, cy=shape_y,
                    fill='#FC6255', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
pulse_circ.grow_from_center(start=10.2, end=10.5)
pulse_circ.pulsate(start=10.5, end=13.0)
pulse_circ.fadeout(14.0, 15.0)
canvas.add(pulse_circ)

pulse_label = Text(text='pulsate()', x=400, y=shape_y + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
pulse_label.fadein(10.3, 10.6)
pulse_label.fadeout(14.0, 15.0)
canvas.add(pulse_label)

# --- undulate ---
undul_rect = Rectangle(140, 100, x=960 - 70, y=shape_y - 50,
                       fill='#58C4DD', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
undul_rect.grow_from_center(start=10.3, end=10.6)
undul_rect.undulate(start=10.5, end=13.0)
undul_rect.fadeout(14.0, 15.0)
canvas.add(undul_rect)

undul_label = Text(text='undulate()', x=960, y=shape_y + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
undul_label.fadein(10.4, 10.7)
undul_label.fadeout(14.0, 15.0)
canvas.add(undul_label)

# --- grow_from_center / shrink_to_center ---
scale_star = Star(n=5, outer_radius=70, cx=1520, cy=shape_y,
                  fill='#83C167', fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)
scale_star.grow_from_center(start=10.5, end=12.0)
scale_star.shrink_to_center(start=13.0, end=14.5)
canvas.add(scale_star)

scale_label = Text(text='grow / shrink', x=1520, y=shape_y + 110, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
scale_label.fadein(10.6, 10.9)
scale_label.fadeout(14.0, 15.0)
canvas.add(scale_label)

# =============================================================================
# Phase 4 (15-20s): Entry/Exit Effects
# =============================================================================

title4 = Text(text='Entry Effects', x=960, y=80, font_size=52,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(15.0, 15.8)
title4.fadeout(19.0, 20.0)
canvas.add(title4)

entry_xs = [240, 540, 840, 1140, 1440]
entry_y = 420
entry_effects = ['spiral_in', 'elastic_in', 'pop_in', 'zoom_in', 'slide_in']
entry_colors = ['#FC6255', '#58C4DD', '#83C167', '#FFFF00', '#9A72AC']

for i, (ex, name, color) in enumerate(zip(entry_xs, entry_effects, entry_colors)):
    circ = Circle(r=60, cx=ex, cy=entry_y,
                  fill=color, fill_opacity=0.8, stroke='#FFFFFF', stroke_width=3)

    delay = i * 0.4
    t_start = 15.5 + delay
    t_end = t_start + 1.0

    if name == 'spiral_in':
        circ.spiral_in(start=t_start, end=t_end)
    elif name == 'elastic_in':
        circ.elastic_in(start=t_start, end=t_end)
    elif name == 'pop_in':
        circ.pop_in(start=t_start, end=t_end)
    elif name == 'zoom_in':
        circ.zoom_in(start=t_start, end=t_end)
    elif name == 'slide_in':
        circ.slide_in(direction='down', start=t_start, end=t_end)

    circ.fadeout(19.0, 20.0)
    canvas.add(circ)

    label = Text(text=name + '()', x=ex, y=entry_y + 100, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
    label.fadein(t_start + 0.3, t_start + 0.6)
    label.fadeout(19.0, 20.0)
    canvas.add(label)

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
