
from __future__ import annotations

import time
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    alpha: float = 1.0
    scale: float = 1.0


def ease_out_cubic(t: float) -> float:
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return 1 - (1 - t) ** 3


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_pose(a: Pose, b: Pose, t: float) -> Pose:
    return Pose(
        x=lerp(a.x, b.x, t),
        y=lerp(a.y, b.y, t),
        alpha=lerp(a.alpha, b.alpha, t),
        scale=lerp(a.scale, b.scale, t),
    )


class Animator:
    DURATION = 0.32

    def __init__(self):
        self._from: dict[str, Pose] = {}
        self._to: dict[str, Pose] = {}
        self._start: float = 0.0

    def commit(self, targets: dict[str, Pose], instant: bool = False):
        now = time.monotonic()
        new_from: dict[str, Pose] = {}
        for key, target in targets.items():
            if instant:
                new_from[key] = target
            elif key in self._to:
                new_from[key] = self._interp(key, now)
            else:
                new_from[key] = replace(target, alpha=0.0, scale=target.scale * 0.55)
        self._from = new_from
        self._to = dict(targets)
        self._start = now - (self.DURATION if instant else 0)

    def reset(self):
        self._from.clear()
        self._to.clear()

    def pose_at(self, key: str) -> Pose | None:
        target = self._to.get(key)
        if target is None:
            return None
        return self._interp(key, time.monotonic())

    def is_running(self) -> bool:
        return (time.monotonic() - self._start) < self.DURATION

    def _interp(self, key: str, now: float) -> Pose:
        start = self._from.get(key)
        target = self._to.get(key)
        if start is None:
            return target
        if target is None:
            return start
        t = (now - self._start) / self.DURATION
        return lerp_pose(start, target, ease_out_cubic(t))
