import os.path as osp
from datetime import timedelta


HISTORY_REPO = 'git@github.com:auroraka/my_history2.git'
HISTORY_DIR = '~/.ytl/var/history_sync/my_history/'

HISTORY_FILE_NAME = 'zsh_history_latest'
BACKUP_BEFORE_DIR = 'backup_before_sync/'
BACKUP_AFTER_DIR = 'backup_after_sync/'

ZSH_HISTORY_FILE = '~/.zsh_history'

LAST_UPDATE_FILE_NAME = '~/.ytl/var/history_sync/last_update_time'
UPDATE_PERIOD = timedelta(days=7)

THIS_REPO = 'git@github.com:auroraka/history_sync.git'
THIS_DIR = '~/.ytl/lib/history_sync/'

CLEAN_RULE_FILE = '~/.ytl/lib/history_sync/clean.rule'

# init settings
if osp.exists(osp.join(osp.dirname(__file__), 'settings_local.py')):
    from conf import settings_local
    for x in dir(settings_local):
        if x.isupper():
            locals()[x] = getattr(settings_local, x)
