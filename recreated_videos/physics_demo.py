"""Physics Demo — Neural Network, Pendulum, Standing Wave, Electric Field.

Showcases physics-related classes from vectormation: NeuralNetwork with
forward propagation, Pendulum simulation, StandingWave visualization,
and Charge + ElectricField with Coulomb field arrows.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_demo')
canvas.set_background()

T = 12.0

# -- Colors -------------------------------------------------------------------
CYAN    = '#58C4DD'
GREEN   = '#83C167'
YELLOW  = '#FFFF00'
RED     = '#FC6255'
ORANGE  = '#F5A623'
BLUE    = '#4488FF'
WHITE   = '#FFFFFF'
GREY    = '#888888'
DARK    = '#2c3e50'

# =============================================================================
# Phase 1 (0-3s): Neural Network with propagation animation
# =============================================================================
p1_title = Text(text='Neural Network', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=0)
p1_title.fadein(0.0, 0.4)
p1_title.fadeout(2.5, 3.0)

p1_sub = Text(text='Forward Propagation', x=960, y=100, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=0)
p1_sub.fadein(0.1, 0.5)
p1_sub.fadeout(2.5, 3.0)

nn = NeuralNetwork(
    layer_sizes=[3, 5, 4, 2],
    cx=960, cy=500,
    width=900, height=500,
    neuron_radius=18,
    neuron_fill=DARK,
    edge_color='#555555',
    edge_width=1,
    creation=0,
)
nn.fadein(0.2, 0.7)
nn.label_input(['x1', 'x2', 'x3'], font_size=18, buff=25)
nn.label_output(['y1', 'y2'], font_size=18, buff=25)
nn.propagate(start=0.8, end=2.6, delay=0.4, color=CYAN)
nn.fadeout(2.6, 3.0)

canvas.add(p1_title, p1_sub, nn)

# =============================================================================
# Phase 2 (3-6s): Pendulum simulation
# =============================================================================
p2_title = Text(text='Simple Pendulum', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=3.0)
p2_title.fadein(3.0, 3.4)
p2_title.fadeout(5.5, 6.0)

p2_sub = Text(text='Damped Harmonic Oscillation', x=960, y=100, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=3.0)
p2_sub.fadein(3.1, 3.5)
p2_sub.fadeout(5.5, 6.0)

# Equation label
p2_eq = Text(text='theta(t) = theta_0 * e^(-bt) * cos(wt)', x=960, y=950,
             font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle',
             creation=3.0)
p2_eq.fadein(3.2, 3.6)
p2_eq.fadeout(5.5, 6.0)

# Create three pendulums with different lengths/periods side by side
pend1 = Pendulum(
    pivot_x=480, pivot_y=220, length=350, angle=35,
    bob_radius=22, period=1.8, damping=0.15,
    start=3.0, end=6.0, creation=3.0,
)
pend1.fadein(3.2, 3.5)
pend1.fadeout(5.6, 6.0)

pend2 = Pendulum(
    pivot_x=960, pivot_y=220, length=280, angle=25,
    bob_radius=18, period=1.4, damping=0.1,
    start=3.0, end=6.0, creation=3.0,
)
pend2.bob.set_fill(color=GREEN, start=3.0, end=3.0)
pend2.fadein(3.3, 3.6)
pend2.fadeout(5.6, 6.0)

pend3 = Pendulum(
    pivot_x=1440, pivot_y=220, length=400, angle=45,
    bob_radius=25, period=2.2, damping=0.08,
    start=3.0, end=6.0, creation=3.0,
)
pend3.bob.set_fill(color=ORANGE, start=3.0, end=3.0)
pend3.fadein(3.4, 3.7)
pend3.fadeout(5.6, 6.0)

# Length labels
for px, label_text in [(480, 'L = 350'), (960, 'L = 280'), (1440, 'L = 400')]:
    lbl = Text(text=label_text, x=px, y=170, font_size=18, fill=GREY,
               stroke_width=0, text_anchor='middle', creation=3.0)
    lbl.fadein(3.3, 3.7)
    lbl.fadeout(5.5, 6.0)
    canvas.add(lbl)

canvas.add(p2_title, p2_sub, p2_eq, pend1, pend2, pend3)

# =============================================================================
# Phase 3 (6-9s): Standing wave visualization
# =============================================================================
p3_title = Text(text='Standing Waves', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=6.0)
p3_title.fadein(6.0, 6.4)
p3_title.fadeout(8.5, 9.0)

p3_sub = Text(text='Harmonic modes n=1,2,3', x=960, y=100, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=6.0)
p3_sub.fadein(6.1, 6.5)
p3_sub.fadeout(8.5, 9.0)

wave_colors = [CYAN, GREEN, YELLOW]
wave_x1, wave_x2 = 260, 1660
wave_spacing = 220

for i, (n, color) in enumerate(zip([1, 2, 3], wave_colors)):
    y_base = 300 + i * wave_spacing
    freq = n * 0.8

    wave = StandingWave(
        x1=wave_x1, y1=y_base, x2=wave_x2, y2=y_base,
        amplitude=70, harmonics=n, frequency=freq, num_points=200,
        start=6.0, end=9.0, creation=6.0,
        stroke=color, stroke_width=3,
    )
    wave.fadein(6.2 + i * 0.2, 6.6 + i * 0.2)
    wave.fadeout(8.5, 9.0)

    # Mode label on the left
    mode_label = Text(text=f'n = {n}', x=wave_x1 - 60, y=y_base + 5,
                      font_size=22, fill=color, stroke_width=0,
                      text_anchor='end', creation=6.0)
    mode_label.fadein(6.2 + i * 0.2, 6.6 + i * 0.2)
    mode_label.fadeout(8.5, 9.0)

    # Frequency label on the right
    freq_label = Text(text=f'f = {n}f1', x=wave_x2 + 60, y=y_base + 5,
                      font_size=18, fill=GREY, stroke_width=0,
                      text_anchor='start', creation=6.0)
    freq_label.fadein(6.2 + i * 0.2, 6.6 + i * 0.2)
    freq_label.fadeout(8.5, 9.0)

    # Equilibrium dashed line
    eq_line = Line(x1=wave_x1, y1=y_base, x2=wave_x2, y2=y_base,
                   stroke='#333', stroke_width=1, stroke_dasharray='4 4',
                   creation=6.0)
    eq_line.fadein(6.1, 6.4)
    eq_line.fadeout(8.5, 9.0)

    canvas.add(eq_line, wave, mode_label, freq_label)

# Equation at the bottom
p3_eq = Text(text='y(x,t) = A sin(n*pi*x/L) cos(w*t)', x=960, y=960,
             font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle',
             creation=6.0)
p3_eq.fadein(6.3, 6.7)
p3_eq.fadeout(8.5, 9.0)

canvas.add(p3_title, p3_sub, p3_eq)

# =============================================================================
# Phase 4 (9-12s): Electric charges with field lines
# =============================================================================
p4_title = Text(text='Electric Field', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=9.0)
p4_title.fadein(9.0, 9.4)
p4_title.fadeout(11.5, 12.0)

p4_sub = Text(text='Coulomb Field from Point Charges', x=960, y=100, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=9.0)
p4_sub.fadein(9.1, 9.5)
p4_sub.fadeout(11.5, 12.0)

# Positive charge on the left, negative on the right
q_pos = Charge(magnitude=3, cx=600, cy=540, radius=28,
               add_glow=True, glow_layers=8, creation=9.0)
q_pos.fadein(9.2, 9.6)
q_pos.fadeout(11.5, 12.0)

q_neg = Charge(magnitude=-3, cx=1320, cy=540, radius=28,
               add_glow=True, glow_layers=8, creation=9.0)
q_neg.fadein(9.3, 9.7)
q_neg.fadeout(11.5, 12.0)

# Electric field arrows
field = ElectricField(
    q_pos, q_neg,
    x_range=(150, 1770, 135),
    y_range=(180, 900, 135),
    max_length=60,
    color=CYAN,
    stroke_width=1.5,
    creation=9.0,
)
field.fadein(9.5, 10.0)
field.fadeout(11.3, 11.8)

# Charge labels
q_pos_label = Text(text='+3q', x=600, y=600, font_size=22, fill=RED,
                   stroke_width=0, text_anchor='middle', creation=9.0)
q_pos_label.fadein(9.4, 9.8)
q_pos_label.fadeout(11.5, 12.0)

q_neg_label = Text(text='-3q', x=1320, y=600, font_size=22, fill=BLUE,
                   stroke_width=0, text_anchor='middle', creation=9.0)
q_neg_label.fadein(9.4, 9.8)
q_neg_label.fadeout(11.5, 12.0)

# Coulomb's law equation
p4_eq = Text(text="E = k * q / r^2", x=960, y=960,
             font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle',
             creation=9.0)
p4_eq.fadein(9.5, 9.9)
p4_eq.fadeout(11.5, 12.0)

canvas.add(p4_title, p4_sub)
canvas.add(field, q_pos, q_neg)
canvas.add(q_pos_label, q_neg_label, p4_eq)

# -- Render -------------------------------------------------------------------
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
