# Django setup
## Synopsis
```python
from django_setup import parse_commandline

parse_commandline()
```

## Description
This module provides some setup and support for some generic command line options
for scripts that require access to the Django environment, including `manage.py` itself.

Some code in this module is specific to the APN/Newscorp environment although the
code can easily be adaptred for any other environment.
See the common_init function in this module for further information.

