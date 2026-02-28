Graphing
========

.. image:: ../_static/images/axes_anatomy.svg
   :width: 520
   :align: center

.. code-block:: python

   from vectormation.objects import *

Graph
-----

.. py:class:: Graph(func, x_range=(-5, 5), y_range=None, x=260, y=100, plot_width=1400, plot_height=880, **styling)

   Bases: :py:class:`Axes`

   Full plot with axes, ticks, labels, and a plotted function curve.
   The most common starting point for mathematical visualizations.

   :param callable func: Function to plot (``f(x) -> y``).
   :param tuple x_range: ``(x_min, x_max)`` or ``(x_min, x_max, step)``.
   :param tuple y_range: ``(y_min, y_max)`` or ``None`` for auto-ranging.
   :param float x: Plot area left edge in SVG coordinates.
   :param float y: Plot area top edge in SVG coordinates.
   :param float plot_width: Plot area width in pixels.
   :param float plot_height: Plot area height in pixels.

   .. code-block:: python

      # Simple sine curve
      g = Graph(math.sin, x_range=(-2*math.pi, 2*math.pi), y_range=(-1.5, 1.5))
      g.fadein(start=0, end=1)
      v.add(g)

   .. code-block:: python

      # Quadratic with annotations
      g = Graph(lambda x: x**2 - 3, x_range=(-4, 4), y_range=(-4, 14))
      g.add_coordinates()
      g.add_grid(stroke='#333', stroke_width=0.5)
      g.add_dot_label(2, lambda x: x**2 - 3, "min", fill='#E74C3C')
      v.add(g)

   .. rubric:: Adding Curves

   .. py:method:: add_function(func, label=None, label_direction='up', num_points=200, x_range=None, **styling)

      Add another function curve to the plot. Returns a :py:class:`Path` object
      whose ``d`` attribute is dynamically recalculated when axes ranges change.

      :param callable func: Function ``f(x) -> y``.
      :param str label: Optional text label near the curve.
      :param str label_direction: Placement of label (``'up'``, ``'down'``, ``'left'``, ``'right'``).
      :param int num_points: Sampling resolution for the curve.
      :param tuple x_range: Override x-range for this curve only.

   .. py:method:: plot(func, label=None, label_direction='up', num_points=200, x_range=None, **styling)

      Alias for :py:meth:`add_function`. Returns a :py:class:`Path` object.

   .. py:method:: plot_line_graph(x_values, y_values, **styling)

      Plot a line graph from data points. Connects the points with line segments.

      .. code-block:: python

         g = Axes(x_range=(0, 10), y_range=(0, 100))
         g.plot_line_graph([1, 3, 5, 7, 9], [20, 45, 30, 80, 60], stroke='#E74C3C')

   .. rubric:: Coordinate Conversion

   .. py:method:: coords_to_point(x, y, time=0)

      Convert math coordinates ``(x, y)`` to SVG pixel coordinates.
      Respects animated axis ranges.

      :param float x: Mathematical x-coordinate.
      :param float y: Mathematical y-coordinate.
      :param float time: Time for animated ranges.
      :returns: ``(svg_x, svg_y)``

   .. py:method:: input_to_graph_point(x, func, time=0)

      Get the SVG point on a function at mathematical x-value.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: graph_position(func, x_attr)

      Return a lambda that gives the SVG position of a point following a function
      curve as *x_attr* changes over time. Useful for animating dots along curves.

      .. code-block:: python

         x_val = attributes.Real(0, 0)
         x_val.move_to(0, 3, 5)  # animate x from 0 to 5 over t=0..3
         dot.c.set_onward(0, graph.graph_position(func, x_val))

   .. rubric:: Areas and Shading

   .. py:method:: get_area(curve_or_func, x_range=None, bounded_graph=None, **styling)

      Shaded area under a curve (or between two curves). Returns a :py:class:`Path`
      that dynamically updates when axis ranges change.

      :param curve_or_func: A Path returned by :py:meth:`plot`, or a callable.
      :param tuple x_range: ``(x_min, x_max)`` to restrict the shaded region.
      :param bounded_graph: Another curve to shade between.

      .. code-block:: python

         g = Graph(math.sin, x_range=(0, 2*math.pi), y_range=(-1.5, 1.5))
         curve = g.plot(math.sin, stroke='#3498DB')
         area = g.get_area(curve, x_range=(0, math.pi), fill='#3498DB', fill_opacity=0.3)
         v.add(g, area)

   .. py:method:: get_area_between(func1, func2, x_range=None, **styling)

      Shaded area between two curves. Returns a :py:class:`Path`.

      .. code-block:: python

         g = Axes(x_range=(-3, 3), y_range=(-2, 10))
         g.plot(lambda x: x**2, stroke='#E74C3C')
         g.plot(lambda x: 2*x + 1, stroke='#3498DB')
         area = g.get_area_between(lambda x: x**2, lambda x: 2*x + 1,
                                    x_range=(-1, 3), fill='#F39C12', fill_opacity=0.3)

   .. py:method:: get_riemann_rectangles(func, x_range, dx=0.1, **styling)

      Riemann sum rectangles under a curve. Returns a :py:class:`DynamicObject`
      that rebuilds rectangles each frame (supports animated ranges).

      :param callable func: Function to integrate.
      :param tuple x_range: ``(x_min, x_max)`` range for rectangles.
      :param float dx: Width of each rectangle in math units.

      .. code-block:: python

         g = Graph(lambda x: x**2, x_range=(0, 3), y_range=(0, 10))
         rects = g.get_riemann_rectangles(lambda x: x**2, (0, 3), dx=0.3,
                                           fill='#3498DB', fill_opacity=0.4)
         v.add(g, rects)

   .. rubric:: Lines and Markers

   .. py:method:: get_vertical_line(x, y_val=None, **styling)

      Vertical line at mathematical *x*. If *y_val* is given, draws from x-axis
      to that value; otherwise draws to the top of the plot. Returns a :py:class:`Line`.

   .. py:method:: get_vertical_lines(func, x_range, dx=1, **styling)

      Multiple vertical lines from x-axis to curve. Returns a :py:class:`VCollection`.

   .. py:method:: get_horizontal_line(y, x_val=None, **styling)

      Horizontal line at mathematical *y*. Returns a :py:class:`Line`.

   .. py:method:: get_tangent_line(func, x, length=200, **styling)

      Tangent line to a function at *x* (numerical derivative). Returns a :py:class:`Line`.

      .. code-block:: python

         g = Graph(math.sin, x_range=(0, 2*math.pi))
         tangent = g.get_tangent_line(math.sin, math.pi/4, stroke='#E74C3C')
         v.add(g, tangent)

   .. py:method:: get_secant_line(func, x1, x2, length=200, **styling)

      Secant line through two points on a function. Returns a :py:class:`Line`.

   .. py:method:: get_dashed_line(x1, y1, x2, y2, **styling)

      Dashed line between two math coordinates. Returns a :py:class:`Line`.

   .. py:method:: get_line_from_to(x1, y1, x2, y2, **styling)

      Solid line between two math coordinates. Returns a :py:class:`Line`.

   .. py:method:: get_rect(x, func, width=None, **styling)

      A single rectangle from the x-axis to ``func(x)`` at the given x-value.
      Uses animated lambdas for dynamic updates.

   .. rubric:: Annotations and Labels

   .. py:method:: add_coordinates(**styling)

      Add coordinate tick labels to both axes.

   .. py:method:: add_grid(**styling)

      Add background grid lines aligned to tick marks.

      :param stroke: Grid line color (default ``'#333'``).
      :param stroke_width: Grid line width.

   .. py:method:: add_title(text, **styling)

      Add a title above the axes.

   .. py:method:: add_legend(entries, **styling)

      Add a legend with colour swatches.

      :param list entries: List of ``(color, label)`` pairs.

      .. code-block:: python

         g = Axes(x_range=(-5, 5), y_range=(-2, 2))
         g.plot(math.sin, stroke='#E74C3C', label='sin(x)')
         g.plot(math.cos, stroke='#3498DB', label='cos(x)')
         g.add_legend([('#E74C3C', 'sin(x)'), ('#3498DB', 'cos(x)')])

   .. py:method:: add_dot_label(x, func, label, **styling)

      Add a labelled dot at ``(x, func(x))``.

   .. py:method:: add_arrow_annotation(x, func, text, **styling)

      Add a labelled arrow pointing at a curve.

   .. py:method:: add_asymptote(x=None, y=None, **styling)

      Add a dashed asymptote line (vertical at *x* or horizontal at *y*).

   .. py:method:: add_horizontal_label(y, text, **styling)

      Add a text label at a horizontal line value.

   .. py:method:: add_vertical_label(x, text, **styling)

      Add a text label at a vertical line value.

   .. py:method:: coords_label(x, y, text=None, **styling)

      Add a coordinate label at ``(x, y)`` showing the coordinates.

   .. py:method:: add_cursor(**styling)

      Add an interactive cursor dot that follows the mouse (browser mode only).

   .. py:method:: add_trace(func, **styling)

      Add a trace dot that follows a function curve.

   .. rubric:: Shading Regions

   .. py:method:: highlight_x_range(x1, x2, **styling)

      Shade a vertical strip between *x1* and *x2*.

   .. py:method:: highlight_y_range(y1, y2, **styling)

      Shade a horizontal strip between *y1* and *y2*.

   .. rubric:: Statistical and Advanced Plots

   .. py:method:: plot_scatter(x_values, y_values, **styling)

      Scatter plot with dots at each data point.

   .. py:method:: plot_step(x_values, y_values, **styling)

      Step function plot from paired x/y value lists.

   .. py:method:: plot_polar(func, **styling)

      Polar function plot (``r = f(theta)``).

   .. py:method:: plot_implicit(func, **styling)

      Implicit curve ``f(x, y) = 0`` via marching squares algorithm.

   .. py:method:: plot_histogram(values, bins=10, **styling)

      Histogram from raw data values.

   .. py:method:: plot_vector_field(func, **styling)

      Vector field overlay on axes. *func* takes ``(x, y)`` and returns ``(dx, dy)``.

   .. rubric:: Vectors, Intervals, and Regression

   .. py:method:: add_vector(x, y, **styling)

      Add a vector arrow from the origin to ``(x, y)``.

   .. py:method:: add_interval(x1, x2, y=0, **styling)

      Add a horizontal interval marker between *x1* and *x2*.

   .. py:method:: add_zero_line(**styling)

      Add a horizontal line at ``y = 0``.

   .. py:method:: add_slope_field(func, **styling)

      Add a slope field (tangent segments at grid points).

   .. py:method:: add_regression_line(x_values, y_values, **styling)

      Add a least-squares regression line.

   .. py:method:: add_error_bars(x_values, y_values, errors, **styling)

      Add error bars at data points.

   .. py:method:: add_min_max_labels(func, x_range=None, **styling)

      Add labels at the minimum and maximum of a function.

   .. py:method:: add_secant_fade(func, x, dx_start=2, dx_end=0.01, **styling)

      Animate a secant line converging to a tangent as ``dx`` shrinks.

   .. rubric:: Animated Ranges

   The axis attributes ``x_min``, ``x_max``, ``y_min``, ``y_max`` are animatable
   :py:class:`Real` attributes. All curves and decorations automatically
   resample when ranges change.

   .. py:method:: animate_range(start, end, x_range=None, y_range=None, easing=smooth)

      Animate the axis range to new bounds.

      :param tuple x_range: ``(new_xmin, new_xmax)`` or ``None``.
      :param tuple y_range: ``(new_ymin, new_ymax)`` or ``None``.

      .. code-block:: python

         g = Graph(math.sin, x_range=(-5, 5), y_range=(-2, 2))
         g.animate_range(start=1, end=3, x_range=(-1, 1), y_range=(-1.5, 1.5))

----

Axes
----

.. py:class:: Axes(x_range=(-5, 5), y_range=None, x=260, y=100, plot_width=1400, plot_height=880, **styling)

   Bases: :py:class:`VCollection`

   Standalone coordinate axes without an initial function plotted.
   Has all the same methods as :py:class:`Graph`.

   Use when you want to build up a plot incrementally by adding functions,
   scatter plots, and annotations separately.

   .. code-block:: python

      ax = Axes(x_range=(0, 10), y_range=(0, 100))
      ax.add_grid()
      ax.add_coordinates()
      curve1 = ax.plot(lambda x: x**2, stroke='#E74C3C', label='x²')
      curve2 = ax.plot(lambda x: 10*x, stroke='#3498DB', label='10x')
      ax.add_legend([('#E74C3C', 'x²'), ('#3498DB', '10x')])
      v.add(ax)

----

FunctionGraph
-------------

.. py:class:: FunctionGraph(func, x_range=(-5, 5), y_range=None, num_points=200, x=120, y=60, width=1440, height=840, **styling)

   Bases: :py:class:`Lines`

   Function plot as a polyline (no axes, ticks, or labels).
   Use when you need a lightweight function curve without the overhead of Axes.

   :param callable func: Function to plot.
   :param int num_points: Number of sample points.

   .. code-block:: python

      curve = FunctionGraph(lambda x: math.sin(x) * math.exp(-x/5),
                            x_range=(0, 20), stroke='#2ECC71', stroke_width=3)
      curve.create(start=0, end=2)

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

   .. py:method:: number_to_point(value)

      Convert a number to its SVG x-coordinate on the line.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: point_to_number(x, y=None)

      Convert an SVG x-coordinate (or ``(x, y)`` tuple) back to a number.

   .. py:method:: add_pointer(value, label=None, color='#FF6B6B', size=12, creation=0, z=1)

      Add an animated pointer triangle above the number line at *value*.

   .. py:method:: add_dot_at(value, **styling)

      Add a dot at the given value on the number line.

   .. py:method:: add_label(value, text, buff=10, font_size=24, side='below', **kwargs)

      Add a text label at a given value on the line.

   .. py:method:: add_segment(v1, v2, **styling)

      Highlight a segment of the line between two values.

   .. code-block:: python

      nl = NumberLine(x_range=(-3, 3, 1), length=800)
      nl.add_pointer(1.5, label='x')
      nl.add_segment(-1, 2, fill='#3498DB', fill_opacity=0.3)
      v.add(nl)

----

NumberPlane
-----------

.. py:class:: NumberPlane(x_range=None, y_range=None, cx=960, cy=540, width=1920, height=1080, **styling)

   Bases: :py:class:`VCollection`

   Full coordinate grid (background grid with axes).
   Covers the entire canvas by default — useful as a background layer.

   :param tuple x_range: ``(x_min, x_max)`` or ``None`` for auto.
   :param tuple y_range: ``(y_min, y_max)`` or ``None`` for auto.

   .. py:method:: coords_to_point(x, y)

      Convert math coordinates to SVG coordinates.

   .. py:method:: point_to_coords(px, py)

      Convert SVG coordinates to math coordinates.

   .. py:method:: get_vector(x, y, creation=0, **kwargs)

      Create a vector :py:class:`Arrow` from the origin to ``(x, y)`` and add it to the plane.

   .. py:method:: apply_complex_function(func, start=0, end=1, easing=smooth)

      Animate a complex-valued transformation of the grid.

   .. code-block:: python

      plane = NumberPlane(x_range=(-5, 5), y_range=(-5, 5))
      plane.apply_complex_function(lambda z: z**2, start=1, end=3)
      v.add(plane)

----

ComplexPlane
------------

.. py:class:: ComplexPlane(x_range=(-5, 5), y_range=(-5, 5), show_grid=True, **styling)

   Bases: :py:class:`Axes`

   Complex number plane with real/imaginary axes and gridlines.
   Provides conversion between complex numbers and SVG coordinates.

   .. py:method:: number_to_point(z)

      Convert a complex number to SVG coordinates.

      :param complex z: Complex number.
      :returns: ``(svg_x, svg_y)``

   .. py:method:: point_to_number(px, py)

      Convert SVG coordinates to a complex number.

   .. py:method:: add_complex_label(z, text=None, **styling)

      Add a labelled dot at the complex number *z*.

   .. code-block:: python

      cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
      cp.add_complex_label(1+2j, 'z₁')
      cp.add_complex_label(-1+1j, 'z₂')
      v.add(cp)

----

PolarAxes
---------

.. py:class:: PolarAxes(r_range=(0, 5), cx=960, cy=540, radius=400, **styling)

   Bases: :py:class:`VCollection`

   Polar coordinate axes with radial and angular grid lines.

   :param tuple r_range: ``(r_min, r_max)`` for the radial axis.
   :param float cx: Center x.
   :param float cy: Center y.
   :param float radius: Radius of the outermost circle in pixels.

   .. py:method:: polar_to_point(r, theta)

      Convert polar coordinates ``(r, theta)`` to SVG coordinates.

   .. code-block:: python

      pa = PolarAxes(r_range=(0, 3), radius=300)
      pa.fadein(start=0, end=1)
      v.add(pa)

----

PieChart
--------

.. py:class:: PieChart(values, labels=None, colors=None, cx=960, cy=540, r=240, **styling)

   Bases: :py:class:`VCollection`

   Pie chart from a list of values. Supports animated value changes.

   :param list values: Numeric values for each slice.
   :param list labels: Optional text labels.
   :param list colors: Optional list of fill colours (defaults to palette).

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Smoothly transition slice sizes to new values.

   .. code-block:: python

      pie = PieChart([30, 20, 50], labels=['A', 'B', 'C'])
      pie.fadein(start=0, end=1)
      pie.animate_values([40, 40, 20], start=2, end=3)

----

BarChart
--------

.. py:class:: BarChart(values, labels=None, colors=None, x=120, y=60, width=1440, height=840, bar_spacing=0.2, **styling)

   Bases: :py:class:`VCollection`

   Bar chart from a list of values. Supports animations for adding, removing,
   reordering, and updating bar values.

   :param list values: Numeric values for each bar.
   :param list colors: Optional list of fill colours.
   :param float bar_spacing: Space between bars (as a fraction, 0-1).

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Smoothly transition bars to new values.

   .. py:method:: add_bar(value, label=None, color=None, start=0, end=0.5)

      Animate adding a new bar to the chart.

   .. py:method:: remove_bar(index=-1, start=0, end=0.5)

      Animate removing a bar.

   .. py:method:: animate_sort(key=None, reverse=False, start=0, end=1)

      Animate bars sliding into sorted order.

   .. py:method:: get_bar_by_label(label)

      Return the bar matching the given label text, or None.

   .. py:method:: get_tallest_bar()

      Return the tallest bar Rectangle.

   .. py:method:: get_shortest_bar()

      Return the shortest bar Rectangle.

   .. code-block:: python

      bc = BarChart([3, 7, 2, 5], labels=['Q1', 'Q2', 'Q3', 'Q4'],
                    colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12'])
      bc.fadein(start=0, end=1)
      bc.animate_sort(start=2, end=3)

----

DonutChart
----------

.. py:class:: DonutChart(values, labels=None, colors=None, cx=960, cy=540, r=240, inner_radius=120, **styling)

   Bases: :py:class:`VCollection`

   Donut chart (pie chart with a hole). Same animation support as PieChart.

----

RadarChart
----------

.. py:class:: RadarChart(values, labels=None, max_val=None, cx=960, cy=540, radius=250, **styling)

   Bases: :py:class:`VCollection`

   Radar/spider chart with concentric rings and a data polygon.

   :param list values: Values for each axis (normalized to ``max_val``).
   :param list labels: Axis labels.
   :param float max_val: Maximum value (default: ``max(values)``).

   .. code-block:: python

      rc = RadarChart(labels=['Speed', 'Power', 'Defense', 'Magic', 'HP'],
                      values=[0.8, 0.5, 0.9, 0.3, 0.7])

----

Tick Formatters
---------------

Custom tick label formatters for axes and number lines:

.. py:function:: pi_format(value)

   Format values as multiples of π (e.g. ``0.5`` → ``π/2``).

.. py:function:: pi_ticks(n=4)

   Generate tick positions at multiples of π.

.. py:function:: pi_tex_format(value)

   Format values as LaTeX multiples of π.

.. py:function:: log_tex_format(base=10)

   Return a formatter for logarithmic tick labels (e.g. ``10²``).

.. py:function:: scientific_format(precision=2)

   Scientific notation formatter (e.g. ``1.23 × 10³``).

.. py:function:: engineering_format(precision=2)

   Engineering notation (exponents are multiples of 3).

.. py:function:: percent_format(precision=0)

   Format as percentage (e.g. ``0.5`` → ``50%``).

.. py:function:: degree_format(precision=0)

   Format as degrees (e.g. ``90`` → ``90°``).

.. code-block:: python

   from vectormation.objects import pi_format, pi_ticks

   g = Graph(math.sin, x_range=(-2*math.pi, 2*math.pi))
   g.x_tick_format = pi_format
   g.x_tick_positions = pi_ticks(4)

----

Examples
--------

**Animated Function with Tangent Line**

.. code-block:: python

   v = VectorMathAnim(duration=6)
   g = Graph(lambda x: x**3 - 3*x, x_range=(-3, 3), y_range=(-5, 5))
   g.add_coordinates()
   g.add_grid(stroke='#222')
   g.fadein(start=0, end=1)

   # Animated tangent
   x_val = attributes.Real(0, -2)
   x_val.move_to(0, 5, 2)
   tangent = g.get_tangent_line(lambda x: x**3 - 3*x, -2, stroke='#E74C3C')
   v.add(g, tangent)

**Riemann Sum Convergence**

.. code-block:: python

   v = VectorMathAnim(duration=5)
   g = Graph(lambda x: x**2, x_range=(0, 3), y_range=(0, 10))
   g.fadein(start=0, end=1)
   rects = g.get_riemann_rectangles(lambda x: x**2, (0, 3), dx=0.5,
                                     fill='#3498DB', fill_opacity=0.4)
   v.add(g, rects)

**Multiple Curves with Legend**

.. code-block:: python

   v = VectorMathAnim(duration=4)
   ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
   ax.plot(math.sin, stroke='#E74C3C')
   ax.plot(math.cos, stroke='#3498DB')
   ax.plot(lambda x: math.sin(2*x), stroke='#2ECC71')
   ax.add_legend([
       ('#E74C3C', 'sin(x)'),
       ('#3498DB', 'cos(x)'),
       ('#2ECC71', 'sin(2x)'),
   ])
   ax.fadein(start=0, end=1)
   v.add(ax)

**Complex Plane Transformation**

.. code-block:: python

   v = VectorMathAnim(duration=5)
   cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
   cp.fadein(start=0, end=1)
   cp.apply_complex_function(lambda z: z**2, start=2, end=4)
   v.add(cp)
