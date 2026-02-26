"""
NOTE: these easings/rate functions are copied from
https://github.com/ManimCommunity/manim/blob/main/manim/utils/rate_functions.py

MIT License

Copyright (c) 2018 3Blue1Brown LLC
Copyright (c) 2021, the Manim Community Developers

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
from collections.abc import Callable
from functools import wraps
from math import cos, exp, pi, sin, sqrt


def unit_interval(function):
    @wraps(function)
    def wrapper(t, *args, **kwargs):
        if 0 <= t <= 1:
            return function(t, *args, **kwargs)
        return 0 if t < 0 else 1
    return wrapper


def zero(function):
    @wraps(function)
    def wrapper(t, *args, **kwargs):
        if 0 <= t <= 1:
            return function(t, *args, **kwargs)
        return 0
    return wrapper


def sigmoid(x: float) -> float:
    return 1.0 / (1 + exp(-x))

@unit_interval
def linear(t: float) -> float:
    return t

@unit_interval
def smooth(t: float, inflection: float = 10.0) -> float:
    error = sigmoid(-inflection / 2)
    return min(max((sigmoid(inflection * (t - 0.5)) - error) / (1 - 2 * error), 0), 1)

@unit_interval
def rush_into(t: float, inflection: float = 10.0) -> float:
    return 2 * smooth(t / 2.0, inflection)

@unit_interval
def rush_from(t: float, inflection: float = 10.0) -> float:
    return 2 * smooth(t / 2.0 + 0.5, inflection) - 1

@unit_interval
def slow_into(t: float) -> float:
    return sqrt(1 - (1 - t) * (1 - t))

@unit_interval
def double_smooth(t: float) -> float:
    if t < 0.5:
        return 0.5 * smooth(2 * t)
    else:
        return 0.5 * (1 + smooth(2 * t - 1))

@zero
def there_and_back(t: float, inflection: float = 10.0) -> float:
    new_t = 2 * t if t < 0.5 else 2 * (1 - t)
    return smooth(new_t, inflection)

@zero
def there_and_back_with_pause(t: float, pause_ratio: float = 1.0 / 3) -> float:
    a = 1.0 / pause_ratio
    if t < 0.5 - pause_ratio / 2:
        return smooth(a * t)
    elif t < 0.5 + pause_ratio / 2:
        return 1
    else:
        return smooth(a - a * t)

def not_quite_there(
    func: Callable[[float], float] = smooth,
    proportion: float = 0.7,
) -> Callable[[float], float]:
    def result(t):
        return proportion * func(t)
    return result

@zero
def wiggle(t: float, wiggles: float = 2) -> float:
    return there_and_back(t) * sin(wiggles * pi * t)

def squish_rate_func(
    func: Callable[[float], float],
    a: float = 0.4,
    b: float = 0.6,
) -> Callable[[float], float]:
    def result(t):
        if a == b:
            return a
        if t < a:
            return func(0)
        elif t > b:
            return func(1)
        else:
            return func((t - a) / (b - a))
    return result

@unit_interval
def lingering(t: float) -> float:
    return squish_rate_func(lambda t: t, 0, 0.8)(t)

@unit_interval
def exponential_decay(t: float, half_life: float = 0.1) -> float:
    return 1 - exp(-t / half_life)

# -- Sine easings --

@unit_interval
def ease_in_sine(t: float) -> float:
    return 1 - cos((t * pi) / 2)

@unit_interval
def ease_out_sine(t: float) -> float:
    return sin((t * pi) / 2)

@unit_interval
def ease_in_out_sine(t: float) -> float:
    return -(cos(pi * t) - 1) / 2

# -- Power easings (quad, cubic, quart, quint) via factory --

def _make_power_easings(n):
    @unit_interval
    def ease_in(t):
        return t ** n
    @unit_interval
    def ease_out(t):
        return 1 - (1 - t) ** n
    @unit_interval
    def ease_in_out(t):
        return (2 ** (n - 1)) * t ** n if t < 0.5 else 1 - (-2 * t + 2) ** n / 2
    return ease_in, ease_out, ease_in_out

for _name, _n in [('quad', 2), ('cubic', 3), ('quart', 4), ('quint', 5)]:
    _ein, _eout, _eio = _make_power_easings(_n)
    _ein.__name__ = f'ease_in_{_name}'
    _eout.__name__ = f'ease_out_{_name}'
    _eio.__name__ = f'ease_in_out_{_name}'
    globals()[f'ease_in_{_name}'] = _ein
    globals()[f'ease_out_{_name}'] = _eout
    globals()[f'ease_in_out_{_name}'] = _eio

# -- Expo easings --

@unit_interval
def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else pow(2, 10 * t - 10)

@unit_interval
def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - pow(2, -10 * t)

@unit_interval
def ease_in_out_expo(t: float) -> float:
    if t == 0: return 0
    if t == 1: return 1
    return pow(2, 20 * t - 10) / 2 if t < 0.5 else (2 - pow(2, -20 * t + 10)) / 2

# -- Circ easings --

@unit_interval
def ease_in_circ(t: float) -> float:
    return 1 - sqrt(1 - t * t)

@unit_interval
def ease_out_circ(t: float) -> float:
    return sqrt(1 - (t - 1) ** 2)

@unit_interval
def ease_in_out_circ(t: float) -> float:
    return (
        (1 - sqrt(1 - (2 * t) ** 2)) / 2
        if t < 0.5
        else (sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2
    )

# -- Back easings --

@unit_interval
def ease_in_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

@unit_interval
def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

@unit_interval
def ease_in_out_back(t: float) -> float:
    c1 = 1.70158
    c2 = c1 * 1.525
    return (
        ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
        if t < 0.5
        else ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    )

# -- Elastic easings --

@unit_interval
def ease_in_elastic(t: float) -> float:
    c4 = (2 * pi) / 3
    if t == 0: return 0
    if t == 1: return 1
    return -pow(2, 10 * t - 10) * sin((t * 10 - 10.75) * c4)

@unit_interval
def ease_out_elastic(t: float) -> float:
    c4 = (2 * pi) / 3
    if t == 0: return 0
    if t == 1: return 1
    return pow(2, -10 * t) * sin((t * 10 - 0.75) * c4) + 1

@unit_interval
def ease_in_out_elastic(t: float) -> float:
    c5 = (2 * pi) / 4.5
    if t == 0: return 0
    if t == 1: return 1
    if t < 0.5:
        return -(pow(2, 20 * t - 10) * sin((20 * t - 11.125) * c5)) / 2
    return (pow(2, -20 * t + 10) * sin((20 * t - 11.125) * c5)) / 2 + 1

# -- Bounce easings --

@unit_interval
def ease_in_bounce(t: float) -> float:
    return 1 - ease_out_bounce(1 - t)

@unit_interval
def ease_out_bounce(t: float) -> float:
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        return n1 * (t - 1.5 / d1) * (t - 1.5 / d1) + 0.75
    elif t < 2.5 / d1:
        return n1 * (t - 2.25 / d1) * (t - 2.25 / d1) + 0.9375
    else:
        return n1 * (t - 2.625 / d1) * (t - 2.625 / d1) + 0.984375

@unit_interval
def ease_in_out_bounce(t: float) -> float:
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + ease_out_bounce(2 * t - 1)) / 2


# ── Easing combinators ──

def step(num_steps):
    """Return a step easing that quantizes t into num_steps discrete levels."""
    n = max(1, num_steps)
    def _step(t):
        t = max(0, min(1, t))
        return min(1.0, int(t * n) / (n - 1)) if n > 1 else 1.0 if t >= 1 else 0.0
    return _step


def reverse(easing):
    """Return an easing that runs in reverse (1→0 instead of 0→1)."""
    def _reversed(t):
        return 1 - easing(1 - t)
    return _reversed


def compose(*easings_list):
    """Chain multiple easings in sequence, each occupying an equal time slice."""
    n = len(easings_list)
    if n == 0:
        return linear
    if n == 1:
        return easings_list[0]
    def _composed(t):
        t = max(0, min(1, t))
        idx = min(int(t * n), n - 1)
        local_t = t * n - idx
        start_val = idx / n
        end_val = (idx + 1) / n
        return start_val + (end_val - start_val) * easings_list[idx](local_t)
    return _composed
