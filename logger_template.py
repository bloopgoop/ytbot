import logging
import datetime

# Define custom log message colors using ANSI escape codes
COLORS = {
    'GRAY': '\033[90m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'RESET': '\033[0m',
    'DEBUG': '\033[94m',
    'INFO': '\033[92m',
    'WARNING': '\033[93m',
    'ERROR': '\033[91m',
    'CRITICAL': '\033[95m'
}


class Formatter(logging.Formatter):
    def format(self, record):
        log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_time = f"{COLORS['GRAY']}{log_time}{COLORS['RESET']}"
        log_level = record.levelname
        log_message = record.getMessage()
        colored_log_message = f"{COLORS[log_level]}{log_level}: {log_message}{COLORS['RESET']}"
        return f"{log_time} {record.name} {colored_log_message}"
