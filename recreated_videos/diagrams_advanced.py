"""Advanced Diagrams Demo — PeriodicTable, ChessBoard, BohrAtom, TimelineBar, OrgChart, MindMap."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
show = VectorMathAnim(verbose=args.verbose, save_dir='svgs/diagrams_advanced')
show.set_background()

T = 18.0

# =============================================================================
# Phase 1 (0-3s): PeriodicTable
# =============================================================================
title1 = Text(
    text='Periodic Table (first 36 elements)', x=960, y=60, font_size=36,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
title1.fadein(0.0, 0.5)
title1.fadeout(2.5, 3.0)
show.add(title1)

periodic = PeriodicTable(cx=960, cy=430, cell_size=42)
periodic.fadein(0.2, 1.0)
periodic.highlight('Fe', start=1.5, end=2.3)
periodic.fadeout(2.5, 3.0)
show.add(periodic)

sub1 = Text(
    text='Color-coded by element category', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle',
)
sub1.fadein(0.5, 1.0)
sub1.fadeout(2.5, 3.0)
show.add(sub1)

# =============================================================================
# Phase 2 (3-6s): ChessBoard
# =============================================================================
title2 = Text(
    text='ChessBoard', x=960, y=60, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=3.0,
)
title2.fadein(3.0, 3.5)
title2.fadeout(5.5, 6.0)
show.add(title2)

board = ChessBoard(
    fen='rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR',
    cx=960, cy=470, size=540, show_coordinates=True,
    creation=3.0,
)
board.fadein(3.0, 3.8)
# Animate a classic response: e7-e5
board.move_piece('e7', 'e5', start=4.2, end=4.8)
board.fadeout(5.5, 6.0)
show.add(board)

sub2 = Text(
    text='FEN-based board with animated piece movement', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=3.0,
)
sub2.fadein(3.3, 3.8)
sub2.fadeout(5.5, 6.0)
show.add(sub2)

# =============================================================================
# Phase 3 (6-9s): BohrAtom
# =============================================================================
title3 = Text(
    text='Bohr Atom Model', x=960, y=60, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=6.0,
)
title3.fadein(6.0, 6.5)
title3.fadeout(8.5, 9.0)
show.add(title3)

# Carbon atom: 6 protons, 6 neutrons, electrons auto-filled [2, 4]
atom = BohrAtom(
    protons=6, neutrons=6, cx=960, cy=480,
    nucleus_r=35, shell_spacing=55,
    creation=6.0,
)
atom.fadein(6.0, 6.8)
atom.orbit(start=6.8, end=9.0, speed=40)
atom.fadeout(8.5, 9.0)
show.add(atom)

sub3 = Text(
    text='Carbon-12 with orbiting electrons', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=6.0,
)
sub3.fadein(6.3, 6.8)
sub3.fadeout(8.5, 9.0)
show.add(sub3)

# =============================================================================
# Phase 4 (9-12s): TimelineBar
# =============================================================================
title4 = Text(
    text='TimelineBar', x=960, y=60, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=9.0,
)
title4.fadein(9.0, 9.5)
title4.fadeout(11.5, 12.0)
show.add(title4)

timeline = TimelineBar(
    markers={
        0: 'Intro',
        2: 'Setup',
        5: 'Core Logic',
        7: 'Testing',
        9: 'Deploy',
        10: 'Done',
    },
    total_duration=10,
    x=200, y=440, width=1520, height=8,
    marker_color='#FFFF00', font_size=18,
    creation=9.0,
)
timeline.fadein(9.0, 9.8)
timeline.fadeout(11.5, 12.0)
show.add(timeline)

sub4 = Text(
    text='Project milestones on a horizontal track', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=9.0,
)
sub4.fadein(9.3, 9.8)
sub4.fadeout(11.5, 12.0)
show.add(sub4)

# =============================================================================
# Phase 5 (12-15s): OrgChart
# =============================================================================
title5 = Text(
    text='OrgChart', x=960, y=40, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=12.0,
)
title5.fadein(12.0, 12.5)
title5.fadeout(14.5, 15.0)
show.add(title5)

# Tree structure: (label, [children])
org_tree = ('CEO', [
    ('CTO', [
        ('Dev Lead', []),
        ('QA Lead', []),
    ]),
    ('CFO', [
        ('Accounting', []),
    ]),
    ('COO', [
        ('Ops Manager', []),
        ('HR', []),
    ]),
])
org = OrgChart(
    root=org_tree, x=960, y=100, h_spacing=200, v_spacing=110,
    box_width=130, box_height=44, font_size=15,
    creation=12.0,
)
org.fadein(12.0, 12.8)
org.fadeout(14.5, 15.0)
show.add(org)

sub5 = Text(
    text='Hierarchical organization structure', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=12.0,
)
sub5.fadein(12.3, 12.8)
sub5.fadeout(14.5, 15.0)
show.add(sub5)

# =============================================================================
# Phase 6 (15-18s): MindMap
# =============================================================================
title6 = Text(
    text='MindMap', x=960, y=40, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=15.0,
)
title6.fadein(15.0, 15.5)
title6.fadeout(17.5, 18.0)
show.add(title6)

# Mind map structure: (label, [children]) — children also have grandchildren
mind = ('Project', [
    ('Design', [
        ('UI', []),
        ('UX', []),
    ]),
    ('Backend', [
        ('API', []),
        ('DB', []),
    ]),
    ('Frontend', [
        ('React', []),
        ('CSS', []),
    ]),
    ('Testing', [
        ('Unit', []),
        ('E2E', []),
    ]),
])
mindmap = MindMap(
    root=mind, cx=960, cy=480, radius=220, font_size=16,
    creation=15.0,
)
mindmap.fadein(15.0, 15.8)
mindmap.fadeout(17.5, 18.0)
show.add(mindmap)

sub6 = Text(
    text='Radial layout with nested topics', x=960, y=880, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=15.0,
)
sub6.fadein(15.3, 15.8)
sub6.fadeout(17.5, 18.0)
show.add(sub6)

# =============================================================================
# Display
# =============================================================================
show.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
