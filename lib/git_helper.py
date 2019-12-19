import os

from lib.tools import sys_call, full_path, LogWarning


def git_check_repo_bare():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'No commits yet' in info or 'Initial commit' in info


def git_check_repo_clean():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'nothing to commit' in info


def git_check_branch_master():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'On branch master' in info


def git_check_repo_exists(repo):
    info = sys_call('git remote -v | grep origin', showcmd=False, printScreen=False)
    return info.split('\n')[0].split(' ')[0].split('\t')[1] == repo


def git_ensure_username_and_email():
    err = None
    info = None
    try:
        info = sys_call('git config --get user.email', showcmd=False, printScreen=False)
    except Exception as e:
        err = e
    if err or not info:
        raise Exception('Please init your git user.email by: git config --global user.email "you@example.com"')
    try:
        info = sys_call('git config --get user.name', showcmd=False, printScreen=False)
    except Exception as e:
        err = e
    if err or not info:
        raise Exception('Please init your git user.name by: git config --global user.name "Your Name"')


def git_init(repo, repo_dir):
    git_dir = full_path(repo_dir)
    if not os.path.exists(git_dir):
        sys_call('git clone %s %s' % (repo, git_dir), showcmd=True)
    os.chdir(git_dir)


def git_check(repo, repo_dir):
    git_ensure_username_and_email()

    if not git_check_repo_exists(repo):
        msg = 'repo %s not found in directory: %s' % (repo, repo_dir)
        raise Exception(msg)

    if not git_check_repo_clean():
        raise Exception('[ self update failed, please commit your changes first ]')

    if not git_check_branch_master():
        LogWarning('not on branch master, will checkout to master first...')
        sys_call('git checkout master', showcmd=True)
