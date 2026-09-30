from enum import IntEnum
import math

class TimePrecision(IntEnum):
    NSECS = 1
    USECS = NSECS*1000
    MSECS = USECS*1000
    SECS = MSECS*1000
    MINUTES = SECS*60
    HOURS = MINUTES*60
    DAYS = HOURS*24
    WEEKS = DAYS*7

def convert_time(time: float, tf_from: TimePrecision, tf_to: TimePrecision, rounding: bool = False) -> int:
    """
    Convert a time value between precisions, returning an integer count in the target unit.

    Args:
        time (float): Time value expressed in tf_from units.
        tf_from (TimePrecision): Source unit.
        tf_to (TimePrecision): Target unit.
        rounding (bool): Round to nearest if True, otherwise floor.
    """
    value = time * (tf_from / tf_to)
    return int(round(value)) if rounding else math.floor(value)

def convert_time_float(time: float, tf_from: TimePrecision, tf_to: TimePrecision) -> float:
    """
    Convert a time value between precisions without truncation.

    Args:
        time (float): Time value expressed in tf_from units.
        tf_from (TimePrecision): Source unit.
        tf_to (TimePrecision): Target unit.
    """
    return time * (tf_from/tf_to)