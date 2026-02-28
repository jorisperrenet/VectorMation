Reference Manual
================

Complete API reference for VectorMation, organised by module and class.

.. code-block:: python

   from vectormation.objects import *

----

Class Hierarchy
---------------

::

   VectorMathAnim               Canvas / scene manager
   VObject (ABC)                Base for all visual objects
   +-- Ellipse                  Ellipse shape
   |   +-- Circle               Circle (rx == ry)
   |       +-- Dot              Small dot (r=0.06)
   +-- Rectangle                Rectangle shape
   |   +-- RoundedRectangle     Rectangle with corner radius
   +-- Line                     Two-point line segment
   |   +-- DashedLine           Line with dash pattern
   +-- Polygon                  Closed polygon from vertices
   |   +-- Lines                Open polyline (closed=False)
   |   |   +-- FunctionGraph    Function plot as polyline
   |   +-- RegularPolygon       N-sided regular polygon
   |   |   +-- EquilateralTriangle
   |   +-- Star                 N-pointed star
   +-- Arc                      SVG arc element
   |   +-- Wedge (Sector)       Pie-wedge
   |   +-- Angle                Angle indicator arc
   +-- Annulus                  Ring / donut shape
   +-- Text                     SVG text element
   |   +-- CountAnimation       Animated number counter
   +-- Path                     SVG <path> element
   +-- Image                    SVG <image> element
   +-- Trace                    Traced polyline following a Coor

   VCollection                  Group of VObjects
   +-- MorphObject              Morph between two shapes
   +-- LabeledDot               Dot with text label
   +-- TexObject                LaTeX rendered as SVG paths
   +-- Arrow                    Line with arrowhead
   |   +-- DoubleArrow          Both ends
   |   +-- LabeledArrow         Arrow with text label
   +-- CurvedArrow              Bezier curve with arrowhead
   +-- Brace                    Curly brace annotation
   +-- Cross                    X mark
   +-- Angle                    Angle arc annotation
   +-- RightAngle               Right angle indicator
   +-- NumberLine               Number line with ticks
   +-- Graph                    Full plot with axes
   |   +-- Axes                 Standalone axes
   +-- NumberPlane              Coordinate grid
   +-- ComplexPlane             Complex number plane
   +-- PolarAxes                Polar coordinate axes
   +-- PieChart                 Pie chart
   +-- DonutChart               Donut chart
   +-- BarChart                 Bar chart
   +-- RadarChart               Radar/spider chart
   +-- Table                    Data table
   +-- Matrix                   Matrix display
   +-- NetworkGraph             Network/graph diagram
   +-- FlowChart                Flow chart
   +-- Tree                     Tree diagram
   +-- NeuralNetwork            Neural network diagram
   +-- Pendulum                 Animated pendulum
   +-- StandingWave             Standing wave animation
   +-- ArrayViz                 Array visualisation
   +-- LinkedListViz            Linked list visualisation
   +-- StackViz                 Stack (LIFO) visualisation
   +-- QueueViz                 Queue (FIFO) visualisation
   +-- Automaton                Finite state machine
   +-- BohrAtom                 Bohr atom model
   +-- ChessBoard               Chess board
   +-- PeriodicTable            Periodic table
   +-- ArrowVectorField         Vector field (arrows)
   +-- StreamLines              Stream lines
   +-- Code                     Syntax-highlighted code
   +-- Title                    Styled title bar
   +-- Variable                 Live variable display
   +-- Underline                Text underline
   +-- Label                    Positioned text label
   +-- Callout                  Speech bubble callout
   +-- Tooltip                  Hovering tooltip
   +-- DimensionLine            Measurement annotation
   +-- Stamp                    Repeated copies of a template
   +-- TimelineBar              Timeline with markers
   +-- Legend                   Chart legend
   +-- ProgressBar              Animated progress bar
   +-- WaterfallChart           Waterfall chart
   +-- GanttChart               Gantt timeline chart
   +-- SankeyDiagram            Sankey flow diagram
   +-- FunnelChart              Funnel chart
   +-- TreeMap                  Treemap visualization
   +-- GaugeChart               Speedometer gauge
   +-- BulletChart              Bullet chart
   +-- CalendarHeatmap          Calendar heatmap
   +-- WaffleChart              Waffle chart
   +-- CircularProgressBar      Circular progress indicator
   +-- Scoreboard               Metric display panel
   +-- MatrixHeatmap            Matrix heatmap
   +-- BoxPlot                  Box-and-whisker plot
   +-- SampleSpace              Probability sample space
   +-- KPICard                  KPI metric card
   +-- SparkLine                Inline sparkline
   +-- TextBox                  Text with box background
   +-- SpeechBubble             Speech bubble annotation
   +-- Badge                    Pill-shaped label
   +-- Divider                  Separator line
   +-- Checklist                Checkbox list
   +-- Stepper                  Step indicator
   +-- TagCloud                 Word cloud
   +-- StatusIndicator          Status dot + label
   +-- Meter                    Bar meter
   +-- Breadcrumb               Breadcrumb trail
   +-- Countdown                Animated countdown
   +-- Filmstrip                Storyboard filmstrip
   +-- Bracket                  Bracket decoration
   +-- IconGrid                 Icon grid
   +-- RoundedCornerPolygon     Polygon with rounded corners
   +-- VennDiagram              Venn diagram
   +-- OrgChart                 Organization chart
   +-- MindMap                  Radial mind map
   +-- ZoomedInset              Zoomed inset viewport

   PhysicsSpace                 2D physics simulation
   +-- Body                     Physics body wrapper
   +-- Spring                   Spring constraint
   +-- Cloth                    Cloth simulation

   SplitTexObject               Multi-line LaTeX container
   DynamicObject                Object rebuilt each frame

   ThreeDAxes                   3D coordinate axes
   +-- Surface                  3D surface plot
   +-- Line3D / Arrow3D / Dot3D 3D primitives
   +-- ParametricCurve3D        3D parametric curve
   +-- Text3D                   3D text
   +-- Sphere3D / Cube / Cylinder3D / Cone3D / Torus3D / Prism3D

.. toctree::
   :maxdepth: 2

   reference/canvas
   reference/vobject
   reference/shapes
   reference/text
   reference/collections
   reference/graphing
   reference/charts
   reference/ui
   reference/diagrams
   reference/physics
   reference/science
   reference/threed
   reference/attributes
   reference/utilities
   reference/svg_utils
