from datetime import datetime


class HistoryObj:
    _DEFAULT_TIME = datetime.fromtimestamp(1)

    def __init__(self, cmd='', time=_DEFAULT_TIME, duration=0, paths=None):

        if paths is None:
            paths = []
        self.cmd = cmd
        self.time = time
        self.duration = duration  # duration is always 0
        self.paths = paths

    def __str__(self):
        return ': %s:%s;%s' % (int(self.time.timestamp()), int(self.duration), self.cmd)

    def __eq__(self, other):
        return self.cmd == other.cmd and self.time == other.time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.time, self.cmd))

    def _print_debug_string(self):
        print(self._debug_string())

    def _debug_string(self):
        return 'time: {}\ncmd: \'{}\'\n'.format(self.time, self.cmd)
