"""Demo of additional diagram types: ChessBoard, BohrAtom, OrgChart,
MindMap, and TimelineBar."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    Text, VectorMathAnim, parse_args,
    ChessBoard, BohrAtom, OrgChart, MindMap, TimelineBar,
)

v = VectorMathAnim('/tmp')

# ── Section 1: ChessBoard + BohrAtom (0-4s) ────────────────────────
title1 = Text(text='ChessBoard & BohrAtom', x=960, y=50,
              font_size=28, text_anchor='middle', creation=0)
title1.fadeout(start=4, end=4.3)
v.add(title1)

board = ChessBoard(cx=420, cy=520, size=500,
                   fen='r1bqkbnr/pppppppp/2n5/8/4P3/8/PPPP1PPP/RNBQKBNR',
                   creation=0)
board.fadein(start=0, end=1)
v.add(board)

atom = BohrAtom(protons=8, neutrons=8, electrons=[2, 6],
                cx=1350, cy=500, creation=0)
atom.fadein(start=0.5, end=1.5)
v.add(atom)

# ── Section 2: OrgChart (4-8s) ─────────────────────────────────────
title2 = Text(text='OrgChart', x=960, y=50,
              font_size=28, text_anchor='middle', creation=4)
title2.fadeout(start=8, end=8.3)
v.add(title2)

org = OrgChart(
    root=('CEO', [
        ('CTO', [('Dev Lead', []), ('QA Lead', [])]),
        ('CFO', [('Finance', []), ('Accounting', [])]),
        ('CMO', [('Marketing', [])]),
    ]),
    x=960, y=150, creation=4,
)
org.fadein(start=4, end=5)
v.add(org)

# ── Section 3: MindMap (8-12s) ─────────────────────────────────────
title3 = Text(text='MindMap', x=960, y=50,
              font_size=28, text_anchor='middle', creation=8)
title3.fadeout(start=12, end=12.3)
v.add(title3)

mind = MindMap(
    root=('CS', [
        ('Algorithms', [('Sorting', []), ('Graphs', [])]),
        ('Languages', [('Python', []), ('Rust', []), ('C++', [])]),
        ('Systems', [('OS', []), ('Networks', [])]),
        ('AI/ML', []),
    ]),
    cx=960, cy=500, radius=250, creation=8,
)
mind.fadein(start=8, end=9)
v.add(mind)

# ── TimelineBar (bottom, full video) ───────────────────────────────
timeline = TimelineBar(
    markers={0: 'Chess+Atom', 4: 'OrgChart', 8: 'MindMap'},
    total_duration=12, x=200, y=1020, width=1520, creation=0,
)
v.add(timeline)

if __name__ == '__main__':
    args = parse_args()
        v.browser_display(start=args.start or 0, end=args.end or 12,
                          fps=args.fps, port=args.port)
