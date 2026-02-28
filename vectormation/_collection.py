"""VCollection — container for multiple VObjects with collective operations."""
import math
import random
from copy import deepcopy

import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation._constants import ORIGIN, SMALL_BUFF, UP, RIGHT
from vectormation._base import (
    _norm_dir, _norm_edge, _ramp,
    _make_brect, _set_attr, _parse_path,
    _BBoxMethodsMixin,
)
def _stagger_timing(n, dur, overlap):
    """Compute (child_dur, step) for *n* items over *dur* with *overlap* fraction."""
    if n <= 1:
        return dur, 0
    child_dur = dur / (1 + (1 - overlap) * (n - 1))
    return child_dur, child_dur * (1 - overlap)

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
        """Insert one or more objects at *index*, preserving insertion order."""
        # Resolve negative indices once so that subsequent inserts stay correct
        # as the list grows.
        if index < 0:
            index = max(len(self.objects) + index, 0)
        for i, obj in enumerate(objs):
            self.objects.insert(index + i, obj)
        return self

    def _reorder_child(self, child, front):
        if isinstance(child, int):
            child = self.objects[child]
        if child in self.objects:
            self.objects.remove(child)
            if front:
                self.objects.append(child)
            else:
                self.objects.insert(0, child)
        return self

    def send_to_back(self, child):
        """Move a child to the back (rendered first, behind others)."""
        return self._reorder_child(child, front=False)

    def bring_to_front(self, child):
        """Move a child to the front (rendered last, on top)."""
        return self._reorder_child(child, front=True)

    def get_child(self, index):
        """Return the child at *index* (supports negative indices)."""
        n = len(self.objects)
        if index < -n or index >= n:
            raise IndexError(
                f"child index {index} out of range for collection with {n} object(s)"
            )
        return self.objects[index]

    nth = get_child

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
        """Sort children in-place by their x or y center coordinate."""
        axis_idx = 0 if axis == 'x' else 1
        self.objects.sort(key=lambda obj: obj.center(0)[axis_idx], reverse=reverse)
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
        return self.sort_objects(key=lambda obj: obj.bbox(time)[1], reverse=reverse)

    def sort_by_z(self, reverse=False, time=0):
        """Sort children by z-depth."""
        return self.sort_objects(key=lambda obj: obj.z.at_time(time), reverse=reverse)

    def sort_by(self, key_func, reverse=False):
        """Sort children by key_func(child). Does not animate — instant reorder."""
        self.objects.sort(key=key_func, reverse=reverse)
        return self

    def max_by(self, key):
        """Return the child with the maximum key value."""
        return max(self.objects, key=key) if self.objects else None

    def min_by(self, key):
        """Return the child with the minimum key value."""
        return min(self.objects, key=key) if self.objects else None

    def sum_by(self, key):
        """Sum the result of key(child) across all children."""
        return sum(key(obj) for obj in self.objects)

    def shuffle(self):
        """Randomly shuffle the order of children in-place."""
        random.shuffle(self.objects)
        return self

    def shuffle_animate(self, start=0, end=1, easing=None):
        """Animated random shuffle -- children smoothly slide to randomly reassigned positions."""
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
        """Rotate children order by *n* positions (first *n* move to end)."""
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
            if n: self.objects[0].set_opacity(start_opacity, start)
            return self
        opacity_attr = 'fill_opacity' if attr == 'fill' else 'stroke_opacity'
        for i, obj in enumerate(self.objects):
            opacity = start_opacity + (end_opacity - start_opacity) * i / (n - 1)
            getattr(obj.styling, opacity_attr).set_onward(start, opacity)
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

    def _resolve_center(self, start: float, cx: float | None = None, cy: float | None = None):
        if cx is None or cy is None:
            gcx, gcy = self.center(start)
            return (gcx if cx is None else cx), (gcy if cy is None else cy)
        return cx, cy

    def scale(self, factor, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale all children around the group center."""
        return self.stretch(factor, factor, start, end, easing)

    def scale_about_point(self, factor, px, py, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale all children about the pivot point (*px*, *py*)."""
        self._scale_origin = (px, py)
        return self.stretch(factor, factor, start, end, easing)

    def stretch(self, x_factor: float = 1, y_factor: float = 1, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Non-uniform scale of all children around the group center."""
        if self._scale_origin is None:
            self._scale_origin = self._resolve_center(start, None, None)
        for attr, factor in [(self._scale_x, x_factor), (self._scale_y, y_factor)]:
            _set_attr(attr, start, end, attr.at_time(start) * factor, easing)
        return self

    def rotate_to(self, start: float, end: float, degrees: float, cx: float | None = None, cy: float | None = None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy); return self._delegate('rotate_to', start, end, degrees, cx=cx, cy=cy, easing=easing)

    def rotate_by(self, start: float, end: float, degrees: float, cx: float | None = None, cy: float | None = None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy); return self._delegate('rotate_by', start, end, degrees, cx=cx, cy=cy, easing=easing)

    @staticmethod
    def _hshift(obj, horizontal, offset, start):
        """Shift *obj* by *offset* along the horizontal or vertical axis."""
        obj.shift(**{'dx' if horizontal else 'dy': offset, 'start': start})

    def arrange(self, direction: str | tuple = 'right', buff=SMALL_BUFF, start: float = 0):
        """Lay out children in a row or column with spacing."""
        direction = _norm_dir(direction)
        if not self.objects:
            return self
        horizontal = direction in ('right', 'left')
        sign = 1 if direction in ('right', 'down') else -1
        cursor = 0
        for obj in self.objects:
            x, y, w, h = obj.bbox(start)
            size = w if horizontal else h
            self._hshift(obj, horizontal, sign * (cursor - (x if horizontal else y)), start)
            cursor += size + buff
        return self

    def animated_arrange(self, direction=RIGHT, buff=SMALL_BUFF, start=0, end=1, easing=None):
        """Animated version of :meth:`arrange` -- smoothly moves children to arranged positions."""
        dir_name = _norm_dir(direction)
        if not self.objects:
            return self
        horizontal = dir_name in ('right', 'left')
        sign = 1 if dir_name in ('right', 'down') else -1
        cursor, targets = 0, []
        for obj in self.objects:
            x, y, w, h = obj.bbox(start)
            cx, cy = obj.center(start)
            size = w if horizontal else h
            offset = sign * (cursor - (x if horizontal else y))
            targets.append((cx + offset, cy) if horizontal else (cx, cy + offset))
            cursor += size + buff
        _easing = easing or easings.smooth
        for obj, (tx, ty) in zip(self.objects, targets):
            obj.center_to_pos(posx=tx, posy=ty, start=start, end=end, easing=_easing)
        return self

    def distribute(self, direction: str | tuple = 'right', buff=0, start: float = 0):
        """Distribute children evenly within the group's bounding box."""
        direction = _norm_dir(direction)
        if len(self.objects) < 2:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start) for obj in self.objects]
        total_size = sum(b[2] if horizontal else b[3] for b in boxes)
        group_box = self.bbox(start)
        available = (group_box[2] if horizontal else group_box[3]) - total_size
        spacing = max(available / (len(self.objects) - 1) if len(self.objects) > 1 else 0, buff)
        cursor = 0
        for obj, box in zip(self.objects, boxes):
            size = box[2] if horizontal else box[3]
            self._hshift(obj, horizontal, cursor - (box[0] if horizontal else box[1]), start)
            cursor += size + spacing
        return self

    def space_evenly(self, direction: str | tuple = 'right', total_span=None,
                     start_pos=None, start: float = 0):
        """Distribute children with equal gaps to fill exactly *total_span* pixels."""
        direction = _norm_dir(direction)
        if not self.objects:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start) for obj in self.objects]
        sizes = [b[2] if horizontal else b[3] for b in boxes]
        group_box = self.bbox(start)
        if total_span is None:
            total_span = group_box[2] if horizontal else group_box[3]
        if start_pos is None:
            start_pos = group_box[0] if horizontal else group_box[1]
        n = len(self.objects)
        gap = (total_span - sum(sizes)) / (n - 1) if n > 1 else 0
        cursor = start_pos
        for obj, box, size in zip(self.objects, boxes, sizes):
            self._hshift(obj, horizontal, cursor - (box[0] if horizontal else box[1]), start)
            cursor += size + gap
        return self

    def arrange_in_circle(self, radius=150, center=None, start_angle=0,
                          start=0, end=None, easing=None):
        """Arrange children in a circle (delegates to :meth:`distribute_radial`)."""
        if center is None:
            center = ORIGIN
        cx, cy = center
        return self.distribute_radial(cx=cx, cy=cy, radius=radius,
                                      start_angle=start_angle,
                                      start=start, end=end,
                                      easing=easing or easings.smooth)

    def distribute_radial(self, cx=ORIGIN[0], cy=ORIGIN[1], radius=200, start_angle=0,
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
        """Arrange children in a circle instantly (defaults center to collection bbox center)."""
        if center is None:
            center = self.center(start)
        cx, cy = center
        return self.distribute_radial(cx=cx, cy=cy, radius=radius,
                                      start_angle=start_angle, start=start)

    @staticmethod
    def _grid_dims(n, rows, cols):
        """Resolve rows/cols for a grid with *n* items."""
        if rows is None and cols is None:
            cols = math.ceil(math.sqrt(n))
        if rows is None:
            rows = math.ceil(n / cols)
        elif cols is None:
            cols = math.ceil(n / rows)
        return rows, cols

    def _grid_targets(self, rows, cols, buff, start):
        """Return (cols, cell_w, cell_h, max_w, max_h, boxes) for grid layout."""
        _, cols = self._grid_dims(len(self.objects), rows, cols)
        boxes = [obj.bbox(start) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        return cols, max_w + buff, max_h + buff, max_w, max_h, boxes

    def arrange_in_grid(self, rows=None, cols=None, buff=SMALL_BUFF, start: float = 0):
        """Lay out children in a grid. If rows/cols omitted, picks a square-ish grid."""
        if not self.objects:
            return self
        cols, cell_w, cell_h, max_w, max_h, boxes = self._grid_targets(rows, cols, buff, start)
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            obj.shift(dx=c * cell_w + max_w / 2 - (box[0] + box[2] / 2),
                       dy=r * cell_h + max_h / 2 - (box[1] + box[3] / 2), start=start)
        return self

    def animated_arrange_in_grid(self, rows=None, cols=None, buff=SMALL_BUFF, start: float = 0, end: float = 1, easing=None):
        """Animated version of :meth:`arrange_in_grid` -- smoothly moves children to grid positions."""
        if not self.objects:
            return self
        cols, cell_w, cell_h, max_w, max_h, _ = self._grid_targets(rows, cols, buff, start)
        kw: dict = {'start': start, 'end': end}
        if easing is not None:
            kw['easing'] = easing
        for idx, obj in enumerate(self.objects):
            r, c = divmod(idx, cols)
            obj.center_to_pos(c * cell_w + max_w / 2, r * cell_h + max_h / 2, **kw)
        return self

    def stagger(self, method_name, delay, **kwargs):
        """Call method on each child with staggered timing offsets."""
        for i, obj in enumerate(self.objects):
            kw = {k: (v + i * delay if k in ('start', 'end') else v) for k, v in kwargs.items()}
            getattr(obj, method_name)(**kw)
        return self

    def stagger_along_path(self, method_name, path_d, start=0, end=1,
                           delay=0.1, **kwargs):
        """Position children along an SVG path, then call *method_name* with staggered timing."""
        from svgpathtools import parse_path
        n = len(self.objects)
        if n == 0:
            return self
        parsed = parse_path(path_d)
        for i, obj in enumerate(self.objects):
            pt = parsed.point(i / max(n - 1, 1))
            obj.center_to_pos(posx=pt.real, posy=pt.imag, start=start)
            getattr(obj, method_name)(start=start + i * delay, end=end + i * delay, **kwargs)
        return self

    def stagger_random(self, method_name, start=0, end=1, seed=None, **kwargs):
        """Call method_name on each child in random order with equal stagger delay."""
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

    def wave_anim(self, start: float = 0, end: float = 1, amplitude=20, n_waves=1):
        """Staggered wave animation: children bob up and down with phase offsets."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        for i, obj in enumerate(self.objects):
            phase = math.tau * i / max(n, 1)
            def _dy(t, _s=start, _d=dur, _a=amplitude, _p=phase, _w=n_waves):
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

    apply_sequentially = sequential
    apply_sequential = sequential

    def spread(self, x1, y1, x2, y2, start: float = 0):
        """Distribute children evenly along a line from (x1, y1) to (x2, y2)."""
        n = len(self.objects)
        if n == 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            cx, cy = obj.center(start)
            obj.shift(dx=x1 + (x2 - x1) * t - cx, dy=y1 + (y2 - y1) * t - cy, start=start)
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
            'left': lambda bx, _y, _w, _h: (gx - bx, 0),
            'right': lambda bx, _y, bw, _h: ((gx + gw) - (bx + bw), 0),
            'top': lambda _x, by, _w, _h: (0, gy - by),
            'bottom': lambda _x, by, _w, bh: (0, (gy + gh) - (by + bh)),
            'center_x': lambda bx, _y, bw, _h: (gx + gw / 2 - (bx + bw / 2), 0),
            'center_y': lambda _x, by, _w, bh: (0, gy + gh / 2 - (by + bh / 2)),
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
        child_dur, step = _stagger_timing(n, dur, overlap)
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = s + child_dur
            getattr(obj, method_name)(start=s, end=e, **kwargs)
        return self

    lagged_start = cascade  # Manim-compatible alias

    def _stagger_fade(self, method, start, end, shift_dir, shift_amount, overlap, easing):
        return self.cascade(method, start=start, end=end, overlap=overlap,
                            shift_dir=shift_dir, shift_amount=shift_amount, easing=easing)

    def stagger_fadein(self, start: float = 0, end: float = 1,
                        shift_dir=None, shift_amount=50, overlap=0.5,
                        easing=easings.smooth):
        """Fade in children with staggered timing and optional shift direction."""
        return self._stagger_fade('fadein', start, end, shift_dir, shift_amount, overlap, easing)

    def stagger_fadeout(self, start: float = 0, end: float = 1,
                         shift_dir=None, shift_amount=50, overlap=0.5,
                         easing=easings.smooth):
        """Fade out children with staggered timing and optional shift direction."""
        return self._stagger_fade('fadeout', start, end, shift_dir, shift_amount, overlap, easing)

    def fade_in_one_by_one(self, start: float = 0, end: float = 1,
                            overlap=0.0, easing=easings.smooth):
        """Fade in each child sequentially with optional overlap between windows."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        slot = dur if n == 1 else (dur + overlap * (n - 1)) / n
        for i, obj in enumerate(self.objects):
            obj_start = start + i * (slot - overlap)
            obj.fadein(start=obj_start, end=min(obj_start + slot, end), easing=easing)
        return self

    def reveal(self, start: float = 0, end: float = 1, direction='left',
                easing=easings.smooth, shift_amount=30):
        """Reveal children one by one from a direction (curtain effect).
        direction: 'left' (left-to-right), 'right', 'top', 'bottom'.
        Each child fades in with a small shift from the given direction."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        per_child = (end - start) / n
        shift_map = {'left': (-shift_amount, 0), 'right': (shift_amount, 0),
                     'top': (0, -shift_amount), 'bottom': (0, shift_amount)}
        sdx, sdy = shift_map.get(direction, (-shift_amount, 0))
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            t1 = min(t0 + per_child * 1.5, end)
            obj.fadein(t0, t1, shift_dir=None)
            _d = max(t1 - t0, 1e-9)
            for s_val, is_x in ((sdx, True), (sdy, False)):
                if s_val == 0:
                    continue
                def _shift(t, _s=s_val, _t0=t0, _d=_d, _ea=easing):
                    return _s * (1 - _ea((t - _t0) / _d))
                for xa, ya in obj._shift_reals():
                    (xa if is_x else ya).add(t0, t1, _shift)
                for c in obj._shift_coors():
                    c.add(t0, t1, lambda t, _f=_shift, _x=is_x: (_f(t), 0) if _x else (0, _f(t)))
        return self

    def _dim_others(self, index, start, end, opacity=0.2, easing=easings.smooth):
        """Dim all children except *index*, restoring near *end*."""
        dur = end - start
        dim_end, undim_start = start + dur * 0.3, start + dur * 0.7
        for i, obj in enumerate(self.objects):
            if i != index:
                obj.dim(start=start, end=dim_end, opacity=opacity, easing=easing)
                obj.undim(start=undim_start, end=end, easing=easing)

    def highlight_child(self, index, start: float = 0, end: float = 1,
                         dim_opacity=0.2, easing=easings.smooth):
        """Emphasize child at `index` by dimming all others.
        At `end`, all opacities are restored."""
        self._dim_others(index, start, end, dim_opacity, easing)
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
        self._dim_others(n, start, end, 0.3, easing)
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
        n = len(self.objects)
        if n <= 1: return self
        centers = [obj.center(start) for obj in self.objects]
        indices = list(range(n))
        random.Random(seed).shuffle(indices)
        for i, obj in enumerate(self.objects):
            obj.move_to(*centers[indices[i]], start=start, end=end, easing=easing)
        return self

    def for_each(self, method_name, **kwargs):
        """Call a method with the same arguments on all children simultaneously.
        Example: group.for_each('set_color', color='red', start=1)"""
        for obj in self.objects:
            getattr(obj, method_name)(**kwargs)
        return self

    def each(self, func):
        """Call ``func(child)`` for every child and return self."""
        for obj in self.objects:
            func(obj)
        return self

    def flip_all(self, start: float = 0, end: float | None = None, axis='x',
                  easing=easings.smooth):
        """Flip (mirror) all children along an axis through the group's center.
        axis: 'x' (horizontal flip, reflect about vertical center line)
              'y' (vertical flip, reflect about horizontal center line)."""
        if not self.objects:
            return self
        gcx, gcy = self.center(start)
        for obj in self.objects:
            cx, cy = obj.center(start)
            ncx = 2 * gcx - cx if axis == 'x' else cx
            ncy = 2 * gcy - cy if axis != 'x' else cy
            obj.move_to(ncx, ncy, start=start, end=end, easing=easing)
        return self

    def stagger_color(self, start: float = 0, end: float = 1, colors=('#FF6B6B', '#58C4DD'),
                       attr='fill'):
        """Propagate a color wave through children — each child transitions
        through the color sequence with a delay."""
        n = len(self.objects)
        if n == 0 or len(colors) < 2 or end <= start:
            return self
        per_child = (end - start) / n
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            obj.color_gradient_anim(colors=colors, start=t0, end=min(t0 + per_child * 2, end), attr=attr)
        return self

    @staticmethod
    def _apply_scale_pop(obj, s, e, factor, easing):
        """Apply a scale-up-and-back animation to obj over [s, e]."""
        obj._ensure_scale_origin(s)
        sx0 = obj.styling.scale_x.at_time(s)
        sy0 = obj.styling.scale_y.at_time(s)
        _d = max(e - s, 1e-9)
        def _make_pop(base, _s=s, _d=_d, _f=factor, _ea=easing):
            return lambda t, _b=base: _b * (1 + (_f - 1) * math.sin(math.pi * _ea((t - _s) / _d)))
        obj._set_scale_xy(s, e, _make_pop(sx0), _make_pop(sy0))

    def stagger_scale(self, start: float = 0, end: float = 1,
                       scale_factor=1.5, delay=0.2, easing=easings.smooth,
                       target_scale=None):
        """Scale each child up then back down with a stagger delay, creating a popping wave."""
        if target_scale is not None:
            scale_factor = target_scale
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        pop_dur = max(dur - (n - 1) * delay, dur / n) if n > 1 else dur
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + pop_dur, end)
            if e <= s:
                continue
            self._apply_scale_pop(obj, s, e, scale_factor, easing)
        return self

    def stagger_rotate(self, start: float = 0, end: float = 1, degrees=360, easing=easings.smooth):
        """Sequentially rotate each child."""
        n = len(self.objects)
        if n == 0 or end <= start: return self
        step = (end - start) / n
        for i, obj in enumerate(self.objects):
            s = start + i * step
            obj.rotate_by(s, min(s + step * 1.5, end), degrees, easing=easing)
        return self

    def animate_each(self, method, start: float = 0, end: float = 1,
                     delay=None, reverse=False, **method_kwargs):
        """Call *method* on each child with staggered timing."""
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

    def scatter_from(self, cx: float | None = None, cy: float | None = None, radius: float = 300,
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

    def gather_to(self, cx=None, cy=None, start=0, end=1, easing=easings.smooth):
        """Converge children to a center point (reverse of scatter_from)."""
        cx, cy = self._resolve_center(start, cx, cy)
        return self.converge(cx, cy, start=start, end=end, easing=easing)

    def rotate_children(self, degrees=90, start: float = 0, end: float | None = None,
                         easing=easings.smooth):
        """Rotate all children around the group's center.
        Moves each child to its new angular position around the centroid."""
        if not self.objects:
            return self
        gcx, gcy = self.center(start)
        cos_r, sin_r = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
        for obj in self.objects:
            cx, cy = obj.center(start)
            dx, dy = cx - gcx, cy - gcy
            obj.move_to(gcx + dx * cos_r - dy * sin_r, gcy + dx * sin_r + dy * cos_r,
                        start=start, end=end, easing=easing)
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
        """Apply ``func(child, index, start)`` to each child with incremental time delay."""
        for i, obj in enumerate(self.objects):
            func(obj, i, start + i * delay)
        return self

    def zip_with(self, other, method_name_or_func, start=0, end=1, **kwargs):
        """Apply a method or function pairwise to children of this and another collection."""
        other_objs = other.objects if hasattr(other, 'objects') else list(other)
        if isinstance(method_name_or_func, str):
            for a, b in zip(self.objects, other_objs):
                getattr(a, method_name_or_func)(b, **kwargs)
        else:
            for a, b in zip(self.objects, other_objs):
                method_name_or_func(a, b, start)
        return self

    def align_to(self, other, edge='left', start: float = 0, end: float | None = None, easing=None):
        """Align the collection's edge to match *other*'s edge.
        other: another VObject/VCollection.
        edge: 'left', 'right', 'top', 'bottom' or direction constant.
        When *end* is given, animate the movement over [start, end]."""
        edge = _norm_edge(edge, 'left')
        mx, my, mw, mh = self.bbox(start)
        ox, oy, ow, oh = other.bbox(start)
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

    # -- Animation delegation: apply to all children simultaneously --

    def fadein(self, start=0.0, end=1.0, **kw): return self._delegate('fadein', start=start, end=end, **kw)
    def fadeout(self, start=0.0, end=1.0, **kw): return self._delegate('fadeout', start=start, end=end, **kw)
    def create(self, start=0.0, end=1.0, **kw): return self._delegate('create', start=start, end=end, **kw)
    def draw_along(self, start=0.0, end=1.0, **kw): return self._delegate('draw_along', start=start, end=end, **kw)
    def slide_in(self, start=0.0, end=1.0, **kw): return self._delegate('slide_in', start=start, end=end, **kw)
    def slide_out(self, start=0.0, end=1.0, **kw): return self._delegate('slide_out', start=start, end=end, **kw)
    def zoom_in(self, start=0.0, end=1.0, **kw): return self._delegate('zoom_in', start=start, end=end, **kw)
    def zoom_out(self, start=0.0, end=1.0, **kw): return self._delegate('zoom_out', start=start, end=end, **kw)
    def grow_from_center(self, start=0.0, end=1.0, **kw): return self._delegate('grow_from_center', start=start, end=end, **kw)
    def shrink_to_center(self, start=0.0, end=1.0, **kw): return self._delegate('shrink_to_center', start=start, end=end, **kw)
    def spin_in(self, start=0.0, end=1.0, **kw): return self._delegate('spin_in', start=start, end=end, **kw)
    def spin_out(self, start=0.0, end=1.0, **kw): return self._delegate('spin_out', start=start, end=end, **kw)
    def pop_in(self, start=0.0, **kw): return self._delegate('pop_in', start=start, **kw)
    def pop_out(self, start=0.0, **kw): return self._delegate('pop_out', start=start, **kw)
    def draw_border_then_fill(self, start=0.0, end=1.0, **kw): return self._delegate('draw_border_then_fill', start=start, end=end, **kw)
    def indicate(self, start=0.0, end=1.0, **kw): return self._delegate('indicate', start=start, end=end, **kw)
    def create_then_fadeout(self, start=0.0, end=2.0, **kw): return self._delegate('create_then_fadeout', start=start, end=end, **kw)
    def write_then_fadeout(self, start=0.0, end=2.0, **kw): return self._delegate('write_then_fadeout', start=start, end=end, **kw)
    def fadein_then_fadeout(self, start=0.0, end=2.0, **kw): return self._delegate('fadein_then_fadeout', start=start, end=end, **kw)

    def show_increasing_subsets(self, start: float = 0, end: float = 1, easing=None):
        """Progressively reveal children over [start, end] — each child appears and stays visible."""
        n = len(self.objects)
        if n == 0: return self
        easing = easing or easings.linear
        dur = end - start
        if dur <= 0: return self
        for i, obj in enumerate(self.objects):
            t = start + dur * i / n
            obj._show_from(t)
        return self

    def show_one_by_one(self, start: float = 0, end: float = 1, method='fadein', **kwargs):
        """Show each child sequentially with a brief animation.
        Each child gets an equal time slice for its entrance animation."""
        n = len(self.objects)
        if n == 0: return self
        dur = end - start
        if dur <= 0: return self
        slice_dur = dur / n
        for i, obj in enumerate(self.objects):
            s = start + i * slice_dur
            getattr(obj, method)(start=s, end=s + slice_dur, **kwargs)
        return self

    def snake_layout(self, cols=None, buff=SMALL_BUFF, start: float = 0):
        """Arrange children in a snake/zigzag grid (alternating row direction)."""
        n = len(self.objects)
        if not n: return self
        if cols is None: cols = math.ceil(math.sqrt(n))
        boxes = [obj.bbox(start) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            if r % 2 == 1: c = cols - 1 - c
            obj.shift(dx=c * cell_w + max_w / 2 - (box[0] + box[2] / 2),
                      dy=r * cell_h + max_h / 2 - (box[1] + box[3] / 2), start=start)
        return self

    def arrange_along_path(self, path_d, start: float = 0,
                           easing=None):
        """Position children evenly along an arbitrary SVG path by arc length."""
        n = len(self.objects)
        if n == 0:
            return self
        parsed, total_length = _parse_path(path_d)
        if total_length <= 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            if easing is not None: t = easing(t)
            pt = parsed.point(parsed.ilength(t * total_length))
            cx, cy = obj.center(start)
            obj.shift(dx=pt.real - cx, dy=pt.imag - cy, start=start)
        return self

    def converge(self, x: float = ORIGIN[0], y: float = ORIGIN[1],
                 start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate all children moving toward a common point (x, y)."""
        if not self.objects or end <= start: return self
        for obj in self.objects:
            ox, oy = obj.center(start)
            if x != ox or y != oy:
                obj.shift(dx=x - ox, dy=y - oy, start=start, end=end, easing=easing)
        return self

    def diverge(self, factor: float = 2.0, cx: float | None = None,
                cy: float | None = None, start: float = 0, end: float = 1,
                easing=easings.smooth):
        """Animate all children moving away from a common center by *factor* times their offset."""
        if not self.objects or end <= start: return self
        cx, cy = self._resolve_center(start, cx, cy)
        for obj in self.objects:
            ocx, ocy = obj.center(start)
            dx, dy = (ocx - cx) * (factor - 1), (ocy - cy) * (factor - 1)
            if dx or dy:
                obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def all_match(self, predicate): return all(predicate(obj) for obj in self.objects)
    def any_match(self, predicate): return any(predicate(obj) for obj in self.objects)

    def pair_up(self):
        """Group adjacent children into pairs of VCollections."""
        if not self.objects:
            raise ValueError("Cannot pair_up an empty collection")
        objs = self.objects
        return [VCollection(*objs[i:i + 2]) for i in range(0, len(objs), 2)]

    def sliding_window(self, size: int, step: int = 1):
        """Return overlapping sub-collections using a sliding window of *size* with *step*."""
        if size < 1: raise ValueError(f"window size must be >= 1, got {size!r}")
        if step < 1: raise ValueError(f"step must be >= 1, got {step!r}")
        objs = self.objects
        return [VCollection(*objs[i:i + size]) for i in range(0, len(objs) - size + 1, step)]

    def waterfall(self, start: float = 0, end: float = 1, height: float = 200,
                  stagger_frac: float = 0.3, easing=easings.smooth):
        """Staggered gravity-like entrance: children drop in from above with cascading delay."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        child_dur, delay = _stagger_timing(n, dur, stagger_frac)
        for i, obj in enumerate(self.objects):
            cs = start + i * delay
            ce = cs + child_dur
            obj.show.set_onward(0, False)
            obj.show.set_onward(cs, True)
            _cs, _cd = cs, max(ce - cs, 1e-9)
            obj.styling.opacity.set(cs, ce, _ramp(_cs, _cd, obj.styling.opacity.at_time(cs), easing))
            def _dy(t, _s=_cs, _d=_cd, _h=height, _e=easing):
                return -_h * (1 - _e((t - _s) / _d))
            for _, ya in obj._shift_reals():
                ya.add(cs, ce, _dy, stay=True)
            for c in obj._shift_coors():
                c.add(cs, ce, lambda t, _f=_dy: (0, _f(t)), stay=True)
        return self

    def orbit_around(self, cx: float | None = None, cy: float | None = None, radius: float | None = None,
                     start: float = 0, end: float = 1, revolutions: float = 1,
                     easing=easings.linear):
        """Animate children orbiting around a center point with equal angular spacing."""
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

        for i, obj in enumerate(self.objects):
            angle0, _, ocx, ocy = child_data[i]
            def _orbit(t, _s=_s, _d=_d, _cx=cx, _cy=cy, _r=radius, _rev=revolutions,
                       _a0=angle0, _ocx=ocx, _ocy=ocy, _e=easing):
                angle = _a0 + math.tau * _rev * _e((t - _s) / _d)
                return _cx + _r * math.cos(angle) - _ocx, _cy + _r * math.sin(angle) - _ocy
            for xa, ya in obj._shift_reals():
                xa.add(start, end, lambda t, _f=_orbit: _f(t)[0])
                ya.add(start, end, lambda t, _f=_orbit: _f(t)[1])
            for c in obj._shift_coors():
                c.add(start, end, lambda t, _f=_orbit: _f(t))
        return self

    def cascade_scale(self, start: float = 0, end: float = 1, factor=1.5,
                      delay=0.15, easing=easings.smooth):
        """Stagger scale-up-and-back animations across children with a fixed delay."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        total_delay = delay * (n - 1) if n > 1 else 0
        child_dur = max((end - start) - total_delay, 0.01)
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + child_dur, end)
            self._apply_scale_pop(obj, s, e, factor, easing)
        return self

    def distribute_along_arc(self, cx=ORIGIN[0], cy=ORIGIN[1], radius=200,
                              start_angle=0, end_angle=None,
                              start: float = 0,
                              end: float | None = None,
                              easing=easings.smooth):
        """Arrange children evenly along a circular arc from *start_angle* to *end_angle*."""
        n = len(self.objects)
        if n == 0:
            return self
        if end_angle is None:
            end_angle = start_angle + math.pi
        arc_span = end_angle - start_angle
        for i, obj in enumerate(self.objects):
            angle = (start_angle + end_angle) / 2 if n == 1 else start_angle + arc_span * i / (n - 1)
            obj_cx, obj_cy = obj.center(start)
            obj.shift(dx=cx + radius * math.cos(angle) - obj_cx,
                      dy=cy + radius * math.sin(angle) - obj_cy,
                      start=start, end=end, easing=easing)
        return self

    def fan_out(self, cx=None, cy=None, radius=200, start=0, end=1, easing=easings.smooth):
        """Animate children spreading radially from a center point to evenly spaced positions."""
        cx, cy = self._resolve_center(start, cx, cy)
        return self.distribute_radial(cx=cx, cy=cy, radius=radius, start=start, end=end, easing=easing)

    def align_centers(self, axis='x', value: float | None = None,
                      start: float = 0, end: float | None = None,
                      easing=easings.smooth):
        """Align all children's centers along a common axis line."""
        if not self.objects: return self
        ai = 0 if axis == 'x' else 1
        if value is None:
            value = self.center(start)[ai]
        for obj in self.objects:
            oc = obj.center(start)
            delta = value - oc[ai]
            if delta:
                dx, dy = (delta, 0) if axis == 'x' else (0, delta)
                obj.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    distribute_evenly = spread

    def cascade_fadein(self, start=0, end=1, direction='left_to_right', easing=easings.smooth):
        """Fade in children with a cascade effect based on spatial ordering."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        if direction == 'left_to_right':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[0])
        elif direction == 'top_to_bottom':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[1])
        elif direction == 'center_out':
            gcx, gcy = self.center(start)
            sorted_objs = sorted(self.objects, key=lambda o: math.hypot(*(oc - gc for oc, gc in zip(o.center(start), (gcx, gcy)))))
        else:
            sorted_objs = list(self.objects)
        tmp = VCollection(*sorted_objs)
        tmp.cascade('fadein', start=start, end=end, overlap=0.5, easing=easing)
        return self

    def label_children(self, labels, direction=UP, buff=20, font_size=None, creation=0):
        """Create Text labels positioned relative to each child and return them as a VCollection."""
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
        """Call a method on each child with a different parameter value from *values*."""
        import inspect
        if values is None:
            values = [None] * len(self.objects)
        for i, obj in enumerate(self.objects):
            if i >= len(values):
                break
            method = getattr(obj, method_name)
            kw = dict(kwargs)
            if not any(k in kw for k in ('start', 'end')):
                params = inspect.signature(method).parameters
                if 'start' in params:
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
        """Draw connecting lines or arrows between consecutive children, adding them to the collection."""
        if arrow:
            from vectormation._arrows import Arrow as _Connector
        else:
            from vectormation._shapes import Line as _Connector
        connectors = []
        for i in range(len(self.objects) - 1):
            x1, y1 = self.objects[i].get_edge('right', time=start)
            x2, y2 = self.objects[i + 1].get_edge('left', time=start)
            if buff > 0:
                length = math.hypot(x2 - x1, y2 - y1)
                if length > 0:
                    ux, uy = (x2 - x1) / length, (y2 - y1) / length
                    x1 += ux * buff; y1 += uy * buff
                    x2 -= ux * buff; y2 -= uy * buff
            connector = _Connector(x1=x1, y1=y1, x2=x2, y2=y2, creation=start, **kwargs)
            connectors.append(connector)
            self.objects.append(connector)
        return connectors

    def align_children(self, axis='x', anchor='center'):
        """Align children along a shared axis using the mean of their anchor values."""
        if len(self.objects) < 2:
            return self
        def _val(x, y, w, h):
            v, s = (x, w) if axis == 'x' else (y, h)
            return v if anchor == 'min' else (v + s if anchor == 'max' else v + s / 2)
        values = [_val(*obj.bbox(0)) for obj in self.objects]
        ref = sum(values) / len(values)
        for obj, val in zip(self.objects, values):
            delta = ref - val
            obj.shift(**({'dx': delta} if axis == 'x' else {'dy': delta}), start=0)
        return self

    def sort_by_distance(self, point, reverse=False, start=0):
        """Sort children in-place by distance from a point."""
        px, py = point
        self.objects.sort(
            key=lambda obj: math.hypot(obj.center(start)[0] - px, obj.center(start)[1] - py),
            reverse=reverse,
        )
        return self

    def apply_each(self, method_name, **per_child_kwargs):
        """Call a method on each child with per-child keyword arguments (lists of values)."""
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

