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
