# pyHiliter - Improved Pygments PythonLexer

Since I am not really happy with [Pygments](https://pygments.org/)' lexical analysis result, and I really could not find another tool that is as easy to use as Pygments, I start this repo for improved code lexing plugins for Pygment users (myself), and bound the lexer with a Markdown extension. The improvement is mainly about adding more syntax scopes. For example, arguments function definition.  

> **What is a lexer?**  
> A program that performs lexical analysis may be termed a lexer, tokenizer, or scanner, although scanner is also a term for the first stage of a lexer. A lexer is generally combined with a parser, which together analyze the syntax of programming languages, web pages, and so forth. 
> 
> from Wikipedia

## Usage

Get the code first:  

```sh
git clone https://github.com/mvfki/pyHiliter.git
cd pyHiliter
```

To make use of the lexer, two approaches are suggested.  

#### Directly import the class

In this approach, you might want to get this package installed to your Python path, so that you can import it wherever you like.  

```sh
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

```python
'<div class="highlight"><pre><span></span><span class="kn">import</span> <span class="nn">os</span>\n<span class="n">os</span><span class="p">.</span><span class="n">path</span><span class="p">.</span><span class="nfc">join</span><span class="p">(</span><span class="s1">&#39;foo&#39;</span><span class="p">,</span> <span class="s1">&#39;bar&#39;</span><span class="p">)</span>\n</pre></div>\n'
```

#### Bundle the feature with Markdown module

Python's native Markdown module allows third-party extension to parse syntax that is not officially supported, or to do the parsing with more detail. Pygments has also been imported by extension developers. If you are using a well-developed third-party extension that imports Pygments, such as [`PyMdown Extensions`](https://facelessuser.github.io/pymdown-extensions/), but you want the Python syntax highlighting to look better (just like me). Look at this smart yet dirty solution:  

```sh
mv ${pathTo}/site-packages/pygments/lexers/python.py ${pathTo}/site-packages/pygments/lexers/python.py.old
ln -s pyHiliter/pyLexer.py {$pathTo}/site-packages/pygments/lexers/python.py
```

Yes, manually override the original Pygment Python lexer. Inspired by [@markperfectsensedigital](https://github.com/markperfectsensedigital/custom_lexers) So anytime when Pygments is invoked and the `PythonLexer` is requested, the one from this package will be found.  

**Note that** There are also other Python related lexers, such as the ones for Python console, traceback, and *etc.*. I also copied those lexers and appended them to the script, since excluding them will cause failure in parsing the corresponding language, yet no significant changes were made.  

And when using it:

```python
import markdown

md_text = "# Header\n```python\nprint('Hello', 'World', sep='!!! ', end='!!!!!!')\n```"
html_string = markdown.markdown(md_text, extensions=['pymdownx.superfences'])
```

## Improved Features

#### Python

- Function, object method, builtins being called
- Argument names in function definition
- keyword argument name in callable calling
- Inheited class in class definition
- Regex raw string
- Lambda function
- Decorator

Python2 related functionality, originally there, is fully discarded intentionally.  

#### Bash

`BashLexer` for shell scripts is also provided with improvements in some degree.  

- Dash-letter style arguments indicator
- Function definition
- `VAR=STR` style string variable assignment

A main difficulty for bash lexer is to mark up the command being executed. Intuitively, they are the first word in a basic, plain expression. But due to how the lexer is originally implemented, the division of lines are totally removed. So it is only possible to parse it correctly if I totally rewrite it. But still for the goal of highlighting a command being called, I hardcoded as many of them as I could remember. (Remind me more through [issue](https://github.com/mvfki/pyHiliter/issues/new) please!) Currently I'm simply mixing up all of them to `Name.Builtin` token category.  

**TODO**

Special syntax (a LOT) that I don't frequently use, I also need to explore more for these. Please [raise an issue](https://github.com/mvfki/pyHiliter/issues/new) if you find something is not supported properly, and sounds like a reasonable request.  

## Demonstration 

Below is a short demo script in Python. Save it to `examples/test_script_to_convert.py`.  

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

Copy-pasting it to Sublime Text editor gives you the figure on the left; running `test_py()` from `run_test.py` with `PythonLexer` from this repository outputs an HTML file at `examples/test_output.html`, where you get the screenshot in the middle; and run the function but import `PythonLexer` from `Pygments.lexers` will give you the one on the right. Then you can see how things are improved.  

![Results](examples/python_results.png)  

Note that due to my fanatic love towards Sublime Monokai theme, I'm actually using the same color schemes for multiple typs of syntax scopes, exactly as how Monokai is designed, even though they can be successfully identified as different elements. Refer to [`examples/monokai.css`](examples/monokai.css).   
