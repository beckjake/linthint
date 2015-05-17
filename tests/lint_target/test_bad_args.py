"""Generator for the test statements."""
from itertools import product

NAMES = [
    'simple_function_add',
    'complex_function_add',
    'simple_class_add',
    'complex_class_add'
]

VALID_PATTERNS = [
    '{func}(1, 2)', '{func}(a=1, b=2)', '{func}(1, b=2)',
    '{func}(1, 2, file=sys.stderr)',
    '{func}(a=1, b=2, file=sys.stderr)',
    '{func}(1, b=2, file=sys.stderr)',
    '{func}(file=sys.stderr, a=1, b=2)',
    '{func}(1, file=sys.stderr, b=2)'
]

INVALID_PATTERNS = [
    '{func}(1, 2, notanarg=None)',
    '{func}(1, b=2, notanarg=None)'
]

VALID_C_PATTERNS = [
    '{func}(1, 2, c=0)',
    '{func}(a=1, b=2, c=0)',
    '{func}(1, file=sys.stderr, c=0, b=2)'
]


EQUALS_4 = ['assert '+x+'==4' for x in VALID_PATTERNS]
EQUALS_3 = ['assert '+x+'==5' for x in VALID_C_PATTERNS]
EQUALS = EQUALS_3 + EQUALS_4

def get_stmts():
    """Get all statements"""
    imp = 'import sys\nfrom lint_target.test_module import {func}\n'
    for pattern, name in product(VALID_PATTERNS+VALID_C_PATTERNS, NAMES):
        fmt = imp+pattern
        yield fmt.format(func=name), True
    for pattern, name in product(INVALID_PATTERNS, NAMES):
        fmt = imp+pattern
        yield fmt.format(func=name), False
    for pattern, name in product(EQUALS, NAMES):
        fmt = imp+pattern
        yield fmt.format(func=name), True
