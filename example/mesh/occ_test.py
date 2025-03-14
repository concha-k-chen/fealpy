from OCC.Display.SimpleGui import init_display


def add_rectangle(x: float, y: float, z: float, dx: float, dy: float):
    """
    创建一个矩形
    Parameters
    ----------
    x: float 矩形左下角x坐标
    y: float 矩形左下角y坐标
    z: float 矩形左下角z坐标
    dx: float 矩形宽度
    dy: float 矩形高度

    Returns
    -------
    OCC 格式的面
    """
    from OCC.Core.gp import gp_Pnt
    from OCC.Core.GC import GC_MakeSegment
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge
    # 定义矩形的四个顶点
    p1 = gp_Pnt(x, y, z)  # 左下角坐标
    p2 = gp_Pnt(x+dx, y, z)  # 右下角
    p3 = gp_Pnt(x+dx, y+dy, z)  # 右上角
    p4 = gp_Pnt(x, y+dy, z)  # 左上角

    # 创建边线（Edge）并添加到线框（Wire）
    wire_builder = BRepBuilderAPI_MakeWire()
    # 底边：p1 -> p2
    edge1 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p1, p2).Value()).Edge()
    wire_builder.Add(edge1)
    # 右边：p2 -> p3
    edge2 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p2, p3).Value()).Edge()
    wire_builder.Add(edge2)
    # 顶边：p3 -> p4
    edge3 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p3, p4).Value()).Edge()
    wire_builder.Add(edge3)
    # 左边：p4 -> p1
    edge4 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p4, p1).Value()).Edge()
    wire_builder.Add(edge4)

    # 生成面
    return BRepBuilderAPI_MakeFace(wire_builder.Wire()).Face()

def add_disk(xc: float, yc: float, zc: float, rx: float, ry: float):
    """
    创建一个椭圆
    Parameters
    ----------
    xc: float 椭圆圆心 x 坐标
    yc: float 椭圆圆心 y 坐标
    zc: float 椭圆圆心 z 坐标
    rx: float 椭圆 x 半径
    ry: float 椭圆 y 半径

    Returns
    -------

    """
    from math import pi
    from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
    from OCC.Core.Geom import Geom_Ellipse
    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_MakeEdge,
        BRepBuilderAPI_MakeWire,
        BRepBuilderAPI_MakeFace,
    )
    # 1. 定义椭圆坐标系（XY平面，Z方向为法向）
    ellipse_axis = gp_Ax2(
        gp_Pnt(xc, yc, zc),  # 圆心位置
        gp_Dir(0, 0, 1)     # 法线方向（Z轴）
    )

    # 2. 创建椭圆几何体
    geom_ellipse = Geom_Ellipse(ellipse_axis, rx, ry)

    # 3. 生成完整椭圆边（角度范围 0~2π）
    edge = BRepBuilderAPI_MakeEdge(geom_ellipse, 0, 2*pi).Edge()

    # 4. 构建闭合线框
    wire = BRepBuilderAPI_MakeWire(edge).Wire()

    # 5. 生成面
    return BRepBuilderAPI_MakeFace(wire).Face()

def add_circle(xc: float, yc: float, zc: float, r: float):
    """
    创建一个圆
    Parameters
    ----------
    xc: float 圆心 x 坐标
    yc: float 圆心 y 坐标
    zc: float 圆心 z 坐标
    r: float 圆半径

    Returns
    -------

    """
    return add_disk(xc, yc, zc, r, r)

def cut(entity1, entity2):
    """
    对两个实体进行切割
    Parameters
    ----------
    entity1: OCC 实体
    entity2: OCC 实体

    Returns
    -------

    """
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
    return BRepAlgoAPI_Cut(entity1, entity2).Shape()


if __name__ == '__main__':
    # 初始化图形界面（自动选择可用后端，如qt或wx）
    # display, start_display, add_menu, add_function = init_display()
    #
    # # 创建 box
    # box1 = add_rectangle(0, 0, 0, 10, 10)
    # # box2 = add_rectangle(10, 20, 1, 15, 25)
    # # # 显示模型并设置颜色
    # # display.DisplayShape(box1, color="blue")
    # # display.DisplayShape(box2, color="red")
    #
    # # 创建椭圆
    # # disk = add_disk(0, 0, 0, 10, 5)
    # circle = add_circle(5, 5, 0, 2.5)
    # # # 显示模型并设置颜色
    # # display.DisplayShape(disk, color="blue")
    # # display.DisplayShape(circle, color="red")
    # cut_result = cut(box1, circle)
    # display.DisplayShape(cut_result, color="green")
    #
    # # 启动交互窗口
    # start_display()

    from fealpy.geometry.geometry_kernel import geometry_kernel_manager as gkm
    gkm.set_kernel("occ")

