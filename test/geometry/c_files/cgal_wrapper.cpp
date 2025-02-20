#include "cgal_wrapper.h"
#include <CGAL/Simple_cartesian.h>
#include <CGAL/convex_hull_2.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
//
typedef CGAL::Exact_predicates_exact_constructions_kernel K;
//typedef CGAL::Simple_cartesian<double> K;
typedef K::Point_2 Point_2;

void convex_hull_2d(const double* points, int num_points, std::vector<std::pair<double, double>>* hull) {
    std::vector<Point_2> cgal_points;
    for (int i = 0; i < num_points; ++i) {
        cgal_points.push_back(Point_2(points[2*i], points[2*i + 1]));
    }

    std::vector<Point_2> cgal_hull;
    CGAL::convex_hull_2(cgal_points.begin(), cgal_points.end(), std::back_inserter(cgal_hull));

    hull->clear();
    for (const auto& p : cgal_hull) {
        hull->emplace_back(CGAL::to_double(p.x()), CGAL::to_double(p.y()));
    }
}

bool collinear_2d(const double* points){
    Point_2 p1(points[0], points[1]);
    Point_2 p2(points[2], points[3]);
    Point_2 p3(points[4], points[5]);
    return CGAL::collinear(p1, p2, p3);
}