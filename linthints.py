from astroid import nodes, MANAGER
try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest

def adds_arguments(**kwargs):
    """A factory for noop decorators. Pylint will inspect kwargs of this
    instantiatiosn of this factory to determine what arguments it provides.
    """
    def inner(func):
        """Return the original function, so that when adds_arguments is
        used as a decorator there is no actual runtime impact.
        """
        return func
    return inner


def sets_arguments(**kwargs):
    """A factory for noop decorators to represent one that sets arguments."""
    def inner(func):
        """Return the original function, so that when adds_arguments is
        used as a decorator there is no actual runtime impact.
        """
        return func
    return inner


class HintTransformer(object):
    def __init__(self, name, func=None):
        self.name = name
        self.func = func

    @staticmethod
    def get_decorator_children(func):
        if func and func.decorators:
            for dec in func.decorators.get_children():
                if isinstance(dec, nodes.CallFunc):
                    dec = dec.func
                yield dec

    @staticmethod
    def decorator_kwargs(defn_dec):
        call_stmt = defn_dec.parent
        if not isinstance(call_stmt, nodes.CallFunc):
            # bail!
            return
        for kwd in call_stmt.args:
            if isinstance(kwd, nodes.Keyword):
                yield kwd.arg, kwd.value

    def function_args(self):
        return dict(zip_longest(reversed(foo.argnames()), reversed(foo.args.defaults)))

    def get_decorators_for(self, node):
        """Get the first statement result for the lookup that defines a given
        node.
        """
        try:
            stmt = self.func.lookup(node.name)[1][0]
        except IndexError:
            return ()
        return self.get_decorator_children(stmt)

    def find_decorator(self):
        for dec in self.get_decorator_children(self.func):
            for defn_dec in self.get_decorators_for(dec):
                if defn_dec.name == self.name:
                    return defn_dec

    def transform(self):
        defn_dec = self.find_decorator()
        if defn_dec:
            self.modify_function(defn_dec)

    def __call__(self, func):
        self.func = func
        self.transform()

    def modify_function(self, dec):
        """Modify the function based on dec."""
        raise NotImplementedError


class AddsArgumentTransformer(HintTransformer):
    """A HintTransformer that adds new arguments based on the decorator's kwargs."""
    def __init__(self, name='adds_arguments', func=None):
        super(AddsArgumentTransformer, self).__init__(name, func)

    def modify_function(self, dec):
        # We want to look at the parent args.
        argsnode = self.func.args
        for argname, default in self.decorator_kwargs(dec):
            new_arg = nodes.AssName()
            new_arg.name = argname
            new_arg.parent = argsnode
            argsnode.args.append(new_arg)
            argsnode.defaults.append(default)
            default.parent = argsnode


class SetsArgumentTransformer(HintTransformer):
    """A HintTransformer that sets existing arguments based on the decorator's kwargs."""
    def __init__(self, name='sets_arguments', func=None):
        super(SetsArgumentTransformer, self).__init__(name, func)

    def make_new_args(self, dec):
        new_settings = {a: d for a, d in self.decorator_kwargs(dec)
                        if self.func.args.is_argument(a)}
        argsnode = nodes.Arguments()
        argsnode.args = []
        argsnode.defaults = []
        argsnode.kwarg = None
        argsnode.vararg = None
        argsnode.kw_defaults = []
        argsnode.kwonlyargs = []
        old = self.func.args
        existing = list(zip_longest(reversed(old.args), reversed(old.defaults)))
        existing.reverse()
        found_defaults = False
        for arg, default in existing:
            try:
                default = new_settings.pop(arg.name)
            except KeyError:
                # we aren't trying to update this setting
                pass
            argsnode.args.append(arg)
            arg.parent = argsnode
            if default:
                found_defaults = True
                argsnode.defaults.append(default)
                default.parent = argsnode
            elif found_defaults:
                raise ValueError('Missing arguments!')
        if new_settings:
            raise ValueError('Unknown arguments: {}'.format(list(new_settings)))
        return argsnode

    def set_new_args(self, new):
        old = self.func.args
        self.func.args = new
        new.parent = self.func
        for arg in old.args:
            del arg.parent
        for default in old.defaults:
            del default.parent
        del old.parent

    def modify_function(self, dec):
        new = self.make_new_args(dec)
        self.set_new_args(new)


from linthints import SetsArgumentTransformer, AddsArgumentTransformer


def register(linter):
    pass


MANAGER.register_transform(nodes.Function, AddsArgumentTransformer('adds_arguments'))
MANAGER.register_transform(nodes.Function, SetsArgumentTransformer('sets_arguments'))

