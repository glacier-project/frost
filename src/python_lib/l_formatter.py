import logging
from time_utils import TimePrecision, convert_time_float

reset_col = '\x1b[0m'
max_name_l = 10
max_lt_l = 20

TIME_UNITS = {
    TimePrecision.WEEKS: 'weeks', TimePrecision.DAYS: 'days', TimePrecision.HOURS: 'hours',
    TimePrecision.MINUTES: 'min', TimePrecision.SECS: 's', TimePrecision.MSECS: 'ms',
    TimePrecision.USECS: 'us', TimePrecision.NSECS: 'ns',
}

color_list = [
    ('\x1b[37m', '\x1b[48;5;23m'),
    ('\x1b[37m', '\x1b[48;5;25m'),
    ('\x1b[37m', '\x1b[48;5;27m'),
    ('\x1b[37m', '\x1b[48;5;35m'),
    ('\x1b[37m', '\x1b[48;5;37m'),
    ('\x1b[37m', '\x1b[48;5;39m'),
    ('\x1b[30m', '\x1b[48;5;47m'),
    ('\x1b[30m', '\x1b[48;5;49m'),
    ('\x1b[30m', '\x1b[48;5;51m'),
    ('\x1b[37m', '\x1b[48;5;95m'),
    ('\x1b[37m', '\x1b[48;5;97m'),
    ('\x1b[37m', '\x1b[48;5;99m'),
    ('\x1b[30m', '\x1b[48;5;107m'),
    ('\x1b[30m', '\x1b[48;5;109m'),
    ('\x1b[30m', '\x1b[48;5;111m'),
    ('\x1b[30m', '\x1b[48;5;119m'),
    ('\x1b[30m', '\x1b[48;5;121m'),
    ('\x1b[30m', '\x1b[48;5;123m'),
    ('\x1b[37m', '\x1b[48;5;167m'),
    ('\x1b[37m', '\x1b[48;5;169m'),
    ('\x1b[37m', '\x1b[48;5;171m'),
    ('\x1b[30m', '\x1b[48;5;179m'),
    ('\x1b[30m', '\x1b[48;5;181m'),
    ('\x1b[30m', '\x1b[48;5;183m'),
    ('\x1b[30m', '\x1b[48;5;191m'),
    ('\x1b[30m', '\x1b[48;5;193m'),
    ('\x1b[30m', '\x1b[48;5;195m'),
]

class LFormatter(logging.Formatter):

    def __init__(
            self, 
            lf_logical_elapsed,
            time_precision: TimePrecision = TimePrecision.NSECS,
            fmt: str = "%(logical_time)s | %(levelname)s | %(name)s | %(message)s"
            ) -> None:
        """
        Initialize a log formatter that prefixes records with Lingua Franca elapsed time and colors.

        Args:
            lf_logical_elapsed (Callable[[], int]): Returns the elapsed LF time in nanoseconds.
            time_precision (TimePrecision): Unit in which the time is displayed.
            fmt (str): Log format string, including the logical_time field.
        """
        super().__init__(fmt)
        self._lf_logical_elapsed = lf_logical_elapsed
        self._time_precision = time_precision
        self._unit = TIME_UNITS[time_precision]
        self._levelname_color = {
            logging.DEBUG: '\x1b[38;21m',
            logging.INFO: '\x1b[38;5;39m',
            logging.WARNING: '\x1b[38;5;226m',
            logging.ERROR: '\x1b[38;5;196m',
            logging.CRITICAL: '\x1b[31;1m'
        }
        self._formatters = {
            level: logging.Formatter(color + fmt + reset_col)
            for level, color in self._levelname_color.items()
        }
        self._name_color_dict = {}
        self._name_col_idx = 0
        self._color_list = color_list

    def get_col_name(self, name):
        """
        Return the (foreground, background) color pair for a logger name, assigning the next one round-robin on first use.

        Args:
            name (str): Logger name.
        """
        if name not in self._name_color_dict:
            colors = self._color_list[self._name_col_idx]
            self._name_col_idx += 1
            self._name_col_idx = self._name_col_idx % len(self._color_list)
            self._name_color_dict[name] = colors
        return self._name_color_dict[name]

    def format(self, record):
        """
        Format a record with elapsed time, padded level name and colored logger name.

        Args:
            record (logging.LogRecord): Record to format.
        """
        logical_time = self._lf_logical_elapsed()
        record.logical_time = f"{convert_time_float(logical_time, TimePrecision.NSECS, self._time_precision):<20} ({self._unit})"
        record.levelname = '{:<10}'.format(record.levelname)
        
        colors = self.get_col_name(record.name)
        record.name = colors[0]+colors[1]+record.name.ljust(max_name_l)+reset_col+self._levelname_color[record.levelno]

        log_fmt = self._formatters[record.levelno]
        return log_fmt.format(record)
