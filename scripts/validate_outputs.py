"""Schema validation for every reported quantity.

Three bugs in this project came from the same root: attribute access on a pandas
row silently returning something that is not a number.

    lo.pct_change   -> DataFrame.pct_change, the method
    p5.between      -> Series.between, the method
    NaN or ""       -> NaN, because NaN is truthy, then str(NaN) == "nan"

Bracket access is the coding convention. This module is the enforceable
protection, because a convention only holds until someone forgets it.

Every coefficient, p-value, residual, rank and sample count that reaches a
document or a frozen artifact must pass `scalar()`, which requires the value to
be a scalar number, finite unless explicitly nullable, inside its domain bounds,
and JSON-serializable without custom coercion -- it returns a plain Python
float or int, so the coercion happens once, visibly, at the boundary.

A trap worth naming: np.float64 subclasses Python float and serializes to JSON
silently, while np.int64, np.float32 and np.bool_ do not. Code that only ever
handled float64 will appear to work and then fail on the first integer field.
scalar() coerces rather than trusting the type.
"""
import math

# domain bounds per kind of reported quantity
KINDS = {
    "p_value":     dict(lo=0.0, hi=1.0, integer=False),
    "r2":          dict(lo=0.0, hi=1.0, integer=False),
    "share":       dict(lo=0.0, hi=1.0, integer=False),
    "correlation": dict(lo=-1.0, hi=1.0, integer=False),
    "coefficient": dict(lo=None, hi=None, integer=False),
    "residual":    dict(lo=None, hi=None, integer=False),
    "se":          dict(lo=0.0, hi=None, integer=False),
    "rank":        dict(lo=1, hi=None, integer=True),
    "count":       dict(lo=0, hi=None, integer=True),
    "year":        dict(lo=1900, hi=2200, integer=True),
}


class OutputError(ValueError):
    """A reported quantity failed validation."""


def scalar(value, kind, name, nullable=False):
    """Validate and return a plain Python float/int. Raises OutputError."""
    if kind not in KINDS:
        raise OutputError(f"{name}: unknown kind {kind!r}; expected one of {sorted(KINDS)}")
    spec = KINDS[kind]

    if callable(value):
        raise OutputError(
            f"{name}: got a callable ({getattr(value, '__qualname__', value)!r}). "
            f"This is the pandas attribute-collision bug -- use row[{name!r}], not row.{name}")
    if isinstance(value, (str, bytes)):
        raise OutputError(f"{name}: got a string {value!r}, expected a number")
    if isinstance(value, (list, tuple, dict, set)):
        raise OutputError(f"{name}: got {type(value).__name__}, expected a scalar")
    # numpy arrays / pandas Series: anything with a length or a non-trivial shape
    if hasattr(value, "shape") and getattr(value, "shape", ()) not in ((), (1,)):
        raise OutputError(f"{name}: got an array of shape {value.shape}, expected a scalar")
    if hasattr(value, "__len__"):
        raise OutputError(f"{name}: got a sized object ({type(value).__name__}), expected a scalar")

    if value is None:
        if nullable:
            return None
        raise OutputError(f"{name}: got None and the field is not nullable")

    try:
        f = float(value)
    except (TypeError, ValueError) as e:
        raise OutputError(f"{name}: not numeric ({type(value).__name__}): {e}") from e

    if math.isnan(f):
        if nullable:
            return None
        raise OutputError(f"{name}: NaN and the field is not nullable")
    if math.isinf(f):
        raise OutputError(f"{name}: infinite")

    lo, hi = spec["lo"], spec["hi"]
    if lo is not None and f < lo:
        raise OutputError(f"{name}: {f} below the {kind} minimum {lo}")
    if hi is not None and f > hi:
        raise OutputError(f"{name}: {f} above the {kind} maximum {hi}")

    if spec["integer"]:
        if abs(f - round(f)) > 1e-9:
            raise OutputError(f"{name}: {f} must be a whole number for kind {kind}")
        return int(round(f))
    return f


def record(**fields):
    """Validate a whole reported record.

    Usage: record(p_value=("p_value", raw_p), rank=("rank", raw_rank))
    Returns a dict of clean Python scalars, JSON-serializable as-is.
    """
    out = {}
    for name, spec in fields.items():
        kind, value = spec[0], spec[1]
        nullable = spec[2] if len(spec) > 2 else False
        out[name] = scalar(value, kind, name, nullable)
    return out


def json_safe(obj, path="root"):
    """Raise unless obj serializes with the stdlib encoder and no custom coercion."""
    import json
    try:
        json.dumps(obj)
    except TypeError as e:
        raise OutputError(f"{path}: not JSON-serializable without coercion: {e}") from e
    return obj
