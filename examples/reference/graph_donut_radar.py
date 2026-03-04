"""DonutChart and RadarChart side by side."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

donut = DonutChart([40, 25, 20, 15],
                   labels=['Python', 'JS', 'Rust', 'Go'],
                   cx=480, cy=540, r=220, inner_radius=110)

radar = RadarChart(values=[0.9, 0.6, 0.8, 0.4, 0.7],
                   labels=['Speed', 'Power', 'Defense', 'Magic', 'HP'],
                   cx=1440, cy=540, radius=220)

v.add(donut, radar)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/graph_donut_radar.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=1)
