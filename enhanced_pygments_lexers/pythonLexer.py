# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 00:08:35 2020

@author: Yichen Wang
"""
from pygments.lexer import bygroups, words, combined, include, default
from pygments.lexers import PythonLexer
from pygments.token import *
from pygments import unistring as uni

STANDARD_TYPES[Keyword.Argument] = 'ka'
STANDARD_TYPES[Name.Function.Called] = 'nfc'
STANDARD_TYPES[String.Regex.Bracket] = 'srb'

class EnhancedPythonLexer(PythonLexer):
    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)
    BUILTINS = words((
                    '__import__', 'abs', 'all', 'any', 'bin', 'bool', 
                    'bytearray', 'bytes', 'chr', 'classmethod', 'compile', 
                    'complex', 'delattr', 'dict', 'dir', 'divmod', 
                    'enumerate', 'eval', 'filter', 'format', 'frozenset', 
                    'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 
                    'input', 'isinstance', 'issubclass', 'iter', 'len', 
                    'locals', 'map', 'max', 'memoryview', 'min', 'next', 
                    'object', 'oct', 'open', 'ord', 'pow', 'print', 
                    'property', 'range', 'repr', 'reversed', 'round', 'set', 
                    'setattr', 'slice', 'sorted', 'staticmethod', 'sum', 
                    'super', 'type', 'vars', 'zip'))
    KEYWORD_TYPES = words(('int', 'float', 'str', 'list', 'set', 'tuple'))
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
             'classname'),
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
        'name': [
            include('expr-keywords'),
            include('magicfuncs'),
            include('magicvars'),
            (r'(@)([a-zA-Z_][\w\d_]*)', bygroups(Operator, Name.Decorator)),
            (r'@', Operator),  # new matrix multiplication operator
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
            ## Keyword arguments
            (r'(\s*)([\w\d_]+)(\s*)(=)(\s*)', 
             bygroups(Text, Keyword.Argument, Text, Operator, Text), 
             'kwargsValue'),
            ## Positional Argument
            (r'(\s*)([\w\d_]+)(\s*)(,*)', 
             bygroups(Text, Keyword.Argument, Text, Punctuation)),
            ## End of a call
            (r'\):', Punctuation, '#pop')
        ],
        'funcCallArgs': [
            (r'[\s\n]+', Text),
            # For Arguments in the parenthesis of a function definition
            (r',', Punctuation),
            ## Keyword arguments
            (r'(\s*)([\w\d_]+)(\s*)(=)(\s*)', 
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
        #### Regex ####
        ## TODO: Merge duplicated patterns due to tdq, tsq, dq and sq string.
        # single quote raw string
        'sqrs': [
            (r"'", String.Single, '#pop'),
            (r"\\\d{1,2}|\\[AZzBb]", String.Regex), # things like \12 \z \b | *
            (r"\\.|\.", String.Escape),
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Single.Raw),
            (r"\(\?#", Comment, 'single-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", bygroups(String.Single.Raw, String.Escape)),
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
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Double.Raw),
            (r"\(\?#", Comment, 'double-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", bygroups(String.Double.Raw, String.Escape)),
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
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Single.Raw),
            (r"\(\?#", Comment, 'single-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", bygroups(String.Single.Raw, String.Escape)),
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
            (r"\{\d+\}|\{\d+,\d+\}|[|*^$+?*]|\(\?[iLmsux]+\)|\(\?P=[_a-zA-Z0-9]+\)", String.Regex),
            (r"\(\?:", String.Double.Raw),
            (r"\(\?#", Comment, 'double-regex-comment'),
            (r"(\()(\?\!|\?\<\!|\?\=|\?\<\=)", bygroups(String.Double.Raw, String.Escape)),
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
        ],
    }
