# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 18:16:33 2020

@author: Yichen Wang

Python Markdown Module extension, using the customized Pygments lexer.
"""
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re
from .pythonLexer import EnhancedPythonLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

class PythonHighlightProcessor(BlockProcessor):
    """Highlight Python3 code in code blocks."""
    RE_FENCE_START = r'(?i)```(py|python|python3)\s*\n' # start line, e.g., `   !!!! `
    RE_FENCE_END = r'\n```\s*$'  # last non-blank line, e.g, '!!!\n  \n\n'

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
                code = etree.SubElement(pre, 'code')
                code.text = ''
                for i in highlighted_elements[0].getchildren():
                    code.append(i)
                print(etree.tostring(parent))
                print('REALLY')
                print()
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False

class PythonHighlightExtension(Extension):
    def extendMarkdown(self, md, *args):
        # Register instance of 'mypattern' with a priority of 20
        md.parser.blockprocessors.register(PythonHighlightProcessor(md.parser), 'pyHighlight', 20)

def makeExtension(*args, **kwargs):
    """Return extension."""
    return PythonHighlightExtension(*args, **kwargs)
