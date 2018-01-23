#### Hsync
Hsync is a history sync script base on git.

This script parse history file to python class, merge histories with remote, and save it to your git server.

#### Feature
- **cross server** sync
- **cross shell** sync
- support pre-deal **pulgin** before/after sync
- use git to **achieve security** and **push history to origin**

#### Install
- clone project
```
git clone git@github.com:auroraka/hsync.git ~/.hsync
```
- add alias to bashrc
for bash user
```
echo 'alias hsync="$HOME/.hsync/sync.py"' > ~/.bashrc
```
for zsh user
```
echo 'alias hsync="$HOME/.hsync/sync.py"' > ~/.zshrc
```
for fish user
```
echo 'alias hsync="$HOME/.hsync/sync.py"' > ~/.config/fish/config.fish
```
- add repo to store history
change `HISTORY_REPO` to the repo you store history in `settings.py`
change `HISTORY_DIR` to the repo directory in `settings.py` 
- restart your shell
```
exec $0
```

#### Use
```
hsync            # sync all shells
hsync bash zsh   # sync specific shells
```

#### Add New Shell
hsync now support these shells
- bash
- zsh
- fish

you can add more shell by inherit `History` class in history.py , and realize `_parse_text`,`__str__` in class.

`_parse_text`: input a string content of history file, output list of History class, each History class is a command history.

`__str__`: convert History class to specific shell format of string

#### Plugin
you can add plugins before/after merge, and register by change attribute `_before_merge_actions`,`_after_merge_actions` of History class.


#### Settings
settings store in `settings.py`

- HISTORY_REPO: repo to store history
- HISTORY_DIR = repo directory
- HISTORY_FILE_NAME = history file name
- BACKUP_DIR = old history backup dir
- ${SHELL_NAME}_FILE = directory of your shell history
