# -*- coding: utf-8 -*-
from pathlib import Path

from django_setup import common_init
from django_settings_env import Env


def test_apn_set():
    prog, env = common_init()
    assert isinstance(prog, str)
    assert isinstance(env, Env)

    assert 'APN_HOME' in env
    assert env('APN_HOME') == str(Path.cwd().parent)

