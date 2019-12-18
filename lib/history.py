from datetime import datetime
from operator import attrgetter
import pickle
import codecs
import os.path as osp
import time

import lib.tools as tools
import lib.action as act
import conf.settings as settings
from lib.tools import Log
from lib.history_base import HistoryObj

'''
Usage:
HistoryMergeHelper.format_file(file_path, save_path)
HistoryMergeHelper.merge_file(file1_path, file2_path, save_path)

Zsh History Format Reference:
: <beginning time>:<elapsed seconds>;<command>

<elapsed seconds> will always be 0, if the INC_APPEND_HISTORY option is set
'''


class HistoryMergeHelper:
    DEFAULT_HISTORY_FILE = '~/.zsh_history'
    _before_merge_actions = []
    _after_merge_actions = [
        act.action_strip_cmd,
        act.action_filter_empty_cmd,
        act.action_unique,
        act.action_unique_cmd,
        act.action_limit_length,
        act.action_limit_cmd_lines,
        act.action_filter_invalid_cmd,
        act.action_filter_invalid_time,

        act.action_delete_password,
        act.action_keep_only_one_for_no_time_cmd,
    ]

    @classmethod
    def _get_history_dir(cls):
        name = cls.__name__
        his_dir = tools.camel_to_upper(name) + '_DIR'
        if hasattr(settings, his_dir):
            return tools.full_path(getattr(settings, his_dir))
        else:
            return tools.full_path(cls.DEFAULT_HISTORY_FILE)

    @classmethod
    def _merge_history(cls, objs1, objs2):
        for func in cls._before_merge_actions:
            objs1, objs2 = func(objs1), func(objs2)
        objs_save = objs1 + objs2
        for func in cls._after_merge_actions:
            cnt = len(objs_save)
            objs_save = func(objs_save)
            cnt2 = len(objs_save)
            inc_cnt = cnt2-cnt
            # Log('{:30}: {} -> {}({:d})'.format(func.__name__, cnt, cnt2, inc_cnt))
        return cls._sort_by_time(objs_save)

    @staticmethod
    def _sort_by_time(histories):
        return sorted(histories, key=attrgetter('time', 'cmd'))

    @staticmethod
    def _sort_by_cmd(histories):
        return sorted(histories, key=attrgetter('cmd', 'time'))

    @staticmethod
    def _text2objs(text):
        # get lines
        lines_tmp = text.split('\n')
        it = iter(lines_tmp)
        lines = []
        for l in it:
            cmd = l
            while cmd.endswith('\\'):
                cmd += '\n' + next(it)
            if cmd:
                lines.append(cmd)
        # make histories
        objs = []
        for line in lines:
            try:
                x = line.split(":", 2)
                time = int(x[1])
                duration, cmd = x[2].split(";", 1)
                objs.append(HistoryObj(cmd=cmd, time=datetime.fromtimestamp(time), duration=int(duration)))
            except:
                Log('[Error while parse]: %s' % line)
        return objs

    @classmethod
    def _objs2text(cls, objs):
        return '\n'.join([h.__str__() for h in objs]) + '\n'

    @classmethod
    def _open_file(cls, file):
        # notice that file can be None
        if file is not None:
            with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            text = None
        return text

    @classmethod
    def merge_text(cls, text1, text2):
        objs1 = cls._text2objs(text1)
        objs2 = cls._text2objs(text2) if text2 is not None else []
        objs_save = cls._merge_history(objs1, objs2)

        text_save = cls._objs2text(objs_save)
        inc_cnt = len(objs_save)-(len(objs1)+len(objs2))
        if text2 is not None:
            Log('{} + {} => {}({:+d})'.format(len(objs1), len(objs2), len(objs_save), inc_cnt))
        else:
            Log('{} => {}({:+d})'.format(len(objs1), len(objs_save), inc_cnt))
        return text_save

    @classmethod
    def merge_file(cls, file1, file2, file_save):
        if not osp.exists(file_save):
            open(file_save, 'w').close()

        text1 = cls._open_file(file1)
        text2 = cls._open_file(file2)

        text_save = cls.merge_text(text1, text2)
        with open(file_save, 'w') as f:
            f.write(text_save)

    @classmethod
    def format_file(cls, file, file_save):
        cls.merge_file(file, None, file_save)
