"""Color & Gradient Features Demo — LinearGradient, RadialGradient,
color_gradient, set_color_by_gradient, set_opacity_by_gradient."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
show = VectorMathAnim(verbose=args.verbose, save_dir='svgs/color_gradients')
show.set_background()

# =============================================================================
# Phase 1 (0-3s): color_gradient — interpolate through a palette
# =============================================================================
title1 = Text(
    text='color_gradient()', x=960, y=80, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
title1.write(0.0, 0.8)
title1.fadeout(2.5, 3.0)
show.add(title1)

# 12 circles across the screen, colors sampled from a rainbow palette
palette = color_gradient(
    ['#FC6255', '#FF862F', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC'], n=12
)
spacing = 130
start_x = 960 - (11 * spacing) / 2
for i, col in enumerate(palette):
    c = Circle(r=45, cx=start_x + i * spacing, cy=250, fill=col,
               fill_opacity=1, stroke=lighten(col, 0.25), stroke_width=3)
    c.fadein(0.3 + i * 0.08, 0.7 + i * 0.08)
    c.fadeout(2.5, 3.0)
    show.add(c)

# Two-color gradient row below
two_color_label = Text(
    text='color_gradient(RED, BLUE, n=8)', x=960, y=370, font_size=26,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
two_color_label.fadein(0.8, 1.3)
two_color_label.fadeout(2.5, 3.0)
show.add(two_color_label)

two_colors = color_gradient('#FC6255', '#58C4DD', n=8)
for i, col in enumerate(two_colors):
    r = Rectangle(120, 80, x=960 - 4 * 140 + i * 140 + 10, y=420,
                  fill=col, fill_opacity=1, stroke_width=0, rx=10, ry=10)
    r.fadein(1.0 + i * 0.08, 1.4 + i * 0.08)
    r.fadeout(2.5, 3.0)
    show.add(r)

# Multi-stop gradient strip
multi_label = Text(
    text='color_gradient([RED, GOLD, GREEN, BLUE, PURPLE], n=20)', x=960, y=560,
    font_size=22, fill='#888888', stroke_width=0, text_anchor='middle',
)
multi_label.fadein(1.3, 1.8)
multi_label.fadeout(2.5, 3.0)
show.add(multi_label)

multi_colors = color_gradient(
    ['#FC6255', '#F0AC5F', '#83C167', '#58C4DD', '#9A72AC'], n=20
)
bar_w = 60
bar_start = 960 - (20 * bar_w) / 2
for i, col in enumerate(multi_colors):
    r = Rectangle(bar_w, 50, x=bar_start + i * bar_w, y=610,
                  fill=col, fill_opacity=1, stroke_width=0)
    r.fadein(1.5 + i * 0.03, 1.8 + i * 0.03)
    r.fadeout(2.5, 3.0)
    show.add(r)

# =============================================================================
# Phase 2 (3-6s): LinearGradient — horizontal, vertical, diagonal
# =============================================================================
title2 = Text(
    text='LinearGradient', x=960, y=80, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=3.0,
)
title2.fadein(3.0, 3.5)
title2.fadeout(5.5, 6.0)
show.add(title2)

# Horizontal gradient (default direction)
horiz_grad = LinearGradient([
    (0, '#FC6255'),
    (0.5, '#F0AC5F'),
    (1, '#FFFF00'),
])
show.add_gradient(horiz_grad)

horiz_rect = Rectangle(450, 250, x=80, y=180, fill=horiz_grad.fill_ref(),
                        fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
horiz_rect.fadein(3.2, 3.7)
horiz_rect.fadeout(5.5, 6.0)
show.add(horiz_rect)

horiz_label = Text(text='Horizontal (default)', x=305, y=470, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
horiz_label.fadein(3.3, 3.7)
horiz_label.fadeout(5.5, 6.0)
show.add(horiz_label)

# Vertical gradient (bottom to top)
vert_grad = LinearGradient([
    (0, '#1e3a5f'),
    (0.4, '#29ABCA'),
    (1, '#5CD0B3'),
], x1='0%', y1='100%', x2='0%', y2='0%')
show.add_gradient(vert_grad)

vert_rect = Rectangle(450, 250, x=735, y=180, fill=vert_grad.fill_ref(),
                       fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
vert_rect.fadein(3.5, 4.0)
vert_rect.fadeout(5.5, 6.0)
show.add(vert_rect)

vert_label = Text(text='Vertical (bottom-to-top)', x=960, y=470, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
vert_label.fadein(3.6, 4.0)
vert_label.fadeout(5.5, 6.0)
show.add(vert_label)

# Diagonal gradient
diag_grad = LinearGradient([
    (0, '#9B59B6'),
    (0.5, '#E84D60'),
    (1, '#F0AC5F'),
], x1='0%', y1='0%', x2='100%', y2='100%')
show.add_gradient(diag_grad)

diag_rect = Rectangle(450, 250, x=1390, y=180, fill=diag_grad.fill_ref(),
                       fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
diag_rect.fadein(3.8, 4.3)
diag_rect.fadeout(5.5, 6.0)
show.add(diag_rect)

diag_label = Text(text='Diagonal (top-left to bottom-right)', x=1615, y=470,
                  font_size=22, fill='#AAAAAA', stroke_width=0,
                  text_anchor='middle', creation=3.0)
diag_label.fadein(3.9, 4.3)
diag_label.fadeout(5.5, 6.0)
show.add(diag_label)

# Full-width gradient bar with many stops
rainbow_grad = LinearGradient([
    (0, '#FF0000'),
    (0.17, '#FF8C00'),
    (0.33, '#FFFF00'),
    (0.5, '#00FF00'),
    (0.67, '#0000FF'),
    (0.83, '#8B00FF'),
    (1, '#FF0000'),
])
show.add_gradient(rainbow_grad)

rainbow_rect = Rectangle(1700, 120, x=110, y=550, fill=rainbow_grad.fill_ref(),
                           fill_opacity=1, stroke_width=0, rx=12, ry=12, creation=3.0)
rainbow_rect.fadein(4.2, 4.8)
rainbow_rect.fadeout(5.5, 6.0)
show.add(rainbow_rect)

rainbow_label = Text(text='Multi-stop Rainbow LinearGradient', x=960, y=720,
                     font_size=24, fill='#AAAAAA', stroke_width=0,
                     text_anchor='middle', creation=3.0)
rainbow_label.fadein(4.3, 4.8)
rainbow_label.fadeout(5.5, 6.0)
show.add(rainbow_label)

# Gradient applied to text-like shapes
grad_text_label = Text(text='Applied to shapes', x=960, y=800, font_size=22,
                       fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0)
grad_text_label.fadein(4.5, 5.0)
grad_text_label.fadeout(5.5, 6.0)
show.add(grad_text_label)

fire_grad = LinearGradient([
    (0, '#FFFF00'),
    (0.5, '#FF862F'),
    (1, '#FC6255'),
], x1='0%', y1='100%', x2='0%', y2='0%')
show.add_gradient(fire_grad)

fire_circle = Circle(r=80, cx=600, cy=920, fill=fire_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=3.0)
fire_circle.fadein(4.6, 5.1)
fire_circle.fadeout(5.5, 6.0)
show.add(fire_circle)

ice_grad = LinearGradient([
    (0, '#FFFFFF'),
    (0.5, '#9CDCEB'),
    (1, '#236B8E'),
])
show.add_gradient(ice_grad)

ice_rect = Rectangle(200, 120, x=860, y=860, fill=ice_grad.fill_ref(),
                      fill_opacity=1, stroke_width=0, rx=20, ry=20, creation=3.0)
ice_rect.fadein(4.7, 5.2)
ice_rect.fadeout(5.5, 6.0)
show.add(ice_rect)

metal_grad = LinearGradient([
    (0, '#444444'),
    (0.3, '#BBBBBB'),
    (0.5, '#FFFFFF'),
    (0.7, '#BBBBBB'),
    (1, '#444444'),
])
show.add_gradient(metal_grad)

metal_rect = Rectangle(200, 120, x=1160, y=860, fill=metal_grad.fill_ref(),
                         fill_opacity=1, stroke_width=0, rx=20, ry=20, creation=3.0)
metal_rect.fadein(4.8, 5.3)
metal_rect.fadeout(5.5, 6.0)
show.add(metal_rect)

# =============================================================================
# Phase 3 (6-9s): RadialGradient — glow, spotlight, multi-stop
# =============================================================================
title3 = Text(
    text='RadialGradient', x=960, y=80, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=6.0,
)
title3.fadein(6.0, 6.5)
title3.fadeout(8.5, 9.0)
show.add(title3)

# Basic radial glow
glow_grad = RadialGradient([
    ('0%', '#FFFF00', 1),
    ('60%', '#FF862F', 0.6),
    ('100%', '#FC6255', 0),
])
show.add_gradient(glow_grad)

glow_circle = Circle(r=170, cx=320, cy=350, fill=glow_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=6.0)
glow_circle.fadein(6.2, 6.8)
glow_circle.fadeout(8.5, 9.0)
show.add(glow_circle)

glow_label = Text(text='Warm Glow', x=320, y=560, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
glow_label.fadein(6.3, 6.8)
glow_label.fadeout(8.5, 9.0)
show.add(glow_label)

# Cool spotlight effect (off-center focus)
spot_grad = RadialGradient([
    ('0%', '#FFFFFF', 1),
    ('40%', '#58C4DD', 0.8),
    ('80%', '#236B8E', 0.4),
    ('100%', '#1e1e2e', 0),
], cx='35%', cy='35%', fx='35%', fy='35%')
show.add_gradient(spot_grad)

spot_circle = Circle(r=170, cx=960, cy=350, fill=spot_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=6.0)
spot_circle.fadein(6.5, 7.1)
spot_circle.fadeout(8.5, 9.0)
show.add(spot_circle)

spot_label = Text(text='Off-center Spotlight', x=960, y=560, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
spot_label.fadein(6.6, 7.1)
spot_label.fadeout(8.5, 9.0)
show.add(spot_label)

# Neon ring effect
neon_grad = RadialGradient([
    ('0%', '#000000', 0),
    ('55%', '#000000', 0),
    ('70%', '#D147BD', 1),
    ('85%', '#9A72AC', 0.5),
    ('100%', '#000000', 0),
])
show.add_gradient(neon_grad)

neon_circle = Circle(r=170, cx=1600, cy=350, fill=neon_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=6.0)
neon_circle.fadein(6.8, 7.4)
neon_circle.fadeout(8.5, 9.0)
show.add(neon_circle)

neon_label = Text(text='Neon Ring Effect', x=1600, y=560, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
neon_label.fadein(6.9, 7.4)
neon_label.fadeout(8.5, 9.0)
show.add(neon_label)

# Radial gradient on a rectangle
earth_grad = RadialGradient([
    ('0%', '#83C167'),
    ('40%', '#5CD0B3'),
    ('70%', '#29ABCA'),
    ('100%', '#236B8E'),
])
show.add_gradient(earth_grad)

earth_rect = Rectangle(500, 200, x=230, y=660, fill=earth_grad.fill_ref(),
                        fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=6.0)
earth_rect.fadein(7.2, 7.7)
earth_rect.fadeout(8.5, 9.0)
show.add(earth_rect)

earth_label = Text(text='Radial on Rectangle', x=480, y=900, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
earth_label.fadein(7.3, 7.7)
earth_label.fadeout(8.5, 9.0)
show.add(earth_label)

# Concentric rings via radial gradient
ring_grad = RadialGradient([
    ('0%', '#FC6255', 1),
    ('20%', '#FC6255', 1),
    ('22%', '#1e1e2e', 1),
    ('38%', '#1e1e2e', 1),
    ('40%', '#FFFF00', 1),
    ('58%', '#FFFF00', 1),
    ('60%', '#1e1e2e', 1),
    ('78%', '#1e1e2e', 1),
    ('80%', '#58C4DD', 1),
    ('98%', '#58C4DD', 1),
    ('100%', '#1e1e2e', 0),
])
show.add_gradient(ring_grad)

ring_circle = Circle(r=140, cx=960, cy=760, fill=ring_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=6.0)
ring_circle.fadein(7.5, 8.0)
ring_circle.fadeout(8.5, 9.0)
show.add(ring_circle)

ring_label = Text(text='Concentric Rings', x=960, y=930, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
ring_label.fadein(7.5, 8.0)
ring_label.fadeout(8.5, 9.0)
show.add(ring_label)

# Sunset sphere illusion
sphere_grad = RadialGradient([
    ('0%', '#FFFFFF', 1),
    ('15%', '#FFD700', 0.9),
    ('50%', '#FF862F', 0.8),
    ('80%', '#CF5044', 0.6),
    ('100%', '#222222', 0.3),
], cx='40%', cy='35%', fx='40%', fy='35%')
show.add_gradient(sphere_grad)

sphere_circle = Circle(r=120, cx=1500, cy=760, fill=sphere_grad.fill_ref(),
                       fill_opacity=1, stroke_width=0, creation=6.0)
sphere_circle.fadein(7.8, 8.3)
sphere_circle.fadeout(8.5, 9.0)
show.add(sphere_circle)

sphere_label = Text(text='3D Sphere Illusion', x=1500, y=920, font_size=22,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
sphere_label.fadein(7.8, 8.3)
sphere_label.fadeout(8.5, 9.0)
show.add(sphere_label)

# =============================================================================
# Phase 4 (9-12s): VCollection gradient methods
# =============================================================================
title4 = Text(
    text='VCollection Gradient Methods', x=960, y=80, font_size=52,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=9.0,
)
title4.fadein(9.0, 9.5)
title4.fadeout(11.5, 12.0)
show.add(title4)

# --- set_color_by_gradient (fill) ---
fill_label = Text(
    text='set_color_by_gradient(RED, YELLOW, BLUE)', x=960, y=190,
    font_size=26, fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0,
)
fill_label.fadein(9.2, 9.7)
fill_label.fadeout(11.5, 12.0)
show.add(fill_label)

fill_circles = []
for i in range(10):
    c = Circle(r=40, cx=235 + i * 155, cy=290, fill='#FFFFFF',
               fill_opacity=1, stroke_width=2, stroke='#333333', creation=9.0)
    fill_circles.append(c)

fill_group = VCollection(*fill_circles, creation=9.0)
fill_group.set_color_by_gradient('#FC6255', '#FFFF00', '#58C4DD', start=9.0)
fill_group.stagger_fadein(9.3, 10.0)
fill_group.fadeout(11.5, 12.0)
show.add(fill_group)

# --- set_color_by_gradient (stroke) ---
stroke_label = Text(
    text='set_color_by_gradient(..., attr="stroke")', x=960, y=400,
    font_size=26, fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0,
)
stroke_label.fadein(9.5, 10.0)
stroke_label.fadeout(11.5, 12.0)
show.add(stroke_label)

stroke_rects = []
for i in range(10):
    r = RoundedRectangle(100, 80, x=185 + i * 155, y=450,
                  fill_opacity=0, stroke='#FFFFFF', stroke_width=5,
                  corner_radius=10, creation=9.0)
    stroke_rects.append(r)

stroke_group = VCollection(*stroke_rects, creation=9.0)
stroke_group.set_color_by_gradient(
    '#83C167', '#FFFF00', '#FC6255', '#9A72AC', attr='stroke', start=9.0,
)
stroke_group.stagger_fadein(9.6, 10.3)
stroke_group.fadeout(11.5, 12.0)
show.add(stroke_group)

# --- set_opacity_by_gradient ---
opacity_label = Text(
    text='set_opacity_by_gradient(1.0, 0.1)', x=960, y=600,
    font_size=26, fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0,
)
opacity_label.fadein(9.8, 10.3)
opacity_label.fadeout(11.5, 12.0)
show.add(opacity_label)

opacity_circles = []
for i in range(10):
    c = Circle(r=40, cx=235 + i * 155, cy=710, fill='#58C4DD',
               fill_opacity=1, stroke_width=0, creation=9.0)
    opacity_circles.append(c)

opacity_group = VCollection(*opacity_circles, creation=9.0)
opacity_group.set_opacity_by_gradient(1.0, 0.1, start=9.0)
opacity_group.stagger_fadein(10.0, 10.7)
opacity_group.fadeout(11.5, 12.0)
show.add(opacity_group)

# Opacity value labels below each circle
for i in range(10):
    opac = 1.0 + (0.1 - 1.0) * i / 9
    lbl = Text(text=f'{opac:.1f}', x=235 + i * 155, y=775,
               font_size=16, fill='#666666', stroke_width=0,
               text_anchor='middle', creation=9.0)
    lbl.fadein(10.0 + i * 0.07, 10.5 + i * 0.07)
    lbl.fadeout(11.5, 12.0)
    show.add(lbl)

# --- Combined: color + opacity gradient ---
combo_label = Text(
    text='Combined: color + opacity gradient', x=960, y=860,
    font_size=24, fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0,
)
combo_label.fadein(10.3, 10.8)
combo_label.fadeout(11.5, 12.0)
show.add(combo_label)

combo_rects = []
for i in range(12):
    r = Rectangle(100, 60, x=190 + i * 130, y=900, fill='#FFFFFF',
                  fill_opacity=1, stroke_width=0, rx=8, ry=8, creation=9.0)
    combo_rects.append(r)

combo_group = VCollection(*combo_rects, creation=9.0)
combo_group.set_color_by_gradient('#FC6255', '#FFFF00', '#83C167', '#58C4DD', start=9.0)
combo_group.set_opacity_by_gradient(0.3, 1.0, start=9.0)
combo_group.stagger_fadein(10.5, 11.2)
combo_group.fadeout(11.5, 12.0)
show.add(combo_group)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    show.browser_display(0, 12)
