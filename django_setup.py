#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{prog} [options] command [django options]
  -h | --help       display this help
  -v | --verbose    display base settings on startup (default={verbose})
  -d | --dotenv     set environment from .env (default={dotenv})
  -e | --env        set run environment, default={env}
  -i | --site_id    set site_id, default={site_id}
  -u | --site_ui    set site_ui, default={site_ui}
  -m | --mobile     render with mobile ui (site_ui=13)
  -o | --noweb      enable NOT_WEB_MODE default={noweb}
  -n | --network    set network, default={network}
                    {network_keys}
"""
import sys
from typing import Union, Any

from django_settings_env import Env


APN_HOME = 'APN_HOME'
DJANGO_BASE = 'DJANGO_BASE'
DJANGO_APP = 'DJANGO_APP'
DEFAULT_NETWORK = 'default'
DEFAULT_ENVIRON = 'localdev'
DEFAULT_SETTINGS_BASE = 'config.settings.sites'


def common_init(env: Env = None):
    import sys
    from pathlib import Path
    from cmdline import add_pythonpath

    # simply use the original command from sys.argv
    prog = Path(sys.argv[0]).name

    env = env or Env()
    # determine where the basedir is
    cwd = Path.cwd()
    # use strict=True to ensure symlinks are resolved
    apn_home = env(APN_HOME, cwd.parent)
    django_base = Path(env(DJANGO_BASE, apn_home)).resolve(strict=True)
    django_app = env(DJANGO_APP, 'code')
    # set this to ensure project code and settings are found
    django_root = django_base / django_app
    add_pythonpath(django_root, prepend=True)

    # ensure APN_HOME is set if it isn't
    env.export(APN_HOME=str(apn_home))

    return prog, env


def default_settings(env: Env = None):
    prog, env = common_init(env)
    # defaults
    environment_settings = {
        'prog': prog,
        'env': env.get('DJANGO_ENVIRON', DEFAULT_ENVIRON),
        'verbose': env.bool('DJANGO_VERBOSE', False),
        'noweb': env.bool('NOT_WEB_MODE', False),
        'dotenv': env.bool('DJANGO_READ_DOT_ENV_FILE', None),
        'mobile': env.bool('RUN_AS_MOBILE', False),
        'network': env.get('DJANGO_NETWORK', DEFAULT_NETWORK),
        'site_id': env.int('SITE_ID', None) or None,
        'site_ui': env.int('SITE_UI', None) or None
    }

    network_settings = {
        # web
        'bss': dict(site_id=96, site_ui=16, network='bss'),
        'mytributes': dict(site_id=94, site_ui=15, network='mytributes'),
        'wl': dict(site_ui=14, network='wl'),
        'wl_mobile': dict(mobile=True, site_ui=13, network='wl'),

        # non-web
        'default': dict(noweb=1),
        'api': dict(noweb=1),
        'apnshell': dict(noweb=1),
        'apncore': dict(noweb=1),
        'apnexec': dict(noweb=1),
        'media': dict(noweb=1, network='media'),
    }

    return prog, env, environment_settings, network_settings


def parse_commandline(env: Env = None, setup: bool = False):
    from cmdline import Option, system_args, redirect_stdout

    prog, env, environment_settings, network_settings = default_settings(env)

    def _help(_option: Option, _opt: str, _args):
        environment_settings['network_keys'] = list(network_settings.keys())
        print(__doc__.format(**environment_settings))
        exit(0)

    def _setting(_option: Option, _opt: str, _args: Any):
        return int(_args) if _opt in ('u', 'i') else _args

    def _network(_option: Union[Option, None], _opt: Union[str, None], _args):
        if _args in network_settings:
            environment_settings.update(network_settings[_args])
        return _args

    def _mobile(_option: Option, _opt: str, _args):
        environment_settings['mobile'] = True
        return True

    cmdline_options = (
        Option('h', 'help', fn=_help),
        Option('i', 'site_id', has_arg=True, fn=_setting),
        Option('u', 'site_ui', has_arg=True, fn=_setting),
        Option('n', 'network', has_arg=True, fn=_network),
        Option('m', 'mobile', fn=_mobile),
        Option('o', 'noweb', fn=True),
        Option('d', 'dotenv', fn=True),
        Option('e', 'env', has_arg=True, fn=_setting),
        Option('v', 'verbose', fn=True),
    )

    def process_args(option, _, _args):
        if not option and prog in network_settings:
            environment_settings.update(network_settings[prog])

    def error_args(message):
        print(f'{prog}: warning: {message}', file=sys.stderr)
        # pycharm and possibly pydev also use pre-command args for passing debugger client
        # connect args so complain in case of user error but otherwise do not quit
        # exit(1)

    # initialise network values if set from environment
    _network(None, None, environment_settings['network'])

    # process partial comamnd line
    system_args(cmdline_options, process=process_args, error=error_args, results=environment_settings)

    # If using wl_mobile directly without -m option
    if prog.endswith('_mobile'):
        prog = prog[:-7]
        environment_settings['mobile'] = True

    # If wl is mobile mode we need to switch the site_ui
    if environment_settings['mobile'] and environment_settings['site_ui'] == 14:
        # mobile site request and site_ui is not overridden
        environment_settings['site_ui'] = 13

    env.export(
        DJANGO_ENVIRON=environment_settings['env'],
        DJANGO_NETWORK=environment_settings['network'],
        SITE_ID=environment_settings['site_id'],
        SITE_UI=environment_settings['site_ui'],
        NOT_WEB_MODE=1 if environment_settings['noweb'] else 0,
        RUN_AS_MOBILE=environment_settings['mobile'],
        DJANGO_READ_DOT_ENV_FILE=1 if environment_settings['dotenv'] else None
    )

    def print_settings(redirect_to, settings_module):
        with redirect_stdout(redirect_to):
            print(f"SITE_ID={environment_settings['site_id']}\n"
                  f"SITE_UI={environment_settings['site_ui']}\n"
                  f"DJANGO_NETWORK={environment_settings['network']}\n"
                  f"DJANGO_ENVIRON={environment_settings['env']}\n"
                  f"DJANGO_READ_DOT_ENV_FILE={environment_settings['dotenv']}\n"
                  f"NOT_WEB_MODE={environment_settings['noweb']}\n"
                  f"RUN_AS_MOBILE={environment_settings['mobile']}\n"
                  f"DJANGO_SETTINGS={settings_module}\n",
                  flush=True, end='')

    site_name = environment_settings['network']
    settings_module_base = env('SETTINGS_BASE', DEFAULT_SETTINGS_BASE)
    settings_module = f"{settings_module_base}.{site_name}" if site_name else settings_module_base
    settings_module_name = env('DJANGO_SETTINGS_MODULE', settings_module)

    try:
        # noinspection PyUnresolvedReferences
        import class_settings

        settings_class = f"{site_name.title()}Settings"
        env.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        env.setdefault('DJANGO_SETTINGS_CLASS', settings_class)

        if ':' in settings_module_name:
            # django class settings has stomped the environment, so use what it has set
            settings_module, settings_class = settings_module_name.rsplit(':', maxsplit=1)
        else:
            settings_module_name = f"{settings_module}:{settings_class}"

        env.set("DJANGO_SETTINGS_MODULE", settings_module)
        env.set('DJANGO_SETTINGS_CLASS', settings_class)

        # workaround for double setup with Pycharm to force correct class-based settings - its run/debug config
        # will attempt to load Django settings *first* before here, so we effectively unhook the existing wrapped
        # settings and let class_settings do its thing instead.
        if env.bool('PYCHARM_RUNNER', False) or env.bool('CLASS_SETTINGS_RESET', False):
            # noinspection PyUnresolvedReferences
            from django.conf import settings
            # noinspection PyUnresolvedReferences
            from django.utils.functional import empty

            settings._wrapped = empty

        class_settings.setup()
    except ModuleNotFoundError:

        env.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    if setup:
        import django
        django.setup()

    if environment_settings['verbose']:
        print_settings(sys.stderr, settings_module_name)
        # reset this, so we don't repeat if we are running under stat reloader
        env.set('DJANGO_VERBOSE', False)

    return prog, env, environment_settings


if __name__ == "__main__":
    raise SystemError(
        "This module is not directly runnable. It is used by other utilities "
        "to parse common command line and provide access to the Django config"
    )
