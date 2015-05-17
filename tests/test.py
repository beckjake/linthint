import sys
sys.path.append('./tests')
from pylint.lint import PyLinter
from pylint.reporters import CollectingReporter
from pylint import interfaces
from pylint import utils
from logilab.common import interface
from lint_target.test_bad_args import get_stmts
from astroid.builder import AstroidBuilder
from astroid import MANAGER


class TestLinter(PyLinter):
    """A test linter that lints strings."""
    def __init__(self):
        super(TestLinter, self).__init__()
        self.load_default_plugins()
        self.load_plugin_modules(['linthints'])
        self.error_mode()

    def lint_string(self, to_lint):
        """A lot of this is copy+pasted from PyLinter."""
        ast_node = AstroidBuilder(MANAGER).string_build(to_lint)

        walker = utils.PyLintASTWalker(self)
        _checkers = self.prepare_checkers()
        tokencheckers = [c for c in _checkers
                         if interface.implements(c, interfaces.ITokenChecker)
                         and c is not self]
        rawcheckers = [c for c in _checkers
                       if interface.implements(c, interfaces.IRawChecker)]
        # notify global begin
        for checker in _checkers:
            checker.open()
            if interface.implements(checker, interfaces.IAstroidChecker):
                walker.add_checker(checker)

        self.set_current_module('<module>')
        self.file_state = utils.FileState('<stmt>')
        self._ignore_file = False
        # fix the current file (if the source file was not available or
        # if it's actually a c extension)
        self.current_file = ast_node.file # pylint: disable=maybe-no-member

        self.check_astroid_module(ast_node, walker, rawcheckers, tokencheckers)

    def check_stmt(self, stmt, success):
        """Check a single statement. Expect no messages if success is True,
        or messages if success is False.
        """
        self.reporter = CollectingReporter()
        self.lint_string(stmt)
        messages = self.reporter.messages
        if success:
            assert not messages, 'Got linter messages: {}'.format(messages)
        else:
            assert messages, 'Got no linter messages'
            for msg in messages:
                assert msg.symbol == 'unexpected-keyword-arg', \
                    'Unexpected error: {}'.format(msg)
                assert "'notanarg'" in msg.msg, \
                    'Unexpected error: {}'.format(msg)



def main(linter=None, verbose=False):
    """Do things"""
    if linter is None:
        linter = TestLinter()
    for stmt, success in get_stmts():
        if verbose:
            print('{}: {}'.format(stmt, success))
        linter.check_stmt(stmt, success)

if __name__ == '__main__':
    main(verbose=('-v' in sys.argv[1:]))
