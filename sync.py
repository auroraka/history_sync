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
    return 'No commits yet' in info


def git_check_repo_clean():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'nothing to commit' in info


def git_check_branch_master():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'On branch master' in info


def git_check_repo_exists():
    info = sys_call('git remote -v | grep origin', showcmd=False, printScreen=False)
    return info.split('\n')[0].split(' ')[0].split('\t')[1] == settings.HISTORY_REPO


def git_init():
    if not os.path.exists(full_path(settings.HISTORY_DIR)):
        sys_call('git clone %s %s' % (settings.HISTORY_REPO, full_path(settings.HISTORY_DIR)), showcmd=True)
    git_dir = full_path(settings.HISTORY_DIR)
    os.chdir(git_dir)


def git_check():
    if not git_check_repo_exists():
        msg = 'repo %s not found in directory: %s' % (settings.HISTORY_REPO, settings.HISTORY_DIR)
        raise Exception(msg)

    if not git_check_branch_master():
        raise Exception('not on branch master')

    if not git_check_repo_clean():
        raise Exception('git directory dirty')


def get_time_now_str():
    return datetime.now().strftime('%Y-%m-%d-%S')


def get_shells():
    shells = []
    for name in dir(history):
        cls = getattr(history, name)
        if 'history' in name.lower() and inspect.isclass(cls) and isinstance(cls(), History):
            shells.append(name.lower().split('history')[0])

    return [s for s in shells if s]


def sync():
    make_default_settings()

    shells = sys.argv[1:] if len(sys.argv) > 1 else get_shells()
    Log('shells: ', shells)

    git_init()
    try:
        git_check()

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
            ShellHistory = globals()[shell.capitalize() + 'History']
            shell_his_dir = ShellHistory._get_history_dir()
            ShellHistory.convert_file(settings.HISTORY_FILE_NAME, shell_his_dir, cls1=History)
    except Exception as e:
        LogError('[Error while syncing]')
        try:
            sys_call('git clean -d -f')
            sys_call('git reset --hard master')
        except Exception as e:
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
