from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, TypeAlias, overload


OffsetLike: TypeAlias = "Offset | tuple[float, float]"


def _as_offset(value: OffsetLike) -> tuple[float, float]:
    if isinstance(value, Offset):
        return value.dx, value.dy
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        return float(value[0]), float(value[1])
    raise TypeError("Expected Offset or tuple[float, float]")


@dataclass(frozen=True)
class Point:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, offset: OffsetLike) -> Point:
        dx, dy = _as_offset(offset)
        return Point(self.x + dx, self.y + dy)

    @overload
    def __sub__(self, other: Point) -> Offset: ...

    @overload
    def __sub__(self, other: OffsetLike) -> Point: ...

    def __sub__(self, other: Point | OffsetLike) -> Point | Offset:
        if isinstance(other, Point):
            return Offset(self.x - other.x, self.y - other.y)

        dx, dy = _as_offset(other)
        return Point(self.x - dx, self.y - dy)

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y


@dataclass(frozen=True)
class Offset:
    dx: float = 0.0
    dy: float = 0.0

    def __add__(self, other: OffsetLike) -> Offset:
        dx, dy = _as_offset(other)
        return Offset(self.dx + dx, self.dy + dy)

    def __sub__(self, other: OffsetLike) -> Offset:
        dx, dy = _as_offset(other)
        return Offset(self.dx - dx, self.dy - dy)

    def __neg__(self) -> Offset:
        return Offset(-self.dx, -self.dy)

    def __mul__(self, scale: float) -> Offset:
        return Offset(self.dx * scale, self.dy * scale)

    def __rmul__(self, scale: float) -> Offset:
        return self * scale

    def as_tuple(self) -> tuple[float, float]:
        return self.dx, self.dy

    def __iter__(self) -> Iterator[float]:
        yield self.dx
        yield self.dy
