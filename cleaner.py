#!/usr/bin/env python3
import argparse
import sys
import os
import textwrap
import os.path as osp

import conf.settings as settings
from lib.history import HistoryMergeHelper
from lib.tools import Log, LogTFile, LogFile


def match_full(cmd, key):
    return cmd == key


def match_start(cmd, key):
    return cmd.startswith(key)


def match_end(cmd, key):
    return cmd.endswith(key)


def match_contains(cmd, key):
    return key in cmd


def match_cmd_use(cmd, key):
    return cmd.split(' ')[0] == key


def _ignore_quota(c):
    return c.replace('"', '').replace('\'', '')


def match_full_ignore_quota(cmd, key):
    if cmd.startswith(sys.argv[0]):
        print(repr(_ignore_quota(cmd)), repr(_ignore_quota(key)))
    return match_full(_ignore_quota(cmd), _ignore_quota(key))


class MatchMethod(object):
    FULL = '_FULL'
    START = '_START'
    END = '_END'
    CONTAINS = '_CONTAINS'
    CMD_USE = '_CMD_USE'
    FULL_IGNORE_QUOTA = '_FULL_IGNORE_QUOTA'

    MATCH_FUNC_MAP = {
        FULL: match_full,
        START: match_start,
        END: match_end,
        CONTAINS: match_contains,
        CMD_USE: match_cmd_use,
        FULL_IGNORE_QUOTA: match_full_ignore_quota,
    }

    LIST = list(MATCH_FUNC_MAP.keys())

    LIST_LOWER = []  # create later

    @staticmethod
    def _upper(m):
        if not m.startswith('_'):
            m = '_'+m
        return m.upper()

    @staticmethod
    def _lower(m):
        if m.startswith('_'):
            m = m[1:]
        return m.lower()


MatchMethod.LIST_LOWER = [MatchMethod._lower(m) for m in MatchMethod.LIST]


class Rule:
    def __init__(self, match_method, key):
        self.match_method = match_method
        self.key = key
        # Log('[rule] add method:{} key:{}'.format(match_method, repr(key)))

    def matched(self, cmd):
        return MatchMethod.MATCH_FUNC_MAP[self.match_method](cmd, self.key)


class Cleaner:
    def __init__(self, key, match_method, rule_path, history_path, save_path):
        self.key = key
        self.rule_path = rule_path
        self.history_path = history_path
        self.save_path = save_path
        self.match_method = match_method
        self.rules = []

    def _get_last_cmd(self, lines):
        i = len(lines)-1
        while (i > 0 and len(lines[i]) == 0):
            i -= 1
        return i, lines[i]

    def _parse_rules(self):
        if not self.rule_path:
            self.rules.append(Rule(match_method=self.match_method, key=self.key))
            return

        with open(self.rule_path, 'r') as f:
            text = f.read()
        lines = text.split('\n')

        it = iter(lines)
        for l in it:
            if (len(l) == 0):
                continue
            if (l.startswith('_') and l.split(' ')[0] in MatchMethod.LIST):
                method = l.split(' ')[0]
                key = next(it)
                while key.endswith('\\'):
                    key += next(it)
                self.rules.append(Rule(match_method=method, key=key))
            else:
                Log('[rule] ignore: {}'.format(l))

    def clean(self):
        self._parse_rules()

        text = HistoryMergeHelper._open_file(self.history_path)
        objs = HistoryMergeHelper._text2objs(text)
        new_objs = []

        # remove cmd itself
        if not self.rule_path:
            rule = Rule(match_method=MatchMethod.CONTAINS, key=self.key)
            if rule.matched(objs[-1].cmd):
                del objs[-1]

        for obj in objs:
            matched = False
            matched_key = None
            matched_method = None
            for rule in self.rules:
                if rule.matched(obj.cmd):
                    matched = True
                    matched_method = rule.match_method
                    matched_key = rule.key
                    break
            if matched:
                pass
                # LogFile('delete.log', 'delete cmd: {}'.format(obj.cmd))
            else:
                new_objs.append(obj)

        new_objs = HistoryMergeHelper._sort_by_time(new_objs)
        new_text = HistoryMergeHelper._objs2text(new_objs)
        with open(self.save_path, 'w') as f:
            f.write(new_text)
        Log('{} => {}({:+d})'.format(len(objs), len(new_objs), len(new_objs) - len(objs)))


USAGE = '''
History Cleaner

example:
history_clean -m start "./clean.sh"
history_clean -r
history_clean -r -p history.txt -o save.txt
history_clean -c rule.txt -p history.txt -o save.txt
'''


def parse_arg():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(USAGE))
    parser.add_argument('cmd', nargs="*", help='cmd')

    # choose one of three
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-m', '--match',  default=MatchMethod.FULL, help='matching method[{}], default={}'.format(','.join(MatchMethod.LIST_LOWER), MatchMethod.FULL_IGNORE_QUOTA))
    g.add_argument('-c', '--rule_config',  default=None, help='rule config file path')
    g.add_argument('-r', '--default_rule', action="store_true", help="use default rule file")

    parser.add_argument('-p', '--history_path', default=osp.expanduser(settings.ZSH_HISTORY_FILE), help='history file path, default ~/.zsh_history')
    parser.add_argument('-o', '--output', help='output path, default same as history_path')
    parser.add_argument('-d', '--debug', action="store_true", help="debug")
    args = parser.parse_args()

    # check cmd
    args.cmd = ' '.join(args.cmd)
    if not args.cmd and (not args.rule_config and not args.default_rule):
        Log('error empty cmd')
        sys.exit(0)

    # check match
    if MatchMethod._upper(args.match) not in MatchMethod.LIST:
        Log('invalid match method: {}'.format(args.match))
        sys.exit(0)
    else:
        args.match = MatchMethod._upper(args.match)

    # check rule
    if args.default_rule:
        args.rule_config = osp.expanduser(settings.CLEAN_RULE_FILE)
    else:
        if args.rule_config is not None:
            if not osp.exists(args.rule_config):
                Log('error cannot open rule config file: {}'.format(args.rule_config))
                sys.exit(0)

    # check history_path
    if not osp.exists(args.history_path):
        Log('error cannot open history file: {}'.format(args.history_path))
        sys.exit(0)

    # check output_path
    if args.output is None:
        args.output = args.history_path

    # check debug
    DEBUG_PATH = 'debug.txt'
    if args.debug:
        # HistoryMergeHelper._sort_by_time = HistoryMergeHelper._sort_by_cmd
        Log('----- DEBUG MODE -----')
        args.output = DEBUG_PATH

    return args


def main():
    args = parse_arg()
    c = Cleaner(
        args.cmd,
        args.match,
        args.rule_config,
        args.history_path,
        args.output,
    )
    c.clean()


if __name__ == '__main__':
    main()
