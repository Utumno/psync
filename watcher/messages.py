LABEL = 'SYNC_MSG_'
FIELD_SEPARATOR = '\x00'
SUBFIELD_SEPARATOR = '\x01'

class Message(object):
    def __init__(self):
        super(Message, self).__init__()

    @staticmethod
    def deserialize(message):
        fields = message.split(FIELD_SEPARATOR)
        if fields[0] == LABEL + 'DISCOVERY':
            uuids = fields[1].split() if len(fields) > 1 else []
            return DiscoveryMSG(uuids)

class DiscoveryMSG(Message):
    def __init__(self, uuids):
        super(DiscoveryMSG, self).__init__()
        self.label = LABEL + 'DISCOVERY'
        self.uuids = uuids

    def serialize(self):
        field = SUBFIELD_SEPARATOR.join(self.uuids)
        return FIELD_SEPARATOR.join((self.label, field))
