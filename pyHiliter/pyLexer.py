# -*- coding: utf-8 -*-
"""
pyHiliter modified version
by Yichen Wang

    pygments.lexers.python
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexers for Python and related languages.

    :copyright: Copyright 2006-2019 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import re
from pygments.lexer import Lexer, RegexLexer, include, bygroups, default, \
words, combined, using, do_insertions
from pygments.util import get_bool_opt, shebang_matches
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Generic, Other, Error, STANDARD_TYPES
from pygments import unistring as uni

__all__ = ['PythonLexer', 'Python3Lexer', 'PythonConsoleLexer', 
           'PythonConsoleLexer', 'Python3TracebackLexer', 
           'PythonTracebackLexer', 'CythonLexer']

line_re = re.compile('.*?\n')

STANDARD_TYPES[Keyword.Argument] = 'ka'
STANDARD_TYPES[Name.Function.Called] = 'nfc'
STANDARD_TYPES[String.Regex.Bracket] = 'srb'
STANDARD_TYPES[Keyword.Lambda] = 'kl'
STANDARD_TYPES[Name.Class.Inherit] = 'nci'

class PythonLexer(RegexLexer):
    """
    pyHiliter modified version
    For `Python <http://www.python.org>`_ source code (version 3.x).
    .. versionadded:: 0.10
    .. versionchanged:: 2.5
       This is now the default ``PythonLexer``.  It is still available as the
       alias ``Python3Lexer``.

    """

    name = 'Python'
    aliases = ['python', 'py', 'sage', 'python3', 'py3']
    filenames = [
        '*.py',
        '*.pyw',
        # Jython
        '*.jy',
        # Sage
        '*.sage',
        # SCons
        '*.sc',
        'SConstruct',
        'SConscript',
        # Skylark/Starlark (used by Bazel, Buck, and Pants)
        '*.bzl',
        'BUCK',
        'BUILD',
        'BUILD.bazel',
        'WORKSPACE',
        # Twisted Application infrastructure
        '*.tac',
    ]
    mimetypes = ['text/x-python', 'application/x-python',
                 'text/x-python3', 'application/x-python3']

    flags = re.MULTILINE | re.UNICODE

    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)

    BUILTINS = words((
                    '__import__', 'abs', 'all', 'any', 'bin', 'chr', 
                    'classmethod', 'compile', 'delattr', 'dir', 'divmod', 
                    'enumerate', 'eval', 'filter', 'format', 'getattr', 
                    'globals', 'hasattr', 'hash', 'hex', 'id', 'input', 
                    'isinstance', 'issubclass', 'iter', 'len', 'locals', 
                    'map', 'max', 'min', 'next', 'oct', 'open', 'ord', 'pow', 
                    'print', 'property', 'range', 'repr', 'reversed', 'round',
                    'setattr', 'sorted', 'staticmethod', 'sum', 'super', 
                    'type', 'vars', 'zip'))

    KEYWORD_TYPES = words((
                    'bool' 'bytearray', 'bytes', 'complex', 'dict', 'float', 
                    'frozenset', 'int', 'list', 'memoryview', 'object', 'set',
                    'slice', 'str', 'tuple'))

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting (still valid in)
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsaux%]', String.Interpol),
            # the new style '{}'.format(...) string formatting
            (r'\{'
             r'((\w+)((\.\w+)|(\[[^\]]+\]))*)?'  # field name
             r'(\![sra])?'                       # conversion
             r'(\:(.?[<>=\^])?[-+ ]?#?0?(\d+)?,?(\.\d+)?[E-GXb-gnosx%]?)?'
             r'\}', String.Interpol),
            # backslashes, quotes and formatting signs must be parsed 
            # one at a time
            (r'[^\\\'"%{\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%|(\{{1,2})', ttype)
            # newlines are an error (use "nl" state)
        ]

    def fstring_rules(ttype):
        return [
            # Assuming that a '}' is the closing brace after format specifier.
            # Sadly, this means that we won't detect syntax error. But it's
            # more important to parse correct syntax correctly, than to
            # highlight invalid syntax.
            (r'\}', String.Interpol),
            (r'\{', String.Interpol, 'expr-inside-fstring'),
            # backslashes, quotes and formatting signs must be parsed 
            # one at a time
            (r'[^\\\'"{}\n]+', ttype),
            (r'[\'"\\]', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Text, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Text, String.Affix, String.Doc)),
            (r'\A#!.+$', Comment.Hashbang),
            (r'#.*$', Comment.Single),
            (r'\\\n', Text),
            (r'\\', Text),
            include('keywords'),
            # Mainly want to change scope of "def" and "class"
            (r'(def)((?:\s|\\\s)+)', bygroups(Keyword.Declaration, Text),
             'funcDef'),
            (r'(class)((?:\s|\\\s)+)', bygroups(Keyword.Declaration, Text),
             'classDef'),
            (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'fromimport'),
            (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'import'),
            include('general-expr')
        ],
        'general-expr': [
            include('expr'),
            (r',', Punctuation)
        ],
        'expr': [
            # raw f-strings
            ('(?i)(rf|fr)(""")',
             bygroups(String.Affix, String.Double.Rawf), 'tdqf'),
            ("(?i)(rf|fr)(''')",
             bygroups(String.Affix, String.Single.Rawf), 'tsqf'),
            ('(?i)(rf|fr)(")',
             bygroups(String.Affix, String.Double.Rawf), 'dqf'),
            ("(?i)(rf|fr)(')",
             bygroups(String.Affix, String.Single.Rawf), 'sqf'),
            # non-raw f-strings
            ('([fF])(""")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'tdqf')),
            ("([fF])(''')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'tsqf')),
            ('([fF])(")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'dqf')),
            ("([fF])(')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'sqf')),
            # raw strings
            ('(?i)(rb|br|r)(""")',
             bygroups(String.Affix, String.Double.Raw), 'tdqrs'),
            ("(?i)(rb|br|r)(''')",
             bygroups(String.Affix, String.Single.Raw), 'tsqrs'),
            ('(?i)(rb|br|r)(")',
             bygroups(String.Affix, String.Double.Raw), 'dqrs'),
            ("(?i)(rb|br|r)(')",
             bygroups(String.Affix.Debug, String.Single.Raw), 'sqrs'),
            # non-raw strings
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            (r'[^\S\n]+', Text),
            # pushed back '=' priority
            (r'!=|==|<<|>>|:=|[-~+/*%<>&^|]', Operator),
            (r'[:;.]', Punctuation),
            (r'\(', Punctuation, 'rbracket'),
            (r'\[', Punctuation, 'bracket'),
            (r'{', Punctuation, 'cbracket'),
            (r'(in|is|and|or|not)\b', Operator.Word),
            include('name'),
            (r'=', Operator),
            include('numbers'),
        ],
        'rbracket': [
            (r'[\s\n]+', Text),
            (r',', Punctuation),
            include('expr'),
            (r'\)', Punctuation, '#pop')
        ],
        'bracket': [
            (r'[\s\n]+', Text),
            (r',', Punctuation),
            include('expr'),
            (r'\]', Punctuation, '#pop')
        ],
        'cbracket': [
            (r'[\s\n]+', Text),
            (r',', Punctuation),
            include('expr'),
            (r'}', Punctuation, '#pop')
        ],
        'expr-inside-fstring': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            # without format specifier
            (r'(=\s*)?'         # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'     # conversion
             r'}', String.Interpol, '#pop'),
            # with format specifier
            # we'll catch the remaining '}' in the outer scope
            (r'(=\s*)?'         # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'     # conversion
             r':', String.Interpol, '#pop'),
            (r'[^\S]+', Text),  # allow new lines
            include('expr'),
        ],
        'expr-inside-fstring-inner': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            (r'[])}]', Punctuation, '#pop'),
            (r'[^\S]+', Text),  # allow new lines
            include('expr'),
        ],
        'keywords': [
            (words((
                'assert', 'async', 'await', 'break', 'continue', 'del', 
                'elif', 'else', 'except', 'finally', 'for', 'global', 'if', 
                'pass', 'raise', 'nonlocal', 'return', 'try', 'while', 
                'yield', 'yield from', 'as', 'with'), suffix=r'\b'),
             Keyword),
        ],
        #### Separate keyword of types ####
        'builtins': [
            (BUILTINS.get() + r'\b', Name.Builtin),
            (KEYWORD_TYPES.get() + r'\b', Keyword.Type),
            (r'(?<!\.)(self|Ellipsis|NotImplemented|cls)\b',
             Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'BufferError', 'BytesWarning',
                'DeprecationWarning', 'EOFError', 'EnvironmentError',
                'Exception', 'FloatingPointError', 'FutureWarning',
                'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning',
                'IndentationError', 'IndexError', 'KeyError',
                'KeyboardInterrupt', 'LookupError', 'MemoryError',
                'NameError', 'NotImplementedError', 'OSError',
                'OverflowError', 'PendingDeprecationWarning',
                'ReferenceError', 'ResourceWarning', 'RuntimeError',
                'RuntimeWarning', 'StopIteration', 'SyntaxError',
                'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError',
                'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
                'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
                'UnicodeWarning', 'UserWarning', 'ValueError', 'VMSError',
                'Warning', 'WindowsError', 'ZeroDivisionError',
                # new builtin exceptions from PEP 3151
                'BlockingIOError', 'ChildProcessError', 'ConnectionError',
                'BrokenPipeError', 'ConnectionAbortedError',
                'ConnectionRefusedError', 'ConnectionResetError',
                'FileExistsError', 'FileNotFoundError', 'InterruptedError',
                'IsADirectoryError', 'NotADirectoryError', 'PermissionError',
                'ProcessLookupError', 'TimeoutError',
                # others new in Python 3
                'StopAsyncIteration', 'ModuleNotFoundError',
                'RecursionError'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'magicfuncs': [
            (words((
                '__abs__', '__add__', '__aenter__', '__aexit__', '__aiter__',
                '__and__', '__anext__', '__await__', '__bool__', '__bytes__',
                '__call__', '__complex__', '__contains__', '__del__', 
                '__delattr__', '__delete__', '__delitem__', '__dir__', 
                '__divmod__', '__enter__', '__eq__', '__exit__', '__float__', 
                '__floordiv__', '__format__', '__ge__', '__get__', 
                '__getattr__', '__getattribute__', '__getitem__', '__gt__', 
                '__hash__', '__iadd__', '__iand__', '__ifloordiv__', 
                '__ilshift__', '__imatmul__', '__imod__', '__imul__', 
                '__index__', '__init__', '__instancecheck__', '__int__', 
                '__invert__', '__ior__', '__ipow__', '__irshift__', 
                '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__',
                '__len__', '__length_hint__', '__lshift__', '__lt__', 
                '__matmul__', '__missing__', '__mod__', '__mul__', '__ne__', 
                '__neg__', '__new__', '__next__', '__or__', '__pos__', 
                '__pow__', '__prepare__', '__radd__', '__rand__', 
                '__rdivmod__', '__repr__', '__reversed__', '__rfloordiv__', 
                '__rlshift__', '__rmatmul__', '__rmod__', '__rmul__', 
                '__ror__', '__round__', '__rpow__', '__rrshift__', 
                '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', 
                '__set__', '__setattr__', '__setitem__', '__str__', '__sub__',
                '__subclasscheck__', '__truediv__', '__xor__'), 
            suffix=r'\b'), Name.Function.Magic),
        ],
        'magicvars': [
            (words((
                '__annotations__', '__bases__', '__class__', '__closure__',
                '__code__', '__defaults__', '__dict__', '__doc__', '__file__',
                '__func__', '__globals__', '__kwdefaults__', '__module__',
                '__mro__', '__name__', '__objclass__', '__qualname__',
                '__self__', '__slots__', '__weakref__'), suffix=r'\b'),
             Name.Variable.Magic),
        ],
        'numbers': [
            (r'(\d(?:_?\d)*\.(?:\d(?:_?\d)*)?|(?:\d(?:_?\d)*)?\.\d(?:_?\d)*)'
             r'([eE][+-]?\d(?:_?\d)*)?', Number.Float),
            (r'\d(?:_?\d)*[eE][+-]?\d(?:_?\d)*j?', Number.Float),
            (r'0[oO](?:_?[0-7])+', Number.Oct),
            (r'0[bB](?:_?[01])+', Number.Bin),
            (r'0[xX](?:_?[a-fA-F0-9])+', Number.Hex),
            (r'\d(?:_?\d)*', Number.Integer),
        ],
        'name': [
            include('magicfuncs'),
            include('magicvars'),
            (words(('True', 'False', 'None'), suffix=r'\b'), 
             Keyword.Constant),
            # new matrix multiplication operator
            (r'([a-zA-Z_][\w\d_]*)(\s*)(@)', bygroups(Name, Text, Operator)),  
            (r'(@)(\s*)', bygroups(Operator, Text), 'decorator'),
            # lambda function
            ('lambda', Keyword.Lambda, 'lambda'),
            # builtin callable
            (rf"({'|'.join(BUILTINS.words)})(\()",
             bygroups(Name.Builtin, Punctuation), 'funcCallArgs', '#pop'),
            # keyword.type callable
            (rf"({'|'.join(KEYWORD_TYPES.words)})(\()",
             bygroups(Keyword.Type, Punctuation), 'funcCallArgs', '#pop'),
            include('builtins'),
            # Other callable
            (r'([a-zA-Z_][\w\d_]*)(\()',
             bygroups(Name.Function.Called, Punctuation), 'funcCallArgs'),
            (uni_name, Name),
        ],
        #### Function definition and calling ####
        'funcDef': [
            include('magicfuncs'),
            # If is magicFunc
            (r'\(', Punctuation, 'funcDefArgs', '#pop'),
            # Wrong funcname
            (r'[\d]+[\w\d_]*', Text, '#pop'),
            # Acceptable funcname
            (r'([a-zA-Z_][\w\d_]*)(\()',
             bygroups(Name.Function, Punctuation), 'funcDefArgs', '#pop')
        ],
        'funcDefArgs': [
            (r'[\s\n]+', Text),
            # For Arguments in the parenthesis of a function definition
            (r',', Punctuation),
            ## Arguments annotation
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(\:)(\s*)', 
             bygroups(Text, Keyword.Argument, Text, Punctuation, Text),
             'annotation-argument'),
            ## Keyword arguments, no annotation
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(=)(\s*)',
             bygroups(Text, Keyword.Argument, Text, Operator, Text),
             'kwargsValue'),
            ## *args, **kwargs with annotation
            (r'(\s*)(\*{1,2})([a-zA-Z_][\w\d_]*)(\s*)(\:)(\s*)',
             bygroups(Text, Operator, Keyword.Argument, Text, 
                      Punctuation, Text),
             'annotation-argument'),
            ## Positional Argument
            (r'(\s*)(\*{0,2})([a-zA-Z_][\w\d_]*)(\s*)(,*)',
             bygroups(Text, Operator, Keyword.Argument, Text, 
                      Punctuation)),
            (r'(\))(\s*)(->)(\s*)', 
             bygroups(Punctuation, Text, Punctuation, Text), 
             'annotation-return'),
            ## End of a call
            (r'\)?:', Punctuation, '#pop'),
            default('#pop')
        ],
        'annotation-argument': [
            (',', Punctuation, '#pop'),
            include('expr'),
            default('#pop')
        ],
        'annotation-return': [
            ('()(?=:)', Text, '#pop'),
            include('expr'),
        ],
        'funcCallArgs': [
            (r'[\s\n]+', Text),
            # For Arguments in the parenthesis of a function definition
            (r',', Punctuation),
            ## Keyword arguments
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(=)(\s*)',
             bygroups(Text, Keyword.Argument, Text, Operator, Text),
             'kwargsValue'),
            include('expr'),
            (r'\)', Punctuation, '#pop')
        ],
        'kwargsValue': [
            include('expr'),
            (r',', Punctuation, '#pop'),
            default('#pop')
        ],
        'lambda': [
            (':', Punctuation, 'expr'),
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(,{0,1})', 
             bygroups(Text, Keyword.Argument, Text, Punctuation))
        ],
        'classDef': [
            (r'([a-zA-Z_][\w\d_]*)(\s*)(\()', 
             bygroups(Name.Class, Text, Punctuation), 'inheritance'),
            (r'([a-zA-Z_][\w\d_]*)(\s*)(:)', 
             bygroups(Name.Class, Text, Punctuation), '#pop'),
            default('#pop')
        ],
        'inheritance': [
            (r'\):', Punctuation, '#pop'),
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(,?)', 
             bygroups(Text, Name.Class.Inherit, Text, Punctuation)),
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'\.', Name.Namespace),
            (uni_name, Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(import)\b', bygroups(Text, Keyword.Namespace), '#pop'),
            (r'\.', Name.Namespace),
            # if None occurs here, it's "raise x from None", since None can
            # never be a module name
            (r'None\b', Name.Builtin.Pseudo, '#pop'),
            (uni_name, Name.Namespace),
            default('#pop'),
        ],
        'decorator': [
            ('\n', Text, '#pop'),
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(\.)', 
             bygroups(Text, Name, Text, Punctuation)),
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(?=\n)', 
             bygroups(Text, Name.Decorator, Text))
        ],
        'fstringescape': [
            ('{{', String.Escape),
            ('}}', String.Escape),
            include('stringescape'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'fstrings-single': fstring_rules(String.Single),
        'fstrings-double': fstring_rules(String.Double),
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqf': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape), # included here for raw strings
            include('fstrings-double')
        ],
        'sqf': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape), # included here for raw strings
            include('fstrings-single')
        ],
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape), # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape), # included here for raw strings
            include('strings-single')
        ],
        'tdqf': [
            (r'"""', String.Double, '#pop'),
            include('fstrings-double'),
            (r'\n', String.Double)
        ],
        'tsqf': [
            (r"'''", String.Single, '#pop'),
            include('fstrings-single'),
            (r'\n', String.Single)
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
        #### Regex ####
        ## TODO: Merge duplicated patterns due to tdq, tsq, dq and sq string.
        # single quote raw string
        'sqrs': [
            (r"'", String.Single, '#pop'),
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex),
            (r"\\.|\.", String.Escape),
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|"
             r"\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Single.Raw),
            (r"\(\?#", Comment, 'single-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", 
                bygroups(String.Single.Raw, String.Escape)),
            (r"\[", String.Regex.Bracket, 'single-regex-bracket'),
            (r".", String.Single.Raw)
        ],
        'single-regex-bracket': [
            (r"\]", String.Regex.Bracket, '#pop'),
            (r".(?=')", String.Regex.Bracket, '#pop'),
            (r".", String.Regex.Bracket)
        ],
        'single-regex-comment': [
            (r"\)", Comment, '#pop'),
            (r".(?=')", Comment, '#pop'),
            (r".", Comment)
        ],
        # double quote raw string
        'dqrs': [
            (r'"', String.Double, '#pop'),
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex),
            (r"\\.|\.", String.Escape),
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|"
             r"\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Double.Raw),
            (r"\(\?#", Comment, 'double-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", 
                bygroups(String.Double.Raw, String.Escape)),
            (r"\[", String.Regex.Bracket, 'double-regex-bracket'),
            (r".", String.Double.Raw)
        ],
        'double-regex-bracket': [
            (r"\]", String.Regex.Bracket, '#pop'),
            (r'.(?=")', String.Regex.Bracket, '#pop'),
            (r".", String.Regex.Bracket)
        ],
        'double-regex-comment': [
            (r"\)", Comment, '#pop'),
            (r'.(?=")', Comment, '#pop'),
            (r".", Comment)
        ],
        # Triple single quote raw string
        'tsqrs': [
            (r"'''", String.Single, '#pop'),
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex),
            (r"\\.|\.", String.Escape),
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|"
             r"\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Single.Raw),
            (r"\(\?#", Comment, 'single-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", 
                bygroups(String.Single.Raw, String.Escape)),
            (r"\[", String.Regex.Bracket, 'single-regex-bracket'),
            (r".", String.Single.Raw)
        ],
        'tsingle-regex-bracket': [
            (r'[\s\n]+', Text),
            (r"\]", String.Regex.Bracket, '#pop'),
            (r".(?='{3})", String.Regex.Bracket, '#pop'),
            (r".", String.Regex.Bracket)
        ],
        'tsingle-regex-comment': [
            (r'[\s\n]+', Text),
            (r"\)", Comment, '#pop'),
            (r".(?='{3})", Comment, '#pop'),
            (r".", Comment)
        ],
        # Triple double quote raw string
        'tdqrs': [
            (r'"""', String.Double, '#pop'),
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex),
            (r"\\.|\.", String.Escape),
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|"
             r"\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Double.Raw),
            (r"\(\?#", Comment, 'double-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", 
                bygroups(String.Double.Raw, String.Escape)),
            (r"\[", String.Regex.Bracket, 'double-regex-bracket'),
            (r".", String.Double.Raw)
        ],
        'double-regex-bracket': [
            (r'[\s\n]+', Text),
            (r"\]", String.Regex.Bracket, '#pop'),
            (r'.(?="{3})', String.Regex.Bracket, '#pop'),
            (r".", String.Regex.Bracket)
        ],
        'double-regex-comment': [
            (r'[\s\n]+', Text),
            (r"\)", Comment, '#pop'),
            (r'.(?="{3})', Comment, '#pop'),
            (r".", Comment)
        ]
    }

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?(3(\.\d)?)?')

Python3Lexer = PythonLexer

class PythonConsoleLexer(Lexer):
    """
    pyHiliter modified version
    For Python console output or doctests, such as:

    .. sourcecode:: pycon

        >>> a = 'foo'
        >>> print a
        foo
        >>> 1 / 0
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ZeroDivisionError: integer division or modulo by zero

    Additional options:

    `python3`
        Use Python 3 lexer for code.  Default is ``True``.

        .. versionadded:: 1.0
        .. versionchanged:: 2.5
           Now defaults to ``True``.

    .. Python2 support disabled (Wang, Y.)
    """
    name = 'Python console session'
    aliases = ['pycon']
    mimetypes = ['text/x-python-doctest']

    def __init__(self, **options):
        Lexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        pylexer = PythonLexer(**self.options)
        tblexer = PythonTracebackLexer(**self.options)

        curcode = ''
        insertions = []
        curtb = ''
        tbindex = 0
        tb = 0
        for match in line_re.finditer(text):
            line = match.group()
            if line.startswith(u'>>> ') or line.startswith(u'... '):
                tb = 0
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, line[:4])]))
                curcode += line[4:]
            elif line.rstrip() == u'...' and not tb:
                # only a new >>> prompt can end an exception block
                # otherwise an ellipsis in place of the traceback frames
                # will be mishandled
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, u'...')]))
                curcode += line[3:]
            else:
                if curcode:
                    for item in do_insertions(
                        insertions, pylexer.get_tokens_unprocessed(curcode)):
                        yield item
                    curcode = ''
                    insertions = []
                if (line.startswith(u'Traceback (most recent call last):') or
                        re.match(u'  File "[^"]+", line \\d+\\n$', line)):
                    tb = 1
                    curtb = line
                    tbindex = match.start()
                elif line == 'KeyboardInterrupt\n':
                    yield match.start(), Name.Class, line
                elif tb:
                    curtb += line
                    if not (line.startswith(' ') or line.strip() == u'...'):
                        tb = 0
                        for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                            yield tbindex+i, t, v
                        curtb = ''
                else:
                    yield match.start(), Generic.Output, line
        if curcode:
            for item in do_insertions(insertions,
                                    pylexer.get_tokens_unprocessed(curcode)):
                yield item
        if curtb:
            for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                yield tbindex+i, t, v


class PythonTracebackLexer(RegexLexer):
    """
    pyHiliter modified version
    For Python 3.x tracebacks, with support for chained exceptions.

    .. versionadded:: 1.0

    .. versionchanged:: 2.5
       This is now the default ``PythonTracebackLexer``.  It is still 
       available as the alias ``Python3TracebackLexer``.
    """

    name = 'Python Traceback'
    aliases = ['pytb', 'py3tb']
    filenames = ['*.pytb', '*.py3tb']
    mimetypes = ['text/x-python-traceback', 'text/x-python3-traceback']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(Traceback)( \(most recent call last\):\n)', 
             bygroups(Generic.Traceback, Text), 'intb'),
            (r'^During handling of the above exception, another '
             r'exception occurred:\n\n', Generic.Traceback),
            (r'^The above exception was the direct cause of the '
             r'following exception:\n\n', Generic.Traceback),
            (r'^(?=  File "[^"]+", line \d+)', Generic.Traceback, 'intb'),
            (r'^.*\n', Other),
        ],
        'intb': [
            (r'^(  File )("[^"]+")(, line )(\d+)(, in )(.+)(\n)',
             bygroups(Text, Name.File, Text, Number.Integer, Text, 
                      Name.Function.Called, Text)),
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Text, Name.File, Text, Number.Integer, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(PythonLexer), Text)),
            (r'^([ \t]*)(\.\.\.)(\n)',
             bygroups(Text, Comment, Text)),  # for doctests...
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Error, Text, Name, Text), '#pop'),
            (r'^([a-zA-Z_]\w*)(:?\n)',
             bygroups(Generic.Error, Text), '#pop')
        ],
    }


Python3TracebackLexer = PythonTracebackLexer

class CythonLexer(RegexLexer):
    """
    pyHiliter modified version
    For Pyrex and `Cython <http://cython.org>`_ source code.

    .. versionadded:: 1.1
    """

    name = 'Cython'
    aliases = ['cython', 'pyx', 'pyrex']
    filenames = ['*.pyx', '*.pxd', '*.pxi']
    mimetypes = ['text/x-cython', 'application/x-cython']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)("""(?:.|\n)*?""")', bygroups(Text, String.Doc)),
            (r"^(\s*)('''(?:.|\n)*?''')", bygroups(Text, String.Doc)),
            (r'[^\S\n]+', Text),
            (r'#.*$', Comment),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'(in|is|and|or|not)\b', Operator.Word),
            (r'(<)([a-zA-Z0-9.?]+)(>)',
             bygroups(Punctuation, Keyword.Type, Punctuation)),
            (r'!=|==|<<|>>|[-~+/*%=<>&^|.?]', Operator),
            (r'(from)(\d+)(<=)(\s+)(<)(\d+)(:)',
             bygroups(Keyword, Number.Integer, Operator, Name, Operator,
                      Name, Punctuation)),
            include('keywords'),
            (r'(def|property)(\s+)', bygroups(Keyword, Text), 'funcname'),
            (r'(cp?def)(\s+)', bygroups(Keyword, Text), 'cdef'),
            # (should actually start a block with only cdefs)
            (r'(cdef)(:)', bygroups(Keyword, Punctuation)),
            (r'(class|struct)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)(\s+)', bygroups(Keyword, Text), 'fromimport'),
            (r'(c?import)(\s+)', bygroups(Keyword, Text), 'import'),
            include('builtins'),
            include('backtick'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"""', String, 'tdqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'''", String, 'tsqs'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"', String, 'dqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'", String, 'sqs'),
            ('[uU]?"""', String, combined('stringescape', 'tdqs')),
            ("[uU]?'''", String, combined('stringescape', 'tsqs')),
            ('[uU]?"', String, combined('stringescape', 'dqs')),
            ("[uU]?'", String, combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (words((
                'assert', 'break', 'by', 'continue', 'ctypedef', 'del', 
                'elif', 'else', 'except', 'except?', 'exec', 'finally', 'for',
                'fused', 'gil', 'global', 'if', 'include', 'lambda', 'nogil', 
                'pass', 'print', 'raise', 'return', 'try', 'while', 'yield', 
                'as', 'with'), suffix=r'\b'),
             Keyword),
            (r'(DEF|IF|ELIF|ELSE)\b', Comment.Preproc),
        ],
        'builtins': [
            (words((
                '__import__', 'abs', 'all', 'any', 'apply', 'basestring', 
                'bin', 'bool', 'buffer', 'bytearray', 'bytes', 'callable', 
                'chr', 'classmethod', 'cmp', 'coerce', 'compile', 'complex', 
                'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 
                'execfile', 'exit', 'file', 'filter', 'float', 'frozenset', 
                'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 'input',
                'int', 'intern', 'isinstance', 'issubclass', 'iter', 'len', 
                'list', 'locals', 'long', 'map', 'max', 'min', 'next', 
                'object', 'oct', 'open', 'ord', 'pow', 'property', 'range', 
                'raw_input', 'reduce', 'reload', 'repr', 'reversed', 'round', 
                'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 
                'sum', 'super', 'tuple', 'type', 'unichr', 'unicode', 
                'unsigned', 'vars', 'xrange', 'zip'), 
             prefix=r'(?<!\.)', suffix=r'\b'), Name.Builtin),
            (r'(?<!\.)(self|None|Ellipsis|NotImplemented|False|True|NULL'
             r')\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'DeprecationWarning', 'EOFError', 
                'EnvironmentError', 'Exception', 'FloatingPointError', 
                'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError', 
                'ImportWarning', 'IndentationError', 'IndexError', 'KeyError',
                'KeyboardInterrupt', 'LookupError', 'MemoryError', 
                'NameError', 'NotImplemented', 'NotImplementedError', 
                'OSError', 'OverflowError', 'OverflowWarning', 
                'PendingDeprecationWarning', 'ReferenceError', 'RuntimeError',
                'RuntimeWarning', 'StandardError', 'StopIteration', 
                'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 
                'TabError', 'TypeError', 'UnboundLocalError', 
                'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 
                'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 
                'ValueError', 'Warning', 'ZeroDivisionError'), 
             prefix=r'(?<!\.)', suffix=r'\b'), Name.Exception),
        ],
        'numbers': [
            (r'(\d+\.?\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'0\d+', Number.Oct),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+', Number.Integer)
        ],
        'backtick': [
            ('`.*?`', String.Backtick),
        ],
        'name': [
            (r'@\w+', Name.Decorator),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'funcname': [
            (r'[a-zA-Z_]\w*', Name.Function, '#pop')
        ],
        'cdef': [
            (r'(public|readonly|extern|api|inline)\b', Keyword.Reserved),
            (r'(struct|enum|union|class)\b', Keyword),
            (r'([a-zA-Z_]\w*)(\s*)(?=[(:#=]|$)',
             bygroups(Name.Function, Text), '#pop'),
            (r'([a-zA-Z_]\w*)(\s*)(,)',
             bygroups(Name.Function, Text, Punctuation)),
            (r'from\b', Keyword, '#pop'),
            (r'as\b', Keyword),
            (r':', Punctuation, '#pop'),
            (r'(?=["\'])', Text, '#pop'),
            (r'[a-zA-Z_]\w*', Keyword.Type),
            (r'.', Text),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'[a-zA-Z_][\w.]*', Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(c?import)\b', bygroups(Text, Keyword), '#pop'),
            (r'[a-zA-Z_.][\w.]*', Name.Namespace),
            # ``cdef foo from "header"``, or ``for foo from 0 < i < 10``
            default('#pop'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings': [
            (r'%(\([a-zA-Z0-9]+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String)
            # newlines are an error (use "nl" state)
        ],
        'nl': [
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape), 
            include('strings')
        ],
        'sqs': [
            (r"'", String, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape), 
            include('strings')
        ],
        'tdqs': [
            (r'"""', String, '#pop'),
            include('strings'),
            include('nl')
        ],
        'tsqs': [
            (r"'''", String, '#pop'),
            include('strings'),
            include('nl')
        ],
    }

class DgLexer(RegexLexer):
    """
    pyHiliter modified version
    Lexer for `dg <http://pyos.github.com/dg>`_,
    a functional and object-oriented programming language
    running on the CPython 3 VM.

    .. versionadded:: 1.6
    """
    name = 'dg'
    aliases = ['dg']
    filenames = ['*.dg']
    mimetypes = ['text/x-dg']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'#.*?$', Comment.Single),

            (r'(?i)0b[01]+', Number.Bin),
            (r'(?i)0o[0-7]+', Number.Oct),
            (r'(?i)0x[0-9a-f]+', Number.Hex),
            (r'(?i)[+-]?[0-9]+\.[0-9]+(e[+-]?[0-9]+)?j?', Number.Float),
            (r'(?i)[+-]?[0-9]+e[+-]?\d+j?', Number.Float),
            (r'(?i)[+-]?[0-9]+j?', Number.Integer),

            (r"(?i)(br|r?b?)'''", String, 
             combined('stringescape', 'tsqs', 'string')),
            (r'(?i)(br|r?b?)"""', String, 
             combined('stringescape', 'tdqs', 'string')),
            (r"(?i)(br|r?b?)'", String, 
             combined('stringescape', 'sqs', 'string')),
            (r'(?i)(br|r?b?)"', String, 
             combined('stringescape', 'dqs', 'string')),

            (r"`\w+'*`", Operator),
            (r'\b(and|in|is|or|where)\b', Operator.Word),
            (r'[!$%&*+\-./:<-@\\^|~;,]+', Operator),

            (words((
                'bool', 'bytearray', 'bytes', 'classmethod', 'complex', 
                'dict', 'dict\'', 'float', 'frozenset', 'int', 'list', 
                'list\'', 'memoryview', 'object', 'property', 'range', 'set', 
                'set\'', 'slice', 'staticmethod', 'str', 'super', 'tuple', 
                'tuple\'', 'type'),
             prefix=r'(?<!\.)', suffix=r'(?![\'\w])'), Name.Builtin),
            (words((
                '__import__', 'abs', 'all', 'any', 'bin', 'bind', 'chr', 
                'cmp', 'compile', 'complex', 'delattr', 'dir', 'divmod', 
                'drop', 'dropwhile', 'enumerate', 'eval', 'exhaust', 'filter',
                'flip', 'foldl1?', 'format', 'fst', 'getattr', 'globals', 
                'hasattr', 'hash', 'head', 'hex', 'id', 'init', 'input', 
                'isinstance', 'issubclass', 'iter', 'iterate', 'last', 'len',
                'locals', 'map', 'max', 'min', 'next', 'oct', 'open', 'ord', 
                'pow', 'print', 'repr', 'reversed', 'round', 'setattr', 
                'scanl1?', 'snd', 'sorted', 'sum', 'tail', 'take', 
                'takewhile', 'vars', 'zip'),
             prefix=r'(?<!\.)', suffix=r'(?![\'\w])'), Name.Builtin),
            (r"(?<!\.)(self|Ellipsis|NotImplemented|None|True|False)"
             r"(?!['\w])", Name.Builtin.Pseudo),

            (r"(?<!\.)[A-Z]\w*(Error|Exception|Warning)'*(?!['\w])",
             Name.Exception),
            (r"(?<!\.)(Exception|GeneratorExit|KeyboardInterrupt|"
             r"StopIteration|SystemExit)(?!['\w])", Name.Exception),

            (r"(?<![\w.])(except|finally|for|if|import|not|otherwise|raise|"
             r"subclass|while|with|yield)(?!['\w])", Keyword.Reserved),

            (r"[A-Z_]+'*(?!['\w])", Name),
            (r"[A-Z]\w+'*(?!['\w])", Keyword.Type),
            (r"\w+'*", Name),

            (r'[()]', Punctuation),
            (r'.', Error),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'string': [
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String),
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop')
        ],
        'sqs': [
            (r"'", String, '#pop')
        ],
        'tdqs': [
            (r'"""', String, '#pop')
        ],
        'tsqs': [
            (r"'''", String, '#pop')
        ],
    }
