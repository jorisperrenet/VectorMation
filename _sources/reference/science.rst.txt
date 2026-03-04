Science
=======

Scientific visualization classes. Higher-level classes such as
:py:class:`NeuralNetwork`, :py:class:`Pendulum`, and :py:class:`StandingWave`
combine geometry with time-varying animation.

----

UnitInterval
------------

.. py:class:: UnitInterval(x=360, y=540, length=600, tick_step=0.1, show_labels=True, font_size=18, creation=0, z=0, **styling_kwargs)
   :no-index:

   Convenience wrapper that returns a :py:class:`NumberLine` pre-configured
   for the ``[0, 1]`` range -- commonly used for probabilities and
   normalized parameters.

   :param float x: Left edge x-position.
   :param float y: Y-position.
   :param float length: Line length in pixels.
   :param float tick_step: Spacing between ticks (in the 0--1 range).
   :param bool show_labels: Show numeric tick labels.
   :param float font_size: Font size for tick labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Passed through to :py:class:`NumberLine`.

   .. note::

      ``UnitInterval`` uses ``__new__`` and returns a ``NumberLine`` instance
      directly, so ``isinstance(UnitInterval(), NumberLine)`` is ``True``.

   .. admonition:: Example: UnitInterval
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_unit_interval.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_unit_interval.py
         :language: python
         :start-after: parse_args()
         :end-before: v.write_frame

----

Molecule2D
----------

.. py:class:: Molecule2D(atoms, bonds=None, scale=80, cx=960, cy=540, atom_radius=20, font_size=16, creation=0, z=0)
   :no-index:

   Simple 2D molecule visualization built from atom positions and bond
   connectivity. Atoms are drawn as colored circles (element-specific
   palette) with text labels, and bonds are rendered as single, double,
   or triple parallel lines.

   :param list atoms: List of ``(element_symbol, x, y)`` tuples where *x*
      and *y* are in abstract units (scaled by *scale*).
   :param list bonds: List of ``(i, j)`` or ``(i, j, order)`` tuples.
      *i* and *j* are zero-based atom indices; *order* defaults to 1
      (single bond). Use 2 for double bonds and 3 for triple bonds.
   :param float scale: Pixels per abstract unit.
   :param float cx: Center x-position of the molecule on canvas.
   :param float cy: Center y-position of the molecule on canvas.
   :param float atom_radius: Radius of each atom circle.
   :param float font_size: Font size for element labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   Built-in atom color palette:

   ======= ============ ============
   Symbol  Color        Description
   ======= ============ ============
   C       ``#555``     Carbon
   H       ``#fff``     Hydrogen
   O       ``#FF4444``  Oxygen
   N       ``#4444FF``  Nitrogen
   S       ``#FFFF00``  Sulfur
   P       ``#FF8800``  Phosphorus
   F       ``#00FF00``  Fluorine
   Cl      ``#00FF00``  Chlorine
   Br      ``#882200``  Bromine
   I       ``#8800FF``  Iodine
   ======= ============ ============

   .. admonition:: Example: Molecule2D
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_molecule.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_molecule.py
         :language: python
         :start-after: parse_args()
         :end-before: v.write_frame

----

NeuralNetwork
-------------

.. py:class:: NeuralNetwork(layer_sizes, cx=960, cy=540, width=800, height=500, neuron_radius=16, neuron_fill='#58C4DD', edge_color='#888', edge_width=1, creation=0, z=0)
   :no-index:

   Neural network diagram with layers of neurons connected by fully-connected
   edges. Supports labeling input/output layers, activating individual neurons,
   animating forward propagation, and highlighting specific paths.

   :param list[int] layer_sizes: Number of neurons per layer
      (e.g. ``[3, 5, 2]`` for a 3-layer network).
   :param float cx: Center x-position.
   :param float cy: Center y-position.
   :param float width: Total diagram width in pixels.
   :param float height: Total diagram height in pixels.
   :param float neuron_radius: Radius of each neuron circle.
   :param str neuron_fill: Fill color for neurons.
   :param str edge_color: Stroke color for connecting lines.
   :param float edge_width: Stroke width for connecting lines.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: label_input(labels, font_size=20, buff=30, **kwargs) -> NeuralNetwork

      Add text labels to the left of each input-layer neuron.

      :param list labels: List of label strings (one per input neuron).
      :param float font_size: Font size for labels.
      :param float buff: Horizontal buffer between neuron and label.

   .. py:method:: label_output(labels, font_size=20, buff=30, **kwargs) -> NeuralNetwork

      Add text labels to the right of each output-layer neuron.

      :param list labels: List of label strings (one per output neuron).
      :param float font_size: Font size for labels.
      :param float buff: Horizontal buffer between neuron and label.

   .. py:method:: activate(layer_idx, neuron_idx, start=0, end=1, color='#FFFF00') -> NeuralNetwork
      :no-index:

      Flash-animate a single neuron to indicate activation.

      :param int layer_idx: Zero-based layer index.
      :param int neuron_idx: Zero-based neuron index within the layer.
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.

   .. py:method:: propagate(start=0, duration=2, delay=0.3, color='#FFFF00') -> NeuralNetwork

      Animate a forward-propagation signal that flashes each layer in
      sequence from input to output.

      :param float start: Animation start time.
      :param float duration: Total duration of the propagation animation.
      :param float delay: Time offset between successive layers.
      :param str color: Flash color.

   .. py:method:: highlight_path(path, start=0, delay=0.3, color='#FF6B6B', edge_color='#FF6B6B') -> NeuralNetwork

      Highlight a specific path through the network by flashing neurons
      and their connecting edges.

      :param list[int] path: Neuron index per layer (e.g. ``[0, 2, 1]``
         for a 3-layer network). Length must match the number of layers.
      :param float start: Animation start time.
      :param float delay: Time offset between successive layers.
      :param str color: Neuron flash color.
      :param str edge_color: Edge flash color.

   .. admonition:: Example: NeuralNetwork propagation
      :class: example

      .. raw:: html

         <video src="../_static/videos/neuralnet.mp4" controls autoplay loop muted></video>

      Neural network with forward propagation animation.

      .. literalinclude:: ../../../examples/reference/neuralnet.py
         :language: python
         :start-after: parse_args()
         :end-before: v.browser_display

----

Pendulum
--------

.. py:class:: Pendulum(pivot_x=960, pivot_y=200, length=300, angle=30, bob_radius=20, period=2.0, damping=0.0, start=0, end=5, creation=0, z=0)
   :no-index:

   Animated simple pendulum consisting of a pivot point, a rigid rod, and
   a circular bob. The bob oscillates according to ``angle * exp(-damping * t) * cos(2*pi/period * t)``.

   :param float pivot_x: Pivot point x-coordinate.
   :param float pivot_y: Pivot point y-coordinate.
   :param float length: Rod length in pixels.
   :param float angle: Initial angle in **degrees** from vertical.
   :param float bob_radius: Radius of the bob circle.
   :param float period: Oscillation period in seconds.
   :param float damping: Exponential damping factor. ``0`` means no damping
      (perpetual oscillation); larger values cause the amplitude to decay.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:attribute:: pivot
      :type: Dot

      The pivot point dot (small grey circle).

   .. py:attribute:: rod
      :type: Line

      The rigid rod connecting the pivot to the bob.

   .. py:attribute:: bob
      :type: Circle

      The bob circle at the end of the rod.

   .. admonition:: Example: Damped pendulum
      :class: example

      .. code-block:: python

         from vectormation.objects import *

         canvas = VectorMathAnim()
         canvas.set_background()

         p = Pendulum(angle=45, period=1.5, damping=0.1, start=0, end=10)
         canvas.add_objects(p)
         canvas.browser_display()

   .. admonition:: Example: Pendulum with trail
      :class: example

      .. raw:: html

         <video src="../_static/videos/pendulum.mp4" controls autoplay loop muted></video>

      Damped pendulum with traced path.

      .. literalinclude:: ../../../examples/reference/pendulum.py
         :language: python
         :start-after: parse_args()
         :end-before: v.browser_display

----

StandingWave
------------

.. py:class:: StandingWave(x1=300, y1=540, x2=1620, y2=540, amplitude=100, harmonics=3, frequency=1.0, num_points=200, start=0, end=5, creation=0, z=0, **kwargs)
   :no-index:

   Animated standing wave between two fixed endpoints. The wave displacement
   is computed as ``amplitude * sin(k * x) * cos(omega * t)`` where *k*
   depends on the harmonic number.

   :param float x1: Left endpoint x-coordinate.
   :param float y1: Left endpoint y-coordinate.
   :param float x2: Right endpoint x-coordinate.
   :param float y2: Right endpoint y-coordinate.
   :param float amplitude: Maximum displacement in pixels.
   :param int harmonics: Number of half-wavelengths (harmonic number).
      ``1`` gives the fundamental mode, ``2`` the second harmonic, etc.
   :param float frequency: Oscillation frequency in Hz.
   :param int num_points: Number of sample points along the wave path.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param kwargs: Additional SVG styling. Supports ``stroke`` (default
      ``'#58C4DD'``) and ``stroke_width`` (default ``3``).

   .. py:attribute:: dot1
      :type: Dot

      Fixed endpoint dot at ``(x1, y1)``.

   .. py:attribute:: dot2
      :type: Dot

      Fixed endpoint dot at ``(x2, y2)``.

   .. py:attribute:: wave
      :type: Path

      The animated wave path whose ``d`` attribute is recomputed each frame.

   .. admonition:: Example: StandingWave
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_standing_wave.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_standing_wave.py
         :language: python
         :start-after: parse_args()
         :end-before: v.write_frame

----

Lens
----

.. py:class:: Lens(cx=960, cy=540, height=300, focal_length=200, thickness=30, n=1.52, color='#58C4DD', show_focal_points=True, show_axis=True, creation=0, z=0, **styling_kwargs)

   Convex or concave lens for geometric optics diagrams.  Convex lenses
   (positive focal length) are drawn as a biconvex shape; concave lenses
   (negative focal length) are thin at the center and thick at the edges.

   :param float cx: Center x-coordinate.
   :param float cy: Center y-coordinate.
   :param float height: Lens height in pixels.
   :param float focal_length: Positive = convex, negative = concave.
   :param float thickness: Maximum lens thickness in pixels.
   :param float n: Refractive index (used by Ray for Snell's law).
   :param str color: Fill color.
   :param bool show_focal_points: Draw dots at the focal points.
   :param bool show_axis: Draw the principal axis as a dashed line.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: image_point(obj_x, obj_y)

      Compute the image position using the thin-lens equation
      ``1/f = 1/do + 1/di``.  Returns ``(image_x, image_y)`` or ``None``
      if the object is at the focal point (image at infinity).

      :param float obj_x: Object x-coordinate.
      :param float obj_y: Object y-coordinate.
      :returns: ``(image_x, image_y)`` or ``None``.

   .. admonition:: Example: Lens
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_lens.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_lens.py
         :language: python
         :start-after: parse_args()
         :end-before: v.write_frame

----

Ray
---

.. py:class:: Ray(x1=200, y1=540, angle=0, length=1600, lenses=None, color='#FFFF00', stroke_width=2, show_arrow=False, creation=0, z=0, **styling_kwargs)

   A light ray that propagates in a straight line and refracts through
   :py:class:`Lens` objects using Snell's law (thin-lens paraxial
   approximation).

   :param float x1: Starting x-coordinate.
   :param float y1: Starting y-coordinate.
   :param float angle: Initial direction in degrees (0 = rightward).
   :param float length: Ray length in pixels.
   :param list lenses: List of :py:class:`Lens` instances to refract through.
   :param str color: Ray stroke color.
   :param float stroke_width: Ray line width.
   :param bool show_arrow: Draw a small arrowhead at the tip.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. admonition:: Example: Ray refracting through a lens
      :class: example

      .. code-block:: python

         lens = Lens(focal_length=200)
         ray = Ray(x1=200, y1=400, angle=5, lenses=[lens], show_arrow=True)
