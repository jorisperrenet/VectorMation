"""Static 3x4 grid showcasing circuit and science components."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 4
ROW_H = 300
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 3

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/circuit_components')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 60

title = Text(text='Circuit & Science Components', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

span = 200

# ── Row 0: Circuit elements ──────────────────────────────────────────────

objs.append(Text(text='Resistor', x=col_x(0), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Resistor(x1=col_x(0) - span // 2, y1=obj_y(0), x2=col_x(0) + span // 2,
                      y2=obj_y(0), label='R'))

objs.append(Text(text='Capacitor', x=col_x(1), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Capacitor(x1=col_x(1) - span // 2, y1=obj_y(0), x2=col_x(1) + span // 2,
                       y2=obj_y(0), label='C'))

objs.append(Text(text='Inductor', x=col_x(2), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Inductor(x1=col_x(2) - span // 2, y1=obj_y(0), x2=col_x(2) + span // 2,
                      y2=obj_y(0), label='L', n_loops=4))

objs.append(Text(text='Diode', x=col_x(3), y=lbl_y(0), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Diode(x1=col_x(3) - span // 2, y1=obj_y(0), x2=col_x(3) + span // 2,
                   y2=obj_y(0), label='D'))

# ── Row 1: More circuit + science ────────────────────────────────────────

objs.append(Text(text='LED', x=col_x(0), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(LED(x1=col_x(0) - span // 2, y1=obj_y(1), x2=col_x(0) + span // 2,
                y2=obj_y(1), label='LED', color='#FF0000'))

objs.append(Text(text='Molecule2D', x=col_x(1), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Molecule2D(
    atoms=[('O', 0, 0), ('H', -1, 0.8), ('H', 1, 0.8)],
    bonds=[(0, 1), (0, 2)],
    scale=70, cx=col_x(1), cy=obj_y(1), atom_radius=18, font_size=14
))

objs.append(Text(text='BohrAtom', x=col_x(2), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
atom = BohrAtom(protons=6, neutrons=6, electrons=[2, 4],
                cx=col_x(2), cy=obj_y(1) + 60,
                nucleus_r=18, shell_spacing=28)
objs.append(atom)

objs.append(Text(text='ElectricField', x=col_x(3), y=lbl_y(1), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
q_pos = Charge(magnitude=3, cx=col_x(3) - 80, cy=obj_y(1) + 60)
q_neg = Charge(magnitude=-3, cx=col_x(3) + 80, cy=obj_y(1) + 60)
ef = ElectricField(q_pos, q_neg, max_length=40,
                   x_range=(col_x(3) - 200, col_x(3) + 200, 60),
                   y_range=(obj_y(1) - 20, obj_y(1) + 160, 60))
objs.extend([ef, q_pos, q_neg])

# ── Row 2: Waves & Optics ───────────────────────────────────────────────

objs.append(Text(text='StandingWave', x=col_x(0), y=lbl_y(2), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
sw = StandingWave(x1=col_x(0) - 180, y1=obj_y(2) + 60, x2=col_x(0) + 180,
                  y2=obj_y(2) + 60, amplitude=50, harmonics=3, frequency=0,
                  start=0, end=0, stroke='#58C4DD', stroke_width=3)
objs.append(sw)

objs.append(Text(text='Lens + Ray', x=col_x(1), y=lbl_y(2), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
lens = Lens(cx=col_x(1), cy=obj_y(2) + 60, height=200, focal_length=150,
            color='#58C4DD', show_focal_points=True, show_axis=True)
ray1 = Ray(x1=col_x(1) - 200, y1=obj_y(2) + 10, angle=0, length=400,
           lenses=[lens], color='#FFFF00', stroke_width=2, show_arrow=True)
ray2 = Ray(x1=col_x(1) - 200, y1=obj_y(2) + 110, angle=0, length=400,
           lenses=[lens], color='#FFA500', stroke_width=2, show_arrow=True)
objs.extend([lens, ray1, ray2])

objs.append(Text(text='Charge (+)', x=col_x(2), y=lbl_y(2), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Charge(magnitude=5, cx=col_x(2), cy=obj_y(2) + 60))

objs.append(Text(text='Charge (\u2013)', x=col_x(3), y=lbl_y(2), font_size=20,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle'))
objs.append(Charge(magnitude=-5, cx=col_x(3), cy=obj_y(2) + 60))

canvas.add_objects(*objs)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/circuit_components.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
