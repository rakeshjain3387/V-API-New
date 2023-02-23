import logging
import os


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    green = "\x1b[32m"
    pink = "\x1b[35m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(env)s - %(levelname)-8s %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: pink + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        record.env = os.environ.get("ENV", "develop")
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def getLogger(app):
    logger = logging.getLogger(app)
    ch = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)
    return logger
