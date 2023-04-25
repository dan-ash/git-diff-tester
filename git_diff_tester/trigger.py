#!/usr/local/bin/python3

import git
import os
import sys
import click
import logging.config
from pprint import pformat
from glob import glob
from pathlib import Path

logging.basicConfig(format='[%(asctime)s] - %(levelname)-6s %(name)s %(funcName)s() L%(lineno)-4d %(message)s', level=logging.INFO)

class EmptyIncludeListException(Exception): 
    pass

class PatternDidNotMatchedFilesException(Exception): 
    pass

class GitDiffTester:

    def __init__(self, target_commit, change_commit, include_list, exclude_list, ignore_authors=[], git_local_dir=os.getcwd()):
        self.logger = logging.getLogger(__name__)
        self.git_repo_obj = git.Repo(git_local_dir)
        self.target_commit = self.git_repo_obj.commit(target_commit)
        self.change_commit = self.git_repo_obj.commit(change_commit)
        self.ignore_authors = ignore_authors
        self.git_root_path = Path(git_local_dir)
        if len(include_list) == 0:
            raise EmptyIncludeListException("include_list can't be empty, at least 1 pattern or file should be pass")
        self.include_list = self.files_glob(include_list)
        self.exclude_list = self.files_glob(exclude_list)
        self.logger.info("Running %s with args:\n%s", pformat(self.__class__.__name__), pformat(self.__dict__))

    def diff_belong_to_application(self, diff_as_path, commit_author):
        for diff in diff_as_path:
            if diff in self.include_list and diff not in self.exclude_list and commit_author not in self.ignore_authors:
                self.logger.info(f"Git diff {diff} found in include list and not specified in the exclude list")
                return True
        return False

    def files_glob(self,file_patterns):
        files_to_return=[]
        if file_patterns:
            for pattern in file_patterns:
                file_list = self._get_absolute_file_list_from_pattern(pattern)
                if len(file_list) == 0:
                    raise PatternDidNotMatchedFilesException(f"Pattern '{pattern}' did not matched any file please check the pattern path")
                files_to_return.extend(file_list)
            return files_to_return
        return []

    def get_commits_diff_list(self,commit_a,commit_b):
        diffs=commit_a.diff(commit_b)
        diffs_list_as_path=[Path(f"{self.git_root_path}/{d.a_path}") for d in diffs]
        return diffs_list_as_path

    def check(self):
        '''
        Check if a git diff should return true based on conditions
        :return: True if should be triggered, otherwise returns False.
        '''
        git_diffs_as_path=self.get_commits_diff_list(self.change_commit,self.target_commit)
        self.logger.info(f"Git diff change_commit [{self.change_commit}] to target_commit [{self.target_commit}] : \n {pformat(git_diffs_as_path)}")
        commit_author=self.change_commit.author.email
        self.logger.info(f"===> commit_author {commit_author}")
        trigger_result=self.diff_belong_to_application(git_diffs_as_path, commit_author)
        self.logger.info(f"*** Trigger decision received [{trigger_result}] ***")
        return trigger_result

    @staticmethod
    def _get_absolute_file_list_from_pattern(pattern):
        return [ Path(f).absolute() for f in glob(pattern, recursive=True) ]



@click.command()
@click.option("-t","--target-commit-hash",required=True, help="Target commit hash to compare")
@click.option("-c","--change-commit-hash", required=True, default=None, help="The commit with new changes")
@click.option("-i","--include-list", required=True, multiple=True, default=None,
              help="Include list files (pathes should be relative, globbinb expressions are supported).")
@click.option("-e","--exclude-list", multiple=True, default=None,
              help="Exclude list files (pathes should be relative, globbinb expressions are supported).")
@click.option("-l","--git-local-dir", default=os.getcwd(),
              help="Git repository local directory full path to be referenced, default value is current directory.")
@click.option("-a","--ignore-authors", multiple=True, default=None,
              help="Ignore commits from the following author")
def main(target_commit_hash, change_commit_hash, include_list, exclude_list, ignore_authors, git_local_dir=os.getcwd()):
    assert target_commit_hash, "target commit hash could not be empty"
    assert change_commit_hash, "change commit hash could not be empty"
    assert include_list, "include list could not be empty"

    gdt=GitDiffTester(
        target_commit=target_commit_hash,
        change_commit=change_commit_hash,
        include_list=include_list,
        exclude_list=exclude_list,
        ignore_authors=ignore_authors,
        git_local_dir=git_local_dir,
    )
    res = gdt.check()
    sys.exit(0 if res else 1)


if __name__ == "__main__":
    main()

