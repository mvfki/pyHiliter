from setuptools import setup
import sys
from pathlib import Path

if sys.version_info.major != 3:
    raise RuntimeError('Requires Python 3')

setup(name = 'pyHiliter',
      version = '0.1',
      description = 'Better Pygments lexer and Markdown extension for Python script',
      long_description = Path('README.md').read_text('utf-8'),
      url = 'https://github.com/mvfki/pyHiliter',
      author = 'Yichen Wang',
      author_email = 'wangych@bu.edu',
      packages = ['pyHiliter'],
      package_dir = {'pyHiliter':'pyHiliter'}
      )

