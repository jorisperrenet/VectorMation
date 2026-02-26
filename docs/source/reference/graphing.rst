Graphing
========

.. image:: ../_static/images/axes_anatomy.svg
   :width: 520
   :align: center

Graph
-----

.. py:class:: Graph(func, x_range=(-5, 5), y_range=None, x=120, y=60, plot_width=1440, plot_height=840, **styling)

   Bases: :py:class:`VCollection`

   Full plot with axes, ticks, labels, and a plotted function curve.

   :param callable func: Function to plot (``f(x) -> y``).
   :param tuple x_range: ``(x_min, x_max)``.
   :param tuple y_range: ``(y_min, y_max)`` or ``None`` for auto.
   :param float x: Plot area left edge.
   :param float y: Plot area top edge.
   :param float plot_width: Plot area width.
   :param float plot_height: Plot area height.

   .. rubric:: Adding Curves

   .. py:method:: add_function(func, **styling)

      Add another function curve to the plot. Returns the :py:class:`Lines` object.

   .. py:method:: plot(func, num_points=200, **styling)

      Plot a function. Returns a :py:class:`Lines` object.

   .. py:method:: plot_line_graph(x_values, y_values, **styling)

      Plot a line graph from data points.

   .. rubric:: Coordinate Conversion

   .. py:method:: coords_to_point(x, y)

      Convert math coordinates to SVG coordinates.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: input_to_graph_point(x, func)

      Get the SVG point on a function at *x*.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: graph_position(func, x_attr)

      Return a lambda that gives the SVG position of a point following a function
      curve as *x_attr* changes over time. Useful with :py:meth:`Coor.set_onward`.

      .. code-block:: python

         x_val = attributes.Real(0, 0)
         x_val.move_to(0, 3, 5)
         dot.c.set_onward(0, graph.graph_position(func, x_val))

   .. rubric:: Decorations

   .. py:method:: get_area(curve, x_range=None, bounded_graph=None, **styling)

      Shaded area under (or between) curves. Returns a :py:class:`Polygon`.

   .. py:method:: get_vertical_line(x, y_val=None, **styling)

      Vertical line at *x*. Returns a :py:class:`Line`.

   .. py:method:: get_riemann_rectangles(func, x_range, dx=0.1, **styling)

      Riemann sum rectangles under a curve. Returns a :py:class:`VCollection`.

----

Axes
----

.. py:class:: Axes(x_range=(-5, 5), y_range=(-5, 5), x=120, y=60, plot_width=1440, plot_height=840, **styling)

   Bases: :py:class:`Graph`

   Standalone coordinate axes. Same constructor and methods as :py:class:`Graph`
   but without an initial function plotted.

----

FunctionGraph
-------------

.. py:class:: FunctionGraph(func, x_range=(-5, 5), y_range=None, num_points=200, x=120, y=60, width=1440, height=840, **styling)

   Bases: :py:class:`Lines`

   Function plot as a polyline (no axes, ticks, or labels).

   :param callable func: Function to plot.
   :param int num_points: Number of sample points.

----

NumberLine
----------

.. image:: ../_static/images/numberline_params.svg
   :width: 500
   :align: center

.. py:class:: NumberLine(x_range=(-5, 5, 1), length=720, x=240, y=540, tick_size=12, include_numbers=True, include_arrows=True, **styling)

   Bases: :py:class:`VCollection`

   Horizontal number line with tick marks and optional labels.

   :param tuple x_range: ``(start, end, step)`` or ``(start, end)`` with auto step.
   :param float length: Line length in pixels.
   :param float tick_size: Tick mark height in pixels.
   :param bool include_numbers: Show tick labels.
   :param bool include_arrows: Show endpoint arrows.

----

PieChart
--------

.. py:class:: PieChart(values, colors=None, cx=960, cy=540, r=240, **styling)

   Bases: :py:class:`VCollection`

   Pie chart from a list of values.

   :param list values: Numeric values for each slice.
   :param list colors: Optional list of fill colours.

----

BarChart
--------

.. py:class:: BarChart(values, colors=None, x=120, y=60, width=1440, height=840, bar_spacing=0.2, **styling)

   Bases: :py:class:`VCollection`

   Bar chart from a list of values.

   :param list values: Numeric values for each bar.
   :param list colors: Optional list of fill colours.
   :param float bar_spacing: Space between bars (as a fraction).
