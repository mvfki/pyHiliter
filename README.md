# pyHiliter 

Since I am not really happy with [Pygments](https://pygments.org/)' lexical analysis result, and I really could not find another tool that is as easy to use as Pygments, I start this repo for improved code lexing plugins for Pygment users (myself), and bound the lexer with a Markdown extension. The improvement is mainly about adding more syntax scopes. For example, arguments function definition.  

## Usage

Get the code

```shell
git clone https://github.com/mvfki/pyHiliter.git
cd pyHiliter
```

To make use of the lexer, two approaches are suggested.

#### Directly import the class

In this approach, you might want to get this package installed to your Python path, so that you can import it wherever you like.  

```shell
python setup.py install
```

And in your Python script run the following commands, which go with the most basic Pygments style.

```python
from pyHiliter import PythonLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

script_text = """
import os
os.path.join('foo', 'bar')
"""

html_string = highlight(script_text, PythonLexer(), HtmlFormatter())
```

The output will be a str, written with HTML syntax, and you can further manipulate it with your favorite HTML handler.

```
'<div class="highlight"><pre><span></span><span class="kn">import</span> <span class="nn">os</span>\n<span class="n">os</span><span class="p">.</span><span class="n">path</span><span class="p">.</span><span class="nfc">join</span><span class="p">(</span><span class="s1">&#39;foo&#39;</span><span class="p">,</span> <span class="s1">&#39;bar&#39;</span><span class="p">)</span>\n</pre></div>\n'
```

#### Bundle the feature with Markdown module

Python's native Markdown module allows third-party extension to parse syntax that is not officially supported, or to do the parsing with more detail. Pygments has also been imported by extension developers. If you are using a well-developed third-party extension that imports Pygments, such as [`PyMdown Extensions`](https://facelessuser.github.io/pymdown-extensions/), but you want the Python syntax highlighting to look better (just like me). Look at this smart yet dirty solution:  

```shell
mv ${pathTo}/site-packages/pygments/lexers/python.py ${pathTo}/site-packages/pygments/lexers/python.py.old
cp pyHiliter/pyLexer.py {$pathTo}/site-packages/pygments/lexers/python.py
```

Yes, manually override the original Pygment Python lexer. So anytime when Pygments is invoked and the `PythonLexer` is requested, the one from this package will be found. 

WARNING: the original `python.py.old` file also contains other Python related lexers, such as the ones for Python console, traceback, and *etc.*. These are not included in my implementation yet. Overriding will cause those features to be disabled.  

And when using it:

```python
import markdown

md_text = "# Header\n```python\nprint('Hello', 'World', sep='!!! ', end='!!!!!!')\n```"
html_string = markdown.markdown(md_text, extensions=['pymdownx.superfences'])
```

## Current Achievements

- Function, object method, builtins being called
- Argument names in function definition
- keyword argument name in callable calling
- Regex raw string

TODOs:

- Inheritance in class declaration
- Special syntax (a LOT) that I don't frequently use, such as "lambda function"

Demonstration code:  

```python
import re
def foo(bar1, bar2=None):
    hello_patter = r"""(?i)hel{2}[iop]\s(?#New
    line)worl.*?\b"""
    all_result = re.search(hello_patter, bar1)
    print(all_result)

text = '''Hello World!!!!'''

foo(text, bar2="not used")
```

The figure below shows how it appears to be improved.  

![Results](examples/python_results.png)  

Note that due to my fanatic love towards Sublime Monokai theme, I'm actually using the same color schemes for multiple typs of syntax scopes, exactly as how Monokai is designed, even though they can be successfully identified as different elements. Refer to [`examles/monokai.css`](examples/monokai.css).   
