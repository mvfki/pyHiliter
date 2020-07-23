import argparse
import shutil
import os, sys
import pygments
from pygments.lexers import get_lexer_by_name
import importlib

__all__ = ['override_pygments']

PYGMENTS_PATH = pygments.__file__
SITE_PACKAGES_PATH = os.path.commonpath([__file__, PYGMENTS_PATH])
LEXERS_PATH = os.path.join(SITE_PACKAGES_PATH, 'pygments', 'lexers')

LANG = {'python', 'css', 'shell'}
FILE_MAP = {'python': 'pyLexer.py', 'css': 'cssLexer.py', 
            'shell': 'shLexer.py'}
def map_lang(alias: str) -> str:
    if alias is None:
        return None
    elif alias.lower() in {'py', 'python', 'python3'}:
        return 'python'
    elif alias.lower() in {'css'}:
        return 'css'
    elif alias.lower() in {'sh', 'shell', 'bash'}:
        return 'shell'
    else:
        raise ValueError(f'Unable to identify: {alias}')

def can_override(lang: str, force: bool) -> bool:
    orig_lexer = get_lexer_by_name(lang)
    original_script_path = os.path.join(SITE_PACKAGES_PATH, 'pygments',
                                        'lexers', lang+'.py')
    if orig_lexer.__doc__.startswith('\n    pyHiliter'):
        if not force:
            sys.stderr.write(f'pyHiliter {lang} lexer is already there. '
                              'Use "-f" to force overriding. \n')
            return False
        else:
            if os.path.exists(original_script_path+'.old'):
                return True
            else:
                sys.stderr.write(f'Backup file for {lang} lexer not found. '
                                  'You need to reinstall Pygments. \n')
                return False
    else:
        return True

def override_one_lang(lang: str):
    original_script_path = os.path.join(SITE_PACKAGES_PATH, 'pygments',
                                        'lexers', lang+'.py')
    new_lexer_path = os.sep.join(__file__.split(os.sep)[:-1] + \
                                 [FILE_MAP[lang]])
    if not os.path.exists(original_script_path+'.old'):
        # Back up already there, directly overwrite '.py', in case that in a
        # forced state old code are gone
        os.rename(original_script_path, original_script_path+'.old')
    shutil.copy(new_lexer_path, original_script_path)
    sys.stdout.write('Done!\n')

def override(lang: str=None, force: bool=False) -> None:
    '''
    mv original_lexer.py original_lexer.py.old
    cp pyHiliter/new_lexer.py original_lexer.py
    lang = None, for all languages supported
    lang = ["python"|"css"|"shell"], for only one of them
    '''
    if not SITE_PACKAGES_PATH.endswith('site-packages'):
        raise ModuleNotFoundError("pyHiliter and Pygments are not under the "
            "same 'site-packages' common path. You will have to manully pass "
            "where Pygments is installed.")
    lang = map_lang(lang)
    if lang is None:
        check_result = [can_override(i, force) for i in LANG]
        if sum(check_result) < len(LANG):
            sys.exit(6)
        else:
            for i in LANG:
                override_one_lang(i)
    elif can_override(lang, force):
        override_one_lang(lang)

def parse_arguments(argv: list):
    parser = argparse.ArgumentParser(
        description='pyHiliter - for some improved Pygments lexers',
    )
    subparsers = parser.add_subparsers(help='Subcommands')
    # For override
    parser_override = subparsers.add_parser('override', 
        help='Override original Pygments lexers with improved ones.'
    )
    ov_lang_group = parser_override.add_mutually_exclusive_group()
    ov_lang_group.add_argument('-a', '--all', action='store_true', 
        help='Override all I have.')
    ov_lang_group.add_argument('-l', '--lang', metavar='str', type=str,
        help='Override specified language.')
    parser_override.add_argument('-f', '--force', action='store_true',
        help='Force overriding selected lexers.')
    # For reset
    parser_reset = subparsers.add_parser('reset',
        help='Reset Pygments library to its original. Not working yet')
    parser_reset.add_argument('-l', '--lang', metavar='str', type=str,
        help='Reset specified language.')
    if len(argv) == 0:
        parser.print_help()
        sys.exit(233)
    elif len(argv) == 1 and argv[0] == 'override':
        parser_override.print_help()
        sys.exit(233)
    elif len(argv) == 1 and argv[0] == 'reset':
        parser_reset.print_help()
        sys.exit(233)
    args = parser.parse_args(argv)
    return args, argv[0]

def main():
    args, mode = parse_arguments(sys.argv[1:])
    if mode == 'override':
        if args.all:
            override(force=args.force)
        else:
            override(args.lang, args.force)