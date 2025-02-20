from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp cimport bool

# cython: language_level=3
cdef extern from "cgal_wrapper.h":
    # 计算输入点的凸包
    cdef void convex_hull_2d(const double* points, int num_points, void* hull)

    # 判断输入的三点是否共线
    cdef bool collinear_2d(const double* points)


def py_convex_hull_2d(double[:, :] points):
    cdef int num_points = points.shape[0]
    cdef const double* ptr = &points[0, 0]

    # 调用 C++ 函数
    cdef vector[pair[double, double]] hull
    convex_hull_2d(ptr, num_points, &hull)

    # 转换为 Python 列表
    py_hull = []
    for p in hull:
        py_hull.append((p.first, p.second))
    return py_hull

def py_collinear_2d(double[:, :] points):
    cdef const double * ptr = &points[0, 0]
    is_linear = collinear_2d(ptr)
    return is_linear

