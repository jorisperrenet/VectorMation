"""
Segments are Lines, Arcs, (Quadratic)BezierCurves
These represent the building blocks of shapes/objects like
    Squares, Circles, TexObjects
Segments do not have styling arguments whereas shapes/objects do.
A path is a collection of segments.

Some thoughts about functionalities are based on "SVG-Morpheus"
See: http://alexk111.github.io/SVG-Morpheus/
See: https://github.com/alexk111/SVG-Morpheus
Copyright (c) 2014 Alex Kaul

This was largely based on "svgpathtools"
See: https://github.com/mathandy/svgpathtools
Copyright (c) 2015 Andrew Allan Port
Copyright (c) 2013-2014 Lennart Regebro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
import svgpathtools
import numpy as np
import vectormation.easings as easings

def convert_to_bezier(seg, n_curves: int = 10):
    """Convert svgpathtools segment to CubicBezier, approximate arcs by n_curves splines."""
    if isinstance(seg, svgpathtools.Line):
        return [CubicBezier(start=seg.start, control1=seg.start, control2=seg.end, end=seg.end)]
    elif isinstance(seg, svgpathtools.CubicBezier):
        return [CubicBezier(start=seg.start, control1=seg.control1, control2=seg.control2, end=seg.end)]
    elif isinstance(seg, svgpathtools.QuadraticBezier):
        return [QuadraticBezier(start=seg.start, control=seg.control, end=seg.end).to_bezier()]
    elif isinstance(seg, svgpathtools.Arc):
        return [convert_to_bezier(bez)[0] for bez in seg.as_cubic_curves(n_curves)]
    else:
        raise TypeError(f"Unsupported segment type: {type(seg)}")


class CubicBezier(svgpathtools.CubicBezier):
    def bezier_morph(self, other, easing=easings.smooth):
        """Returns a function f(t) where 0<=t<=1 that interpolates this bezier to other."""
        def _lerp(a, b):
            return lambda t: a + (b - a) * easing(t)
        s, c1, c2, e = [_lerp(getattr(self, a), getattr(other, a))
                        for a in ('start', 'control1', 'control2', 'end')]
        return lambda t: CubicBezier(s(t), c1(t), c2(t), e(t))


class QuadraticBezier(svgpathtools.QuadraticBezier):
    def to_bezier(self):
        # https://stackoverflow.com/questions/3162645/convert-a-quadratic-bezier-to-a-cubic-one
        return CubicBezier(
            start=self.start,
            control1=self.start + 2/3*(self.control-self.start),
            control2=self.end + 2/3*(self.control-self.end),
            end=self.end
        )

class Path(svgpathtools.Path):
    def adjusted_bbox(self, *transforms):
        """Adjust the bbox of this path to the transforms given in svg-format as strings"""
        if transforms == ('',):
            return self.bbox()
        return self.adjusted_path(*transforms).bbox()

    def adjusted_path(self, *transforms):
        """Apply SVG transform strings to this path (in reverse order, matching SVG semantics)."""
        segs = self._segments  # type: ignore[attr-defined]
        for transform in reversed(transforms):
            match = re.match(r'(\w+)\(([^)]+)\)', transform)
            assert match is not None, f"Invalid SVG transform: {transform!r}"
            command, raw = match.groups()
            vals = [float(v) for v in re.split(r'[\s,]+', raw)]
            if command == 'scale':
                x, y = vals[0], vals[1] if len(vals) > 1 else vals[0]
                segs = Path(*segs).scaled(x, y, origin=0j)._segments  # type: ignore[attr-defined]
            elif command == 'translate':
                x, y = vals[0], vals[1] if len(vals) > 1 else 0
                segs = [s.translated(x + y * 1j) for s in segs]
            elif command == 'rotate':
                segs = Path(*segs).rotated(vals[0], origin=vals[1] + vals[2] * 1j)._segments  # type: ignore[attr-defined]
            else:
                raise NotImplementedError(f'Transform {command!r} not implemented')
        return Path(*segs)

def _segs_to_bezier(sub):
    """Flatten a subpath's segments into a list of CubicBezier curves."""
    return [b for seg in sub for b in convert_to_bezier(seg)]


def _point_at_bbox_center(path):
    """Return a degenerate CubicBezier at the bbox center of *path*."""
    xmin, xmax, ymin, ymax = path.bbox()
    c = (xmin + xmax) / 2 + (ymin + ymax) / 2 * 1j
    return CubicBezier(start=c, control1=c, control2=c, end=c)


def _balance_segments(segs, target_len):
    """Split longest segments until segs has target_len entries."""
    if not segs or target_len <= 0:
        return segs
    while len(segs) < target_len:
        max_idx = max(enumerate(segs), key=lambda x: x[1].length())[0]
        new1, new2 = segs[max_idx].split(0.5)
        segs = segs[:max_idx] + convert_to_bezier(new1) + convert_to_bezier(new2) + segs[max_idx+1:]
    return segs


class Paths:
    """A collection of Path objects, e.g. forming two Tex letters."""
    def __init__(self, *args):
        self.paths = [arg[0] for arg in args]
        self.stylings = [arg[1] for arg in args]

    def _morph_prepare(self, other, start: float = 0, end: float = 1, dist_vs_length=True):
        """Returns the segment pairs in Cubic Bezier form that need be merged.
        Matches whole compound paths first, then handles subpaths within each pair
        to preserve compound path structure (e.g. letters with holes)."""
        assert isinstance(other, Paths)

        # Step 1: Match whole paths (compound paths) by distance
        n_from, n_to = len(self.paths), len(other.paths)
        mat_dist = np.zeros((n_from, n_to))

        from_centers = {}
        to_centers = {}
        if dist_vs_length:
            for i, (path, st) in enumerate(zip(self.paths, self.stylings)):
                transforms = st.transform_style(start).split()
                xmin, xmax, ymin, ymax = path.adjusted_bbox(*transforms)
                from_centers[i] = ((xmin+xmax)/2, (ymin+ymax)/2)
            for j, (path, st) in enumerate(zip(other.paths, other.stylings)):
                transforms = st.transform_style(end).split()
                xmin, xmax, ymin, ymax = path.adjusted_bbox(*transforms)
                to_centers[j] = ((xmin+xmax)/2, (ymin+ymax)/2)

        for i in range(n_from):
            for j in range(n_to):
                if dist_vs_length:
                    fc, tc = from_centers[i], to_centers[j]
                    mat_dist[i, j] = ((fc[0]-tc[0])**2 + (fc[1]-tc[1])**2)**(1/2)
                else:
                    mat_dist[i, j] = abs(self.paths[i].length() / other.paths[j].length() - 1)

        matches = []
        for _ in range(min(n_from, n_to)):
            idx = np.unravel_index(np.nanargmin(mat_dist, axis=None), mat_dist.shape)
            mat_dist[idx[0], :] = np.nan
            mat_dist[:, idx[1]] = np.nan
            matches.append(idx)

        # Build path-level matches (including unmatched)
        path_matches = []
        if n_from >= n_to:
            for idx in set(range(n_from)) - {m[0] for m in matches}:
                path_matches.append((idx, None))
        else:
            for idx in set(range(n_to)) - {m[1] for m in matches}:
                path_matches.append((None, idx))
        for i, j in matches:
            path_matches.append((i, j))

        # Step 2: For each matched pair, split into subpaths and process
        subpath_segment_pairs = []
        for compound_id, (fi, ti) in enumerate(path_matches):
            path_from = Path(*self.paths[fi]._segments) if fi is not None else Path()  # type: ignore[attr-defined]
            path_to = Path(*other.paths[ti]._segments) if ti is not None else Path()  # type: ignore[attr-defined]
            style_from = self.stylings[fi] if fi is not None else other.stylings[ti]
            style_to = other.stylings[ti] if ti is not None else self.stylings[fi]

            subs_from = [Path(*p._segments) for p in path_from.continuous_subpaths()] if path_from else []  # type: ignore[attr-defined]
            subs_to = [Path(*p._segments) for p in path_to.continuous_subpaths()] if path_to else []  # type: ignore[attr-defined]

            if not subs_from and not subs_to:
                continue

            # One side empty: grow from / shrink to center
            if not subs_from or not subs_to:
                filled_subs = subs_to if not subs_from else subs_from
                src_path = path_to if not subs_from else path_from
                point = _point_at_bbox_center(src_path)
                for sub in filled_subs:
                    is_closed = sub.isclosed()
                    segs = _segs_to_bezier(sub)
                    if not subs_from:
                        segment_pairs = [(point, s) for s in segs]
                    else:
                        segment_pairs = [(s, point) for s in segs]
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to, is_closed, compound_id))
                continue

            # Both sides have subpaths — pair by index, pad shorter side
            n_sf, n_st = len(subs_from), len(subs_to)
            paired_from = list(subs_from)
            paired_to = list(subs_to)
            if n_sf < n_st:
                paired_from += [None] * (n_st - n_sf)
            elif n_st < n_sf:
                paired_to += [None] * (n_sf - n_st)

            for sf, st in zip(paired_from, paired_to):
                if sf is None:
                    # Extra target subpath: grow from source center
                    assert st is not None
                    is_closed = st.isclosed()
                    point = _point_at_bbox_center(path_from)
                    segs = _segs_to_bezier(st)
                    segment_pairs = [(point, s) for s in segs]
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to, is_closed, compound_id))
                elif st is None:
                    # Extra source subpath: shrink to target center
                    assert sf is not None
                    is_closed = sf.isclosed()
                    point = _point_at_bbox_center(path_to)
                    segs = _segs_to_bezier(sf)
                    segment_pairs = [(s, point) for s in segs]
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to, is_closed, compound_id))
                else:
                    is_closed = sf.isclosed() or st.isclosed()
                    segs_from = _segs_to_bezier(sf)
                    segs_to = _segs_to_bezier(st)
                    segs_from = _balance_segments(segs_from, len(segs_to))
                    segs_to = _balance_segments(segs_to, len(segs_from))
                    segment_pairs = list(zip(segs_from, segs_to))
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to, is_closed, compound_id))

        self.subpath_segment_pairs = subpath_segment_pairs
        return subpath_segment_pairs


    def morph(self, other, start: float = 0, end: float = 1, easing=easings.smooth):
        """Compute the morph from self to other, returning a list of
        (path_func, style_from, style_to) tuples for each matched subpath pair."""
        if hasattr(self, 'subpath_segment_pairs'):
            subpath_segment_pairs = self.subpath_segment_pairs
        else:
            subpath_segment_pairs = self._morph_prepare(other, start, end, dist_vs_length=True)

        objects = []
        for segment_pairs, style_from, style_to, is_closed, compound_id in subpath_segment_pairs:
            path = []
            for f, t in segment_pairs:
                seg_func = f.bezier_morph(t, easing=easing)
                path.append(seg_func)

            # Define the subpath as a function of time (0<=t<=1)
            def make_path_func(path, closed):
                def path_func(t):
                    d = Path(*[s(t) for s in path]).d()
                    if closed:
                        d += 'Z'
                    return d
                return path_func
            obj = (make_path_func(path, is_closed), style_from, style_to, compound_id)
            objects.append(obj)

        return objects
