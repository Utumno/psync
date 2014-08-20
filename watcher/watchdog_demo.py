import logging
import shlex
from watchdog.observers import Observer

# internal imports
from watcher.cli import Parser
from gitter import git_api_wrapper
from watcher.event_handler import TestEventHandler

class Sync():

    observers=[]

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        parser = Parser.new(description='Monitor and sync directory changes')
        try:
            while True:
                # http://stackoverflow.com/a/17352877/281545
                cmd = shlex.split(raw_input('> ').strip())
                logging.debug('command line: %s', cmd)
                try:
                    parser.parse(cmd)
                except SystemExit: # DUH http://stackoverflow.com/q/16004901/281545
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
        git = git_api_wrapper.Git(path, ignored_files=ignored_files)
        ignored = git.getIgnoredPaths()
        logging.debug(ignored)
        ignored.append(".*\.git.*")
        event_handler = TestEventHandler(ignore_regexes=ignored)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        Sync.observers.append(observer)

if __name__ == "__main__":
    Sync()
