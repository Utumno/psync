import argparse
from collections import OrderedDict
from log import Log
from watcher.commands.command import Command, Arg # move to __init__ ?
from watcher.sync import Sync

class Share(Command):
    class _ShareAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            Log.cd('%r %r %r' % (namespace, values, option_string))
            # sync = sys.modules['__main__']  # http://stackoverflow.com/
            # questions/13181559#comment17940192_13181615
            setattr(namespace, self.dest, values)
            # print sync.Sync.sync_client
            Sync.newRequest(host=namespace.host, repo=values)

    CMD_NAME = 'share'
    CMD_HELP = 'Request to share a repo.'
    ARGUMENTS = OrderedDict()
    ARGUMENTS['host'] = Arg(hlp='The ip address of the peer')
    ARGUMENTS['repo'] = Arg(hlp='The repo id', action=_ShareAction)
