#!/usr/bin/env python2
import logging
import shlex
import os
from watchdog.observers import Observer
# internal imports
from watcher.cli import Parser
from gitter import git_api_wrapper
from watcher.event_handler import TestEventHandler

class Sync(object):
    """Static class that keeps all the state of the running application.
    TODO: add persistent state (an ini ?)
    """
    # observers are threads - on exiting shut them down
    observers = []
    # _Tree classes that keep info on directory trees being watched
    watches = []

    class _Tree(object):
        def __init__(self, path):
            self.root = os.path.abspath(path)

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        parser = Parser(description='Monitor and sync directory changes')
        try:
            while True:
                # http://stackoverflow.com/a/17352877/281545
                cmd = shlex.split(raw_input('> ').strip())
                logging.debug('command line: %s', cmd)
                try:
                    parser.parse(cmd)
                except SystemExit:  # DUH
                # http://stackoverflow.com/q/16004901/281545
                    pass
        except KeyboardInterrupt:
            pass
        finally:
            for observer in self.observers:
                observer.stop()
            for observer in self.observers:
                observer.join()

    @staticmethod
    def addObserver(path='../../sandbox', ignored_files=("lol/*",)):
        abspath = os.path.abspath(path)
        logging.debug("User given path: %s -> %s" % (path, abspath))
        if not os.path.exists(abspath):
            logging.info("Creating directory %s" % abspath)
            os.makedirs(abspath)
        elif not os.path.isdir(abspath):
            logging.warn("%s is not a directory" % abspath)
            return
        for watch in Sync.watches:
            if abspath.startswith(watch.root + os.path.sep):
                # TODO: check parent folders
                logging.warn(
                    "%s is a subpath of %s which you already watch" % (
                    path, watch.root))
                return
        # FIXME - time of check time of use - lock the dir for deletion ?
        git = git_api_wrapper.Git(path, ignored_files=ignored_files)
        ignored = git.getIgnoredPaths()
        logging.debug(ignored)
        ignored.append(".*\.git.*")
        event_handler = TestEventHandler(ignore_regexes=ignored)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        Sync.observers.append(observer)
        Sync.watches.append(Sync._Tree(abspath))

if __name__ == "__main__":
    Sync()
