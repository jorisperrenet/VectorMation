"""Code block with syntax highlighting."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

code = Code('''def greet(name):
    return f"Hello, {name}!"

print(greet("World"))''', language='python', x=560, y=350, font_size=28)

v.add(code)

v.show(end=0)
