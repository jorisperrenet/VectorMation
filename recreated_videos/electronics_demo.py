"""Electronics & Optics Demo — Resistor, Capacitor, Inductor, Diode, LED, Circuit, Lens, Ray."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/electronics_demo')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0–4s): Basic Components — Resistor, Capacitor, Inductor, Diode
# =============================================================================

phase1_title = Text(
    text='Electronic Components', x=960, y=80, font_size=44,
    fill='#ffffff', stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.5)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# Layout: four components evenly spaced across the canvas
# Each component spans ~160px horizontally, centered at y=400
comp_y = 420
comp_len = 180
spacing = 400
x_start = 960 - 1.5 * spacing  # leftmost center

# -- Resistor --
r_cx = x_start
resistor = Resistor(
    x1=r_cx - comp_len / 2, y1=comp_y,
    x2=r_cx + comp_len / 2, y2=comp_y,
    label='R1 = 1k\u03A9', stroke='#FC6255',
)
resistor.fadein(0.3, 0.8)
resistor.fadeout(3.5, 4.0)
canvas.add(resistor)

r_desc = Text(
    text='Resistor', x=r_cx, y=comp_y + 70, font_size=28,
    fill='#FC6255', stroke_width=0, text_anchor='middle',
)
r_desc.fadein(0.5, 1.0)
r_desc.fadeout(3.5, 4.0)
canvas.add(r_desc)

# -- Capacitor --
c_cx = x_start + spacing
capacitor = Capacitor(
    x1=c_cx - comp_len / 2, y1=comp_y,
    x2=c_cx + comp_len / 2, y2=comp_y,
    label='C1 = 10\u00B5F', stroke='#58C4DD',
)
capacitor.fadein(0.8, 1.3)
capacitor.fadeout(3.5, 4.0)
canvas.add(capacitor)

c_desc = Text(
    text='Capacitor', x=c_cx, y=comp_y + 70, font_size=28,
    fill='#58C4DD', stroke_width=0, text_anchor='middle',
)
c_desc.fadein(1.0, 1.5)
c_desc.fadeout(3.5, 4.0)
canvas.add(c_desc)

# -- Inductor --
l_cx = x_start + 2 * spacing
inductor = Inductor(
    x1=l_cx - comp_len / 2, y1=comp_y,
    x2=l_cx + comp_len / 2, y2=comp_y,
    label='L1 = 100mH', stroke='#83C167', n_loops=5,
)
inductor.fadein(1.3, 1.8)
inductor.fadeout(3.5, 4.0)
canvas.add(inductor)

l_desc = Text(
    text='Inductor', x=l_cx, y=comp_y + 70, font_size=28,
    fill='#83C167', stroke_width=0, text_anchor='middle',
)
l_desc.fadein(1.5, 2.0)
l_desc.fadeout(3.5, 4.0)
canvas.add(l_desc)

# -- Diode --
d_cx = x_start + 3 * spacing
diode = Diode(
    x1=d_cx - comp_len / 2, y1=comp_y,
    x2=d_cx + comp_len / 2, y2=comp_y,
    label='D1', stroke='#F5A623',
)
diode.fadein(1.8, 2.3)
diode.fadeout(3.5, 4.0)
canvas.add(diode)

d_desc = Text(
    text='Diode', x=d_cx, y=comp_y + 70, font_size=28,
    fill='#F5A623', stroke_width=0, text_anchor='middle',
)
d_desc.fadein(2.0, 2.5)
d_desc.fadeout(3.5, 4.0)
canvas.add(d_desc)

# Subtitle
phase1_sub = Text(
    text='Fundamental passive and active components', x=960, y=700, font_size=24,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
phase1_sub.fadein(2.5, 3.0)
phase1_sub.fadeout(3.5, 4.0)
canvas.add(phase1_sub)

# =============================================================================
# Phase 2 (4–8s): LED + Simple Circuit Layout
# =============================================================================

phase2_title = Text(
    text='LED Circuit', x=960, y=80, font_size=44,
    fill='#ffffff', stroke_width=0, text_anchor='middle', creation=4.0,
)
phase2_title.fadein(4.0, 4.5)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# -- LED component (large, centered upper area) --
led = LED(
    x1=760, y1=300, x2=1000, y2=300,
    label='Red LED', color='#FF4444', creation=4.0,
)
led.fadein(4.0, 4.6)
led.fadeout(7.5, 8.0)
canvas.add(led)

# -- Simple circuit: battery -> resistor -> LED -> ground --
# Draw a rectangular circuit loop using Lines
wire_color = '#aaaaaa'
wire_width = 2

# Circuit rectangle corners
cx_left = 400
cx_right = 1520
cy_top = 500
cy_bottom = 750

# Top wire (left to right)
wire_top = Line(
    x1=cx_left, y1=cy_top, x2=cx_right, y2=cy_top,
    stroke=wire_color, stroke_width=wire_width, creation=4.5,
)
wire_top.fadein(4.5, 5.0)
wire_top.fadeout(7.5, 8.0)
canvas.add(wire_top)

# Right wire (top to bottom)
wire_right = Line(
    x1=cx_right, y1=cy_top, x2=cx_right, y2=cy_bottom,
    stroke=wire_color, stroke_width=wire_width, creation=4.5,
)
wire_right.fadein(4.7, 5.2)
wire_right.fadeout(7.5, 8.0)
canvas.add(wire_right)

# Bottom wire (right to left)
wire_bottom = Line(
    x1=cx_right, y1=cy_bottom, x2=cx_left, y2=cy_bottom,
    stroke=wire_color, stroke_width=wire_width, creation=4.5,
)
wire_bottom.fadein(4.9, 5.4)
wire_bottom.fadeout(7.5, 8.0)
canvas.add(wire_bottom)

# Left wire (bottom to top)
wire_left = Line(
    x1=cx_left, y1=cy_bottom, x2=cx_left, y2=cy_top,
    stroke=wire_color, stroke_width=wire_width, creation=4.5,
)
wire_left.fadein(5.1, 5.6)
wire_left.fadeout(7.5, 8.0)
canvas.add(wire_left)

# Place a resistor on the top wire
circuit_resistor = Resistor(
    x1=cx_left + 80, y1=cy_top,
    x2=cx_left + 280, y2=cy_top,
    label='330\u03A9', stroke='#FC6255', creation=5.0,
)
circuit_resistor.fadein(5.0, 5.5)
circuit_resistor.fadeout(7.5, 8.0)
canvas.add(circuit_resistor)

# Place an LED on the top wire (right side)
circuit_led = LED(
    x1=cx_right - 320, y1=cy_top,
    x2=cx_right - 120, y2=cy_top,
    label='LED', color='#FF4444', creation=5.2,
)
circuit_led.fadein(5.2, 5.7)
circuit_led.fadeout(7.5, 8.0)
canvas.add(circuit_led)

# Battery symbol on the left wire (+ and - labels)
batt_y_mid = (cy_top + cy_bottom) / 2
batt_plus = Text(
    text='+', x=cx_left - 30, y=batt_y_mid - 30, font_size=32,
    fill='#FC6255', stroke_width=0, text_anchor='middle', creation=5.5,
)
batt_plus.fadein(5.5, 6.0)
batt_plus.fadeout(7.5, 8.0)
canvas.add(batt_plus)

batt_minus = Text(
    text='\u2013', x=cx_left - 30, y=batt_y_mid + 30, font_size=32,
    fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=5.5,
)
batt_minus.fadein(5.5, 6.0)
batt_minus.fadeout(7.5, 8.0)
canvas.add(batt_minus)

batt_label = Text(
    text='9V', x=cx_left - 60, y=batt_y_mid, font_size=24,
    fill='#ffffff', stroke_width=0, text_anchor='middle', creation=5.5,
)
batt_label.fadein(5.5, 6.0)
batt_label.fadeout(7.5, 8.0)
canvas.add(batt_label)

# Current flow arrow indicator
current_arrow = Arrow(
    x1=cx_left + 400, y1=cy_top - 40,
    x2=cx_left + 550, y2=cy_top - 40,
    stroke='#FFFF00', stroke_width=2, fill='#FFFF00', creation=6.0,
)
current_arrow.fadein(6.0, 6.5)
current_arrow.fadeout(7.5, 8.0)
canvas.add(current_arrow)

current_label = Text(
    text='I (current)', x=cx_left + 475, y=cy_top - 60, font_size=20,
    fill='#FFFF00', stroke_width=0, text_anchor='middle', creation=6.0,
)
current_label.fadein(6.0, 6.5)
current_label.fadeout(7.5, 8.0)
canvas.add(current_label)

# Ground symbol text at bottom center
gnd_label = Text(
    text='GND', x=960, y=cy_bottom + 40, font_size=22,
    fill='#888888', stroke_width=0, text_anchor='middle', creation=5.5,
)
gnd_label.fadein(5.5, 6.0)
gnd_label.fadeout(7.5, 8.0)
canvas.add(gnd_label)

# =============================================================================
# Phase 3 (8–12s): Lens and Optics
# =============================================================================

phase3_title = Text(
    text='Geometric Optics', x=960, y=80, font_size=44,
    fill='#ffffff', stroke_width=0, text_anchor='middle', creation=8.0,
)
phase3_title.fadein(8.0, 8.5)
phase3_title.fadeout(11.0, 11.5)
canvas.add(phase3_title)

# -- Convex lens --
convex_lens = Lens(
    cx=960, cy=500, height=350, focal_length=250, thickness=35,
    color='#58C4DD', show_focal_points=True, show_axis=True,
    creation=8.0,
)
convex_lens.fadein(8.0, 8.8)
convex_lens.fadeout(11.0, 11.5)
canvas.add(convex_lens)

lens_label = Text(
    text='Convex Lens (f = 250px)', x=960, y=730, font_size=24,
    fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=8.3,
)
lens_label.fadein(8.3, 8.8)
lens_label.fadeout(11.0, 11.5)
canvas.add(lens_label)

# -- Three parallel rays through the lens --
ray_colors = ['#FF4444', '#FFFF00', '#83C167']
ray_y_offsets = [-100, 0, 100]

for i, (rc, ry_off) in enumerate(zip(ray_colors, ray_y_offsets)):
    ray = Ray(
        x1=200, y1=500 + ry_off, angle=0, length=1600,
        lenses=[convex_lens], color=rc, stroke_width=2,
        show_arrow=True, creation=8.5 + i * 0.3,
    )
    ray.fadein(8.5 + i * 0.3, 9.0 + i * 0.3)
    ray.fadeout(11.0, 11.5)
    canvas.add(ray)

# -- Concave lens on the right side for comparison --
concave_lens = Lens(
    cx=960, cy=500, height=280, focal_length=-200, thickness=30,
    color='#F5A623', show_focal_points=True, show_axis=False,
    creation=9.8,
)
concave_lens.fadein(9.8, 10.3)
concave_lens.fadeout(11.0, 11.5)
canvas.add(concave_lens)

concave_label = Text(
    text='+ Concave Lens (f = -200px)', x=960, y=770, font_size=22,
    fill='#F5A623', stroke_width=0, text_anchor='middle', creation=9.8,
)
concave_label.fadein(9.8, 10.3)
concave_label.fadeout(11.0, 11.5)
canvas.add(concave_label)

# Subtitle
phase3_sub = Text(
    text='Rays refract through thin lenses (paraxial approximation)',
    x=960, y=830, font_size=22,
    fill='#888888', stroke_width=0, text_anchor='middle', creation=9.0,
)
phase3_sub.fadein(9.0, 9.5)
phase3_sub.fadeout(11.0, 11.5)
canvas.add(phase3_sub)

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
