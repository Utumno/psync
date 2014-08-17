import argparse

class Watch(object):

    class _WatchAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # print '%r %r %r' % (namespace, values, option_string)
            setattr(namespace, self.dest, values)

    class _Arg(object):
        def __init__(self, hlp=None, action='store'):
            self.help = hlp
            self.action = action

    CMD_NAME = 'watch'
    CMD_HELP = 'Watch a directory tree for changes'
    ARGUMENTS = {'path': _Arg(hlp='Path to a directory to watch. May be '
                                  'relative or absolute', action=_WatchAction)}

    def __call__(self, subparsers):
        parser_a = subparsers.add_parser(self.__class__.CMD_NAME,
                                         help=self.__class__.CMD_HELP)
        for dest, arg in self.__class__.ARGUMENTS.iteritems():
            parser_a.add_argument(dest=dest, help=arg.help, action=arg.action)
        return parser_a
