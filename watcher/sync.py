#!/usr/bin/env python2
import datetime
import shlex
import os, sys
import threading, time
from os.path import expanduser
# watchdog
from watchdog.observers import Observer
# internal imports
from gitter.git_api_wrapper import RemoteUnreachableException, \
    RemoteExistsException, RemoteNotFoundException, GitWrapperException
from log import Log
import server as sr
from server import uniqueid
from watcher.cli import Parser
from gitter import git_api_wrapper
from watcher.event_handler import TestEventHandler
from watcher.messages import DiscoveryMSG, RequestMSG, AcceptRequestMSG, \
    CloneSucceededMSG, PullMSG

VERSION = 0.1

class Sync(Log):
    """Static class that keeps all the state of the running application.
    TODO: add persistent state (an ini ?)
    """
    # observers are threads - on exiting shut them down
    _observers = []
    # _Tree classes that keep info on directory trees being watched
    _watches = {}
    # Peers
    SECONDS_BEFORE_REMOVAL = 30
    _peers = {}
    # requests made to the server (us)
    _requests_pending = {}
    _requests_accepted = {}
    # request made to the remote server
    _requests_made = {}
    # Locks
    _lock_observers = threading.RLock()
    _lock_watches = threading.RLock() # use this for observers too
    _lock_peers = threading.RLock()
    _lock_requests_pending = threading.RLock()
    _lock_requests_made = threading.RLock()
    _lock_requests_accepted = threading.RLock()
    sync_client = None
    # http://stackoverflow.com/a/4028943/281545
    home = expanduser("~")
    app_path = os.path.abspath(os.path.join(home,'.sync'))
    if not os.path.exists(app_path):
        Log.ci("Creating directory %s" % app_path)
        os.makedirs(app_path)
    elif not os.path.isdir(app_path):
        Log.cw("%s is not a directory" % app_path)

    def __init__(self):
        super(Sync, self).__init__()
        self.__class__.sync_client = sr.clients.SyncClient()

    def main(self):
        server, client, http, pullservice = None, None, None, None
        try:
            ### Servers/Clients ###
            try:
                self.__class__.sync_client.start()
            except:
                self.e("Failed to start Sync client.")
            try:
                server = sr.servers.DiscoveryServer()
                server.start()
            except:
                self.e("Failed to start Discovery server.")
            try:
                client = sr.clients.DiscoveryClient()
                client.start()
            except:
                self.e("Failed to start Discovery client.")
            try:
                http = sr.servers.HttpServer()
                http.start()
            except:
                self.e("Failed to start HttpServer server.")
            ### COMMAND LOOP ###
            parser = Parser(description='Monitor and sync directory changes')
            while True:
                # http://stackoverflow.com/questions/230751
                sys.stdout.flush()
                sys.stderr.flush()
                # http://stackoverflow.com/a/17352877/281545
                try:
                    cmd = shlex.split(raw_input('> ').strip())
                except ValueError:
                    self.e('malformed command')
                    cmd = None
                if not cmd: continue
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
            if self.__class__.sync_client:
                self.__class__.sync_client.shutdown()
                self.__class__.sync_client.join()

    @classmethod
    def _addObserver(cls, abspath, git, repoid):
        # Observer setup
        ignored = git.getIgnoredPaths() # cls.cd(ignored)
        ignored.append(".*\.git.*")
        event_handler = TestEventHandler(git, ignore_regexes=ignored)
        observer = Observer()
        observer.schedule(event_handler, abspath, recursive=True)
        observer.start()
        Sync._observers.append(observer)
        Sync._watches[repoid] = (abspath, git, [])

    @classmethod
    def addObserver(cls, path='../../sandbox', ignored_files=("lol/*",), git=None):
        abspath = os.path.abspath(path)
        cls.cd("User given path: %s -> %s" % (path, abspath))
        if not os.path.exists(abspath):
            cls.ci("Creating directory %s" % abspath)
            os.makedirs(abspath)
        elif not os.path.isdir(abspath):
            cls.cw("%s is not a directory" % abspath)
            return
        # FIXME: LOCKING !!!!!
        for id_, tuple_ in Sync._watches.iteritems():
            if abspath.startswith(tuple_[0] + os.path.sep):
                # TODO: check parent folders
                cls.cw("%s is a subpath of %s which you already watch" % (
                    path, tuple_[0]))
                return
        # FIXME - time of check time of use - lock the dir for deletion ?
        if not git:
            git = git_api_wrapper.Git(abspath, ignored_files=ignored_files)
        was_git = git.init()
        repoid = uniqueid.Uuid.readId(abspath)
        if was_git:
            # TODO allow git repos - VERY difficult
            if not repoid:
                # FIXME : go to the root of repository to check if .sync exists
                # use rev-parse --show-toplevel
                cls.cw("%s is already a git repo but not a sync one" % abspath)
                return
            git.commitAll(msg=Sync._now() + ':batch committing changes')
        else:
            # TODO: name the dir .sync instead of .git
            cls.ci('Creating git repo at %s', abspath)
            repoid = uniqueid.Uuid.create(abspath)
            git.commitAll(msg="Initializing:"+ repoid, allow_empty=True)
        cls._addObserver(abspath, git, repoid)

    @staticmethod
    def _now():
        return datetime.datetime.now().isoformat()

    @staticmethod
    def broadcastMsg():
        with Sync._lock_peers:
            for p, p_info in Sync._peers.items():
                if  int(time.time()) - p_info[1] > Sync.SECONDS_BEFORE_REMOVAL:
                    Sync.removePeer(p)
        with Sync._lock_watches:
            return DiscoveryMSG(Sync._watches.keys())

    @staticmethod
    def newPeer(_from, uuids):
        _from = _from[0]
        with Sync._lock_peers:
            try:
                old_uuids = Sync._peers[_from][0]
            except KeyError:
                old_uuids = None
            Sync._peers[_from] = (uuids, int(time.time()))
            if old_uuids is None:
                msg = "New peer %s."
            elif old_uuids != uuids:
                msg = "Peer %s updated its repos."
            else: return
            if uuids:
                msg += " Repos:\n" + '\n'.join(map(str, uuids))
            else:
                msg += " No repos."
            Log.ci(msg % (_from,))

    @classmethod
    def newRequest(cls, host, repo):
        """Used by client and server - FIXME"""
        if repo in Sync._watches.keys():
            with Sync._lock_requests_accepted, Sync._lock_watches, \
                 Sync._lock_requests_pending:
                try:
                    old_reqs = Sync._requests_pending[host]
                    if not repo in old_reqs:
                        cls.cw(
                            "No pending request from %s for %s" % (host, repo))
                        return
                    Sync._requests_pending[host] = old_reqs - {repo}
                except KeyError:
                    cls.cw("No pending requests from %s" % host)
                    return
                old_reqs = Sync._requests_accepted.get(host, set())
                Sync._requests_accepted[host] = old_reqs | {repo}
            cls.sync_client.add(
                (AcceptRequestMSG(repo, Sync._watches[repo]), host))
            #enter the info of the other in the .conf file
            # and then delete/update for the next time
            cls.ci("Accepted request from %s for %s" % (host, repo))
            return
        # else: # FIXME - the repo is not watched by us - used here to
        # differentiate client/server - wrong
        #     cls.ci("Can not accept request from %s for %s - repo not watched"
        #  % (host, repo))
        #     return
        with Sync._lock_requests_made:
            old_reqs = Sync._requests_made.get(host, set())
            Sync._requests_made[host] = old_reqs | {repo}
        cls.sync_client.add((RequestMSG(repo),host))
        cls.cd("New request sent to %s for %s" % (host, repo))

    @classmethod
    def newRequestServer(cls, _from, repo):
        with Sync._lock_requests_pending:
            old_reqs = Sync._requests_pending.get(_from[0], set())
            Sync._requests_pending[_from[0]] = old_reqs | {repo}
        cls.ci("New request from %s for %s" % (_from[0], repo))

    @classmethod
    def acceptedRequest(cls, _from, repo, path):
        with Sync._lock_requests_made:
            try:
                old_reqs = Sync._requests_made[_from[0]]
                if not repo in old_reqs:
                    cls.cw(
                        "No pending request to %s for %s" % (_from[0], repo))
                    return
                Sync._requests_made[_from[0]] = old_reqs - {repo}
            except KeyError:
                cls.cw("No request made to %s for %s" % (_from[0], repo))
                return
        cls.ci(
            "Request to %s for %s accepted - path: %s" % (_from, repo, path))
        clone_path = os.path.join(Sync.app_path, repo)
        if not os.path.exists(clone_path):
            Log.ci("Creating directory %s" % clone_path)
            os.makedirs(clone_path)
        if not os.path.isdir(clone_path):
            Log.cw("%s is not a directory" % clone_path)
            return
        git = git_api_wrapper.Git(clone_path)
        repoid = uniqueid.Uuid.readId(clone_path)
        # print repoid
        if repoid == repo:
            Log.ci("Repository %s is already cloned. Adding remote." % repo)
            try:
                git.addRemote(_from[0], path)
            except RemoteExistsException:
                cls.cw("Trying to re-add a remote")
        elif repoid:
            Log.cw("Trying to clone %s into %s " % (repo, repoid))
            return
        else:
            git.clone(Sync.app_path, _from[0], path, repo)
        # just add the observer (and add to _watches) - clone is _asynchronous_
        # time.sleep(5) # FIXME: is clone really synchronous ?
        cls._addObserver(clone_path, git, repo)
        with Sync._lock_watches:
            pull_clients = Sync._watches[repo][2]
            pull_clients.append(_from[0])
            print Sync._watches
        cls.sync_client.add((CloneSucceededMSG(repo,clone_path),_from[0]))

    @classmethod
    def pullAll(cls):
        with Sync._lock_watches: # FIXME read write locks !
            for repo, watch in cls._watches.items():
                for client in watch[2]:
                    print "PM to", client, 'for', repo
                    cls.sync_client.add((PullMSG(repo), client))
                # How are pulls from multiple machines handled? Need to send
                # msg to temporarily stop the service(BroadCast or Send)

    @classmethod
    def cloneSucceeded(cls, _from, repo, clone_path):
        with cls._lock_watches:
            try:
                git = cls._watches[repo][1]
            except KeyError:
                cls.cw("%s cloned repo %s which is not watched." % ( _from[0],
                    repo))
                return
            try:
                git.addRemote(_from[0], clone_path)
            except RemoteExistsException:
                cls.cw("Trying to re-add a remote") # FIXME: stale remote ?
            pull_clients = cls._watches[repo][2]
            pull_clients.append(_from[0])
            print cls._watches

    @classmethod
    def initiatePull(cls, _from, repo):
        host = _from[0]
        with cls._lock_watches:
            watch = cls._watches.get(repo, None)
            if not watch:
                cls.cw('Received pull message from %s for %s which we do not '
                       'watch.' % (host, repo))
                return
            pull_clients = watch[2]
            if not host in pull_clients:
                cls.cw('Received pull message for %s from %s which we do not '
                       'have in our pull clients.' % (repo, host))
                return
            git = watch[1]
            try:
                info_list = git.fetch(host)
                if not info_list:
                    print 'No fetch'
                    return
            except RemoteUnreachableException:
                cls.cw("Remote %s unreachable - removing." % host)
                cls.removePeer(host)
                return
            except RemoteNotFoundException:
                cls.cw("Repo %s not found on peer %s - removing remote." % (
                    repo, host))
                for client in watch[2]:
                    if client == host:
                        watch[2].remove(host)
                        watch[1].removeRemote(host)
                return
            try:
                info = info_list[0]
                git.merge(info)
            except GitWrapperException:
                cls.ce('Automatic merge failed - please merge manually.')

    @classmethod
    def removePeer(cls, p):
        cls.ci("Peer %s appears dead - removing." % (p,))
        with cls._lock_peers, cls._lock_watches:
            del cls._peers[p]
            for repo, watch in cls._watches.items():
                for client in watch[2]:
                    if client == p:
                        watch[2].remove(p)
                        watch[1].removeRemote(p)

if __name__ == "__main__":
    from watcher.sync import Sync
    Sync().main()
