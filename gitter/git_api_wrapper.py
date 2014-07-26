import datetime

__author__ = 'MrD'

from  git import Repo, InvalidGitRepositoryError
from  git import cmd, exc
import os

class Git(object):

    def __init__(self, path, ignored_files=None):
        print path
        dir_ = os.path.abspath(path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        elif not os.path.isdir(dir_):
            raise RuntimeError(dir_ + "is not a directory")
        try:  # http://stackoverflow.com/a/23666860/281545
            self.repo = Repo(dir_)
            self._g = _g = cmd.Git(dir_)
            try:
                _g.add('-A')
                _g.commit(str(datetime.date.today))
            except exc.GitCommandError:
                # see: http://stackoverflow.com/a/21078070/281545
                pass
        except InvalidGitRepositoryError:
            print 'isn`t git repo'
            self._g = _g = cmd.Git(dir_)
            _g.init()
            self.repo = repo = Repo()
            if ignored_files:
                with open(os.path.join(repo.git_dir,"/info/exclude"),
                          'w') as exclude:
                    exclude.truncate()
                    for path in ignored_files:
                        exclude.write(str(path) + '\n')
            try:
                _g.add('-A')
                _g.commit(m="Initial commit")
            except exc.GitCommandError:
                pass

    def commit(self, message):
        pass

    def getIgnoredPaths(self, message):
        from  git import cmd
    def dir(self):
        repo_git_dir = self.repo.git_dir
        return repo_git_dir
