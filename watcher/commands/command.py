class Command(object):
    """A command given by the users - subclasses must define  the CMD_NAME,
    CMD_HELP and ARGUMENTS class fields"""

    def __call__(self, subparsers):
        parser_a = subparsers.add_parser(self.__class__.CMD_NAME,
                                         help=self.__class__.CMD_HELP)
        for dest, arg in self.__class__.ARGUMENTS.iteritems():
            parser_a.add_argument(dest=dest, help=arg.help, action=arg.action)
        return parser_a

class Arg(object):
    """Wrapper around cli arguments for a command"""

    def __init__(self, hlp=None, action='store'):
        self.help = hlp
        self.action = action
