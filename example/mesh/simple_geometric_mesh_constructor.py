import math
import matplotlib.pyplot as plt
import gmsh
from fealpy.backend import backend_manager as bm
from fealpy.mesh import TriangleMesh


def simple_geometric_mesh_constructor(box: list = None,
                                      holes: list[list] = None,
                                      rectangles: list[list] = None,
                                      notches: list[list] = None,
                                      lc: float = 0.05,
                                      itype=None, ftype=None, device=None):
    """
    使用 Gmsh 创建简单的几何网格，包括矩形区域、圆形孔洞、矩形孔洞和切口。

    Parameters:
        box(list): 矩形区域的边界框，格式为 [xmin, xmax, ymin, ymax]。

        holes(list[list]): 圆形孔洞的列表，每个孔洞为 [x, y, r]，
        列表中每个元素为[圆形孔洞圆心x坐标，圆形孔洞圆心y坐标，圆形孔洞半径]，默认不输入。

        rectangles(list[list]): 矩形孔洞的列表，每个孔洞为 [xmin, xmax, ymin, ymax]，
        列表中每个元素为[矩形孔洞左下角x坐标，矩形孔洞右上角x坐标，矩形孔洞左下角y坐标，矩形孔洞右上角y坐标]，默认不输入。

        notches(list[list]): 切口的列表，每个切口为 [sx, sy, ex, ey]，
        列表中每个元素为[切口起点x坐标，切口起点y坐标，切口终点x坐标，切口终点y坐标]，默认不输入。

        lc(float): 网格特征长度，用于控制网格细化程度，默认为 0.05。

    Returns:
        TriangleMesh: 生成的三角形网格。
    """
    if box is None:
        box = [0, 1, 0, 1]
    if itype is None:
        itype = bm.int64
    if ftype is None:
        ftype = bm.float64

    gmsh.initialize()
    # 创建主矩形区域
    main_rect = gmsh.model.occ.addRectangle(box[0], box[2], 0, box[1] - box[0], box[3] - box[2])
    gmsh.model.occ.synchronize()

    # 初始化工具形状列表（包含孔洞和切口）
    tool_shapes = []

    # 处理圆形孔洞
    if holes:
        for h in holes:
            x, y, r = h
            circle = gmsh.model.occ.addDisk(x, y, 0, r, r)
            tool_shapes.append((2, circle))

    # 处理矩形孔洞
    if rectangles:
        for r in rectangles:
            xmin, xmax, ymin, ymax = r
            rect = gmsh.model.occ.addRectangle(xmin, ymin, 0, xmax - xmin, ymax - ymin)
            tool_shapes.append((2, rect))

    # 处理切口（转换为极窄矩形孔洞）
    epsilon = 5e-4  # 切口宽度控制参数
    if notches:
        for notch in notches:
            sx, sy, ex, ey = notch
            dx = ex - sx
            dy = ey - sy
            length = math.hypot(dx, dy)
            if length < 1e-6:  # 忽略零长度切口
                continue
            # 计算切口法线方向
            nx = -dy / length * epsilon / 2
            ny = dx / length * epsilon / 2
            # 创建四个顶点
            points = [
                (sx - nx, sy - ny),
                (ex - nx, ey - ny),
                (ex + nx, ey + ny),
                (sx + nx, sy + ny)
            ]
            # OpenCASCADE 方式创建多边形
            p_tags = [gmsh.model.occ.addPoint(x, y, 0) for x, y in points]
            # 创建边
            edges = []
            for i in range(4):
                edges.append(gmsh.model.occ.addLine(p_tags[i], p_tags[(i + 1) % 4]))
            # 创建闭合线环
            wire = gmsh.model.occ.addWire(edges)
            # 创建面
            face = gmsh.model.occ.addPlaneSurface([wire])
            tool_shapes.append((2, face))

    # 执行布尔差集操作（一次性处理所有孔洞和切口）
    if tool_shapes:
        main_part = gmsh.model.occ.cut([(2, main_rect)], tool_shapes)
        if main_part[0]:
            main_rect = main_part[0][0][1]
        gmsh.model.occ.synchronize()

    # 设置网格参数（切口附近细化）
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)

    # 生成网格
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)

    # 显示网格
    # gmsh.fltk.run()

    # 读取网格节点与单元
    # 获取所有节点信息
    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
    node_tags = bm.array(node_tags)
    node_coords = bm.array(node_coords, dtype=ftype, device=device)
    node = node_coords.reshape((-1, 3))[:, :2]
    # 节点编号映射
    nodetags_map = dict({int(j): i for i, j in enumerate(node_tags)})
    # 获取单元信息
    cell_type = 2  # 三角形单元的类型编号为 2
    cell_tags, cell_connectivity = gmsh.model.mesh.getElementsByType(cell_type)
    # 节点编号映射到单元
    evid = bm.array([nodetags_map[int(j)] for j in cell_connectivity], dtype=itype, device=device)
    cell = evid.reshape((cell_tags.shape[-1], -1))

    gmsh.finalize()
    return TriangleMesh(node, cell)


if __name__ == "__main__":
    # 示例参数
    params = {
        "box": [0, 1, 0, 2],
        "holes": [[0.2, 1.8, 0.1], [0.2, 0.2, 0.1], [0.5, 1, 0.2]],
        "rectangles": [[0.7, 1.0, 1.7, 2.0], [0.4, 0.7, 1.84, 1.86]],
        "notches": [[0.8, 0.2, 1.0, 0.2], [0.5, 0.2, 0.5, 0.0]],
        "lc": 0.05
    }

    mesh = simple_geometric_mesh_constructor(**params)

    fig, axes = plt.subplots()
    mesh.add_plot(axes)
    plt.show()
