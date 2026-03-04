"""Color Theory Demo — Gradients, Color Manipulation, Color Harmonies."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0-3s): Title + color gradient row
# =============================================================================
title = Text(
    text='Color Theory', x=960, y=100, font_size=56,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle',
)
title.write(0.0, 1.0)
title.fadeout(2.5, 3.0)
canvas.add(title)

# A row of 10 circles showing a color gradient from red through yellow to blue
gradient_colors = color_gradient(['#FC6255', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC'], n=10)
gradient_label = Text(
    text='color_gradient()', x=960, y=210, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
gradient_label.fadein(0.5, 1.0)
gradient_label.fadeout(2.5, 3.0)
canvas.add(gradient_label)

spacing = 140
start_x = 960 - (9 * spacing) / 2
for i, col in enumerate(gradient_colors):
    c = Circle(r=50, cx=start_x + i * spacing, cy=400, fill=col,
               fill_opacity=1, stroke=lighten(col, 0.3), stroke_width=3)
    c.fadein(0.3 + i * 0.1, 0.8 + i * 0.1)
    c.fadeout(2.5, 3.0)
    canvas.add(c)

# Interpolation demo below the gradient row
interp_label = Text(
    text='interpolate_color()', x=960, y=520, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
interp_label.fadein(1.0, 1.5)
interp_label.fadeout(2.5, 3.0)
canvas.add(interp_label)

for i in range(7):
    t = i / 6
    col = interpolate_color('#FC6255', '#58C4DD', t)
    r = Rectangle(120, 80, x=960 - 3 * 150 + i * 150 - 60, y=580,
                  fill=col, fill_opacity=1, stroke_width=0, rx=10, ry=10)
    r.fadein(1.2 + i * 0.08, 1.7 + i * 0.08)
    r.fadeout(2.5, 3.0)
    canvas.add(r)

# t labels under interpolation bars
for i in range(7):
    t = i / 6
    tl = Text(text=f't={t:.1f}', x=960 - 3 * 150 + i * 150, y=690,
              font_size=18, fill='#666666', stroke_width=0, text_anchor='middle')
    tl.fadein(1.2 + i * 0.08, 1.7 + i * 0.08)
    tl.fadeout(2.5, 3.0)
    canvas.add(tl)

# =============================================================================
# Phase 2 (3-6s): LinearGradient and RadialGradient fills
# =============================================================================
phase2_title = Text(
    text='SVG Gradients', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=3.0,
)
phase2_title.fadein(3.0, 3.5)
phase2_title.fadeout(5.5, 6.0)
canvas.add(phase2_title)

# Linear gradient: sunset horizontal
sunset_grad = LinearGradient([
    (0, '#FC6255'),
    (0.5, '#F0AC5F'),
    (1, '#FFFF00'),
])
canvas.add_def(sunset_grad)

sunset_rect = Rectangle(500, 280, x=100, y=200, fill=sunset_grad.fill_ref(),
                         fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
sunset_rect.fadein(3.2, 3.8)
sunset_rect.fadeout(5.5, 6.0)
canvas.add(sunset_rect)

sunset_label = Text(text='LinearGradient', x=350, y=530, font_size=24,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
sunset_label.fadein(3.3, 3.8)
sunset_label.fadeout(5.5, 6.0)
canvas.add(sunset_label)

sunset_sub = Text(text='(horizontal)', x=350, y=565, font_size=20,
                  fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0)
sunset_sub.fadein(3.3, 3.8)
sunset_sub.fadeout(5.5, 6.0)
canvas.add(sunset_sub)

# Linear gradient: ocean vertical
ocean_grad = LinearGradient([
    (0, '#1e3a5f'),
    (0.5, '#58C4DD'),
    (1, '#5CD0B3'),
], x1='0%', y1='100%', x2='0%', y2='0%')
canvas.add_def(ocean_grad)

ocean_rect = Rectangle(500, 280, x=710, y=200, fill=ocean_grad.fill_ref(),
                        fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
ocean_rect.fadein(3.5, 4.1)
ocean_rect.fadeout(5.5, 6.0)
canvas.add(ocean_rect)

ocean_label = Text(text='LinearGradient', x=960, y=530, font_size=24,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
ocean_label.fadein(3.6, 4.1)
ocean_label.fadeout(5.5, 6.0)
canvas.add(ocean_label)

ocean_sub = Text(text='(vertical)', x=960, y=565, font_size=20,
                 fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0)
ocean_sub.fadein(3.6, 4.1)
ocean_sub.fadeout(5.5, 6.0)
canvas.add(ocean_sub)

# Radial gradient: glow
glow_grad = RadialGradient([
    ('0%', '#FFFF00', 1),
    ('50%', '#FC6255', 0.7),
    ('100%', '#9A72AC', 0),
])
canvas.add_def(glow_grad)

glow_circle = Circle(r=160, cx=1570, cy=340, fill=glow_grad.fill_ref(),
                     fill_opacity=1, stroke_width=0, creation=3.0)
glow_circle.fadein(3.8, 4.4)
glow_circle.fadeout(5.5, 6.0)
canvas.add(glow_circle)

glow_label = Text(text='RadialGradient', x=1570, y=530, font_size=24,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
glow_label.fadein(3.9, 4.4)
glow_label.fadeout(5.5, 6.0)
canvas.add(glow_label)

# Diagonal gradient demo
diag_grad = LinearGradient([
    (0, '#9B59B6'),
    (1, '#4ECDC4'),
], x1='0%', y1='0%', x2='100%', y2='100%')
canvas.add_def(diag_grad)

diag_rect = Rectangle(600, 200, x=350, y=650, fill=diag_grad.fill_ref(),
                       fill_opacity=1, stroke_width=0, rx=15, ry=15, creation=3.0)
diag_rect.fadein(4.2, 4.8)
diag_rect.fadeout(5.5, 6.0)
canvas.add(diag_rect)

diag_label = Text(text='Diagonal Gradient', x=650, y=900, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
diag_label.fadein(4.3, 4.8)
diag_label.fadeout(5.5, 6.0)
canvas.add(diag_label)

# Multi-stop radial gradient
multi_grad = RadialGradient([
    ('0%', '#FFFFFF', 1),
    ('30%', '#58C4DD', 0.9),
    ('60%', '#236B8E', 0.7),
    ('100%', '#1e1e2e', 0),
])
canvas.add_def(multi_grad)

multi_circle = Circle(r=120, cx=1350, cy=750, fill=multi_grad.fill_ref(),
                      fill_opacity=1, stroke_width=0, creation=3.0)
multi_circle.fadein(4.5, 5.0)
multi_circle.fadeout(5.5, 6.0)
canvas.add(multi_circle)

multi_label = Text(text='Multi-stop Radial', x=1350, y=900, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=3.0)
multi_label.fadein(4.5, 5.0)
multi_label.fadeout(5.5, 6.0)
canvas.add(multi_label)

# =============================================================================
# Phase 3 (6-9s): Color manipulation — lighten, darken, complementary
# =============================================================================
phase3_title = Text(
    text='Color Manipulation', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=6.0,
)
phase3_title.fadein(6.0, 6.5)
phase3_title.fadeout(8.5, 9.0)
canvas.add(phase3_title)

# Lighten demo — centered on left half (x=420)
base_color = '#FC6255'
lighten_label = Text(text='lighten()', x=420, y=180, font_size=28,
                     fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
lighten_label.fadein(6.2, 6.7)
lighten_label.fadeout(8.5, 9.0)
canvas.add(lighten_label)

lighten_amounts = [0.0, 0.15, 0.3, 0.5, 0.7]
for i, amt in enumerate(lighten_amounts):
    col = lighten(base_color, amt) if amt > 0 else base_color
    cx_l = 420 + (i - 2) * 115
    r = Rectangle(100, 80, x=cx_l - 50, y=220,
                  fill=col, fill_opacity=1, stroke_width=0, rx=8, ry=8, creation=6.0)
    r.fadein(6.3 + i * 0.08, 6.8 + i * 0.08)
    r.fadeout(8.5, 9.0)
    canvas.add(r)
    lbl = Text(text=f'{amt:.0%}', x=cx_l, y=325,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=6.0)
    lbl.fadein(6.3 + i * 0.08, 6.8 + i * 0.08)
    lbl.fadeout(8.5, 9.0)
    canvas.add(lbl)

# Darken demo — centered on left half (x=420)
darken_label = Text(text='darken()', x=420, y=390, font_size=28,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
darken_label.fadein(6.5, 7.0)
darken_label.fadeout(8.5, 9.0)
canvas.add(darken_label)

darken_amounts = [0.0, 0.15, 0.3, 0.5, 0.7]
for i, amt in enumerate(darken_amounts):
    col = darken(base_color, amt) if amt > 0 else base_color
    cx_d = 420 + (i - 2) * 115
    r = Rectangle(100, 80, x=cx_d - 50, y=430,
                  fill=col, fill_opacity=1, stroke_width=0, rx=8, ry=8, creation=6.0)
    r.fadein(6.6 + i * 0.08, 7.1 + i * 0.08)
    r.fadeout(8.5, 9.0)
    canvas.add(r)
    lbl = Text(text=f'{amt:.0%}', x=cx_d, y=535,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=6.0)
    lbl.fadein(6.6 + i * 0.08, 7.1 + i * 0.08)
    lbl.fadeout(8.5, 9.0)
    canvas.add(lbl)

# Complementary colors — centered on right half (x=1380)
comp_label = Text(text='complementary()', x=1380, y=180, font_size=28,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
comp_label.fadein(6.8, 7.3)
comp_label.fadeout(8.5, 9.0)
canvas.add(comp_label)

comp_colors = ['#FC6255', '#58C4DD', '#83C167', '#FF862F']
for i, col in enumerate(comp_colors):
    col_comp = complementary(col)
    cx_pos = 1380 + (i - 1.5) * 120
    # Original color circle
    c1 = Circle(r=35, cx=cx_pos, cy=270, fill=col,
                fill_opacity=1, stroke_width=2, stroke='#333333', creation=6.0)
    c1.fadein(7.0 + i * 0.1, 7.4 + i * 0.1)
    c1.fadeout(8.5, 9.0)
    canvas.add(c1)
    # Complementary color circle
    c2 = Circle(r=35, cx=cx_pos, cy=370, fill=col_comp,
                fill_opacity=1, stroke_width=2, stroke='#333333', creation=6.0)
    c2.fadein(7.0 + i * 0.1, 7.4 + i * 0.1)
    c2.fadeout(8.5, 9.0)
    canvas.add(c2)

orig_label = Text(text='Original', x=1380 - 1.5 * 120 - 70, y=275, font_size=18,
                  fill='#666666', stroke_width=0, text_anchor='end', creation=6.0)
orig_label.fadein(7.0, 7.4)
orig_label.fadeout(8.5, 9.0)
canvas.add(orig_label)

comp_res_label = Text(text='Complement', x=1380 - 1.5 * 120 - 70, y=375, font_size=18,
                      fill='#666666', stroke_width=0, text_anchor='end', creation=6.0)
comp_res_label.fadein(7.0, 7.4)
comp_res_label.fadeout(8.5, 9.0)
canvas.add(comp_res_label)

# Saturate / Desaturate demo — centered at x=960
sat_label = Text(text='saturate / desaturate', x=960, y=580, font_size=28,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=6.0)
sat_label.fadein(7.2, 7.7)
sat_label.fadeout(8.5, 9.0)
canvas.add(sat_label)

sat_base = '#9A72AC'  # PURPLE
sat_levels = [-0.4, -0.2, 0, 0.2, 0.4]
sat_names = ['-0.4', '-0.2', 'base', '+0.2', '+0.4']
for i, (lvl, name) in enumerate(zip(sat_levels, sat_names)):
    if lvl < 0:
        col = desaturate(sat_base, abs(lvl))
    elif lvl > 0:
        col = saturate(sat_base, lvl)
    else:
        col = sat_base
    cx_s = 960 + (i - 2) * 200
    r = Rectangle(160, 100, x=cx_s - 80, y=640,
                  fill=col, fill_opacity=1, stroke_width=0, rx=10, ry=10, creation=6.0)
    r.fadein(7.3 + i * 0.08, 7.8 + i * 0.08)
    r.fadeout(8.5, 9.0)
    canvas.add(r)
    lbl = Text(text=name, x=cx_s, y=770,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=6.0)
    lbl.fadein(7.3 + i * 0.08, 7.8 + i * 0.08)
    lbl.fadeout(8.5, 9.0)
    canvas.add(lbl)

# =============================================================================
# Phase 4 (9-12s): Color harmonies — triadic, analogous, split_complementary
# =============================================================================
phase4_title = Text(
    text='Color Harmonies', x=960, y=80, font_size=48,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=9.0,
)
phase4_title.fadein(9.0, 9.5)
phase4_title.fadeout(11.5, 12.0)
canvas.add(phase4_title)

harmony_base = '#E84D60'  # A vibrant red
harmony_r = 55

# --- Triadic ---
triadic_label = Text(text='triadic()', x=320, y=200, font_size=30,
                     fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0)
triadic_label.fadein(9.2, 9.7)
triadic_label.fadeout(11.5, 12.0)
canvas.add(triadic_label)

tri_colors = triadic(harmony_base)
tri_all = [harmony_base] + tri_colors
tri_labels_text = ['Base', '+120', '+240']
for i, (col, ltxt) in enumerate(zip(tri_all, tri_labels_text)):
    c = Circle(r=harmony_r, cx=180 + i * 140, cy=330, fill=col,
               fill_opacity=1, stroke_width=3, stroke=lighten(col, 0.3), creation=9.0)
    c.fadein(9.3 + i * 0.12, 9.8 + i * 0.12)
    c.fadeout(11.5, 12.0)
    canvas.add(c)
    lbl = Text(text=ltxt, x=180 + i * 140, y=410,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0)
    lbl.fadein(9.3 + i * 0.12, 9.8 + i * 0.12)
    lbl.fadeout(11.5, 12.0)
    canvas.add(lbl)

# --- Analogous ---
analog_label = Text(text='analogous()', x=960, y=200, font_size=30,
                    fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0)
analog_label.fadein(9.5, 10.0)
analog_label.fadeout(11.5, 12.0)
canvas.add(analog_label)

analog_colors = analogous(harmony_base)
analog_all = [analog_colors[0], harmony_base, analog_colors[1]]
analog_labels_text = ['-30', 'Base', '+30']
for i, (col, ltxt) in enumerate(zip(analog_all, analog_labels_text)):
    c = Circle(r=harmony_r, cx=820 + i * 140, cy=330, fill=col,
               fill_opacity=1, stroke_width=3, stroke=lighten(col, 0.3), creation=9.0)
    c.fadein(9.6 + i * 0.12, 10.1 + i * 0.12)
    c.fadeout(11.5, 12.0)
    canvas.add(c)
    lbl = Text(text=ltxt, x=820 + i * 140, y=410,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0)
    lbl.fadein(9.6 + i * 0.12, 10.1 + i * 0.12)
    lbl.fadeout(11.5, 12.0)
    canvas.add(lbl)

# --- Split Complementary ---
split_label = Text(text='split_complementary()', x=1570, y=200, font_size=30,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0)
split_label.fadein(9.8, 10.3)
split_label.fadeout(11.5, 12.0)
canvas.add(split_label)

split_colors = split_complementary(harmony_base)
split_all = [harmony_base] + split_colors
split_labels_text = ['Base', '+150', '+210']
for i, (col, ltxt) in enumerate(zip(split_all, split_labels_text)):
    c = Circle(r=harmony_r, cx=1430 + i * 140, cy=330, fill=col,
               fill_opacity=1, stroke_width=3, stroke=lighten(col, 0.3), creation=9.0)
    c.fadein(9.9 + i * 0.12, 10.4 + i * 0.12)
    c.fadeout(11.5, 12.0)
    canvas.add(c)
    lbl = Text(text=ltxt, x=1430 + i * 140, y=410,
               font_size=16, fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0)
    lbl.fadein(9.9 + i * 0.12, 10.4 + i * 0.12)
    lbl.fadeout(11.5, 12.0)
    canvas.add(lbl)

# --- Additional: adjust_hue color wheel demonstration ---
wheel_label = Text(text='adjust_hue() — Color Wheel', x=960, y=510, font_size=28,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle', creation=9.0)
wheel_label.fadein(10.0, 10.5)
wheel_label.fadeout(11.5, 12.0)
canvas.add(wheel_label)

import math
wheel_cx, wheel_cy = 960, 720
wheel_r = 150
n_wheel = 12
for i in range(n_wheel):
    deg = i * (360 / n_wheel)
    col = adjust_hue(harmony_base, deg)
    angle_rad = math.radians(deg - 90)  # start from top
    cx_pos = wheel_cx + wheel_r * math.cos(angle_rad)
    cy_pos = wheel_cy + wheel_r * math.sin(angle_rad)
    c = Circle(r=30, cx=cx_pos, cy=cy_pos, fill=col,
               fill_opacity=1, stroke_width=2, stroke=darken(col, 0.2), creation=9.0)
    c.fadein(10.2 + i * 0.05, 10.6 + i * 0.05)
    c.fadeout(11.5, 12.0)
    canvas.add(c)

# Center label for the wheel
wheel_center_label = Text(text=f'{harmony_base}', x=wheel_cx, y=wheel_cy + 5,
                          font_size=18, fill='#AAAAAA', stroke_width=0,
                          text_anchor='middle', creation=9.0)
wheel_center_label.fadein(10.2, 10.7)
wheel_center_label.fadeout(11.5, 12.0)
canvas.add(wheel_center_label)

# =============================================================================
# Display
# =============================================================================

canvas.show(end=T)
