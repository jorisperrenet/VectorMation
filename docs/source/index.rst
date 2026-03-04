VectorMation
============

**An entirely vector-based math-oriented animation engine.**

VectorMation produces compact SVG animations by treating every visual property as a function of time. Instead of rasterising frames, it generates precise vector graphics that can be played back in a browser, exported as SVGs, or used in presentations.

Quick Start
-----------

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   point = Dot()
   trace = Trace(point.c)
   point.c.set(0, 5, lambda t: (t * 80 + 960, 540))
   point.c.rotate_around(0, 5, (960, 540), 360 * 4)

   canvas.add(trace, point)
   canvas.show(end=6)

This opens a browser window showing a spiral being drawn in real time.

Key Features
------------

- **Time-varying attributes** -- every property (position, colour, opacity, ...) is a function of time
- **Browser-based viewer** -- real-time playback with zoom, speed control, debug panel, and keyboard shortcuts
- **Morphing** -- smoothly morph any shape into any other shape, with optional rotation
- **LaTeX support** -- render LaTeX expressions as animatable SVG objects
- **Graph plotting** -- axes, function graphs, scatter plots, vector fields, polar plots, and more
- **3D rendering** -- 3D axes, surfaces, primitives, and camera rotation with depth-sorted SVG output
- **Charts and diagrams** -- bar charts, pie charts, flowcharts, tree diagrams, Sankey diagrams, and more
- **Physics simulations** -- pendulums, springs, cloth, bouncing objects
- **Sections** -- pause the animation at section breaks for presentation-style delivery
- **Export** -- SVG frames, PNG, MP4/WebM video (via ffmpeg), and animated GIF

Next Steps
----------

- :doc:`Installation <installation>` -- system requirements and setup
- :doc:`Tutorial <tutorial>` -- build your first animation step by step
- :doc:`Reference Manual <reference>` -- complete API reference
- :doc:`Animation & Playback <animation>` -- browser controls, sections, and export

.. toctree::
   :hidden:
   :maxdepth: 2

   installation
   tutorial
   reference
   attributes
   animation
   graphing
   examples
   advanced_examples
   vs_manim
   release_notes
