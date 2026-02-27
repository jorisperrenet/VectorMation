Graphing
========

.. image:: ../_static/images/axes_anatomy.svg
   :width: 520
   :align: center

Graph
-----

.. py:class:: Graph(func, x_range=(-5, 5), y_range=None, x=260, y=100, plot_width=1400, plot_height=880, **styling)

   Bases: :py:class:`Axes`

   Full plot with axes, ticks, labels, and a plotted function curve.

   :param callable func: Function to plot (``f(x) -> y``).
   :param tuple x_range: ``(x_min, x_max)``.
   :param tuple y_range: ``(y_min, y_max)`` or ``None`` for auto.
   :param float x: Plot area left edge.
   :param float y: Plot area top edge.
   :param float plot_width: Plot area width.
   :param float plot_height: Plot area height.

   .. rubric:: Adding Curves

   .. py:method:: add_function(func, label=None, label_direction='up', num_points=200, x_range=None, **styling)

      Add another function curve to the plot. Returns a :py:class:`Path` object.

   .. py:method:: plot(func, label=None, label_direction='up', num_points=200, x_range=None, **styling)

      Plot a function (alias for :py:meth:`add_function`). Returns a :py:class:`Path` object.

   .. py:method:: plot_line_graph(x_values, y_values, **styling)

      Plot a line graph from data points.

   .. rubric:: Coordinate Conversion

   .. py:method:: coords_to_point(x, y, time=0)

      Convert math coordinates to SVG coordinates.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: input_to_graph_point(x, func, time=0)

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

      Shaded area under (or between) curves. Returns a :py:class:`Path`.

   .. py:method:: get_vertical_line(x, y_val=None, **styling)

      Vertical line at *x*. Returns a :py:class:`Line`.

   .. py:method:: get_vertical_lines(func, x_range, dx=1, **styling)

      Multiple vertical lines from x-axis to curve. Returns a :py:class:`VCollection`.

   .. py:method:: get_horizontal_line(y, x_val=None, **styling)

      Horizontal line at *y*. Returns a :py:class:`Line`.

   .. py:method:: get_tangent_line(func, x, length=200, **styling)

      Tangent line to a function at *x*. Returns a :py:class:`Line`.

   .. py:method:: get_secant_line(func, x1, x2, length=200, **styling)

      Secant line through two points on a function. Returns a :py:class:`Line`.

   .. py:method:: get_riemann_rectangles(func, x_range, dx=0.1, **styling)

      Riemann sum rectangles under a curve. Returns a :py:class:`DynamicObject`.

   .. py:method:: get_area_between(func1, func2, x_range=None, **styling)

      Shaded area between two curves. Returns a :py:class:`Path`.

   .. rubric:: Annotations

   .. py:method:: add_coordinates(**styling)

      Add coordinate tick labels to axes.

   .. py:method:: add_grid(**styling)

      Add background grid lines.

   .. py:method:: add_title(text, **styling)

      Add a title above the axes.

   .. py:method:: add_legend(entries, **styling)

      Add a legend with colour swatches. *entries*: list of ``(color, label)`` pairs.

   .. py:method:: add_dot_label(x, func, label, **styling)

      Add a labelled dot at ``(x, func(x))``.

   .. py:method:: add_arrow_annotation(x, func, text, **styling)

      Add a labelled arrow pointing at a curve.

   .. py:method:: add_asymptote(x=None, y=None, **styling)

      Add a dashed asymptote line.

   .. py:method:: highlight_x_range(x1, x2, **styling)

      Shade a vertical strip between *x1* and *x2*.

   .. py:method:: highlight_y_range(y1, y2, **styling)

      Shade a horizontal strip between *y1* and *y2*.

   .. rubric:: Plot Types

   .. py:method:: plot_scatter(x_values, y_values, **styling)

      Scatter plot with dots.

   .. py:method:: plot_step(x_values, y_values, **styling)

      Step function plot from paired x/y value lists.

   .. py:method:: plot_polar(func, **styling)

      Polar function plot.

   .. py:method:: plot_implicit(func, **styling)

      Implicit curve ``f(x, y) = 0`` via marching squares.

   .. py:method:: plot_histogram(values, bins=10, **styling)

      Histogram from raw data.

   .. py:method:: plot_vector_field(func, **styling)

      Vector field overlay on axes.

   .. rubric:: Animated Ranges

   .. py:method:: animate_range(start, end, x_range=None, y_range=None, easing=smooth)

      Animate the axis range to new bounds. Curves resample automatically.

      :param tuple x_range: ``(new_xmin, new_xmax)`` or ``None``.
      :param tuple y_range: ``(new_ymin, new_ymax)`` or ``None``.

----

Axes
----

.. py:class:: Axes(x_range=(-5, 5), y_range=None, x=260, y=100, plot_width=1400, plot_height=880, **styling)

   Bases: :py:class:`VCollection`

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

.. py:class:: NumberLine(x_range=(-5, 5, 1), length=720, x=240, y=540, tick_size=28, include_numbers=True, include_arrows=True, **styling)

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

.. py:class:: PieChart(values, labels=None, colors=None, cx=960, cy=540, r=240, **styling)

   Bases: :py:class:`VCollection`

   Pie chart from a list of values.

   :param list values: Numeric values for each slice.
   :param list colors: Optional list of fill colours.

----

BarChart
--------

.. py:class:: BarChart(values, labels=None, colors=None, x=120, y=60, width=1440, height=840, bar_spacing=0.2, **styling)

   Bases: :py:class:`VCollection`

   Bar chart from a list of values.

   :param list values: Numeric values for each bar.
   :param list colors: Optional list of fill colours.
   :param float bar_spacing: Space between bars (as a fraction).

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Smoothly transition bars to new values.

   .. py:method:: add_bar(value, label=None, color=None, start=0, end=0.5)

      Animate adding a new bar.

   .. py:method:: remove_bar(index=-1, start=0, end=0.5)

      Animate removing a bar.

   .. py:method:: animate_sort(key=None, reverse=False, start=0, end=1)

      Animate bars sliding into sorted order.

----

DonutChart
----------

.. py:class:: DonutChart(values, labels=None, colors=None, cx=960, cy=540, r=240, inner_radius=120, **styling)

   Bases: :py:class:`VCollection`

   Donut chart (pie chart with a hole).

----

RadarChart
----------

.. py:class:: RadarChart(values, labels=None, max_val=None, cx=960, cy=540, radius=250, **styling)

   Bases: :py:class:`VCollection`

   Radar/spider chart with concentric rings and data polygon.

----

ComplexPlane
------------

.. py:class:: ComplexPlane(x_range=(-5, 5), y_range=(-5, 5), show_grid=True, **styling)

   Bases: :py:class:`Axes`

   Complex number plane with real/imaginary axes.

   .. py:method:: number_to_point(z)

      Convert a complex number to SVG coordinates.

----

PolarAxes
---------

.. py:class:: PolarAxes(r_range=(0, 5), cx=960, cy=540, radius=400, **styling)

   Bases: :py:class:`VCollection`

   Polar coordinate axes with radial and angular grid lines.

   .. py:method:: polar_to_point(r, theta)

      Convert polar coordinates to SVG coordinates.

----

NumberPlane
-----------

.. py:class:: NumberPlane(x_range=None, y_range=None, cx=960, cy=540, width=1920, height=1080, **styling)

   Bases: :py:class:`VCollection`

   Full coordinate grid (background grid with axes).
