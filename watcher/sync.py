#!/usr/bin/env python2
import logging
import shlex
import os, sys
from watchdog.observers import Observer
# internal imports
import server as sr
from server import uniqueid
from watcher.cli import Parser
from gitter import git_api_wrapper
from watcher.event_handler import TestEventHandler
from watcher.messages import DiscoveryMSG

VERSION = 0.1

class Sync(object):
    """Static class that keeps all the state of the running application.
    TODO: add persistent state (an ini ?)
    """
    # observers are threads - on exiting shut them down
    _observers = []
    # _Tree classes that keep info on directory trees being watched
    _watches = []

    class _Tree(object):
        def __init__(self, path, uuid):
            self.root = os.path.abspath(path)
            self.uuid = uuid

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        parser = Parser(description='Monitor and sync directory changes')
        server, client, http = None, None, None
        try:
            ### Discovery Server/Client ###
            try:
                server = sr.servers.DiscoveryServer()
                server.start()
            except: logging.exception("Failed to start Discovery server.")
            try:
                client = sr.clients.DiscoveryClient()
                client.start()
            except: logging.exception("Failed to start Discovery client.")
            try:
                http = sr.servers.HttpServer()
                http.start()
            except: logging.exception("Failed to start HttpServer server.")
            ### COMMAND LOOP ###
            while True:
                # http://stackoverflow.com/questions/230751
                sys.stdout.flush()
                sys.stderr.flush()
                # http://stackoverflow.com/a/17352877/281545
                cmd = shlex.split(raw_input('> ').strip())
                # logging.debug('command line: %s', cmd)
                try:
                    parser.parse(cmd)
                except SystemExit:  # DUH
                    # http://stackoverflow.com/q/16004901/281545
                    pass
        except KeyboardInterrupt:
            pass
        finally:
            for observer in self._observers:
                observer.stop()
            for observer in self._observers:
                observer.join()
            if server:
                server.shutdown()
                server.join()
            if http:
                http.shutdown()
                http.join()
            if client:
                client.shutdown()
                client.join()

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
        for watch in Sync._watches:
            if abspath.startswith(watch.root + os.path.sep):
                # TODO: check parent folders
                logging.warn(
                    "%s is a subpath of %s which you already watch" % (
                    path, watch.root))
                return
        # FIXME - time of check time of use - lock the dir for deletion ?
        git = git_api_wrapper.Git(path, ignored_files=ignored_files)
        git.init()
        # TODO if a git repo and NOT a sync repo quit
        repoid = uniqueid.readId(path)
        if not repoid:
            repoid = uniqueid.create(path)
        ignored = git.getIgnoredPaths()
        logging.debug(ignored)
        ignored.append(".*\.git.*")
        event_handler = TestEventHandler(ignore_regexes=ignored)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        Sync._observers.append(observer)
        Sync._watches.append(Sync._Tree(abspath, repoid))

    @staticmethod
    def broadcastMsg():
        return DiscoveryMSG(map(lambda x: x.uuid, Sync._watches)).serialize()

if __name__ == "__main__":
    Sync()
