Examples
========

All examples are in the ``examples/`` directory. Run any example with:

.. code-block:: bash

   python examples/<example_name>.py

Use ``python examples/<name>.py -v`` for verbose logging or ``--no-display`` to skip the browser viewer.

Manim comparison examples are in ``examples/manim/`` (see :doc:`vs Manim <vs_manim>`).

Animations
----------

.. admonition:: Example: AnimationsCreation
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_creation.mp4" controls autoplay loop muted></video>

   Creation and destruction animations: ``fadein``, ``fadeout``, ``write``, ``create``, ``draw_along``, ``slide_in``, ``slide_out``, ``zoom_in``, ``zoom_out``, ``rotate_in``, ``pop_in``, ``wipe``, ``elastic_in``, ``elastic_out``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_creation.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsMovement
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_movement.mp4" controls autoplay loop muted></video>

   Movement animations: ``shift``, ``move_to``, ``to_edge``, ``to_corner``, ``along_path``, ``path_arc``, ``orbit``, ``spiral_in``, ``spiral_out``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_movement.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsEffects
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_effects.mp4" controls autoplay loop muted></video>

   Visual effects: ``shake``, ``jiggle``, ``glitch``, ``bounce``, ``wiggle``, ``wave``, ``rubber_band``, ``emphasize``, ``spring``, ``ripple``, ``pulsate``, ``indicate``, ``flash``, ``circumscribe``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_effects.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsColor
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_color.mp4" controls autoplay loop muted></video>

   Color animations: ``set_color``, ``set_fill``, ``set_stroke``, ``color_cycle``, ``flash_color``, ``pulse_color``, ``set_color_by_gradient``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_color.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsText
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_text.mp4" controls autoplay loop muted></video>

   Text-specific animations: ``typewrite``, ``untype``, ``scramble``, ``typing``, ``reveal_by_word``, ``highlight_substring``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_text.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsVCollection
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_vcollection.mp4" controls autoplay loop muted></video>

   VCollection animations: ``stagger``, ``stagger_fadein``, ``stagger_fadeout``, ``wave_anim``, ``wave_effect``, ``reveal``, ``rotate_children``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_vcollection.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AnimationsCounters
   :class: example

   .. raw:: html

      <video src="_static/videos/animations_counters.mp4" controls autoplay loop muted></video>

   Counter animations: ``CountAnimation``, ``DecimalNumber``, ``Integer``, ``ValueTracker``, ``Variable``, with TeX-rendered counterparts using ``TexCountAnimation``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animations_counters.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: Morphing
   :class: example

   .. raw:: html

      <video src="_static/videos/morphing_example.mp4" controls autoplay loop muted></video>

   A LaTeX phrase morphs into another with a colour change.

   .. literalinclude:: ../../examples/morphing_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: RotatingMorph
   :class: example

   .. raw:: html

      <video src="_static/videos/rotating_morph.mp4" controls autoplay loop muted></video>

   A circle morphs into a square while spinning 360 degrees.

   .. literalinclude:: ../../examples/rotating_morph.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CurveEffects
   :class: example

   .. raw:: html

      <video src="_static/videos/curve_effects_example.mp4" controls autoplay loop muted></video>

   Curve effects: ``passing_flash`` highlights a stroke segment, ``get_subcurve`` extracts a portion of a polygon, and an animated tangent line tracks a curve.

   .. literalinclude:: ../../examples/curve_effects_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: TransformFromCopy
   :class: example

   .. raw:: html

      <video src="_static/videos/transform_from_copy_example.mp4" controls autoplay loop muted></video>

   ``transform_from_copy`` morphs a ghost duplicate while the original object stays in place.

   .. literalinclude:: ../../examples/transform_from_copy_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Plotting
--------

.. admonition:: Example: GraphExample
   :class: example

   .. raw:: html

      <img src="_static/videos/graph_example.svg">

   A simple ``sin(x)`` plot on labelled axes -- the minimal plotting example.

   .. literalinclude:: ../../examples/graph_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AnimatedGraph
   :class: example

   .. raw:: html

      <video src="_static/videos/graph_animated.mp4" controls autoplay loop muted></video>

   Sine and cosine curves drawn progressively with ``create`` animations.

   .. literalinclude:: ../../examples/graph_animated.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AxesZoom
   :class: example

   .. raw:: html

      <video src="_static/videos/axes_zoom.mp4" controls autoplay loop muted></video>

   Animated axis ranges: draw a parabola, zoom into a region of interest, pan across the curve, and track a dot — all by animating ``x_min``, ``x_max``, ``y_min``, ``y_max`` as ``Real`` attributes.

   .. literalinclude:: ../../examples/axes_zoom.py
      :language: python
      :start-after: set_background
      :end-before: if args

.. admonition:: Example: ParametricCurve
   :class: example

   .. raw:: html

      <video src="_static/videos/parametric_curve_example.mp4" controls autoplay loop muted></video>

   A Lissajous figure plotted as a parametric curve on axes.

   .. literalinclude:: ../../examples/parametric_curve_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PolarPlot
   :class: example

   .. raw:: html

      <video src="_static/videos/polar_plot_example.mp4" controls autoplay loop muted></video>

   A 4-petal rose curve drawn on polar axes with ``plot_polar``.

   .. literalinclude:: ../../examples/polar_plot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HighlightRange
   :class: example

   .. raw:: html

      <video src="_static/videos/highlight_range_example.mp4" controls autoplay loop muted></video>

   ``highlight_x_range`` and ``get_line_from_to`` on axes, shading a region of interest and drawing reference lines.

   .. literalinclude:: ../../examples/highlight_range_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SlopeWave
   :class: example

   .. raw:: html

      <video src="_static/videos/slope_wave_example.mp4" controls autoplay loop muted></video>

   Slope field for a circular ODE, combined with wave and glitch text effects.

   .. literalinclude:: ../../examples/slope_wave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TraceArea
   :class: example

   .. raw:: html

      <video src="_static/videos/trace_area_example.mp4" controls autoplay loop muted></video>

   ``trace_path`` records a moving circle's orbit, combined with ``get_area_between`` on axes and ``flash_color``.

   .. literalinclude:: ../../examples/trace_area_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TangentAreaLabel
   :class: example

   .. raw:: html

      <video src="_static/videos/tangent_arealabel_example.mp4" controls autoplay loop muted></video>

   A moving tangent line tracks a curve while a shaded area grows, with stagger colour animations on a dot collection.

   .. literalinclude:: ../../examples/tangent_arealabel_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SpiralSecant
   :class: example

   .. raw:: html

      <video src="_static/videos/spiral_secant_example.mp4" controls autoplay loop muted></video>

   ``spiral_in`` / ``spiral_out`` entrance effects and animated secant-line fade on a parabola.

   .. literalinclude:: ../../examples/spiral_secant_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Advanced
--------

.. admonition:: Example: Spiral
   :class: example

   .. raw:: html

      <video src="_static/videos/spiral.mp4" controls autoplay loop muted></video>

   A dot traces a spiral path outward from the centre using parametric motion and rotation.

   .. literalinclude:: ../../examples/spiral.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HeartCurve
   :class: example

   .. raw:: html

      <video src="_static/videos/heart.mp4" controls autoplay loop muted></video>

   A parametric heart curve traced by a moving dot, then filled with red.

   .. literalinclude:: ../../examples/heart.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SierpinskiTriangle
   :class: example

   .. raw:: html

      <img src="_static/videos/sierpinski_triangle.svg">

   A fractal triangle built recursively over 6 levels using ``deepcopy``.

   .. literalinclude:: ../../examples/sierpinski_triangle.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SectionsAndSpeedControl
   :class: example

   .. raw:: html

      <video src="_static/videos/speed_and_sections.mp4" controls autoplay loop muted></video>

   Shapes appear one at a time, pausing at section breaks. Press Space to advance, +/- to change speed.

   .. literalinclude:: ../../examples/speed_and_sections.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: LineArcUtils
   :class: example

   .. raw:: html

      <video src="_static/videos/line_arc_utils_example.mp4" controls autoplay loop muted></video>

   Line and Arc utility methods: ``get_length``, ``get_angle``, ``point_at``, ``perpendicular_at``, and ``add_label``.

   .. literalinclude:: ../../examples/line_arc_utils_example.py
      :language: python
      :start-after: tempfile.mkdtemp()
      :end-before: args = parse_args

Concepts
--------

.. admonition:: Example: CodeExplanation
   :class: example

   .. raw:: html

      <img src="_static/videos/code_explanation.svg">

   An explanatory diagram showing how VectorMation decomposes an animation into frames, objects, and time-varying attributes.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/code_explanation.py
         :language: python
         :start-after: set_background
         :end-before: if not

.. admonition:: Example: Logo
   :class: example

   .. raw:: html

      <img src="_static/logo.svg" width="300">

   The VectorMation crystal V logo, built from triangular polygon facets.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/logo.py
         :language: python
         :start-after: width=1000, height=1000)

Data Structures
---------------

.. admonition:: Example: ArrayViz
   :class: example

   .. raw:: html

      <video src="_static/videos/array_viz_example.mp4" controls autoplay loop muted></video>

   Visualise an array and animate bubble sort steps: highlight cells, compare, and swap.

   .. literalinclude:: ../../examples/array_viz_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: LinkedList
   :class: example

   .. raw:: html

      <video src="_static/videos/linked_list_example.mp4" controls autoplay loop muted></video>

   A singly linked list with animated node-by-node traversal.

   .. literalinclude:: ../../examples/linked_list_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Stack
   :class: example

   .. raw:: html

      <video src="_static/videos/stack_viz_example.mp4" controls autoplay loop muted></video>

   A stack (LIFO) with push and pop animations.

   .. literalinclude:: ../../examples/stack_viz_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: DataStructures
   :class: example

   .. raw:: html

      <video src="_static/videos/data_structures_example.mp4" controls autoplay loop muted></video>

   All four data-structure visualisations -- Array, Stack, Queue, LinkedList -- with highlight, push, pop, enqueue, and traversal animations.

   .. literalinclude:: ../../examples/data_structures_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Animation Effects
-----------------

.. admonition:: Example: Orbit
   :class: example

   .. raw:: html

      <video src="_static/videos/orbit_example.mp4" controls autoplay loop muted></video>

   Objects orbiting around a central point using ``orbit`` animation.

   .. literalinclude:: ../../examples/orbit_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CascadeShake
   :class: example

   .. raw:: html

      <video src="_static/videos/cascade_shake_example.mp4" controls autoplay loop muted></video>

   Staggered cascade animation with shake effects on a group of objects.

   .. literalinclude:: ../../examples/cascade_shake_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StepSquish
   :class: example

   .. raw:: html

      <video src="_static/videos/step_squish_example.mp4" controls autoplay loop muted></video>

   Step-function plot on axes, ``squish`` animation, and staggered ``fadein`` on a VCollection.

   .. literalinclude:: ../../examples/step_squish_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SpringGrid
   :class: example

   .. raw:: html

      <video src="_static/videos/spring_grid_example.mp4" controls autoplay loop muted></video>

   ``spring`` animation on a bouncing ball, axes grid, and ``for_each`` to transform a collection of dots.

   .. literalinclude:: ../../examples/spring_grid_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TraceElastic
   :class: example

   .. raw:: html

      <video src="_static/videos/trace_elastic_example.mp4" controls autoplay loop muted></video>

   ``trace_path`` on an orbiting dot, ``elastic_in`` / ``elastic_out`` entrance/exit, and ``add_secant_fade`` on axes.

   .. literalinclude:: ../../examples/trace_elastic_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StemGrouped
   :class: example

   .. raw:: html

      <video src="_static/videos/stem_grouped_example.mp4" controls autoplay loop muted></video>

   Stem plot, grouped bar chart, ``trail`` ghost images, and ``uncreate`` reverse-draw animation.

   .. literalinclude:: ../../examples/stem_grouped_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TrailReveal
   :class: example

   .. raw:: html

      <video src="_static/videos/trail_reveal_example.mp4" controls autoplay loop muted></video>

   ``trail`` stamps ghost copies along a moving ball's arc, ``reveal`` animates letters into view, and ``add_min_max_labels`` marks curve extrema.

   .. literalinclude:: ../../examples/trail_reveal_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Text Animations
---------------

.. admonition:: Example: Typewriter
   :class: example

   .. raw:: html

      <video src="_static/videos/typewrite_example.mp4" controls autoplay loop muted></video>

   Typewriter and count animations: text appears character-by-character with a blinking cursor.

   .. literalinclude:: ../../examples/typewrite_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScrambleText
   :class: example

   .. raw:: html

      <video src="_static/videos/scramble_text_example.mp4" controls autoplay loop muted></video>

   Scramble decode: random characters resolve into the final text.

   .. literalinclude:: ../../examples/scramble_text_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TextHighlight
   :class: example

   .. raw:: html

      <video src="_static/videos/text_highlight_example.mp4" controls autoplay loop muted></video>

   Highlight spans of text with coloured background boxes.

   .. literalinclude:: ../../examples/text_highlight_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CodeHighlight
   :class: example

   .. raw:: html

      <video src="_static/videos/code_highlight_lines_example.mp4" controls autoplay loop muted></video>

   Syntax-highlighted code block with animated line highlighting.

   .. literalinclude:: ../../examples/code_highlight_lines_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AnnotationUntype
   :class: example

   .. raw:: html

      <video src="_static/videos/annotation_untype_example.mp4" controls autoplay loop muted></video>

   Arrow annotations on axes combined with ``untype`` to erase text character-by-character.

   .. literalinclude:: ../../examples/annotation_untype_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CodeBlock
   :class: example

   .. raw:: html

      <video src="_static/videos/code_highlight.mp4" controls autoplay loop muted></video>

   Syntax-highlighted ``Code`` block with a Fibonacci function and animated write-in.

   .. literalinclude:: ../../examples/code_highlight.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: DashedTitle
   :class: example

   .. raw:: html

      <video src="_static/videos/dashed_title_example.mp4" controls autoplay loop muted></video>

   Dashed guide lines on axes, an axes title, and ``sequential`` staggered animation on a VCollection.

   .. literalinclude:: ../../examples/dashed_title_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Charts & Data
-------------

.. admonition:: Example: BarChartAnimate
   :class: example

   .. raw:: html

      <video src="_static/videos/bar_chart_animate_example.mp4" controls autoplay loop muted></video>

   Animated bar chart: bars grow in and transition to new values.

   .. literalinclude:: ../../examples/bar_chart_animate_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: RadarChart
   :class: example

   .. raw:: html

      <video src="_static/videos/radar_chart_example.mp4" controls autoplay loop muted></video>

   Radar/spider chart visualisation with multiple data categories.

   .. literalinclude:: ../../examples/radar_chart_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TableHighlight
   :class: example

   .. raw:: html

      <video src="_static/videos/table_highlight_example.mp4" controls autoplay loop muted></video>

   Data table with animated cell highlighting and value changes.

   .. literalinclude:: ../../examples/table_highlight_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ChartShowcase
   :class: example

   .. raw:: html

      <video src="_static/videos/chart_showcase_example.mp4" controls autoplay loop muted></video>

   Five chart types side-by-side: RadarChart, GaugeChart, SparkLine, KPICard, and WaffleChart.

   .. literalinclude:: ../../examples/chart_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: ChartEnhance
   :class: example

   .. raw:: html

      <video src="_static/videos/chart_enhance_example.mp4" controls autoplay loop muted></video>

   Pie chart with animated slice highlighting and bar chart with ``set_values`` transitions.

   .. literalinclude:: ../../examples/chart_enhance_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: FunnelGauge
   :class: example

   .. raw:: html

      <video src="_static/videos/funnel_gauge_example.mp4" controls autoplay loop muted></video>

   Funnel chart, TreeMap, GaugeChart, and multiple SparkLines showcased together.

   .. literalinclude:: ../../examples/funnel_gauge_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BubbleDonut
   :class: example

   .. raw:: html

      <video src="_static/videos/bubble_donut_example.mp4" controls autoplay loop muted></video>

   Bubble chart, stacked area, heatmap with colour bar, and donut chart on a single canvas.

   .. literalinclude:: ../../examples/bubble_donut_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CandlestickGantt
   :class: example

   .. raw:: html

      <video src="_static/videos/candlestick_gantt_example.mp4" controls autoplay loop muted></video>

   Candlestick chart, dumbbell plot, parametric area fill, and Gantt chart.

   .. literalinclude:: ../../examples/candlestick_gantt_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HeatmapWaterfall
   :class: example

   .. raw:: html

      <video src="_static/videos/heatmap_waterfall_example.mp4" controls autoplay loop muted></video>

   Heatmap with crosshair, violin plots, and waterfall chart.

   .. literalinclude:: ../../examples/heatmap_waterfall_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SankeyLollipop
   :class: example

   .. raw:: html

      <video src="_static/videos/sankey_lollipop_example.mp4" controls autoplay loop muted></video>

   Threshold line with data labels, lollipop chart, and Sankey flow diagram.

   .. literalinclude:: ../../examples/sankey_lollipop_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: KPIBullet
   :class: example

   .. raw:: html

      <video src="_static/videos/kpi_bullet_example.mp4" controls autoplay loop muted></video>

   KPI cards with trend spark lines, bullet charts, filled step plot, and calendar heatmap.

   .. literalinclude:: ../../examples/kpi_bullet_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ProgressScoreboard
   :class: example

   .. raw:: html

      <video src="_static/videos/progress_scoreboard_example.mp4" controls autoplay loop muted></video>

   Circular progress bars, population pyramid, data table, and animated scoreboard.

   .. literalinclude:: ../../examples/progress_scoreboard_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ErrorbarHistogramBoxplot
   :class: example

   .. raw:: html

      <video src="_static/videos/errorbar_histogram_boxplot_example.mp4" controls autoplay loop muted></video>

   Error bars on a scatter plot, histogram, colour bar, and box plot.

   .. literalinclude:: ../../examples/errorbar_histogram_boxplot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ContourQuiverBand
   :class: example

   .. raw:: html

      <video src="_static/videos/contour_quiver_band_example.mp4" controls autoplay loop muted></video>

   Contour plot, quiver (vector) field, reference band, and colour bar -- all on axes.

   .. literalinclude:: ../../examples/contour_quiver_band_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScatterColorwave
   :class: example

   .. raw:: html

      <video src="_static/videos/scatter_colorwave_example.mp4" controls autoplay loop muted></video>

   Scatter/gather animations on dots, ``color_wave`` on a circle, and shaded inequality region.

   .. literalinclude:: ../../examples/scatter_colorwave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BoxplotBand
   :class: example

   .. raw:: html

      <video src="_static/videos/boxplot_band_example.mp4" controls autoplay loop muted></video>

   Box plots, confidence bands on a curve, and ``shuffle`` animation on a VCollection.

   .. literalinclude:: ../../examples/boxplot_band_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: RibbonSwarmHeatmap
   :class: example

   .. raw:: html

      <video src="_static/videos/ribbon_swarm_heatmap_example.mp4" controls autoplay loop muted></video>

   Ribbon plot, swarm plot, axis break, and matrix heatmap.

   .. literalinclude:: ../../examples/ribbon_swarm_heatmap_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BarHeartbeat
   :class: example

   .. raw:: html

      <video src="_static/videos/bar_heartbeat_example.mp4" controls autoplay loop muted></video>

   Bar plot on axes, heartbeat pulsate animation, and ``flip`` transform on a VCollection.

   .. literalinclude:: ../../examples/bar_heartbeat_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HistogramRotate
   :class: example

   .. raw:: html

      <video src="_static/videos/histogram_rotate_example.mp4" controls autoplay loop muted></video>

   Histogram on axes, ``rotate_children`` on a VCollection, and labelled axes with data annotations.

   .. literalinclude:: ../../examples/histogram_rotate_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ImplicitDotplot
   :class: example

   .. raw:: html

      <video src="_static/videos/implicit_dotplot_example.mp4" controls autoplay loop muted></video>

   Implicit curves (circle, ellipse) and dot plot on separate axes panels.

   .. literalinclude:: ../../examples/implicit_dotplot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Graphs & Diagrams
-----------------

.. admonition:: Example: NetworkGraph
   :class: example

   .. raw:: html

      <video src="_static/videos/network_graph_example.mp4" controls autoplay loop muted></video>

   Directed graph with spring layout, animated edge creation.

   .. literalinclude:: ../../examples/network_graph_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: FlowChart
   :class: example

   .. raw:: html

      <video src="_static/videos/flowchart_example.mp4" controls autoplay loop muted></video>

   Flowchart with decision nodes and directional arrows.

   .. literalinclude:: ../../examples/flowchart_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Tree
   :class: example

   .. raw:: html

      <video src="_static/videos/tree_example.mp4" controls autoplay loop muted></video>

   Binary search tree with parent-child connections.

   .. literalinclude:: ../../examples/tree_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Automaton
   :class: example

   .. raw:: html

      <video src="_static/videos/automaton_example.mp4" controls autoplay loop muted></video>

   Deterministic finite automaton (DFA) accepting strings ending in "ab", with state highlighting.

   .. literalinclude:: ../../examples/automaton_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NetworkTree
   :class: example

   .. raw:: html

      <video src="_static/videos/network_tree_example.mp4" controls autoplay loop muted></video>

   NetworkGraph with directed edges and a Tree (org chart) with animated node highlighting.

   .. literalinclude:: ../../examples/network_tree_example.py
      :language: python
      :start-after: parse_args()
      :end-before: if not

.. admonition:: Example: VennOrg
   :class: example

   .. raw:: html

      <video src="_static/videos/venn_org_example.mp4" controls autoplay loop muted></video>

   Moving axis labels, span annotations, Venn diagrams (2-set and 3-set), and an OrgChart.

   .. literalinclude:: ../../examples/venn_org_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: WaffleMindmap
   :class: example

   .. raw:: html

      <video src="_static/videos/waffle_mindmap_example.mp4" controls autoplay loop muted></video>

   Density plot with annotation box, WaffleChart, and MindMap with animated node expansion.

   .. literalinclude:: ../../examples/waffle_mindmap_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Math & Science
--------------

.. admonition:: Example: VectorField
   :class: example

   .. raw:: html

      <video src="_static/videos/vector_field_example.mp4" controls autoplay loop muted></video>

   Arrow-based vector field showing a spiral source pattern.

   .. literalinclude:: ../../examples/vector_field_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ComplexPlane
   :class: example

   .. raw:: html

      <video src="_static/videos/complex_plane_example.mp4" controls autoplay loop muted></video>

   Complex plane with 5th roots of unity plotted as a pentagon.

   .. literalinclude:: ../../examples/complex_plane_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ImplicitCurve
   :class: example

   .. raw:: html

      <video src="_static/videos/implicit_curve_example.mp4" controls autoplay loop muted></video>

   Implicit curve plots: circles and lemniscates defined by equations.

   .. literalinclude:: ../../examples/implicit_curve_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TangentLine
   :class: example

   .. raw:: html

      <video src="_static/videos/tangent_line_example.mp4" controls autoplay loop muted></video>

   Tangent line tracking along a curve with animated point of tangency.

   .. literalinclude:: ../../examples/tangent_line_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NeuralNetwork
   :class: example

   .. raw:: html

      <video src="_static/videos/neural_network_example.mp4" controls autoplay loop muted></video>

   Feed-forward neural network diagram with forward propagation animation.

   .. literalinclude:: ../../examples/neural_network_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Pendulum
   :class: example

   .. raw:: html

      <video src="_static/videos/pendulum_example.mp4" controls autoplay loop muted></video>

   Damped pendulum with path trace — rod swings from a pivot point.

   .. literalinclude:: ../../examples/pendulum_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StandingWave
   :class: example

   .. raw:: html

      <video src="_static/videos/standing_wave_example.mp4" controls autoplay loop muted></video>

   Standing wave harmonics: the first four modes side-by-side.

   .. literalinclude:: ../../examples/standing_wave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BohrAtom
   :class: example

   .. raw:: html

      <video src="_static/videos/bohr_atom_example.mp4" controls autoplay loop muted></video>

   Bohr model of a Carbon atom with orbiting electrons.

   .. literalinclude:: ../../examples/bohr_atom_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NumberPlaneTransform
   :class: example

   .. raw:: html

      <video src="_static/videos/number_plane_transform_example.mp4" controls autoplay loop muted></video>

   NumberPlane grid transformed by a 2x2 matrix with animated basis vectors (i-hat, j-hat) using ``apply_matrix``.

   .. literalinclude:: ../../examples/number_plane_transform_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StreamLines
   :class: example

   .. raw:: html

      <video src="_static/videos/stream_lines_example.mp4" controls autoplay loop muted></video>

   Animated stream lines for a dipole-like vector field with source and sink markers.

   .. literalinclude:: ../../examples/stream_lines_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScienceShowcase
   :class: example

   .. raw:: html

      <video src="_static/videos/science_showcase_example.mp4" controls autoplay loop muted></video>

   Electronic circuit components (Resistor, Capacitor, Inductor, Diode) and a NeuralNetwork diagram with forward-propagation animation.

   .. literalinclude:: ../../examples/science_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: VectorFieldAxes
   :class: example

   .. raw:: html

      <video src="_static/videos/vector_field_axes_example.mp4" controls autoplay loop muted></video>

   Vector field plotted on axes with ``plot_vector_field``, combined with animated ``set_width`` / ``set_height`` on rectangles.

   .. literalinclude:: ../../examples/vector_field_axes_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: VectorSort
   :class: example

   .. raw:: html

      <video src="_static/videos/vector_sort_example.mp4" controls autoplay loop muted></video>

   Vectors and intervals on axes, with ``sort_children`` reordering a VCollection.

   .. literalinclude:: ../../examples/vector_sort_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScatterArc
   :class: example

   .. raw:: html

      <video src="_static/videos/scatter_arc_example.mp4" controls autoplay loop muted></video>

   Scatter plot on axes, ``path_arc`` movement along curved paths, and ``align_to`` on a VCollection.

   .. literalinclude:: ../../examples/scatter_arc_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AsymptoteCoords
   :class: example

   .. raw:: html

      <video src="_static/videos/asymptote_coords_example.mp4" controls autoplay loop muted></video>

   Asymptote lines on a rational function, ``coords_label`` displaying coordinate readouts, and ``pulsate`` animation.

   .. literalinclude:: ../../examples/asymptote_coords_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CursorDim
   :class: example

   .. raw:: html

      <video src="_static/videos/cursor_dim_example.mp4" controls autoplay loop muted></video>

   Animated cursor following a parabola on axes, ``dim`` / ``undim`` to fade rectangles in and out of focus.

   .. literalinclude:: ../../examples/cursor_dim_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ZerolineWarp
   :class: example

   .. raw:: html

      <video src="_static/videos/zeroline_warp_example.mp4" controls autoplay loop muted></video>

   Zero line on axes with negative range, ``add_dot_label`` annotations, and ``warp`` distortion effect.

   .. literalinclude:: ../../examples/zeroline_warp_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ErrorbarsRadial
   :class: example

   .. raw:: html

      <video src="_static/videos/errorbars_radial_example.mp4" controls autoplay loop muted></video>

   Error bars and regression line on scatter data, with radial ``distribute_radial`` layout.

   .. literalinclude:: ../../examples/errorbars_radial_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Styling & Effects
-----------------

.. admonition:: Example: Gradients
   :class: example

   .. raw:: html

      <video src="_static/videos/gradient_example.mp4" controls autoplay loop muted></video>

   Linear and radial SVG gradients applied to shapes.

   .. literalinclude:: ../../examples/gradient_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Variable
   :class: example

   .. raw:: html

      <video src="_static/videos/variable_example.mp4" controls autoplay loop muted></video>

   Live variable display that tracks a changing value over time.

   .. literalinclude:: ../../examples/variable_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Clone
   :class: example

   .. raw:: html

      <video src="_static/videos/clone_example.mp4" controls autoplay loop muted></video>

   Deep-copy objects with independent animations using ``clone``.

   .. literalinclude:: ../../examples/clone_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: GradientStyling
   :class: example

   .. raw:: html

      <video src="_static/videos/gradient_styling_example.mp4" controls autoplay loop muted></video>

   ``set_color_by_gradient`` on a row of circles, ``set_opacity_by_gradient``, and ``SurroundingRectangle``.

   .. literalinclude:: ../../examples/gradient_styling_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NumberlinePointer
   :class: example

   .. raw:: html

      <video src="_static/videos/numberline_pointer_example.mp4" controls autoplay loop muted></video>

   NumberLine with an animated pointer and ``color_cycle`` on a circle.

   .. literalinclude:: ../../examples/numberline_pointer_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: LegendFlip
   :class: example

   .. raw:: html

      <video src="_static/videos/legend_flip_example.mp4" controls autoplay loop muted></video>

   Legend on axes with multiple curves, ``flip`` animation, and ``wave_anim`` on a VCollection.

   .. literalinclude:: ../../examples/legend_flip_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Camera
------

.. admonition:: Example: FocusCamera
   :class: example

   .. raw:: html

      <video src="_static/videos/focus_camera_example.mp4" controls autoplay loop muted></video>

   Camera focus/zoom on individual objects, then reset to full view.

   .. literalinclude:: ../../examples/focus_camera_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Games
-----

.. admonition:: Example: ChessBoard
   :class: example

   .. raw:: html

      <video src="_static/videos/chess_example.mp4" controls autoplay loop muted></video>

   Chess board with the starting position and piece movement.

   .. literalinclude:: ../../examples/chess_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Physics
-------

.. admonition:: Example: PhysicsBouncingBalls
   :class: example

   .. raw:: html

      <video src="_static/videos/physics_bouncing_balls.mp4" controls autoplay loop muted></video>

   Multiple coloured balls bouncing with gravity, walls, and ball-ball collisions using ``PhysicsSpace``.

   .. literalinclude:: ../../examples/physics_bouncing_balls.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsSpring
   :class: example

   .. raw:: html

      <video src="_static/videos/physics_spring.mp4" controls autoplay loop muted></video>

   A spring pendulum: a bob attached to a fixed anchor oscillates under gravity, leaving a trace path.

   .. literalinclude:: ../../examples/physics_spring.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsCloth
   :class: example

   .. raw:: html

      <video src="_static/videos/physics_cloth.mp4" controls autoplay loop muted></video>

   Cloth simulation with the top row pinned, fluttering under gravity using spring constraints.

   .. literalinclude:: ../../examples/physics_cloth.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsShowcase
   :class: example

   .. raw:: html

      <video src="_static/videos/physics_showcase_example.mp4" controls autoplay loop muted></video>

   Physics engine showcase: bouncing balls with walls and a spring-connected anchor-and-weight system.

   .. literalinclude:: ../../examples/physics_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

UI Components
-------------

.. admonition:: Example: UIShowcase
   :class: example

   .. raw:: html

      <video src="_static/videos/ui_showcase_example.mp4" controls autoplay loop muted></video>

   Badge, TextBox, SpeechBubble, Divider, Checklist, and ProgressBar components.

   .. literalinclude:: ../../examples/ui_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: SpeechBadgeDivider
   :class: example

   .. raw:: html

      <video src="_static/videos/speech_badge_divider_example.mp4" controls autoplay loop muted></video>

   SpeechBubble with different tail directions, Badge variants, NumberedList, and Divider.

   .. literalinclude:: ../../examples/speech_badge_divider_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Callout
   :class: example

   .. raw:: html

      <video src="_static/videos/callout_example.mp4" controls autoplay loop muted></video>

   Callout annotations pointing to shapes, with dimension lines and tooltip-style labels.

   .. literalinclude:: ../../examples/callout_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ChecklistStepperTagCloud
   :class: example

   .. raw:: html

      <video src="_static/videos/checklist_stepper_tagcloud_example.mp4" controls autoplay loop muted></video>

   Checklist with animated check marks, Stepper progress indicators, and a TagCloud.

   .. literalinclude:: ../../examples/checklist_stepper_tagcloud_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TextBoxBracketIconGrid
   :class: example

   .. raw:: html

      <video src="_static/videos/textbox_bracket_icongrid_example.mp4" controls autoplay loop muted></video>

   TextBox callouts, animated Bracket annotations, area chart, and an IconGrid layout.

   .. literalinclude:: ../../examples/textbox_bracket_icongrid_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ProgressBar
   :class: example

   .. raw:: html

      <video src="_static/videos/progress_bar_example.mp4" controls autoplay loop muted></video>

   Animated ProgressBar filling to target values, combined with marching-ants dash animation on shapes.

   .. literalinclude:: ../../examples/progress_bar_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StatusMeterBreadcrumb
   :class: example

   .. raw:: html

      <video src="_static/videos/status_meter_breadcrumb_example.mp4" controls autoplay loop muted></video>

   StatusIndicator dots, Meter gauges, and Breadcrumb navigation components.

   .. literalinclude:: ../../examples/status_meter_breadcrumb_example.py
      :language: python
      :start-after: set_background
      :end-before: if not
