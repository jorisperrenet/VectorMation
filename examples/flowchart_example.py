import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/flowchart')
canvas.set_background()

title = Text(text='FlowChart Example', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Horizontal flow chart
flow_h = FlowChart(
    ['Input', 'Process', 'Validate', 'Output'],
    direction='right', x=200, y=200,
    box_width=250, box_height=60, spacing=100,
    box_color='#58C4DD', font_size=22,
)
flow_h.stagger('fadein', start=0.5, end=1)

# Vertical flow chart
flow_v = FlowChart(
    ['Start', 'Check', 'Execute', 'Done'],
    direction='down', x=800, y=400,
    box_width=200, box_height=50, spacing=60,
    box_color='#83C167', font_size=20,
)
flow_v.stagger('fadein', start=2, end=2.5)

canvas.add_objects(flow_h, flow_v, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/flowchart_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
