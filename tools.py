import subprocess
import os

try:
    import settings
except ModuleNotFoundError as e:
    settings_file = os.path.join(os.path.dirname(__file__), 'settings.py')
    if not os.path.exists(settings_file):
        open(settings_file, 'a').close()
        import settings
    else:
        raise e
try:
    import settings_default
except ImportError:
    raise Exception('Error: setting_default.py must exist')


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


def Log(*args, **kwarg):
    print(*args, **kwarg)


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


def make_default_settings():
    default_settings = [(x, getattr(settings_default, x)) for x in dir(settings_default) if x.isupper()]
    for k, v in default_settings:
        if not hasattr(settings, k):
            setattr(settings, k, v)


if __name__ == '__main__':
    make_default_settings()
