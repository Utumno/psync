import argparse
from watcher.commands.command import Command, Arg

class Quit(Command):
    class _QuitAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print("Bye")
            raise KeyboardInterrupt

    CMD_NAME = 'qqq'
    CMD_HELP = 'Quit the program'
    ARGUMENTS = {'dummy': Arg(action=_QuitAction, nargs='?')}
