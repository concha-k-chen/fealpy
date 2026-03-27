from __future__ import annotations

from math import sqrt
from typing import Dict

from ..backend import backend_manager as bm
from .gmsh_fsi_pipe_mesher import BaseGmshFSIPipeMesher, build_dimtag_maps


class ElbowPipeRemesher(BaseGmshFSIPipeMesher):
    """FSI elbow pipe remesher based on gmsh OCC geometry and FEALPy mesh output."""

    @staticmethod
    def default_parameters():
        return {
            "D": 25.0,
            "bend_angle": 90.0,
            "R_bend_inner": 1.5,
            "L_in_ratio": 5.0,
            "L_out_ratio": 10.0,
            "wall_thickness": 5.0,
            "mesh_size_global": None,
            "mesh_size_bend": None,
            "mesh_size_interface": None,
        }

    @classmethod
    def validate_parameters(cls, params):
        defaults = cls.default_parameters()
        unknown_keys = sorted(set(params) - set(defaults))
        if unknown_keys:
            raise ValueError(f"unknown parameter keys: {unknown_keys}")

        raw = {**defaults, **params}
        D = float(raw["D"])
        bend_angle = float(raw["bend_angle"])
        R_bend_inner_ratio = float(raw["R_bend_inner"])
        L_in_ratio = float(raw["L_in_ratio"])
        L_out_ratio = float(raw["L_out_ratio"])
        wall_thickness = float(raw["wall_thickness"])

        if D <= 0.0:
            raise ValueError("D must be > 0")
        if wall_thickness <= 0.0:
            raise ValueError("wall_thickness must be > 0")
        if R_bend_inner_ratio <= 0.0:
            raise ValueError("R_bend_inner must be > 0 (ratio to D)")
        if L_in_ratio <= 0.0:
            raise ValueError("L_in_ratio must be > 0")
        if L_out_ratio <= 0.0:
            raise ValueError("L_out_ratio must be > 0")
        if not 0.0 < bend_angle < 180.0:
            raise ValueError("bend_angle must be between 0 and 180 degrees")

        default_sizes = {
            "mesh_size_global": 0.3 * D,
            "mesh_size_bend": 0.2 * D,
            "mesh_size_interface": 0.15 * D,
        }
        mesh_size_global = default_sizes["mesh_size_global"] if raw["mesh_size_global"] is None else float(raw["mesh_size_global"])
        mesh_size_bend = default_sizes["mesh_size_bend"] if raw["mesh_size_bend"] is None else float(raw["mesh_size_bend"])
        mesh_size_interface = default_sizes["mesh_size_interface"] if raw["mesh_size_interface"] is None else float(raw["mesh_size_interface"])
        if mesh_size_global <= 0.0 or mesh_size_bend <= 0.0 or mesh_size_interface <= 0.0:
            raise ValueError("mesh_size_global/mesh_size_bend/mesh_size_interface must be > 0")

        inner_diameter = D
        outer_radius = D / 2.0 + wall_thickness
        R_bend_inner = R_bend_inner_ratio * D
        if R_bend_inner <= wall_thickness:
            raise ValueError("R_bend_inner * D must be greater than wall_thickness")
        return {
            "inner_diameter": inner_diameter,
            "outer_radius": outer_radius,
            "wall_thickness": wall_thickness,
            "bend_radius_centerline": R_bend_inner + D / 2.0,
            "straight_inlet_length": L_in_ratio * D,
            "straight_outlet_length": L_out_ratio * D,
            "bend_angle_deg": bend_angle,
            "mesh_size_global": mesh_size_global,
            "mesh_size_bend": mesh_size_bend,
            "mesh_size_interface": mesh_size_interface,
        }

    def __init__(self, params=None, gmsh_module=None):
        external = self.default_parameters() if params is None else dict(params)
        internal = self.validate_parameters(external)
        super().__init__(internal, gmsh_module=gmsh_module)
        self.external_params = external
        self.internal_params = internal

    @classmethod
    def from_remesher_parameters(cls, params=None, gmsh_module=None):
        return cls(params=params, gmsh_module=gmsh_module)

    def model_name(self) -> str:
        return "fealpy_elbow_pipe_remesher"

    def _centerline_points(self, params):
        r = float(params["bend_radius_centerline"])
        inlet = float(params["straight_inlet_length"])
        outlet = float(params["straight_outlet_length"])
        bend_angle_rad = float(params["bend_angle_deg"]) * float(bm.pi) / 180.0

        sin_a = float(bm.sin(bend_angle_rad))
        cos_a = float(bm.cos(bend_angle_rad))
        bend_end = (r * sin_a, r * (1.0 - cos_a), 0.0)
        end = (
            bend_end[0] + outlet * cos_a,
            bend_end[1] + outlet * sin_a,
            0.0,
        )
        start = (-inlet, 0.0, 0.0)
        bend_start = (0.0, 0.0, 0.0)
        bend_center = (0.0, r, 0.0)
        return start, bend_start, bend_center, bend_end, end

    def _build_centerline_wire(self, gmsh_module, params):
        occ = gmsh_module.model.occ
        start, bend_start, bend_center, bend_end, end = self._centerline_points(params)
        p0 = occ.addPoint(*start)
        p1 = occ.addPoint(*bend_start)
        pc = occ.addPoint(*bend_center)
        p2 = occ.addPoint(*bend_end)
        p3 = occ.addPoint(*end)
        c0 = occ.addLine(p0, p1)
        c1 = occ.addCircleArc(p1, pc, p2)
        c2 = occ.addLine(p2, p3)
        return occ.addWire([c0, c1, c2])

    def _build_pipe_volume_from_wire(self, gmsh_module, radius, params, wire):
        occ = gmsh_module.model.occ
        start, _, _, _, _ = self._centerline_points(params)
        profile = occ.addDisk(
            start[0], start[1], start[2],
            float(radius), float(radius),
            zAxis=[1.0, 0.0, 0.0],
            xAxis=[0.0, 1.0, 0.0],
        )
        return occ.addPipe([(2, profile)], wire)[0]

    def build_fsi_volumes(self, gmsh_module, params):
        occ = gmsh_module.model.occ
        wire = self._build_centerline_wire(gmsh_module, params)
        fluid = self._build_pipe_volume_from_wire(gmsh_module, params["inner_diameter"] / 2.0, params, wire)
        outer = self._build_pipe_volume_from_wire(gmsh_module, params["outer_radius"], params, wire)
        solid = occ.cut([outer], [fluid], removeObject=True, removeTool=False)[0][0]
        fragment = occ.fragment([fluid], [solid])
        return {"fluid": fragment[1][0][0], "solid": fragment[1][1][0]}

    def _surface_center(self, gmsh_module, surface_dimtag):
        return gmsh_module.model.occ.getCenterOfMass(*surface_dimtag)

    def _surface_matches_point(self, gmsh_module, surface_dimtag, point, tol):
        center = self._surface_center(gmsh_module, surface_dimtag)
        bbox = gmsh_module.model.occ.getBoundingBox(*surface_dimtag)
        bbox_center = (
            0.5 * (bbox[0] + bbox[3]),
            0.5 * (bbox[1] + bbox[4]),
            0.5 * (bbox[2] + bbox[5]),
        )
        dist_center = sqrt((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2 + (center[2] - point[2]) ** 2)
        dist_bbox = sqrt((bbox_center[0] - point[0]) ** 2 + (bbox_center[1] - point[1]) ** 2 + (bbox_center[2] - point[2]) ** 2)
        return min(dist_center, dist_bbox) <= tol

    def _surface_boundary_count(self, gmsh_module, surface_dimtag):
        return len(gmsh_module.model.getBoundary([surface_dimtag], oriented=False, recursive=False))

    def _pick_smallest_surface(self, gmsh_module, candidates):
        if not candidates:
            return []
        best = min(candidates, key=lambda s: gmsh_module.model.occ.getMass(*s))
        return [best]

    def classify_boundaries(self, gmsh_module, volumes, params):
        start, _, _, _, end = self._centerline_points(params)
        tol = max(
            float(params["inner_diameter"]),
            float(params["bend_radius_centerline"]),
            float(params["straight_inlet_length"]),
            float(params["straight_outlet_length"]),
        ) * 1e-5

        fluid_surfaces = gmsh_module.model.getBoundary([volumes["fluid"]], oriented=False, recursive=False)
        solid_surfaces = gmsh_module.model.getBoundary([volumes["solid"]], oriented=False, recursive=False)
        solid_surface_tags = {s[1] for s in solid_surfaces}
        shared_surfaces = [s for s in fluid_surfaces if s[1] in solid_surface_tags]
        interface_surfaces = [s for s in shared_surfaces if self._surface_boundary_count(gmsh_module, s) > 1]
        interface_tags = {s[1] for s in interface_surfaces}

        inlet_candidates = []
        outlet_candidates = []
        for surface in fluid_surfaces:
            if surface[1] in interface_tags:
                continue
            if self._surface_boundary_count(gmsh_module, surface) != 1:
                continue
            if self._surface_matches_point(gmsh_module, surface, start, tol):
                inlet_candidates.append(surface)
            elif self._surface_matches_point(gmsh_module, surface, end, tol):
                outlet_candidates.append(surface)
        inlet = self._pick_smallest_surface(gmsh_module, inlet_candidates)
        outlet = self._pick_smallest_surface(gmsh_module, outlet_candidates)

        solid_inlet_candidates = []
        solid_outlet_candidates = []
        for surface in solid_surfaces:
            if surface[1] in interface_tags:
                continue
            if self._surface_boundary_count(gmsh_module, surface) < 2:
                continue
            if self._surface_matches_point(gmsh_module, surface, start, tol):
                solid_inlet_candidates.append(surface)
            elif self._surface_matches_point(gmsh_module, surface, end, tol):
                solid_outlet_candidates.append(surface)
        solid_inlet_end = self._pick_smallest_surface(gmsh_module, solid_inlet_candidates)
        solid_outlet_end = self._pick_smallest_surface(gmsh_module, solid_outlet_candidates)

        excluded = interface_tags | {s[1] for s in inlet + outlet + solid_inlet_end + solid_outlet_end}
        outer_wall = [s for s in solid_surfaces if s[1] not in excluded]

        groups = [
            (3, volumes["fluid"][1], "fluid"),
            (3, volumes["solid"][1], "solid"),
            (2, [s[1] for s in inlet], "inlet"),
            (2, [s[1] for s in outlet], "outlet"),
            (2, [s[1] for s in interface_surfaces], "fsi_interface"),
            (2, [s[1] for s in outer_wall if s[1] not in {x[1] for x in solid_inlet_end + solid_outlet_end}], "outer_wall"),
            (2, [s[1] for s in solid_inlet_end], "solid_inlet_end"),
            (2, [s[1] for s in solid_outlet_end], "solid_outlet_end"),
        ]

        physical_groups = []
        boundary_dimtags = {}
        for dim, tags, name in groups:
            if isinstance(tags, int):
                tags = [tags]
            tags = [int(tag) for tag in tags]
            if not tags:
                raise RuntimeError(f"expected at least one surface for {name}")
            boundary_dimtags[name] = [(dim, tag) for tag in tags]
            ptag = len(physical_groups) + 1
            gmsh_module.model.addPhysicalGroup(dim, tags, ptag)
            gmsh_module.model.setPhysicalName(dim, ptag, name)
            physical_groups.append((dim, ptag, name))

        physical_name_to_dimtag, physical_dimtag_to_name = build_dimtag_maps(physical_groups)
        return {
            "physical_groups": physical_groups,
            "physical_name_to_dimtag": physical_name_to_dimtag,
            "physical_dimtag_to_name": physical_dimtag_to_name,
            "volume_dimtags": {"fluid": volumes["fluid"], "solid": volumes["solid"]},
            "boundary_dimtags": boundary_dimtags,
        }

    def set_mesh_fields(self, gmsh_module, params, boundary_info):
        gmsh_module.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh_module.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh_module.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh_module.option.setNumber("Mesh.MeshSizeMax", float(params["mesh_size_global"]))
        gmsh_module.option.setNumber("Mesh.MeshSizeMin", float(params["mesh_size_global"]) * 0.5)

        interface_surfaces = [surface[1] for surface in boundary_info["boundary_dimtags"]["fsi_interface"]]
        distance_field = gmsh_module.model.mesh.field.add("Distance")
        gmsh_module.model.mesh.field.setNumbers(distance_field, "FacesList", interface_surfaces)

        interface_field = gmsh_module.model.mesh.field.add("Threshold")
        gmsh_module.model.mesh.field.setNumber(interface_field, "InField", distance_field)
        gmsh_module.model.mesh.field.setNumber(interface_field, "SizeMin", float(params["mesh_size_interface"]))
        gmsh_module.model.mesh.field.setNumber(interface_field, "SizeMax", float(params["mesh_size_global"]))
        gmsh_module.model.mesh.field.setNumber(interface_field, "DistMin", 0.0)
        gmsh_module.model.mesh.field.setNumber(interface_field, "DistMax", float(params["mesh_size_global"]))

        bend_angle_rad = float(params["bend_angle_deg"]) * float(bm.pi) / 180.0
        bend_end_x = float(params["bend_radius_centerline"]) * float(bm.sin(bend_angle_rad))
        bend_end_y = float(params["bend_radius_centerline"]) * (1.0 - float(bm.cos(bend_angle_rad)))
        bend_field = gmsh_module.model.mesh.field.add("Box")
        gmsh_module.model.mesh.field.setNumber(bend_field, "XMin", -float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "XMax", bend_end_x + float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "YMin", -float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "YMax", bend_end_y + float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "ZMin", -float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "ZMax", float(params["outer_radius"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "VIn", float(params["mesh_size_bend"]))
        gmsh_module.model.mesh.field.setNumber(bend_field, "VOut", float(params["mesh_size_global"]))

        background = gmsh_module.model.mesh.field.add("Min")
        gmsh_module.model.mesh.field.setNumbers(background, "FieldsList", [interface_field, bend_field])
        gmsh_module.model.mesh.field.setAsBackgroundMesh(background)
