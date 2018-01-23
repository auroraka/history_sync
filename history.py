from datetime import datetime
from operator import attrgetter
from action import *
import pickle


class Tools:
    @staticmethod
    def filter_white_lines(lines):
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        return lines


class History:
    _SEPARATOR = '\n'
    _brefore_merge_actions = [filter_white_line_action]
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
    def _merge_text(cls, text1, text2, cls1=None, cls2=None):
        histories1 = cls1._parse_text(text1, cls)
        histories2 = cls2._parse_text(text2, cls)
        histories_save = cls._merge_history(histories1, histories2)
        return cls._SEPARATOR.join([h.__str__() for h in histories_save])

    @classmethod
    def merge_file(cls, file1, file2, file_save, cls1=None, cls2=None):
        if cls1 is None:
            cls1 = cls
        if cls2 is None:
            cls2 = cls

        with open(file1, 'r') as f:
            text1 = f.read()
        with open(file2, 'r') as f:
            text2 = f.read()
        text_save = cls._merge_text(text1, text2, cls1, cls2)
        with open(file_save, 'w') as f:
            f.write(text_save)

    @classmethod
    def _convert_text(cls, text1, cls1=None):
        return cls1._parse_text(text1, cls)

    @classmethod
    def convert_file(cls, file1, file_save, cls1=None):
        if cls1 is None:
            cls1 = cls
        with open(file1, 'r') as f:
            text1 = f.read()
        text_save = cls._convert_text(text1, cls1)
        with open(file_save, 'w') as f:
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
        for func in cls._brefore_merge_actions:
            histories1, histories2 = func(histories1), func(histories2)
        histories_save = histories1 + histories2
        for func in cls._after_merge_actions:
            histories_save = func(histories_save)
        return cls._sort(histories_save)

    @staticmethod
    def _sort(histories):
        return sorted(histories, key=attrgetter('time'))


class BashHistory(History):
    @staticmethod
    def _parse_text(text, aim_cls=None):
        if aim_cls is None:
            aim_cls = BashHistory
        lines = text.split('\n')
        lines = Tools.filter_white_lines(lines)
        histories = [aim_cls(cmd=l) for l in lines]
        return histories

    def __str__(self):
        return self.cmd


class ZshHistory(History):
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
    History.merge_file('test/za', 'test/fb', 'test/co', cls1=ZshHistory, cls2=FishHistory)
    with open('test/co') as f:
        hs = History._parse_text(f.read())
        for h in hs:
            # pass
            h.__class__ = ZshHistory
            print(h)
