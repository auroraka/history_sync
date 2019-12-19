#!/usr/bin/env python3
import shutil
import sys
import inspect
import textwrap
import os
import os.path as osp
from datetime import datetime
import argparse

from lib.tools import Log, LogError, sys_call, full_path, touch_file
import conf.settings as settings
from lib.history import HistoryMergeHelper
from cleaner import Cleaner
import lib.git_helper as git


def get_time_now_str():
    return datetime.now().strftime('%Y-%m-%d_%H-%M')


def self_update():
    if settings.args.debug:
        Log('[ Debug Mode: skip self update ]')
        return
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


USAGE = '''
History Sync

example:
history_sync
history_sync -d
history_sync -dd
'''


def parse_arg():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(USAGE))
    parser.add_argument('-d', '--debug', action='count', default=0, help='debug')
    args = parser.parse_args()
    settings.args = args
    return args


def sync():
    args = parse_arg()
    self_update()

    if settings.args.debug > 1:
        Log('[ Debug Mode: skip history repo check ]')
    else:
        # init history repo
        git.git_init(settings.HISTORY_REPO, settings.HISTORY_DIR)

        # check git status all right
        git.git_check(settings.HISTORY_REPO, settings.HISTORY_DIR)
        if not git.git_check_repo_clean():
            raise Exception('git directory dirty')

    # do history merge and sync
    try:
        if settings.args.debug > 1:
            Log('[ Debug Mode: skip pull origin ]')
        else:
            Log('==> [ pull history from origin ]')
            sys_call('git fetch origin')
            if not git.git_check_repo_bare():
                sys_call('git reset --hard origin/master')

        Log('==> [ sync zsh_history ]')

        os.makedirs(full_path(settings.BACKUP_BEFORE_DIR), exist_ok=True)
        os.makedirs(full_path(settings.BACKUP_AFTER_DIR), exist_ok=True)
        if not os.path.exists(settings.HISTORY_FILE_NAME):
            touch_file(settings.HISTORY_FILE_NAME)

        zsh_history = full_path(settings.ZSH_HISTORY_FILE)
        time_now_str = get_time_now_str()

        Log('[ backup before sync... ]')
        backup_name = osp.join(settings.BACKUP_BEFORE_DIR, 'zsh_histroy.'+time_now_str)
        shutil.copy(zsh_history, backup_name)

        Log('[ merge history file... ]')
        HistoryMergeHelper.merge_file(zsh_history, settings.HISTORY_FILE_NAME, zsh_history)
        Log('[ run history clean... ]')
        Cleaner(use_default_rule=True, history_path=full_path(settings.ZSH_HISTORY_FILE)).clean()
        if settings.args.debug <= 1:
            shutil.copy(zsh_history, settings.HISTORY_FILE_NAME)

        Log('[ backup after sync... ]')
        backup_name = osp.join(settings.BACKUP_BEFORE_DIR, 'zsh_histroy.'+time_now_str)
        shutil.copy(zsh_history, backup_name)

    except Exception as e:
        LogError('[Error while syncing]')
        try:
            if not settings.args.debug:
                Log('cleanup git...')
                if git.git_check_repo_bare():
                    sys_call('git rm -r -f --cached .')
                sys_call('git clean -d -f')
                sys_call('git reset --hard master')
        except Exception as e1:
            pass
        raise e

    if settings.args.debug > 1:
        Log('[ Debug Mode: skip push origin ]')
    else:
        Log('==> [ push history to origin ]')
        sys_call('git add --all')
        if not git.git_check_repo_clean():
            sys_call('git commit -m "save history: {}"'.format(time_now_str))
            sys_call('git push origin master')


if __name__ == '__main__':
    sync()
