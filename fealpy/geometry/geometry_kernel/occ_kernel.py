import OCC.Core.BRepBuilderAPI as BRepBuilderAPI
from .geometry_kernel_base import (
    GeometryKernelBase, ATTRIBUTE_MAPPING,
    FUNCTION_MAPPING, TRANSFORMS_MAPPING
)


class OCCKernel(GeometryKernelBase, kernel_name="occ"):
    def initialize(self, config=None):
        pass

    def shutdown(self):
        pass

    def create_box(self, width, height, depth):
        pass

    def create_sphere(self, radius):
        pass

    def boolean_union(self, shape1, shape2):
        pass

    def boolean_difference(self, shape1, shape2):
        pass

    def transform(self, shape, translation, rotation):
        pass

    def get_volume(self, shape):
        pass

    def get_bounding_box(self, shape):
        pass

    def save_to_file(self, shape, filename, format="STEP"):
        pass

attribute_mapping = ATTRIBUTE_MAPPING.copy()
function_mapping = FUNCTION_MAPPING.copy()

OCCKernel.attach_attributes(attribute_mapping, BRepBuilderAPI)
OCCKernel.attach_methods(function_mapping, BRepBuilderAPI)