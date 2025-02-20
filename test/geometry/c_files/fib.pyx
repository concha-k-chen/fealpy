# 通过 cdef extern from 导入头文件, 写上里面的函数
cdef extern from "cfib.h":
    double cfib(int n)

# 然后 Cython 可以直接调用
def fib_with_c(n):
    """调用 C 编写的斐波那契数列"""
    return cfib(n)