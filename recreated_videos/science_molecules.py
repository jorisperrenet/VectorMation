"""Science Molecules & Atoms — Molecule2D, UnitInterval, Pendulum, StandingWave, BohrAtom.

Showcases science-related vectormation classes:
- Molecule2D: 2D molecular structure visualizations (water, methane, benzene)
- UnitInterval: probability/parameter number line from 0 to 1
- Pendulum: damped harmonic oscillation
- StandingWave: vibrational harmonic modes
- BohrAtom: electron shell model
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
show = VectorMathAnim(verbose=args.verbose, save_dir='svgs/science_molecules')
show.set_background()

T = 18.0

# -- Colors -------------------------------------------------------------------
WHITE   = '#FFFFFF'
GREY    = '#888888'
CYAN    = '#58C4DD'
GREEN   = '#83C167'
RED     = '#FC6255'
YELLOW  = '#FFFF00'
ORANGE  = '#F5A623'
BLUE    = '#4488FF'

# =============================================================================
# Phase 1 (0-4s): Molecule2D — water, methane, benzene ring
# =============================================================================

p1_title = Text(text='Molecular Structures', x=960, y=70, font_size=44,
                fill=WHITE, stroke_width=0, text_anchor='middle')
p1_title.fadein(0.0, 0.5)
p1_title.fadeout(3.5, 4.0)

p1_sub = Text(text='2D Ball-and-Stick Models', x=960, y=115, font_size=24,
              fill=GREY, stroke_width=0, text_anchor='middle')
p1_sub.fadein(0.1, 0.6)
p1_sub.fadeout(3.5, 4.0)

# -- Water (H2O) --
water_atoms = [
    ('O', 0, 0),
    ('H', -0.8, -0.6),
    ('H',  0.8, -0.6),
]
water_bonds = [(0, 1, 1), (0, 2, 1)]
water = Molecule2D(water_atoms, water_bonds, scale=100,
                   cx=300, cy=450, atom_radius=22, font_size=18)
water.fadein(0.3, 0.8)
water.fadeout(3.5, 4.0)

water_label = Text(text='H2O (Water)', x=300, y=600, font_size=26,
                   fill=CYAN, stroke_width=0, text_anchor='middle')
water_label.fadein(0.5, 1.0)
water_label.fadeout(3.5, 4.0)

# -- Methane (CH4) --
methane_atoms = [
    ('C', 0, 0),
    ('H', -0.9, -0.7),
    ('H',  0.9, -0.7),
    ('H', -0.9,  0.7),
    ('H',  0.9,  0.7),
]
methane_bonds = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)]
methane = Molecule2D(methane_atoms, methane_bonds, scale=90,
                     cx=960, cy=450, atom_radius=20, font_size=16)
methane.fadein(0.8, 1.3)
methane.fadeout(3.5, 4.0)

methane_label = Text(text='CH4 (Methane)', x=960, y=600, font_size=26,
                     fill=CYAN, stroke_width=0, text_anchor='middle')
methane_label.fadein(1.0, 1.5)
methane_label.fadeout(3.5, 4.0)

# -- Benzene ring (C6H6) --
import math as _math
benzene_atoms = []
benzene_bonds = []
for i in range(6):
    angle = _math.tau * i / 6 - _math.pi / 2
    cx_b = _math.cos(angle)
    cy_b = _math.sin(angle)
    benzene_atoms.append(('C', cx_b, cy_b))
for i in range(6):
    # C-C bonds around the ring; alternating single/double
    order = 2 if i % 2 == 0 else 1
    benzene_bonds.append((i, (i + 1) % 6, order))
# Add hydrogens pointing outward
for i in range(6):
    angle = _math.tau * i / 6 - _math.pi / 2
    hx = 1.6 * _math.cos(angle)
    hy = 1.6 * _math.sin(angle)
    h_idx = len(benzene_atoms)
    benzene_atoms.append(('H', hx, hy))
    benzene_bonds.append((i, h_idx, 1))

benzene = Molecule2D(benzene_atoms, benzene_bonds, scale=80,
                     cx=1620, cy=450, atom_radius=18, font_size=14)
benzene.fadein(1.3, 1.8)
benzene.fadeout(3.5, 4.0)

benzene_label = Text(text='C6H6 (Benzene)', x=1620, y=620, font_size=26,
                     fill=CYAN, stroke_width=0, text_anchor='middle')
benzene_label.fadein(1.5, 2.0)
benzene_label.fadeout(3.5, 4.0)

# Formula annotations at the bottom
formula_text = Text(text='Atom colors: O=red  C=grey  H=white  N=blue',
                    x=960, y=950, font_size=20, fill='#aaa', stroke_width=0,
                    text_anchor='middle')
formula_text.fadein(2.0, 2.5)
formula_text.fadeout(3.5, 4.0)

show.add(p1_title, p1_sub)
show.add(water, water_label, methane, methane_label, benzene, benzene_label)
show.add(formula_text)

# =============================================================================
# Phase 2 (4-7s): UnitInterval — probability / parameter visualization
# =============================================================================

p2_title = Text(text='Unit Interval [0, 1]', x=960, y=70, font_size=44,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=4.0)
p2_title.fadein(4.0, 4.5)
p2_title.fadeout(6.5, 7.0)

p2_sub = Text(text='Probability and Parameter Space', x=960, y=115, font_size=24,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=4.0)
p2_sub.fadein(4.1, 4.6)
p2_sub.fadeout(6.5, 7.0)

# Three unit intervals showing different use cases
# 1) Probability with a marker at p=0.7
ui1 = UnitInterval(x=260, y=320, length=700, tick_step=0.1,
                   show_labels=True, font_size=16, creation=4.0,
                   stroke='#58C4DD')
ui1.fadein(4.2, 4.7)
ui1.fadeout(6.5, 7.0)

ui1_label = Text(text='Probability', x=960, y=290, font_size=24,
                 fill=CYAN, stroke_width=0, text_anchor='middle', creation=4.0)
ui1_label.fadein(4.3, 4.8)
ui1_label.fadeout(6.5, 7.0)

# Marker dot at p=0.7 on the first unit interval
marker_x = 260 + 700 * 0.7
marker1 = Dot(r=10, cx=marker_x, cy=320, fill=RED, creation=4.5)
marker1.fadein(4.5, 5.0)
marker1.fadeout(6.5, 7.0)

marker1_label = Text(text='P = 0.7', x=marker_x, y=350, font_size=18,
                     fill=RED, stroke_width=0, text_anchor='middle', creation=4.5)
marker1_label.fadein(4.5, 5.0)
marker1_label.fadeout(6.5, 7.0)

# 2) Learning rate parameter
ui2 = UnitInterval(x=260, y=520, length=700, tick_step=0.2,
                   show_labels=True, font_size=16, creation=4.3,
                   stroke='#83C167')
ui2.fadein(4.5, 5.0)
ui2.fadeout(6.5, 7.0)

ui2_label = Text(text='Learning Rate', x=960, y=490, font_size=24,
                 fill=GREEN, stroke_width=0, text_anchor='middle', creation=4.3)
ui2_label.fadein(4.6, 5.1)
ui2_label.fadeout(6.5, 7.0)

# Marker at alpha=0.01 (near 0)
marker2_x = 260 + 700 * 0.01
marker2 = Dot(r=10, cx=marker2_x, cy=520, fill=ORANGE, creation=4.8)
marker2.fadein(4.8, 5.3)
marker2.fadeout(6.5, 7.0)

marker2_label = Text(text='alpha = 0.01', x=marker2_x + 60, y=550, font_size=18,
                     fill=ORANGE, stroke_width=0, text_anchor='middle', creation=4.8)
marker2_label.fadein(4.8, 5.3)
marker2_label.fadeout(6.5, 7.0)

# 3) Progress bar style
ui3 = UnitInterval(x=260, y=720, length=700, tick_step=0.25,
                   show_labels=True, font_size=16, creation=4.6,
                   stroke='#F5A623')
ui3.fadein(4.8, 5.3)
ui3.fadeout(6.5, 7.0)

ui3_label = Text(text='Completion', x=960, y=690, font_size=24,
                 fill=ORANGE, stroke_width=0, text_anchor='middle', creation=4.6)
ui3_label.fadein(4.9, 5.4)
ui3_label.fadeout(6.5, 7.0)

# Animated marker sweeping from 0 to 1
progress_dot = Dot(r=10, cx=260, cy=720, fill=YELLOW, creation=5.0)
progress_dot.fadein(5.0, 5.3)
progress_dot.move_to(260 + 700, 720, start=5.3, end=6.3)
progress_dot.fadeout(6.5, 7.0)

show.add(p2_title, p2_sub)
show.add(ui1, ui1_label, marker1, marker1_label)
show.add(ui2, ui2_label, marker2, marker2_label)
show.add(ui3, ui3_label, progress_dot)

# =============================================================================
# Phase 3 (7-11s): BohrAtom — electron shell models
# =============================================================================

p3_title = Text(text='Bohr Atomic Model', x=960, y=70, font_size=44,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=7.0)
p3_title.fadein(7.0, 7.5)
p3_title.fadeout(10.5, 11.0)

p3_sub = Text(text='Electron Shells and Orbital Structure', x=960, y=115, font_size=24,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=7.0)
p3_sub.fadein(7.1, 7.6)
p3_sub.fadeout(10.5, 11.0)

# -- Hydrogen (Z=1) --
hydrogen = BohrAtom(protons=1, neutrons=0, cx=300, cy=500,
                    nucleus_r=22, shell_spacing=50, creation=7.0)
hydrogen.fadein(7.2, 7.7)
hydrogen.orbit(start=7.7, end=11.0, speed=60)
hydrogen.fadeout(10.5, 11.0)

h_label = Text(text='Hydrogen (Z=1)', x=300, y=620, font_size=24,
               fill=CYAN, stroke_width=0, text_anchor='middle', creation=7.0)
h_label.fadein(7.3, 7.8)
h_label.fadeout(10.5, 11.0)

# -- Carbon (Z=6) --
carbon = BohrAtom(protons=6, neutrons=6, cx=960, cy=500,
                  nucleus_r=28, shell_spacing=45, creation=7.3)
carbon.fadein(7.5, 8.0)
carbon.orbit(start=8.0, end=11.0, speed=40)
carbon.fadeout(10.5, 11.0)

c_label = Text(text='Carbon (Z=6)', x=960, y=650, font_size=24,
               fill=CYAN, stroke_width=0, text_anchor='middle', creation=7.3)
c_label.fadein(7.6, 8.1)
c_label.fadeout(10.5, 11.0)

# -- Sodium (Z=11) --
sodium = BohrAtom(protons=11, neutrons=12, cx=1620, cy=500,
                  nucleus_r=30, shell_spacing=40, creation=7.6)
sodium.fadein(7.8, 8.3)
sodium.orbit(start=8.3, end=11.0, speed=30)
sodium.fadeout(10.5, 11.0)

na_label = Text(text='Sodium (Z=11)', x=1620, y=680, font_size=24,
                fill=CYAN, stroke_width=0, text_anchor='middle', creation=7.6)
na_label.fadein(7.9, 8.4)
na_label.fadeout(10.5, 11.0)

# Shell configuration annotation
shell_text = Text(text='Shells: 2, 8, 18, 32 ... (max electrons per shell)',
                  x=960, y=950, font_size=20, fill='#aaa', stroke_width=0,
                  text_anchor='middle', creation=7.5)
shell_text.fadein(8.0, 8.5)
shell_text.fadeout(10.5, 11.0)

show.add(p3_title, p3_sub)
show.add(hydrogen, h_label, carbon, c_label, sodium, na_label)
show.add(shell_text)

# =============================================================================
# Phase 4 (11-14.5s): Pendulum — three pendulums side by side
# =============================================================================

p4_title = Text(text='Pendulum Dynamics', x=960, y=70, font_size=44,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=11.0)
p4_title.fadein(11.0, 11.5)
p4_title.fadeout(14.0, 14.5)

p4_sub = Text(text='Damped Harmonic Oscillation', x=960, y=115, font_size=24,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=11.0)
p4_sub.fadein(11.1, 11.6)
p4_sub.fadeout(14.0, 14.5)

# Short period, no damping
pend_a = Pendulum(pivot_x=350, pivot_y=230, length=320, angle=40,
                  bob_radius=20, period=1.6, damping=0.0,
                  start=11.0, end=14.5, creation=11.0)
pend_a.fadein(11.2, 11.6)
pend_a.fadeout(14.0, 14.5)

pa_label = Text(text='No damping', x=350, y=190, font_size=20,
                fill=GREEN, stroke_width=0, text_anchor='middle', creation=11.0)
pa_label.fadein(11.3, 11.8)
pa_label.fadeout(14.0, 14.5)

# Medium period, light damping
pend_b = Pendulum(pivot_x=960, pivot_y=230, length=300, angle=35,
                  bob_radius=20, period=2.0, damping=0.2,
                  start=11.0, end=14.5, creation=11.0)
pend_b.bob.set_fill(color=ORANGE, start=11.0, end=11.0)
pend_b.fadein(11.4, 11.8)
pend_b.fadeout(14.0, 14.5)

pb_label = Text(text='Light damping', x=960, y=190, font_size=20,
                fill=ORANGE, stroke_width=0, text_anchor='middle', creation=11.0)
pb_label.fadein(11.5, 12.0)
pb_label.fadeout(14.0, 14.5)

# Long period, heavy damping
pend_c = Pendulum(pivot_x=1570, pivot_y=230, length=350, angle=45,
                  bob_radius=22, period=2.4, damping=0.5,
                  start=11.0, end=14.5, creation=11.0)
pend_c.bob.set_fill(color=RED, start=11.0, end=11.0)
pend_c.fadein(11.6, 12.0)
pend_c.fadeout(14.0, 14.5)

pc_label = Text(text='Heavy damping', x=1570, y=190, font_size=20,
                fill=RED, stroke_width=0, text_anchor='middle', creation=11.0)
pc_label.fadein(11.7, 12.2)
pc_label.fadeout(14.0, 14.5)

pend_eq = Text(text='theta(t) = theta_0 * exp(-b*t) * cos(omega*t)',
               x=960, y=950, font_size=20, fill='#aaa', stroke_width=0,
               text_anchor='middle', creation=11.0)
pend_eq.fadein(11.5, 12.0)
pend_eq.fadeout(14.0, 14.5)

show.add(p4_title, p4_sub)
show.add(pend_a, pa_label, pend_b, pb_label, pend_c, pc_label)
show.add(pend_eq)

# =============================================================================
# Phase 5 (14.5-18s): StandingWave — harmonic modes
# =============================================================================

p5_title = Text(text='Standing Waves', x=960, y=70, font_size=44,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=14.5)
p5_title.fadein(14.5, 15.0)
p5_title.fadeout(17.5, 18.0)

p5_sub = Text(text='Fundamental and Overtones', x=960, y=115, font_size=24,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=14.5)
p5_sub.fadein(14.6, 15.1)
p5_sub.fadeout(17.5, 18.0)

wave_colors = [CYAN, GREEN, YELLOW, ORANGE]
wave_x1, wave_x2 = 200, 1720
wave_modes = [1, 2, 3, 4]
wave_labels = ['Fundamental (n=1)', '1st Overtone (n=2)',
               '2nd Overtone (n=3)', '3rd Overtone (n=4)']

for i, (n, color, label_txt) in enumerate(zip(wave_modes, wave_colors, wave_labels)):
    y_base = 280 + i * 180
    freq = n * 0.7

    # Equilibrium dashed line
    eq_line = Line(x1=wave_x1, y1=y_base, x2=wave_x2, y2=y_base,
                   stroke='#333', stroke_width=1, stroke_dasharray='4 4',
                   creation=14.5)
    eq_line.fadein(14.6 + i * 0.15, 15.0 + i * 0.15)
    eq_line.fadeout(17.5, 18.0)

    wave = StandingWave(
        x1=wave_x1, y1=y_base, x2=wave_x2, y2=y_base,
        amplitude=55, harmonics=n, frequency=freq, num_points=200,
        start=14.5, end=18.0, creation=14.5,
        stroke=color, stroke_width=3,
    )
    wave.fadein(14.7 + i * 0.15, 15.1 + i * 0.15)
    wave.fadeout(17.5, 18.0)

    mode_label = Text(text=label_txt, x=wave_x1 - 10, y=y_base + 5,
                      font_size=18, fill=color, stroke_width=0,
                      text_anchor='end', creation=14.5)
    mode_label.fadein(14.7 + i * 0.15, 15.1 + i * 0.15)
    mode_label.fadeout(17.5, 18.0)

    show.add(eq_line, wave, mode_label)

wave_eq = Text(text='y(x,t) = A * sin(n*pi*x/L) * cos(omega*t)',
               x=960, y=1010, font_size=20, fill='#aaa', stroke_width=0,
               text_anchor='middle', creation=14.5)
wave_eq.fadein(15.0, 15.5)
wave_eq.fadeout(17.5, 18.0)

show.add(p5_title, p5_sub, wave_eq)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    show.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
