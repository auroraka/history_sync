#!/usr/bin/env python3
import os
from datetime import datetime
import tools
import settings
from sync import sync

def auto_sync():
    tools.make_default_settings()
    record_file = settings.LAST_UPDATE_FILE_NAME
    if not os.path.exists(record_file):
        os.makedirs(os.path.dirname(record_file))
        open(record_file, 'a').close()
    with open(record_file) as f:
        try:
            last_update_time = datetime.fromtimestamp(float(f.read()))
        except Exception as e:
            tools.Log('no record file found, create one')
            last_update_time = datetime.fromtimestamp(0)
    if datetime.now() - last_update_time > settings.UPDATE_PERIOD:
        shall = input("sync history? (y/N) ").lower() == 'y'
        if shall:
            tools.Log('[ start history syncing... ]')
            sync()
        with open(record_file, 'w') as f:
            f.write(str(datetime.now().timestamp()))


if __name__ == '__main__':
    auto_sync()
