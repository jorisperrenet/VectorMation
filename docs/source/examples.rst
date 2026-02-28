Examples
========

All examples are in the ``examples/`` directory. Run any example with:

.. code-block:: bash

   python examples/<example_name>.py

Use ``python examples/<name>.py -v`` for verbose logging or ``--no-display`` to skip the browser viewer.

Manim comparison examples are in ``examples/manim/`` (see :doc:`vs Manim <vs_manim>`).

.. admonition:: Example: AnimationShowcase
   :class: example

   .. raw:: html

      <video src="_static/videos/animation_showcase.mp4" controls autoplay loop muted></video>

   A comprehensive showcase of all animation methods: appearance, drawing, movement, scaling, rotation, effects, and transforms.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/animation_showcase.py
         :language: python
         :start-after: set_background
         :end-before: if args

Animations
----------

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

.. admonition:: Example: EasingPreview
   :class: example

   .. raw:: html

      <img src="_static/videos/easing_preview.svg">

   All 18 easing functions visualised side-by-side. Each dot travels its track using a different easing curve.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/easing_preview.py
         :language: python
         :start-after: set_background
         :end-before: if not

.. admonition:: Example: AnimationsShowcase
   :class: example

   A grid of labelled effects -- shake, swing, wiggle, pulse, jiggle, rubber band, emphasize, and bounce -- each applied to a different shape.

   .. literalinclude:: ../../examples/animations_showcase_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CollectionAnimations
   :class: example

   VCollection animation methods demonstrated on groups of circles, rectangles, and stars: stagger, cascade, wave, and spin.

   .. literalinclude:: ../../examples/collection_animations_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: CombinedAnimations
   :class: example

   Combined animation methods: ``create_then_fadeout``, ``fadein_then_fadeout``, and chained sequences on circles, rectangles, and stars.

   .. literalinclude:: ../../examples/combined_animations_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: CurveEffects
   :class: example

   Curve effects: ``passing_flash`` highlights a stroke segment, ``get_subcurve`` extracts a portion of a polygon, and an animated tangent line tracks a curve.

   .. literalinclude:: ../../examples/curve_effects_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: TransformFromCopy
   :class: example

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

   A Lissajous figure plotted as a parametric curve on axes.

   .. literalinclude:: ../../examples/parametric_curve_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PolarPlot
   :class: example

   A 4-petal rose curve drawn on polar axes with ``plot_polar``.

   .. literalinclude:: ../../examples/polar_plot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HighlightRange
   :class: example

   ``highlight_x_range`` and ``get_line_from_to`` on axes, shading a region of interest and drawing reference lines.

   .. literalinclude:: ../../examples/highlight_range_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SlopeWave
   :class: example

   Slope field for a circular ODE, combined with wave and glitch text effects.

   .. literalinclude:: ../../examples/slope_wave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TraceArea
   :class: example

   ``trace_path`` records a moving circle's orbit, combined with ``get_area_between`` on axes and ``flash_color``.

   .. literalinclude:: ../../examples/trace_area_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TangentAreaLabel
   :class: example

   A moving tangent line tracks a curve while a shaded area grows, with stagger colour animations on a dot collection.

   .. literalinclude:: ../../examples/tangent_arealabel_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SpiralSecant
   :class: example

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

   Visualise an array and animate bubble sort steps: highlight cells, compare, and swap.

   .. literalinclude:: ../../examples/array_viz_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: LinkedList
   :class: example

   A singly linked list with animated node-by-node traversal.

   .. literalinclude:: ../../examples/linked_list_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Stack
   :class: example

   A stack (LIFO) with push and pop animations.

   .. literalinclude:: ../../examples/stack_viz_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: DataStructures
   :class: example

   All four data-structure visualisations -- Array, Stack, Queue, LinkedList -- with highlight, push, pop, enqueue, and traversal animations.

   .. literalinclude:: ../../examples/data_structures_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Animation Effects
-----------------

.. admonition:: Example: FadeInShift
   :class: example

   Objects fade in from different directions using directional shifts.

   .. literalinclude:: ../../examples/fadein_shift_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Bounce
   :class: example

   Bouncing entrance and exit animations using elastic and bounce easings.

   .. literalinclude:: ../../examples/bounce_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Ripple
   :class: example

   Ripple effect expanding outward from shapes.

   .. literalinclude:: ../../examples/ripple_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Orbit
   :class: example

   Objects orbiting around a central point using ``orbit`` animation.

   .. literalinclude:: ../../examples/orbit_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PopAndFloat
   :class: example

   Objects pop in with overshoot and then gently float up and down.

   .. literalinclude:: ../../examples/pop_and_float_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CascadeShake
   :class: example

   Staggered cascade animation with shake effects on a group of objects.

   .. literalinclude:: ../../examples/cascade_shake_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CrossoutPulse
   :class: example

   Cross out and pulse animations for emphasis and attention.

   .. literalinclude:: ../../examples/crossout_pulse_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SlideInOut
   :class: example

   Slide in / slide out entrance and exit animations from different edges.

   .. literalinclude:: ../../examples/slide_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: WipeUnderline
   :class: example

   Wipe transition and animated text underline.

   .. literalinclude:: ../../examples/wipe_underline_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StepSquish
   :class: example

   Step-function plot on axes, ``squish`` animation, and staggered ``fadein`` on a VCollection.

   .. literalinclude:: ../../examples/step_squish_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SpringGrid
   :class: example

   ``spring`` animation on a bouncing ball, axes grid, and ``for_each`` to transform a collection of dots.

   .. literalinclude:: ../../examples/spring_grid_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TraceElastic
   :class: example

   ``trace_path`` on an orbiting dot, ``elastic_in`` / ``elastic_out`` entrance/exit, and ``add_secant_fade`` on axes.

   .. literalinclude:: ../../examples/trace_elastic_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StemGrouped
   :class: example

   Stem plot, grouped bar chart, ``trail`` ghost images, and ``uncreate`` reverse-draw animation.

   .. literalinclude:: ../../examples/stem_grouped_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SplineFollow
   :class: example

   A circle follows a smooth spline through waypoints using ``along_path``.

   .. literalinclude:: ../../examples/spline_follow_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TrailReveal
   :class: example

   ``trail`` stamps ghost copies along a moving ball's arc, ``reveal`` animates letters into view, and ``add_min_max_labels`` marks curve extrema.

   .. literalinclude:: ../../examples/trail_reveal_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Text Animations
---------------

.. admonition:: Example: Typewriter
   :class: example

   Typewriter and count animations: text appears character-by-character with a blinking cursor.

   .. literalinclude:: ../../examples/typewrite_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScrambleText
   :class: example

   Scramble decode: random characters resolve into the final text.

   .. literalinclude:: ../../examples/scramble_text_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TextHighlight
   :class: example

   Highlight spans of text with coloured background boxes.

   .. literalinclude:: ../../examples/text_highlight_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CodeHighlight
   :class: example

   Syntax-highlighted code block with animated line highlighting.

   .. literalinclude:: ../../examples/code_highlight_lines_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AnnotationUntype
   :class: example

   Arrow annotations on axes combined with ``untype`` to erase text character-by-character.

   .. literalinclude:: ../../examples/annotation_untype_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CodeBlock
   :class: example

   Syntax-highlighted ``Code`` block with a Fibonacci function and animated write-in.

   .. literalinclude:: ../../examples/code_highlight.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: DashedTitle
   :class: example

   Dashed guide lines on axes, an axes title, and ``sequential`` staggered animation on a VCollection.

   .. literalinclude:: ../../examples/dashed_title_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Charts & Data
-------------

.. admonition:: Example: BarChartAnimate
   :class: example

   Animated bar chart: bars grow in and transition to new values.

   .. literalinclude:: ../../examples/bar_chart_animate_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: RadarChart
   :class: example

   Radar/spider chart visualisation with multiple data categories.

   .. literalinclude:: ../../examples/radar_chart_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TableHighlight
   :class: example

   Data table with animated cell highlighting and value changes.

   .. literalinclude:: ../../examples/table_highlight_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ChartShowcase
   :class: example

   Five chart types side-by-side: RadarChart, GaugeChart, SparkLine, KPICard, and WaffleChart.

   .. literalinclude:: ../../examples/chart_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: ChartEnhance
   :class: example

   Pie chart with animated slice highlighting and bar chart with ``set_values`` transitions.

   .. literalinclude:: ../../examples/chart_enhance_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: FunnelGauge
   :class: example

   Funnel chart, TreeMap, GaugeChart, and multiple SparkLines showcased together.

   .. literalinclude:: ../../examples/funnel_gauge_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BubbleDonut
   :class: example

   Bubble chart, stacked area, heatmap with colour bar, and donut chart on a single canvas.

   .. literalinclude:: ../../examples/bubble_donut_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CandlestickGantt
   :class: example

   Candlestick chart, dumbbell plot, parametric area fill, and Gantt chart.

   .. literalinclude:: ../../examples/candlestick_gantt_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HeatmapWaterfall
   :class: example

   Heatmap with crosshair, violin plots, and waterfall chart.

   .. literalinclude:: ../../examples/heatmap_waterfall_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SankeyLollipop
   :class: example

   Threshold line with data labels, lollipop chart, and Sankey flow diagram.

   .. literalinclude:: ../../examples/sankey_lollipop_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: KPIBullet
   :class: example

   KPI cards with trend spark lines, bullet charts, filled step plot, and calendar heatmap.

   .. literalinclude:: ../../examples/kpi_bullet_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ProgressScoreboard
   :class: example

   Circular progress bars, population pyramid, data table, and animated scoreboard.

   .. literalinclude:: ../../examples/progress_scoreboard_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ErrorbarHistogramBoxplot
   :class: example

   Error bars on a scatter plot, histogram, colour bar, and box plot.

   .. literalinclude:: ../../examples/errorbar_histogram_boxplot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ContourQuiverBand
   :class: example

   Contour plot, quiver (vector) field, reference band, and colour bar -- all on axes.

   .. literalinclude:: ../../examples/contour_quiver_band_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScatterColorwave
   :class: example

   Scatter/gather animations on dots, ``color_wave`` on a circle, and shaded inequality region.

   .. literalinclude:: ../../examples/scatter_colorwave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BoxplotBand
   :class: example

   Box plots, confidence bands on a curve, and ``shuffle`` animation on a VCollection.

   .. literalinclude:: ../../examples/boxplot_band_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: RibbonSwarmHeatmap
   :class: example

   Ribbon plot, swarm plot, axis break, and matrix heatmap.

   .. literalinclude:: ../../examples/ribbon_swarm_heatmap_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BarHeartbeat
   :class: example

   Bar plot on axes, heartbeat pulsate animation, and ``flip`` transform on a VCollection.

   .. literalinclude:: ../../examples/bar_heartbeat_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: HistogramRotate
   :class: example

   Histogram on axes, ``rotate_children`` on a VCollection, and labelled axes with data annotations.

   .. literalinclude:: ../../examples/histogram_rotate_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ImplicitDotplot
   :class: example

   Implicit curves (circle, ellipse) and dot plot on separate axes panels.

   .. literalinclude:: ../../examples/implicit_dotplot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Graphs & Diagrams
-----------------

.. admonition:: Example: NetworkGraph
   :class: example

   Directed graph with spring layout, animated edge creation.

   .. literalinclude:: ../../examples/network_graph_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: FlowChart
   :class: example

   Flowchart with decision nodes and directional arrows.

   .. literalinclude:: ../../examples/flowchart_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Tree
   :class: example

   Binary search tree with parent-child connections.

   .. literalinclude:: ../../examples/tree_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Automaton
   :class: example

   Deterministic finite automaton (DFA) accepting strings ending in "ab", with state highlighting.

   .. literalinclude:: ../../examples/automaton_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NetworkTree
   :class: example

   NetworkGraph with directed edges and a Tree (org chart) with animated node highlighting.

   .. literalinclude:: ../../examples/network_tree_example.py
      :language: python
      :start-after: parse_args()
      :end-before: if not

.. admonition:: Example: VennOrg
   :class: example

   Moving axis labels, span annotations, Venn diagrams (2-set and 3-set), and an OrgChart.

   .. literalinclude:: ../../examples/venn_org_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: WaffleMindmap
   :class: example

   Density plot with annotation box, WaffleChart, and MindMap with animated node expansion.

   .. literalinclude:: ../../examples/waffle_mindmap_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Math & Science
--------------

.. admonition:: Example: VectorField
   :class: example

   Arrow-based vector field showing a spiral source pattern.

   .. literalinclude:: ../../examples/vector_field_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ComplexPlane
   :class: example

   Complex plane with 5th roots of unity plotted as a pentagon.

   .. literalinclude:: ../../examples/complex_plane_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ImplicitCurve
   :class: example

   Implicit curve plots: circles and lemniscates defined by equations.

   .. literalinclude:: ../../examples/implicit_curve_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TangentLine
   :class: example

   Tangent line tracking along a curve with animated point of tangency.

   .. literalinclude:: ../../examples/tangent_line_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NeuralNetwork
   :class: example

   Feed-forward neural network diagram with forward propagation animation.

   .. literalinclude:: ../../examples/neural_network_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Pendulum
   :class: example

   Damped pendulum with path trace — rod swings from a pivot point.

   .. literalinclude:: ../../examples/pendulum_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StandingWave
   :class: example

   Standing wave harmonics: the first four modes side-by-side.

   .. literalinclude:: ../../examples/standing_wave_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: BohrAtom
   :class: example

   Bohr model of a Carbon atom with orbiting electrons.

   .. literalinclude:: ../../examples/bohr_atom_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NumberPlaneTransform
   :class: example

   NumberPlane grid transformed by a 2x2 matrix with animated basis vectors (i-hat, j-hat) using ``apply_matrix``.

   .. literalinclude:: ../../examples/number_plane_transform_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StreamLines
   :class: example

   Animated stream lines for a dipole-like vector field with source and sink markers.

   .. literalinclude:: ../../examples/stream_lines_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScienceShowcase
   :class: example

   Electronic circuit components (Resistor, Capacitor, Inductor, Diode) and a NeuralNetwork diagram with forward-propagation animation.

   .. literalinclude:: ../../examples/science_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: VectorFieldAxes
   :class: example

   Vector field plotted on axes with ``plot_vector_field``, combined with animated ``set_width`` / ``set_height`` on rectangles.

   .. literalinclude:: ../../examples/vector_field_axes_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: VectorSort
   :class: example

   Vectors and intervals on axes, with ``sort_children`` reordering a VCollection.

   .. literalinclude:: ../../examples/vector_sort_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ScatterArc
   :class: example

   Scatter plot on axes, ``path_arc`` movement along curved paths, and ``align_to`` on a VCollection.

   .. literalinclude:: ../../examples/scatter_arc_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AsymptoteCoords
   :class: example

   Asymptote lines on a rational function, ``coords_label`` displaying coordinate readouts, and ``pulsate`` animation.

   .. literalinclude:: ../../examples/asymptote_coords_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CursorDim
   :class: example

   Animated cursor following a parabola on axes, ``dim`` / ``undim`` to fade rectangles in and out of focus.

   .. literalinclude:: ../../examples/cursor_dim_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ZerolineWarp
   :class: example

   Zero line on axes with negative range, ``add_dot_label`` annotations, and ``warp`` distortion effect.

   .. literalinclude:: ../../examples/zeroline_warp_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ErrorbarsRadial
   :class: example

   Error bars and regression line on scatter data, with radial ``distribute_radial`` layout.

   .. literalinclude:: ../../examples/errorbars_radial_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Styling & Effects
-----------------

.. admonition:: Example: Gradients
   :class: example

   Linear and radial SVG gradients applied to shapes.

   .. literalinclude:: ../../examples/gradient_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Variable
   :class: example

   Live variable display that tracks a changing value over time.

   .. literalinclude:: ../../examples/variable_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: SaveRestore
   :class: example

   Save an object's state (position, colour), modify it, then restore the original state.

   .. literalinclude:: ../../examples/save_restore_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Clone
   :class: example

   Deep-copy objects with independent animations using ``clone``.

   .. literalinclude:: ../../examples/clone_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: GradientStyling
   :class: example

   ``set_color_by_gradient`` on a row of circles, ``set_opacity_by_gradient``, and ``SurroundingRectangle``.

   .. literalinclude:: ../../examples/gradient_styling_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: NumberlinePointer
   :class: example

   NumberLine with an animated pointer and ``color_cycle`` on a circle.

   .. literalinclude:: ../../examples/numberline_pointer_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: LegendFlip
   :class: example

   Legend on axes with multiple curves, ``flip`` animation, and ``wave_anim`` on a VCollection.

   .. literalinclude:: ../../examples/legend_flip_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Camera
------

.. admonition:: Example: FocusCamera
   :class: example

   Camera focus/zoom on individual objects, then reset to full view.

   .. literalinclude:: ../../examples/focus_camera_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Zoom
   :class: example

   Camera zoom and pan to inspect details of a scene.

   .. literalinclude:: ../../examples/zoom_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

Games
-----

.. admonition:: Example: ChessBoard
   :class: example

   Chess board with the starting position and piece movement.

   .. literalinclude:: ../../examples/chess_example.py
      :language: python
      :start-after: set_background
      :end-before: if not
         :end-before: # Export

Physics
-------

.. admonition:: Example: PhysicsBouncingBalls
   :class: example

   Multiple coloured balls bouncing with gravity, walls, and ball-ball collisions using ``PhysicsSpace``.

   .. literalinclude:: ../../examples/physics_bouncing_balls.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsSpring
   :class: example

   A spring pendulum: a bob attached to a fixed anchor oscillates under gravity, leaving a trace path.

   .. literalinclude:: ../../examples/physics_spring.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsCloth
   :class: example

   Cloth simulation with the top row pinned, fluttering under gravity using spring constraints.

   .. literalinclude:: ../../examples/physics_cloth.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PhysicsShowcase
   :class: example

   Physics engine showcase: bouncing balls with walls and a spring-connected anchor-and-weight system.

   .. literalinclude:: ../../examples/physics_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

UI Components
-------------

.. admonition:: Example: UIShowcase
   :class: example

   Badge, TextBox, SpeechBubble, Divider, Checklist, and ProgressBar components.

   .. literalinclude:: ../../examples/ui_showcase_example.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

.. admonition:: Example: SpeechBadgeDivider
   :class: example

   SpeechBubble with different tail directions, Badge variants, NumberedList, and Divider.

   .. literalinclude:: ../../examples/speech_badge_divider_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: Callout
   :class: example

   Callout annotations pointing to shapes, with dimension lines and tooltip-style labels.

   .. literalinclude:: ../../examples/callout_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ChecklistStepperTagCloud
   :class: example

   Checklist with animated check marks, Stepper progress indicators, and a TagCloud.

   .. literalinclude:: ../../examples/checklist_stepper_tagcloud_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: TextBoxBracketIconGrid
   :class: example

   TextBox callouts, animated Bracket annotations, area chart, and an IconGrid layout.

   .. literalinclude:: ../../examples/textbox_bracket_icongrid_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ProgressBar
   :class: example

   Animated ProgressBar filling to target values, combined with marching-ants dash animation on shapes.

   .. literalinclude:: ../../examples/progress_bar_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: StatusMeterBreadcrumb
   :class: example

   StatusIndicator dots, Meter gauges, and Breadcrumb navigation components.

   .. literalinclude:: ../../examples/status_meter_breadcrumb_example.py
      :language: python
      :start-after: set_background
      :end-before: if not
