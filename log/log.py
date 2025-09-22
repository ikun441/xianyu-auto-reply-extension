import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class Log:
    def __init__(self,log_name):
        self.log_name = log_name
        self.logger = logging.getLogger(self.log_name)
    def info(self,msg):
        self.logger.info(msg)
    def error(self,msg):
        self.logger.error(msg)
    def debug(self,msg):
        self.logger.debug(msg)
    def warning(self,msg):
        self.logger.warning(msg)