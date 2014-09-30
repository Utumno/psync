import fnmatch
import logging
import os
import threading
from  git import Repo, InvalidGitRepositoryError, cmd, exc, GitCommandError
from log import Log

class Git(object):
    class _Excluder(object):
        # TODO: be able to exclude files that were not initially excluded
        # TODO: filter duplicate paths/subpaths

        def __init__(self, ignored_files=None, repo=None, append=False):
            # path to the .git/info/exclude file
            self._exclude = exclude = os.path.join(repo.git_dir, "info",
                                                   "exclude")
            Log.cd("Exclude file: %s", exclude)
            if not ignored_files: return
            mode = 'ab' if append else 'wb'  # 'w' will truncate - 'b' for
            # unix newlines
            with open(exclude, mode) as excl:
                for path in ignored_files:
                    # TODO check that paths are subpaths and valid
                    excl.write(path + "\n")

        def getIgnoredPaths(self):
            excl_regex_patterns = []
            with open(self._exclude, 'r') as excl:
                # http://stackoverflow.com/a/22123823/281545
                excl_lines = excl.read().splitlines()
                for line in excl_lines:
                    excl_regex_patterns.append(fnmatch.translate(line))
            return excl_regex_patterns

    def _updateServerInfo(self):
        self.cmd.update_server_info()

    def init(self):
        ignored_files = self.ignored_files
        try:  # http://stackoverflow.com/a/23666860/281545
            self._excluder = Git._Excluder(ignored_files, self.repo,
                                           append=True)
            return True
        except InvalidGitRepositoryError:
            self.cmd.init()
            self._excluder = Git._Excluder(ignored_files, self.repo)
        return False

    def get_excluder(self):
        if not hasattr(self, '_excluder'):
            self._excluder = self._Excluder(repo=self.repo)
        return self._excluder

    def get_repo(self):
        if not hasattr(self, '_repo'):
            self._repo = Repo(self._dir)
        return self._repo

    def get_cmd(self):
        if not hasattr(self, '_g'):
            self._g = cmd.Git(self._dir)
        return self._g

    excluder = property(get_excluder)
    repo = property(get_repo)
    cmd = property(get_cmd)

    def __init__(self, dir_, ignored_files=None):
        if not os.path.isdir(dir_): raise RuntimeError(
            "%s is not a directory" % dir_)
        self._dir = dir_
        self.ignored_files = ignored_files
        self._merge_lock = threading.RLock()

    def commitAll(self, msg, allow_empty=False):
        with self._merge_lock:
            if self._commitAll(msg, allow_empty):
                self._updateServerInfo()

    def _commitAll(self, msg, allow_empty=False):
        dirty = self.repo.is_dirty(untracked_files=True) # GitPython > 0.3.2rc1
        if dirty or allow_empty:
            try:
                if dirty: self.cmd.add('-A')
            except exc.GitCommandError:
                # see: http://stackoverflow.com/a/21078070/281545
                logging.exception("add('-A') failed")
                if allow_empty :
                    self.cmd.commit("--allow-empty",m=msg)
                    return True
                return False
            if allow_empty :
                self.cmd.commit("--allow-empty",m=msg)
                return True
            self.cmd.commit(m=msg)
            return True
        return False

    @staticmethod
    def _normalizePath(path):
        # path = str(path).split(os.path.abspath(os.sep))[0] # not needed
        path = os.path.normpath(path)
        path = path.replace('\\', '/')
        return path

    def clone(self, clone_path, host, path, repo):
        path = self._normalizePath(path)
        self.cmd.clone("-o" + host,
            "http://" + host + ':8002' + '/' + path + '/' + '.git',
            os.path.join(clone_path, repo))
        self._updateServerInfo()

    def addRemote(self, remote_ip, clone_path):
        clone_path = self._normalizePath(clone_path)
        try:
            self.cmd.remote("add", remote_ip,
                           "http://" + remote_ip + ':8002' + '/' + clone_path
                           + '/.git' # FIXME: needed ?
            )
        except GitCommandError as e:
            if 'already exists' in str(e):
                raise RemoteExistsException(cause=e)
            raise GitWrapperException(cause=e)

    def removeRemote(self, remote):
        try:
            self.repo.delete_remote(remote)
        except GitCommandError as e:
            # FIXME
            if 'already exists' in str(e):
                raise RemoteExistsException(cause=e)
            raise GitWrapperException(cause=e)

    def fetch(self, host):
        try:
            self.cmd.fetch(host, 'master',
                          # '--dry-run'
            )
        except GitCommandError as e:
            if 'fatal: unable to access' in str(e):
                raise RemoteUnreachableException(cause=e)
            if 'not found' in str(e):
                raise RemoteNotFoundException(cause=e)
            raise GitWrapperException(cause=e)

    def merge(self, host):
        with self._merge_lock:
            try:
                self.cmd.merge(host + '/master')
            except GitCommandError as e:
                raise GitWrapperException(cause=e)

    def getIgnoredPaths(self):
        return self.excluder.getIgnoredPaths()

    def dir(self):
        return self.repo.git_dir

class GitWrapperException(Exception):
    def __init__(self, message='Exception in git operation', cause=None):
        # http://stackoverflow.com/a/16414892/281545
        super(GitWrapperException, self).__init__(
            message + u', caused by ' + str(cause))
        self.cause = cause

class RemoteUnreachableException(GitWrapperException):
    def __init__(self, message='Unable to reach remote', cause=None):
        super(RemoteUnreachableException, self).__init__(
            message + u', error:' + str(cause))
        self.cause = cause

class RemoteNotFoundException(GitWrapperException):
    def __init__(self, message='Remote not found', cause=None):
        super(RemoteNotFoundException, self).__init__(
            message + u', error:' + str(cause))
        self.cause = cause

class RemoteExistsException(GitWrapperException):
    def __init__(self, message='Remote exists', cause=None):
        super(RemoteExistsException, self).__init__(
            message + u', error:' + str(cause))
        self.cause = cause
