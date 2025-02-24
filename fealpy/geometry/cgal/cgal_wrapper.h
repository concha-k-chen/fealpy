#ifndef CGAL_WRAPPER_H
#define CGAL_WRAPPER_H

#include <vector>
#include <utility> // for std::pair

#ifdef __cplusplus
extern "C" {
#endif

// 定义 C 接口函数
void convex_hull_2d(const double* points, int num_points, std::vector<std::pair<double, double>>* hull);

#ifdef __cplusplus
}
#endif

#endif