from datetime import timedelta

HISTORY_REPO = 'git@github.com:auroraka/my_history.git'
HISTORY_DIR = '~/.ytl/var/history_sync/my_history'
HISTORY_FILE_NAME = 'history'

BACKUP_DIR = 'backup'

BASH_HISTORY_FILE = '~/.bash_history'
ZSH_HISTORY_FILE = '~/.zsh_history'
FISH_HISTORY_FILE = '~/.local/share/fish/fish_history'

LAST_UPDATE_FILE_NAME = '~/.ytl/var/history_sync/last_update_time'
UPDATE_PERIOD = timedelta(days=14)

THIS_REPO = 'git@github.com:auroraka/history_sync.git'
THIS_DIR = '~/.ytl/lib/history_sync'
