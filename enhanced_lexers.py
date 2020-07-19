# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 00:08:35 2020

@author: Yichen Wang
"""
from pygments.lexer import bygroups, words, combined, include, default
from pygments.lexers import PythonLexer
from pygments.token import *
from pygments import unistring as uni
# For running a test
from pygments import highlight
from pygments.formatters import HtmlFormatter


STANDARD_TYPES[Keyword.Argument] = 'ka'

class EnhancedPythonLexer(PythonLexer):
    tokens = PythonLexer.tokens
    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)
    tokens['name'] = [
        (r'(@)([a-zA-Z_][\w\d_]*)', bygroups(Operator, Name.Decorator)),
        (r'@', Operator),  # new matrix multiplication operator
        (uni_name, Name),
    ]
    tokens['root'] = [
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
        (r'(def)((?:\s|\\\s)+)', bygroups(Keyword.Declaration, Text), 'funcDec'),
        (r'(class)((?:\s|\\\s)+)', bygroups(Keyword.Declaration, Text), 'classname'),
        (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
         'fromimport'),
        (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
         'import'),
        include('expr'),
    ]
    tokens['funcDec'] = [
        include('magicfuncs'),
        include('keywords'),
        include('numbers'),
        (r',', Punctuation),
        # Wrong funcname
        (r'[\d]+[\w\d_]*', Text),
        # Acceptable funcname
        (r'([a-zA-Z_][\w\d_]*)(\()', bygroups(Name.Function, Punctuation)),
        # Keyword Argument
        (r'(\s*)([\w\d_]+)(\s*)(=)(\s*)', bygroups(Text, Keyword.Argument, Text, Operator, Text)),
        # Positional Argument
        (r'(\s*)([\w\d_]+)(\s*)(,*)', bygroups(Text, Keyword.Argument, Text, Punctuation)),
        (r'\)', Punctuation, '#pop')
    ]

if __name__ == '__main__':
    code = '''
@property
def hello(bar1, bar2=2, bar3=23):
    if not bar1:
        print('not bar1')
    elif bar2 is None:
        print("bar2 None")
    return bar1

a = a.foo(23)
'''
    print(highlight(code, EnhancedPythonLexer(), HtmlFormatter()))