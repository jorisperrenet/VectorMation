Graphing
========

VectorMation provides two ways to plot mathematical functions: ``Graph`` (full axes, ticks, labels) and ``FunctionGraph`` (bare curve only).

Graph
-----

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *
   import math

   canvas = VectorMathAnim(save_dir='svgs/graph', width=1000, height=1000)
   canvas.set_background()

   graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
                 y_range=(-1.5, 1.5))

   canvas.add_objects(graph)
   canvas.browser_display(end_time=0)

Constructor
^^^^^^^^^^^

.. code-block:: python

   Graph(func, x_range=(-5, 5), y_range=None, num_points=200,
         x=100, y=50, plot_width=800, plot_height=600,
         x_label='x', y_label='y', show_grid=False,
         creation=0, z=0, **styling_kwargs)

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Parameter
     - Description
   * - ``func``
     - A callable ``f(x) -> y``
   * - ``x_range``
     - ``(x_min, x_max)`` in math coordinates
   * - ``y_range``
     - ``(y_min, y_max)`` or ``None`` for auto
   * - ``num_points``
     - Number of sample points for the curve
   * - ``x``, ``y``
     - Top-left position of the plot area in SVG pixels
   * - ``plot_width``, ``plot_height``
     - Size of the plot area in SVG pixels
   * - ``x_label``, ``y_label``
     - Axis labels (set to ``''`` to hide)
   * - ``show_grid``
     - Show grid lines at tick positions
   * - ``**styling_kwargs``
     - Passed to the curve (e.g. ``stroke``, ``stroke_width``)

The default curve colour is ``#58C4DD`` (light blue) with ``stroke_width=3``.

Auto Y-Range
^^^^^^^^^^^^^

If ``y_range`` is not specified, the graph samples the function across the x-range and automatically determines appropriate y-axis bounds with 5% padding.

Adding More Functions
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   cos_curve = graph.add_function(math.cos, stroke='#FC6255')

``add_function()`` returns a ``Path`` object, which you can animate independently:

.. code-block:: python

   cos_curve.create(start=2, end=4)

Animating the Curve
^^^^^^^^^^^^^^^^^^^

The graph's curve is a ``Path`` accessible as ``graph.curve``. You can animate it:

.. code-block:: python

   graph.curve.create(start=0, end=2)      # animate drawing
   graph.curve.fadein(start=0, end=1)      # fade in

Sub-Objects
^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Attribute
     - Type
     - Description
   * - ``graph.curve``
     - ``Path``
     - The main function curve
   * - ``graph.x_min`` / ``x_max``
     - ``Real``
     - Animated x-axis range bounds
   * - ``graph.y_min`` / ``y_max``
     - ``Real``
     - Animated y-axis range bounds

Coordinate Mapping
^^^^^^^^^^^^^^^^^^

The graph provides methods for mapping between math and SVG coordinates:

- Math x/y values are mapped linearly to the SVG plot area
- The y-axis is inverted (SVG y increases downward)
- The axes are positioned at the math origin (0, 0) when it falls within the range
- ``coords_to_point(x, y, time=0)`` converts math coordinates to SVG pixels

Animated Ranges
^^^^^^^^^^^^^^^

The axis ranges (``x_min``, ``x_max``, ``y_min``, ``y_max``) are ``Real`` attributes, so they can be
animated like any other property. Use the convenience methods to animate both ends at once:

.. code-block:: python

   ax.set_x_range(0, 2, (1, 4))           # animate x-axis bounds
   ax.set_y_range(0, 2, (0, 18))          # animate y-axis bounds
   ax.set_ranges(0, 2, (1, 4), (0, 18))   # animate both at once

You can also animate individual bounds directly:

.. code-block:: python

   ax.x_max.move_to(0, 2, 20)  # only change the upper x bound

Full example:

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim(save_dir='svgs/zoom')
   canvas.set_background()

   ax = Axes(x_range=(-5, 5), y_range=(-2, 26))
   curve = ax.plot(lambda x: x ** 2, stroke='#58C4DD')

   # Zoom into x=[1, 4], y=[0, 18]
   ax.set_ranges(0, 2, x_range=(1, 4), y_range=(0, 18))

   canvas.add_objects(ax)
   canvas.browser_display(fps=60)

Axis decorations (lines, ticks, tick labels, grid) automatically re-render each frame to match the
current range. Curves resample the function at each frame too, so everything stays in sync.

Example: Animated Graph
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import math
   from vectormation.objects import *

   canvas = VectorMathAnim(save_dir='svgs/graph_anim')
   canvas.set_background()

   graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
                 y_range=(-1.5, 1.5))

   # Draw sin curve
   graph.curve.create(start=0, end=2)

   # Add and draw cos curve
   cos_curve = graph.add_function(math.cos, stroke='#FC6255')
   cos_curve.create(start=2.5, end=4.5)

   canvas.add_objects(graph)
   canvas.browser_display(fps=60)

----

FunctionGraph
-------------

``FunctionGraph`` plots a function as a bare polyline -- no axes, ticks, or labels. Useful when you only need the curve itself, or want to compose it with other objects.

Constructor
^^^^^^^^^^^

.. code-block:: python

   FunctionGraph(func, x_range=(-5, 5), y_range=None, num_points=200,
                 x=100, y=50, width=800, height=600,
                 creation=0, z=0, **styling_kwargs)

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Parameter
     - Description
   * - ``func``
     - A callable ``f(x) -> y``
   * - ``x_range``
     - ``(x_min, x_max)`` in math coordinates
   * - ``y_range``
     - ``(y_min, y_max)`` or ``None`` for auto
   * - ``num_points``
     - Number of sample points
   * - ``x``, ``y``
     - Top-left position of the plot area in SVG pixels
   * - ``width``, ``height``
     - Size of the plot area in SVG pixels
   * - ``**styling_kwargs``
     - Passed to the polyline (e.g. ``stroke``, ``stroke_width``)

The default curve style is ``stroke='#58C4DD'``, ``stroke_width=3``, ``fill_opacity=0``.

Example
^^^^^^^

.. code-block:: python

   import math
   from vectormation.objects import *

   canvas = VectorMathAnim(save_dir='svgs/func_graph')
   canvas.set_background()

   curve = FunctionGraph(math.sin, x_range=(0, 2 * math.pi),
                         width=600, height=300, x=200, y=350)
   curve.draw_along(start=0, end=2)

   canvas.add_objects(curve)
   canvas.browser_display(fps=60)

``FunctionGraph`` extends ``Lines``, so all ``VObject`` animation methods (fadein, write, shift, etc.) work directly on it.
