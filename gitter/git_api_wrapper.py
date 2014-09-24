import datetime
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

    @staticmethod
    def _now():
        return datetime.datetime.now().isoformat()

    def init(self):
        dir_ = self._dir
        ignored_files = self.ignored_files
        try:  # http://stackoverflow.com/a/23666860/281545
            self.repo = repo = Repo(dir_)
            self._g = cmd.Git(dir_)
            self._excluder = self._Excluder(ignored_files, repo, append=True)
            return self.commitAll(
                msg=self._now() + '- batch committing changes')
        except InvalidGitRepositoryError:
            # TODO: name the dir .sync instead of .git
            logging.info('Creating git repo at %s', dir_)
            self._g = _g = cmd.Git(dir_)
            _g.init()
            self.repo = repo = Repo(dir_)
            self._excluder = self._Excluder(ignored_files, repo)
            return self.commitAll(msg="Initial commit", allow_empty=True)

    def __init__(self, dir_, ignored_files=None):
        if not os.path.isdir(dir_): raise RuntimeError(
            "%s is not a directory" % dir_)
        self._dir = dir_
        self.ignored_files = ignored_files

    def commitAll(self, msg, allow_empty=False):
        dirty = self.repo.is_dirty(untracked_files=True)
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
        _g.clone(
            "http://" + host + ':8002' + '/' + path + os.path.sep + '.git',
            os.path.join(clone_path, repo))

    def getIgnoredPaths(self):
        return self._excluder.getIgnoredPaths()

    def dir(self):
        return self.repo.git_dir
