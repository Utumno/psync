import datetime
import os

from  git import Repo, InvalidGitRepositoryError
from  git import cmd, exc

class Git(object):
    def __init__(self, path, ignored_files=None):
        print 'path', path
        dir_ = os.path.abspath(path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        elif not os.path.isdir(dir_):
            raise RuntimeError(dir_ + "is not a directory")
        try:  # http://stackoverflow.com/a/23666860/281545
            self.repo = Repo(dir_)
            self._g = cmd.Git(dir_)
            self.commitAll(
                msg=str(datetime.date.today) + '- batch committing changes')
        except InvalidGitRepositoryError:
            print 'isn`t git repo'
            self._g = _g = cmd.Git(dir_)
            _g.init()
            self.repo = repo = Repo(dir_)
            if ignored_files:
                exclude = os.path.join(repo.git_dir, "info", "exclude")
                print 'exclude', exclude
                with open(exclude, 'w') as excl:  # 'w' will truncate
                    for path in ignored_files:
                        excl.write(path + "\n")
            self.commitAll(msg="Initial commit")

    def commitAll(self, msg):
        try:
            self._g.add('-A')
            self._g.commit(m=msg)
        except exc.GitCommandError:
            # see: http://stackoverflow.com/a/21078070/281545
            pass

    def getIgnoredPaths(self, message):
        pass

    def dir(self):
        repo_git_dir = self.repo.git_dir
        return repo_git_dir
