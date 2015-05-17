=========
linthints
=========

Setting up your code to use linthints requires using a decorator on your
decorator itself, and otherwise writing your decorator as you normally
would.

Adding a new optional argument interpreted by the decorator::

    >>> from linthints import adds_arguments, sets_arguments
    >>> import functools
    >>> @adds_arguments(name=None)
    ... def log_name(func):
    ...     @functools.wraps(func)
    ...     def inner(*args, **kwargs):
    ...         name = kwargs.pop('name', None)
    ...         if name is None:
    ...             name = func.__name__
    ...         print('running {}(*{}, **{})'.format(name, args, kwargs))
    ...         return func(*args, **kwargs)
    ...     return inner
    >>> @log_name
    ... def add(a, b, c=0):
    ...     return a + b + c
    >>> add(1, 2, 3) == 6
    running add(*(1, 2, 3), **{})
    True


Mark setting a value to a default likewise::

    >>> from linthints import adds_arguments, sets_arguments
    >>> import functools
    >>> @sets_arguments(b=2)
    ... def set_b(func):
    ...     @functools.wraps(func)
    ...     def inner(*args, **kwargs):
    ...         if len(args) < 2:
    ...             kwargs.setdefault('b', 2)
    ...         return func(*args, **kwargs)
    ...     return inner
    >>> @set_b
    ... def add(a, b, c=0):
    ...     return a + b + c
    >>> add(0) == 2
    True
    >>> add(a=2, b=3, c=1) == 6
    True
    >>> add(2, 3, 1) == 6
    True

Requirements
============
pylint!


Limitations
===========

For now, you have to use linthints as decorators (via the "@" syntax).
This means you can't use them via the pre-"@" syntax method. The same goes for
the decorators you decorate.


Tests
=====

Try this from the checked-out directory::

    PYTHONPATH=. python tests/test.py
    python -m doctest README.md
    pylint --load-module linthints tests/lint_targets
