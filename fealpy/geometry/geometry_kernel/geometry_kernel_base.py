from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, List, Dict, Literal, Type
from ... import logger


def _make_default_mapping(*names: str):
    return {k: k for k in names}

ATTRIBUTE_MAPPING = _make_default_mapping(

)

FUNCTION_MAPPING = _make_default_mapping(

)

TRANSFORMS_MAPPING = _make_default_mapping(

)


class ModuleProxy():
    @classmethod
    def attach_attributes(cls, mapping: Dict[str, str], source: Any, /):
        for target_key, source_key in mapping.items():
            if (source_key is None) or (source_key == ''):
                continue
            if hasattr(source, source_key):
                setattr(cls, target_key, getattr(source, source_key))

    @classmethod
    def attach_methods(cls, mapping: Dict[str, str], source: Any, /):
        for target_key, source_key in mapping.items():
            if (source_key is None) or (source_key == ''):
                continue
            if hasattr(cls, target_key):
                # Methods will not be copied from source if implemented manually.
                logger.debug(f"`{target_key}` already defined. "
                             f"Skip the copy from {source.__name__}.")
                continue
            if hasattr(source, source_key):
                setattr(cls, target_key, staticmethod(getattr(source, source_key)))
            else:
                logger.info(f"`{source_key}` not found in {source.__name__}. "
                            f"Method `{target_key}` remains unimplemented.")

    @classmethod
    def show_unsupported(cls, signal: bool, function_name: str, arg_name: str) -> None:
        if signal:
            logger.warning(f"{cls.__name__} does not support the "
                           f"'{arg_name}' argument in the function {function_name}. "
                           f"The argument will be ignored.")


class GeometryKernelBase(ABC, ModuleProxy):
    """几何内核适配器基类，定义所有内核必须实现的接口"""
    _available_kernels: Dict[str, Type["GeometryKernelBase"]] = {}

    def __init_subclass__(cls, kernel_name: str, **kwargs):
        super().__init_subclass__(**kwargs)

        if kernel_name != "":
            cls._available_kernels[kernel_name.lower()] = cls
            cls.backend_name = kernel_name
        else:
            raise ValueError("Backend name cannot be empty.")

    @abstractmethod
    def initialize(self, config: Optional[dict] = None) -> None:
        """初始化几何内核（如加载依赖库、配置参数）"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """清理内核资源"""
        pass

    @abstractmethod
    def create_box(self, width: float, height: float, depth: float) -> Any:
        """创建立方体，返回内核内部对象句柄"""
        pass

    @abstractmethod
    def create_sphere(self, radius: float) -> Any:
        """创建球体"""
        pass

    @abstractmethod
    def boolean_union(self, shape1: Any, shape2: Any) -> Any:
        """布尔并集操作"""
        pass

    @abstractmethod
    def boolean_difference(self, shape1: Any, shape2: Any) -> Any:
        """布尔差集操作"""
        pass

    @abstractmethod
    def transform(self, shape: Any, translation: Tuple[float, float, float], rotation: Tuple[float, ...]) -> Any:
        """几何变换（平移+旋转）"""
        pass

    @abstractmethod
    def get_volume(self, shape: Any) -> float:
        """计算几何体体积"""
        pass

    @abstractmethod
    def get_bounding_box(self, shape: Any) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """获取几何体包围盒（min_point, max_point）"""
        pass

    @abstractmethod
    def save_to_file(self, shape: Any, filename: str, format: str = "STEP") -> None:
        """将几何体导出为文件（如STEP、IGES）"""
        pass