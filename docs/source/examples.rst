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

   VCollection animations and methods: ``stagger``, ``stagger_fadein``/``fadeout``, ``wave_anim``/``effect``, ``reveal``, ``rotate_children``, ``spread``, ``align_submobjects``, ``distribute_radial``, ``set_color_by_gradient``, ``clone``, ``filter``, ``sort_children``.

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

   MorphObject: TeX phrase morphing and circle-to-square morph with 360-degree rotation.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/morphing_example.py
         :language: python
         :start-after: set_background
         :end-before: if args


Plotting
--------

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

      <img src="_static/videos/parametric_curve_example.svg" style="width:100%">

   A Lissajous figure plotted as a parametric curve on axes.

   .. literalinclude:: ../../examples/parametric_curve_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: PolarPlot
   :class: example

   .. raw:: html

      <img src="_static/videos/polar_plot_example.svg" style="width:100%">

   A 4-petal rose curve drawn on polar axes with ``plot_polar``.

   .. literalinclude:: ../../examples/polar_plot_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: AxesPlotTypes
   :class: example

   .. raw:: html

      <img src="_static/videos/axes_plot_types.svg" style="width:100%">

   All Axes plot types: ``plot_bar``, ``plot_scatter``, ``plot_histogram``, ``plot_stem``, ``plot_grouped_bar``, ``plot_lollipop``, ``plot_bubble``, ``plot_dot_plot``, ``plot_candlestick``, ``plot_dumbbell``, ``plot_population_pyramid``, ``plot_stacked_area``, ``plot_filled_step``, ``plot_area``, ``plot_density``, ``plot_ribbon``, ``plot_swarm``, ``plot_error_bar``, ``plot_contour``, ``plot_quiver``, ``plot_step``, ``plot_implicit``, ``plot_polar``, ``plot_heatmap``, ``ParametricFunction``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/axes_plot_types.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AxesAnnotations
   :class: example

   .. raw:: html

      <img src="_static/videos/axes_annotations.svg" style="width:100%">

   Axes annotation methods: ``add_legend``, ``add_cursor``, ``add_title``, ``add_color_bar``, ``add_crosshair``, ``add_zero_line``, ``add_dot_label``, ``add_arrow_annotation``, ``add_text_annotation``, ``add_annotation_box``, ``add_area_label``, ``add_data_labels``, ``add_data_table``, ``add_min_max_labels``, ``add_moving_label``, ``add_moving_tangent``, ``add_horizontal_label``, ``add_vertical_label``, ``add_asymptote``, ``coords_label``, ``add_trace``, ``add_secant_fade``, ``add_vector``, ``add_interval``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/axes_annotations.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AxesOverlays
   :class: example

   .. raw:: html

      <img src="_static/videos/axes_overlays.svg" style="width:100%">

   Axes overlay methods: ``add_reference_band``, ``add_confidence_band``, ``add_shaded_inequality``, ``add_vertical_span``, ``add_horizontal_span``, ``add_threshold_line``, ``add_axis_break``, ``add_boxplot``, ``add_violin_plot``, ``add_error_bars``, ``add_regression_line``, ``get_dashed_line``, ``get_area``, ``get_area_between``, ``get_slope_field``, ``highlight_y_range``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/axes_overlays.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: AxesFormatters
   :class: example

   .. raw:: html

      <img src="_static/videos/axes_formatters.svg" style="width:100%">

   Axes tick formatters: ``pi_format``, ``pi_tex_format``, ``log_tex_format``, ``scientific_format``, ``engineering_format``, ``percent_format``, ``degree_format``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/axes_formatters.py
         :language: python
         :start-after: set_background
         :end-before: if args

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

.. admonition:: Example: SectionsAndSpeedControl
   :class: example

   .. raw:: html

      <video src="_static/videos/speed_and_sections.mp4" controls autoplay loop muted></video>

   Shapes appear one at a time, pausing at section breaks. Press Space to advance, +/- to change speed.

   .. literalinclude:: ../../examples/speed_and_sections.py
      :language: python
      :start-after: set_background
      :end-before: if not

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

.. admonition:: Example: DataStructureMethods
   :class: example

   .. raw:: html

      <video src="_static/videos/data_structure_methods.mp4" controls autoplay loop muted></video>

   Data structure methods: ``Stack.push``/``pop``, ``Queue.enqueue``/``dequeue``, ``LinkedList.append_node``/``remove_node``, ``Array.sort``/``reverse``, ``BinaryTree.traverse``, ``DecimalMatrix``/``IntegerMatrix``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/data_structure_methods.py
         :language: python
         :start-after: set_background
         :end-before: if args

Animation Effects
-----------------

.. admonition:: Example: NumberlineFeatures
   :class: example

   .. raw:: html

      <video src="_static/videos/numberline_features.mp4" controls autoplay loop muted></video>

   NumberLine features: ``add_pointer``, ``animate_pointer``, ``point_to_number``, ``snap_to_tick``, ``highlight_range``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/numberline_features.py
         :language: python
         :start-after: set_background
         :end-before: if args

Text & Code
-----------

.. admonition:: Example: CodeHighlight
   :class: example

   .. raw:: html

      <video src="_static/videos/code_highlight.mp4" controls autoplay loop muted></video>

   Syntax-highlighted ``Code`` block with static display and animated ``highlight_lines`` walkthrough.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/code_highlight.py
         :language: python
         :start-after: set_background
         :end-before: if args

Charts & Data
-------------

.. admonition:: Example: TableHighlight
   :class: example

   .. raw:: html

      <video src="_static/videos/table_highlight_example.mp4" controls autoplay loop muted></video>

   Data table with animated cell highlighting and value changes.

   .. literalinclude:: ../../examples/table_highlight_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ChartTypes
   :class: example

   .. raw:: html

      <img src="_static/videos/chart_types.svg" style="width:100%">

   Chart types: ``GaugeChart``, ``SparkLine``, ``DonutChart``, ``FunnelChart``, ``TreeMap``, ``WaffleChart``, ``BulletChart``, ``SankeyDiagram``, ``WaterfallChart``, ``GanttChart``, ``CalendarHeatmap``, ``MatrixHeatmap``, ``Scoreboard``, ``KPICard``, ``SampleSpace``, ``TimelineBar``, ``RadarChart``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/chart_types.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: ChartMethods
   :class: example

   .. raw:: html

      <video src="_static/videos/chart_methods.mp4" controls autoplay loop muted></video>

   Chart animation methods: ``PieChart.sweep_in``, ``PieChart.add_percentage_labels``, ``PieChart.explode``, ``PieChart.highlight_sector``, ``BarChart.grow_from_zero``, ``BarChart.add_bar``/``remove_bar``, ``BarChart.animate_sort``, ``BarChart.add_value_labels``, ``BarChart.set_bar_color``, ``BarChart.animate_values``, ``BarChart.set_bar_colors``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/chart_methods.py
         :language: python
         :start-after: set_background
         :end-before: if args

Graphs & Diagrams
-----------------

.. admonition:: Example: GraphStructures
   :class: example

   .. raw:: html

      <video src="_static/videos/graph_structures.mp4" controls autoplay loop muted></video>

   Graph structures: ``NetworkGraph`` with spring layout, ``FlowChart``, ``Tree`` (BST search), ``NetworkTree`` with ``Legend``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/graph_structures.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: Automaton
   :class: example

   .. raw:: html

      <video src="_static/videos/automaton_example.mp4" controls autoplay loop muted></video>

   Deterministic finite automaton (DFA) accepting strings ending in "ab", with state highlighting.

   .. literalinclude:: ../../examples/automaton_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: DiagramTypes
   :class: example

   .. raw:: html

      <img src="_static/videos/diagram_types.svg" style="width:100%">

   Diagram types: ``VennDiagram``, ``OrgChart``, ``MindMap``, ``BoxPlot``, ``BinaryTree``, ``Stamp``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/diagram_types.py
         :language: python
         :start-after: set_background
         :end-before: if args

Math & Science
--------------

.. admonition:: Example: VectorFields
   :class: example

   .. raw:: html

      <img src="_static/videos/vector_fields.svg" style="width:100%">

   Vector field visualizations: ``ArrowVectorField``, ``Axes.plot_vector_field``, ``StreamLines`` (dipole).

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/vector_fields.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: ComplexPlane
   :class: example

   .. raw:: html

      <img src="_static/videos/complex_plane_example.svg" style="width:100%">

   Complex plane with 5th roots of unity plotted as a pentagon.

   .. literalinclude:: ../../examples/complex_plane_example.py
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

.. admonition:: Example: NumberPlaneTransform
   :class: example

   .. raw:: html

      <video src="_static/videos/number_plane_transform_example.mp4" controls autoplay loop muted></video>

   NumberPlane grid transformed by a 2x2 matrix with animated basis vectors (i-hat, j-hat) using ``apply_matrix``.

   .. literalinclude:: ../../examples/number_plane_transform_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: CircuitComponents
   :class: example

   .. raw:: html

      <img src="_static/videos/circuit_components.svg" style="width:100%">

   Circuit and science components: ``Resistor``, ``Capacitor``, ``Inductor``, ``Diode``, ``LED``, ``Molecule2D``, ``BohrAtom``, ``ElectricField``, ``Charge``, ``StandingWave``, ``Lens``, ``Ray``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/circuit_components.py
         :language: python
         :start-after: set_background
         :end-before: if args

.. admonition:: Example: ThreeDObjects
   :class: example

   .. raw:: html

      <img src="_static/videos/threed.svg" style="width:100%">

   3D objects: ``Surface``, ``Sphere3D``, ``Cube``, ``Cylinder3D``, ``Torus3D``, ``Prism3D``, ``Line3D``, ``Dot3D``, ``Arrow3D``, ``Text3D``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/threed.py
         :language: python
         :start-after: set_background
         :end-before: if args


Styling & Effects
-----------------

.. admonition:: Example: Gradients
   :class: example

   .. raw:: html

      <img src="_static/videos/gradient_example.svg" style="width:100%">

   Linear and radial SVG gradients applied to shapes.

   .. literalinclude:: ../../examples/gradient_example.py
      :language: python
      :start-after: set_background
      :end-before: if not

.. admonition:: Example: ShapeTypes
   :class: example

   .. raw:: html

      <img src="_static/videos/shapes.svg" style="width:100%">

   Shape types: ``AnnotationDot``, ``ArcBetweenPoints``, ``Elbow``, ``AnnularSector``, ``ArcPolygon``, ``CubicBezier``, ``DashedLine``, ``KochSnowflake``, ``SierpinskiTriangle``, ``SurroundingCircle``, ``BackgroundRectangle``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/shapes.py
         :language: python
         :start-after: set_background
         :end-before: if args

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

UI Components
-------------

.. admonition:: Example: UIWidgets
   :class: example

   .. raw:: html

      <img src="_static/videos/ui_widgets.svg" style="width:100%">

   UI widgets: ``Badge``, ``Label``, ``TextBox``, ``SpeechBubble``, ``StatusIndicator``, ``Checklist``, ``Stepper``, ``Breadcrumb``, ``Countdown``, ``CircularProgressBar``, ``Meter``, ``IconGrid``, ``DimensionLine``, ``Bracket``, ``LabeledArrow``, ``LabeledLine``, ``Underline``, ``Filmstrip``, ``Divider``, ``TagCloud``, ``NumberedList``, ``BulletedList``, ``Paragraph``, ``RoundedCornerPolygon``, ``Callout``.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/ui_widgets.py
         :language: python
         :start-after: set_background
         :end-before: if args
