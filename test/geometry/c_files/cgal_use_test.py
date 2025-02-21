from cgal_cython import py_convex_hull_2d, py_collinear_2d

from fealpy.backend import backend_manager as bm
from fealpy.mesh import TriangleMesh
bm.set_backend('pytorch')

# points = bm.array([
#     [0, 0], [1, 1], [2, 2], [3, 3],
#     [1, 0], [0, 1], [2, 1], [5, 4]
# ], dtype=bm.float64)
#
# hull = py_convex_hull_2d(points)
# print("凸包顶点坐标：", hull)
#
# points2 = bm.array([
#     [0, 0],
#     [1, 1],
#     [2, 2]
# ], dtype=bm.float64)
#
# is_collinear = py_collinear_2d(points2)
# print("是否共线：", is_collinear)


a = bm.array([
    [0, 0],
    [1, 1],
    [2, 2]
], dtype=bm.float64)

b = bm.astype(a, bm.int64)
print(b)



