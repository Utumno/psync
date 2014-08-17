import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self, desc, add_h=True):
        super(Parser, self).__init__(description=desc, add_help=add_h,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        # https://docs.python.org/dev/library/argparse.html#sub-commands
        self.subparsers = subparsers = self.add_subparsers(
            help='sub-command help')
        # http://stackoverflow.com/a/8757447/281545
        subparsers._parser_class = argparse.ArgumentParser
        parsers = []
        # print watcher.commands
        # for parser in watcher.commands:
        # parsers.append(parser(subparsers))

    @staticmethod
    def new(description, add_help=True):
        return Parser(description, add_help)

    def parse(self, args):
        """
        Return an object which can be used to get the arguments as in:
            parser_instance.parse().milestone

        :return: ArgumentParser
        """
        return self.parse_args(args)
