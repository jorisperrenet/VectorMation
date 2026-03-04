from vectormation.objects import *

# Initialize the canvas
canvas = VectorMathAnim(width=1000, height=1000)

# --- Crystal V shape made of triangular facets ---
# Scaled to fill the 1000x1000 canvas
TL  = (20, 20)      # top left
TR  = (980, 20)     # top right
B   = (500, 970)    # bottom tip
IL  = (270, 20)     # inner top left
IR  = (730, 20)     # inner top right
ML  = (245, 496)    # mid left outer
MR  = (755, 496)    # mid right outer
IML = (385, 496)    # inner mid left
IMR = (616, 496)    # inner mid right

# Left arm facets (blue tones)
canvas.add_objects(
    Polygon(TL, IL, ML,
            fill='#0077B6', fill_opacity=0.9, stroke_width=0, z=5),
    Polygon(IL, IML, ML,
            fill='#00B4D8', fill_opacity=0.85, stroke_width=0, z=5),
    Polygon(TL, ML, B,
            fill='#023E8A', fill_opacity=0.9, stroke_width=0, z=5),
    Polygon(ML, IML, B,
            fill='#0096C7', fill_opacity=0.8, stroke_width=0, z=5),
)

# Right arm facets (purple tones)
canvas.add_objects(
    Polygon(TR, IR, MR,
            fill='#6D28D9', fill_opacity=0.9, stroke_width=0, z=5),
    Polygon(IR, IMR, MR,
            fill='#8B5CF6', fill_opacity=0.85, stroke_width=0, z=5),
    Polygon(TR, MR, B,
            fill='#4C1D95', fill_opacity=0.9, stroke_width=0, z=5),
    Polygon(MR, IMR, B,
            fill='#7C3AED', fill_opacity=0.8, stroke_width=0, z=5),
)

# Center highlight where arms meet
canvas.add_objects(Polygon(
    IML, IMR, B,
    fill='#6B1D5E', fill_opacity=0.55, stroke_width=0, z=6
))

# Export to all logo locations

canvas.show(end=3)
