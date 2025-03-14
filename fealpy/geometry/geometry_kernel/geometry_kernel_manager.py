from typing import Any, Optional, Tuple, List, Dict, Literal
import importlib
import threading

from ... import logger
from .geometry_kernel_base import GeometryKernelBase


class GeometryKernelManager():
    def __init__(self, *, default_kernel: Optional[str]=None):
        self._kernels: Dict[str, GeometryKernelBase] = {}
        self._THREAD_LOCAL = threading.local()
        self._default_kernel_name = default_kernel

    def load_kernel(self, name: str) -> None:
        if name not in GeometryKernelBase._available_kernels:
            try:
                importlib.import_module(f"fealpy.geometry.geometry_kernel.{name}_kernel")
            except ImportError:
                raise RuntimeError(f"Kernel '{name}' is not found.")

        if name in GeometryKernelBase._available_kernels:
            if name in self._kernels:
                logger.info(f"Kernel '{name}' has already been loaded.")
                return
            kernel = GeometryKernelBase._available_kernels[name]()
            kernel.initialize()
            self._kernels[name] = kernel
        else:
            raise RuntimeError(f"Failed to load kernel '{name}'.")

    def set_kernel(self, name: str) -> None:
        if name not in self._kernels:
            self.load_kernel(name)
        self._THREAD_LOCAL.__dict__['kernel'] = self._kernels[name]

    def get_current_kernel(self, logger_msg=None) -> GeometryKernelBase:
        if 'kernel' not in self._THREAD_LOCAL.__dict__:
            if self._default_kernel_name is None:
                raise RuntimeError(
                    f"Kernel properties were accessed ({logger_msg}) "
                    "before a kernel was specified, "
                    "and no default kernel was set in the kernel manager."
                )
            self.set_kernel(self._default_kernel_name)
            logger.info(f"Kernel auto-setting triggered by {logger_msg}."
                        "To reduce unnecessary kernel loading, "
                        "get kernel properties and methods after executing set_kernel()")
        return self._THREAD_LOCAL.__dict__['kernel']

    def __getattr__(self, item):
        return getattr(self.get_current_kernel("GET_ATTR: " + item), item)

    def __setattr__(self, key, value):
        if key in {'_kernels', '_THREAD_LOCAL', '_default_kernel_name'}:
            super().__setattr__(key, value)
        else:
            setattr(self.get_current_kernel("SET_ATTR: " + key), key, value)