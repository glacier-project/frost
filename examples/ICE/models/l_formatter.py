import logging
from time_utils import TimeFormat, TimeUtils


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
            ltf: TimeFormat = TimeFormat.NSECS,
            fmt: str = "%(logical_time)s | %(levelname)s | %(name)s | %(message)s", 
            colors: bool = True
            ) -> None:
        super().__init__(fmt)
        self._lf_logical_elapsed = lf_logical_elapsed
        self._ltf = TimeUtils(time_precision=ltf)
        self._unit = self.time_unit(ltf)
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
        self._name_color_dict={}
        self._name_col_idx = 0
        # import random
        # random.seed(404)
        self._color_list = color_list
        # random.shuffle(self._color_list)

    def get_col_name(self, name):
        if name not in self._name_color_dict:
            colors = self._color_list[self._name_col_idx]
            self._name_col_idx+=1
            self._name_col_idx = self._name_col_idx%len(self._color_list)
            self._name_color_dict[name] = colors
        return self._name_color_dict[name]

    def format(self, record):
        global max_name_l
        logical_time = self._lf_logical_elapsed()
        record.logical_time = '{:<20} ({})'.format(self._ltf.f_convert(logical_time, TimeFormat.NSECS), self._unit)
        record.levelname = '{:<10}'.format(record.levelname)
        
        name = record.name
        colors = self.get_col_name(record.name)
        record.name = colors[0]+colors[1]+record.name.ljust(max_name_l)+reset_col+self._levelname_color[record.levelno]

        log_fmt = self._formatters[record.levelno]
        return log_fmt.format(record)
    
    def time_unit(self, ltf: TimeFormat):
        if ltf == TimeFormat.WEEKS:
            return 'weeks'
        if ltf == TimeFormat.DAYS:
            return 'days'
        if ltf == TimeFormat.HOURS:
            return 'hours'
        if ltf == TimeFormat.MINUTES:
            return 'min'
        if ltf == TimeFormat.SECS:
            return 's'
        if ltf == TimeFormat.MSECS:
            return 'ms'
        if ltf == TimeFormat.USECS:
            return 'us'
        if ltf == TimeFormat.NSECS:
            return 'ns'
    
    def get_best_time_unit(self, time):
        # TODO is it usefull?
        if time > TimeFormat.SECS*10:
            return TimeFormat.SECS, 's'
        if time > TimeFormat.MSECS*10:
            return TimeFormat.MSECS, 'ms'
        if time > TimeFormat.USECS*10:
            return TimeFormat.USECS, 'us'
    
        return TimeFormat.NSECS, 'ns'
    