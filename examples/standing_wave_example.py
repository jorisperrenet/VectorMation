"""Standing wave animation showing different harmonics."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

canvas = VectorMathAnim(save_dir='svgs/standing_wave')
canvas.set_background()

waves = []
for n in range(1, 5):
    y_pos = 150 + (n - 1) * 220
    sw = StandingWave(x1=300, y1=y_pos, x2=1620, y2=y_pos,
                      amplitude=70, harmonics=n, frequency=0.8,
                      start=0, end=8, stroke='#58C4DD', stroke_width=3)
    label = Text(f'n = {n}', x=200, y=y_pos, font_size=28,
                 text_anchor='end', fill='#aaa')
    sw.fadein(start=n * 0.3, end=n * 0.3 + 0.5)
    label.fadein(start=n * 0.3, end=n * 0.3 + 0.5)
    waves.extend([sw, label])

title = Text('Standing Waves — First Four Harmonics', x=960, y=60,
             font_size=36, text_anchor='middle', fill='#fff')
title.fadein(start=0, end=1)

canvas.add_objects(title, *waves)
args = parse_args()
if not args.no_display:
    canvas.browser_display(start=0, end=8, fps=args.fps, port=args.port,
                           hot_reload=True)
