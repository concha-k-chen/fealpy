from fealpy.backend import bm
from fealpy.mesh import TriangleMesh

from datetime import datetime
import gmsh


def generate_surface_mesh(stp_file, min_size=0.1, max_size=1.0, curvature_elements=20, output_base="output"):
    """
    使用 Gmsh 生成 STP 文件的表面网格。
    - stp_file: STP 文件路径。
    - min_size: 最小网格大小（高密度）。
    - max_size: 最大网格大小（低密度）。
    - curvature_elements: 曲率自适应元素数（每 2π 弧度至少 N 个元素）。
    - output_base: 输出文件基础名。
    """
    gmsh.initialize()
    gmsh.model.add("stp_model")

    try:
        # 导入 STP 文件
        gmsh.model.occ.importShapes(stp_file)

        # 几何修复（提高鲁棒性，修复拓扑问题）
        gmsh.option.setNumber("Geometry.OCCFixDegenerated", 1)  # 修复退化边缘
        gmsh.option.setNumber("Geometry.OCCFixSmallEdges", 1)   # 修复小边缘
        gmsh.option.setNumber("Geometry.OCCFixSmallFaces", 1)   # 修复小面
        # gmsh.option.setNumber("Geometry.OCCStitching", 1)       # 缝合拓扑
        # gmsh.model.occ.healShapes(tolerance=1e-6)               # 应用修复，设置公差

        # 同步几何
        gmsh.model.occ.synchronize()

        # 检查几何实体（日志输出，便于调试）
        surfaces = gmsh.model.getEntities(2)
        curves = gmsh.model.getEntities(1)
        print(f"导入几何：{len(surfaces)} 个表面，{len(curves)} 条曲线")

        # 定义物理组（可选，用于保留壳体主要表面）
        if surfaces:
            gmsh.model.addPhysicalGroup(2, [tag for _, tag in surfaces], name="ShellSurface")

        # 设置网格密度（自定义 + 自适应）
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", max_size)
        # gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", curvature_elements)  # 自适应曲率
        # gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)              # 从边界扩展

        # 效率优化：生成四边形网格（Recombine），减少三角形
        gmsh.option.setNumber("Mesh.RecombineAll", 1)    # 重组为四边形
        gmsh.option.setNumber("Mesh.Algorithm", 6)       # 使用 Delaunay 算法，提高效率
        # gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)  # 细分优化

        # 生成表面网格（2D，只针对壳体表面）
        print("生成表面网格...")
        gmsh.model.mesh.generate(2)  # 仅生成 2D 网格

        # 优化网格质量
        gmsh.model.mesh.optimize("Netgen")  # 或 "Laplace2D" 对于表面
        gmsh.fltk.run()

        # 生成时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msh_file = f"{output_base}_{max_size}_{timestamp}.msh"
        gmsh.write(msh_file)
        print(f"表面网格生成完成，已保存到 {msh_file}")

    except Exception as e:
        print(f"错误：{e}")
    finally:
        gmsh.finalize()

if __name__ == "__main__":
    stp_file = "D:\\documents\\壳体模型\\壳体模型_2.stp"  # 替换为您的 STP 文件路径
    generate_surface_mesh(stp_file, min_size=0.05, max_size=5, curvature_elements=30, output_base='壳体模型_2')

    # tri_mesh = TriangleMesh(node, cell)
    #
    # # 可视化网格
    # import matplotlib.pyplot as plt
    #
    # fig, axes = plt.subplots()
    # tri_mesh.add_plot(axes)
    # plt.show()
    # import gmsh
    #
    # # 初始化 Gmsh
    # gmsh.initialize()
    #
    # # 创建模型
    # gmsh.model.add("shell_model")
    #
    # # 加载 .step 文件（使用 OpenCASCADE 内核）
    # gmsh.model.occ.importShapes("D:\\documents\\云泊\\四边形占优模型及参考网格\\1.stp")  # 替换为你的 .step 文件路径
    # gmsh.model.occ.synchronize()  # 同步几何到 Gmsh 模型
    #
    # # 获取几何实体（检查加载的壳体面）
    # faces = gmsh.model.getEntities(3)  # 2 表示 2D 实体（面）
    # print("Loaded faces:", faces)  # 输出格式：[(2, tag1), (2, tag2), ...]
    #
    # # 设置网格参数
    # gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 12.0)  # 最大网格尺寸（单位：模型单位，如 mm）
    # # gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 2.5)  # 最小网格尺寸
    # gmsh.option.setNumber("Mesh.Algorithm", 6)  # 2D 网格算法：6 = Frontal-Delaunay（适合壳体）
    # gmsh.option.setNumber("Mesh.RecombineAll", 1)  # 尝试生成结构化四边形网格（可选，适合壳体）
    # gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 1)  # 优化四边形重组
    #
    # # 为壳体生成 2D 网格
    # gmsh.model.mesh.generate(2)  # 2 表示生成 2D 网格
    #
    # # （可选）优化网格质量
    # # gmsh.model.mesh.optimize("Laplace")  # 使用 Laplace 平滑优化网格
    #
    # # 获取网格统计信息
    # # stats = gmsh.model.mesh.getStatistics()[0]
    # # print(f"Mesh statistics: {stats} nodes, {stats['NumElements']} elements")
    #
    # # 保存网格
    # gmsh.write("shell_model.msh")  # 保存为 .msh 格式
    # print("Mesh saved as shell_model.msh")
    #
    # # （可选）导出为其他格式（如 .vtk）
    # # gmsh.write("shell_model.vtk")
    # # print("Mesh saved as shell_model.vtk")
    #
    # # 可视化
    # gmsh.fltk.run()
    #
    # # 结束 Gmsh
    # gmsh.finalize()