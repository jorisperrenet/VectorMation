"""Geometry Showcase — Polygon decomposition, circle constructions, rectangle operations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/geometry_showcase')
canvas.set_background()
T = 24.0

# =============================================================================
# Phase 1 (0-6s): Polygon Decomposition
# =============================================================================

title1 = TexObject(r'Polygon Decomposition', x=960, y=70, font_size=48,
                   fill='#FFFFFF', stroke_width=0, anchor='center')
title1.write(0.0, 0.8)
title1.fadeout(5.5, 6.0)
canvas.add(title1)

# Hexagon (left)
hexagon = RegularPolygon(6, radius=140, cx=480, cy=400,
                         fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=3)
hexagon.grow_from_center(start=0.3, end=1.0)
hexagon.always_rotate(start=1.0, end=5.5, degrees_per_second=15)
hexagon.fadeout(5.5, 6.0)
canvas.add(hexagon)

hex_label = TexObject(r'Regular Hexagon', x=480, y=590, font_size=22,
                      fill='#FFFFFF', stroke_width=0, anchor='center')
hex_label.fadein(0.5, 1.0)
hex_label.fadeout(5.5, 6.0)
canvas.add(hex_label)

# Colored edges — batch with VCollection + stagger
edges = hexagon.get_edges()
edge_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC']
edge_coll = VCollection(creation=0)
for i, edge in enumerate(edges):
    edge.set_stroke(color=edge_colors[i % len(edge_colors)], width=4)
    edge_coll.add(edge)
edge_coll.stagger_fadein(start=1.2, end=2.2)
edge_coll.fadeout(5.5, 6.0)
canvas.add(edge_coll)

# Interior angle labels — batch with VCollection
angles = hexagon.interior_angles()
verts = hexagon.get_vertices()
angle_labels = VCollection(creation=0)
for angle_val, vert in zip(angles, verts):
    dx = 480 - vert[0]
    dy = 400 - vert[1]
    dist = (dx**2 + dy**2) ** 0.5
    nx, ny = (dx / dist, dy / dist) if dist > 0 else (0, 0)
    lx = vert[0] + nx * 40
    ly = vert[1] + ny * 40
    angle_labels.add(TexObject(rf'${angle_val:.0f}^\circ$', x=lx, y=ly, font_size=15,
                               fill='#FFFF00', stroke_width=0, anchor='center'))
angle_labels.stagger_fadein(start=2.3, end=3.0)
angle_labels.fadeout(5.5, 6.0)
canvas.add(angle_labels)

# Triangulation (right side)
hex2 = RegularPolygon(6, radius=140, cx=1440, cy=400,
                      fill='#9A72AC', fill_opacity=0.15, stroke='#9A72AC', stroke_width=3)
hex2.grow_from_center(start=0.5, end=1.2)
hex2.always_rotate(start=1.2, end=5.5, degrees_per_second=-15)
hex2.fadeout(5.5, 6.0)
canvas.add(hex2)

tri_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167']
triangles = hex2.triangulate(fill='#FFFFFF', fill_opacity=0.4, stroke='#FFFFFF', stroke_width=1)
tri_coll = VCollection(creation=0)
for i, tri in enumerate(triangles):
    tri.set_fill(color=tri_colors[i % len(tri_colors)])
    tri_coll.add(tri)
tri_coll.stagger_fadein(start=2.5, end=3.5)
tri_coll.fadeout(5.5, 6.0)
canvas.add(tri_coll)

tri_label = TexObject(r'Triangulation', x=1440, y=590, font_size=22,
                      fill='#83C167', stroke_width=0, anchor='center')
tri_label.fadein(3.0, 3.5)
tri_label.fadeout(5.5, 6.0)
canvas.add(tri_label)

# Bounding circle on the right hexagon
bcircle = hex2.bounding_circle(fill_opacity=0, stroke='#FFFF00', stroke_width=2)
bcircle.set_stroke_dash('8 4')
bcircle.fadein(start=4.0, end=4.5)
bcircle.fadeout(5.5, 6.0)
canvas.add(bcircle)

bc_label = TexObject(r'Bounding Circle', x=1440, y=620, font_size=18,
                     fill='#FFFF00', stroke_width=0, anchor='center')
bc_label.fadein(4.0, 4.5)
bc_label.fadeout(5.5, 6.0)
canvas.add(bc_label)

# =============================================================================
# Phase 2 (6-12s): Circle Constructions
# =============================================================================

title2 = TexObject(r'Circle Constructions', x=960, y=70, font_size=48,
                   fill='#FFFFFF', stroke_width=0, anchor='center')
title2.write(6.0, 6.8)
title2.fadeout(11.5, 12.0)
canvas.add(title2)

# Inscribed & circumscribed polygons (left)
circ1 = Circle(r=130, cx=480, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=3)
circ1.grow_from_center(start=6.3, end=6.9)
circ1.fadeout(11.5, 12.0)
canvas.add(circ1)

inscribed = circ1.inscribed_polygon(5, fill_opacity=0, stroke='#83C167', stroke_width=2)
inscribed.fadein(start=7.2, end=7.7)
inscribed.always_rotate(start=7.7, end=11.5, degrees_per_second=20)
inscribed.fadeout(11.5, 12.0)
canvas.add(inscribed)

insc_label = TexObject(r'Inscribed Pentagon', x=480, y=590, font_size=20,
                       fill='#83C167', stroke_width=0, anchor='center')
insc_label.fadein(7.2, 7.7)
insc_label.fadeout(11.5, 12.0)
canvas.add(insc_label)

circumscribed = circ1.circumscribed_polygon(5, fill_opacity=0, stroke='#FF862F', stroke_width=2)
circumscribed.fadein(start=8.2, end=8.7)
circumscribed.always_rotate(start=8.7, end=11.5, degrees_per_second=-20)
circumscribed.fadeout(11.5, 12.0)
canvas.add(circumscribed)

circ_label = TexObject(r'Circumscribed Pentagon', x=480, y=620, font_size=20,
                       fill='#FF862F', stroke_width=0, anchor='center')
circ_label.fadein(8.2, 8.7)
circ_label.fadeout(11.5, 12.0)
canvas.add(circ_label)

# Sectors (center)
circ2 = Circle(r=130, cx=960, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
circ2.grow_from_center(start=6.4, end=7.0)
circ2.fadeout(8.5, 8.8)
canvas.add(circ2)

sectors = circ2.get_sectors(6, stroke='#FFFFFF', stroke_width=2)
sector_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC']
for i, sector in enumerate(sectors.objects):
    sector.set_fill(color=sector_colors[i], opacity=0.6)
sectors.stagger_fadein(start=8.2, end=9.5)
sectors.fadeout(11.5, 12.0)
canvas.add(sectors)

sec_label = TexObject(r'6 Sectors', x=960, y=590, font_size=22,
                      fill='#FFFFFF', stroke_width=0, anchor='center')
sec_label.fadein(9.0, 9.5)
sec_label.fadeout(11.5, 12.0)
canvas.add(sec_label)

# Annulus (right)
circ3 = Circle(r=130, cx=1440, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
circ3.grow_from_center(start=6.5, end=7.1)
circ3.fadeout(9.5, 9.8)
canvas.add(circ3)

annulus = circ3.get_annulus(0.5, fill='#BD93F9', fill_opacity=0.5,
                           stroke='#FFFFFF', stroke_width=2)
annulus.fadein(start=9.5, end=10.1)
annulus.fadeout(11.5, 12.0)
canvas.add(annulus)

ann_label = TexObject(r'Annulus (ratio $= 0.5$)', x=1440, y=590, font_size=22,
                      fill='#FFFFFF', stroke_width=0, anchor='center')
ann_label.fadein(9.5, 10.0)
ann_label.fadeout(11.5, 12.0)
canvas.add(ann_label)

# =============================================================================
# Phase 3 (12-18s): Rectangle Operations
# =============================================================================

title3 = TexObject(r'Rectangle Operations', x=960, y=70, font_size=48,
                   fill='#FFFFFF', stroke_width=0, anchor='center')
title3.write(12.0, 12.8)
title3.fadeout(17.5, 18.0)
canvas.add(title3)

# Subdivide grid (left)
rect = Rectangle(400, 300, x=280, y=270,
                 fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=3)
rect.grow_from_center(start=12.2, end=12.8)
rect.fadeout(17.5, 18.0)
canvas.add(rect)

sub_grid = rect.subdivide(3, 4, stroke='#FFFFFF', stroke_width=1)
grid_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167',
               '#58C4DD', '#9A72AC', '#BD93F9', '#FFB86C',
               '#FF6B6B', '#FF79C6', '#B8BB26', '#E0E0E0']
for i, cell in enumerate(sub_grid.objects):
    cell.set_fill(color=grid_colors[i % len(grid_colors)], opacity=0.4)
sub_grid.stagger_fadein(start=13.0, end=14.5)
sub_grid.fadeout(17.5, 18.0)
canvas.add(sub_grid)

grid_label = TexObject(r'subdivide(3, 4)', x=480, y=610, font_size=22,
                       fill='#FFFFFF', stroke_width=0, anchor='center')
grid_label.fadein(13.5, 14.0)
grid_label.fadeout(17.5, 18.0)
canvas.add(grid_label)

# Split horizontal (center)
rect2 = Rectangle(300, 300, x=810, y=270,
                  fill='#83C167', fill_opacity=0.15, stroke='#83C167', stroke_width=3)
rect2.grow_from_center(start=12.3, end=12.9)
rect2.fadeout(14.3, 14.5)
canvas.add(rect2)

strips = rect2.split_horizontal(3, stroke='#FFFFFF', stroke_width=2)
strip_colors = ['#FC6255', '#58C4DD', '#FFFF00']
for i, strip in enumerate(strips.objects):
    strip.set_fill(color=strip_colors[i], opacity=0.5)
strips.stagger_fadein(start=14.0, end=15.2)
strips.fadeout(17.5, 18.0)
canvas.add(strips)

strip_label = TexObject(r'split\_horizontal(3)', x=960, y=610, font_size=22,
                        fill='#FFFFFF', stroke_width=0, anchor='center')
strip_label.fadein(14.3, 14.8)
strip_label.fadeout(17.5, 18.0)
canvas.add(strip_label)

# Inset (right)
rect3 = Rectangle(350, 300, x=1265, y=270,
                  fill='#9A72AC', fill_opacity=0.2, stroke='#9A72AC', stroke_width=3)
rect3.grow_from_center(start=12.4, end=13.0)
rect3.fadeout(17.5, 18.0)
canvas.add(rect3)

inset_rect = rect3.inset(30, fill_opacity=0, stroke='#FFFF00', stroke_width=2)
inset_rect.set_stroke_dash('6 3')
inset_rect.fadein(start=15.0, end=15.5)
inset_rect.fadeout(17.5, 18.0)
canvas.add(inset_rect)

inset_rect2 = rect3.inset(60, fill_opacity=0, stroke='#83C167', stroke_width=2)
inset_rect2.set_stroke_dash('6 3')
inset_rect2.fadein(start=15.5, end=16.0)
inset_rect2.fadeout(17.5, 18.0)
canvas.add(inset_rect2)

inset_label = TexObject(r'inset(30) \& inset(60)', x=1440, y=610, font_size=22,
                        fill='#FFFFFF', stroke_width=0, anchor='center')
inset_label.fadein(15.3, 15.8)
inset_label.fadeout(17.5, 18.0)
canvas.add(inset_label)

# =============================================================================
# Phase 4 (18-24s): Star & RegularPolygon Gallery
# =============================================================================

title4 = TexObject(r'Star Gallery', x=960, y=70, font_size=48,
                   fill='#FFFFFF', stroke_width=0, anchor='center')
title4.write(18.0, 18.8)
title4.fadeout(23.5, 24.0)
canvas.add(title4)

# Stars row — VCollection + arrange for clean layout
star_ns = [3, 4, 5, 6, 7]
colors = DEFAULT_CHART_COLORS
stars = VCollection(creation=0)
star_labels = VCollection(creation=0)

for i, n in enumerate(star_ns):
    s = Star(n=n, outer_radius=90, cx=0, cy=0,
             fill=colors[i], fill_opacity=0.7, stroke='#FFFFFF', stroke_width=2)
    stars.add(s)
    s_label = TexObject(rf'Star($n={n}$)', x=0, y=130, font_size=20,
                        fill=colors[i], stroke_width=0, anchor='center')
    star_labels.add(s_label)

stars.arrange(direction=RIGHT, buff=100)
stars.center_to_pos(960, 350)
star_labels.arrange(direction=RIGHT, buff=100)
star_labels.center_to_pos(960, 480)

# Staggered entrance with pulsate + varied rotation speeds
for i, (s, lbl) in enumerate(zip(stars.objects, star_labels.objects)):
    delay = i * 0.25
    s.grow_from_center(start=18.3 + delay, end=19.0 + delay)
    s.pulsate(start=19.0 + delay, end=19.5 + delay, scale_factor=1.15)
    s.always_rotate(start=19.5 + delay, end=23.0, degrees_per_second=25 + i * 8)
    s.fadeout(23.5, 24.0)
    lbl.fadein(18.5 + delay, 19.0 + delay)
    lbl.fadeout(23.5, 24.0)

canvas.add(stars, star_labels)

# Polygons row below — also using arrange
polys = VCollection(creation=0)
poly_labels = VCollection(creation=0)

for i, n in enumerate(star_ns):
    p = RegularPolygon(n, radius=80, cx=0, cy=0,
                       fill=colors[(i + 3) % len(colors)], fill_opacity=0.5,
                       stroke='#FFFFFF', stroke_width=2)
    polys.add(p)
    p_label = TexObject(rf'${n}$-gon', x=0, y=120, font_size=20,
                        fill=colors[(i + 3) % len(colors)], stroke_width=0, anchor='center')
    poly_labels.add(p_label)

polys.arrange(direction=RIGHT, buff=100)
polys.center_to_pos(960, 680)
poly_labels.arrange(direction=RIGHT, buff=100)
poly_labels.center_to_pos(960, 800)

for i, (p, lbl) in enumerate(zip(polys.objects, poly_labels.objects)):
    delay = i * 0.25
    p.grow_from_center(start=20.0 + delay, end=20.7 + delay)
    p.always_rotate(start=20.7 + delay, end=23.0, degrees_per_second=20 + i * 6)
    p.fadeout(23.5, 24.0)
    lbl.fadein(20.2 + delay, 20.7 + delay)
    lbl.fadeout(23.5, 24.0)

canvas.add(polys, poly_labels)

# =============================================================================
# Display
# =============================================================================
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/geometry_showcase.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
        hot_reload=args.hot_reload,
    )
