from setuptools import setup
import sys
from pathlib import Path

if sys.version_info.major != 3:
    raise RuntimeError('Requires Python 3')

setup(name = 'enhanced_pygments_lexers',
      version = '0.1',
      description = 'Pygments lexers that with more scopes on popular languages',
      long_description = Path('README.md').read_text('utf-8'),
      url = 'https://github.com/mvfki/enhanced_pygments_lexers',
      author = 'Yichen Wang',
      author_email = 'wangych@bu.edu',
      packages = ['enhanced_pygments_lexers'],
      package_dir = {'enhanced_pygments_lexers':'enhanced_pygments_lexers'}
      )

