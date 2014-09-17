import logging
import os
import uuid

UUID_FILENAME = '.sync'

class UniqueID:
    """Static class that keeps information regarding UUID"""

    @staticmethod
    def create(dir='.'):
        _id = uuid.uuid4()
        try:
            abspath = os.path.abspath(dir)
            filename = os.path.join(abspath, UUID_FILENAME)
            with open(filename, "a") as f:
                f.write(str(_id)+"\n")
            return _id
        except:
            logging.exception("Failed to create the file.")
            return None

    @staticmethod
    def loadrc(dir = '.'):
        try:
            abspath = os.path.abspath(dir)
            filename = os.path.join(abspath, UUID_FILENAME)
            with open(filename, "r") as f:
               return f.read().splitlines()
        except:
            logging.exception("Failed to read the .sync file")
            return None
