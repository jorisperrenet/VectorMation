"""Geometry Showcase — Polygon decomposition, circle constructions, rectangle operations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/geometry_showcase')
canvas.set_background()
T = 20.0

# =============================================================================
# Phase 1 (0-5s): Polygon Operations
# =============================================================================

title1 = Text(text='Polygon Operations', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0.0, 0.8)
title1.fadeout(4.5, 5.0)
canvas.add(title1)

# Create hexagon (left side) — no creation= so geometry methods work at time=0
hexagon = RegularPolygon(6, radius=120, cx=480, cy=420,
                         fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=3)
hexagon.grow_from_center(start=0.3, end=1.0)
hexagon.fadeout(4.5, 5.0)
canvas.add(hexagon)

hex_label = Text(text='Regular Hexagon', x=480, y=580, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
hex_label.fadein(0.5, 1.0)
hex_label.fadeout(4.5, 5.0)
canvas.add(hex_label)

# Show edges with different colors
edges = hexagon.get_edges()
edge_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC']
for i, edge in enumerate(edges):
    edge.set_stroke(color=edge_colors[i % len(edge_colors)], width=4)
    edge.fadein(start=1.0 + i * 0.1, end=1.3 + i * 0.1)
    edge.fadeout(4.5, 5.0)
    canvas.add(edge)

# Show interior angles as text labels
angles = hexagon.interior_angles()
verts = hexagon.get_vertices()
for i, (angle_val, vert) in enumerate(zip(angles, verts)):
    # Offset label toward center
    dx = 480 - vert[0]
    dy = 420 - vert[1]
    dist = (dx**2 + dy**2) ** 0.5
    if dist > 0:
        nx, ny = dx / dist, dy / dist
    else:
        nx, ny = 0, 0
    lx = vert[0] + nx * 35
    ly = vert[1] + ny * 35
    angle_text = Text(text=f'{angle_val:.0f}', x=lx, y=ly, font_size=14,
                      fill='#FFFF00', stroke_width=0, text_anchor='middle')
    angle_text.fadein(start=1.5, end=2.0)
    angle_text.fadeout(4.5, 5.0)
    canvas.add(angle_text)

# Triangulate and show with different fill colors
tri_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167']
triangles = hexagon.triangulate(fill='#FFFFFF', fill_opacity=0.4, stroke='#FFFFFF', stroke_width=1)
for i, tri in enumerate(triangles):
    tri.set_fill(color=tri_colors[i % len(tri_colors)])
    tri.fadein(start=2.2 + i * 0.15, end=2.6 + i * 0.15)
    tri.fadeout(4.5, 5.0)
    canvas.add(tri)

tri_label = Text(text='Triangulation', x=480, y=610, font_size=18,
                 fill='#83C167', stroke_width=0, text_anchor='middle')
tri_label.fadein(2.5, 3.0)
tri_label.fadeout(4.5, 5.0)
canvas.add(tri_label)

# Show bounding circle on the right side
hex2 = RegularPolygon(6, radius=120, cx=1440, cy=420,
                      fill='#9A72AC', fill_opacity=0.2, stroke='#9A72AC', stroke_width=3)
hex2.grow_from_center(start=2.5, end=3.2)
hex2.fadeout(4.5, 5.0)
canvas.add(hex2)

bcircle = hex2.bounding_circle(fill_opacity=0, stroke='#FFFF00', stroke_width=2)
bcircle.set_stroke_dash('8 4')
bcircle.fadein(start=3.2, end=3.6)
bcircle.fadeout(4.5, 5.0)
canvas.add(bcircle)

bc_label = Text(text='Bounding Circle', x=1440, y=580, font_size=22,
                fill='#AAAAAA', stroke_width=0, text_anchor='middle')
bc_label.fadein(3.2, 3.6)
bc_label.fadeout(4.5, 5.0)
canvas.add(bc_label)

# =============================================================================
# Phase 2 (5-10s): Circle Constructions
# =============================================================================

title2 = Text(text='Circle Constructions', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(5.0, 5.8)
title2.fadeout(9.5, 10.0)
canvas.add(title2)

# Inscribed & circumscribed polygons (left side)
circ1 = Circle(r=120, cx=480, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=3)
circ1.grow_from_center(start=5.2, end=5.8)
circ1.fadeout(9.5, 10.0)
canvas.add(circ1)

# Inscribed pentagon
inscribed = circ1.inscribed_polygon(5, fill_opacity=0, stroke='#83C167', stroke_width=2)
inscribed.fadein(start=6.0, end=6.5)
inscribed.fadeout(9.5, 10.0)
canvas.add(inscribed)

insc_label = Text(text='Inscribed Pentagon', x=480, y=580, font_size=20,
                  fill='#83C167', stroke_width=0, text_anchor='middle')
insc_label.fadein(6.0, 6.5)
insc_label.fadeout(9.5, 10.0)
canvas.add(insc_label)

# Circumscribed pentagon
circumscribed = circ1.circumscribed_polygon(5, fill_opacity=0, stroke='#FF862F', stroke_width=2)
circumscribed.fadein(start=6.8, end=7.3)
circumscribed.fadeout(9.5, 10.0)
canvas.add(circumscribed)

circ_label = Text(text='Circumscribed Pentagon', x=480, y=610, font_size=20,
                  fill='#FF862F', stroke_width=0, text_anchor='middle')
circ_label.fadein(6.8, 7.3)
circ_label.fadeout(9.5, 10.0)
canvas.add(circ_label)

# Sectors (center)
circ2 = Circle(r=120, cx=960, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
circ2.grow_from_center(start=5.3, end=5.9)
circ2.fadeout(7.3, 7.5)
canvas.add(circ2)

sectors = circ2.get_sectors(6, stroke='#FFFFFF', stroke_width=2)
sector_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167', '#58C4DD', '#9A72AC']
for i, sector in enumerate(sectors.objects):
    sector.set_fill(color=sector_colors[i], opacity=0.6)
sectors.stagger_fadein(start=7.0, end=8.2)
sectors.fadeout(9.5, 10.0)
canvas.add(sectors)

sec_label = Text(text='6 Sectors', x=960, y=580, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
sec_label.fadein(7.5, 8.0)
sec_label.fadeout(9.5, 10.0)
canvas.add(sec_label)

# Annulus (right side)
circ3 = Circle(r=120, cx=1440, cy=420,
               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
circ3.grow_from_center(start=5.4, end=6.0)
circ3.fadeout(8.2, 8.5)
canvas.add(circ3)

annulus = circ3.get_annulus(0.5, fill='#BD93F9', fill_opacity=0.5,
                           stroke='#FFFFFF', stroke_width=2)
annulus.fadein(start=8.0, end=8.6)
annulus.fadeout(9.5, 10.0)
canvas.add(annulus)

ann_label = Text(text='Annulus (ratio=0.5)', x=1440, y=580, font_size=22,
                 fill='#AAAAAA', stroke_width=0, text_anchor='middle')
ann_label.fadein(8.2, 8.6)
ann_label.fadeout(9.5, 10.0)
canvas.add(ann_label)

# =============================================================================
# Phase 3 (10-15s): Rectangle Operations
# =============================================================================

title3 = Text(text='Rectangle Operations', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(10.0, 10.8)
title3.fadeout(14.5, 15.0)
canvas.add(title3)

# Original rectangle (left side)
rect = Rectangle(400, 300, x=280, y=270,
                 fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=3)
rect.grow_from_center(start=10.2, end=10.8)
rect.fadeout(14.5, 15.0)
canvas.add(rect)

# Subdivide into 3x4 grid
sub_grid = rect.subdivide(3, 4, stroke='#FFFFFF', stroke_width=1)
grid_colors = ['#FC6255', '#FF862F', '#FFFF00', '#83C167',
               '#58C4DD', '#9A72AC', '#BD93F9', '#FFB86C',
               '#FF6B6B', '#FF79C6', '#B8BB26', '#E0E0E0']
for i, cell in enumerate(sub_grid.objects):
    cell.set_fill(color=grid_colors[i % len(grid_colors)], opacity=0.4)
sub_grid.stagger_fadein(start=11.0, end=12.2)
sub_grid.fadeout(14.5, 15.0)
canvas.add(sub_grid)

grid_label = Text(text='subdivide(3, 4)', x=480, y=610, font_size=22,
                  fill='#AAAAAA', stroke_width=0, text_anchor='middle')
grid_label.fadein(11.5, 12.0)
grid_label.fadeout(14.5, 15.0)
canvas.add(grid_label)

# Split horizontal (center)
rect2 = Rectangle(300, 300, x=810, y=270,
                  fill='#83C167', fill_opacity=0.15, stroke='#83C167', stroke_width=3)
rect2.grow_from_center(start=10.3, end=10.9)
rect2.fadeout(12.3, 12.5)
canvas.add(rect2)

strips = rect2.split_horizontal(3, stroke='#FFFFFF', stroke_width=2)
strip_colors = ['#FC6255', '#58C4DD', '#FFFF00']
for i, strip in enumerate(strips.objects):
    strip.set_fill(color=strip_colors[i], opacity=0.5)
strips.stagger_fadein(start=12.0, end=13.0)
strips.fadeout(14.5, 15.0)
canvas.add(strips)

strip_label = Text(text='split_horizontal(3)', x=960, y=610, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
strip_label.fadein(12.2, 12.7)
strip_label.fadeout(14.5, 15.0)
canvas.add(strip_label)

# Inset (right side)
rect3 = Rectangle(350, 300, x=1265, y=270,
                  fill='#9A72AC', fill_opacity=0.2, stroke='#9A72AC', stroke_width=3)
rect3.grow_from_center(start=10.4, end=11.0)
rect3.fadeout(14.5, 15.0)
canvas.add(rect3)

inset_rect = rect3.inset(30, fill_opacity=0, stroke='#FFFF00', stroke_width=2)
inset_rect.set_stroke_dash('6 3')
inset_rect.fadein(start=13.0, end=13.5)
inset_rect.fadeout(14.5, 15.0)
canvas.add(inset_rect)

inset_rect2 = rect3.inset(60, fill_opacity=0, stroke='#83C167', stroke_width=2)
inset_rect2.set_stroke_dash('6 3')
inset_rect2.fadein(start=13.3, end=13.8)
inset_rect2.fadeout(14.5, 15.0)
canvas.add(inset_rect2)

inset_label = Text(text='inset(30) & inset(60)', x=1440, y=610, font_size=22,
                   fill='#AAAAAA', stroke_width=0, text_anchor='middle')
inset_label.fadein(13.2, 13.7)
inset_label.fadeout(14.5, 15.0)
canvas.add(inset_label)

# =============================================================================
# Phase 4 (15-20s): Star & RegularPolygon Gallery
# =============================================================================

title4 = Text(text='Star Gallery', x=960, y=70, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(15.0, 15.8)
title4.fadeout(19.5, 20.0)
canvas.add(title4)

# Row of stars with n=3,4,5,6,7
star_ns = [3, 4, 5, 6, 7]
star_xs = [240, 480, 720, 960, 1200]
colors = DEFAULT_CHART_COLORS

for i, n in enumerate(star_ns):
    s = Star(n=n, outer_radius=90, cx=star_xs[i], cy=380,
             fill=colors[i], fill_opacity=0.7, stroke='#FFFFFF', stroke_width=2)
    delay = i * 0.2
    s.grow_from_center(start=15.3 + delay, end=15.9 + delay)
    s.always_rotate(start=16.5 + delay, end=19.0, degrees_per_second=30)
    s.fadeout(19.5, 20.0)
    canvas.add(s)

    s_label = Text(text=f'Star(n={n})', x=star_xs[i], y=510, font_size=20,
                   fill=colors[i], stroke_width=0, text_anchor='middle')
    s_label.fadein(15.5 + delay, 16.0 + delay)
    s_label.fadeout(19.5, 20.0)
    canvas.add(s_label)

# Row of regular polygons below with n=3,4,5,6,7
poly_xs = [240, 480, 720, 960, 1200]

for i, n in enumerate(star_ns):
    p = RegularPolygon(n, radius=80, cx=poly_xs[i], cy=700,
                       fill=colors[(i + 3) % len(colors)], fill_opacity=0.5,
                       stroke='#FFFFFF', stroke_width=2)
    delay = i * 0.2
    p.grow_from_center(start=16.5 + delay, end=17.1 + delay)
    p.fadeout(19.5, 20.0)
    canvas.add(p)

    p_label = Text(text=f'{n}-gon', x=poly_xs[i], y=810, font_size=20,
                   fill=colors[(i + 3) % len(colors)], stroke_width=0, text_anchor='middle')
    p_label.fadein(16.7 + delay, 17.2 + delay)
    p_label.fadeout(19.5, 20.0)
    canvas.add(p_label)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
        hot_reload=args.hot_reload,
    )
