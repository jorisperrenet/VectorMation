"""Static 2x3 grid showcasing 3D objects rendered with ThreeDAxes."""
from vectormation.objects import *
import math

COLS = 3
ROW_H = 400
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 2

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 160

title = Text(text='3D Objects', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# Helper to create a label for each cell
def cell_label(text, col, row):
    return Text(text=text, x=col_x(col), y=lbl_y(row), font_size=22,
                fill='#aaa', stroke_width=0, text_anchor='middle')

# --- Row 0, Col 0: Surface (height-map) ---
objs.append(cell_label('Surface', 0, 0))
ax_surf = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-1.5, 1.5),
                     cx=col_x(0), cy=obj_y(0), scale=80,
                     phi=math.radians(75), theta=math.radians(-30),
                     show_ticks=False, show_labels=False)
ax_surf.plot_surface(lambda x, y: math.sin(x) * math.cos(y),
                     resolution=(20, 20), fill_color='#4488ff',
                     stroke_width=0.5, fill_opacity=0.8)
objs.append(ax_surf)

# --- Row 0, Col 1: Sphere3D ---
objs.append(cell_label('Sphere3D', 1, 0))
ax_sphere = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
                       cx=col_x(1), cy=obj_y(0), scale=80,
                       phi=math.radians(75), theta=math.radians(-30),
                       show_ticks=False, show_labels=False)
sphere = Sphere3D(radius=1.5, center=(0, 0, 0), fill_color='#FC6255', fill_opacity=0.9)
ax_sphere.add_surface(sphere)
objs.append(ax_sphere)

# --- Row 0, Col 2: Cube ---
objs.append(cell_label('Cube', 2, 0))
ax_cube = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
                     cx=col_x(2), cy=obj_y(0), scale=80,
                     phi=math.radians(75), theta=math.radians(-30),
                     show_ticks=False, show_labels=False)
cube_faces = Cube(side_length=2, center=(0, 0, 0), fill_color='#58C4DD')
for face in cube_faces:
    ax_cube.add_surface(face)
objs.append(ax_cube)

# --- Row 1, Col 0: Cylinder3D ---
objs.append(cell_label('Cylinder3D', 0, 1))
ax_cyl = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
                    cx=col_x(0), cy=obj_y(1), scale=80,
                    phi=math.radians(75), theta=math.radians(-30),
                    show_ticks=False, show_labels=False)
cyl = Cylinder3D(radius=1, height=2.5, center=(0, 0, 0), fill_color='#83C167')
ax_cyl.add_surface(cyl)
objs.append(ax_cyl)

# --- Row 1, Col 1: Torus3D ---
objs.append(cell_label('Torus3D', 1, 1))
ax_torus = ThreeDAxes(x_range=(-4, 4), y_range=(-4, 4), z_range=(-2, 2),
                      cx=col_x(1), cy=obj_y(1), scale=60,
                      phi=math.radians(75), theta=math.radians(-30),
                      show_ticks=False, show_labels=False)
torus = Torus3D(major_radius=2, minor_radius=0.6, center=(0, 0, 0), fill_color='#F0AC5F')
ax_torus.add_surface(torus)
objs.append(ax_torus)

# --- Row 1, Col 2: Prism3D + primitives ---
objs.append(cell_label('Prism3D + Primitives', 2, 1))
ax_prism = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
                      cx=col_x(2), cy=obj_y(1), scale=80,
                      phi=math.radians(75), theta=math.radians(-30),
                      show_ticks=False, show_labels=False)
prism_faces = Prism3D(n_sides=6, radius=1, height=2, center=(0, 0, 0), fill_color='#9A72AC')
for face in prism_faces:
    ax_prism.add_surface(face)

# Add primitives around the prism
ax_prism.add_3d(Line3D(start=(-2, -2, -1), end=(2, 2, 2), stroke='#E8E8E8', stroke_width=2))
ax_prism.add_3d(Dot3D(point=(2, 2, 2), radius=6, fill='#FC6255'))
ax_prism.add_3d(Arrow3D(start=(-2, 2, 0), end=(-2, 2, 2.5), stroke='#83C167', stroke_width=2))
ax_prism.add_3d(Text3D('Hi!', point=(2, -1.5, 2), font_size=18, fill='#58C4DD'))
objs.append(ax_prism)

canvas.add_objects(*objs)

canvas.show()
