## Zsh History Sync

History sync script base on git/python/shell.

This script cleanup your zsh history and sync it with remote version from git private/public repository.

## Feature
- **cross server** sync
- **cross shell** sync
- support pre-deal **pulgin** before/after sync
- use git to **achieve security** and **push history to origin**
- **auto sync** history when shell start up

## Require
- git version >= 2.0
- python version >= 3.0

## Usage
- `./sync.py`
- `./cleaner.py -c clean.rule -p ~/.zsh_history`

## TODO
- add pip install