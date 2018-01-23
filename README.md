#### History sync
History sync script base on git.

This script parse history file to python class, merge histories with remote, and save it to your git server.

#### Feature
- **cross server** sync
- **cross shell** sync
- support pre-deal **pulgin** before/after sync
- use git to **achieve security** and **push history to origin**
- **auto sync** history when shell start up

#### Require
- git version >= 2.0
- python version >= 3.0

#### Install
- create an empty repository in github to store your history files, we recommend to use a private repo

    for example:`git@github.com:auroraka/my_history.git`
- clone project
```bash
git clone git@github.com:auroraka/history_sync.git ~/.history_sync
cd ~/.history_sync
```
- record your new repo in `settings.py`
    
    for example:
    ```bash
    echo "HISTORY_REPO = 'git@github.com:auroraka/my_history.git'" >> settings.py
    echo "HISTORY_DIR = '~/.my_history'" >> settings.py
    ```
    
    more settings refer [settings](#settings)

- add command alias to bashrc
for bash user
```bash
echo 'alias history_sync="$HOME/.history_sync/sync.py"' > ~/.bashrc
```
for zsh user
```bash
echo 'alias history_sync="$HOME/.history_sync/sync.py"' > ~/.zshrc
```
for fish user
```bash
echo 'alias history_sync "$HOME/.history_sync/sync.py"' > ~/.config/fish/config.fish
```
- refresh your shell and enjoy it
```bash
exec $0
```

#### Auto sync history
- add these command to the end of your bashrc/zshrc
```bash
if [[ -f $HOME/.history_sync/autosync.py ]];then;$HOME/.history_sync/autosync.py;fi
```

#### Command
```bash
history_sync            # sync all shells
history_sync bash zsh   # sync specific shells
```

#### Add New Shell
history_sync now support these shells
- bash
- zsh
- fish

you can add more shell by inherit `History` class in history.py , and realize `_parse_text`,`__str__` in class.

`_parse_text`: input a string content of history file, output list of History class, each History class is a command history.

`__str__`: convert History class to specific shell format of string

#### Plugin
you can add plugins before/after merge, and register by change attribute `_before_merge_actions`,`_after_merge_actions` of History class.
see `action.py`

#### Settings
<a name="setting"></a>
settings store in `settings.py`

| variable_name              | meaning                              | required | default      |
|----------------------------|--------------------------------------|----------|--------------|
| HISTORY_REPO               | repo to store history                | yes      | #            |
| HISTORY_DIR                | repo directory                       | yes      | #            |
| HISTORY_FILE_NAME          | history file name                    | no       | history      |
| BACKUP_DIR                 | old history backup dir               | no       | backup       |
| ${SHELL_NAME}_HISTORY_FILE | directory of your shell history      | no       | ...          |
| LAST_UPDATE_FILE_NAME      | file name of last update time record | no       | .last_update |
| UPDATE_PERIOD              | time period of auto sync             | no       | 7 days       |

example file of `settings.py`, you can find this text under `settings_default.py`
```python
from datetime import timedelta

HISTORY_REPO = 'git@github.com:auroraka/my_history.git'
HISTORY_DIR = '~/.my_history'
HISTORY_FILE_NAME = 'history'

BACKUP_DIR = 'backup'

BASH_HISTORY_FILE = '~/.bash_history'
ZSH_HISTORY_FILE = '~/.zsh_history'
FISH_HISTORY_FILE = '~/.local/share/fish/fish_history'

LAST_UPDATE_FILE_NAME = '.last_update'
UPDATE_PERIOD = timedelta(days=7)
```
