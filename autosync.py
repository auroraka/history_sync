#!/usr/bin/env python3
import os
import settings
from datetime import datetime
from sync import sync
import tools

if __name__ == '__main__':
    tools.make_default_settings()
    record_file = os.path.join(os.path.dirname(__file__), settings.LAST_UPDATE_FILE_NAME)
    if not os.path.exists(record_file):
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
