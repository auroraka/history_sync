#!/usr/bin/env python3
import shutil
import sys
import inspect
import os
from datetime import datetime

from lib.tools import Log, LogError, sys_call, full_path, touch_file
import conf.settings as settings
import lib.history as history
import lib.git_helper as git


def get_time_now_str():
    return datetime.now().strftime('%Y-%m-%d-%S')


def get_shells():
    shells = []
    for name in dir(history):
        cls = getattr(history, name)
        if 'history' in name.lower() and inspect.isclass(cls) and isinstance(cls(), history.History):
            shells.append(name.lower().split('history')[0])

    return [s for s in shells if s]


def self_update():
    Log('[ history_sync self update... ]')
    running_dir = os.getcwd()
    git.git_init(settings.THIS_REPO, settings.THIS_DIR)
    git.git_check(settings.THIS_REPO, settings.THIS_DIR)
    try:
        sys_call('git fetch --all', showcmd=True)
        sys_call('git rebase origin/master', showcmd=True)
        sys_call('git push origin master', showcmd=True)
    except:
        LogError('[Error while self update]')
        try:
            Log('cleanup git...')
            if git.git_check_repo_bare():
                sys_call('git rm -r -f --cached .')
            sys_call('git clean -d -f')
            sys_call('git reset --hard master')
        except:
            pass

    os.chdir(running_dir)


def sync():
    self_update()

    # shells = sys.argv[1:] if len(sys.argv) > 1 else get_shells()
    shells = ['zsh']
    Log('shells: ', shells)

    # init history repo
    git.git_init_history_repo(settings.HISTORY_REPO, settings.HISTORY_DIR)

    # check git status all right
    git.git_check(settings.HISTORY_REPO, settings.HISTORY_DIR)
    if not git.git_check_repo_clean():
        raise Exception('git directory dirty')

    # do history merge and sync
    try:
        Log('==> [ pull history from origin ]')
        sys_call('git fetch origin')
        if not git.git_check_repo_bare():
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
            shutil.copy(shell_his_dir, os.path.join(settings.BACKUP_DIR, shell + '_history.' + get_time_now_str()))
            history.History.merge_file(shell_his_dir, settings.HISTORY_FILE_NAME, settings.HISTORY_FILE_NAME, cls1=ShellHistory, cls2=history.History)

        for shell in shells:
            Log('[ update history %s... ]' % shell)
            ShellHistory = globals()[shell.capitalize() + 'History']
            shell_his_dir = ShellHistory._get_history_dir()
            if not os.path.exists(shell_his_dir):
                Log('%s shell history does not exist' % shell)
                continue
            ShellHistory.convert_file(settings.HISTORY_FILE_NAME, shell_his_dir, cls1=history.History)
    except Exception as e:
        LogError('[Error while syncing]')
        try:
            Log('cleanup git...')
            if git.git_check_repo_bare():
                sys_call('git rm -r -f --cached .')
            sys_call('git clean -d -f')
            sys_call('git reset --hard master')
        except Exception as e1:
            pass
        raise e

    Log('==> [ push history to origin ]')
    # sys_call('git add %s' % settings.HISTORY_FILE_NAME)
    sys_call('git add --all')
    if not git.git_check_repo_clean():
        sys_call('git commit -m "%s save history: %s"' % (get_time_now_str(), shells))
        sys_call('git push origin master')


if __name__ == '__main__':
    sync()
