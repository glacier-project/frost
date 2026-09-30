"""Model-neutral logical time shared by simulation participants."""

from dataclasses import dataclass

from time_utils import TimePrecision


@dataclass(frozen=True)
class SimTime:
    """An integer logical time with an explicit precision, independent of FMI."""

    value: int
    precision: TimePrecision = TimePrecision.NSECS

    def __post_init__(self) -> None:
        """Reject fractional ticks and unrecognized precision values."""
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise TypeError(f"SimTime.value must be an int, got {self.value!r}")
        if not isinstance(self.precision, TimePrecision):
            raise TypeError(f"SimTime.precision must be a TimePrecision, got {self.precision!r}")

    def ns(self) -> int:
        """Return the exact integer nanosecond count."""
        return self.value * int(self.precision)

    def to(self, precision: TimePrecision) -> "SimTime":
        """
        Convert to another precision using integer arithmetic, rounding down.

        Args:
            precision (TimePrecision): Target precision.
        """
        if not isinstance(precision, TimePrecision):
            raise TypeError(f"precision must be a TimePrecision, got {precision!r}")
        return SimTime(self.ns() // int(precision), precision)
