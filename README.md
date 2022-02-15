# Django setup
## Synopsis
```python
from django_setup import parse_commandline

parse_commandline()
```
or, as a context manager
```python
from django_setup import DjangoSetup

with DjangoSetup():
    import ...
```

## Description
This module provides some setup and support for some generic command line options
for scripts that require access to the Django environment, including `manage.py` itself.

Some code in this module is specific to the APN/Newscorp environment although the
code can easily be adaptred for any other environment.
See the `common_init` and `default_settings` functions in this module for further information.

`parse_commandline` supports some additional kwargs:

- `env` (default=None) is a Env instance (see [django-settings-env](https://pypi.org/project/django-settings-env/))
  if not specified or set to None, one is created. This may be useful to prepare the environment before Django is
  initialised.
- `setup` (default=False) specifies whether to call `django.setup()` to run all Django initialisations and
  readying apps

`DjangoSetup` is a context manager that takes the same arguments and does much the same as `parse_commandline`
except that by default `setup=True`.

Django imports, specifically models in your apps, should be placed within the context manger
to ensure that apps are ready to be accessed in your script.
