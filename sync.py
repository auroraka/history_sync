#!/usr/bin/env python3
import shutil
import sys
import inspect
import history
import os
from history import *
from tools import *


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
    if not git_check_repo_exists(repo):
        msg = 'repo %s not found in directory: %s' % (repo, repo_dir)
        raise Exception(msg)

    if not git_check_branch_master():
        raise Exception('not on branch master')

    git_ensure_username_and_email()


def get_time_now_str():
    return datetime.now().strftime('%Y-%m-%d-%S')


def get_shells():
    shells = []
    for name in dir(history):
        cls = getattr(history, name)
        if 'history' in name.lower() and inspect.isclass(cls) and isinstance(cls(), History):
            shells.append(name.lower().split('history')[0])

    return [s for s in shells if s]


def self_update():
    Log('[ history_sync self update... ]')
    running_dir = os.getcwd()
    git_init(settings.THIS_REPO, settings.THIS_DIR)
    git_check(settings.THIS_REPO, settings.THIS_DIR)
    if git_check_repo_clean():
        try:
            sys_call('git fetch --all', showcmd=True)
            sys_call('git rebase origin/master', showcmd=True)
            sys_call('git push origin master', showcmd=True)
        except Exception as e:
            LogError('[Error while self update]')
            try:
                Log('cleanup git...')
                if git_check_repo_bare():
                    sys_call('git rm -r -f --cached .')
                sys_call('git clean -d -f')
                sys_call('git reset --hard master')
            except Exception as e1:
                pass
    else:
        raise Exception('[ self update failed, please commit your changes first ]')

    os.chdir(running_dir)


def sync():
    make_default_settings()
    self_update()

    shells = sys.argv[1:] if len(sys.argv) > 1 else get_shells()
    Log('shells: ', shells)

    git_init(settings.HISTORY_REPO, settings.HISTORY_DIR)
    git_check(settings.HISTORY_REPO, settings.HISTORY_DIR)
    if not git_check_repo_clean():
        raise Exception('git directory dirty')

    try:

        Log('==> [ pull history from origin ]')
        sys_call('git fetch origin')
        if not git_check_repo_bare():
            sys_call('git reset --hard origin/master')

        Log('==> [ merge histories ]')
        os.makedirs(full_path(settings.BACKUP_DIR), exist_ok=True)
        if not os.path.exists(settings.HISTORY_FILE_NAME):
            touch_file(settings.HISTORY_FILE_NAME)

        for shell in shells:
            Log('[ merge %s... ]' % shell)
            ShellHistory = globals()[shell.capitalize() + 'History']
            shell_his_dir = ShellHistory._get_history_dir()
            if not os.path.exists(shell_his_dir):
                Log('%s shell history does not exist' % shell)
                continue
            shutil.copy(shell_his_dir,
                        os.path.join(settings.BACKUP_DIR, shell + '_history.' + get_time_now_str()))
            History.merge_file(shell_his_dir, settings.HISTORY_FILE_NAME, settings.HISTORY_FILE_NAME, cls1=ShellHistory,
                               cls2=History)

        for shell in shells:
            Log('[ update history %s... ]' % shell)
            ShellHistory = globals()[shell.capitalize() + 'History']
            shell_his_dir = ShellHistory._get_history_dir()
            if not os.path.exists(shell_his_dir):
                Log('%s shell history does not exist' % shell)
                continue
            ShellHistory.convert_file(settings.HISTORY_FILE_NAME, shell_his_dir, cls1=History)
    except Exception as e:
        LogError('[Error while syncing]')
        try:
            Log('cleanup git...')
            if git_check_repo_bare():
                sys_call('git rm -r -f --cached .')
            sys_call('git clean -d -f')
            sys_call('git reset --hard master')
        except Exception as e1:
            pass
        raise e

    Log('==> [ push history to origin ]')
    # sys_call('git add %s' % settings.HISTORY_FILE_NAME)
    sys_call('git add --all')
    if not git_check_repo_clean():
        sys_call('git commit -m "%s save history: %s"' % (get_time_now_str(), shells))
        sys_call('git push origin master')


if __name__ == '__main__':
    sync()
