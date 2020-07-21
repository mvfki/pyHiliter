import re

from pygments.lexer import RegexLexer, include, bygroups, default, words, \
combined
from pygments.util import get_bool_opt, shebang_matches
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Generic, Other, Error, STANDARD_TYPES
from pygments import unistring as uni

__all__ = ['PythonLexer', 'Python3Lexer']

line_re = re.compile('.*?\n')

STANDARD_TYPES[Keyword.Argument] = 'ka'
STANDARD_TYPES[Name.Function.Called] = 'nfc'
STANDARD_TYPES[String.Regex.Bracket] = 'srb'
STANDARD_TYPES[Keyword.Lambda] = 'kl'

class PythonLexer(RegexLexer):
    """
    For `Python <http://www.python.org>`_ source code (version 3.x).
    .. versionadded:: 0.10
    .. versionchanged:: 2.5
       This is now the default ``PythonLexer``.  It is still available as the
       alias ``Python3Lexer``.

    .. Modified by Yichen Wang, Jul, 2020.
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
             bygroups(Text, Keyword.Argument.One, Text, Punctuation, Text),
             'annotation-argument'),
            ## Keyword arguments, no annotation
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(=)(\s*)',
             bygroups(Text, Keyword.Argument.Two, Text, Operator, Text),
             'kwargsValue'),
            ## *args, **kwargs with annotation
            (r'(\s*)(\*{1,2})([a-zA-Z_][\w\d_]*)(\s*)(\:)(\s*)',
             bygroups(Text, Operator, Keyword.Argument.StarAnn, Text, Punctuation, Text),
             'annotation-argument'),
            ## Positional Argument
            (r'(\s*)(\*{0,2})([a-zA-Z_][\w\d_]*)(\s*)(,*)',
             bygroups(Text, Operator, Keyword.Argument.Three, Text, Punctuation)),
            (r'(\))(\s*)(->)(\s*)', 
             bygroups(Punctuation, Text, Punctuation.Arrow, Text), 'annotation-return'),
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
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(\.)', bygroups(Text, Name, Text, Punctuation)),
            (r'(\s*)([a-zA-Z_][\w\d_]*)(\s*)(?=\n)', bygroups(Text, Name.Decorator, Text))
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
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex), # things like \12 \z \b | *
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
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex), # things like \12 \z \b | *
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
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex), # things like \12 \z \b | *
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