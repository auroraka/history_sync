from operator import attrgetter
import re

from lib.history_base import HistoryObj


def action_filter_empty_cmd(objs):
    return [h for h in objs if h.cmd]


def action_unique(objs):
    return list(set(objs))


def action_unique_cmd(objs):
    objs = sorted(objs, key=attrgetter('cmd', 'time'))
    new_objs = []
    size = len(objs)
    for i, h in enumerate(objs):
        if i < size-1 and h.cmd == objs[i+1].cmd:
            continue
        new_objs.append(h)
    return new_objs


def action_delete_password(objs):
    return [h for h in objs if 'pwd' not in h.cmd and 'password' not in h.cmd and 'passwd' not in h.cmd]


def action_limit_length(objs):
    LENGTH_LIMIT = 500
    return [h for h in objs if len(h.cmd) < LENGTH_LIMIT]


def action_limit_cmd_lines(objs):
    LINES_LIMIT = 3
    return [h for h in objs if h.cmd.count('\n') <= LINES_LIMIT]


def action_filter_invalid_cmd(objs):
    objs = [h for h in objs if (': 1:0;' not in h.cmd)]
    objs = [h for h in objs if not h.cmd.endswith('\\')]
    r = re.compile(r'[\s\S]*: \d{10}:\d;[\s\S]*')
    objs = [h for h in objs if not r.match(h.cmd)]
    return objs


def action_filter_invalid_time(objs):
    for i, h in enumerate(objs):
        if h.time.timestamp() < 0:
            objs[i].time = HistoryObj._DEFAULT_TIME
    return objs
