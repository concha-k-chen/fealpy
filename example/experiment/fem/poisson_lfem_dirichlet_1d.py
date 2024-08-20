import ipdb
import argparse
from matplotlib import pyplot as plt

from fealpy.experimental import logger
logger.setLevel('WARNING')

from fealpy.experimental.backend import backend_manager as bm
from fealpy.experimental.mesh import TriangleMesh
from fealpy.experimental.mesh import QuadrangleMesh
from fealpy.experimental.mesh import IntervalMesh
from fealpy.experimental.mesh import HexahedronMesh
from fealpy.experimental.mesh import TetrahedronMesh
from fealpy.experimental.functionspace import LagrangeFESpace
from fealpy.experimental.fem import BilinearForm, ScalarDiffusionIntegrator
from fealpy.experimental.fem import LinearForm, ScalarSourceIntegrator
from fealpy.experimental.fem import DirichletBC
from fealpy.experimental.solver.conjugate_gradient import cg

from fealpy.experimental.pde.poisson_1d import CosData 
from fealpy.utils import timer




## 参数解析
parser = argparse.ArgumentParser(description=
        """
        任意次有限元方法求解possion方程
        """)

parser.add_argument('--degree',
        default=1, type=int,
        help='Lagrange 有限元空间的次数, 默认为 1 次.')

parser.add_argument('--n',
        default=4, type=int,
        help='初始网格剖分段数.')

parser.add_argument('--maxit',
        default=4, type=int,
        help='默认网格加密求解的次数, 默认加密求解 4 次')

parser.add_argument('--backend',
        default='numpy', type=str,
        help='默认后端为numpy')

parser.add_argument('--meshtype',
        default='int', type=str,
        help='默认网格为区间网格')

args = parser.parse_args()


bm.set_backend(args.backend)
p = args.degree
n = args.n
meshtype = args.meshtype
maxit = args.maxit

tmr = timer()
next(tmr)
pde = CosData() 
# 三角形网格
if meshtype == 'tri':
    mesh = TriangleMesh.from_box([0,1,0,1], n, n)
# 区间网格
elif meshtype == 'int':
    mesh = IntervalMesh.from_interval_domain([0,1], n)
# 四边形网格
elif meshtype == 'quad':
    mesh = QuadrangleMesh.from_box([0,1,0,1], n, n)
# 六面体网格
elif meshtype == 'hexa':
    mesh = HexahedronMesh.from_box([0,1,0,1,0,1], n, n, n)
# 四面体网格
elif meshtype == 'tet':
    mesh = TetrahedronMesh.from_box([0,1,0,1,0,1], n, n, n)
else: 
    raise ValueError(f"Unsupported : {meshtype} mesh")

errorType = ['$|| u - u_h||_{\\Omega,0}$']
errorMatrix = bm.zeros((1, maxit), dtype=bm.float64)
tmr.send('网格和pde生成时间')


for i in range(maxit):
    space= LagrangeFESpace(mesh, p=p)
    tmr.send(f'第{i}次空间时间') 

    ipdb.set_trace()
    uh = space.function() # 建立一个有限元函数

    bform = BilinearForm(space)
    bform.add_integrator(ScalarDiffusionIntegrator())
    lform = LinearForm(space)
    lform.add_integrator(ScalarSourceIntegrator(pde.source))
    
    A = bform.assembly()
    F = lform.assembly()
    tmr.send(f'第{i}次矩组装时间') 

    gdof = space.number_of_global_dofs()
    A, F = DirichletBC(space, gd = pde.solution).apply(A, F)
    tmr.send(f'第{i}次边界处理时间') 

    uh[:] = cg(A, F, maxiter=5000, atol=1e-14, rtol=1e-14)
    tmr.send(f'第{i}次求解器时间') 
    
    errorMatrix[0, i] = mesh.error(pde.solution, uh)
    
    if i < maxit-1:
        mesh.uniform_refine(n=1)
    tmr.send(f'第{i}次误差计算及网格加密时间') 
next(tmr)
print("最终误差",errorMatrix)
print("order : ", bm.log2(errorMatrix[0,:-1]/errorMatrix[0,1:]))