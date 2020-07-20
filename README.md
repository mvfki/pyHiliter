# enhanced_Pygments_lexers

Since I am not really happy with [Pygments](https://pygments.org/)' lexical analysis result, and I really could not find another tool that is as easy to use as Pygments, I start this repo for improved code lexing plugins for Pygment users (myself). The improvement is mainly about adding more syntax scopes. For example, arguments in a Python function/method call.  

## Stages of Goals

1. Make this plugin be able to parse as many types of Python elements as Sublime Text editor can.  
2. Wrap it as a extension to Python Markdown module.  
3. Extend to other programming languages that I frequently use (and whose Pygments output I'm not satisfied with)  

## Current Achievements

Demonstration code:

```python
import numpy as np
def foo(bar1, bar2, bar3=233, bar4=None):
    # Do something
    print(bar1)
    print(str(bar2) + str(bar4))

foo('hi')
np.array([[1, 2, 3], 
          [2, 3, 4]], 
          dtype=np.int)
```

How it looks in Sublime under Monokai theme:  

[Sublime Display](examples/python_Sublime.png)

How it looks in browser after conversion by the enhanced lexer:  

[Converted Result](examples/python_demo.png)

Note that the font type and color scheme are set in external CSS file: `examples/highlight.css`.  
