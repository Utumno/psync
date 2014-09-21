import argparse
from collections import OrderedDict
from log import Log
from watcher.commands.command import Command, Arg # move to __init__ ?
from watcher.sync import Sync

class Share(Command):
    class _ShareAction(argparse.Action,Log):
        def __call__(self, parser, namespace, values, option_string=None):
            Log.cd('%r %r %r' % (namespace, values, option_string))
            setattr(namespace, self.dest, values)
            Sync.newRequestClient(host=namespace.host, repo=values)

    CMD_NAME = 'share'
    CMD_HELP = 'Request to share a repo.'
    ARGUMENTS = OrderedDict()
    ARGUMENTS['host'] = Arg(hlp='The ip address of the peer')
    ARGUMENTS['repo'] = Arg(hlp='The repo id', action=_ShareAction)
