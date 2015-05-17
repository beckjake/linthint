# pylint:disable=invalid-name,missing-docstring,too-few-public-methods,redefined-builtin
from __future__ import print_function
from linthints import adds_arguments, sets_arguments

import sys
def bogus_dec(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


@adds_arguments(file=None)
@sets_arguments(c=1)
def simple_function_dec(func):
    def inner(*args, **kwargs):
        file = kwargs.pop('file', None) or sys.stdout
        print('{}(*{}, **{})'.format(func.__name__, args, kwargs), file=file)
        kwargs['c'] = 1
        return func(*args, **kwargs)
    return inner


@adds_arguments(file=None)
@sets_arguments(c=1)
def complex_function_dec(*oargs, **okwargs):
    def wrapper(func):
        def inner(*args, **kwargs):
            file = kwargs.pop('file', None) or sys.stdout
            print('Outer args={}, kwargs={}'.format(oargs, okwargs), file=file)
            kwargs['c'] = 1
            return func(*args, **kwargs)
        return inner
    return wrapper


@adds_arguments(file=None)
@sets_arguments(c=1)
class SimpleClassDec(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, func):
        def inner(*args, **kwargs):
            file = kwargs.pop('file', None) or sys.stdout
            print('{}(*{}, **{})'.format(func.__name__, args, kwargs), file=file)
            kwargs['c'] = 1
            return func(*args, **kwargs)
        return inner


@adds_arguments(file=None)
@sets_arguments(c=1)
class ComplexClassDec(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        def inner(*args, **kwargs):
            file = kwargs.pop('file', None) or sys.stdout
            print('Class args={}, kwargs={}'.format(self.args, self.kwargs), file=file)
            kwargs['c'] = 1
            return func(*args, **kwargs)
        return inner


@bogus_dec
@simple_function_dec
@bogus_dec
def simple_function_add(a, b, c=0):
    return a + b + c

@complex_function_dec('hello', world='world')
@bogus_dec
def complex_function_add(a, b, c=0):
    return a + b + c

@SimpleClassDec
def simple_class_add(a, b, c=0):
    return a + b + c

@bogus_dec
@ComplexClassDec('hello', world='world')
def complex_class_add(a, b, c=0):
    return a + b + c

def undecorated_add(a, b, c=0):
    return a + b + c

@bogus_dec
def noarg_decorated_add(a, b, c=0):
    return a + b + c


