import os
import uuid
from log import Log

UUID_FILENAME = '.sync'

class Uuid(Log):
    """Static class that creates and reads the UUID file of the repo."""
    @classmethod
    def create(cls, dir='.'):
        _id = str(uuid.uuid4())
        try:
            filename = os.path.join(os.path.abspath(dir), UUID_FILENAME)
            with open(filename, "a") as f:
                f.write(_id + "\n")
            return _id
        except:
            cls.ce("Failed to create the file.")
            return None

    @classmethod
    def readId(cls, dir='.'):
        try:
            filename = os.path.join(os.path.abspath(dir), UUID_FILENAME)
            if not os.path.isfile(filename): return None
            with open(filename, "r") as f:
                return f.read().splitlines()[0]
        except:
            cls.ce("Failed to read the .sync file")
            return None
