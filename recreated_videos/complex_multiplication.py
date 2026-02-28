"""Complex Multiplication — visualizing multiplication on the complex plane.

Shows how multiplying complex numbers combines magnitudes and adds angles:
|z*w| = |z|*|w| and arg(z*w) = arg(z) + arg(w).
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/complex_multiplication')
canvas.set_background()

T = 10

# ── Complex plane (Axes) ────────────────────────────────────────────
axes = Axes(x_range=(-3, 3), y_range=(-3, 3),
            x=260, y=40, plot_width=1000, plot_height=1000,
            x_label='Re', y_label='Im',
            show_grid=True, creation=0)
axes.add_coordinates()
axes.fadein(0, 0.8)

# Origin in SVG coordinates
ox, oy = axes.coords_to_point(0, 0)

# ── Unit circle (dashed, subtle) ────────────────────────────────────
uc_r_px = abs(axes.coords_to_point(1, 0)[0] - ox)
unit_circle = Circle(r=uc_r_px, cx=ox, cy=oy,
                     fill_opacity=0, stroke='#555', stroke_width=1.5,
                     stroke_dasharray='8 4', creation=0)
unit_circle.fadein(0.5, 1.2)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Complex Multiplication', x=1550, y=60,
             font_size=38, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 0.8)

# ── Helper: complex to SVG coords ───────────────────────────────────
def c2s(re, im):
    """Convert complex coords to SVG pixel coords."""
    return axes.coords_to_point(re, im)

# ── z = 1 + i ───────────────────────────────────────────────────────
z_re, z_im = 1, 1
z_mag = math.hypot(z_re, z_im)
z_arg = math.atan2(z_im, z_re)  # 45 degrees = pi/4

zx, zy = c2s(z_re, z_im)

# Arrow for z
z_arrow = Arrow(x1=ox, y1=oy, x2=zx, y2=zy,
                stroke='#58C4DD', fill='#58C4DD', stroke_width=3,
                tip_length=20, tip_width=16, creation=0)
z_arrow.fadein(1.0, 1.8)

z_dot = Dot(cx=zx, cy=zy, r=5, fill='#58C4DD', creation=0)
z_dot.fadein(1.0, 1.8)

# Label for z in rectangular form
z_label = Text(text='z = 1 + i', x=zx + 15, y=zy - 20,
               font_size=22, fill='#58C4DD', stroke_width=0, text_anchor='start',
               creation=0)
z_label.fadein(1.2, 1.8)

# Label for z in polar form
z_polar_label = Text(text=f'|z| = \u221a2, arg(z) = 45\u00b0',
                     x=1550, y=130,
                     font_size=20, fill='#58C4DD', stroke_width=0,
                     text_anchor='middle', creation=0)
z_polar_label.fadein(1.5, 2.0)

# ── Animate rotation by e^(i*pi/3) ─ rotating z around origin ──────
# From t=2.5 to t=4.5, rotate z by 60 degrees (pi/3)
rotation_angle = math.pi / 3  # 60 degrees
rot_duration_start = 2.5
rot_duration_end = 4.5

# Label for the rotation
rot_label = Text(text='Multiply by e^(i\u03c0/3): rotate 60\u00b0',
                 x=1550, y=200,
                 font_size=20, fill='#FFFF00', stroke_width=0,
                 text_anchor='middle', creation=0)
rot_label.fadein(2.0, 2.5)
rot_label.fadeout(5.0, 5.5)

# Animated arrow endpoint for the rotation
z_rot_re = z_mag * math.cos(z_arg + rotation_angle)
z_rot_im = z_mag * math.sin(z_arg + rotation_angle)
z_rot_x, z_rot_y = c2s(z_rot_re, z_rot_im)

def _z_rotating_endpoint(t):
    """Smoothly interpolate z through rotation from t=2.5 to t=4.5."""
    if t <= rot_duration_start:
        angle = z_arg
    elif t >= rot_duration_end:
        angle = z_arg + rotation_angle
    else:
        frac = (t - rot_duration_start) / (rot_duration_end - rot_duration_start)
        # Smooth easing
        frac = frac * frac * (3 - 2 * frac)
        angle = z_arg + rotation_angle * frac
    re = z_mag * math.cos(angle)
    im = z_mag * math.sin(angle)
    return c2s(re, im)

z_arrow.shaft.p2.set_onward(rot_duration_start, _z_rotating_endpoint)
z_arrow._update_tip_dynamic(rot_duration_start)

z_dot.c.set_onward(rot_duration_start, _z_rotating_endpoint)

# Update z label position to follow the dot
def _z_label_pos(t):
    pos = _z_rotating_endpoint(t)
    return (pos[0] + 15, pos[1] - 20)

z_label.x.set_onward(rot_duration_start, lambda t: _z_label_pos(t)[0])
z_label.y.set_onward(rot_duration_start, lambda t: _z_label_pos(t)[1])

# Update label text after rotation completes
z_label.text.set_onward(rot_duration_end, f'z\u00b7e^(i\u03c0/3)')

# Arc showing the rotation angle
rot_arc = Arc(cx=ox, cy=oy, r=40, start_angle=0, end_angle=0,
              stroke='#FFFF00', stroke_width=2, fill_opacity=0, creation=0)
rot_arc.start_angle.set_onward(rot_duration_start,
    -math.degrees(z_arg))  # negative because SVG y is flipped
rot_arc.end_angle.set_onward(rot_duration_start,
    lambda t: -math.degrees(z_arg + rotation_angle) if t >= rot_duration_end
    else -math.degrees(z_arg + rotation_angle * min(1, max(0, (t - rot_duration_start) / (rot_duration_end - rot_duration_start))**2 * (3 - 2 * min(1, max(0, (t - rot_duration_start) / (rot_duration_end - rot_duration_start)))))))
rot_arc.fadein(rot_duration_start, rot_duration_start + 0.3)
rot_arc.fadeout(5.0, 5.5)

# ── Second number w = 2 at 45 degrees = sqrt(2) + sqrt(2)i ─────────
w_mag = 2
w_arg_deg = 45
w_arg = math.radians(w_arg_deg)
w_re = w_mag * math.cos(w_arg)  # sqrt(2)
w_im = w_mag * math.sin(w_arg)  # sqrt(2)

wx, wy = c2s(w_re, w_im)

# Arrow for w
w_arrow = Arrow(x1=ox, y1=oy, x2=wx, y2=wy,
                stroke='#83C167', fill='#83C167', stroke_width=3,
                tip_length=20, tip_width=16, creation=0)
w_arrow.fadein(5.0, 5.8)

w_dot = Dot(cx=wx, cy=wy, r=5, fill='#83C167', creation=0)
w_dot.fadein(5.0, 5.8)

# Label for w
w_label = Text(text=f'w = 2\u222045\u00b0', x=wx + 15, y=wy - 20,
               font_size=22, fill='#83C167', stroke_width=0, text_anchor='start',
               creation=0)
w_label.fadein(5.2, 5.8)

w_polar_label = Text(text=f'|w| = 2, arg(w) = 45\u00b0',
                     x=1550, y=250,
                     font_size=20, fill='#83C167', stroke_width=0,
                     text_anchor='middle', creation=0)
w_polar_label.fadein(5.2, 5.8)

# ── Reset z back to original position for the multiplication demo ───
# At t=5.0, snap z arrow back to original z = 1+i
_z_reset = c2s(z_re, z_im)
z_arrow.shaft.p2.set_onward(5.0, _z_reset)
z_arrow._update_tip_dynamic(5.0)
z_dot.c.set_onward(5.0, _z_reset)
z_label.text.set_onward(5.0, 'z = 1 + i')
z_label.x.set_onward(5.0, _z_reset[0] + 15)
z_label.y.set_onward(5.0, _z_reset[1] - 20)

# ── Compute the product z * w ───────────────────────────────────────
# z = 1+i, w = sqrt(2)+sqrt(2)i
# z*w = (1+i)(sqrt(2)+sqrt(2)i) = sqrt(2) + sqrt(2)i + sqrt(2)i + sqrt(2)*i^2
#     = sqrt(2) - sqrt(2) + 2*sqrt(2)i = 2*sqrt(2)i
# |z*w| = |z|*|w| = sqrt(2)*2 = 2*sqrt(2)
# arg(z*w) = arg(z)+arg(w) = 45+45 = 90 degrees
product_mag = z_mag * w_mag
product_arg = z_arg + w_arg  # 90 degrees
product_re = product_mag * math.cos(product_arg)
product_im = product_mag * math.sin(product_arg)

px, py = c2s(product_re, product_im)

# Arrow for product z*w — animate it growing from t=6.5 to t=8.0
product_arrow = Arrow(x1=ox, y1=oy, x2=ox, y2=oy,
                      stroke='#FC6255', fill='#FC6255', stroke_width=3,
                      tip_length=20, tip_width=16, creation=0)

anim_start = 6.5
anim_end = 8.0

def _product_endpoint(t):
    """Animate the product arrow: rotate z by arg(w) while scaling by |w|."""
    if t <= anim_start:
        return c2s(z_re, z_im)
    elif t >= anim_end:
        return c2s(product_re, product_im)
    else:
        frac = (t - anim_start) / (anim_end - anim_start)
        frac = frac * frac * (3 - 2 * frac)  # smooth
        cur_mag = z_mag + (product_mag - z_mag) * frac
        cur_arg = z_arg + w_arg * frac
        re = cur_mag * math.cos(cur_arg)
        im = cur_mag * math.sin(cur_arg)
        return c2s(re, im)

product_arrow.shaft.p2.set_onward(anim_start, _product_endpoint)
product_arrow._update_tip_dynamic(anim_start)
product_arrow.fadein(6.0, 6.5)

product_dot = Dot(cx=0, cy=0, r=5, fill='#FC6255', creation=0)
product_dot.c.set_onward(anim_start, _product_endpoint)
product_dot.fadein(6.0, 6.5)

# Label for the product
product_label = Text(text='z\u00b7w = 2\u221a2 i', x=0, y=0,
                     font_size=22, fill='#FC6255', stroke_width=0,
                     text_anchor='start', creation=0)
product_label.x.set_onward(anim_start,
    lambda t: _product_endpoint(t)[0] + 15)
product_label.y.set_onward(anim_start,
    lambda t: _product_endpoint(t)[1] - 20)
product_label.fadein(7.5, 8.0)

# ── Show the multiplication rules ───────────────────────────────────
rule1 = Text(text='|z\u00b7w| = |z|\u00b7|w| = \u221a2 \u00b7 2 = 2\u221a2',
             x=1550, y=350,
             font_size=20, fill='#FC6255', stroke_width=0,
             text_anchor='middle', creation=0)
rule1.fadein(8.0, 8.5)

rule2 = Text(text='arg(z\u00b7w) = arg(z) + arg(w) = 45\u00b0 + 45\u00b0 = 90\u00b0',
             x=1550, y=390,
             font_size=20, fill='#FC6255', stroke_width=0,
             text_anchor='middle', creation=0)
rule2.fadein(8.3, 8.8)

# General rules
general1 = Text(text='|z\u00b7w| = |z| \u00b7 |w|',
                x=1550, y=480,
                font_size=24, fill='#fff', stroke_width=0,
                text_anchor='middle', creation=0)
general1.fadein(8.8, 9.3)

general2 = Text(text='arg(z\u00b7w) = arg(z) + arg(w)',
                x=1550, y=520,
                font_size=24, fill='#fff', stroke_width=0,
                text_anchor='middle', creation=0)
general2.fadein(9.0, 9.5)

subtitle = Text(text='Multiplication = Stretch + Rotate',
                x=1550, y=600,
                font_size=22, fill='#aaa', stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(9.2, 9.7)

# ── Add everything to canvas ────────────────────────────────────────
canvas.add(
    axes, unit_circle, title,
    z_arrow, z_dot, z_label, z_polar_label,
    rot_arc, rot_label,
    w_arrow, w_dot, w_label, w_polar_label,
    product_arrow, product_dot, product_label,
    rule1, rule2, general1, general2, subtitle,
)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
