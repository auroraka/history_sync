from operator import attrgetter
import re


def filter_white_line_action(histories):
    return [h for h in histories if h.cmd]


def unique_action(histories):
    return list(set(histories))


def unique_cmd_action(histories):
    histories = sorted(histories, key=attrgetter('cmd', 'time'))
    try:
        last = histories[0]
        last.cmd = '#'
    except Exception as e:
        last = None

    new_histories = []
    for h in histories:
        if h.cmd != last.cmd:
            new_histories.append(h)
        last = h
    return new_histories


def delete_password_action(histories):
    return [h for h in histories if 'pwd' not in h.cmd and 'password' not in h.cmd and 'passwd' not in h.cmd]


def limit_length_action(histories):
    return [h for h in histories if len(h.cmd) < 500]


def filter_invalid(histories):
    histories = [h for h in histories if (': 1:0;' not in h.cmd)]
    histories = [h for h in histories if not h.cmd.endswith('\\')]
    r = re.compile(r'[\s\S]*: \d{10}:\d;[\s\S]*')
    histories = [h for h in histories if not r.match(h.cmd)]
    return histories
