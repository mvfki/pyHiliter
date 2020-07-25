import argparse
import shutil
import os, sys
import logging
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pyHiliter import PythonLexer as pyLexer
from pyHiliter import CssLexer as cssLexer
from pyHiliter import BashLexer as shLexer

__all__ = ['override_pygments']

PYGMENTS_PATH = pygments.__file__
SITE_PACKAGES_PATH = os.path.commonpath([__file__, PYGMENTS_PATH])
LEXERS_PATH = os.path.join(SITE_PACKAGES_PATH, 'pygments', 'lexers')

LANG = ['python', 'shell', 'css']
METAVAR = f"[{' | '.join(LANG)}]"
FILE_MAP = {'python': 'pyLexer.py', 'css': 'cssLexer.py', 
            'shell': 'shLexer.py'}
LEXER_MAP = {'python': pyLexer, 'css': cssLexer, 'shell': shLexer}

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def map_lang(alias: str, local=False) -> str:
    if alias is None:
        return None
    elif alias.lower() in {'py', 'python', 'python3'}:
        return 'python'
    elif alias.lower() in {'css'}:
        return 'css'
    elif alias.lower() in {'sh', 'shell', 'bash'}:
        return 'shell'
    else:
        if local:
            # Only mapping to lang I have
            raise ValueError(f'map_lang(): unable to identify: {alias}')
        else:
            # If not supported, can also use Pygments
            return alias

def can_override(lang: str, force: bool) -> bool:
    orig_lexer = get_lexer_by_name(lang)
    original_script_path = os.path.join(SITE_PACKAGES_PATH, 'pygments',
                                        'lexers', lang+'.py')
    if orig_lexer.__doc__.startswith('\n    pyHiliter'):
        logging.warning(f'pyHiliter {lang} lexer is already there. ')
        if not force:
            logging.warning('Use "-f" to force overriding. ')
            return False
        else:
            if os.path.exists(original_script_path+'.old'):
                logging.info(f'Force overriding {lang}.')
                return True
            else:
                logging.critical(f'Backup file for {lang} lexer not found. '
                                  'You need to reinstall Pygments. ')
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
        shutil.move(original_script_path, original_script_path+'.old')
    shutil.copy(new_lexer_path, original_script_path)
    logging.info(f"Overriding '{lang}' Done!")

def override(lang: str=None, force: bool=False) -> None:
    '''
    mv original_lexer.py original_lexer.py.old
    cp pyHiliter/new_lexer.py original_lexer.py
    lang = None, for all languages supported
    lang = ["python"|"css"|"shell"], for only one of them
    '''
    lang = map_lang(lang, True)
    if lang is None:
        check_result = [can_override(i, force) for i in LANG]
        if sum(check_result) < len(LANG):
            logging.error('Not all languages can be overridden at the time. '
                          'Choose the ones that work. ')
            sys.exit(6)
        else:
            for i in LANG:
                override_one_lang(i)
    elif can_override(lang, force):
        override_one_lang(lang)

def can_reset(lang: str) -> bool:
    original_script_path = os.path.join(SITE_PACKAGES_PATH, 'pygments',
                                        'lexers', lang+'.py')
    orig_lexer = get_lexer_by_name(lang)
    using_pyHiliter_now = orig_lexer.__doc__.startswith('\n    pyHiliter')
    if not os.path.exists(original_script_path+'.old'):
        logging.error(f'Unable to find backup for {lang}. ')
        if using_pyHiliter_now:
            logging.critical(f'While current active lexer for {lang} is from '
                              'pyHiliter. You should reinstall Pygments in '
                              'order to reset.')
        else:
            logging.info(f'While current active lexer for {lang} is not '
                          'from pyHiliter. Skipping.')
        return False
    else:
        if using_pyHiliter_now:
            return True
        else:
            logging.warning(f'Backup for {lang} found, but current active '
                              'lexer is not from pyHiliter. Skipping.')
            return False

def reset_one_lang(lang: str) -> None:
    original_script_path = os.path.join(SITE_PACKAGES_PATH, 'pygments',
                                        'lexers', lang+'.py')
    shutil.move(original_script_path+'.old', original_script_path)

def reset(lang: str=None) -> None:
    lang = map_lang(lang, True)
    if lang is None:
        for i in LANG:
            if can_reset(i):
                reset_one_lang(i)
    elif can_reset(lang):
        reset_one_lang(lang)

def convert(filename, lang=None, output=None):
    with open(filename, 'r', encoding='utf-8') as f:
        script_text = f.read()
    f.close()
    # Get lexer instance
    lang = map_lang(lang, False)
    if lang is None:
        logging.info("Languages not specified. ")
        # First look at the ext. name, if supported, still use mine.
        if '.' in filename:
            ext_name = filename.split('.')[-1]
            ext_lang = map_lang(ext_name, False)
            if ext_lang in LANG:
                logging.info(f"Using {ext_lang} lexer for extension name "
                             f"'{ext_name}'. ")
                lexer = LEXER_MAP[ext_lang]()
            else:
                try:
                    logging.info(f"Trying to use Pygments lexer for "
                                 f"extension name '{ext_name}'. ")
                    lexer = get_lexer_by_name(ext_lang)
                except Exception as e:
                    logging.warning(f"{e} occured when getting a lexer from "
                                     "Pygments with extension name "
                                     "'{ext_name}'. Directly guessing the "
                                     "language from text. ")
                    lexer = guess_lexer(script_text)
        else:
            logging.info(f"No extension name seen. Directly guessing the "
                          "language from text. ")
            lexer = guess_lexer(script_text)
    elif lang not in LANG:
        logging.warning(f"Specified language '{lang}' is not supported by "
                         "pyHiliter. Going to use Pygments. ")
        lexer = get_lexer_by_name(lang)
    else:
        # Has to be an instance not class
        lexer = LEXER_MAP[lang]()
    # Convert
    html_str = highlight(script_text, lexer, HtmlFormatter())
    if output is None:
        sys.stdout.write(html_str+'\n')
    else:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_str)
        f.close()

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
    ov_lang_group.add_argument('-l', '--lang', metavar=METAVAR, type=str,
        help='Override specified language.')
    parser_override.add_argument('-f', '--force', action='store_true',
        help='Force overriding selected lexers.')
    # For reset
    parser_reset = subparsers.add_parser('reset',
        help='Reset Pygments library to its original. Not working yet')
    rs_lang_group = parser_reset.add_mutually_exclusive_group()
    rs_lang_group.add_argument('-l', '--lang', metavar=METAVAR, type=str,
        help='Reset specified language.')
    rs_lang_group.add_argument('-a', '--all', action='store_true',
        help='Reset all languages.')
    # For Convert
    parser_convert = subparsers.add_parser('convert',
        help='Convert script file to code highlighited HTML file. ')
    parser_convert.add_argument('File', help='The script file.')
    parser_convert.add_argument('-l', '--lang', metavar=METAVAR, type=str,
        default=None, help='Language of the script being converted. If '
                           'unset, will let Pygments to guess language; '
                           'Languages other than these can also be converted '
                           'by using Pygments default lexers; If not '
                           'specified, Pygments will guess the language, but '
                           'the accuracy depends. ')
    parser_convert.add_argument('-o', '--output', metavar='FILE', type=str,
        default=None, help='The file to write the output result. By '
                               'default printed to <STDOUT>')
    
    if len(argv) == 0:
        parser.print_help()
        sys.exit(233)
    elif len(argv) == 1 and argv[0] == 'override':
        parser_override.print_help()
        sys.exit(233)
    elif len(argv) == 1 and argv[0] == 'reset':
        parser_reset.print_help()
        sys.exit(233)
    elif len(argv) == 1 and argv[0] == 'convert':
        parser_convert.print_help()
        sys.exit(233)
    args = parser.parse_args(argv)
    return args, argv[0]

def main():
    args, mode = parse_arguments(sys.argv[1:])
    if not SITE_PACKAGES_PATH.endswith('site-packages'):
        raise ModuleNotFoundError("pyHiliter and Pygments are not under the "
            "same 'site-packages' common path. You will have to manully pass "
            "where Pygments is installed.")
    if mode == 'override':
        if args.all:
            override(force=args.force)
        else:
            override(args.lang, args.force)
    elif mode == 'reset':
        if args.all:
            reset()
        else:
            reset(args.lang)
    elif mode == 'convert':
        convert(args.File, args.lang, args.output)