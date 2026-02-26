import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/bohr_atom')
canvas.set_background()

# Create a Bohr model of Carbon (6 protons, 6 neutrons, shells: 2 + 4 electrons)
atom = BohrAtom(protons=6, neutrons=6, electrons=[2, 4])
atom.fadein(0, 1)

# Start electrons orbiting
atom.orbit(1, 8)

title = Text(text='Carbon Atom (Bohr Model)', x=960, y=120,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(atom, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
