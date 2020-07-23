from setuptools import setup, find_packages
from pathlib import Path
import sys

if sys.version_info.major != 3:
    raise RuntimeError('Requires Python 3')

setup(name = 'pyHiliter',
      version = '0.1',
      description = 'Some of improved Pygments lexers',
      long_description = Path('README.md').read_text('utf-8'),
      url = 'https://github.com/mvfki/pyHiliter',
      author = 'Yichen Wang',
      author_email = 'wangych@bu.edu',
      packages = find_packages(), 
      package_dir = {'pyHiliter':'pyHiliter'},
      entry_points ={'console_scripts': ['pyHiliter = pyHiliter.__main__:main']}
      )

