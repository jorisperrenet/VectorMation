"""3D Primitives Demo — Lines, Dots, Arrows, Text, Solids, and Platonic Solids.

Showcases 3D primitive objects (Line3D, Dot3D, Arrow3D, Text3D),
solid shapes (Cube, Cylinder3D, Cone3D, Torus3D, Prism3D),
and all four Platonic solids (Tetrahedron, Octahedron, Icosahedron, Dodecahedron).
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/threed_primitives')
canvas.set_background()

T = 12

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='3D Primitives & Platonic Solids', x=960, y=50,
             font_size=44, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1)
title.fadeout(10.5, 11.5)

# =====================================================================
# Phase 1 (0-4s): 3D Primitives — Line3D, Dot3D, Arrow3D, Text3D
# =====================================================================

phase1_label = Text(text='Phase 1: 3D Primitives', x=960, y=90,
                    font_size=22, fill='#888888', stroke_width=0,
                    text_anchor='middle', creation=0)
phase1_label.fadein(0.3, 1.3)
phase1_label.fadeout(3.5, 4.0)

axes1 = ThreeDAxes(
    x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3),
    cx=960, cy=580, scale=100,
    phi=math.radians(70), theta=math.radians(-40),
    show_ticks=True, show_labels=True, show_grid=False,
    x_label='x', y_label='y', z_label='z',
    creation=0,
)
axes1.set_light_direction(0.3, -0.5, 0.8)

# Line3D: a diagonal line
line3d = Line3D(start=(-2, -2, -1), end=(2, 2, 1),
                stroke='#FF6470', stroke_width=3, creation=0)
line3d.show.set(0, 0.5, False)
line3d.show.set_onward(0.5, True)
axes1.add_3d(line3d)

# Dot3D: several dots at key positions
dots_data = [
    ((-2, -2, -1), '#FF6470', 'Start'),
    ((2, 2, 1), '#FF6470', 'End'),
    ((0, 0, 0), '#FFFFFF', 'Origin'),
    ((1, -1, 2), '#83C167', 'P1'),
    ((-1, 2, -1), '#FCBE55', 'P2'),
]

dots_3d = []
texts_3d = []
for i, (pt, color, label) in enumerate(dots_data):
    dot = Dot3D(point=pt, radius=6, fill=color, creation=0)
    dot.show.set(0, 0.8 + i * 0.2, False)
    dot.show.set_onward(0.8 + i * 0.2, True)
    axes1.add_3d(dot)
    dots_3d.append(dot)

    txt = Text3D(text=label, point=(pt[0], pt[1], pt[2] + 0.4),
                 font_size=14, fill=color, creation=0)
    txt.show.set(0, 0.8 + i * 0.2, False)
    txt.show.set_onward(0.8 + i * 0.2, True)
    axes1.add_3d(txt)
    texts_3d.append(txt)

# Arrow3D: arrows from origin to P1 and P2
arrow1 = Arrow3D(start=(0, 0, 0), end=(1, -1, 2),
                 stroke='#83C167', stroke_width=2,
                 tip_length=14, tip_radius=5, creation=0)
arrow1.show.set(0, 1.5, False)
arrow1.show.set_onward(1.5, True)
axes1.add_3d(arrow1)

arrow2 = Arrow3D(start=(0, 0, 0), end=(-1, 2, -1),
                 stroke='#FCBE55', stroke_width=2,
                 tip_length=14, tip_radius=5, creation=0)
arrow2.show.set(0, 1.8, False)
arrow2.show.set_onward(1.8, True)
axes1.add_3d(arrow2)

# ParametricCurve3D: a helix
helix = ParametricCurve3D(
    func=lambda t: (1.5 * math.cos(t * math.tau * 2),
                    1.5 * math.sin(t * math.tau * 2),
                    -2 + 4 * t),
    t_range=(0, 1), num_points=120,
    stroke='#58C4DD', stroke_width=2, creation=0,
)
helix.show.set(0, 2.2, False)
helix.show.set_onward(2.2, True)
axes1.add_3d(helix)

helix_label = Text3D(text='Helix', point=(1.5, 0, 2.5),
                     font_size=16, fill='#58C4DD', creation=0)
helix_label.show.set(0, 2.5, False)
helix_label.show.set_onward(2.5, True)
axes1.add_3d(helix_label)

# Camera animation for phase 1
axes1.set_camera_orientation(2.0, 4.0,
                             phi=math.radians(60),
                             theta=math.radians(-20))

# Hide axes1 after phase 1
axes1.fadeout(3.5, 4.0)
axes1.show.set_onward(4.0, False)

# =====================================================================
# Phase 2 (4-8s): 3D Solids — Cube, Cylinder3D, Cone3D, Torus3D, Prism3D
# =====================================================================

phase2_label = Text(text='Phase 2: 3D Solids', x=960, y=90,
                    font_size=22, fill='#888888', stroke_width=0,
                    text_anchor='middle', creation=0)
phase2_label.set_opacity(0, 0)
phase2_label.set_opacity(4.0, 4.5, 1.0)
phase2_label.fadeout(7.5, 8.0)

axes2 = ThreeDAxes(
    x_range=(-4, 4), y_range=(-4, 4), z_range=(-3, 3),
    cx=960, cy=580, scale=90,
    phi=math.radians(68), theta=math.radians(-35),
    show_ticks=False, show_labels=False, show_grid=False,
    x_label=None, y_label=None, z_label=None,
    creation=0,
)
axes2.set_light_direction(0.4, -0.3, 0.8)
axes2.show.set(0, 4.0, False)
axes2.show.set_onward(4.0, True)

# Cube — blue
cube_faces = Cube(
    side_length=1.4, center=(-2.5, -2.5, 0),
    fill_color='#58C4DD', stroke_color='#1a5577',
    stroke_width=0.5, fill_opacity=0.0, creation=0,
)
for face in cube_faces:
    axes2.add_surface(face)
    face.show.set(0, 4.0, False)
    face.show.set_onward(4.0, True)

# Fade cube in
for face in cube_faces:
    _orig = face.to_patches
    def _make_fadein_cube(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 4.0:
                return []
            frac = min((time - 4.0) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_cube(_orig, face)

cube_label = Text3D(text='Cube', point=(-2.5, -2.5, 1.2),
                    font_size=16, fill='#58C4DD', creation=0)
cube_label.show.set(0, 4.5, False)
cube_label.show.set_onward(4.5, True)
axes2.add_3d(cube_label)

# Cylinder3D — green
cylinder = Cylinder3D(
    radius=0.8, height=1.8, center=(2.5, -2.5, 0),
    resolution=(20, 8),
    fill_color='#83C167', stroke_color='#2d5520',
    stroke_width=0.3, fill_opacity=0.0, creation=0,
)
cylinder.set_checkerboard('#83C167', '#A0D680')
axes2.add_surface(cylinder)
cylinder.show.set(0, 4.5, False)
cylinder.show.set_onward(4.5, True)

_orig_cyl = cylinder.to_patches
def _fadein_cyl(axes_ref, time):
    if time < 4.5:
        return []
    frac = min((time - 4.5) / 0.8, 1.0)
    cylinder._fill_opacity = 0.85 * frac
    return _orig_cyl(axes_ref, time)
cylinder.to_patches = _fadein_cyl

cyl_label = Text3D(text='Cylinder', point=(2.5, -2.5, 1.5),
                   font_size=16, fill='#83C167', creation=0)
cyl_label.show.set(0, 5.0, False)
cyl_label.show.set_onward(5.0, True)
axes2.add_3d(cyl_label)

# Cone3D — orange
cone = Cone3D(
    radius=0.9, height=2.0, center=(-2.5, 2.5, 0),
    resolution=(20, 8),
    fill_color='#FCBE55', stroke_color='#8B6914',
    stroke_width=0.3, fill_opacity=0.0, creation=0,
)
cone.set_checkerboard('#FCBE55', '#FFD98A')
axes2.add_surface(cone)
cone.show.set(0, 5.0, False)
cone.show.set_onward(5.0, True)

_orig_cone = cone.to_patches
def _fadein_cone(axes_ref, time):
    if time < 5.0:
        return []
    frac = min((time - 5.0) / 0.8, 1.0)
    cone._fill_opacity = 0.85 * frac
    return _orig_cone(axes_ref, time)
cone.to_patches = _fadein_cone

cone_label = Text3D(text='Cone', point=(-2.5, 2.5, 1.5),
                    font_size=16, fill='#FCBE55', creation=0)
cone_label.show.set(0, 5.5, False)
cone_label.show.set_onward(5.5, True)
axes2.add_3d(cone_label)

# Torus3D — red
torus = Torus3D(
    major_radius=1.0, minor_radius=0.3, center=(2.5, 2.5, 0),
    resolution=(20, 10),
    fill_color='#FC6255', stroke_color='#7A2020',
    stroke_width=0.2, fill_opacity=0.0, creation=0,
)
torus.set_checkerboard('#FC6255', '#FF8877')
axes2.add_surface(torus)
torus.show.set(0, 5.5, False)
torus.show.set_onward(5.5, True)

_orig_torus = torus.to_patches
def _fadein_torus(axes_ref, time):
    if time < 5.5:
        return []
    frac = min((time - 5.5) / 0.8, 1.0)
    torus._fill_opacity = 0.85 * frac
    return _orig_torus(axes_ref, time)
torus.to_patches = _fadein_torus

torus_label = Text3D(text='Torus', point=(2.5, 2.5, 0.8),
                     font_size=16, fill='#FC6255', creation=0)
torus_label.show.set(0, 6.0, False)
torus_label.show.set_onward(6.0, True)
axes2.add_3d(torus_label)

# Prism3D (hexagonal) — purple, at the center
prism_faces = Prism3D(
    n_sides=6, radius=0.8, height=1.6, center=(0, 0, 0),
    fill_color='#B070DD', stroke_color='#5A2E7A',
    stroke_width=0.5, fill_opacity=0.0, creation=0,
)
for face in prism_faces:
    axes2.add_surface(face)
    face.show.set(0, 6.0, False)
    face.show.set_onward(6.0, True)

for face in prism_faces:
    _orig_p = face.to_patches
    def _make_fadein_prism(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 6.0:
                return []
            frac = min((time - 6.0) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_prism(_orig_p, face)

prism_label = Text3D(text='Prism', point=(0, 0, 1.3),
                     font_size=16, fill='#B070DD', creation=0)
prism_label.show.set(0, 6.5, False)
prism_label.show.set_onward(6.5, True)
axes2.add_3d(prism_label)

# Ambient camera rotation for phase 2
axes2.begin_ambient_camera_rotation(start=4.0, end=8.0, rate=0.5)

# Fade out axes2 at end of phase 2
axes2.fadeout(7.5, 8.0)
axes2.show.set_onward(8.0, False)

# =====================================================================
# Phase 3 (8-12s): Platonic Solids
# =====================================================================

phase3_label = Text(text='Phase 3: Platonic Solids', x=960, y=90,
                    font_size=22, fill='#888888', stroke_width=0,
                    text_anchor='middle', creation=0)
phase3_label.set_opacity(0, 0)
phase3_label.set_opacity(8.0, 8.5, 1.0)
phase3_label.fadeout(10.5, 11.5)

axes3 = ThreeDAxes(
    x_range=(-5, 5), y_range=(-5, 5), z_range=(-4, 4),
    cx=960, cy=580, scale=80,
    phi=math.radians(65), theta=math.radians(-30),
    show_ticks=False, show_labels=False, show_grid=False,
    x_label=None, y_label=None, z_label=None,
    creation=0,
)
axes3.set_light_direction(0.3, -0.6, 0.7)
axes3.show.set(0, 8.0, False)
axes3.show.set_onward(8.0, True)

# Tetrahedron — cyan, upper-left
tetra_faces = Tetrahedron(
    cx=-3, cy=-3, cz=0, size=1.2,
    fill_color='#58C4DD', stroke_color='#FFFFFF',
    stroke_width=1.5, fill_opacity=0.0, creation=0,
)
for face in tetra_faces:
    axes3.add_surface(face)
    face.show.set(0, 8.0, False)
    face.show.set_onward(8.0, True)

for face in tetra_faces:
    _orig_t = face.to_patches
    def _make_fadein_tetra(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 8.0:
                return []
            frac = min((time - 8.0) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_tetra(_orig_t, face)

tetra_label = Text3D(text='Tetrahedron', point=(-3, -3, 2.0),
                     font_size=15, fill='#58C4DD', creation=0)
tetra_label.show.set(0, 8.5, False)
tetra_label.show.set_onward(8.5, True)
axes3.add_3d(tetra_label)

# Octahedron — green, upper-right
octa_faces = Octahedron(
    cx=3, cy=-3, cz=0, size=1.3,
    fill_color='#83C167', stroke_color='#FFFFFF',
    stroke_width=1.5, fill_opacity=0.0, creation=0,
)
for face in octa_faces:
    axes3.add_surface(face)
    face.show.set(0, 8.5, False)
    face.show.set_onward(8.5, True)

for face in octa_faces:
    _orig_o = face.to_patches
    def _make_fadein_octa(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 8.5:
                return []
            frac = min((time - 8.5) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_octa(_orig_o, face)

octa_label = Text3D(text='Octahedron', point=(3, -3, 2.0),
                    font_size=15, fill='#83C167', creation=0)
octa_label.show.set(0, 9.0, False)
octa_label.show.set_onward(9.0, True)
axes3.add_3d(octa_label)

# Icosahedron — orange, lower-left
icosa_faces = Icosahedron(
    cx=-3, cy=3, cz=0, size=1.0,
    fill_color='#FCBE55', stroke_color='#FFFFFF',
    stroke_width=1.0, fill_opacity=0.0, creation=0,
)
for face in icosa_faces:
    axes3.add_surface(face)
    face.show.set(0, 9.0, False)
    face.show.set_onward(9.0, True)

for face in icosa_faces:
    _orig_i = face.to_patches
    def _make_fadein_icosa(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 9.0:
                return []
            frac = min((time - 9.0) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_icosa(_orig_i, face)

icosa_label = Text3D(text='Icosahedron', point=(-3, 3, 2.0),
                     font_size=15, fill='#FCBE55', creation=0)
icosa_label.show.set(0, 9.5, False)
icosa_label.show.set_onward(9.5, True)
axes3.add_3d(icosa_label)

# Dodecahedron — red/pink, lower-right
dodeca_faces = Dodecahedron(
    cx=3, cy=3, cz=0, size=0.9,
    fill_color='#FC6255', stroke_color='#FFFFFF',
    stroke_width=1.0, fill_opacity=0.0, creation=0,
)
for face in dodeca_faces:
    axes3.add_surface(face)
    face.show.set(0, 9.5, False)
    face.show.set_onward(9.5, True)

for face in dodeca_faces:
    _orig_d = face.to_patches
    def _make_fadein_dodeca(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 9.5:
                return []
            frac = min((time - 9.5) / 0.8, 1.0)
            f._fill_opacity = 0.85 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein_dodeca(_orig_d, face)

dodeca_label = Text3D(text='Dodecahedron', point=(3, 3, 2.0),
                      font_size=15, fill='#FC6255', creation=0)
dodeca_label.show.set(0, 10.0, False)
dodeca_label.show.set_onward(10.0, True)
axes3.add_3d(dodeca_label)

# Ambient camera rotation for phase 3
axes3.begin_ambient_camera_rotation(start=8.0, end=12.0, rate=0.4)

# Fade out axes3 toward the end
axes3.fadeout(10.5, 11.5)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axes1)
canvas.add(axes2)
canvas.add(axes3)
canvas.add(title)
canvas.add(phase1_label, phase2_label, phase3_label)

canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
