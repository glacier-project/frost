import logging
from time_utils import TimePrecision, convert_time_float

reset_col = '\x1b[0m'
max_name_l = 10
max_lt_l = 20

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

def get_logger_instance(parent_reactor: str, reactor_name: str):
    global max_name_l
    logger_name = parent_reactor
    if logger_name:
        logger_name += "."
    logger_name += reactor_name
    if len(logger_name) > max_name_l:
        max_name_l = len(logger_name)
    return logging.getLogger(logger_name)

class LFormatter(logging.Formatter):

    def __init__(
            self, 
            lf_logical_elapsed,
            time_precision: TimePrecision = TimePrecision.NSECS,
            fmt: str = "%(logical_time)s | %(levelname)s | %(name)s | %(message)s"
            ) -> None:
        super().__init__(fmt)
        self._lf_logical_elapsed = lf_logical_elapsed
        self._time_precision = time_precision
        self._unit = self.time_unit(time_precision)
        self._levelname_color = {
            logging.DEBUG: '\x1b[38;21m',
            logging.INFO: '\x1b[38;5;39m',
            logging.WARNING: '\x1b[38;5;226m',
            logging.ERROR: '\x1b[38;5;196m',
            logging.CRITICAL: '\x1b[31;1m'
        }
        self._formatters = {
            logging.DEBUG: logging.Formatter(self._levelname_color[logging.DEBUG] + fmt + reset_col),
            logging.INFO: logging.Formatter(self._levelname_color[logging.INFO] + fmt + reset_col),
            logging.WARNING: logging.Formatter(self._levelname_color[logging.WARNING] + fmt + reset_col),
            logging.ERROR: logging.Formatter(self._levelname_color[logging.ERROR] + fmt + reset_col),
            logging.CRITICAL: logging.Formatter(self._levelname_color[logging.CRITICAL] + fmt + reset_col)
        }
        self._name_color_dict = {}
        self._name_col_idx = 0
        # import random
        # random.seed(404)
        self._color_list = color_list
        # random.shuffle(self._color_list)

    def get_col_name(self, name):
        if name not in self._name_color_dict:
            colors = self._color_list[self._name_col_idx]
            self._name_col_idx += 1
            self._name_col_idx = self._name_col_idx % len(self._color_list)
            self._name_color_dict[name] = colors
        return self._name_color_dict[name]

    def format(self, record):
        global max_name_l
        logical_time = self._lf_logical_elapsed()
        record.logical_time = f"{convert_time_float(logical_time, TimePrecision.NSECS, self._time_precision):<20} ({self._unit})"
        record.levelname = '{:<10}'.format(record.levelname)
        
        colors = self.get_col_name(record.name)
        record.name = colors[0]+colors[1]+record.name.ljust(max_name_l)+reset_col+self._levelname_color[record.levelno]

        log_fmt = self._formatters[record.levelno]
        return log_fmt.format(record)
    
    def time_unit(self, ltf: TimePrecision) -> str:
        '''
        Get the time unit string for the given time unit.
        '''
        if ltf == TimePrecision.WEEKS:
            return 'weeks'
        if ltf == TimePrecision.DAYS:
            return 'days'
        if ltf == TimePrecision.HOURS:
            return 'hours'
        if ltf == TimePrecision.MINUTES:
            return 'min'
        if ltf == TimePrecision.SECS:
            return 's'
        if ltf == TimePrecision.MSECS:
            return 'ms'
        if ltf == TimePrecision.USECS:
            return 'us'
        if ltf == TimePrecision.NSECS:
            return 'ns'