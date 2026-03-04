"""Static 3x3 grid showcasing science components."""
from vectormation.objects import *

COLS = 3
ROW_H = 300
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 2

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 60

title = Text(text='Science Components', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# ── Row 0: Chemistry ────────────────────────────────────────────────────

objs.append(Text(text='Molecule2D', x=col_x(0), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Molecule2D(
    atoms=[('O', 0, 0), ('H', -1, 0.8), ('H', 1, 0.8)],
    bonds=[(0, 1), (0, 2)],
    scale=70, cx=col_x(0), cy=obj_y(0), atom_radius=18, font_size=14
))

objs.append(Text(text='BohrAtom', x=col_x(1), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
atom = BohrAtom(protons=6, neutrons=6, electrons=[2, 4],
                cx=col_x(1), cy=obj_y(0) + 60,
                nucleus_r=18, shell_spacing=28)
objs.append(atom)

objs.append(Text(text='NeuralNetwork', x=col_x(2), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
nn = NeuralNetwork([3, 5, 4, 2], cx=col_x(2), cy=obj_y(0) + 60,
                   width=350, height=200, neuron_radius=10)
objs.append(nn)

# ── Row 1: Waves & Optics ──────────────────────────────────────────────

objs.append(Text(text='StandingWave', x=col_x(0), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
sw = StandingWave(x1=col_x(0) - 180, y1=obj_y(1) + 60, x2=col_x(0) + 180,
                  y2=obj_y(1) + 60, amplitude=50, harmonics=3, frequency=0,
                  start=0, end=0, stroke='#58C4DD', stroke_width=3)
objs.append(sw)

objs.append(Text(text='Lens + Ray', x=col_x(1), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
lens = Lens(cx=col_x(1), cy=obj_y(1) + 60, height=200, focal_length=150,
            color='#58C4DD', show_focal_points=True, show_axis=True)
ray1 = Ray(x1=col_x(1) - 200, y1=obj_y(1) + 10, angle=0, length=400,
           lenses=[lens], color='#FFFF00', stroke_width=2, show_arrow=True)
ray2 = Ray(x1=col_x(1) - 200, y1=obj_y(1) + 110, angle=0, length=400,
           lenses=[lens], color='#FFA500', stroke_width=2, show_arrow=True)
objs.extend([lens, ray1, ray2])

objs.append(Text(text='Pendulum', x=col_x(2), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
pend = Pendulum(pivot_x=col_x(2), pivot_y=obj_y(1), length=120, angle=30,
                bob_radius=14, period=2.0, damping=0, start=0, end=0)
objs.append(pend)

canvas.add_objects(*objs)

canvas.show()
