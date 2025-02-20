# cgal_cython.pyx
# cython: language_level=3
from libcpp.vector cimport vector
from libcpp.pair cimport pair
import numpy as np

cdef extern from "cgal_wrapper.h":
    cdef void convex_hull_2d(const double* points, int num_points, vector[pair[double, double]]* hull)

def py_convex_hull_2d(double[:, :] points):
    cdef int num_points = points.shape[0]
    cdef const double* ptr = &points[0, 0]

    # 创建 C++ vector 来存储结果
    cdef vector[pair[double, double]] hull

    # 调用 C++ 函数
    convex_hull_2d(ptr, num_points, &hull)

    # 转换为 Python 列表
    py_hull = [(p.first, p.second) for p in hull]
    return py_hull
