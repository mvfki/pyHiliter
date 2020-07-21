from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup
import markdown

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

def test_md(md_filename, output_html_filename='examples/test_output.html', template='examples/test_template.html'):
    md_text = open(md_filename, 'r').read()
    html_str = markdown.markdown(md_text, 
        extensions=['markdown.extensions.toc', 
                    'enhanced_pygments_lexers.pyHighlight',
                    'pymdownx.tilde',
                    'pymdownx.superfences'])
    output_soup = BeautifulSoup(open(template, 'r').read(), features="html5lib")
    md_soup = BeautifulSoup(html_str, features="html5lib")
    output_soup.body.replaceWith(md_soup.body)
    with open(output_html_filename, 'w') as file_out:
        file_out.write(str(output_soup))
    file_out.close()

if __name__ == '__main__':
    #test_py('examples/test_script_to_convert.py')
    test_md('examples/test_input.md')