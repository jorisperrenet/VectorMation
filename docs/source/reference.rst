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
   +-- CurvedArrow              Bezier curve with arrowhead
   +-- Brace                    Curly brace annotation
   +-- Cross                    X mark
   +-- RightAngle               Right angle indicator
   +-- NumberLine               Number line with ticks
   +-- Graph                    Full plot with axes
   |   +-- Axes                 Standalone axes
   +-- PieChart / BarChart      Charts

   SplitTexObject               Multi-line LaTeX container

.. toctree::
   :maxdepth: 2

   reference/canvas
   reference/vobject
   reference/shapes
   reference/text
   reference/collections
   reference/graphing
   reference/attributes
   reference/utilities
