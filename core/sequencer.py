from typing import Callable, TypedDict
import pykraken as kn


class SequenceFrame(TypedDict):
    name: list[Callable[[], None]]
    duration: float


class Sequencer:
    def __init__(self, frames: list[SequenceFrame]):
        self.frames = frames
        self.time = 0.0
        self.done = False
        self._total_duration = sum(f["duration"] for f in frames)

        self._current_index = -1      # so frame 0 fires immediately
        self._frame_start_times = self._compute_starts()

    def _compute_starts(self) -> list[float]:
        starts = []
        t = 0.0
        for f in self.frames:
            starts.append(t)
            t += f["duration"]
        return starts

    def _find_frame(self, t: float) -> int:
        """Return index of the frame for time t (clamped)."""
        if t >= self._total_duration:
            return len(self.frames) - 1

        # simple linear scan (fast enough for small lists)
        for i, start in enumerate(self._frame_start_times):
            end = start + self.frames[i]["duration"]
            if start <= t < end:
                return i

        return len(self.frames) - 1  # fallback

    def reset(self) -> None:
        self.time = 0.0
        self.done = False
        self._current_index = -1

    def update(self) -> None:
        if self.done:
            return

        self.time += kn.time.get_delta()

        # Clamp and mark done
        if self.time >= self._total_duration:
            self.time = self._total_duration
            self.done = True

        # Determine which frame time is currently in
        frame_index = self._find_frame(self.time)

        # If we changed frames → fire its callbacks
        if frame_index != self._current_index:
            self._current_index = frame_index
            for fn in self.frames[frame_index]["name"]:
                fn()
