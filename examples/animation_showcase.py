"""Showcase of VectorMation animation methods — only animations that change values over time."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animation_showcase', width=1200, height=1700)
canvas.set_background(fill='#1a1a2e')

# Layout: 5 columns, 6 rows
cols = [120, 360, 600, 840, 1080]
rows = [190, 430, 670, 910, 1150, 1390]
label_kw = dict(font_size=13, fill='#aaa', stroke_width=0, text_anchor='middle')
header_kw = dict(font_size=22, fill='#58C4DD', stroke_width=0, text_anchor='middle')

def lbl(text, col, row, t):
    l = Text(text, x=cols[col], y=rows[row] + 90, **label_kw)
    canvas.add_objects(l)
    l.fadein(start=t, end=t + 0.3)

def section(text, row, t):
    s = Text(text, x=600, y=rows[row] - 90, **header_kw)
    canvas.add_objects(s)
    s.fadein(start=t, end=t + 0.3)

# Title
title = Text('Animation Showcase', x=600, y=55, font_size=48,
             text_anchor='middle', fill='#58C4DD', stroke_width=0)
canvas.add_objects(title)
title.fadein(start=0, end=0.5)

# =============================================================================
# Row 0 — Appearance
# =============================================================================
t = 1.0
section('Appearance', 0, t)

# fadein
fi = Circle(r=35, cx=cols[0], cy=rows[0], fill='#FC6255', fill_opacity=0.8, stroke='#FF8080', stroke_width=4)
canvas.add_objects(fi)
fi.fadein(start=t, end=t + 1.0)
lbl('fadein', 0, 0, t)

# fadeout
fo = Circle(r=35, cx=cols[1], cy=rows[0], fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4)
canvas.add_objects(fo)
fo.fadein(start=t, end=t + 0.3)
fo.fadeout(start=t + 0.5, end=t + 1.5)
lbl('fadeout', 1, 0, t + 0.5)

# grow_from_center
gfc = Star(n=5, outer_radius=40, cx=cols[2], cy=rows[0],
           fill='#F0AC5F', fill_opacity=0.8, stroke='#FFD700', stroke_width=4)
canvas.add_objects(gfc)
gfc.grow_from_center(start=t + 0.5, end=t + 1.5)
lbl('grow_from_center', 2, 0, t + 0.5)

# shrink_to_center
stc = EquilateralTriangle(side_length=65, cx=cols[3], cy=rows[0],
                           fill='#E8C11C', fill_opacity=0.8, stroke='#FFD700', stroke_width=4)
canvas.add_objects(stc)
stc.fadein(start=t, end=t + 0.3)
stc.shrink_to_center(start=t + 1.0, end=t + 2.0)
lbl('shrink_to_center', 3, 0, t + 1.0)

# write
wr = VCollection(
    Rectangle(22, 22, x=cols[4] - 30 - 11, y=rows[0] - 11,
              fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4),
    Circle(r=11, cx=cols[4], cy=rows[0],
           fill='#58C4DD', fill_opacity=0.8, stroke='#88D4EE', stroke_width=4),
    Star(n=5, outer_radius=13, cx=cols[4] + 30, cy=rows[0],
         fill='#F0AC5F', fill_opacity=0.8, stroke='#FFD700', stroke_width=4),
)
canvas.add_objects(wr)
wr.write(start=t + 1.0, end=t + 2.5)
lbl('write', 4, 0, t + 1.0)

# =============================================================================
# Row 1 — Drawing & Text
# =============================================================================
t = 4.0
section('Drawing & Text', 1, t)

# create
cr = RegularPolygon(5, radius=35, cx=cols[0], cy=rows[1],
                     fill='#9A72AC', fill_opacity=0.8, stroke='#B189C6', stroke_width=4)
canvas.add_objects(cr)
cr_path = cr.create(start=t, end=t + 1.5)
canvas.add_objects(cr_path)
lbl('create', 0, 1, t)

# draw_along
da = Path(f'M{cols[1]-35},{rows[1]+20} C{cols[1]-35},{rows[1]-40} {cols[1]+35},{rows[1]-40} {cols[1]+35},{rows[1]+20}',
          stroke='#58C4DD', stroke_width=4, fill_opacity=0)
canvas.add_objects(da)
da.draw_along(start=t + 0.5, end=t + 2.0)
lbl('draw_along', 1, 1, t + 0.5)

# typing
ty = Text('Hello!', x=cols[2], y=rows[1] + 8, text_anchor='middle',
          font_size=28, fill='#83C167', stroke_width=0)
canvas.add_objects(ty)
ty.typing(start=t + 1.0, end=t + 2.5)
lbl('typing', 2, 1, t + 1.0)

# CountAnimation
ca = CountAnimation(start_val=0, end_val=42, start=t + 1.5, end=t + 2.5,
                    x=cols[3], y=rows[1] + 12, text_anchor='middle',
                    font_size=36, fill='#FC6255', stroke_width=0)
canvas.add_objects(ca)
ca.fadein(start=t + 1.5, end=t + 1.8)
lbl('CountAnimation', 3, 1, t + 1.5)

# stagger (each child grows one after another)
stg = VCollection(
    Dot(r=12, cx=cols[4] - 30, cy=rows[1], fill='#FC6255'),
    Dot(r=12, cx=cols[4] - 10, cy=rows[1], fill='#F0AC5F'),
    Dot(r=12, cx=cols[4] + 10, cy=rows[1], fill='#E8C11C'),
    Dot(r=12, cx=cols[4] + 30, cy=rows[1], fill='#83C167'),
)
canvas.add_objects(stg)
stg.stagger('grow_from_center', delay=0.3, start=t + 2.0, end=t + 2.5)
lbl('stagger', 4, 1, t + 2.0)

# =============================================================================
# Row 2 — Movement
# =============================================================================
t = 7.5
section('Movement', 2, t)

# shift
sh = Dot(r=10, cx=cols[0] - 30, cy=rows[2], fill='#58C4DD')
canvas.add_objects(sh)
sh.fadein(start=t, end=t + 0.3)
sh.shift(dx=60, dy=0, start=t + 0.3, end=t + 1.5)
lbl('shift', 0, 2, t)

# move_to
mt = Dot(r=10, cx=cols[1] - 30, cy=rows[2] + 20, fill='#FC6255')
canvas.add_objects(mt)
mt.fadein(start=t + 0.3, end=t + 0.6)
mt.move_to(cols[1] + 30, rows[2] - 20, start=t + 0.6, end=t + 1.8)
lbl('move_to', 1, 2, t + 0.3)

# center_to_pos
ctp = Rectangle(30, 30, x=cols[2] - 30, y=rows[2] + 16,
                fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4)
canvas.add_objects(ctp)
ctp.fadein(start=t + 0.6, end=t + 0.9)
ctp.center_to_pos(cols[2] + 16, rows[2] - 16, start=t + 0.9, end=t + 2.0)
lbl('center_to_pos', 2, 2, t + 0.6)

# along_path
ap = Dot(r=8, cx=cols[3] - 40, cy=rows[2], fill='#F0AC5F')
ap_path_d = f'M{cols[3]-40},{rows[2]} C{cols[3]-40},{rows[2]-60} {cols[3]+40},{rows[2]-60} {cols[3]+40},{rows[2]}'
ap_guide = Path(ap_path_d, stroke='#444', stroke_width=1, fill_opacity=0)
canvas.add_objects(ap_guide, ap)
ap_guide.fadein(start=t + 0.9, end=t + 1.1)
ap.fadein(start=t + 0.9, end=t + 1.1)
ap.along_path(start=t + 1.2, end=t + 2.5, path_d=ap_path_d)
lbl('along_path', 3, 2, t + 0.9)

# set_onward oscillating dot — custom per-frame animation
upd_dot = Dot(r=10, cx=cols[4], cy=rows[2], fill='#E8C11C')
canvas.add_objects(upd_dot)
upd_dot.fadein(start=t + 1.2, end=t + 1.5)
_upd_t0 = t + 1.5
upd_dot.styling.dy.set_onward(_upd_t0, lambda t: 25 * math.sin((t - _upd_t0) * 4))
upd_dot.styling.dy.set_onward(t + 3.5, 0)
lbl('set_onward', 4, 2, t + 1.2)

# =============================================================================
# Row 3 — Scaling & Rotation
# =============================================================================
t = 11.0
section('Scaling & Rotation', 3, t)

# scale
sc = RegularPolygon(6, radius=25, cx=cols[0], cy=rows[3],
                     fill='#FC6255', fill_opacity=0.8, stroke='#FF8080', stroke_width=4)
canvas.add_objects(sc)
sc.fadein(start=t, end=t + 0.3)
sc.scale(1.6, start=t + 0.3, end=t + 1.5)
lbl('scale', 0, 3, t)

# stretch
str_r = Rectangle(50, 30, x=cols[1] - 25, y=rows[3] - 16,
                  fill='#9A72AC', fill_opacity=0.8, stroke='#B189C6', stroke_width=4)
canvas.add_objects(str_r)
str_r.fadein(start=t + 0.3, end=t + 0.6)
str_r.stretch(x_factor=1.8, y_factor=0.6, start=t + 0.6, end=t + 1.8)
lbl('stretch', 1, 3, t + 0.3)

# rotate_to
rto = Rectangle(50, 30, x=cols[2] - 25, y=rows[3] - 16,
                fill='#FC6255', fill_opacity=0.8, stroke='#FF8080', stroke_width=4)
canvas.add_objects(rto)
rto.fadein(start=t + 0.6, end=t + 0.9)
rto.rotate_to(start=t + 0.9, end=t + 2.0, degrees=45)
lbl('rotate_to', 2, 3, t + 0.6)

# rotate_by
rby = Star(n=4, outer_radius=30, cx=cols[3], cy=rows[3],
           fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4)
canvas.add_objects(rby)
rby.fadein(start=t + 0.9, end=t + 1.2)
rby.rotate_by(start=t + 1.2, end=t + 2.3, degrees=180)
lbl('rotate_by', 3, 3, t + 0.9)

# spin
spn = RegularPolygon(6, radius=30, cx=cols[4], cy=rows[3],
                      fill='#9A72AC', fill_opacity=0.8, stroke='#B189C6', stroke_width=4)
canvas.add_objects(spn)
spn.fadein(start=t + 1.2, end=t + 1.5)
spn.spin(start=t + 1.5, end=t + 3.0, degrees=360)
lbl('spin', 4, 3, t + 1.2)

# =============================================================================
# Row 4 — Effects
# =============================================================================
t = 14.5
section('Effects', 4, t)

# indicate
ind = Circle(r=30, cx=cols[0], cy=rows[4],
             fill='#FC6255', fill_opacity=0.8, stroke='#FF8080', stroke_width=4)
canvas.add_objects(ind)
ind.fadein(start=t, end=t + 0.3)
ind.indicate(start=t + 0.5, end=t + 1.5, scale_factor=1.3)
lbl('indicate', 0, 4, t)

# flash
fl = Circle(r=30, cx=cols[1], cy=rows[4],
            fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD', stroke_width=4)
canvas.add_objects(fl)
fl.fadein(start=t + 0.3, end=t + 0.6)
fl.flash(start=t + 0.8, end=t + 1.8, color='#FFFF00')
lbl('flash', 1, 4, t + 0.3)

# pulse
pu = Dot(r=14, cx=cols[2], cy=rows[4], fill='#83C167')
canvas.add_objects(pu)
pu.fadein(start=t + 0.6, end=t + 0.9)
pu.pulse(start=t + 1.0, end=t + 2.0, scale_factor=2.0)
lbl('pulse', 2, 4, t + 0.6)

# wiggle
wig = RoundedRectangle(60, 40, x=cols[3] - 30, y=rows[4] - 20,
                        corner_radius=6, fill='#E8C11C', fill_opacity=0.8,
                        stroke='#FFD700', stroke_width=4)
canvas.add_objects(wig)
wig.fadein(start=t + 0.9, end=t + 1.2)
wig.wiggle(start=t + 1.3, end=t + 2.3, amplitude=12, n_wiggles=5)
lbl('wiggle', 3, 4, t + 0.9)

# circumscribe
circ_obj = Star(n=5, outer_radius=28, cx=cols[4], cy=rows[4],
                fill='#9A72AC', fill_opacity=0.8, stroke='#B189C6', stroke_width=4)
canvas.add_objects(circ_obj)
circ_obj.fadein(start=t + 1.2, end=t + 1.5)
circ_rect = circ_obj.circumscribe(start=t + 1.6, end=t + 2.8)
canvas.add_objects(circ_rect)
lbl('circumscribe', 4, 4, t + 1.2)

# =============================================================================
# Row 5 — Transforms
# =============================================================================
t = 18.0
section('Transforms', 5, t)

# MorphObject
mo_from = Circle(r=30, cx=cols[0], cy=rows[5],
                 fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD', stroke_width=4)
mo_from.fadein(start=t, end=t + 0.3)
mo_to = Rectangle(55, 55, x=cols[0] - 28, y=rows[5] - 28,
                  fill='#E8C11C', fill_opacity=0.8, stroke='#FFD700', stroke_width=4)
morph = MorphObject(mo_from, mo_to, start=t + 0.5, end=t + 2.0)
canvas.add_objects(mo_from, morph, mo_to)
lbl('MorphObject', 0, 5, t)

# fade_transform
ft_src = Circle(r=25, cx=cols[1], cy=rows[5],
                fill='#FC6255', fill_opacity=0.8, stroke='#FF8080', stroke_width=4)
ft_tgt = Star(n=5, outer_radius=30, cx=cols[1], cy=rows[5],
              fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4)
canvas.add_objects(ft_src, ft_tgt)
ft_src.fadein(start=t + 0.3, end=t + 0.6)
VObject.fade_transform(ft_src, ft_tgt, start=t + 0.8, end=t + 2.0)
lbl('fade_transform', 1, 5, t + 0.3)

# swap
sw_a = Circle(r=18, cx=cols[2] - 25, cy=rows[5],
              fill='#F0AC5F', fill_opacity=0.8, stroke='#FFD700', stroke_width=4)
sw_b = Rectangle(30, 30, x=cols[2] + 10, y=rows[5] - 16,
                 fill='#9A72AC', fill_opacity=0.8, stroke='#B189C6', stroke_width=4)
canvas.add_objects(sw_a, sw_b)
sw_a.fadein(start=t + 0.6, end=t + 0.9)
sw_b.fadein(start=t + 0.6, end=t + 0.9)
VObject.swap(sw_a, sw_b, start=t + 1.0, end=t + 2.2)
lbl('swap', 2, 5, t + 0.6)

# always_rotate (with explicit center)
ar = Star(n=5, outer_radius=28, cx=cols[3], cy=rows[5],
          fill='#F0AC5F', fill_opacity=0.8, stroke='#FFD700', stroke_width=4)
canvas.add_objects(ar)
ar.fadein(start=t + 0.9, end=t + 1.2)
ar.always_rotate(start=t + 1.2, end=t + 3.5, degrees_per_second=120, cx=cols[3], cy=rows[5])
lbl('always_rotate', 3, 5, t + 0.9)

# scale_to
sct = Circle(r=20, cx=cols[4], cy=rows[5],
             fill='#83C167', fill_opacity=0.8, stroke='#A6CF8C', stroke_width=4)
canvas.add_objects(sct)
sct.fadein(start=t + 1.2, end=t + 1.5)
sct.scale_to(start=t + 1.5, end=t + 2.8, factor=2.0)
lbl('scale_to', 4, 5, t + 1.2)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/animation_showcase.mp4', fps=30, end=22)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
