from collections import defaultdict


def filter_white_line_action(histories):
    return [h for h in histories if h.cmd]


def unique_action(histories):
    return list(set(histories))


def delete_password_action(histories):
    return [h for h in histories if 'pwd' not in h.cmd and 'password' not in h.cmd and 'passwd' not in h.cmd]


def limit_length_action(histories):
    return [h for h in histories if len(h.cmd) < 500]
