import subprocess
import os
import settings
import shutil
import sys
from history import *


def LogError(info, *args, **kwarg):
    print('[ERROR]')
    print(info, *args, **kwarg)


def Log(*args, **kwarg):
    print(*args, **kwarg)


def sys_call(cmd, showcmd=False, printScreen=True):
    if showcmd:
        Log('==>', cmd)
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip(' \n')
    Log(output)
    return output


def git_check_repo_clean():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'working tree clean' in info


def git_check_branch_master():
    info = sys_call('git status', showcmd=False, printScreen=False)
    return 'On branch master' in info


def git_check_repo_exists():
    info = sys_call('git remote -v | grep origin', showcmd=False, printScreen=False)
    return info.split('\n')[0].split(' ')[1] == settings.HISTORY_SAVE_REPO


def git_check():
    if not git_check_repo_exists():
        raise Exception('repo %s not found in directory: %s' % (settings.HISTORY_SAVE_REPO, settings.HISTORY_SAVE_DIR))

    if not git_check_branch_master():
        raise Exception('not on branch master')

    if not git_check_repo_clean():
        raise Exception('git directory dirty')


def get_path(path):
    return os.path.abspath(os.path.expanduser(path))


def get_time_now_str():
    return datetime.now().strftime('%Y-%m-%d-%S')


def sync():
    shells = sys.argv[1:] if len(sys.argv) > 1 else settings.SHELLS

    git_dir = get_path(settings.HISTORY_SAVE_DIR)
    os.chdir(git_dir)
    git_check()

    Log('[ pull history from origin ]')
    sys_call('git fetch origin')
    sys_call('git reset --hard origin/master')

    os.makedirs(get_path(settings.BACKUP_DIR), exist_ok=True)
    for shell in settings.SHELLS:
        ShellHistory = globals()[shell.capitalize() + 'History']
        shell_his_dir = getattr(settings, shell.upper() + '_HISTORY_DIR')
        shutil.copy(shell_his_dir,
                    os.path.join(settings.BACKUP_DIR, shell + '_history.' + get_time_now_str()))
        History.merge_file(shell_his_dir, settings.HISTORY_FILE_NAME, settings.HISTORY_FILE_NAME, cls1=ShellHistory,
                           cls2=History)

    for shell in settings.SHELLS:
        ShellHistory = globals()[shell.capitalize() + 'History']
        shell_his_dir = getattr(settings, shell.upper() + '_HISTORY_DIR')
        ShellHistory.convert_file(settings.HISTORY_FILE_NAME, shell_his_dir, cls1=History)

    Log('[ push history to origin ]')
    sys_call('git add %s' % settings.HISTORY_FILE_NAME)
    if not git_check_repo_clean():
        sys_call('git commit -m "%s save history: %s"' % (get_time_now_str(), shells))
        sys_call('git push origin master')


if __name__ == '__main__':
    sync()
