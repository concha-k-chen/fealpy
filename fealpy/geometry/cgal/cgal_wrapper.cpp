#include "cgal_wrapper.h"
#include <CGAL/Simple_cartesian.h>
#include <CGAL/convex_hull_2.h>

typedef CGAL::Simple_cartesian<double> K;
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
        hull->emplace_back(p.x(), p.y());
    }
}