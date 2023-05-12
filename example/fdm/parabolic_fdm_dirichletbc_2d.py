#!/usr/bin/env python3
# 

from typing import Callable, Tuple, Any
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve
from fealpy.pde.parabolic_2d import SinSinExpPDEData
from fealpy.mesh import UniformMesh2d


## 参数解析
parser = argparse.ArgumentParser(description=
        """
        二维均匀网格（区间）上抛物型方程的有限差分方法，
        边界条件为的带纯 Dirichlet 型，
        有三种离散格式供选择：1、向前欧拉；2、向后欧拉；3、crank_nicholson。
        """)

parser.add_argument('--nx',
        default=40, type=int,
        help="x 方向上的剖分段数，默认为 40 段.")

parser.add_argument('--ny',
        default=40, type=int,
        help="y 方向上的剖分段数，默认为 40 段.")

parser.add_argument('--nt',
        default=6400, type=int,
        help='时间剖分段数，默认为 6400 段.')

parser.add_argument('--discrete_format',
        default=1, type=int,
        help=
        """
        离散格式选择：1、向前欧拉；2、向后欧拉；3、crank_nicholson，
        使用相应的数字编号选择离散格式，默认为 1、向前欧拉格式。
        """)

parser.add_argument('--box',
        default=[0, 1, 0, 1], type=list,
        help="图像显示的范围，默认为： 0 <= x <= 1, 0 <= y <= 1")

args = parser.parse_args()

nx = args.nx
ny = args.ny
nt = args.nt
discrete_format = args.discrete_format



# PDE 模型
pde = SinSinExpPDEData()

# 空间离散
domain = pde.domain()
hx = (domain[1] - domain[0])/nx
hy = (domain[3] - domain[2])/ny
mesh = UniformMesh2d([0, nx, 0, ny], h=(hx, hy), origin=(domain[0], domain[2]))
node = mesh.node
isBdNode = mesh.ds.boundary_node_flag()

# 时间离散
duration = pde.duration()
tau = (duration[1] - duration[0])/nt 

# 准备初值
uh0 = mesh.interpolate(pde.init_solution, intertype='node') # uh0.shape = (nx+1, ny+1)

# 三种时间步进格式

def advance_forward(
        n: int, *frags: Any) -> Tuple[np.ndarray, float]:
    """
    @brief 时间步进格式为向前欧拉方法
    
    @param[in] n int, 表示第 `n` 个时间步（当前时间步） 
    """
    t = duration[0] + n*tau
    if n == 0:
        return uh0, t
    else:
        A = mesh.parabolic_operator_forward(tau)
        
        source = lambda p: pde.source(p, t + tau)
        f = mesh.interpolate(source, intertype='node')
        
        uh0.flat = A@uh0.flat + (tau*f).flat
        gD = lambda p: pde.dirichlet(p, t+tau)
        mesh.update_dirichlet_bc(gD, uh0)
        
        solution = lambda p: pde.solution(p, t + tau)
        e = mesh.error(solution, uh0, errortype='max')
        print(f"the max error is {e}")
        return uh0, t


def advance_backward(
        n: int, *frags: Any) -> Tuple[np.ndarray, float]:
    """
    @brief 时间步进格式为向后欧拉方法
    
    @param[in] n int, 表示第 `n` 个时间步（当前时间步） 
    """
    t = duration[0] + n*tau
    if n == 0:
        return uh0, t
    else:
        A = mesh.parabolic_operator_backward(tau)
        
        source = lambda p: pde.source(p, t + tau)
        f = mesh.interpolate(source, intertype='node')
        f *= tau
        f += uh0

        gD = lambda p: pde.dirichlet(p, t+tau)
        A, f = mesh.apply_dirichlet_bc(gD, A, f)
        uh0.flat = spsolve(A, f)
        
        solution = lambda p: pde.solution(p, t + tau)
        e = mesh.error(solution, uh0, errortype='max')
        print(f"the max error is {e}")
        return uh0, t

def advance_crank_nicholson(
        n: int, *frags: Any) -> Tuple[np.ndarray, float]:
    """
    @brief 时间步进格式为 CN 方法
    
    @param[in] n int, 表示第 `n` 个时间步（当前时间步） 
    """
    t = duration[0] + n*tau
    if n == 0:
        return uh0, t
    else:
        A, B = mesh.parabolic_operator_crank_nicholson(tau)
        source = lambda p: pde.source(p, t + tau)
        # f.shape = (nx+1,ny+1)
        f = mesh.interpolate(source, intertype='node') 
        f *= tau
        f.flat += B@uh0.flat
         
        gD = lambda p: pde.dirichlet(p, t+tau)
        A, f = mesh.apply_dirichlet_bc(gD, A, f)
        uh0.flat = spsolve(A, f)

        solution = lambda p: pde.solution(p, t + tau)
        e = mesh.error(solution, uh0, errortype='max')
        print(f"the max error is {e}")

        return uh0, t

if discrete_format == 1:
    dis_format = advance_forward
elif discrete_format == 2:
    dis_format = advance_backward
elif discrete_format == 3:
    dis_format = advance_crank_nicholson
else:
    raise ValueError("请选择正确的离散格式.")

fig, axes = plt.subplots()
box = args.box
mesh.show_animation(fig, axes, box, dis_format, frames=nt + 1)
plt.show()