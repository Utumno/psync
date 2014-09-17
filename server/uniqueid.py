import logging
import uuid

class UniqueID:
    """Static class that keeps information regarding UUID
    """

    uuid_cache = set([])

    @staticmethod
    def create():
        _id = uuid.uuid4()
        UniqueID.uuid_cache.add(_id)
        try:
            f = open(".sync", "a+")
            f.write(str(_id)+"\n")
        except:
            logging.exception("Failed to create the file.")


    @staticmethod
    def loadrc():
        try:
            f = open(".sync", "r")
            for line in f:
               UniqueID.uuid_cache.add(uuid.UUID(line))
        except:
            logging.exception("Failed to read the .sync file")


    @staticmethod
    def emfanise():
        print UniqueID.uuid_cache

    @staticmethod
    def remove(uuid):
        UniqueID.uuid_cache.remove(uuid)

if __name__ == "__main__":
    UniqueID.loadrc()
    UniqueID.emfanise()
    UniqueID.create()
    UniqueID.emfanise()
    UniqueID.remove()
    UniqueID.emfanise()
