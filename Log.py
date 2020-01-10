import logging


class Log:

    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('logfile.log', encoding='utf8')
        formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                                      "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self.logger = logger


logger = Log().logger
