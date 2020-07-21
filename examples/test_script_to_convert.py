import os
class myClass(str, object):
    '''Docstring'''
    def __init__(self, *args, **kwargs):
        super(myClass, self).__init__(*args, **kwargs)

a = myClass()
print(isinstance(a, str))