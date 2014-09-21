import watcher.sync

LABEL = 'SYNC_MSG_'
FIELD_SEPARATOR = '\x00'
SUBFIELD_SEPARATOR = '\x01'

class UnknownMessageException(Exception):
    pass

class Message(object):
    def __init__(self):
        super(Message, self).__init__()

    @staticmethod
    def deserialize(message,_from=None):
        fields = message.split(FIELD_SEPARATOR)
        if fields[0] == LABEL + 'DISCOVERY':
            uuids = fields[1].split(SUBFIELD_SEPARATOR) if fields[1] else []
            return DiscoveryMSG(uuids,_from)
        elif fields[0] == LABEL + 'REQUEST':
            return RequestMSG(fields[1], fields[2], _from)
        else:
            raise UnknownMessageException

    def handle(self): raise NotImplemented

class DiscoveryMSG(Message):
    def __init__(self, uuids,_from=None):
        super(DiscoveryMSG, self).__init__()
        self.label = LABEL + 'DISCOVERY'
        self.uuids = set(uuids) if uuids else set()
        self._from = _from

    def serialize(self):
        field = SUBFIELD_SEPARATOR.join(map(str,self.uuids))
        return FIELD_SEPARATOR.join((self.label, field))

    def handle(self):
        if self._from:
            watcher.sync.Sync.newPeer(self._from,self.uuids)

class RequestMSG(Message):
    """Client sends this message to request from host the repo given."""
    def __init__(self, host, repo, _from=None):
        super(RequestMSG, self).__init__()
        self.label = LABEL + 'REQUEST'
        self.host = host
        self.repo = repo
        self._from = _from

    def serialize(self):
        return FIELD_SEPARATOR.join((self.label, self.host, self.repo))

    def handle(self):
        if self._from:
            watcher.sync.Sync.newRequestServer(self._from, self.host, self.repo)
