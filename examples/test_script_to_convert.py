import re
def foo(bar1, bar2=None):
    hello_patter = r"""(?i)hel{2}[iop]\s(?#New
    line)worl.*?\b"""
    all_result = re.search(hello_patter, bar1)
    print(all_result)

text = '''Hello World!!!!'''

foo(text, bar2="not used")
