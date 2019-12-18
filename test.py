#!/usr/bin/env python3
import os
import os.path as osp

from lib.history import HistoryMergeHelper


def merge():
    HistoryMergeHelper._sort_by_time = HistoryMergeHelper._sort_by_cmd

    base_dir = 'my_history/backup'
    summary = 'summary.txt'
    cnt = 0
    open(summary, 'w').close()
    for f in os.listdir(base_dir):
        if f.startswith('zsh'):
            file_path = osp.join(base_dir, f)
            print(file_path)
            HistoryMergeHelper.merge_file(file_path, summary, summary)
            print()


if __name__ == '__main__':
    merge()
