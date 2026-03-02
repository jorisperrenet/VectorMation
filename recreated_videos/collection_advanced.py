"""VCollection Advanced Methods: arrange_in_circle, converge/diverge,
scatter_from/gather_to, orbit_around, rotate_children, shuffle_animate,
show_one_by_one, pop_in/pop_out, snake_layout, stagger_scale, cascade_scale,
connect_children, label_children, distribute_radial, flip_all, space_evenly."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/collection_advanced')
v.set_background()
T = 36.0

BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#FFFF00'
PURPLE = '#9A72AC'
ORANGE = '#FF862F'
CYAN   = '#00CED1'
PALETTE = [BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, CYAN]

def make_shapes(n=7, shape='circle', size=25):
    """Create n colored shapes."""
    items = []
    for i in range(n):
        c = PALETTE[i % len(PALETTE)]
        if shape == 'circle':
            items.append(Circle(r=size, fill=c, fill_opacity=0.8,
                                stroke='#fff', stroke_width=2, creation=0))
        elif shape == 'square':
            items.append(Square(side=size * 2, fill=c, fill_opacity=0.8,
                                stroke='#fff', stroke_width=2, creation=0))
        elif shape == 'dot':
            items.append(Dot(r=size, fill=c, creation=0))
    return VCollection(*items)

# =============================================================================
# Phase 1 (0-6s): Circular & Radial Arrangements
# =============================================================================
title1 = Text(text='Circular & Radial', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title1.write(0, 0.5)
title1.fadeout(5.0, 5.5)
v.add(title1)

# --- arrange_in_circle ---
lbl1 = Text(text='arrange_in_circle', x=350, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl1.fadeout(5.0, 5.5)
v.add(lbl1)

circ1 = make_shapes(8, 'circle', 20)
circ1.arrange_in_circle(radius=100)
circ1.center_to_pos(350, 350, start=0)
circ1.stagger('fadein', start=0.5, end=1.5)
circ1.fadeout(5.0, 5.5)
v.add(circ1)

# --- distribute_radial ---
lbl2 = Text(text='distribute_radial', x=960, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl2.fadeout(5.0, 5.5)
v.add(lbl2)

rad1 = make_shapes(6, 'dot', 12)
rad1.center_to_pos(960, 350, start=0)
rad1.stagger('fadein', start=0.5, end=1.3)
rad1.distribute_radial(cx=960, cy=350, radius=100, start=1.5, end=2.5)
rad1.fadeout(5.0, 5.5)
v.add(rad1)

# --- orbit_around ---
lbl3 = Text(text='orbit_around', x=1570, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl3.fadeout(5.0, 5.5)
v.add(lbl3)

orb = make_shapes(5, 'circle', 15)
orb.arrange_in_circle(radius=80)
orb.center_to_pos(1570, 350, start=0)
orb.stagger('fadein', start=0.5, end=1.2)
orb.orbit_around(cx=1570, cy=350, start=1.5, end=5.0, degrees=720)
orb.fadeout(5.0, 5.5)
v.add(orb)

# --- space_evenly ---
lbl4 = Text(text='space_evenly', x=350, y=560, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl4.fadeout(5.0, 5.5)
v.add(lbl4)

sp = make_shapes(5, 'square', 20)
sp.center_to_pos(350, 700, start=0)
sp.stagger('fadein', start=0.5, end=1.3)
sp.space_evenly(start=1.5, direction=(1, 0), total_span=300)
sp.fadeout(5.0, 5.5)
v.add(sp)

# --- flip_all ---
lbl5 = Text(text='flip_all', x=960, y=560, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl5.fadeout(5.0, 5.5)
v.add(lbl5)

flp = make_shapes(5, 'square', 25)
flp.arrange(direction=(1, 0), buff=15)
flp.center_to_pos(960, 700, start=0)
flp.stagger('fadein', start=0.5, end=1.3)
flp.flip_all(start=2.0, end=3.5)
flp.fadeout(5.0, 5.5)
v.add(flp)

# --- connect_children ---
lbl6 = Text(text='connect_children', x=1570, y=560, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=0.3)
lbl6.fadeout(5.0, 5.5)
v.add(lbl6)

conn = make_shapes(5, 'dot', 10)
conn.arrange_in_circle(radius=80)
conn.center_to_pos(1570, 700, start=0)
conn.stagger('fadein', start=0.5, end=1.3)
lines = conn.connect_children(stroke='#555', stroke_width=1, start=1.5)
for line in lines:
    line.fadeout(5.0, 5.5)
    v.add(line)
conn.fadeout(5.0, 5.5)
v.add(conn)

# =============================================================================
# Phase 2 (6-12s): Converge/Diverge & Scatter/Gather
# =============================================================================
title2 = Text(text='Converge, Diverge & Scatter', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title2.write(6, 6.5)
title2.fadeout(11.0, 11.5)
v.add(title2)

# --- converge ---
lbl7 = Text(text='converge', x=350, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl7.fadeout(11.0, 11.5)
v.add(lbl7)

conv = make_shapes(7, 'circle', 18)
conv.arrange_in_circle(radius=100)
conv.center_to_pos(350, 350, start=6)
conv.stagger('fadein', start=6.3, end=7)
conv.converge(x=350, y=350, start=7.5, end=8.5)
conv.fadeout(11.0, 11.5)
v.add(conv)

# --- diverge ---
lbl8 = Text(text='diverge', x=960, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl8.fadeout(11.0, 11.5)
v.add(lbl8)

div1 = make_shapes(7, 'circle', 18)
div1.center_to_pos(960, 350, start=6)
div1.stagger('fadein', start=6.3, end=7)
div1.diverge(factor=2.0, cx=960, cy=350, start=7.5, end=8.5)
div1.fadeout(11.0, 11.5)
v.add(div1)

# --- scatter_from ---
lbl9 = Text(text='scatter_from', x=1570, y=160, font_size=22,
            fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl9.fadeout(11.0, 11.5)
v.add(lbl9)

scat = make_shapes(8, 'dot', 12)
scat.center_to_pos(1570, 350, start=6)
scat.stagger('fadein', start=6.3, end=7)
scat.scatter_from(cx=1570, cy=350, radius=120, start=7.5, end=8.5)
scat.fadeout(11.0, 11.5)
v.add(scat)

# --- gather_to ---
lbl10 = Text(text='gather_to', x=350, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl10.fadeout(11.0, 11.5)
v.add(lbl10)

gath = make_shapes(8, 'dot', 12)
gath.arrange_in_circle(radius=100)
gath.center_to_pos(350, 700, start=6)
gath.stagger('fadein', start=6.3, end=7)
gath.gather_to(cx=350, cy=700, start=8, end=9)
gath.fadeout(11.0, 11.5)
v.add(gath)

# --- show_one_by_one ---
lbl11 = Text(text='stagger overlap=0', x=960, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl11.fadeout(11.0, 11.5)
v.add(lbl11)

obo = make_shapes(5, 'square', 25)
obo.arrange(direction=(1, 0), buff=15)
obo.center_to_pos(960, 700, start=6)
obo.stagger('fadein', start=7, end=9, overlap=0)
obo.fadeout(11.0, 11.5)
v.add(obo)

# --- show_increasing_subsets ---
lbl12 = Text(text='show_increasing_subsets', x=1570, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=6.3)
lbl12.fadeout(11.0, 11.5)
v.add(lbl12)

inc = make_shapes(6, 'circle', 20)
inc.arrange(direction=(1, 0), buff=12)
inc.center_to_pos(1570, 700, start=6)
inc.show_increasing_subsets(start=7, end=9)
inc.fadeout(11.0, 11.5)
v.add(inc)

# =============================================================================
# Phase 3 (12-18s): Stagger Variants
# =============================================================================
title3 = Text(text='Stagger Variants', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title3.write(12, 12.5)
title3.fadeout(17.0, 17.5)
v.add(title3)

# --- stagger_scale ---
lbl13 = Text(text='stagger_scale', x=350, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl13.fadeout(17.0, 17.5)
v.add(lbl13)

ss = make_shapes(5, 'circle', 25)
ss.arrange(direction=(1, 0), buff=15)
ss.center_to_pos(350, 350, start=12)
ss.stagger('fadein', start=12.3, end=13)
ss.stagger_scale(scale_factor=1.5, start=13.5, end=15, delay=0.2)
ss.fadeout(17.0, 17.5)
v.add(ss)

# --- stagger_rotate ---
lbl14 = Text(text='stagger_rotate', x=960, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl14.fadeout(17.0, 17.5)
v.add(lbl14)

sr = make_shapes(5, 'square', 22)
sr.arrange(direction=(1, 0), buff=15)
sr.center_to_pos(960, 350, start=12)
sr.stagger('fadein', start=12.3, end=13)
sr.stagger_rotate(degrees=360, start=13.5, end=15.5)
sr.fadeout(17.0, 17.5)
v.add(sr)

# --- stagger_color ---
lbl15 = Text(text='stagger_color', x=1570, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl15.fadeout(17.0, 17.5)
v.add(lbl15)

sc = make_shapes(6, 'circle', 22)
sc.arrange(direction=(1, 0), buff=15)
sc.center_to_pos(1570, 350, start=12)
sc.stagger('fadein', start=12.3, end=13)
sc.stagger_color(colors=('#FF0000', '#FFFF00'), start=13.5, end=15)
sc.fadeout(17.0, 17.5)
v.add(sc)

# --- cascade_fadein ---
lbl16 = Text(text='stagger_fadein_sorted', x=350, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl16.fadeout(17.0, 17.5)
v.add(lbl16)

cf = make_shapes(6, 'square', 22)
cf.arrange(direction=(1, 0), buff=12)
cf.center_to_pos(350, 700, start=12)
cf.stagger_fadein_sorted(start=13, end=14.5)
cf.fadeout(17.0, 17.5)
v.add(cf)

# --- cascade_scale ---
lbl17 = Text(text='stagger_scale', x=960, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl17.fadeout(17.0, 17.5)
v.add(lbl17)

cs = make_shapes(5, 'circle', 22)
cs.arrange(direction=(1, 0), buff=15)
cs.center_to_pos(960, 700, start=12)
cs.stagger('fadein', start=12.3, end=13)
cs.stagger_scale(start=14, end=15.5, scale_factor=0.5)
cs.fadeout(17.0, 17.5)
v.add(cs)

# --- stagger_fadeout ---
lbl18 = Text(text='stagger_fadeout', x=1570, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=12.3)
lbl18.fadeout(17.0, 17.5)
v.add(lbl18)

sfo = make_shapes(5, 'circle', 25)
sfo.arrange(direction=(1, 0), buff=15)
sfo.center_to_pos(1570, 700, start=12)
sfo.stagger('fadein', start=12.3, end=13)
sfo.stagger_fadeout(start=14.5, end=16)
v.add(sfo)

# =============================================================================
# Phase 4 (18-24s): Transform & Layout
# =============================================================================
title4 = Text(text='Transform & Layout', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title4.write(18, 18.5)
title4.fadeout(23.0, 23.5)
v.add(title4)

# --- rotate_children ---
lbl19 = Text(text='rotate_children', x=350, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl19.fadeout(23.0, 23.5)
v.add(lbl19)

rc = make_shapes(5, 'square', 25)
rc.arrange(direction=(1, 0), buff=15)
rc.center_to_pos(350, 350, start=18)
rc.stagger('fadein', start=18.3, end=19)
rc.rotate_children(degrees=45, start=19.5, end=21)
rc.fadeout(23.0, 23.5)
v.add(rc)

# --- shuffle_animate ---
lbl20 = Text(text='shuffle_animate', x=960, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl20.fadeout(23.0, 23.5)
v.add(lbl20)

sha = make_shapes(5, 'circle', 22)
sha.arrange(direction=(1, 0), buff=20)
sha.center_to_pos(960, 350, start=18)
sha.stagger('fadein', start=18.3, end=19)
sha.shuffle_animate(start=19.5, end=21)
sha.fadeout(23.0, 23.5)
v.add(sha)

# --- pop_in/pop_out ---
lbl21 = Text(text='pop_in + pop_out', x=1570, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl21.fadeout(23.0, 23.5)
v.add(lbl21)

pp = make_shapes(5, 'circle', 25)
pp.arrange(direction=(1, 0), buff=15)
pp.center_to_pos(1570, 350, start=18)
pp.pop_in(start=18.5, end=19.5)
pp.pop_out(start=21.0, end=22.0)
v.add(pp)

# --- snake_layout ---
lbl22 = Text(text='snake_layout', x=350, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl22.fadeout(23.0, 23.5)
v.add(lbl22)

snk = make_shapes(8, 'dot', 12)
snk.center_to_pos(350, 700, start=18)
snk.stagger('fadein', start=18.3, end=19)
snk.snake_layout(cols=4, buff=30, start=19.5)
snk.fadeout(23.0, 23.5)
v.add(snk)

# --- shuffle_positions ---
lbl23 = Text(text='shuffle_positions', x=960, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl23.fadeout(23.0, 23.5)
v.add(lbl23)

shp = make_shapes(6, 'square', 20)
shp.arrange(direction=(1, 0), buff=15)
shp.center_to_pos(960, 700, start=18)
shp.stagger('fadein', start=18.3, end=19)
shp.shuffle_positions(start=19.5, end=20.5)
shp.fadeout(23.0, 23.5)
v.add(shp)

# --- label_children ---
lbl24 = Text(text='label_children', x=1570, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=18.3)
lbl24.fadeout(23.0, 23.5)
v.add(lbl24)

lab = make_shapes(4, 'circle', 25)
lab.arrange(direction=(1, 0), buff=25)
lab.center_to_pos(1570, 680, start=18)
lab.stagger('fadein', start=18.3, end=19)
lbl_coll = lab.label_children(['A', 'B', 'C', 'D'], direction=(0, -1),
                              buff=40, font_size=18, creation=19.5)
lbl_coll.fadeout(23.0, 23.5)
v.add(lbl_coll)
lab.fadeout(23.0, 23.5)
v.add(lab)

# =============================================================================
# Phase 5 (24-30s): Advanced Animations
# =============================================================================
title5 = Text(text='Advanced Animations', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title5.write(24, 24.5)
title5.fadeout(29.0, 29.5)
v.add(title5)

# --- animated_arrange ---
lbl25 = Text(text='animated_arrange', x=350, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl25.fadeout(29.0, 29.5)
v.add(lbl25)

aa = make_shapes(6, 'circle', 20)
aa.center_to_pos(350, 350, start=24)
aa.stagger('fadein', start=24.3, end=25)
aa.animated_arrange(direction=(1, 0), buff=15, start=25.5, end=26.5)
aa.fadeout(29.0, 29.5)
v.add(aa)

# --- animated_arrange_in_grid ---
lbl26 = Text(text='animated_arrange_in_grid', x=960, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl26.fadeout(29.0, 29.5)
v.add(lbl26)

aag = make_shapes(8, 'square', 18)
aag.center_to_pos(960, 350, start=24)
aag.stagger('fadein', start=24.3, end=25)
aag.animated_arrange_in_grid(rows=2, cols=4, buff=12, start=25.5, end=26.5)
aag.fadeout(29.0, 29.5)
v.add(aag)

# --- wave_effect ---
lbl27 = Text(text='wave_effect', x=1570, y=160, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl27.fadeout(29.0, 29.5)
v.add(lbl27)

we = make_shapes(7, 'circle', 20)
we.arrange(direction=(1, 0), buff=12)
we.center_to_pos(1570, 350, start=24)
we.stagger('fadein', start=24.3, end=25)
we.wave_effect(start=25.5, end=28, amplitude=50)
we.fadeout(29.0, 29.5)
v.add(we)

# --- fade_in_one_by_one ---
lbl28 = Text(text='stagger_fadein overlap=0', x=350, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl28.fadeout(29.0, 29.5)
v.add(lbl28)

fio = make_shapes(5, 'square', 25)
fio.arrange(direction=(1, 0), buff=15)
fio.center_to_pos(350, 700, start=24)
fio.stagger_fadein(start=25, end=27, overlap=0)
fio.fadeout(29.0, 29.5)
v.add(fio)

# --- distribute_along_arc ---
lbl29 = Text(text='distribute_along_arc', x=960, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl29.fadeout(29.0, 29.5)
v.add(lbl29)

daa = make_shapes(6, 'dot', 14)
daa.center_to_pos(960, 700, start=24)
daa.stagger('fadein', start=24.3, end=25)
daa.distribute_along_arc(cx=960, cy=700, radius=90, start=25.5, end=26.5)
daa.fadeout(29.0, 29.5)
v.add(daa)

# --- reveal ---
lbl30 = Text(text='reveal', x=1570, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=24.3)
lbl30.fadeout(29.0, 29.5)
v.add(lbl30)

rev = make_shapes(5, 'circle', 25)
rev.arrange(direction=(1, 0), buff=15)
rev.center_to_pos(1570, 700, start=24)
rev.reveal(start=25, end=27)
rev.fadeout(29.0, 29.5)
v.add(rev)

# =============================================================================
# Phase 6 (30-36s): Sort & Filter
# =============================================================================
title6 = Text(text='Sort, Filter & Highlight', x=960, y=60, font_size=48,
              fill='#FFFFFF', stroke_width=0, text_anchor='middle')
title6.write(30, 30.5)
title6.fadeout(35.0, 35.5)
v.add(title6)

# --- sort_children ---
lbl31 = Text(text='sort_children (by color)', x=480, y=200, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=30.3)
lbl31.fadeout(35.0, 35.5)
v.add(lbl31)

sc2 = VCollection(
    Circle(r=30, fill=RED, fill_opacity=0.8, stroke='#fff', stroke_width=2, creation=30),
    Circle(r=30, fill=BLUE, fill_opacity=0.8, stroke='#fff', stroke_width=2, creation=30),
    Circle(r=30, fill=GREEN, fill_opacity=0.8, stroke='#fff', stroke_width=2, creation=30),
    Circle(r=30, fill=YELLOW, fill_opacity=0.8, stroke='#fff', stroke_width=2, creation=30),
    Circle(r=30, fill=PURPLE, fill_opacity=0.8, stroke='#fff', stroke_width=2, creation=30),
)
sc2.arrange(direction=(1, 0), buff=20)
sc2.center_to_pos(480, 380, start=30)
sc2.stagger('fadein', start=30.3, end=31)
# sort_children reorders internal list (instant operation)
sc2.sort_children(key=lambda c, t: c.styling.fill.time_func(t))
sc2.animated_arrange(direction=(1, 0), buff=20, start=31.5, end=32.5)
sc2.fadeout(35.0, 35.5)
v.add(sc2)

# --- highlight_child / highlight_nth ---
lbl32 = Text(text='highlight_nth', x=1440, y=200, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=30.3)
lbl32.fadeout(35.0, 35.5)
v.add(lbl32)

hl = make_shapes(5, 'square', 30)
hl.arrange(direction=(1, 0), buff=15)
hl.center_to_pos(1440, 380, start=30)
hl.stagger('fadein', start=30.3, end=31)
# Highlight each child sequentially
for i in range(5):
    t = 31.5 + i * 0.7
    hl.highlight_nth(i, start=t, end=t + 0.5, color='#FFFFFF')
hl.fadeout(35.0, 35.5)
v.add(hl)

# --- set_opacity_by_gradient ---
lbl33 = Text(text='set_opacity_by_gradient', x=480, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=30.3)
lbl33.fadeout(35.0, 35.5)
v.add(lbl33)

og = make_shapes(7, 'circle', 25)
og.arrange(direction=(1, 0), buff=12)
og.center_to_pos(480, 700, start=30)
og.stagger('fadein', start=30.3, end=31)
og.set_opacity_by_gradient(0.1, 1.0)
og.fadeout(35.0, 35.5)
v.add(og)

# --- set_color_by_gradient (another example) ---
lbl34 = Text(text='set_color_by_gradient', x=1440, y=560, font_size=22,
             fill='#888', stroke_width=0, text_anchor='middle', creation=30.3)
lbl34.fadeout(35.0, 35.5)
v.add(lbl34)

cg = VCollection(*[Square(side=50, creation=30) for _ in range(8)])
cg.arrange(direction=(1, 0), buff=8)
cg.center_to_pos(1440, 700, start=30)
cg.set_color_by_gradient('#FF0000', '#FFFF00', '#00FF00')
cg.stagger('fadein', start=30.5, end=31.5)
cg.fadeout(35.0, 35.5)
v.add(cg)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    v.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
