"""VectorMation -- vector-based math animation engine."""
from vectormation.objects import (
    VectorMathAnim, VObject, VCollection, MorphObject,
    Polygon, Circle, Ellipse, Dot, LabeledDot, Rectangle, RoundedRectangle, EquilateralTriangle,
    Line, Lines, DashedLine, Text, Image, Path, Trace, TexObject, SplitTexObject,
    Graph, FunctionGraph, Axes, NumberPlane, from_svg, from_svg_file, parse_args, CountAnimation,
    RegularPolygon, Star, Arrow, DoubleArrow, CurvedArrow, Brace, Arc, Wedge, Sector,
    ClipPath, NumberLine, Annulus, Cross, BarChart, PieChart, Table, Matrix, DynamicObject,
    BlurFilter, DropShadowFilter, Angle, RightAngle,
    ValueTracker, DecimalNumber, Integer, always_redraw, Square,
    UNIT, SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF, LARGE_BUFF,
    DEFAULT_STROKE_WIDTH, DEFAULT_FONT_SIZE, DEFAULT_DOT_RADIUS, DEFAULT_SMALL_DOT_RADIUS,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_OBJECT_TO_OBJECT_BUFF,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR, ORIGIN,
    SurroundingRectangle, BackgroundRectangle, VGroup,
    ZoomedInset, Intersection, Difference, Union, Exclusion,
    ThreeDAxes, Title, ScreenRectangle,
)
from vectormation.colors import (
    LinearGradient, RadialGradient, color_gradient, interpolate_color,
    lighten, darken,
    PALETTE_BLUE, PALETTE_GREEN, PALETTE_RED, PALETTE_WARM, PALETTE_COOL, PALETTE_RAINBOW,
)

# Export color constants (WHITE, RED, BLUE, etc.) as module-level names
import vectormation.colors as _colors_module
globals().update(_colors_module.colors)
