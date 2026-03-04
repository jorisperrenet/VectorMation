Advanced Examples
=================

These are longer, self-contained animations that recreate popular math and science videos (many inspired by 3Blue1Brown). They demonstrate how VectorMation can be used for real-world projects. All scripts are in the ``examples/advanced/`` directory.

.. code-block:: bash

   python examples/advanced/<script_name>.py

Physics & Simulation
--------------------

.. admonition:: Double Pendulum
   :class: example

   .. raw:: html

      <video src="_static/videos/double_pendulum.mp4" controls autoplay loop muted></video>

   Chaotic motion from a simple system. Two connected pendulums produce wildly different trajectories from nearly identical initial conditions, illustrating sensitive dependence. Uses the exact Lagrangian equations of motion.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/double_pendulum.py
         :language: python

.. admonition:: Colliding Blocks
   :class: example

   .. raw:: html

      <video src="_static/videos/colliding_blocks.mp4" controls autoplay loop muted></video>

   Recreation of 3b1b's "Why do colliding blocks compute pi?" A small block slides into a larger block against a wall -- the number of collisions encodes digits of pi when the mass ratio is a power of 100.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/colliding_blocks.py
         :language: python

.. admonition:: Spring-Mass System
   :class: example

   .. raw:: html

      <video src="_static/videos/spring_mass.mp4" controls autoplay loop muted></video>

   Simple harmonic motion with damping. Inspired by 3b1b's Laplace transform series. Shows a mass on a spring oscillating with damping, alongside a phase-space diagram and the governing equation.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/spring_mass.py
         :language: python

.. admonition:: Galton Board
   :class: example

   .. raw:: html

      <video src="_static/videos/galton_board.mp4" controls autoplay loop muted></video>

   Balls bounce through pegs into buckets, forming a binomial/normal distribution. Inspired by 3Blue1Brown's Central Limit Theorem video.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/galton_board.py
         :language: python


Math & Visualization
--------------------

.. admonition:: Fourier Circles
   :class: example

   .. raw:: html

      <video src="_static/videos/fourier_circles.mp4" controls autoplay loop muted></video>

   Epicycles tracing complex shapes. Demonstrates Fourier series approximation using rotating circles. Starts with a single circle and progressively adds harmonics, tracing out a square-wave-like path.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/fourier_circles.py
         :language: python

.. admonition:: Convolutions
   :class: example

   .. raw:: html

      <video src="_static/videos/convolutions.mp4" controls autoplay loop muted></video>

   Convolution of two continuous functions. Inspired by 3Blue1Brown's video on convolutions. A Gaussian kernel slides across a rectangular function, with the overlapping product area building up the convolution result in real time.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/convolutions.py
         :language: python

.. admonition:: Fibonacci Spiral
   :class: example

   .. raw:: html

      <video src="_static/videos/fibonacci_spiral.mp4" controls autoplay loop muted></video>

   Golden ratio visualization. Draws successive Fibonacci squares and the inscribed quarter-circle arcs that form the classic golden spiral.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/fibonacci_spiral.py
         :language: python

.. admonition:: Mandelbrot Zoom
   :class: example

   .. raw:: html

      <video src="_static/videos/mandelbrot_zoom.mp4" controls autoplay loop muted></video>

   Progressive zoom into the Mandelbrot set's seahorse valley. Renders on the GPU (numba CUDA) and displays as an inline PNG image, smoothly zooming near -0.75 + 0.1i.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/mandelbrot_zoom.py
         :language: python

.. admonition:: Maurer Rose
   :class: example

   .. raw:: html

      <video src="_static/videos/maurer_rose.mp4" controls autoplay loop muted></video>

   Beautiful geometric patterns from polar curves. Connects points on a rose curve at evenly-spaced angular steps, creating stunning geometric patterns.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/maurer_rose.py
         :language: python

Graphing & Axes
---------------

.. admonition:: Axes Graphing
   :class: example

   .. raw:: html

      <video src="_static/videos/axes_graphing.mp4" controls autoplay loop muted></video>

   Showcases Axes and graphing features: function plotting, area shading, tangent lines, Riemann rectangles, animated axis ranges, legends, polar curves, and NumberLine with pointer.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/axes_graphing.py
         :language: python

.. admonition:: Easing Showcase
   :class: example

   .. raw:: html

      <video src="_static/videos/easing_showcase.mp4" controls autoplay loop muted></video>

   Visual comparison of all easing families. Each easing function is shown as a small graph with an animated dot tracing the curve.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/easing_showcase.py
         :language: python

3D
--

.. admonition:: Animated 3D Ripple
   :class: example

   .. raw:: html

      <video src="_static/videos/animated_3d_ripple.mp4" controls autoplay loop muted></video>

   Time-varying surface plot. A ripple surface ``z = sin(r - t) * exp(-r^2)`` animates over time, showing the wave propagating outward with ambient camera rotation.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/animated_3d_ripple.py
         :language: python

.. admonition:: 3D Primitives
   :class: example

   .. raw:: html

      <video src="_static/videos/threed_primitives.mp4" controls autoplay loop muted></video>

   Showcases 3D primitive objects (Line3D, Dot3D, Arrow3D, Text3D), solid shapes (Cube, Cylinder3D, Cone3D, Torus3D, Prism3D), and Platonic solids (Tetrahedron, Octahedron, Icosahedron, Dodecahedron).

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/threed_primitives.py
         :language: python

Geometry & Shapes
-----------------

.. admonition:: Geometry Showcase
   :class: example

   .. raw:: html

      <video src="_static/videos/geometry_showcase.mp4" controls autoplay loop muted></video>

   Polygon decomposition, circle constructions, and rectangle operations.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/geometry_showcase.py
         :language: python

.. admonition:: Boolean Ops Demo
   :class: example

   .. raw:: html

      <video src="_static/videos/boolean_ops_demo.mp4" controls autoplay loop muted></video>

   Boolean operations on shapes: Union, Intersection, Difference, and Exclusion.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/boolean_ops_demo.py
         :language: python

.. admonition:: Cutout & ConvexHull
   :class: example

   .. raw:: html

      <video src="_static/videos/cutout_convexhull.mp4" controls autoplay loop muted></video>

   Spotlight cutout overlay and convex hull wrapping of scattered points.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/cutout_convexhull.py
         :language: python

.. admonition:: ZoomedInset
   :class: example

   .. raw:: html

      <video src="_static/videos/zoomed_inset.mp4" controls autoplay loop muted></video>

   Magnify a region of the canvas with a zoomed inset display.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/zoomed_inset.py
         :language: python

Styling & Effects
-----------------

.. admonition:: Color Theory
   :class: example

   .. raw:: html

      <video src="_static/videos/color_theory.mp4" controls autoplay loop muted></video>

   Gradients, color manipulation, and color harmonies.

   .. dropdown:: Show code
      :class-container: sd-shadow-none

      .. literalinclude:: ../../examples/advanced/color_theory.py
         :language: python

