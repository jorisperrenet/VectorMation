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
         :end-before: # Export
