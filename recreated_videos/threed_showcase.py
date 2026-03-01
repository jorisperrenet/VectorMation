"""3D Visualization Showcase — Surfaces, camera rotation, and 3D primitives.

Demonstrates ThreeDAxes with surfaces, ambient camera rotation,
3D primitives (Sphere, Cube, Torus), and animated camera orientation.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/threed_showcase')
canvas.set_background()

T = 12

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='3D Visualization Showcase', x=960, y=50,
             font_size=44, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1)
title.fadeout(10.5, 11.5)

subtitle = Text(text='Surfaces, Primitives & Camera Motion',
                x=960, y=90, font_size=22, fill='#888888',
                stroke_width=0, text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)
subtitle.fadeout(10.5, 11.5)

# ── Equation label ──────────────────────────────────────────────────
eq_label = Text(text='z = x² − y²  (saddle surface)', x=170, y=180,
                font_size=22, fill='#58C4DD', stroke_width=0,
                text_anchor='start', creation=0)
eq_label.fadein(1.0, 2.0)
eq_label.fadeout(10.0, 11.0)

dot_indicator = Circle(r=6, cx=145, cy=183, fill='#58C4DD',
                       stroke_width=0, creation=0)
dot_indicator.fadein(1.0, 2.0)
dot_indicator.fadeout(10.0, 11.0)

# ── Primitives label (appears at t=6) ──────────────────────────────
prim_label = Text(text='3D Primitives: Sphere, Cube, Torus', x=170, y=216,
                  font_size=22, fill='#FCBE55', stroke_width=0,
                  text_anchor='start', creation=0)
prim_label.set_opacity(0, 0)
prim_label.set_opacity(6.0, 7.0, 1.0)
prim_label.fadeout(10.0, 11.0)

prim_dot = Circle(r=6, cx=145, cy=219, fill='#FCBE55',
                  stroke_width=0, creation=0)
prim_dot.set_opacity(0, 0)
prim_dot.set_opacity(6.0, 7.0, 1.0)
prim_dot.fadeout(10.0, 11.0)

# ── 3D Axes ──────────────────────────────────────────────────────────
axes = ThreeDAxes(
    x_range=(-3, 3), y_range=(-3, 3), z_range=(-4, 4),
    cx=960, cy=560, scale=110,
    phi=math.radians(72), theta=math.radians(-50),
    show_ticks=True, show_labels=True, show_grid=True,
    x_label='x', y_label='y', z_label='z',
    creation=0,
)
axes.set_light_direction(0.3, -0.5, 0.8)

# ── Phase 1 (0-3s): Saddle surface z = x² - y² with grid plane ─────
axes.add_grid_plane(plane='xy', step=1, color='#444444', opacity=0.2)

def saddle(x, y):
    return x * x - y * y

surface = axes.plot_surface(
    saddle,
    u_range=(-2, 2), v_range=(-2, 2),
    resolution=(20, 20),
    fill_color='#58C4DD',
    stroke_color='#1a5577',
    stroke_width=0.3,
    fill_opacity=0.0,
    creation=0,
)
surface.set_checkerboard('#58C4DD', '#83D9F0')

# Fade the surface in over 0-2s
_orig_surface_patches = surface.to_patches
def _fadein_surface(axes_ref, time):
    if time < 0.5:
        return []
    frac = min((time - 0.5) / 1.5, 1.0)
    surface._fill_opacity = 0.85 * frac
    return _orig_surface_patches(axes_ref, time)
surface.to_patches = _fadein_surface

# Initial camera settle
axes.set_camera_orientation(0, 1.5,
                            phi=math.radians(65),
                            theta=math.radians(-30))

# ── Phase 2 (3-6s): Ambient camera rotation ─────────────────────────
axes.begin_ambient_camera_rotation(start=3.0, end=6.0, rate=0.5)

# ── Phase 3 (6-9s): Add 3D primitives ───────────────────────────────
# Sphere — positioned to the left
sphere = Sphere3D(
    radius=0.8, center=(-2.2, -2.2, 0),
    fill_color='#FC6255', fill_opacity=0.0,
    stroke_width=0.2, creation=0,
)
sphere.set_checkerboard('#FC6255', '#FF8877')
axes.add_surface(sphere)
sphere.show.set(0, 6.0, False)
sphere.show.set_onward(6.0, True)

_orig_sphere_patches = sphere.to_patches
def _fadein_sphere(axes_ref, time):
    if time < 6.0:
        return []
    frac = min((time - 6.0) / 1.0, 1.0)
    sphere._fill_opacity = 0.9 * frac
    return _orig_sphere_patches(axes_ref, time)
sphere.to_patches = _fadein_sphere

# Cube — positioned to the right
cube_faces = Cube(
    side_length=1.4, center=(2.2, -2.2, 0),
    fill_color='#83C167', fill_opacity=0.0,
    stroke_width=0.3, creation=0,
)
for face in cube_faces:
    axes.add_surface(face)
    face.show.set(0, 6.5, False)
    face.show.set_onward(6.5, True)

# Fade cube faces in
for face in cube_faces:
    _orig_face_patches = face.to_patches
    def _make_fadein(orig_fn, f):
        def _fadein(axes_ref, time):
            if time < 6.5:
                return []
            frac = min((time - 6.5) / 1.0, 1.0)
            f._fill_opacity = 0.8 * frac
            return orig_fn(axes_ref, time)
        return _fadein
    face.to_patches = _make_fadein(_orig_face_patches, face)

# Torus — positioned above center
torus = Torus3D(
    major_radius=1.0, minor_radius=0.3, center=(0, 2.5, 0),
    resolution=(20, 10),
    fill_color='#FCBE55', fill_opacity=0.0,
    stroke_width=0.2, creation=0,
)
torus.set_checkerboard('#FCBE55', '#FFD98A')
axes.add_surface(torus)
torus.show.set(0, 7.0, False)
torus.show.set_onward(7.0, True)

_orig_torus_patches = torus.to_patches
def _fadein_torus(axes_ref, time):
    if time < 7.0:
        return []
    frac = min((time - 7.0) / 1.0, 1.0)
    torus._fill_opacity = 0.9 * frac
    return _orig_torus_patches(axes_ref, time)
torus.to_patches = _fadein_torus

# SurfaceMesh wireframe overlay on the saddle surface (appears at t=7.5)
mesh = SurfaceMesh(
    surface, resolution=(12, 12),
    stroke_color='#ffffff', stroke_width=0.8, stroke_opacity=0.5,
    creation=0,
)
axes.add_surface(mesh)
mesh.show.set(0, 7.5, False)
mesh.show.set_onward(7.5, True)

# Continue ambient rotation while primitives appear
axes.begin_ambient_camera_rotation(start=6.0, end=9.0, rate=0.4)

# ── Phase 4 (9-12s): Camera to 'top' preset, fade out ───────────────
axes.set_camera_preset('top', start=9.0, end=11.0)

# Fade out surfaces toward the end
def _make_fadeout(orig_fn, surf, appear_time, full_opacity):
    def _fadeout(axes_ref, time):
        if time < appear_time:
            return []
        if time >= 10.5:
            frac = max(0, 1.0 - (time - 10.5) / 1.5)
            surf._fill_opacity = full_opacity * frac
            if frac <= 0:
                return []
        return orig_fn(axes_ref, time)
    return _fadeout

surface.to_patches = _make_fadeout(surface.to_patches, surface, 0.5, 0.85)
sphere.to_patches = _make_fadeout(sphere.to_patches, sphere, 6.0, 0.9)
torus.to_patches = _make_fadeout(torus.to_patches, torus, 7.0, 0.9)
mesh.show.set(10.5, 10.51, False)
for face in cube_faces:
    face.to_patches = _make_fadeout(face.to_patches, face, 6.5, 0.8)

# Fade out the axes labels/ticks themselves
axes.fadeout(10.5, 11.5)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axes)
canvas.add(title, subtitle)
canvas.add(eq_label, dot_indicator)
canvas.add(prim_label, prim_dot)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
