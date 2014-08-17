import logging
import shlex
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
# internal imports
from watcher.cli import Parser
from gitter import git_api_wrapper

class TestEventHandler(RegexMatchingEventHandler):
    """Logs all the events captured."""

    def __init__(self, ignore_regexes=(".*\.git.*",)):
        """

        :param ignore_patterns: a list/tuple of wirldcard patterns - see
        Python27\Lib\site-packages\pathtools\patterns.py.match_path
        """
        super(TestEventHandler, self).__init__(ignore_regexes=ignore_regexes)

    def on_moved(self, event):
        super(TestEventHandler, self).on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(TestEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(TestEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(TestEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)

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
