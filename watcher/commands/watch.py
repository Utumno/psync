import argparse
from watcher.commands.command import Command, Arg # move to __init__ ?
from watcher.sync import Sync

class Watch(Command):
    class _WatchAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # logging.debug('%r %r %r' % (namespace, values, option_string))
            setattr(namespace, self.dest, values)
            Sync.addObserver(path=values)

    CMD_NAME = 'watch'
    CMD_HELP = 'Watch a directory tree for changes'
    ARGUMENTS = {'path': Arg(hlp='Path to a directory to watch. May be '
                                 'relative or absolute', action=_WatchAction)}
