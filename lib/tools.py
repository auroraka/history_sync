import subprocess
import os

ROOT_PATH = os.path.dirname(os.path.join(__file__, '../'))


def touch_file(file):
    open(file, 'a').close()


def full_path(path):
    return os.path.abspath(os.path.expanduser(path))


def filter_white_lines(lines):
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l]
    return lines


def LogError(info, *args, **kwarg):
    print('[ERROR]')
    print(info, *args, **kwarg)


def LogWarning(info, *args, **kwarg):
    print('[Warning]')
    print(info, *args, **kwarg)


def Log(*args, **kwarg):
    print(*args, **kwarg)


def LogFile(file_path, *args, **kwarg):
    f = open(file_path, 'a')
    kwarg.update({'file': f})
    print(*args, **kwarg)
    f.close()


def LogTFile(*args, **kwarg):
    LogFile('tmp.txt', *args, **kwarg)


def sys_call(cmd, showcmd=False, printScreen=True):
    if showcmd:
        Log('==>', cmd)
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip(' \n')
    if printScreen:
        Log(output)
    return output


def camel_to_underline(camel_format):
    underline_format = ''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += '_' + _s_.lower() if _s_.isupper() and underline_format else _s_
    return underline_format


def camel_to_upper(camel_format):
    return camel_to_underline(camel_format).upper()


def underline_to_camel(underline_format):
    camel_format = ''
    if isinstance(underline_format, str):
        for _s_ in underline_format.split('_'):
            camel_format += _s_.capitalize()
    return camel_format
