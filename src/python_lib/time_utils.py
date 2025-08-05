from enum import IntEnum
import math 

class TimePrecision(IntEnum):
    NSECS = 1
    USECS = NSECS*1e3
    MSECS = USECS*1e3
    SECS = MSECS*1e3
    MINUTES = SECS*60
    HOURS = MINUTES*60
    DAYS = HOURS*24
    WEEKS = DAYS*7

def convert(time: float, tf_from: TimePrecision, tf_to: TimePrecision, rounding: bool = False) -> int:
    time = time * (tf_from/tf_to)
    if rounding:
        time = round(time)

    return math.floor(time)

def f_convert(time: float, tf_from: TimePrecision, tf_to: TimePrecision) -> float:
    # time is 
    time = time * (tf_from/tf_to)
    return time