import fnmatch
import logging
import os
from  git import Repo, InvalidGitRepositoryError, cmd, exc
from log import Log

class Git(object):
    class _Excluder(object):
        # TODO: be able to exclude files that were not initially excluded
        # TODO: filter duplicate paths/subpaths

        def __init__(self, ignored_files, repo, append=False):
            # path to the .git/info/exclude file
            self._exclude = exclude = os.path.join(repo.git_dir, "info",
                                                   "exclude")
            logging.debug("Exclude file: %s", exclude)
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
        self._g.update_server_info()

    def init(self):
        dir_ = self._dir
        ignored_files = self.ignored_files
        try:  # http://stackoverflow.com/a/23666860/281545
            self.repo = repo = Repo(dir_)
            self._g = cmd.Git(dir_)
            self._excluder = self._Excluder(ignored_files, repo, append=True)
            return True
        except InvalidGitRepositoryError:
            self._g = _g = cmd.Git(dir_)
            _g.init()
            self.repo = repo = Repo(dir_)
            self._excluder = self._Excluder(ignored_files, repo)
        return False

    def __init__(self, dir_, ignored_files=None):
        if not os.path.isdir(dir_): raise RuntimeError(
            "%s is not a directory" % dir_)
        self._dir = dir_
        self.ignored_files = ignored_files

    def commitAll(self, msg, allow_empty=False):
        if self._commitAll(msg, allow_empty):
            self._updateServerInfo()

    def _commitAll(self, msg, allow_empty=False):
        dirty = self.repo.is_dirty(untracked_files=True) # GitPython > 0.3.2rc1
        if dirty or allow_empty:
            try:
                if dirty: self._g.add('-A')
            except exc.GitCommandError:
                # see: http://stackoverflow.com/a/21078070/281545
                logging.exception("add('-A') failed")
                if allow_empty :
                    self._g.commit("--allow-empty",m=msg)
                    return True
                return False
            if allow_empty :
                self._g.commit("--allow-empty",m=msg)
                return True
            self._g.commit(m=msg)
            return True
        return False

    def clone(self, clone_path, host, path, repo):
        if not os.path.exists(clone_path):
            Log.ci("Creating directory %s" % clone_path)
            os.makedirs(clone_path)
        elif not os.path.isdir(clone_path):
            Log.cw("%s is not a directory" % clone_path)
        self._g = _g = cmd.Git(clone_path)
        # path = str(path).split(os.path.abspath(os.sep))[0] # not needed
        path = os.path.normcase(os.path.normpath(path))
        path = path.replace('\\', '/')
        _g.clone("-o" + host,
            "http://" + host + ':8002' + '/' + path + '/' + '.git',
            os.path.join(clone_path, repo))

    def addRemote(self, remote_ip, clone_path):
        clone_path = os.path.normcase(os.path.normpath(clone_path))
        clone_path = clone_path.replace('\\', '/')
        self._g.remote("add", remote_ip,
                       "http://" + remote_ip + ':8002' + '/' + clone_path +
                       '/.git')

    def pull(self, host):
        self._g.pull(host)

    def getIgnoredPaths(self):
        return self._excluder.getIgnoredPaths()

    def dir(self):
        return self.repo.git_dir
