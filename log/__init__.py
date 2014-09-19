import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s',
                    datefmt='%H:%M:%S')

# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

class Log(object):
    def __init__(self,*args,**kwargs):
        super(Log, self).__init__(*args,**kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def d(self, msg, *args, **kwargs):
        self.logger.debug(msg, args, **kwargs)

    def w(self, msg, *args, **kwargs):
        self.logger.warn(msg, args, **kwargs)

    def i(self, msg, *args, **kwargs):
        self.logger.info(msg, args, **kwargs)

    def e(self, msg, *args, **kwargs):
        self.logger.exception(msg, args, **kwargs)
