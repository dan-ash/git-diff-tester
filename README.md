# Git Diff Tester

## Overview
This tool can be used to test for diffs between commits and return boolean (exit code 0 or 1) based on set of rules to test

## Use case
When working in mono repos it is helpful to have a way of check for changes that are related to specific components
and the ability to ignore changes in specific paths.
during a CI pipeline this tool can be used for a step prior for running the full pipeline

## Usage

```
poetry run python git_diff_tester/trigger.py --help
Usage: trigger.py [OPTIONS]

Options:
  -t, --target-commit-hash TEXT  Target commit hash to compare  [required]
  -c, --change-commit-hash TEXT  The commit with new changes  [required]
  -i, --include-list TEXT        Include list files (pathes should be
                                 relative, globbinb expressions are
                                 supported).  [required]
  -e, --exclude-list TEXT        Exclude list files (pathes should be
                                 relative, globbinb expressions are
                                 supported).
  -l, --git-local-dir TEXT       Git repository local directory full path to
                                 be referenced, default value is current
                                 directory.
  -a, --ignore-authors TEXT      Ignore commits from the following author
  --help                         Show this message and exit.
```

