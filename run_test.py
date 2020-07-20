from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup

from enhanced_pygments_lexers import EnhancedPythonLexer

def test_py(script_filename, output_html_filename='examples/test_output.html'):
    code = open(script_filename, 'r').read()
    html = highlight(code, EnhancedPythonLexer(), HtmlFormatter())
    with open(output_html_filename, 'r') as file_in:
        template = file_in.read()
    file_in.close()
    out = BeautifulSoup(template, features="html5lib")
    out.body.replaceWith(BeautifulSoup(html, features="html5lib").div)
    with open(output_html_filename, 'w') as file_out:
        file_out.write(str(out))
    file_out.close()

if __name__ == '__main__':
    test_py('examples/test_script_to_convert.py')