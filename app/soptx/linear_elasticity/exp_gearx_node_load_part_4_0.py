"""
一个载荷点，不处理重心坐标，考虑外法线方向的载荷的计算
"""
from fealpy.backend import backend_manager as bm
from fealpy.functionspace import LagrangeFESpace, TensorFunctionSpace
from fealpy.sparse import COOTensor
from fealpy.fem.linear_elastic_integrator import LinearElasticIntegrator
from fealpy.material.elastic_material import LinearElasticMaterial
from fealpy.fem.bilinear_form import BilinearForm
from fealpy.fem.dirichlet_bc import DirichletBC
from fealpy.typing import TensorLike
from fealpy.solver import cg, spsolve

import pickle
from app.gearx.gear import ExternalGear, InternalGear
from app.gearx.utils import *

from fealpy.mesh import HexahedronMesh


with open('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/external_gear_data_part.pkl', 'rb') as f:
    data = pickle.load(f)

hex_mesh = data['hex_mesh']
helix_node = data['helix_node']
target_cells_idx = data['target_cell_idx']
parameters = data['parameters']
is_inner_node = data['is_inner_node']

parameter = parameters[-1]
target_cell_idx = target_cells_idx[-1]
hex_cell = hex_mesh.cell
hex_node = hex_mesh.node

mesh = HexahedronMesh(hex_node, hex_cell)

GD = mesh.geo_dimension()   
NC = mesh.number_of_cells()
NN = mesh.number_of_nodes()
node = mesh.entity('node')
cell = mesh.entity('cell')

load_values = bm.array([131.0], dtype=bm.float64) # (1, )
# cellnorm = mesh.cell_normal() # (NC, 3)
cellnorm = bm.zeros((NC, 3), dtype=bm.float64)
cellnorm[:, 1] = -1

target_cellnorm = cellnorm[target_cell_idx] # (3, )
P = bm.einsum('p,d -> pd', load_values, target_cellnorm)  # (1, 3)

u = parameter[..., 0]
v = parameter[..., 1]
w = parameter[..., 2]

bcs = (bm.tensor([[u, 1 - u]]), bm.tensor([[v, 1 - v]]), bm.tensor([[w, 1 - w]]))

space = LagrangeFESpace(mesh, p=1, ctype='C')
scalar_gdof = space.number_of_global_dofs()
tensor_space = TensorFunctionSpace(space, shape=(3, -1))
tgdof = tensor_space.number_of_global_dofs()
tldof = tensor_space.number_of_local_dofs()
cell2tdof = tensor_space.cell_to_dof()

phi_loads_array = tensor_space.basis(bcs) # (1, 1, 24, 3)

FE_load = bm.einsum('pd, cpld -> pl', P, phi_loads_array) # (1, 24)

FE = bm.zeros((NC, tldof), dtype=bm.float64)
FE[target_cell_idx, :] = FE_load[:, :] # (NC, tldof)

F = COOTensor(indices = bm.empty((1, 0), dtype=bm.int32, device=bm.get_device(space)),
            values = bm.empty((0, ), dtype=bm.float64, device=bm.get_device(space)),
            spshape = (tgdof, ))
indices = cell2tdof.reshape(1, -1)
F = F.add(COOTensor(indices, FE.reshape(-1), (tgdof, ))).to_dense() # (tgdof, )


linear_elastic_material = LinearElasticMaterial(name='E_nu', 
                                                elastic_modulus=206e3, poisson_ratio=0.3, 
                                                hypo='3D', device=bm.get_device(mesh))
lam = linear_elastic_material.lam
mu = linear_elastic_material.mu
print("lam:", lam)
print("mu:", mu)

integrator_K = LinearElasticIntegrator(material=linear_elastic_material, q=2)

KE = integrator_K.assembly(space=tensor_space)
bform = BilinearForm(tensor_space)
bform.add_integrator(integrator_K)
K = bform.assembly(format='csr')

# 矩阵和载荷向量的范数
values = K.values()
K_norm = bm.sqrt(bm.sum(values * values))
F_norm = bm.sqrt(bm.sum(F * F))   
print(f"Matrix norm before dc: {K_norm:.6f}")
print(f"Load vector norm before dc: {F_norm:.6f}")

def dirichlet(points: TensorLike) -> TensorLike:
    return bm.zeros(points.shape, dtype=points.dtype, device=bm.get_device(points))

scalar_is_bd_dof = is_inner_node
scalar_num = bm.sum(scalar_is_bd_dof)
tensor_is_bd_dof = tensor_space.is_boundary_dof(
        threshold=(scalar_is_bd_dof, scalar_is_bd_dof, scalar_is_bd_dof), 
        method='interp')
tensor_num = bm.sum(tensor_is_bd_dof)

dbc = DirichletBC(space=tensor_space, 
                    gd=dirichlet, 
                    threshold=tensor_is_bd_dof, 
                    method='interp')
K, F = dbc.apply(A=K, f=F, check=True)


# 矩阵和载荷向量的范数
values = K.values()
K_norm = bm.sqrt(bm.sum(values * values))
F_norm = bm.sqrt(bm.sum(F * F))   
print(f"Matrix norm after dc: {K_norm:.6f}")
print(f"Load vector norm after dc: {F_norm:.6f}")

# 载荷向量的范围
F_min = bm.min(F)
F_max = bm.max(F)
print(f"F min: {F_min:.6f}")
print(f"F max: {F_max:.6f}")

from fealpy import logger
logger.setLevel('INFO')

uh = tensor_space.function()
uh[:] = cg(K, F, maxiter=10000, atol=1e-8, rtol=1e-8)
# uh[:] = spsolve(K, F, solver='mumps')

# 计算残差向量和范数
residual = K.matmul(uh[:]) - F  # 使用 CSRTensor 的 matmul 方法
residual_norm = bm.sqrt(bm.sum(residual * residual))
print(f"Final residual norm: {residual_norm:.6e}")

uh = uh.reshape(GD, NN).T

mesh.nodedata['deform'] = uh[:]
mesh.to_vtk('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/gearx_part_1_node_load.vtu')
print("-----------")