#!/usr/bin/env python3
#

import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse.linalg import spsolve
import pyamg

from fealpy.pde.poisson_2d import LShapeRSinData
from fealpy.functionspace import LagrangeFiniteElementSpace
from fealpy.boundarycondition import DirichletBC

from fealpy.mesh.adaptive_tools import mark
from fealpy.tools.show import showmultirate


pde = LShapeRSinData()
mesh = pde.init_mesh(n=4, meshtype='tri')

theta = 0.3
maxit = 30
p = 1
errorType = ['$|| u - u_h||_{0}$',
             '$||\\nabla u - \\nabla u_h||_{0}$',
             '$||\\nabla u - G(\\nabla u_h)||_{0}$']

NDof = np.zeros((maxit,), dtype=np.int_)
errorMatrix = np.zeros((len(errorType), maxit), dtype=np.float64)

mesh.add_plot(plt)
plt.savefig('/home/why/test-0.png')
plt.close()

for i in range(maxit):
    print('step:', i)
    space = LagrangeFiniteElementSpace(mesh, p=p)
    A = space.stiff_matrix()
    F = space.source_vector(pde.source)

    NDof[i] = space.number_of_global_dofs()
    bc = DirichletBC(space, pde.dirichlet) 

    uh = space.function()
    A, F = bc.apply(A, F, uh)
    uh[:] = spsolve(A, F)

    rguh = space.grad_recovery(uh)

    errorMatrix[0, i] = space.integralalg.L2_error(pde.solution, uh)
    errorMatrix[1, i] = space.integralalg.L2_error(pde.gradient, uh.grad_value)  
    errorMatrix[2, i] = np.sqrt(np.sum(eta**2))

    if i < maxit - 1:
        isMarkedCell = mark(eta, theta=theta)
        mesh.bisect(isMarkedCell)
        mesh.add_plot(plt)
        plt.savefig('/home/why/test-' + str(i+1) + '.png')
        plt.close()

fig = plt.figure()
axes = fig.gca()
mesh.add_plot(axes)
showmultirate(plt, maxit - 15, NDof, errorMatrix, errorType)
plt.show()
