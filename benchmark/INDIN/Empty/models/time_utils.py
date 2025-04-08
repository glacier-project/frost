from singleton_meta import SingletonMeta
from enum import IntEnum
import math 

class TimeFormat(IntEnum):
    NSECS = 1
    USECS = NSECS*1e3
    MSECS = USECS*1e3
    SECS = MSECS*1e3
    MINUTES = SECS*60
    HOURS = MINUTES*60
    DAYS = HOURS*24
    WEEKS = DAYS*7

class TimeUtils(metaclass=SingletonMeta):
    def __init__(self, time_precision: TimeFormat=TimeFormat.NSECS, rounding:bool=False) -> None:
        self._time_precision = time_precision
        self._rounding = rounding

    def convert(self, time: float, time_precision: TimeFormat) -> int:
        # time is 
        time = time * (time_precision/self._time_precision)
        if self._rounding:
            time = round(time)

        return math.floor(time)

    def f_convert(self, time: float, time_precision: TimeFormat) -> int:
        # time is 
        time = time * (time_precision/self._time_precision)
        return time
    
def convert(time: float, tf_from: TimeFormat, tf_to: TimeFormat, rounding: bool = False) -> int:
    time = time * (tf_from/tf_to)
    if rounding:
        time = round(time)

    return math.floor(time)

def f_convert(time: float, tf_from: TimeFormat, tf_to: TimeFormat) -> float:
    # time is 
    time = time * (tf_from/tf_to)
    return time