#!/usr/bin/env python2
import logging
import shlex
import os, sys
import threading
from watchdog.observers import Observer
# internal imports
from log import Log
import server as sr
from server import uniqueid
from watcher.cli import Parser
from gitter import git_api_wrapper
from watcher.event_handler import TestEventHandler
from watcher.messages import DiscoveryMSG

VERSION = 0.1

class Sync(Log):
    """Static class that keeps all the state of the running application.
    TODO: add persistent state (an ini ?)
    """
    # observers are threads - on exiting shut them down
    _observers = []
    # _Tree classes that keep info on directory trees being watched
    _watches = []
    _peers = {}
    _lock_observers = threading.RLock()
    _lock_watches = threading.RLock() # use this for observers too
    _lock_peers = threading.RLock()

    class _Tree(object):
        def __init__(self, path, uuid):
            self.root = os.path.abspath(path)
            self.uuid = uuid

    def __init__(self):
        super(Sync, self).__init__()
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
                # self.d('command line: %s', cmd)
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

    @classmethod
    def addObserver(cls,path='../../sandbox', ignored_files=("lol/*",)):
        abspath = os.path.abspath(path)
        cls.cd("User given path: %s -> %s" % (path, abspath))
        if not os.path.exists(abspath):
            cls.ci("Creating directory %s" % abspath)
            os.makedirs(abspath)
        elif not os.path.isdir(abspath):
            cls.cw("%s is not a directory" % abspath)
            return
        # FIXME: LOCKING !!!!!
        for watch in Sync._watches:
            if abspath.startswith(watch.root + os.path.sep):
                # TODO: check parent folders
                cls.cw("%s is a subpath of %s which you already watch" % (
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
        cls.cd(ignored)
        ignored.append(".*\.git.*")
        event_handler = TestEventHandler(git, ignore_regexes=ignored)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        Sync._observers.append(observer)
        Sync._watches.append(Sync._Tree(abspath, repoid))

    @staticmethod
    def broadcastMsg():
        with Sync._lock_watches:
            return DiscoveryMSG(
                map(lambda x: x.uuid, Sync._watches)).serialize()

    @staticmethod
    def newPeer(_from,uuids):
        with Sync._lock_peers:
                Sync._peers[_from] = uuids

if __name__ == "__main__":
    Sync()
