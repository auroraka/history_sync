#!/usr/bin/env python3

'''
Filename: /Users/ytl/.ytl/var/history_sync/merge.py
Path: /Users/ytl/.ytl/var/history_sync
Created Date: Thursday, December 12th 2019, 1:14:20 pm
Author: aurayang <aurayang@tencent.com>

Copyright (c) 2019 Your Company
'''

import os
import os.path as osp


def unique_add_to_summary(file_paths):
    with open('summary.txt', 'r') as f:
        lines = f.readlines()
    s = set(lines)

    for file_path in file_paths:
        print('add file {}'.format(file_path), end='')

        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
        s2 = s.union(set(lines))
        print(' + {}'.format(len(s2)-len(s)))
        s = s2

    with open('summary.txt', 'w') as f:
        ls = list(s)
        ls.sort()
        f.writelines(ls)


def main():
    f = open('summary.txt', 'w')
    f.close()

    dir_name = 'my_history/backup'
    file_paths = []
    for file_name in os.listdir(dir_name):
        if file_name.startswith('zsh'):
            file_path = osp.join(dir_name, file_name)
            file_paths.append(file_path)

    unique_add_to_summary(file_paths)


if __name__ == '__main__':
    main()
