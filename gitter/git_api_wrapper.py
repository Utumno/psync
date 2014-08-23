import datetime
import fnmatch
import os
from  git import Repo, InvalidGitRepositoryError, cmd, exc

class Git(object):
    class _Excluder(object):
        # TODO: be able to exclude files that were not initially excluded
        # TODO: filter duplicate paths/subpaths

        def __init__(self, ignored_files, repo, append=False):
            # path to the .git/info/exclude file
            self._exclude = exclude = os.path.join(repo.git_dir, "info",
                                                   "exclude")
            print "exclude", exclude
            mode = 'ab' if append else 'wb'  # 'w' will truncate - 'b' for
            # unix newlines
            with open(exclude, mode) as excl:
                for path in ignored_files:
                    excl.write(path + "\n")

        def getIgnoredPaths(self):
            excl_regex_patterns = []
            with open(self._exclude, 'r') as excl:
                # http://stackoverflow.com/a/22123823/281545
                excl_lines = excl.read().splitlines()
                for line in excl_lines:
                    excl_regex_patterns.append(fnmatch.translate(line))
            return excl_regex_patterns

    def __init__(self, dir_, ignored_files=None):
        if not os.path.isdir(dir_): raise RuntimeError(
            "%s is not a directory" % dir_)
        try:  # http://stackoverflow.com/a/23666860/281545
            self.repo = repo = Repo(dir_)
            self._g = cmd.Git(dir_)
            self._excluder = self._Excluder(ignored_files, repo, append=True)
            self.commitAll(
                msg=str(datetime.date.today) + '- batch committing changes')
        except InvalidGitRepositoryError:
            print 'isn`t git repo'
            self._g = _g = cmd.Git(dir_)
            _g.init()
            self.repo = repo = Repo(dir_)
            self._excluder = self._Excluder(ignored_files, repo)
            self.commitAll(msg="Initial commit")

    def commitAll(self, msg):
        try:
            self._g.add('-A')
            self._g.commit(m=msg)
        except exc.GitCommandError:
            # see: http://stackoverflow.com/a/21078070/281545
            pass

    def getIgnoredPaths(self):
        return self._excluder.getIgnoredPaths()

    def dir(self):
        return self.repo.git_dir
