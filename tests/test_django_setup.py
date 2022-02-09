# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from django_setup import common_init, default_settings, parse_commandline
from django_settings_env import Env


def test_apn_is_set():
    prog, env = common_init()
    assert isinstance(prog, str)
    assert isinstance(env, Env)

    assert 'APN_HOME' in env
    # if this fails, then most likely APN_HOME is set in the environment
    assert env('APN_HOME') == Path.cwd().parent.as_posix()


def test_apn_is_set2():
    env = Env()
    env['APN_HOME'] = Path.cwd().as_posix()
    env['DJANGO_APP'] = 'myapp'

    prog, env = common_init(env)

    assert 'APN_HOME' in env
    apn_home = env('APN_HOME')
    assert apn_home == Path.cwd().as_posix()

    django_root = Path(apn_home) / env('DJANGO_APP', 'myapp')
    assert django_root.as_posix() in sys.path


def test_default_settings():
    env = Env()
    env['APN_HOME'] = Path.cwd().as_posix()
    env['DJANGO_APP'] = 'myapp'

    prog, env, environment_settings, network_settings = default_settings()
    assert isinstance(prog, str)
    assert isinstance(env, Env)
    assert isinstance(network_settings, dict)
    assert isinstance(environment_settings, dict)


def common_commandline(argv):
    env = Env()
    env['APN_HOME'] = Path.cwd().as_posix()
    env['DJANGO_APP'] = 'myapp'
    env['SETTINGS_BASE'] = 'tests.settings'

    sys.argv = argv
    return parse_commandline(env)


def test_settings_commandline():
    prog, env, settings = common_commandline(['test', '-e', 'production', '-o', 'otherarg'])

    assert prog == 'test'
    assert len(sys.argv) == 2
    assert sys.argv[1] == 'otherarg'

    assert settings['env'] == 'production'
    assert settings['noweb']
    assert not settings['mobile']
    assert settings['site_id'] is None
    assert settings['site_ui'] is None


def test_settings_commandline2():
    prog, env, settings = common_commandline(['test', '-e', 'staging', '-n', 'bss', '-u', '16', '-o', 'otherarg'])

    assert prog == 'test'
    assert len(sys.argv) == 2
    assert sys.argv[1] == 'otherarg'

    assert settings['env'] == 'staging'
    assert settings['noweb']
    assert not settings['mobile']
    assert settings['site_id'] == 96
    assert settings['site_ui'] == 16


def test_settings_commandline_verbose(capsys):
    prog, env, settings = common_commandline(['test', '-v', '-e', 'localdev', '-n', 'bss', '-u', '16', '-o', 'extra'])

    assert prog == 'test'
    assert len(sys.argv) == 2
    assert sys.argv[1] == 'extra'

    assert settings['env'] == 'localdev'
    assert settings['noweb']
    assert not settings['mobile']
    assert settings['site_id'] == 96
    assert settings['site_ui'] == 16

    captured = capsys.readouterr()
    assert captured.err == """\
SITE_ID=96
SITE_UI=16
DJANGO_NETWORK=bss
DJANGO_ENVIRON=localdev
DJANGO_READ_DOT_ENV_FILE=False
NOT_WEB_MODE=True
RUN_AS_MOBILE=False
DJANGO_SETTINGS=tests.settings.default
"""
