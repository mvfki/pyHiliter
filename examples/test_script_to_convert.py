import numpy as np
def foo(bar1, bar2, bar3=233, bar4=None):
    # Do something
    print(bar1)
    print(str(bar2) + str(bar4))

foo('hi')
np.array([[1, 2, 3], 
          [2, 3, 4]], 
          dtype=np.int)