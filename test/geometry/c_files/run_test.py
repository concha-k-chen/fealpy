# import wrapper_cfib
# import time
#
#
# def fib(n):
#     if n < 2:
#         return n
#     a = 1
#     b = 1
#     for i in range(2, n):
#         a, b = b, a + b
#     return b
#
#
# started_time1 = time.time()
# print(wrapper_cfib.fib_with_c(90))
# ended_time1 = time.time()
# print("Time elapsed: ", ended_time1 - started_time1)
#
# started_time2 = time.time()
# print(fib(90))
# ended_time2 = time.time()
# print("Time elapsed: ", ended_time2 - started_time2)
from torch.onnx.symbolic_opset11 import linalg_det

from fealpy.backend import backend_manager as bm
from fealpy.mesh import IntervalMesh
import numpy as np
from fealpy.solver import spsolve
# bm.set_backend('numpy')


print(-1)
