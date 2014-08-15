__author__ = 'https://github.com/gorakhargosh/watchdog'
import sys
import time
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from gitter import git_api_wrapper

class TestEventHandler(PatternMatchingEventHandler):
    """Logs all the events captured."""

    def __init__(self, ignore_patterns=("*.git*",)):
        """

        :param ignore_patterns: a list/tuple of wirldcard patterns - see
        Python27\Lib\site-packages\pathtools\patterns.py.match_path
        """
        super(TestEventHandler, self).__init__(ignore_patterns=ignore_patterns)

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '../../sandbox'
    git = git_api_wrapper.Git(path, ignored_files=("lol/",))
    ignored = git.getIgnoredPaths()
    print ignored
    event_handler = TestEventHandler(ignore_patterns=("*.git*","*lol*",))
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
