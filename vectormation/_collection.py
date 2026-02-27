"""VCollection — container for multiple VObjects with collective operations."""
import math
import random
from copy import deepcopy

import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation._constants import ORIGIN, SMALL_BUFF, UP, DOWN, RIGHT, DR
from vectormation._base import (
    VObject, _norm_dir, _norm_edge, _ramp, _lerp_point,
    _DIR_NAMES, _EDGE_NAMES,
    _make_brect, _set_attr, _parse_path,
    _BBoxMethodsMixin,
)
class VCollection(_BBoxMethodsMixin):
    """Container for a group of VObjects, delegating operations to children."""

    def __init__(self, *objects, creation: float = 0, z: float = 0):
        self.objects = list(objects)
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)
        self._scale_x = attributes.Real(creation, 1)
        self._scale_y = attributes.Real(creation, 1)
        self._scale_origin: tuple[float, float] | None = None

    def add(self, *objs):
        """Add one or more objects to this collection."""
        self.objects.extend(objs)
        return self

    def remove(self, obj):
        """Remove an object from this collection."""
        self.objects.remove(obj)
        return self

    def remove_at(self, index):
        """Remove and return the child at the given index."""
        return self.objects.pop(index)

    def clear(self):
        """Remove all children."""
        self.objects.clear()
        return self

    def insert_at(self, index, *objs):
        """Insert one or more objects at *index*.

        Negative indices are supported (same semantics as ``list.insert``).
        Objects are inserted in order so that ``objs[0]`` ends up at *index*.

        Returns self.
        """
        # Resolve negative indices once so that subsequent inserts stay correct
        # as the list grows.
        if index < 0:
            index = max(len(self.objects) + index, 0)
        for i, obj in enumerate(objs):
            self.objects.insert(index + i, obj)
        return self

    def send_to_back(self, child):
        """Move a child to the back (rendered first, behind others)."""
        if isinstance(child, int):
            child = self.objects[child]
        if child in self.objects:
            self.objects.remove(child)
            self.objects.insert(0, child)
        return self

    def bring_to_front(self, child):
        """Move a child to the front (rendered last, on top).

        Parameters
        ----------
        child:
            Either the child object itself or its integer index in
            ``self.objects``.
        """
        if isinstance(child, int):
            child = self.objects[child]
        if child in self.objects:
            self.objects.remove(child)
            self.objects.append(child)
        return self

    def get_child(self, index):
        """Return the child at *index* (supports negative indices)."""
        n = len(self.objects)
        if index < -n or index >= n:
            raise IndexError(
                f"child index {index} out of range for collection with {n} object(s)"
            )
        return self.objects[index]

    def nth(self, n):
        """Alias for :meth:`get_child`."""
        return self.get_child(n)

    def first(self):
        """Return the first child object."""
        return self.get_child(0)

    def last(self):
        """Return the last child object."""
        return self.get_child(-1)

    def _delegate(self, method, *args, **kwargs):
        """Call method on each child object, return self."""
        for obj in self.objects:
            getattr(obj, method)(*args, **kwargs)
        return self

    @property
    def last_change(self):
        candidates = [obj.last_change for obj in self.objects]
        candidates.append(self.z.last_change)
        candidates.append(self.show.last_change)
        return max(candidates)

    def __repr__(self):
        return f'{self.__class__.__name__}({len(self.objects)} objects)'

    def __iter__(self):
        return iter(self.objects)

    def __getitem__(self, idx):
        return self.objects[idx]

    def __len__(self):
        return len(self.objects)

    def count(self):
        """Return the number of child objects in this collection."""
        return len(self.objects)

    def __contains__(self, obj):
        return obj in self.objects

    def copy(self):
        return deepcopy(self)

    def to_svg(self, time):
        visible = [(getattr(o, 'z', attributes.Real(0, 0)).at_time(time), o)
                    for o in self.objects if o.show.at_time(time)]
        inner = '\n'.join(o.to_svg(time) for _, o in sorted(visible, key=lambda x: x[0]))
        sx, sy = self._scale_x.at_time(time), self._scale_y.at_time(time)
        transform = ''
        if sx != 1 or sy != 1:
            if self._scale_origin:
                cx, cy = self._scale_origin
                transform = f' transform="translate({cx},{cy}) scale({sx},{sy}) translate({-cx},{-cy})"'
            else:
                transform = f' transform="scale({sx},{sy})"'
        return f'<g{transform}>\n{inner}\n</g>'

    def bbox(self, time, start_idx=0, end_idx=None):
        objs = self.objects[start_idx:end_idx]
        if not objs:
            return (0, 0, 0, 0)
        boxes = [o.bbox(time) for o in objs]
        xmin = min(b[0] for b in boxes)
        ymin = min(b[1] for b in boxes)
        xmax = max(b[0] + b[2] for b in boxes)
        ymax = max(b[1] + b[3] for b in boxes)
        return (xmin, ymin, xmax - xmin, ymax - ymin)

    def brect(self, time, start_idx=0, end_idx=None, rx=0, ry=0, buff=SMALL_BUFF, follow=True):
        """Bounding rectangle with buff outward padding."""
        return _make_brect(self.bbox, time, rx, ry, buff, follow,
                           start_idx=start_idx, end_idx=end_idx)

    def move_to(self, x, y, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Move the collection's center to (x, y)."""
        xmin, ymin, w, h = self.bbox(start)
        self.shift(dx=x-(xmin+w/2), dy=y-(ymin+h/2),
                   start=start, end=end, easing=easing)
        return self

    def center_to_pos(self, posx: float = 960, posy: float = 540, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Move the collection's center to (posx, posy)."""
        return self.move_to(posx, posy, start, end, easing)

    def _scale_to_dim(self, cur, target, start, end, easing):
        """Scale to match a target dimension (width or height)."""
        if cur == 0:
            return self
        factor = target / cur
        self.scale(factor, start=start, end=end, easing=easing or easings.smooth)
        return self

    def set_width(self, width, start: float = 0, end: float | None = None, easing=None):
        """Scale the entire group so its bounding box has the given *width*."""
        return self._scale_to_dim(self.get_width(start), width, start, end, easing)

    def set_height(self, height, start: float = 0, end: float | None = None, easing=None):
        """Scale the entire group so its bounding box has the given *height*."""
        return self._scale_to_dim(self.get_height(start), height, start, end, easing)

    def total_width(self, time=0):
        """Return sum of children's widths (not overall bbox width)."""
        return sum(obj.bbox(time)[2] for obj in self.objects)

    def total_height(self, time=0):
        """Return sum of children's heights (not overall bbox height)."""
        return sum(obj.bbox(time)[3] for obj in self.objects)

    def filter(self, predicate):
        """Return a new VCollection with only children matching predicate(obj) -> bool."""
        return VCollection(*(obj for obj in self.objects if predicate(obj)))

    def filter_by_type(self, cls):
        """Return a new VCollection with only children of the given type."""
        return self.filter(lambda obj: isinstance(obj, cls))

    def find(self, predicate, time=0):
        """Return the first child satisfying predicate(obj, time), or None."""
        for obj in self.objects:
            if predicate(obj, time):
                return obj
        return None

    def find_by_type(self, cls):
        """Return a list of all children that are instances of cls."""
        return [obj for obj in self.objects if isinstance(obj, cls)]

    def find_index(self, predicate, time=0):
        """Return the index of the first child satisfying predicate, or -1."""
        for i, obj in enumerate(self.objects):
            if predicate(obj, time):
                return i
        return -1

    def group_by(self, key_func):
        """Return a dict mapping *key_func(child)* to VCollections of matching children."""
        groups: dict = {}
        for obj in self.objects:
            k = key_func(obj)
            groups.setdefault(k, []).append(obj)
        return {k: VCollection(*objs) for k, objs in groups.items()}

    def partition(self, predicate):
        """Split into two VCollections: (matching, non_matching)."""
        yes, no = [], []
        for obj in self.objects:
            (yes if predicate(obj) else no).append(obj)
        return VCollection(*yes), VCollection(*no)

    def chunk(self, size: int):
        """Split children into sub-collections of at most *size* each."""
        if size < 1:
            raise ValueError(f"chunk size must be >= 1, got {size!r}")
        objs = self.objects
        return [VCollection(*objs[i:i + size]) for i in range(0, len(objs), size)]

    def sort_by_position(self, axis='x', reverse=False):
        """Sort children in-place by their x or y centre coordinate."""
        if axis == 'x':
            self.objects.sort(key=lambda obj: obj.center(0)[0], reverse=reverse)
        elif axis == 'y':
            self.objects.sort(key=lambda obj: obj.center(0)[1], reverse=reverse)
        return self

    def group_into(self, n):
        """Split into *n* roughly equal sub-collections. Returns a VCollection of VCollections."""
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n!r}")
        objs = self.objects
        total = len(objs)
        groups = []
        base, remainder = divmod(total, n)
        idx = 0
        for i in range(n):
            size = base + (1 if i < remainder else 0)
            groups.append(VCollection(*objs[idx:idx + size]))
            idx += size
        return VCollection(*groups)

    def enumerate_children(self):
        """Return a list of ``(index, child)`` tuples."""
        return list(enumerate(self.objects))

    def select(self, start=0, end=None):
        """Return a new VCollection with children at indices [start:end]."""
        return VCollection(*self.objects[start:end])

    def take(self, n):
        """Return a new VCollection with the first *n* children."""
        return VCollection(*self.objects[:n])

    def skip(self, n):
        """Return a new VCollection skipping the first *n* children."""
        return VCollection(*self.objects[n:])

    def interleave(self, other):
        """Return a new VCollection with children alternated: [a1, b1, a2, b2, ...]."""
        from itertools import zip_longest
        sentinel = object()
        result = [x for pair in zip_longest(self.objects, other.objects, fillvalue=sentinel)
                  for x in pair if x is not sentinel]
        return VCollection(*result)

    def flatten(self):
        """Flatten nested VCollections into a single-level collection in-place."""
        changed = True
        while changed:
            changed = False
            new_objects = []
            for obj in self.objects:
                if isinstance(obj, VCollection):
                    new_objects.extend(obj.objects)
                    changed = True
                else:
                    new_objects.append(obj)
            self.objects = new_objects
        return self

    def sort_objects(self, key=None, reverse=False, time=0):
        """Sort children in-place. Default key: x position at given time."""
        if key is None:
            key = lambda obj: obj.bbox(time)[0]
        self.objects.sort(key=key, reverse=reverse)
        return self

    def sort_by_y(self, reverse=False, time=0):
        """Sort children by y position (top to bottom by default)."""
        return self.sort_objects(key=lambda obj: obj.bbox(time)[1], reverse=reverse, time=time)

    def sort_by_z(self, reverse=False, time=0):
        """Sort children by z-depth."""
        return self.sort_objects(key=lambda obj: obj.z.at_time(time), reverse=reverse, time=time)

    def sort_by(self, key_func, reverse=False):
        """Sort children by key_func(child). Does not animate — instant reorder."""
        self.objects.sort(key=key_func, reverse=reverse)
        return self

    def max_by(self, key):
        """Return the child with the maximum key value."""
        if not self.objects:
            return None
        return max(self.objects, key=key)

    def min_by(self, key):
        """Return the child with the minimum key value."""
        if not self.objects:
            return None
        return min(self.objects, key=key)

    def sum_by(self, key):
        """Sum the result of key(child) across all children."""
        return sum(key(obj) for obj in self.objects)

    def shuffle(self):
        """Randomly shuffle the order of children in-place."""
        import random
        random.shuffle(self.objects)
        return self

    def shuffle_animate(self, start=0, end=1, easing=None):
        """Animated random shuffle — all children smoothly slide to randomly reassigned positions.

        Records each child's current center, generates a random permutation,
        then animates each child to its new position.

        Parameters
        ----------
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function (default: None = smooth).
        """
        import random
        n = len(self.objects)
        if n < 2:
            return self
        centers = [obj.center(start) for obj in self.objects]
        perm = random.sample(range(n), n)
        for i, obj in enumerate(self.objects):
            tx, ty = centers[perm[i]]
            obj.center_to_pos(tx, ty, start=start, end=end, easing=easing)
        return self

    def reverse_children(self):
        """Reverse the order of children in-place."""
        self.objects.reverse()
        return self

    reverse = reverse_children
    reverse_order = reverse_children

    def rotate_order(self, n=1):
        """Rotate children order by *n* positions.

        Positive *n* moves the first *n* children to the end (like
        ``collections.deque.rotate(-n)``).  Returns *self*.
        """
        if not self.objects:
            return self
        n = n % len(self.objects)
        self.objects = self.objects[n:] + self.objects[:n]
        return self

    def set_z_order(self, order):
        """Reorder children by index list (a permutation of ``range(len(self))``)."""
        self.objects = [self.objects[i] for i in order]
        return self

    def index_of(self, obj):
        """Find object index by identity. Returns -1 if not found."""
        try:
            return self.objects.index(obj)
        except ValueError:
            return -1

    def replace(self, old, new):
        """In-place swap: replace *old* child with *new*."""
        idx = self.index_of(old)
        if idx >= 0:
            self.objects[idx] = new
        return self

    def map_objects(self, func):
        """Apply *func* to each child and return a new VCollection."""
        return VCollection(*(func(obj) for obj in self.objects))

    def set_z_values(self, start=0):
        """Assign ascending z-order values starting from *start*."""
        for i, obj in enumerate(self.objects):
            obj.z.set_onward(start, i)
        return self

    def set_color_by_gradient(self, *colors, attr='fill', start=0):
        """Assign interpolated colors across children.
        colors: two or more hex color strings to interpolate between."""
        setter = 'set_fill' if attr == 'fill' else 'set_stroke'
        n = len(self.objects)
        if n < 2 or len(colors) < 2:
            if colors and n:
                for obj in self.objects:
                    getattr(obj, setter)(colors[0], start=start)
            return self
        from vectormation.colors import interpolate_color
        for i, obj in enumerate(self.objects):
            t = i / (n - 1)
            seg = t * (len(colors) - 1)
            idx = min(int(seg), len(colors) - 2)
            local_t = seg - idx
            color = interpolate_color(colors[idx], colors[idx + 1], local_t)
            getattr(obj, setter)(color, start=start)
        return self

    def set_opacity_by_gradient(self, start_opacity, end_opacity, attr='fill', start=0):
        """Set linearly interpolated opacity across children."""
        n = len(self.objects)
        if n < 2:
            if n:
                self.objects[0].set_opacity(start_opacity, start)
            return self
        for i, obj in enumerate(self.objects):
            t = i / (n - 1)
            opacity = start_opacity + (end_opacity - start_opacity) * t
            if attr == 'fill':
                obj.styling.fill_opacity.set_onward(start, opacity)
            else:
                obj.styling.stroke_opacity.set_onward(start, opacity)
        return self

    def __getattr__(self, name):
        """Delegate unknown methods to children if all children support them."""
        if name.startswith('_'):
            raise AttributeError(name)
        if all(hasattr(obj, name) for obj in self.objects):
            def delegated(*args, **kwargs):
                return self._delegate(name, *args, **kwargs)
            return delegated
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _resolve_center(self, start, cx=None, cy=None):
        if cx is None or cy is None:
            _cx, _cy = self.center(start)
            return (_cx if cx is None else cx, _cy if cy is None else cy)
        return cx, cy

    def scale(self, factor, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale all children around the group center."""
        return self.stretch(factor, factor, start, end, easing)

    def scale_about_point(self, factor, px, py, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale all children about the pivot point (*px*, *py*).

        Sets the group's scale origin to the pivot and applies the
        scale factor, so the pivot stays fixed while children move.
        """
        self._scale_origin = (px, py)
        return self.stretch(factor, factor, start, end, easing)

    def stretch(self, x_factor: float = 1, y_factor: float = 1, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Non-uniform scale of all children around the group center."""
        if self._scale_origin is None:
            self._scale_origin = self._resolve_center(start, None, None)
        for attr, factor in [(self._scale_x, x_factor), (self._scale_y, y_factor)]:
            _set_attr(attr, start, end, attr.at_time(start) * factor, easing)
        return self

    def rotate_to(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy)
        return self._delegate('rotate_to', start, end, degrees, cx=cx, cy=cy, easing=easing)

    def rotate_by(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy)
        return self._delegate('rotate_by', start, end, degrees, cx=cx, cy=cy, easing=easing)

    def arrange(self, direction: str | tuple = 'right', buff=SMALL_BUFF, start: float = 0):
        """Lay out children in a row or column with spacing.
        direction: 'right', 'left', 'down', 'up' or a direction constant."""
        direction = _norm_dir(direction)
        if not self.objects:
            return self
        horizontal = direction in ('right', 'left')
        sign = 1 if direction in ('right', 'down') else -1
        cursor = 0
        for obj in self.objects:
            x, y, w, h = obj.bbox(start)
            size = w if horizontal else h
            offset = cursor - (x if horizontal else y)
            if horizontal:
                obj.shift(dx=sign * offset, start=start)
            else:
                obj.shift(dy=sign * offset, start=start)
            cursor += size + buff
        return self

    def animated_arrange(self, direction=RIGHT, buff=SMALL_BUFF, start=0, end=1, easing=None):
        """Animated version of :meth:`arrange`.

        Computes the target positions that ``arrange`` would produce,
        then animates each child to its target via :meth:`center_to_pos`.

        Parameters
        ----------
        direction:
            Direction constant (e.g. ``RIGHT``, ``DOWN``) or string.
        buff:
            Pixel spacing between children.
        start:
            Start time for the animation.
        end:
            End time for the animation.
        easing:
            Easing function (defaults to ``easings.smooth``).

        Returns self.
        """
        dir_name = _norm_dir(direction)
        if not self.objects:
            return self
        horizontal = dir_name in ('right', 'left')
        sign = 1 if dir_name in ('right', 'down') else -1
        # Compute target centers for each child
        cursor = 0
        targets = []
        for obj in self.objects:
            x, y, w, h = obj.bbox(start)
            cx, cy = obj.center(start)
            size = w if horizontal else h
            offset = cursor - (x if horizontal else y)
            if horizontal:
                targets.append((cx + sign * offset, cy))
            else:
                targets.append((cx, cy + sign * offset))
            cursor += size + buff
        # Animate each child to its target
        _easing = easing or easings.smooth
        for obj, (tx, ty) in zip(self.objects, targets):
            obj.center_to_pos(posx=tx, posy=ty, start=start,
                              end=end, easing=_easing)
        return self

    def distribute(self, direction: str | tuple = 'right', buff=0, start: float = 0):
        """Distribute children evenly within the group's bounding box.
        Unlike arrange(), this spaces children evenly to fill the available space.
        direction: 'right', 'left', 'down', 'up' or a direction constant."""
        direction = _norm_dir(direction)
        if len(self.objects) < 2:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start) for obj in self.objects]
        total_size = sum(b[2] if horizontal else b[3] for b in boxes)
        group_box = self.bbox(start)
        available = (group_box[2] if horizontal else group_box[3]) - total_size
        spacing = available / (len(self.objects) - 1) if len(self.objects) > 1 else 0
        spacing = max(spacing, buff)
        cursor = 0
        for obj, box in zip(self.objects, boxes):
            x, y, w, h = box
            size = w if horizontal else h
            offset = cursor - (x if horizontal else y)
            if horizontal:
                obj.shift(dx=offset, start=start)
            else:
                obj.shift(dy=offset, start=start)
            cursor += size + spacing
        return self

    def space_evenly(self, direction: str | tuple = 'right', total_span=None,
                     start_pos=None, start: float = 0):
        """Distribute children so they fill exactly *total_span* pixels.

        Unlike :meth:`arrange` (fixed gap between children) and :meth:`distribute`
        (uses existing group bbox), ``space_evenly`` lets you specify an explicit
        span and optional start position, then positions children so their combined
        widths (or heights) plus equal gaps exactly fill that span.

        Parameters
        ----------
        direction:
            ``'right'`` / ``'left'`` (horizontal) or ``'down'`` / ``'up'``
            (vertical).
        total_span:
            Total pixel width (horizontal) or height (vertical) to fill.
            Defaults to the group's current bounding-box dimension.
        start_pos:
            Left edge (horizontal) or top edge (vertical) of the first child.
            Defaults to the current leftmost / topmost edge of the group.
        start:
            Time at which to read current positions.

        Returns
        -------
        self
        """
        direction = _norm_dir(direction)
        if len(self.objects) == 0:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start) for obj in self.objects]
        sizes = [b[2] if horizontal else b[3] for b in boxes]
        total_child_size = sum(sizes)
        group_box = self.bbox(start)
        if total_span is None:
            total_span = group_box[2] if horizontal else group_box[3]
        if start_pos is None:
            start_pos = group_box[0] if horizontal else group_box[1]
        n = len(self.objects)
        gap = (total_span - total_child_size) / (n - 1) if n > 1 else 0
        cursor = start_pos
        for obj, box, size in zip(self.objects, boxes, sizes):
            edge = box[0] if horizontal else box[1]
            offset = cursor - edge
            if horizontal:
                obj.shift(dx=offset, start=start)
            else:
                obj.shift(dy=offset, start=start)
            cursor += size + gap
        return self

    def arrange_in_circle(self, radius=150, center=None, start_angle=0,
                          start=0, end=None, easing=None):
        """Arrange children in a circle.

        If *center* is ``None``, the canvas center ``(960, 540)`` is used.
        Each child is placed at angle ``start_angle + i * 2*pi/n``.

        Delegates to :meth:`distribute_radial`.

        Parameters
        ----------
        radius:
            Distance from center to each child's center.
        center:
            ``(cx, cy)`` tuple, or ``None`` for canvas center.
        start_angle:
            Angle in radians for the first child (0 = right).
        start:
            Animation start time.
        end:
            Animation end time.  ``None`` = instant placement.
        easing:
            Easing function for animated mode.
        """
        if center is None:
            center = ORIGIN
        cx, cy = center
        return self.distribute_radial(cx=cx, cy=cy, radius=radius,
                                      start_angle=start_angle,
                                      start=start, end=end,
                                      easing=easing or easings.smooth)

    def distribute_radial(self, cx=960, cy=540, radius=200, start_angle=0,
                           start: float = 0, end: float | None = None,
                           easing=easings.smooth):
        """Arrange children in a circle around (cx, cy).
        With end=None, positions instantly. With end, animates."""
        n = len(self.objects)
        if n == 0:
            return self
        for i, obj in enumerate(self.objects):
            angle = start_angle + math.tau * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            obj_cx, obj_cy = obj.center(start)
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def radial_arrange(self, radius=200, start_angle=0, center=None,
                       start: float = 0):
        """Arrange children in a circle with given radius and starting angle.

        Unlike :meth:`distribute_radial` which accepts animated end,
        this is a simple instant layout method.  center defaults to the
        collection's bounding-box center.

        Parameters
        ----------
        radius: distance from center to each child's center.
        start_angle: angle in radians for the first child (0 = right).
        center: (cx, cy) tuple, or None to use the collection center.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if center is None:
            center = self.center(start)
        cx, cy = center
        for i, obj in enumerate(self.objects):
            angle = start_angle + math.tau * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            obj_cx, obj_cy = obj.center(start)
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start=start)
        return self

    def arrange_in_grid(self, rows=None, cols=None, buff=SMALL_BUFF, start: float = 0):
        """Lay out children in a grid. If rows/cols omitted, picks a square-ish grid."""
        n = len(self.objects)
        if not n:
            return self
        if rows is None and cols is None:
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
        elif rows is None:
            rows = math.ceil(n / cols)
        elif cols is None:
            cols = math.ceil(n / rows)
        # Measure max cell size
        boxes = [obj.bbox(start) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        # Position each object centered in its cell
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            target_cx = c * cell_w + max_w / 2
            target_cy = r * cell_h + max_h / 2
            cur_cx = box[0] + box[2] / 2
            cur_cy = box[1] + box[3] / 2
            obj.shift(dx=target_cx - cur_cx, dy=target_cy - cur_cy, start=start)
        return self

    def animated_arrange_in_grid(self, rows=None, cols=None, buff=SMALL_BUFF, start: float = 0, end: float = 1, easing=None):
        """Animated version of :meth:`arrange_in_grid`.

        Computes the same grid layout as *arrange_in_grid* but animates each
        child to its target position over [start, end] using *center_to_pos*.
        """
        n = len(self.objects)
        if not n:
            return self
        if rows is None and cols is None:
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
        elif rows is None:
            rows = math.ceil(n / cols)
        elif cols is None:
            cols = math.ceil(n / rows)
        # Measure max cell size
        boxes = [obj.bbox(start) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        # Animate each object to its cell center
        for idx, (obj, _box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            target_cx = c * cell_w + max_w / 2
            target_cy = r * cell_h + max_h / 2
            kw = {'start': start, 'end': end}
            if easing is not None:
                kw['easing'] = easing
            obj.center_to_pos(target_cx, target_cy, **kw)
        return self

    def stagger(self, method_name, delay, **kwargs):
        """Call method on each child with staggered timing offsets."""
        for i, obj in enumerate(self.objects):
            kw = dict(kwargs)
            for key in ('start', 'end'):
                if key in kw:
                    kw[key] = kw[key] + i * delay
            getattr(obj, method_name)(**kw)
        return self

    def stagger_along_path(self, method_name, path_d, start=0, end=1,
                           delay=0.1, **kwargs):
        """Position children along an SVG path, then call *method_name* with stagger.

        Each child is moved to an evenly-spaced point on the path described
        by the SVG path string *path_d*, then the named animation method is
        invoked with timing staggered by *delay*.

        Parameters
        ----------
        method_name:
            Name of the method to call on each child.
        path_d:
            SVG path data string (e.g. ``'M0,0 L500,500'``).
        start:
            Base start time for the first child's method call.
        end:
            Base end time for the first child's method call.
        delay:
            Timing offset between successive children.
        **kwargs:
            Extra keyword arguments forwarded to the method.
        """
        from svgpathtools import parse_path
        n = len(self.objects)
        if n == 0:
            return self
        parsed = parse_path(path_d)
        for i, obj in enumerate(self.objects):
            # Sample evenly along the path
            frac = i / max(n - 1, 1)
            pt = parsed.point(frac)
            px, py = pt.real, pt.imag
            obj.center_to_pos(posx=px, posy=py, start=start)
            # Call the method with staggered timing
            kw = dict(kwargs)
            kw['start'] = start + i * delay
            kw['end'] = end + i * delay
            getattr(obj, method_name)(**kw)
        return self

    def stagger_random(self, method_name, start=0, end=1, seed=None, **kwargs):
        """Call method_name on each child in random order with equal stagger delay."""
        import random
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        delay = dur / n
        shuffled = random.Random(seed).sample(self.objects, n)
        for i, obj in enumerate(shuffled):
            obj_start = start + i * delay
            obj_end = obj_start + delay
            kw = dict(kwargs, start=obj_start, end=obj_end)
            getattr(obj, method_name)(**kw)
        return self

    def wave_anim(self, start: float = 0, end: float = 1, amplitude=20, waves=1):
        """Staggered wave animation: children bob up and down with phase offsets."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        for i, obj in enumerate(self.objects):
            phase = math.tau * i / max(n, 1)
            s, d, a, p = start, dur, amplitude, phase
            w = waves
            def _dy(t, _s=s, _d=d, _a=a, _p=p, _w=w):
                progress = (t - _s) / _d
                return -_a * math.sin(math.tau * _w * progress + _p) * (1 - progress)
            for _, ya in obj._shift_reals():
                ya.add(start, end, _dy)
            for c in obj._shift_coors():
                c.add(start, end, lambda t, _f=_dy: (0, _f(t)))
        return self

    def sequential(self, method_name, start: float = 0, end: float = 1, **kwargs):
        """Run an animation method on children one after another with no overlap.
        Equivalent to cascade with overlap=0."""
        return self.cascade(method_name, start=start, end=end, overlap=0, **kwargs)

    def apply_sequentially(self, method_name, start=0, end=1, **kwargs):
        """Apply method to each child in sequence, dividing [start, end] equally.

        Unlike :meth:`sequential` / :meth:`cascade`, this directly computes
        equal-duration time slices without any overlap logic, making it a
        simpler and more predictable alternative.

        Parameters
        ----------
        method_name:
            Name of the animation method to call on each child (e.g. ``'fadein'``).
        start, end:
            Overall time range to divide among the children.
        **kwargs:
            Additional keyword arguments forwarded to each child method call.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dt = (end - start) / n
        for i, obj in enumerate(self.objects):
            getattr(obj, method_name)(start=start + i * dt, end=start + (i + 1) * dt, **kwargs)
        return self

    def apply_sequential(self, method_name, start=0, end=1, **kwargs):
        """Alias for :meth:`apply_sequentially`."""
        return self.apply_sequentially(method_name, start=start, end=end, **kwargs)

    def spread(self, x1, y1, x2, y2, start: float = 0):
        """Distribute children evenly along a line from (x1, y1) to (x2, y2)."""
        n = len(self.objects)
        if n == 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            tx = x1 + (x2 - x1) * t
            ty = y1 + (y2 - y1) * t
            cx, cy = obj.center(start)
            obj.shift(dx=tx - cx, dy=ty - cy, start=start)
        return self

    def align_submobjects(self, edge='left', start: float = 0):
        """Align all children to a common edge: 'left', 'right', 'top', 'bottom', 'center_x', 'center_y'.
        Shifts each child so their specified edge aligns with the collection's edge."""
        n = len(self.objects)
        if n == 0:
            return self
        edge = _norm_edge(edge, 'left')
        # Find the target value from the collection's bbox
        gx, gy, gw, gh = self.bbox(start)
        targets = {
            'left': lambda bx, by, bw, bh: (gx - bx, 0),
            'right': lambda bx, by, bw, bh: ((gx + gw) - (bx + bw), 0),
            'top': lambda bx, by, bw, bh: (0, gy - by),
            'bottom': lambda bx, by, bw, bh: (0, (gy + gh) - (by + bh)),
            'center_x': lambda bx, by, bw, bh: (gx + gw / 2 - (bx + bw / 2), 0),
            'center_y': lambda bx, by, bw, bh: (0, gy + gh / 2 - (by + bh / 2)),
        }
        func = targets.get(edge)
        if func is None:
            return self
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            dx, dy = func(bx, by, bw, bh)
            if dx != 0 or dy != 0:
                obj.shift(dx=dx, dy=dy, start=start)
        return self

    def cascade(self, method_name, start: float = 0, end: float = 1, overlap=0.5, **kwargs):
        """Call an animation method on children with overlapping timing.
        overlap: 0 = sequential, 1 = all simultaneous. 0.5 = half overlap."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        overlap = max(0.0, min(1.0, overlap))
        if n == 1:
            child_dur = dur
            step = 0
        else:
            child_dur = dur / (1 + (1 - overlap) * (n - 1))
            step = child_dur * (1 - overlap)
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = s + child_dur
            getattr(obj, method_name)(start=s, end=e, **kwargs)
        return self

    def stagger_fadein(self, start: float = 0, end: float = 1,
                        shift_dir=None, shift_amount=50, overlap=0.5,
                        easing=easings.smooth):
        """Fade in children with staggered timing and optional shift direction.
        Convenience wrapper around cascade + fadein."""
        kwargs = {'shift_dir': shift_dir, 'shift_amount': shift_amount, 'easing': easing}
        return self.cascade('fadein', start=start, end=end, overlap=overlap, **kwargs)

    def stagger_fadeout(self, start: float = 0, end: float = 1,
                         shift_dir=None, shift_amount=50, overlap=0.5,
                         easing=easings.smooth):
        """Fade out children with staggered timing and optional shift direction.
        Convenience wrapper around cascade + fadeout."""
        kwargs = {'shift_dir': shift_dir, 'shift_amount': shift_amount, 'easing': easing}
        return self.cascade('fadeout', start=start, end=end, overlap=overlap, **kwargs)

    def fade_in_one_by_one(self, start: float = 0, end: float = 1,
                            overlap=0.0, easing=easings.smooth):
        """Fade in each child sequentially with optional overlap.

        Each child gets an equal-duration window in which it fades in.
        When *overlap* is 0 the windows are strictly sequential (no two
        children animate at the same time).  Positive overlap values let
        consecutive windows overlap so the next child starts fading in
        before the previous one finishes.

        Parameters
        ----------
        start, end:
            Overall time interval.
        overlap:
            Fraction of each child's window that overlaps with the next
            (0 = sequential, positive = overlapping).
        easing:
            Easing function for each child's fade.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if n == 1:
            slot = dur
        else:
            slot = (dur + overlap * (n - 1)) / n
        for i, obj in enumerate(self.objects):
            obj_start = start + i * (slot - overlap)
            obj_end = obj_start + slot
            obj.fadein(start=obj_start, end=min(obj_end, end), easing=easing)
        return self

    def reveal(self, start: float = 0, end: float = 1, direction='left',
                easing=easings.smooth, shift_amount=30):
        """Reveal children one by one from a direction (curtain effect).
        direction: 'left' (left-to-right), 'right', 'top', 'bottom'.
        Each child fades in with a small shift from the given direction."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        per_child = dur / n
        shift_map = {'left': (-shift_amount, 0), 'right': (shift_amount, 0),
                     'top': (0, -shift_amount), 'bottom': (0, shift_amount)}
        sdx, sdy = shift_map.get(direction, (-shift_amount, 0))
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            t1 = min(t0 + per_child * 1.5, end)  # slight overlap
            obj.fadein(t0, t1, shift_dir=None)
            # Temporary shift: offset→0 via .add() (additive, non-persistent)
            _dur = max(t1 - t0, 1e-9)
            if sdx != 0:
                _sdx, _t0, _d = sdx, t0, _dur
                def _dx(t, _sdx=_sdx, _t0=_t0, _d=_d, _easing=easing):
                    return _sdx * (1 - _easing((t - _t0) / _d))
                for xa, ya in obj._shift_reals():
                    xa.add(t0, t1, _dx)
                for c in obj._shift_coors():
                    c.add(t0, t1, lambda t, _f=_dx: (_f(t), 0))
            if sdy != 0:
                _sdy, _t0, _d = sdy, t0, _dur
                def _dy(t, _sdy=_sdy, _t0=_t0, _d=_d, _easing=easing):
                    return _sdy * (1 - _easing((t - _t0) / _d))
                for xa, ya in obj._shift_reals():
                    ya.add(t0, t1, _dy)
                for c in obj._shift_coors():
                    c.add(t0, t1, lambda t, _f=_dy: (0, _f(t)))
        return self

    def highlight_child(self, index, start: float = 0, end: float = 1,
                         dim_opacity=0.2, easing=easings.smooth):
        """Emphasize child at `index` by dimming all others.
        At `end`, all opacities are restored."""
        for i, obj in enumerate(self.objects):
            if i != index:
                obj.dim(start=start, end=start + (end - start) * 0.3,
                        opacity=dim_opacity, easing=easing)
                obj.undim(start=start + (end - start) * 0.7, end=end, easing=easing)
        return self

    def swap_children(self, i, j, start: float = 0, end: float = 1,
                       easing=easings.smooth):
        """Animate swapping the positions of children at indices i and j.
        Each child moves along an arc to the other's position, using
        opposite arc directions to avoid overlapping.  Returns self."""
        n = len(self.objects)
        if i < 0 or j < 0 or i >= n or j >= n or i == j:
            return self
        a, b = self.objects[i], self.objects[j]
        acx, acy = a.center(start)
        bcx, bcy = b.center(start)
        a.path_arc(bcx, bcy, start=start, end=end, angle=math.pi / 3, easing=easing)
        b.path_arc(acx, acy, start=start, end=end, angle=-math.pi / 3, easing=easing)
        return self

    swap_animated = swap_children  # backward compat alias

    def highlight_nth(self, n, start=0, end=1, color='#FFFF00', easing=easings.smooth):
        """Highlight the nth child by temporarily changing its fill color while
        dimming others.  At end, restore all original colors.  Returns self."""
        if n < 0 or n >= len(self.objects):
            return self
        mid = start + (end - start) * 0.5
        # Dim non-target children
        for i, obj in enumerate(self.objects):
            if i != n:
                obj.dim(start=start, end=start + (end - start) * 0.3,
                        opacity=0.3, easing=easing)
                obj.undim(start=start + (end - start) * 0.7, end=end, easing=easing)
        # Change nth child fill to highlight color, then restore
        target = self.objects[n]
        # Save original fill as raw tuple for reliable round-tripping
        orig_fill_raw = target.styling.fill.time_func(start)
        target.set_fill(color=color, start=start, end=mid, easing=easing)
        target.set_fill(color=orig_fill_raw, start=mid, end=end, easing=easing)
        return self

    def shuffle_positions(self, start: float = 0, end: float = 1,
                           easing=easings.smooth, seed=None):
        """Randomly rearrange children positions with animation (visual shuffle).
        Unlike shuffle() which reorders the list, this animates children to each
        other's positions. seed: optional random seed for reproducibility."""
        import random
        n = len(self.objects)
        if n <= 1:
            return self
        rng = random.Random(seed)
        centers = [obj.center(start) for obj in self.objects]
        indices = list(range(n))
        rng.shuffle(indices)
        for i, obj in enumerate(self.objects):
            target = centers[indices[i]]
            obj.move_to(target[0], target[1], start=start, end=end, easing=easing)
        return self

    def for_each(self, method_name, **kwargs):
        """Call a method with the same arguments on all children simultaneously.
        Example: group.for_each('set_color', color='red', start=1)"""
        for obj in self.objects:
            getattr(obj, method_name)(**kwargs)
        return self

    def each(self, func):
        """Call ``func(child)`` for every child and return self.

        Unlike :meth:`for_each` (named method) and :meth:`apply` (passes
        ``(child, index)``), this accepts a plain callable.
        """
        for obj in self.objects:
            func(obj)
        return self

    def flip_all(self, start: float = 0, end: float | None = None, axis='x',
                  easing=easings.smooth):
        """Flip (mirror) all children along an axis through the group's center.
        axis: 'x' (horizontal flip, reflect about vertical center line)
              'y' (vertical flip, reflect about horizontal center line)."""
        n = len(self.objects)
        if n == 0:
            return self
        gcx, gcy = self.center(start)
        for obj in self.objects:
            cx, cy = obj.center(start)
            if axis == 'x':
                new_cx = 2 * gcx - cx
                obj.move_to(new_cx, cy, start=start, end=end, easing=easing)
            else:
                new_cy = 2 * gcy - cy
                obj.move_to(cx, new_cy, start=start, end=end, easing=easing)
        return self

    def stagger_color(self, start: float = 0, end: float = 1, colors=('#FF6B6B', '#58C4DD'),
                       attr='fill'):
        """Propagate a color wave through children — each child transitions
        through the color sequence with a delay."""
        n = len(self.objects)
        if n == 0 or len(colors) < 2:
            return self
        dur = end - start
        if dur <= 0:
            return self
        per_child = dur / n
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            t1 = min(t0 + per_child * 2, end)
            obj.color_gradient_anim(colors=colors, start=t0, end=t1, attr=attr)
        return self

    def stagger_scale(self, start: float = 0, end: float = 1,
                       scale_factor=1.5, delay=0.2, easing=easings.smooth,
                       target_scale=None):
        """Scale each child up then back down with a stagger delay between children.

        Creates a "popping" wave effect where each child grows to *scale_factor*
        and shrinks back to its original size, with *delay* seconds between
        successive children starting their animation.

        scale_factor: peak scale factor for each child's pop.
        delay: time offset between successive children starting.
        target_scale: deprecated alias for scale_factor (backward compatibility).
        """
        if target_scale is not None:
            scale_factor = target_scale
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        # Each child gets a pop duration: total time minus all delays, but
        # at least enough for one cycle
        pop_dur = max(dur - (n - 1) * delay, dur / n) if n > 1 else dur
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + pop_dur, end)
            if e <= s:
                continue
            obj._ensure_scale_origin(s)
            _sx0 = obj.styling.scale_x.at_time(s)
            _sy0 = obj.styling.scale_y.at_time(s)
            _d = max(e - s, 1e-9)
            def _make_pop(base, _s=s, _d=_d, _sf=scale_factor, _easing=easing):
                return lambda t, _b=base: \
                    _b * (1 + (_sf - 1) * math.sin(math.pi * _easing((t - _s) / _d)))
            obj.styling.scale_x.set(s, e, _make_pop(_sx0))
            obj.styling.scale_y.set(s, e, _make_pop(_sy0))
        return self

    def stagger_rotate(self, start: float = 0, end: float = 1, degrees=360, easing=easings.smooth):
        """Sequentially rotate each child."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        child_dur = dur / n * 1.5
        step = dur / n
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = min(s + child_dur, end)
            obj.rotate_by(s, e, degrees, easing=easing)
        return self

    def animate_each(self, method, start: float = 0, end: float = 1,
                     delay=None, reverse=False, **method_kwargs):
        """Call *method* on each child with staggered timing.

        method: string name of a VObject method (e.g. 'fadein', 'wiggle', 'indicate').
        delay: time between each child's start (auto-computed from duration if None).
        reverse: iterate children in reverse order.
        Extra keyword arguments are forwarded to the method.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if delay is None:
            delay = dur / max(n, 1) * 0.5
        # Clamp delay so children don't overflow past end
        max_delay = dur / max(n, 2)
        delay = min(delay, max_delay)
        child_dur = max(dur - (n - 1) * delay, 0.01)
        items = list(reversed(self.objects)) if reverse else list(self.objects)
        for i, obj in enumerate(items):
            obj_start = start + i * delay
            obj_end = obj_start + child_dur
            getattr(obj, method)(start=obj_start, end=obj_end, **method_kwargs)
        return self

    def scatter_from(self, cx=None, cy=None, radius=300,
                      start: float = 0, end: float = 1, easing=easings.smooth):
        """Explode children outward from a center point.
        Each child moves along the ray from (cx, cy) through its center."""
        n = len(self.objects)
        if n == 0:
            return self
        cx, cy = self._resolve_center(start, cx, cy)
        for i, obj in enumerate(self.objects):
            ocx, ocy = obj.center(start)
            dx, dy = ocx - cx, ocy - cy
            dist = math.hypot(dx, dy)
            if dist < 1e-6:
                # At center: use evenly-spaced angles
                angle = math.tau * i / max(n, 1)
                dx, dy = math.cos(angle), math.sin(angle)
                dist = 1
            tx = ocx + dx / dist * radius
            ty = ocy + dy / dist * radius
            obj.move_to(tx, ty, start=start, end=end, easing=easing)
        return self

    def gather_to(self, cx=None, cy=None,
                   start: float = 0, end: float = 1, easing=easings.smooth):
        """Converge children to a center point (reverse of scatter_from)."""
        n = len(self.objects)
        if n == 0:
            return self
        gx, gy, gw, gh = self.bbox(start)
        cx = cx if cx is not None else gx + gw / 2
        cy = cy if cy is not None else gy + gh / 2
        for obj in self.objects:
            obj.move_to(cx, cy, start=start, end=end, easing=easing)
        return self

    def rotate_children(self, degrees=90, start: float = 0, end: float | None = None,
                         easing=easings.smooth):
        """Rotate all children around the group's center.
        Moves each child to its new angular position around the centroid."""
        n = len(self.objects)
        if n == 0:
            return self
        gcx, gcy = self.center(start)
        rad = math.radians(degrees)
        for obj in self.objects:
            cx, cy = obj.center(start)
            # Rotate (cx, cy) around (gcx, gcy)
            dx, dy = cx - gcx, cy - gcy
            new_cx = gcx + dx * math.cos(rad) - dy * math.sin(rad)
            new_cy = gcy + dx * math.sin(rad) + dy * math.cos(rad)
            obj.move_to(new_cx, new_cy, start=start, end=end, easing=easing)
        return self

    def wave_effect(self, start: float = 0, end: float = 1, amplitude=20, axis='y',
                    easing=easings.smooth):
        """Propagate a wave through children — each child shifts up/down (or left/right)
        with a phase offset creating a traveling wave effect."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        for i, obj in enumerate(self.objects):
            phase = i / max(n - 1, 1)
            _s, _d, _a, _ph = start, max(dur, 1e-9), amplitude, phase
            def _wave(t, _s=_s, _d=_d, _a=_a, _ph=_ph, _easing=easing):
                p = _easing((t - _s) / _d)
                envelope = math.sin(math.pi * p)  # 0→1→0
                return _a * math.sin(math.tau * (p - _ph)) * envelope
            if axis == 'y':
                for xa, ya in obj._shift_reals():
                    ya.add(start, end, _wave)
                for c in obj._shift_coors():
                    c.add(start, end, lambda t, _w=_wave: (0, _w(t)))
            else:
                for xa, ya in obj._shift_reals():
                    xa.add(start, end, _wave)
                for c in obj._shift_coors():
                    c.add(start, end, lambda t, _w=_wave: (_w(t), 0))
        return self

    def sort_children(self, key='x', start: float = 0, end: float | None = None,
                       easing=easings.smooth):
        """Animate children to sorted positions along their arrangement axis.
        key: 'x' (sort left-to-right by x), 'y' (sort top-to-bottom by y),
             or a callable(obj, time) -> number.
        With end=None, reorders instantly. With end set, animates moves."""
        n = len(self.objects)
        if n <= 1:
            return self
        # Get current centers
        centers = [obj.center(start) for obj in self.objects]
        # Determine sort key for values
        if key == 'x':
            val_key = lambda i: centers[i][0]
        elif key == 'y':
            val_key = lambda i: centers[i][1]
        else:
            val_key = lambda i: key(self.objects[i], start)
        # value_order: indices sorted by value (value_order[0] has smallest value)
        value_order = sorted(range(n), key=val_key)
        if end is None:
            self.objects[:] = [self.objects[i] for i in value_order]
            return self
        # Position slots: sorted by position (leftmost/topmost first)
        pos_axis = 0 if key != 'y' else 1
        slot_order = sorted(range(n), key=lambda i: centers[i][pos_axis])
        # Object value_order[rank] should move to center of slot_order[rank]
        for rank in range(n):
            obj_idx = value_order[rank]
            slot_idx = slot_order[rank]
            if obj_idx == slot_idx:
                continue
            target = centers[slot_idx]
            cur = centers[obj_idx]
            dx, dy = target[0] - cur[0], target[1] - cur[1]
            if abs(dx) > 0.5 or abs(dy) > 0.5:
                self.objects[obj_idx].shift(dx=dx, dy=dy,
                    start=start, end=end, easing=easing)
        return self

    def apply(self, func):
        """Apply a function to each child. The function receives (child, index).
        Returns self for chaining."""
        for i, obj in enumerate(self.objects):
            func(obj, i)
        return self

    apply_function = apply

    def apply_with_delay(self, func, delay=0.1, start=0):
        """Apply *func* to each child with an incremental time delay.

        Calls ``func(child, index, start)`` for each child, where
        ``start = start + index * delay``.

        Parameters
        ----------
        func:
            A callable receiving ``(child, index, start)``.
        delay:
            Time delay between successive children.
        start:
            Base start time for the first child.

        Returns
        -------
        self
        """
        for i, obj in enumerate(self.objects):
            func(obj, i, start + i * delay)
        return self

    def zip_with(self, other, method_name_or_func, start=0, end=1, time=None, **kwargs):
        """Apply a method or function pairwise to children of this and another collection.

        Two calling styles are supported:

        * **Method-name string** — ``method_name_or_func`` is a ``str``; the
          named method is called on each child of *self* with the corresponding
          child of *other* as its first positional argument, followed by any
          extra ``**kwargs``::

              col_a.zip_with(col_b, 'become')
              col_a.zip_with(col_b, 'set_color', color='#FF0000')

        * **Callable** — ``method_name_or_func`` is a callable; it is invoked
          as ``func(obj_a, obj_b, time)`` for each pair (legacy behaviour)::

              col_a.zip_with(col_b, lambda a, b, t: a.move_to(*b.center(t), t))

        Iteration stops at the shorter collection's length.

        Parameters
        ----------
        other:
            Another :class:`VCollection` or any iterable of objects.
        method_name_or_func:
            Either a ``str`` naming a method on each child object, or a
            callable with signature ``(obj_a, obj_b, time)``.
        start:
            Start time. Default 0.
        end:
            End time. Default 1.
        time:
            Legacy parameter for the callable form. If not provided, defaults
            to *start*.
        **kwargs:
            Extra keyword arguments forwarded to the method when using the
            string form.  Ignored in the callable form.
        """
        if time is None:
            time = start
        other_objs = other.objects if hasattr(other, 'objects') else list(other)
        if isinstance(method_name_or_func, str):
            for a, b in zip(self.objects, other_objs):
                getattr(a, method_name_or_func)(b, **kwargs)
        else:
            for a, b in zip(self.objects, other_objs):
                method_name_or_func(a, b, time)
        return self

    def align_to(self, target, edge='left', start: float = 0, end: float | None = None, easing=None):
        """Align the collection's edge to match *target*'s edge.
        target: another VObject/VCollection.
        edge: 'left', 'right', 'top', 'bottom' or direction constant.
        When *end* is given, animate the movement over [start, end]."""
        edge = _norm_edge(edge, 'left')
        mx, my, mw, mh = self.bbox(start)
        ox, oy, ow, oh = target.bbox(start)
        offsets = {
            'left': (ox - mx, 0),
            'right': ((ox + ow) - (mx + mw), 0),
            'top': (0, oy - my),
            'bottom': (0, (oy + oh) - (my + mh)),
        }
        dx, dy = offsets.get(edge, (0, 0))
        kw = {'start': start}
        if end is not None:
            kw['end'] = end
        if easing is not None:
            kw['easing'] = easing
        for obj in self.objects:
            obj.shift(dx=dx, dy=dy, **kw)
        return self

    def write(self, start: float = 0, end: float = 1, processing=10, max_stroke_width=2, change_existence=True, easing=easings.smooth):
        if not self.objects:
            return self
        spc = (end - start) / (len(self.objects) + processing)
        for i, obj in enumerate(self.objects):
            obj.write(start=start+spc*i, end=start+spc*(i+processing+1),
                      max_stroke_width=max_stroke_width, change_existence=change_existence,
                      easing=easing)
        return self

    def snake_layout(self, cols=None, buff=SMALL_BUFF, start: float = 0):
        """Arrange children in a snake/zigzag grid pattern.

        Like :meth:`arrange_in_grid`, but alternates row direction: the first
        row goes left-to-right, the second row goes right-to-left, and so on.
        This creates a continuous reading path that avoids large jumps between
        row endings and beginnings, useful for flowcharts, timelines, or any
        sequential layout where visual continuity matters.

        Parameters
        ----------
        cols:
            Number of columns per row.  Defaults to ``ceil(sqrt(n))``.
        buff:
            Pixel spacing between cells (default ``SMALL_BUFF``).
        start:
            Time at which to read current positions and apply shifts.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if not n:
            return self
        if cols is None:
            cols = math.ceil(math.sqrt(n))
        boxes = [obj.bbox(start) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            # Reverse column order on odd rows (snake pattern)
            if r % 2 == 1:
                c = cols - 1 - c
            target_cx = c * cell_w + max_w / 2
            target_cy = r * cell_h + max_h / 2
            cur_cx = box[0] + box[2] / 2
            cur_cy = box[1] + box[3] / 2
            obj.shift(dx=target_cx - cur_cx, dy=target_cy - cur_cy,
                      start=start)
        return self

    def arrange_along_path(self, path_d, start: float = 0,
                           easing=None):
        """Position children evenly along an arbitrary SVG path.

        Each child's center is moved to a point on the path.  The children
        are spaced equally by arc length so they distribute uniformly along
        curves, straight segments, or any combination.

        Parameters
        ----------
        path_d:
            An SVG path ``d`` attribute string (e.g.
            ``'M100,500 C300,100 600,100 800,500'``).
        start:
            Time at which to read current positions and apply shifts.
        easing:
            Optional easing function to remap the parameter distribution.
            When ``None`` children are spaced uniformly by arc length.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        parsed, total_length = _parse_path(path_d)
        if total_length <= 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            if easing is not None:
                t = easing(t)
            target_len = t * total_length
            pt = parsed.point(parsed.ilength(target_len))
            tx, ty = pt.real, pt.imag
            cx, cy = obj.center(start)
            obj.shift(dx=tx - cx, dy=ty - cy, start=start)
        return self

    def converge(self, x: float = 960, y: float = 540,
                 start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate all children moving toward a common point.

        Each child slides from its current center to the target point (x, y)
        over [start, end].  This is useful for gathering scattered objects
        into a single location.

        Parameters
        ----------
        x, y:
            Target convergence point in SVG coordinates.
            Defaults to the canvas center (960, 540).
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function for the movement.

        Returns
        -------
        self
        """
        if not self.objects or end <= start:
            return self
        for obj in self.objects:
            ox, oy = obj.center(start)
            dx, dy = x - ox, y - oy
            if dx == 0 and dy == 0:
                continue
            obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def diverge(self, factor: float = 2.0, cx: float | None = None,
                cy: float | None = None, start: float = 0, end: float = 1,
                easing=easings.smooth):
        """Animate all children moving away from a common center.

        Each child slides outward from the collection's center (or the
        specified center) by a distance equal to *factor* times its
        current offset.  A factor of 2.0 doubles each child's distance
        from the center.

        Parameters
        ----------
        factor:
            Expansion multiplier.  Values > 1 spread children apart;
            values between 0 and 1 bring them closer together (but see
            :meth:`converge` for bringing them to a single point).
        cx, cy:
            Center of expansion.  Defaults to the collection's bounding
            box center at *start*.
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function for the movement.

        Returns
        -------
        self
        """
        if not self.objects or end <= start:
            return self
        cx, cy = self._resolve_center(start, cx, cy)
        for obj in self.objects:
            obj_cx, obj_cy = obj.center(start)
            dx = (obj_cx - cx) * (factor - 1)
            dy = (obj_cy - cy) * (factor - 1)
            if dx == 0 and dy == 0:
                continue
            obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def all_match(self, predicate):
        """Return True if all children match the predicate."""
        return all(predicate(obj) for obj in self.objects)

    def any_match(self, predicate):
        """Return True if any child matches the predicate."""
        return any(predicate(obj) for obj in self.objects)

    def pair_up(self):
        """Group adjacent children into pairs.

        Returns a list of :class:`VCollection` objects, each containing
        exactly two children.  If the number of children is odd, the last
        child is placed alone in a final single-element collection.

        This is useful for pairing labels with shapes, creating before/after
        pairs, or processing children two at a time.

        Returns
        -------
        list of VCollection
            Each collection contains two adjacent children (or one if the
            total count is odd).

        Raises
        ------
        ValueError
            If the collection is empty.

        Examples
        --------
        >>> col = VCollection(a, b, c, d)
        >>> pairs = col.pair_up()
        >>> len(pairs)
        2
        >>> len(pairs[0].objects)
        2
        """
        if len(self.objects) == 0:
            raise ValueError("Cannot pair_up an empty collection")
        result = []
        objs = self.objects
        for i in range(0, len(objs), 2):
            group = objs[i:i + 2]
            result.append(VCollection(*group))
        return result

    def sliding_window(self, size: int, step: int = 1):
        """Yield overlapping sub-collections using a sliding window.

        Slides a window of *size* elements across the children list,
        advancing by *step* each time.  Each window is returned as a
        :class:`VCollection`.

        Parameters
        ----------
        size:
            Number of children in each window.  Must be >= 1.
        step:
            Number of positions to advance between windows.  Must be >= 1.

        Returns
        -------
        list of VCollection
            Each sub-collection contains *size* children (the last window
            may contain fewer if *step* does not divide evenly).

        Raises
        ------
        ValueError
            If *size* or *step* is less than 1.

        Examples
        --------
        >>> col = VCollection(a, b, c, d, e)
        >>> windows = col.sliding_window(3, step=1)
        >>> len(windows)
        3
        >>> [len(w.objects) for w in windows]
        [3, 3, 3]
        """
        if size < 1:
            raise ValueError(f"window size must be >= 1, got {size!r}")
        if step < 1:
            raise ValueError(f"step must be >= 1, got {step!r}")
        objs = self.objects
        result = []
        i = 0
        while i + size <= len(objs):
            result.append(VCollection(*objs[i:i + size]))
            i += step
        return result

    def waterfall(self, start: float = 0, end: float = 1, height: float = 200,
                  stagger_frac: float = 0.3, easing=easings.smooth):
        """Staggered gravity-like entrance: children drop in from above.

        Each child starts above its final position (offset by *height* pixels)
        and falls down into place with a cascading delay.  Children also fade
        in during the fall.  Earlier children in the list start falling first.

        Parameters
        ----------
        start, end:
            Overall time interval for the waterfall.
        height:
            How far above its resting position each child starts (pixels).
        stagger_frac:
            Fraction of each child's duration that overlaps with the next
            child's start (0 = fully sequential, 1 = all start at once).
        easing:
            Easing function for each child's fall; ``easings.smooth`` gives
            a decelerating landing feel.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Compute per-child window with stagger overlap
        if n == 1:
            child_dur = dur
            delay = 0
        else:
            # Each child gets a window; consecutive windows overlap by stagger_frac
            child_dur = dur / (1 + (1 - stagger_frac) * (n - 1))
            delay = child_dur * (1 - stagger_frac)

        for i, obj in enumerate(self.objects):
            cs = start + i * delay
            ce = cs + child_dur
            # Hide before entrance
            obj.show.set_onward(0, False)
            obj.show.set_onward(cs, True)
            # Fade in
            _cs, _cd = cs, max(ce - cs, 1e-9)
            end_opacity = obj.styling.opacity.at_time(cs)
            obj.styling.opacity.set(cs, ce, _ramp(_cs, _cd, end_opacity, easing))
            # Drop from above: shift up by height, then animate down
            _h = height
            def _dy(t, _s=_cs, _d=_cd, _h=_h, _e=easing):
                p = _e((t - _s) / _d)
                return -_h * (1 - p)
            for _xa, ya in obj._shift_reals():
                ya.add(cs, ce, _dy, stay=True)
            for c in obj._shift_coors():
                c.add(cs, ce, lambda t, _f=_dy: (0, _f(t)), stay=True)
        return self

    def orbit_around(self, cx=None, cy=None, radius=None,
                     start: float = 0, end: float = 1, revolutions: float = 1,
                     easing=easings.linear):
        """Animate children orbiting around a center point.

        Each child is placed on a circle at equal angular intervals and
        then rotated around (cx, cy) over the time interval.  Children
        maintain their angular spacing while revolving.

        Parameters
        ----------
        cx, cy:
            Center of the orbit.  Defaults to the collection's bounding-box
            center.
        radius:
            Orbit radius in pixels.  Defaults to the average distance from
            each child's center to (cx, cy) at *start*.
        start, end:
            Time interval for the orbit animation.
        revolutions:
            Number of full revolutions (1.0 = 360 degrees).
        easing:
            Easing function applied to the angular progress.  Use
            ``easings.linear`` for constant-speed orbiting.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Resolve center
        cx, cy = self._resolve_center(start, cx, cy)
        # Compute initial angle and radius for each child
        child_data = []
        for obj in self.objects:
            ocx, ocy = obj.center(start)
            dx, dy = ocx - cx, ocy - cy
            dist = math.hypot(dx, dy)
            angle0 = math.atan2(dy, dx)
            child_data.append((angle0, dist, ocx, ocy))
        if radius is None:
            radius = sum(d[1] for d in child_data) / max(n, 1)
            # Use at least a small radius to avoid degenerate orbits
            if radius < 1:
                radius = 100
        _s, _d = start, max(dur, 1e-9)
        _cx, _cy, _r, _rev = cx, cy, radius, revolutions

        for i, obj in enumerate(self.objects):
            angle0, _, ocx, ocy = child_data[i]
            _a0, _ocx, _ocy = angle0, ocx, ocy
            def _dx(t, _s=_s, _d=_d, _cx=_cx, _r=_r, _rev=_rev,
                    _a0=_a0, _ocx=_ocx, _e=easing):
                p = _e((t - _s) / _d)
                angle = _a0 + math.tau * _rev * p
                return _cx + _r * math.cos(angle) - _ocx
            def _dy(t, _s=_s, _d=_d, _cy=_cy, _r=_r, _rev=_rev,
                    _a0=_a0, _ocy=_ocy, _e=easing):
                p = _e((t - _s) / _d)
                angle = _a0 + math.tau * _rev * p
                return _cy + _r * math.sin(angle) - _ocy
            for xa, ya in obj._shift_reals():
                xa.add(start, end, _dx)
                ya.add(start, end, _dy)
            for c in obj._shift_coors():
                c.add(start, end,
                      lambda t, _fdx=_dx, _fdy=_dy: (_fdx(t), _fdy(t)))
        return self

    def cascade_scale(self, start: float = 0, end: float = 1, factor=1.5,
                      delay=0.15, easing=easings.smooth):
        """Stagger scale animations across children with a fixed delay.

        Each child scales from its current size to *factor* times its size
        and back, with each successive child starting *delay* seconds after
        the previous one.  The per-child animation duration is automatically
        computed so that the last child finishes at *end*.

        Parameters
        ----------
        start, end:
            Overall time window for the staggered animation.
        factor:
            Peak scale multiplier for each child's pulse.
        delay:
            Seconds between the start of one child's animation and the next.
        easing:
            Easing used for the there-and-back scale motion.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Per-child animation duration
        total_delay = delay * (n - 1) if n > 1 else 0
        child_dur = max(dur - total_delay, 0.01)
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + child_dur, end)
            obj._ensure_scale_origin(s)
            sx0 = obj.styling.scale_x.at_time(s)
            sy0 = obj.styling.scale_y.at_time(s)
            _s, _d, _f = s, max(e - s, 1e-9), factor
            def _make_there_and_back(base, _s=_s, _d=_d, _f=_f, _easing=easing):
                return lambda t, _s=_s, _d=_d, _f=_f, _b=base, _easing=_easing: \
                    _b * (1 + (_f - 1) * math.sin(math.pi * _easing((t - _s) / _d)))
            obj.styling.scale_x.set(s, e, _make_there_and_back(sx0))
            obj.styling.scale_y.set(s, e, _make_there_and_back(sy0))
        return self

    def distribute_along_arc(self, cx=960, cy=540, radius=200,
                              start_angle=0, end_angle=None,
                              start: float = 0,
                              end: float | None = None,
                              easing=easings.smooth):
        """Arrange children evenly along a circular arc.

        Unlike :meth:`distribute_radial` (which places children around a
        full circle), this method distributes children along an arc spanning
        from *start_angle* to *end_angle* (in radians).

        Parameters
        ----------
        cx, cy:
            Center of the arc (default: canvas center).
        radius:
            Arc radius in pixels.
        start_angle:
            Starting angle in radians (0 = right, pi/2 = down).
        end_angle:
            Ending angle in radians.  Defaults to ``start_angle + pi``
            (a semicircle).
        start:
            Time at which to read current positions and apply the layout.
        end:
            If given, animate the children into position over
            [start, end].  If ``None``, positions are set
            instantly.
        easing:
            Easing for the animated version.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if end_angle is None:
            end_angle = start_angle + math.pi
        # For a single object, place it at the midpoint of the arc
        if n == 1:
            angle = (start_angle + end_angle) / 2
        for i, obj in enumerate(self.objects):
            if n > 1:
                t_frac = i / (n - 1)
                angle = start_angle + (end_angle - start_angle) * t_frac
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            obj_cx, obj_cy = obj.center(start)
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def fan_out(self, cx: float | None = None, cy: float | None = None,
                radius: float = 200, start: float = 0, end: float = 1,
                easing=easings.smooth):
        """Animate children spreading radially from a center point.

        All children move from their current positions to evenly spaced points
        on a circle of the given radius around (cx, cy).  If cx/cy are None,
        the collection's bounding box center is used.

        This is a creation/reveal animation: children fan outward like
        cards being dealt from a deck.
        """
        n = len(self.objects)
        if n == 0:
            return self
        cx, cy = self._resolve_center(start, cx, cy)
        for i, obj in enumerate(self.objects):
            angle = math.tau * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            obj_cx, obj_cy = obj.center(start)
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def align_centers(self, axis='x', value: float | None = None,
                      start: float = 0, end: float | None = None,
                      easing=easings.smooth):
        """Align all children's centers along a common axis line.

        axis: 'x' to align vertically (same x center) or 'y' to align
              horizontally (same y center).
        value: the target coordinate. If None, uses the collection's
               bounding box center for that axis.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if value is None:
            gc = self.center(start)
            value = gc[0] if axis == 'x' else gc[1]
        for obj in self.objects:
            oc = obj.center(start)
            if axis == 'x':
                dx = value - oc[0]
                dy = 0
            else:
                dx = 0
                dy = value - oc[1]
            if dx != 0 or dy != 0:
                obj.shift(dx=dx, dy=dy, start=start,
                          end=end, easing=easing)
        return self

    def distribute_evenly(self, start_x, start_y, end_x, end_y):
        """Distribute children evenly along a line from (start_x, start_y) to (end_x, end_y).

        The first child is centered at the start point, the last child at the
        end point, and the rest are evenly spaced between them.  With a single
        child, it is placed at the start point.  Returns self.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if n == 1:
            self.objects[0].center_to_pos(posx=start_x, posy=start_y)
            return self
        for i, obj in enumerate(self.objects):
            frac = i / (n - 1)
            px = start_x + frac * (end_x - start_x)
            py = start_y + frac * (end_y - start_y)
            obj.center_to_pos(posx=px, posy=py)
        return self

    def cascade_fadein(self, start=0, end=1, direction='left_to_right', easing=easings.smooth):
        """Fade in children with a cascade effect based on spatial ordering.

        direction determines sort order:
          'left_to_right' - sorts by x-position (ascending)
          'top_to_bottom' - sorts by y-position (ascending)
          'center_out' - sorts by distance from collection center (ascending)

        Each child gets a staggered fadein. Returns self.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Sort children by spatial criteria
        if direction == 'left_to_right':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[0])
        elif direction == 'top_to_bottom':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[1])
        elif direction == 'center_out':
            group_cx, group_cy = self.center(start)
            def _dist(o):
                ox, oy = o.center(start)
                return math.hypot(ox - group_cx, oy - group_cy)
            sorted_objs = sorted(self.objects, key=_dist)
        else:
            sorted_objs = list(self.objects)
        if n == 1:
            sorted_objs[0].fadein(start=start, end=end, easing=easing)
            return self
        # Compute staggered timing with overlap
        overlap = 0.5
        child_dur = dur / (1 + (1 - overlap) * (n - 1))
        step = child_dur * (1 - overlap)
        for i, obj in enumerate(sorted_objs):
            s = start + i * step
            e = s + child_dur
            obj.fadein(start=s, end=e, easing=easing)
        return self

    def label_children(self, labels, direction=UP, buff=20, font_size=None, creation=0):
        """Create Text labels positioned relative to each child.

        Parameters
        ----------
        labels : list[str]
            List of label strings, one per child.
        direction : tuple
            Direction to place labels relative to children (e.g. UP, DOWN).
        buff : float
            Buffer space between child and label.
        font_size : float or None
            Font size for labels. If None, uses the default (48).
        creation : float
            Creation time for the label objects.

        Returns
        -------
        VCollection
            A new VCollection containing the Text labels.
        """
        from vectormation._shapes import Text  # lazy to avoid circular import
        label_objects = []
        for i, obj in enumerate(self.objects):
            if i >= len(labels):
                break
            text_kwargs = {'creation': creation}
            if font_size is not None:
                text_kwargs['font_size'] = font_size
            label = Text(labels[i], **text_kwargs)
            label.next_to(obj, direction=direction, buff=buff, start=creation)
            label_objects.append(label)
        return VCollection(*label_objects)

    def batch_animate(self, method_name, start=0, end=1, param_name=None, values=None, **kwargs):
        """Call a method on each child with a different parameter value.

        The *start* and *end* timing parameters are passed to the target
        method using whichever naming convention it expects.  If *kwargs*
        already contains explicit timing keys (``start``, ``end``,
        ``start``, ``end``), those take precedence.  Otherwise
        this method inspects the target to choose the right names.

        Parameters
        ----------
        method_name : str
            Name of the method to call on each child.
        start : float
            Start time for the animation.
        end : float
            End time for the animation.
        param_name : str or None
            If given, this keyword argument varies per child.
        values : list or None
            List of values, one per child. If param_name is given, each value
            is passed as that kwarg. Otherwise, each value is passed as the
            first positional argument after start/end.
        **kwargs
            Additional keyword arguments passed to every child's method call.

        Returns
        -------
        self
        """
        import inspect
        if values is None:
            values = [None] * len(self.objects)
        for i, obj in enumerate(self.objects):
            if i >= len(values):
                break
            method = getattr(obj, method_name)
            kw = dict(kwargs)
            # Add timing parameters if not already provided by caller
            has_timing = any(k in kw for k in ('start', 'end', 'start', 'end'))
            if not has_timing:
                sig = inspect.signature(method)
                params = sig.parameters
                if 'start' in params:
                    kw['start'] = start
                    if 'end' in params:
                        kw['end'] = end
                elif 'start' in params:
                    kw['start'] = start
                    if 'end' in params:
                        kw['end'] = end
            if param_name is not None:
                kw[param_name] = values[i]
                method(**kw)
            else:
                method(values[i], **kw)
        return self

    def connect_children(self, arrow=False, buff=0, start=0, **kwargs):
        """Draw connecting lines or arrows between consecutive children.

        For each pair of consecutive children ``(children[i], children[i+1])``,
        a :class:`Line` (or :class:`Arrow` if *arrow* is ``True``) is created
        from the right edge of child *i* to the left edge of child *i+1*.

        The *buff* parameter shrinks each connector by that many pixels at
        each end (useful to avoid overlapping the children).

        All connectors are added to this collection. Returns the list of
        connector objects.

        Parameters
        ----------
        arrow:
            If ``True``, use Arrow connectors instead of Lines.
        buff:
            Inset from each child edge in SVG units.
        start:
            Creation time for the connectors.
        **kwargs:
            Extra keyword arguments passed to the Line/Arrow constructor.

        Returns
        -------
        list
            The connector objects (also added to this collection).
        """
        connectors = []
        for i in range(len(self.objects) - 1):
            child_a = self.objects[i]
            child_b = self.objects[i + 1]
            x1, y1 = child_a.get_edge('right', time=start)
            x2, y2 = child_b.get_edge('left', time=start)
            # Apply buff: move start point right and end point left
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0 and buff > 0:
                ux, uy = dx / length, dy / length
                x1 += ux * buff
                y1 += uy * buff
                x2 -= ux * buff
                y2 -= uy * buff
            if arrow:
                from vectormation._arrows import Arrow as _Arrow
                connector = _Arrow(x1=x1, y1=y1, x2=x2, y2=y2,
                                   creation=start, **kwargs)
            else:
                from vectormation._shapes import Line as _Line
                connector = _Line(x1=x1, y1=y1, x2=x2, y2=y2,
                                  creation=start, **kwargs)
            connectors.append(connector)
            self.objects.append(connector)
        return connectors

    def align_children(self, axis='x', anchor='center'):
        """Align children along a shared axis.

        For ``axis='x'``: aligns children's x-positions so they share the
        same x-coordinate, based on *anchor* (``'min'`` = left edges,
        ``'center'`` = centers, ``'max'`` = right edges).

        For ``axis='y'``: same logic applied to y-positions (``'min'`` = top
        edges, ``'center'`` = centers, ``'max'`` = bottom edges).

        The reference value is the mean of all children's anchor values.
        Each child is shifted to match that reference.

        Parameters
        ----------
        axis:
            ``'x'`` or ``'y'``.
        anchor:
            ``'min'``, ``'center'``, or ``'max'``.

        Returns self.
        """
        if len(self.objects) < 2:
            return self
        # Compute anchor value for each child
        values = []
        for obj in self.objects:
            x, y, w, h = obj.bbox(0)
            if axis == 'x':
                if anchor == 'min':
                    values.append(x)
                elif anchor == 'max':
                    values.append(x + w)
                else:  # center
                    values.append(x + w / 2)
            else:  # axis == 'y'
                if anchor == 'min':
                    values.append(y)
                elif anchor == 'max':
                    values.append(y + h)
                else:  # center
                    values.append(y + h / 2)
        ref = sum(values) / len(values)
        # Shift each child to match the reference
        for obj, val in zip(self.objects, values):
            delta = ref - val
            if axis == 'x':
                obj.shift(dx=delta, start=0)
            else:
                obj.shift(dy=delta, start=0)
        return self

    def sort_by_distance(self, point, reverse=False, start=0):
        """Sort children by distance from a point.

        Parameters
        ----------
        point:
            An (x, y) tuple to measure distance from.
        reverse:
            If True, sort farthest first.
        start:
            Time at which to evaluate each child's center.

        Returns self.
        """
        px, py = point
        centers = {id(obj): obj.center(start) for obj in self.objects}
        self.objects.sort(
            key=lambda obj: math.hypot(centers[id(obj)][0] - px,
                                       centers[id(obj)][1] - py),
            reverse=reverse,
        )
        return self

    def apply_each(self, method_name, **per_child_kwargs):
        """Call a method on each child with per-child arguments.

        Each keyword argument should be a list whose length matches the
        number of children.  For child *i*, the i-th element of each list
        is passed as the corresponding keyword argument.

        Example::

            col.apply_each('set_fill', color=['#f00', '#0f0', '#00f'])

        Returns self.
        """
        n = len(self.objects)
        for key, values in per_child_kwargs.items():
            if len(values) != n:
                raise ValueError(
                    f"Length of '{key}' ({len(values)}) does not match "
                    f"number of children ({n})"
                )
        for i, child in enumerate(self.objects):
            kwargs_i = {key: values[i] for key, values in per_child_kwargs.items()}
            getattr(child, method_name)(**kwargs_i)
        return self

VGroup = VCollection

