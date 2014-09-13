import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self, description, add_h=True):
        super(Parser, self).__init__(description=description, add_help=add_h,
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                        prog='sync')
        from watcher.sync import VERSION
        self.add_argument('-v', '--version', action='version',
                          version='%(prog)s ' + str(VERSION),
                          help="show program's version")
        # https://docs.python.org/dev/library/argparse.html#sub-commands
        subparsers = self.add_subparsers(title='Commands',
                                         description='valid subcommands',
                                         help='Type any of those passing the '
                                              '-h flag to get additional help')
        # http://stackoverflow.com/a/8757447/281545
        subparsers._parser_class = argparse.ArgumentParser
        from  watcher.commands import CMDS
        for cmd in CMDS: cmd()(subparsers)

    def parse(self, args):
        """
        Return an object which can be used to get the arguments as in:
            parser_instance.parse().milestone

        :return: ArgumentParser
        """
        return self.parse_args(args)
