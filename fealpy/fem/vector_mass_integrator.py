import numpy as np

from fealpy.fem.precomp_data import data

from .scalar_mass_integrator import ScalarMassIntegrator

class VectorMassIntegrator:
    """
    @note (c u, v)
    """    
    def __init__(self, c=None, q=None):
        self.coef = c
        self.q = q
        self.type = 'BL11'

    def assembly_cell_matrix(self, space, index=np.s_[:], cellmeasure=None, out=None):
        """
        @note 没有参考单元的组装方式
        """
        if isinstance(space, tuple): # 由标量空间组合而成的空间
            return self.assembly_cell_matrix_for_scalar_basis_vspace(space, index=index, cellmeasure=cellmeasure, out=out)
        else: # 空间基函数是向量函数
            return self.assembly_cell_matrix_for_vector_basis_vspace(space, index=index, cellmeasure=cellmeasure, out=out)

    def assembly_cell_matrix_for_vector_basis_vspace(self, space, index=np.s_[:], cellmeasure=None, out=None):
        """
        @brief 空间基函数是向量型
        """
        p = space.p
        q = self.q if self.q is not None else p+1 

        coef = self.coef
        mesh = space.mesh
        GD = mesh.geo_dimension()

        if cellmeasure is None:
            cellmeasure = mesh.entity_measure('cell', index=index)

        NC = len(cellmeasure)
        ldof = space.number_of_local_dofs() 
        if out is None:
            D = np.zeros((NC, ldof, ldof), dtype=space.ftype)
        else:
            D = out

        qf = mesh.integrator(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()
        NQ = len(ws)

        phi0 = space.basis(bcs, index=index) # (NQ, NC, ldof, GD)

        if coef is None:
            D += np.einsum('q, qcim, qcjm, c->cij', ws, phi0, phi0, cellmeasure, optimize=True)
        else:
            pass
        if out is None:
            return D

    def assembly_cell_matrix_for_scalar_basis_vspace(self, space, index=np.s_[:], cellmeasure=None, out=None):
        """
        @brief 标量空间拼成的向量空间 
        """
        
        mesh = space[0].mesh
        GD = space[0].geo_dimension()
        assert len(space) == GD
        
        mesh =space[0].mesh
        if cellmeasure is None:
            cellmeasure = mesh.entity_measure('cell', index=index)
        ldof = space[0].number_of_local_dofs()
        integrator = ScalarMassIntegrator(self.coef, self.q)
        # 组装标量的单元扩散矩阵
        # D.shape == (NC, ldof, ldof)
        D = integrator.assembly_cell_matrix(space[0], index=index, cellmeasure=cellmeasure)
        NC = len(cellmeasure)

        if out is None:
            VD = np.zeros((NC, GD*ldof, GD*ldof), dtype=space[0].ftype)
        else:
            assert out.shape == (NC, GD*ldof, GD*ldof)
            VD = out
        if space[0].doforder == 'sdofs':
            for i in range(GD):
                VD[:, i*ldof:(i+1)*ldof, i*ldof:(i+1)*ldof] += D
        elif space[0].doforder == 'vdims':
            for i in range(GD):
                VD[:, i::GD, i::GD] += D 
        if out is None:
            return VD

    def assembly_cell_matrix_for_scalar_basis_vspace_fast(self, trialspace, testspace=None, index=np.s_[:], 
            cellmeasure=None, out=None):
        """
        @brief 基于无数值积分的组装方式
        """
        coef = self.coef
        mesh = trialspace.mesh 
        meshtype = mesh.type

        TAFtype = trialspace.btype
        TAFdegree = trialspace.p
        TAFldof = trialspace.number_of_local_dofs()  
        TSFtype = TAFtype
        TSFdegree = TAFdegree
        TSFldof = TAFldof
        if testspace is not None:
            TSFtype = testspace.btype
            TSFdegree = testspace.p 
            TSFldof = testspace.number_of_local_dofs()
        Itype = self.type 
        dataindex = Itype + "_" + meshtype + "_TAF_" + TAFtype + "_" + \
                str(TAFdegree) + "_TSF_" + TSFtype + "_" + str(TSFdegree)

        if cellmeasure is None:
            if mesh.meshtype == 'UniformMesh2d':
                 NC = mesh.number_of_cells()
                 cellmeasure = np.broadcast_to(mesh.entity_measure('cell', index=index), (NC,))
            else:
                 cellmeasure = mesh.entity_measure('cell', index=index)
        
        NC = len(cellmeasure)

        if out is None:
            M = np.zeros((NC, TSFldof, TAFldof), dtype=trialspace.ftype)
        else:
            M = out
        
        if coef is None:
            M += np.einsum('c,cij->cij', cellmeasure, data[dataindex], optimize=True)
        else:
            raise ValueError("coef is not correct!")

        if out is None:
            return M
