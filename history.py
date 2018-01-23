from datetime import datetime
from operator import attrgetter
from action import *
import pickle
import tools
import settings
import codecs


class History:
    DEFAULT_HISTORY_FILE = '~/.my_history/history'
    _SEPARATOR = '\n'
    _before_merge_actions = [filter_white_line_action]
    _after_merge_actions = [unique_action, delete_password_action, limit_length_action]

    _DEFAULT_TIME = datetime.fromtimestamp(1)

    def __init__(self, cmd='', time=_DEFAULT_TIME, duration=0, paths=None):

        if paths is None:
            paths = []
        self.cmd = cmd
        self.time = time
        self.duration = duration
        self.paths = paths

    def __str__(self):
        return ' '.join([str(x) for x in pickle.dumps(self)])

    def __eq__(self, other):
        return self.cmd == other.cmd and self.time == other.time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.time, self.cmd))

    @classmethod
    def _get_history_dir(cls):
        name = cls.__name__
        his_dir = tools.camel_to_upper(name) + '_DIR'
        if hasattr(settings, his_dir):
            return tools.full_path(getattr(settings, his_dir))
        else:
            return tools.full_path(cls.DEFAULT_HISTORY_FILE)

    @classmethod
    def _merge_text(cls, text1, text2, cls1=None, cls2=None):
        histories1 = cls1._parse_text(text1, cls)
        histories2 = cls2._parse_text(text2, cls)
        histories_save = cls._merge_history(histories1, histories2)
        text_save = cls._SEPARATOR.join([h.__str__() for h in histories_save]) + cls._SEPARATOR
        tools.Log('%s(%s) + %s(%s) => %s(%s)' % (
            cls1.__name__, len(histories1), cls2.__name__, len(histories2), cls.__name__, len(histories_save)))
        return text_save

    @classmethod
    def merge_file(cls, file1, file2, file_save, cls1=None, cls2=None):
        if cls1 is None:
            cls1 = cls
        if cls2 is None:
            cls2 = cls

        with codecs.open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            text1 = f.read()
        with codecs.open(file2, 'r', encoding='utf-8', errors='ignore') as f:
            text2 = f.read()
        text_save = cls._merge_text(text1, text2, cls1, cls2)
        with open(file_save, 'w') as f:
            f.write(text_save)

    @classmethod
    def _convert_text(cls, text1, cls1=None):
        histories = cls1._parse_text(text1, cls)

        for func in cls._before_merge_actions:
            histories = func(histories)
        for func in cls._after_merge_actions:
            histories = func(histories)
        histories = cls._sort(histories)

        text_save = cls._SEPARATOR.join([h.__str__() for h in histories]) + cls._SEPARATOR
        return text_save

    @classmethod
    def convert_file(cls, file1, file_save, cls1=None):
        if cls1 is None:
            cls1 = cls
        with codecs.open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            text1 = f.read()
        text_save = cls._convert_text(text1, cls1)
        with codecs.open(file_save, 'w') as f:
            f.write(text_save)

    @staticmethod
    def _parse_text(text, aim_cls=None):
        if aim_cls is None:
            aim_cls = History
        lines = text.split('\n')
        histories = []
        for line in lines:
            if line:
                h = pickle.loads(bytes([int(x) for x in line.split(' ')]))
                h.__class__ = aim_cls
                histories.append(h)
        return histories

    @classmethod
    def _merge_history(cls, histories1, histories2):
        for func in cls._before_merge_actions:
            histories1, histories2 = func(histories1), func(histories2)
        histories_save = histories1 + histories2
        for func in cls._after_merge_actions:
            histories_save = func(histories_save)
        return cls._sort(histories_save)

    @staticmethod
    def _sort(histories):
        return sorted(histories, key=attrgetter('time'))


class BashHistory(History):
    DEFAULT_HISTORY_FILE = '~/.bash_history'

    @staticmethod
    def _parse_text(text, aim_cls=None):
        if aim_cls is None:
            aim_cls = BashHistory
        lines = text.split('\n')
        lines = tools.filter_white_lines(lines)
        histories = [aim_cls(cmd=l) for l in lines]
        return histories

    def __str__(self):
        return self.cmd


class ZshHistory(History):
    DEFAULT_HISTORY_FILE = '~/.zsh_history'
    _after_merge_actions = History._after_merge_actions + [unique_cmd_action]

    @staticmethod
    def _parse_text(text, aim_cls=None):
        if aim_cls is None:
            aim_cls = ZshHistory
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
        histories = []
        for line in lines:
            try:
                x = line.split(":", 2)
                time = int(x[1])
                duration, cmd = x[2].split(";", 1)
                histories.append(aim_cls(cmd, datetime.fromtimestamp(time), int(duration)))
            except Exception as e:
                print('[Error while parse]: %s' % line)
        return histories

    def __str__(self):
        return ': %s:%s;%s' % (int(self.time.timestamp()), int(self.duration), self.cmd)


class FishHistory(History):
    DEFAULT_HISTORY_FILE = '~/.local/share/fish/fish_history'

    @staticmethod
    def _parse_text(text, aim_cls=None):
        if aim_cls is None:
            aim_cls = FishHistory
        lines = text.split('\n')
        histories = []
        h = aim_cls()
        for (id, line) in enumerate(lines):
            try:
                if line.startswith('- cmd:'):
                    if h.cmd:
                        histories.append(h)
                    h = aim_cls(cmd=line.split(':')[1][1:])
                elif line.startswith('  when:'):
                    h.time = datetime.fromtimestamp(int(line.split(':')[1][1:]))
                elif line.startswith('  paths:'):
                    pass
                elif line.startswith('    -'):
                    h.paths.append(line.split('-')[1][1:])
            except Exception as e:
                print('[Error while parse]: %s' % line)
                raise e

        if h.cmd:
            histories.append(h)
        return histories

    def __str__(self):
        s = '- cmd: %s\n' \
            '  when: %s' % (self.cmd, int(self.time.timestamp()))
        if self.paths:
            s += '\n  paths:\n' + '\n'.join(['    - ' + p for p in self.paths])
        return s


if __name__ == '__main__':
    # History.merge_file('test/za', 'test/fb', 'test/co', cls1=ZshHistory, cls2=FishHistory)
    # ZshHistory.merge_file('test/a', 'test/b', 'test/c')
    ZshHistory.convert_file('test/a', 'test/c')
    # with open('test/co') as f:
    #     hs = History._parse_text(f.read())
    #     for h in hs:
    #         # pass
    #         h.__class__ = ZshHistory
    #         print(h)
    # print(History._get_history_dir())
    # print(ZshHistory._get_history_dir())
    # print(FishHistory._get_history_dir())
    pass
