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

def convert(time: float, tf_from: TimePrecision, tf_to: TimePrecision, rounding: bool = False) -> int:
    value = time * (tf_from / tf_to)
    return int(round(value)) if rounding else math.floor(value)

def f_convert(time: float, tf_from: TimePrecision, tf_to: TimePrecision) -> float:
    return time * (tf_from/tf_to)