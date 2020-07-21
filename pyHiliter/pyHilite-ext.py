# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 18:16:33 2020

@author: Yichen Wang

Python Markdown Module extension, using the customized Pygments lexer.
"""
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re
from .pythonLexer import EnhancedPythonLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

class PythonHighlightPreprocessor(Preprocessor):
    def __init__(self, md):
        super(PythonHighlightPreprocessor, self).__init__(md)
    def run(self, lines):
        py_blocks = []
        passed = []
        in_py_block = False
        for line in lines:
            if in_py_block:
                if re.match(r'```\s*', line):
                    in_py_block = False
                    passed.append('')
                    passed.append('MVFKIPYBLOCK')
                    passed.append('')
                else:
                    py_blocks[-1].append(line)
            else:
                if re.match(r'(?i)```(py|python|python3)\s*', line):
                    in_py_block = True
                    py_blocks.append([])
                else:
                    passed.append(line)
        for i in py_blocks:
            print(i)
        return passed

class PythonHighlightProcessor(BlockProcessor):
    """Highlight Python3 code in code blocks."""
    RE_FENCE_START = r'==py\s*\n' # start line, e.g., `   !!!! `
    RE_FENCE_END = r'\n==\s*$'  # last non-blank line, e.g, '!!!\n  \n\n'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])
        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                code_text = ''.join(blocks[0:block_num + 1])
                code_highlighted = highlight(code_text, EnhancedPythonLexer(),
                                             HtmlFormatter())
                highlighted_elements = etree.fromstring(code_highlighted)
                pre = etree.SubElement(parent, 'pre')
                #code = etree.SubElement(pre, 'code')
                #code.text = ' '
                for i in highlighted_elements[0].getchildren():
                    if i.text:
                        pre.append(i)
                print(etree.tostring(parent))
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False

class PythonHighlightExtension(Extension):
    def extendMarkdown(self, md):
        # Register instance of 'mypattern' with a priority of 20
        md.parser.blockprocessors.register(PythonHighlightProcessor(md.parser), 'pyHighlight', 81)
        md.preprocessors.register(PythonHighlightPreprocessor(md), 'pyHiPre', 26)

def makeExtension(*args, **kwargs):
    """Return extension."""
    return PythonHighlightExtension(*args, **kwargs)
