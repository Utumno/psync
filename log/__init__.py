import logging

# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                    datefmt='%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

class Log(object):
    clogger = logging.getLogger("Log")
    clogger.addHandler(fh)
    clogger.addHandler(ch)
    clogger.propagate = False # yep
    clogger.setLevel(logging.DEBUG)

    def __init__(self,*args,**kwargs):
        super(Log, self).__init__(*args,**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # yep
        # self.clogger.name = self.__class__.__name__ # cls picks this one up !
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def d(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def w(self, msg, *args, **kwargs):
        self.logger.warn(msg, *args, **kwargs)

    def i(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def e(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    @classmethod
    def cd(cls, msg, *args, **kwargs):
        cls.clogger.debug(msg, *args, **kwargs)

    @classmethod
    def cw(cls, msg, *args, **kwargs):
        cls.clogger.warn(msg, *args, **kwargs)

    @classmethod
    def ci(cls, msg, *args, **kwargs):
        cls.clogger.info(msg, *args, **kwargs)

    @classmethod
    def ce(cls, msg, *args, **kwargs):
        cls.clogger.exception(msg, *args, **kwargs)
