import tempfile
from unittest import TestCase
import shutil
from gitter.git_api_wrapper import Git


class TestGit(TestCase):
    TMP = tempfile.gettempdir()

    def test_init(self):
        tmp_dir = tempfile.mkdtemp(dir=TestGit.TMP)
        Git(tmp_dir)
        shutil.rmtree(tmp_dir)

    # def test_commitAll(self):
    # self.fail()

    # def test_getIgnoredPaths(self):
    #     self.fail()

    # def test_dir(self):
    #     self.fail()
