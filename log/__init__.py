import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s',
                    datefmt='%H:%M:%S')
class Log(object):
    def __init__(self,*args,**kwargs):
        super(Log, self).__init__(*args,**kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def d(self, msg, *args, **kwargs):
        self.logger.debug(msg, args, **kwargs)

    def w(self, msg, *args, **kwargs):
        self.logger.warn(msg, args, **kwargs)

    def i(self, msg, *args, **kwargs):
        self.logger.info(msg, args, **kwargs)

    def e(self, msg, *args, **kwargs):
        self.logger.exception(msg, args, **kwargs)
