#!/usr/bin/python3
'''!    	
	@Author: wpx
	@File Name: press_work_integrator.py
	@Mail: wpx15673207315@gmail.com 
	@Created Time: Thu 15 Aug 2024 12:08:28 PM CST
	@bref 
	@ref 
'''  
from typing import Optional

from ..mesh import HomogeneousMesh
from ..functionspace.space import FunctionSpace as _FS
from ..utils import process_coef_func
from ..functional import bilinear_integral
from .integrator import LinearInt, OpInt, CellInt, CoefLike, enable_cache
from ..typing import TensorLike, Index, _S


class PressWorkIntegrator(LinearInt, OpInt, CellInt):
    def __init__(self, coef: Optional[CoefLike]=None, q: int=3, *,
                 index: Index=_S,
                 batched: bool=False) -> None:
        super().__init__()
        self.coef = coef
        self.q = q
        self.index = index
        self.batched = batched

    @enable_cache
    def to_global_dof(self, space: _FS) -> TensorLike:
        return space.cell_to_dof()[self.index]

    @enable_cache
    def fetch(self, space: _FS):
        space0 = space[0]
        space1 = space[1]
        index = self.index
        q = self.q
        mesh = getattr(space[0], 'mesh', None)

        if not isinstance(mesh, HomogeneousMesh):
            raise RuntimeError("The PressWorkIntegrator only support spaces on"
                               f"homogeneous meshes, but {type(mesh).__name__} is"
                               "not a subclass of HomoMesh.")

        cm = mesh.entity_measure('cell', index=index)
        qf = mesh.quadrature_formula(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()

        phi = space0.basis(bcs, index=index)
        gphi = space1.grad_basis(bcs, index=index)
        return phi, gphi, cm, bcs, ws, index

    def assembly(self, space: _FS) -> TensorLike:
        assert space[0].mesh == space[1].mesh, "The mesh should be same for two space " 
        coef = self.coef
        mesh = getattr(space[0], 'mesh', None)
        phi_0, gphi_1, cm, bcs, ws, index = self.fetch(space) 
        val = process_coef_func(coef, bcs=bcs, mesh=mesh, etype='cell', index=index)
        result = bilinear_integral(gphi_1[...,0], phi_0, ws, cm, val, batched=self.batched)
        return result


class PressWorkIntegrator1(LinearInt, OpInt, CellInt):
    def __init__(self, coef: Optional[CoefLike]=None, q: int=3, *,
                 index: Index=_S,
                 batched: bool=False) -> None:
        super().__init__()
        self.coef = coef
        self.q = q
        self.index = index
        self.batched = batched

    @enable_cache
    def to_global_dof(self, space: _FS) -> TensorLike:
        return space.cell_to_dof()[self.index]

    @enable_cache
    def fetch(self, space: _FS):
        space0 = space[0]
        space1 = space[1]
        index = self.index
        q = self.q
        mesh = getattr(space[0], 'mesh', None)

        if not isinstance(mesh, HomogeneousMesh):
            raise RuntimeError("The PressWorkIntegrator only support spaces on"
                               f"homogeneous meshes, but {type(mesh).__name__} is"
                               "not a subclass of HomoMesh.")

        cm = mesh.entity_measure('cell', index=index)
        qf = mesh.quadrature_formula(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()

        phi = space0.basis(bcs, index=index)
        gphi = space1.grad_basis(bcs, index=index)
        return phi, gphi, cm, bcs, ws, index

    def assembly(self, space: _FS) -> TensorLike:
        assert space[0].mesh == space[1].mesh, "The mesh should be same for two space " 
        coef = self.coef
        mesh = getattr(space[0], 'mesh', None)
        phi_0, gphi_1, cm, bcs, ws, index = self.fetch(space) 
        val = process_coef_func(coef, bcs=bcs, mesh=mesh, etype='cell', index=index)
        result = bilinear_integral(gphi_1[...,1], phi_0, ws, cm, val, batched=self.batched)
        return result
