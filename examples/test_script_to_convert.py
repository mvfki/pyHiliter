"""
docstring
"""
#from bar import foo
#import bar2 as b2

class myClass1 :
    """
    class docstring
    """
    def __init__(self, var1, var2=1, var3=2):
        """Initialize"""
        self.var1 = var1
        self.var2 = var2
        # random hash comment
        self.var3 = var3

    def classMethod1(self):
        """
        Returns self.var2 + 1
        """
        return self.var2 + 1

    @property
    def Var3(self, mat1, mat2):
        """
        get self.var3
        """
        mat = mat1 @ mat2
        return self.var3
