Charts
======

Chart and data visualization classes. All charts inherit from
:py:class:`VCollection` (unless noted) and can be animated, positioned,
and styled like any other object.

----

PieChart
--------

.. py:class:: PieChart(values, labels=None, colors=None, cx=960, cy=540, r=240, start_angle=90, creation=0, z=0)

   Pie chart built from ``Wedge`` sectors.

   :param list values: Numeric values for each sector.
   :param list labels: Optional labels placed inside sectors.
   :param list colors: Sector fill colors (cycles through defaults if ``None``).
   :param float r: Outer radius.

   .. py:classmethod:: from_dict(data, **kwargs)

      Create a ``PieChart`` from a ``{label: value}`` dictionary.

   .. py:method:: get_sector(index)

      Return the ``Wedge`` object at *index*.

   .. py:method:: highlight_sector(index, start=0, end=1, pull_distance=30, easing=there_and_back)

      Pull a sector outward to highlight it.

   .. py:method:: explode(indices, distance=20, start=0, end=None, easing=smooth)

      Permanently shift the given sectors outward.

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Animate sector angles to reflect *new_values*.

   .. py:method:: add_percentage_labels(fmt='{:.0f}%', font_size=16, color='#fff', creation=0)

      Add percentage text inside each sector.

   .. code-block:: python

      pie = PieChart([30, 20, 50], labels=['A', 'B', 'C'])
      pie.highlight_sector(2, start=0, end=1)

----

DonutChart
----------

.. py:class:: DonutChart(values, labels=None, colors=None, cx=960, cy=540, r=240, inner_radius=120, start_angle=90, center_text=None, font_size=17, creation=0, z=0)

   Donut (ring) chart -- a ``PieChart`` with a hollow center.

   :param float inner_radius: Inner ring radius.
   :param str center_text: Optional text displayed in the hole.

   .. py:classmethod:: from_dict(data, **kwargs)

      Create a ``DonutChart`` from a ``{label: value}`` dictionary.

   .. py:method:: get_sector(index)

      Return the ``Path`` object for the sector at *index*.

   .. py:method:: highlight_sector(index, start=0, end=1, pull_distance=30, easing=there_and_back)

      Pull a sector outward to highlight it.

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Animate sector paths to new proportions.

----

BarChart
--------

.. py:class:: BarChart(values, labels=None, colors=None, x=120, y=60, width=1440, height=840, bar_spacing=0.2, creation=0, z=0)

   Simple bar chart with a baseline and optional labels.

   :param list values: Numeric bar heights.
   :param list labels: Category labels below bars.
   :param float bar_spacing: Fraction of bar width used as gap (0--1).

   .. py:classmethod:: from_dict(data, **kwargs)

      Create a ``BarChart`` from a ``{label: value}`` dictionary.

   .. py:method:: animate_values(new_values, start=0, end=1, easing=smooth)

      Animate bars to new heights.

   .. py:method:: set_bar_color(index, color, start=0, end=None, easing=smooth)

      Change the fill color of one bar.

   .. py:method:: set_bar_colors(colors, start=0)

      Set all bar colors at once.

   .. py:method:: get_bar(index)

      Return the ``Rectangle`` for bar *index*.

   .. py:method:: get_bars(start_idx=None, end_idx=None)

      Return a ``VCollection`` of bars, optionally sliced.

   .. py:method:: highlight_bar(index, color='#FFFF00', start=0, end=None, opacity=None)

      Highlight a single bar.

   .. py:method:: get_bar_by_label(label)

      Return the bar matching a label string, or ``None``.

   .. py:method:: add_value_labels(fmt='{:.0f}', offset=10, font_size=20, creation=0)

      Place value text above each bar.

   .. py:method:: grow_from_zero(start=0, end=1, easing=smooth, stagger=True, delay=0.1)

      Animate bars growing from the baseline.

   .. py:method:: get_max_bar()

      Return the ``Rectangle`` with the highest value.

   .. py:method:: get_min_bar()

      Return the ``Rectangle`` with the lowest value.

   .. py:method:: add_bar(value, label=None, start=0, end=None)

      Append a new bar to the right side of the chart.

   .. py:method:: remove_bar(index, start=0, end=None)

      Remove a bar by index, optionally with a shrink animation.

   .. py:method:: animate_sort(key=None, reverse=False, start=0, end=1, easing=smooth)

      Smoothly slide bars into sorted order. Alias: ``sort_bars``.

   .. code-block:: python

      chart = BarChart.from_dict({'Q1': 40, 'Q2': 65, 'Q3': 50})
      chart.grow_from_zero(start=0, end=1.5)

----

RadarChart
----------

.. py:class:: RadarChart(values, labels=None, max_val=None, colors=None, cx=960, cy=540, radius=250, font_size=16, fill_opacity=0.3, creation=0, z=0)

   Radar (spider) chart. Requires at least 3 values.

   :param list values: Data values, one per axis.
   :param list labels: Axis labels around the perimeter.
   :param float max_val: Maximum data value (auto-detected if ``None``).

   .. py:classmethod:: from_dict(data, **kwargs)

      Create a ``RadarChart`` from a ``{label: value}`` dictionary.

   .. py:method:: add_dataset(values, color=None, fill_opacity=None, creation=0, z=0.15)

      Add an additional data polygon overlay to the radar chart.

----

PolarAxes
---------

.. py:class:: PolarAxes(cx=960, cy=540, max_radius=400, r_range=(0, 5), n_rings=5, n_sectors=12, creation=0, z=0)

   Polar coordinate system with concentric rings and angular gridlines.

   :param float max_radius: Outer radius in pixels.
   :param tuple r_range: ``(min, max)`` radial data range.
   :param int n_rings: Number of concentric rings.
   :param int n_sectors: Number of angular sector lines.

   .. py:method:: polar_to_point(r, theta_deg)

      Convert polar ``(r, theta)`` to SVG pixel coordinates.

   .. py:method:: plot_polar(func, theta_range=(0, 360), num_points=200, creation=0, z=0, **styling)

      Plot ``r = func(theta_deg)`` as a polyline on these axes. Returns the ``Lines`` object.

----

Legend
------

.. py:class:: Legend(items, x=100, y=100, swatch_size=16, spacing=8, font_size=16, direction='down', creation=0, z=0)

   Chart legend with colored swatches and text labels.

   :param list items: List of ``(color, label)`` tuples.
   :param str direction: ``'down'`` for vertical, ``'right'`` for horizontal.

----

ProgressBar
-----------

.. py:class:: ProgressBar(width=400, height=30, x=760, y=520, bg_color='#333', fill_color='#58C4DD', corner_radius=6, creation=0, z=0)

   Animated progress bar that fills from left to right.

   .. py:method:: set_progress(value, start=0, end=None, easing=smooth)

      Set progress (0 to 1). Animates if *end* is given.

   .. py:method:: animate_to(value, start=0, end=1, easing=smooth)

      Animate progress to a target value (0--1).

   .. py:method:: get_progress(time=0)

      Return the current progress value (0--1) at the given time.

   .. code-block:: python

      bar = ProgressBar()
      bar.animate_to(0.75, start=0, end=2)

----

SampleSpace
-----------

.. py:class:: SampleSpace(width=500, height=400, x=710, y=340, creation=0, z=0, **styling)

   Rectangle representing a probability sample space, divisible into regions.

   .. py:method:: divide_horizontally(proportion, colors=('#58C4DD', '#FC6255'), labels=None, creation=0, z=0)

      Split the space left/right by *proportion* (0--1).

   .. py:method:: divide_vertically(proportion, colors=('#58C4DD', '#FC6255'), labels=None, creation=0, z=0)

      Split the space top/bottom by *proportion* (0--1).

----

WaterfallChart
--------------

.. py:class:: WaterfallChart(values, labels=None, x=200, y=100, width=800, height=400, bar_width=0.7, pos_color='#83C167', neg_color='#FF6B6B', total_color='#58C4DD', connector_color='#666', font_size=16, show_total=True, creation=0, z=0)

   Waterfall chart showing the cumulative effect of positive and negative values.
   Each bar starts where the previous one ended, with dashed connectors between them.

   :param list values: Incremental values (positive or negative).
   :param list labels: Bar labels.
   :param bool show_total: Append a total bar at the end.

   .. py:classmethod:: from_dict(data, **kwargs)

      Create a ``WaterfallChart`` from a ``{label: value}`` dictionary.

----

GanttChart
----------

.. py:class:: GanttChart(tasks, x=100, y=80, width=1200, bar_height=30, bar_spacing=10, colors=None, font_size=16, creation=0, z=0)

   Gantt chart for project timelines.

   :param list tasks: List of ``(label, start, end)`` or ``(label, start, end, color)`` tuples.
   :param float bar_height: Height of each task bar.

   .. code-block:: python

      gantt = GanttChart([
          ('Design', 0, 3),
          ('Build',  2, 7),
          ('Test',   6, 9),
      ])

----

SankeyDiagram
-------------

.. py:class:: SankeyDiagram(flows, x=100, y=100, width=1200, height=600, node_width=30, node_spacing=20, colors=None, font_size=16, creation=0, z=0)

   Sankey flow diagram showing weighted flows between source and target nodes
   connected by curved bands.

   :param list flows: List of ``(source, target, value)`` tuples.
   :param float node_width: Width of the node rectangles.

----

FunnelChart
-----------

.. py:class:: FunnelChart(stages, x=100, y=100, width=600, height=500, colors=None, font_size=18, gap=4, creation=0, z=0)

   Funnel chart showing progressive narrowing stages.

   :param list stages: List of ``(label, value)`` tuples, from widest to narrowest.
   :param float gap: Vertical gap between trapezoids.

----

TreeMap
-------

.. py:class:: TreeMap(data, x=100, y=100, width=800, height=600, colors=None, font_size=14, padding=2, creation=0, z=0)

   Treemap visualization using a squarified layout.

   :param list data: List of ``(label, value)`` tuples.
   :param float padding: Gap between cells.

----

GaugeChart
----------

.. py:class:: GaugeChart(value, min_val=0, max_val=100, x=960, y=540, radius=200, start_angle=225, end_angle=-45, colors=None, label=None, font_size=36, tick_count=5, creation=0, z=0)

   Speedometer-style gauge chart with a needle, colored arc bands, and
   tick marks.

   :param float value: Current gauge value.
   :param float min_val: Minimum scale value.
   :param float max_val: Maximum scale value.
   :param list colors: Color stops as ``[(hex_color, position), ...]`` where position is 0--1.
   :param str label: Optional label below the value.

----

SparkLine
---------

.. py:class:: SparkLine(data, x=100, y=100, width=120, height=30, stroke='#58C4DD', stroke_width=1.5, show_endpoint=False, creation=0, z=0)

   Bases: :py:class:`VObject`

   Minimal inline sparkline chart rendered as a single SVG path.

   :param list data: Numeric data points.
   :param bool show_endpoint: Draw a dot at the last data point.

----

KPICard
-------

.. py:class:: KPICard(title, value, subtitle=None, trend_data=None, x=100, y=100, width=280, height=160, bg_color='#1a1a2e', title_color='#aaa', value_color='#fff', font_size=48, creation=0, z=0)

   Metric card showing a title, large value, optional subtitle, and an
   embedded trend sparkline.

   :param str title: Card header text.
   :param value: Main displayed value.
   :param str subtitle: Optional secondary text.
   :param list trend_data: Data points for the embedded ``SparkLine``.

   .. code-block:: python

      card = KPICard('Revenue', '$1.2M',
                     subtitle='+12% MoM',
                     trend_data=[10, 12, 11, 14, 13, 16])

----

BulletChart
-----------

.. py:class:: BulletChart(actual, target, ranges=None, label=None, x=100, y=100, width=500, height=40, bar_color='#333', target_color='#fff', font_size=16, max_val=None, creation=0, z=0)

   Bullet chart: qualitative background ranges, an actual-value bar, and a
   target marker line.

   :param float actual: Actual measured value.
   :param float target: Target value (shown as a vertical line).
   :param list ranges: ``[(threshold, color), ...]`` background bands.
   :param str label: Label text to the left.

----

CalendarHeatmap
---------------

.. py:class:: CalendarHeatmap(data, rows=7, cols=52, x=100, y=100, cell_size=14, gap=2, colormap=None, creation=0, z=0)

   Grid heatmap similar to a GitHub contribution graph.

   :param data: A ``dict`` mapping ``(row, col)`` to values, or a flat iterable.
   :param list colormap: List of color strings from low to high.

----

WaffleChart
-----------

.. py:class:: WaffleChart(categories, x=100, y=100, grid_size=10, cell_size=20, gap=3, font_size=14, creation=0, z=0)

   Waffle chart: a grid of colored squares showing category proportions,
   with an auto-generated legend.

   :param list categories: List of ``(label, value, color)`` tuples.
   :param int grid_size: Number of cells per row/column.

----

CircularProgressBar
-------------------

.. py:class:: CircularProgressBar(value, x=960, y=540, radius=80, stroke_width=12, track_color='#2a2a3a', bar_color='#58C4DD', font_size=36, show_text=True, creation=0, z=0)

   Circular (ring) progress indicator with percentage text in the center.

   :param float value: Progress percentage (0--100).
   :param bool show_text: Display the percentage as text.

----

Scoreboard
----------

.. py:class:: Scoreboard(entries, x=100, y=100, col_width=200, row_height=60, bg_color='#1a1a2e', label_color='#aaa', value_color='#fff', font_size=28, cols=None, creation=0, z=0)

   Score/metric display panel arranged in a grid layout.

   :param list entries: List of ``(label, value)`` tuples.
   :param int cols: Number of columns (defaults to ``min(len(entries), 4)``).

----

MatrixHeatmap
-------------

.. py:class:: MatrixHeatmap(data, row_labels=None, col_labels=None, x=100, y=100, cell_size=50, gap=2, colormap=None, font_size=14, show_values=True, creation=0, z=0)

   Labeled matrix heatmap with colored cells.

   :param list data: 2D list of numeric values (list of rows).
   :param list row_labels: Labels for each row.
   :param list col_labels: Labels for each column.
   :param list colormap: Color scale from low to high.
   :param bool show_values: Display cell values as text.

----

BoxPlot
-------

.. py:class:: BoxPlot(data_groups, positions=None, x=100, y=100, plot_width=400, plot_height=300, box_width=30, box_color='#58C4DD', whisker_color='#aaa', median_color='#FF6B6B', font_size=12, creation=0, z=0)

   Box-and-whisker plot for one or more data groups. Computes quartiles,
   median, and whiskers automatically.

   :param list data_groups: List of lists, each containing numeric data for one group.
   :param list positions: X-axis positions for each group (defaults to 1, 2, 3, ...).
