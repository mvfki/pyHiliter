from pygments import highlight
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup
import markdown

from pyHiliter import PythonLexer, PythonConsoleLexer

def test_py(script_filename, output_html_filename='examples/test_output.html',
            template='examples/test_template.html'):
    script_text = open(script_filename, 'r').read()
    html_str = highlight(script_text, PythonConsoleLexer(), HtmlFormatter())
    output_soup = BeautifulSoup(open(template, 'r').read(),
                                features="html5lib")
    script_soup = BeautifulSoup(html_str, features="html5lib")
    output_soup.body.replaceWith(script_soup.body)
    with open(output_html_filename, 'w') as file_out:
        file_out.write(str(output_soup))
    file_out.close()

def test_md(md_filename, output_html_filename='examples/test_output.html',
            template='examples/test_template.html'):
    '''
    Be sure to carefully override the python lexer with 
    path/to/site-packages/pygments/lexers/python.py
    '''
    md_text = open(md_filename, 'r').read()
    html_str = markdown.markdown(md_text, 
        extensions=['markdown.extensions.toc',
                    'pymdownx.superfences'])
    output_soup = BeautifulSoup(open(template, 'r').read(),
                                features="html5lib")
    md_soup = BeautifulSoup(html_str, features="html5lib")
    output_soup.body.replaceWith(md_soup.body)
    with open(output_html_filename, 'w') as file_out:
        file_out.write(str(output_soup))
    file_out.close()

if __name__ == '__main__':
    test_py('examples/test_script_to_convert.py')
    #test_md('examples/test_input.md')
