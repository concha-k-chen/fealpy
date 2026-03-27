import pytest

from fealpy.backend import backend_manager as bm
from fealpy.mesh import TetrahedronMesh
from fealpy.mesher import ElbowPipeRemesher


class TestElbowPipeRemesher:
    @pytest.mark.parametrize("backend", ["numpy"])
    def test_validate_parameters_mapping(self, backend):
        bm.set_backend(backend)
        params = {
            "D": 25.0,
            "bend_angle": 90.0,
            "R_bend_inner": 1.5,
            "L_in_ratio": 5.0,
            "L_out_ratio": 10.0,
            "wall_thickness": 5.0,
            "mesh_size_global": 1.0,
            "mesh_size_bend": 0.8,
            "mesh_size_interface": 0.6,
        }
        internal = ElbowPipeRemesher.validate_parameters(params)
        assert internal["inner_diameter"] == pytest.approx(25.0)
        assert internal["outer_radius"] == pytest.approx(17.5)
        assert internal["bend_radius_centerline"] == pytest.approx(50.0)
        assert internal["straight_inlet_length"] == pytest.approx(125.0)
        assert internal["straight_outlet_length"] == pytest.approx(250.0)

    @pytest.mark.parametrize("backend", ["numpy"])
    def test_init_mesh_returns_tetra_with_region(self, backend):
        bm.set_backend(backend)
        remesher = ElbowPipeRemesher(
            {
                "D": 1.0,
                "bend_angle": 90.0,
                "R_bend_inner": 1.5,
                "L_in_ratio": 1.5,
                "L_out_ratio": 1.5,
                "wall_thickness": 0.2,
                "mesh_size_global": 0.6,
                "mesh_size_bend": 0.5,
                "mesh_size_interface": 0.4,
            }
        )
        mesh = remesher.init_mesh()
        assert isinstance(mesh, TetrahedronMesh)
        assert "region" in mesh.celldata
        assert mesh.celldata["region"].shape[0] == mesh.cell.shape[0]

    @pytest.mark.parametrize("backend", ["numpy"])
    def test_mesh_data_contract(self, backend):
        bm.set_backend(backend)
        remesher = ElbowPipeRemesher(
            {
                "D": 1.0,
                "bend_angle": 60.0,
                "R_bend_inner": 1.5,
                "L_in_ratio": 1.5,
                "L_out_ratio": 1.5,
                "wall_thickness": 0.2,
                "mesh_size_global": 0.6,
                "mesh_size_bend": 0.5,
                "mesh_size_interface": 0.4,
            }
        )
        mesh_data = remesher.mesh_data()
        expected_keys = {
            "node",
            "tetra",
            "tetra_region",
            "boundary_tri",
            "boundary_tri_marker",
            "interface_tri",
            "interface_adjacent_tet",
            "interface_adjacent_region",
            "physical_name_to_dimtag",
            "physical_dimtag_to_name",
        }
        assert set(mesh_data.keys()) == expected_keys
