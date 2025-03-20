import pytest

from fealpy.geometry.geometry_kernel import geometry_kernel_manager as gkm

from geometry_base_data import *

class TestGeometryKernelBase:

    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_load_kernel(self, input_data, kernel):
        gkm.set_kernel(kernel)

    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_display(self, input_data, kernel):
        gkm.set_kernel(kernel)

        box1 = gkm.add_rectangle(0, 0, 0, 5, 10)
        box2 = gkm.add_rectangle(5, 5, 0, 5, 10)

        gkm.display(box1, box2, color=["blue", "red"], transpose=[0.3, 0.6])


    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_entity_construct(self, input_data, kernel):
        gkm.set_kernel(kernel)

        # 点
        p1 = gkm.add_point(0, 0, 0)
        p2 = gkm.add_point(5, 5, 0)
        p3 = gkm.add_point(10, 0, 0)
        p4 = gkm.add_point(0, 10, 0)
        # 线
        line = gkm.add_line(p1, p2)
        # 圆弧
        arc = gkm.add_arc(p1, p2, p3)
        arc2 = gkm.add_arc_center([0, 0, 0], [2, 0, 0], [-1, 0, 0])
        # 样条曲线
        ctrl_points1 = [(0, 0, 0), (2, 3, 1), (5, 4, 2), (7, 1, 3)]
        spline1 = gkm.add_spline(ctrl_points1)
        spline2 = gkm.add_spline([p1, p2, p3, p4])
        # 显示
        gkm.display(p1, p2, p3, line, arc, arc2, spline1, spline2)

    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_entity_construct2(self, input_data, kernel):
        gkm.set_kernel(kernel)

        box = gkm.add_box(2, 2, 2, 1, 1, 1)
        ellipsoid = gkm.add_ellipsoid(0, 0, 0, 5, 3, 2)
        cylinder1 = gkm.add_cylinder(0, 0, 0, 1, 4)
        cylinder2 = gkm.add_cylinder(-2, -2, -2, 1, 4, axis=(1, 0, 0))
        ring = gkm.add_ring(10, 10, 0, 1, 2)
        torus = gkm.add_torus(10, 10, 0, 10, 2)

        gkm.display(box, ellipsoid, cylinder1, cylinder2, ring, torus, color=["blue", "red", "g", 'y'])

    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_bool_operate(self, input_data, kernel):
        gkm.set_kernel(kernel)
        pass


    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_geometry_operate(self, input_data, kernel):
        gkm.set_kernel(kernel)

        box_ori = gkm.add_box(0, 0, 0, 3, 4, 5)
        box_trans = gkm.translate(box_ori, (3, 4, 5))
        box_rotation1 = gkm.rotate(box_ori, (0, 0, 0), (0, 0, 1), 3.14/2)
        box_rotation2 = gkm.rotate(box_trans, (0, 0, 0), (0, 0, 1), 3.14/2)
        box_rotation3 = gkm.rotate(box_ori, (0, 4, 0), (1, 0, 0), 3.14/4)


        gkm.display(box_ori, box_trans, box_rotation1, box_rotation2, box_rotation3,
                    color=["blue", "red", "green", "yellow", "purple"], transpose=0.5)



    @pytest.mark.parametrize("kernel", ['occ'])
    @pytest.mark.parametrize("input_data", geometry_data)
    def test_example_metalenses(self, input_data, kernel):
        gkm.set_kernel(kernel)

        ori = gkm.add_point(0, 0, 0)
        box_base = gkm.add_box(-12.5, -12.5, -0.1, 25, 25, 0.1)

        box1 = gkm.add_box(-0.12, -0.06, 0.0, 0.24, 0.12, 0.6)
        box2 = gkm.translate(box1, (0.4, 0, 0))
        box3 = gkm.translate(gkm.rotate(box1, (0, 0, 0), (0, 0, 1), 3.14/4), (0, 0.4, 0))

        total_shape = gkm.boolean_union(box_base, box1, box2, box3)


        gkm.display(ori, total_shape)












if __name__ == "__main__":
    pytest.main(["./test_geometry_base.py", "-k", "test_load_kernel"])