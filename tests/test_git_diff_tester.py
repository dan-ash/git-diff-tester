import os
import logging
import git
from git_diff_tester import __version__
from git_diff_tester.trigger import GitDiffTester, EmptyIncludeListException, PatternDidNotMatchedFilesException, main
from pathlib import PosixPath
import unittest
from unittest.mock import patch
from click.testing import CliRunner


class TestGitDiffTester(unittest.TestCase):

    def custom_init(self, include_list, exclude_list, ignore_authors=[]):
        self.logger = logging.getLogger(__name__)
        self.include_list = include_list
        self.exclude_list = exclude_list
        self.ignore_authors = ignore_authors

    def custom_git_repo_init(self, path):
        pass

    def custom_git_repo_commit(self, rev):
        pass

    @patch.object(git.Repo, '__init__', custom_git_repo_init)
    @patch.object(git.Repo, 'commit', custom_git_repo_commit)
    def test_empty_include_list(self):
        include_list = []
        exclude_list = []
        with self.assertRaises(EmptyIncludeListException) as context:
            GitDiffTester("356cfcfbaf2329c2644dbb945a8c5bf11dc2a064", "356cfcfbaf2329c2644dbb945a8c5bf11dc2a064", include_list, exclude_list)


    @patch.object(git.Repo, '__init__', custom_git_repo_init)
    @patch.object(git.Repo, 'commit', custom_git_repo_commit)
    def test_no_real_path_in_include_list(self):
        include_list = ["not_real_path/**/*"]
        exclude_list = []
        with self.assertRaises(PatternDidNotMatchedFilesException) as context:
            GitDiffTester("356cfcfbaf2329c2644dbb945a8c5bf11dc2a064", "356cfcfbaf2329c2644dbb945a8c5bf11dc2a064", include_list, exclude_list)

    @patch.object(GitDiffTester, '__init__', custom_init)
    def test_get_absolute_file_list(self):
        expected_single_file = [
            PosixPath(f'{os.getcwd()}/pyproject.toml'),
                ]
        single_file = GitDiffTester._get_absolute_file_list_from_pattern("pyproject.toml")
        self.assertListEqual(expected_single_file, single_file, "Expected single file not equal")
        expected_glob_pattern_files = [
            PosixPath(f'{os.getcwd()}/tests/__init__.py'),
            PosixPath(f'{os.getcwd()}/tests/{os.path.basename(__file__)}'),
                ]
        glob_relative_files = GitDiffTester._get_absolute_file_list_from_pattern("tests/**/*.py")
        glob_absolute_files = GitDiffTester._get_absolute_file_list_from_pattern(f"{os.getcwd()}/tests/**/*.py")
        self.assertListEqual(expected_glob_pattern_files, glob_relative_files, "Expected glob for relative files not equal")
        self.assertListEqual(expected_glob_pattern_files, glob_absolute_files, "Expected glob for absolute files not equal")


    @patch.object(GitDiffTester, '__init__', custom_init)
    def test_diff_belong_to_application(self):
        diffs = [
            "app/file1.txt",
            "app/file2.txt"
        ]
        exclude_list = ["app/file3.txt"]
        include_list = ["app/file1.txt"]
        commit_author = "user"
        gdt = GitDiffTester(include_list,exclude_list)
        assert gdt.diff_belong_to_application(diffs,commit_author) == True

        commit_author = "Author"
        gdt.include_list = ["app/file4.txt"]
        assert gdt.diff_belong_to_application(diffs,commit_author) == False
    
    @patch.object(GitDiffTester, '__init__', custom_init)
    def test_ignore_author(self):
        diffs = [
            "app/file1.txt",
            "app/file2.txt"
        ]
        exclude_list = ["app/file3.txt"]
        include_list = ["app/file1.txt"]
        commit_author = "user"
        gdt = GitDiffTester(include_list,exclude_list, ignore_authors=[commit_author])
        assert gdt.diff_belong_to_application(diffs,commit_author) == False
