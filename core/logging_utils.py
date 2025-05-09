import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class Logger:
    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def error(msg):
        logging.error(msg) 