import logging
from watchdog.events import RegexMatchingEventHandler

class TestEventHandler(RegexMatchingEventHandler):
    """Logs all the events captured."""

    def __init__(self, ignore_regexes=(".*\.git.*",)):
        """

        :param ignore_patterns: a list/tuple of wildcard patterns - see
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
