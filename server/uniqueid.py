import logging
import os
import uuid

"""Static module that creates and reads the UUID file of the repo."""

UUID_FILENAME = '.sync'

def create(dir='.'):
    _id = uuid.uuid4()
    try:
        filename = os.path.join(os.path.abspath(dir), UUID_FILENAME)
        with open(filename, "a") as f: f.write(str(_id) + "\n")
        return _id
    except:
        logging.exception("Failed to create the file.")
        return None

def loadrc(dir='.'):
    try:
        filename = os.path.join(os.path.abspath(dir), UUID_FILENAME)
        with open(filename, "r") as f: return f.read().splitlines()
    except:
        logging.exception("Failed to read the .sync file")
        return None
