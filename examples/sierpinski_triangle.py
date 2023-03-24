from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/sierpinski_triangle')
canvas.set_background()

# Draw the objects
# NOTE: TODO: Speed up all corresponding functions
tr = EquilateralTriangle(14, fill='white', fill_opacity=1, stroke_width=0)
# We build the triangle recursively (instead of dynamically for more of a challenge)
tr = VCollection(tr)
for level in range(6):
    print(f'At level {level}')
    xmin, ymin, width, height = tr.bbox(0)
    lu, ru, um = (xmin, ymin+height), (xmin+width, ymin+height), (xmin+width/2, ymin)
    tr.center_to_pos(posx=lu[0], posy=lu[1])
    tr2 = deepcopy(tr)
    tr2.center_to_pos(posx=ru[0], posy=ru[1])
    tr3 = deepcopy(tr)
    tr3.center_to_pos(posx=um[0], posy=um[1])
    tr.objects.extend(tr2.objects)
    tr.objects.extend(tr3.objects)

# Add the objects to the canvas
canvas.add_objects(tr)

# Display the window
canvas.standard_display(fps=60)
