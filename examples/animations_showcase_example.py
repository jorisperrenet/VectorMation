import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animations_showcase')
canvas.set_background()

# Showcase various animations
title = Text(text='Animation Showcase', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Row 1: shake, swing, wiggle, pulse
lbl1 = Text(text='shake', x=340, y=240, font_size=28, fill='#aaa',
            stroke_width=0, text_anchor='middle')
c1 = Circle(r=60, cx=340, cy=380, fill='#58C4DD', fill_opacity=0.7)
c1.fadein(0, 0.5)
c1.shake(start=1, end=2, amplitude=8)
lbl1.fadein(0, 0.5)

lbl2 = Text(text='swing', x=760, y=240, font_size=28, fill='#aaa',
            stroke_width=0, text_anchor='middle')
r1 = Rectangle(100, 100, x=710, y=330, fill='#83C167', fill_opacity=0.7)
r1.fadein(0, 0.5)
r1.swing(start=1, end=3, amplitude=20, n_swings=4)
lbl2.fadein(0, 0.5)

lbl3 = Text(text='wiggle', x=1180, y=240, font_size=28, fill='#aaa',
            stroke_width=0, text_anchor='middle')
s1 = Star(n=5, outer_radius=60, inner_radius=30, cx=1180, cy=380,
          fill='#FC6255', fill_opacity=0.7)
s1.fadein(0, 0.5)
s1.wiggle(start=1, end=2.5, amplitude=15)
lbl3.fadein(0, 0.5)

lbl4 = Text(text='pulse', x=1580, y=240, font_size=28, fill='#aaa',
            stroke_width=0, text_anchor='middle')
d1 = Dot(cx=1580, cy=380, r=40, fill='#FFFF00')
d1.fadein(0, 0.5)
d1.pulse(start=1, end=2)
lbl4.fadein(0, 0.5)

# Row 2: draw_border_then_fill, grow_from_edge, wave, circumscribe
lbl5 = Text(text='draw_border_then_fill', x=340, y=560, font_size=22, fill='#aaa',
            stroke_width=0, text_anchor='middle')
c2 = Circle(r=60, cx=340, cy=700, fill='#9A72AC', fill_opacity=0.7)
c2.draw_border_then_fill(start=1, end=2.5)
lbl5.fadein(0, 0.5)

lbl6 = Text(text='grow_from_edge', x=760, y=560, font_size=22, fill='#aaa',
            stroke_width=0, text_anchor='middle')
r2 = Rectangle(100, 100, x=710, y=650, fill='#F0AC5F', fill_opacity=0.7)
r2.grow_from_edge('bottom', start=1, end=2)
lbl6.fadein(0, 0.5)

lbl7 = Text(text='wave', x=1180, y=560, font_size=22, fill='#aaa',
            stroke_width=0, text_anchor='middle')
t1 = EquilateralTriangle(side_length=100, cx=1180, cy=700,
                         fill='#5CD0B3', fill_opacity=0.7)
t1.fadein(0, 0.5)
t1.wave(start=1, end=3, amplitude=25)
lbl7.fadein(0, 0.5)

lbl8 = Text(text='circumscribe', x=1580, y=560, font_size=22, fill='#aaa',
            stroke_width=0, text_anchor='middle')
r3 = Rectangle(80, 80, x=1540, y=660, fill='#C55F73', fill_opacity=0.7)
r3.fadein(0, 0.5)
r3.circumscribe(start=1.5, end=2.5, stroke='#FFFF00')
lbl8.fadein(0, 0.5)

canvas.add_objects(title,
                   lbl1, c1, lbl2, r1, lbl3, s1, lbl4, d1,
                   lbl5, c2, lbl6, r2, lbl7, t1, lbl8, r3)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
