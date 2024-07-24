
from typing import Any, Tuple, Union, Optional, overload, TypeGuard

from .base import Backend, Size, Number
from .base import TensorLike as _DT


class BackendManager():
    def __init__(self, *, default_backend: str): ...
    def set_backend(self, name: str) -> None: ...
    def load_backend(self, name: str) -> None: ...
    def get_current_backend(self) -> Backend: ...

    ### constants ###

    pi: float
    e: float
    nan: float
    inf: float
    dtype: type
    device: type
    bool_: Any
    uint8: Any
    int_: Any
    int8: Any
    int16: Any
    int32: Any
    int64: Any
    float_: Any
    float16: Any
    float32: Any
    float64: Any
    complex_: Any
    complex64: Any
    complex128: Any

    ### Backend tools ###

    @staticmethod
    def is_tensor(obj: Any, /) -> TypeGuard[_DT]: ...
    @staticmethod # PyTorch
    def set_default_device(device: str) -> None: ...
    @staticmethod
    def to_numpy(tensor_like: _DT, /) -> Any: ...
    @staticmethod # PyTorch
    def from_numpy(ndarray: Any, /) -> _DT: ...

    ### Tensor creation methods ###

    @staticmethod # Numpy + PyTorch(tensor)
    def array(object, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy(array) + PyTorch
    def tensor(data, /, dtype=None, **kwargs) -> _DT: ...
    @overload
    @staticmethod # Numpy + PyTorch
    def arange(stop: int, /, *, dtype=None, **kwargs) -> _DT: ...
    @overload
    @staticmethod # Numpy + PyTorch
    def arange(start: int, stop: int, /, step=1, *, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy
    def linspace(start, stop, num, /, endpoint=True, retstep=False, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def empty(shape: Size, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def zeros(shape: Size, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def ones(shape: Size, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def empty_like(prototype: _DT, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def zeros_like(prototype: _DT, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def ones_like(prototype: _DT, /, dtype=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy
    def eye(n: int, m: Optional[int]=None, /, k: int=0, dtype=None, **kwargs) -> _DT: ...

    ### Reduction methods ###

    @staticmethod # Numpy
    def all(a: _DT, axis=None, out=None, keepdims=False) -> _DT: ...
    @staticmethod # Numpy
    def any(a: _DT, axis=None, out=None, keepdims=False) -> _DT: ...
    @staticmethod # Numpy
    def sum(a: _DT, axis=None, dtype=None, out=None, keepdims=False, initial: Number=...) -> _DT: ...
    @staticmethod # Numpy
    def prod(a: _DT, axis=None, dtype=None, out=None, keepdims=False, initial: Number=...) -> _DT: ...
    @staticmethod # Numpy
    def mean(a: _DT, axis=None, dtype=None, out=None, keepdims=False) -> _DT: ...
    @staticmethod # Numpy
    def max(a: _DT, axis=None, out=None, keepdims=False): ...
    @staticmethod # Numpy
    def min(a: _DT, axis=None, out=None, keepdims=False): ...

    ### Unary operations ###

    @staticmethod # Numpy + PyTorch
    def abs(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def sign(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def sqrt(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def log(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def log10(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def log2(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def sin(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def cos(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def tan(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def sinh(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def cosh(__x1: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def tanh(__x1: _DT, out=None, **kwargs) -> _DT: ...

    ### Binary operations ###

    @staticmethod # Numpy + PyTorch
    def add(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def substract(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def multiply(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def divide(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def power(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def matmul(__x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def dot(a: _DT, b: _DT, out=None) -> _DT: ...
    @staticmethod # Numpy
    def cross(a: _DT, b: _DT, axis: Optional[int]=None, **kwargs) -> _DT: ...
    @staticmethod # Numpy
    def tensordot(a: _DT, b: _DT, axes: Union[int, Tuple]) -> _DT: ...

    ### Other methods ##

    @staticmethod # Numpy + PyTorch
    def reshape(a: _DT, newshape: Size, /) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def broadcast_to(array: _DT, shape: Size, /) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def einsum(subscripts: str, /, *operands: _DT, optimize=False, **kwargs) -> _DT: ...
    @staticmethod # Numpy
    def unique(ar: _DT, return_index=False, return_inverse=False, return_counts=False, axis=0, **kwargs): ...
    @staticmethod # Numpy
    def sort(a: _DT, axis=0, **kwargs) -> _DT: ...
    @staticmethod # -
    def nonzero(a: _DT, /, as_tuple=True) -> Union[_DT, Tuple[_DT, ...]]: ...
    @staticmethod # Numpy
    def cumsum(a: _DT, axis=None, dtype=None, out=None) -> _DT: ...
    @staticmethod # Numpy
    def cumprod(a: _DT, axis=None, dtype=None, out=None) -> _DT: ...
    @staticmethod # PyTorch
    def cat(tensors, dim=0, *, out=None) -> _DT: ...
    @staticmethod # Numpy
    def concatenate(arrays, /, axis=0, out=None, *, dtype=None) -> _DT: ...
    @staticmethod # Numpy
    def stack(arrays, axis=0, out=None, *, dtype=None) -> _DT: ...
    @staticmethod # Numpy + PyTorch(permute)
    def transpose(a: _DT, axes: Size, /) -> _DT: ...
    @staticmethod # Numpy + PyTorch
    def swapaxes(a: _DT, axis1: int, axis2: int, /) -> _DT: ...

    ### FEALPy functionals ###

    @staticmethod
    def multi_index_matrix(p: int, dim: int, *, dtype=None) -> _DT: ...
    @staticmethod
    def edge_length(edge: _DT, node: _DT, *, out=None) -> _DT: ...
    @staticmethod
    def edge_normal(edge: _DT, node: _DT, normalize=False, *, out=None) -> _DT: ...
    @staticmethod
    def edge_tengent(edge: _DT, node: _DT, normalize=False, *, out=None) -> _DT: ...
    @staticmethod
    def tensorprod(*tensors: _DT) -> _DT: ...
    @staticmethod
    def bc_to_points(bcs: Union[_DT, Tuple[_DT, ...]], node: _DT, entity: _DT) -> _DT: ...
    @staticmethod
    def barycenter(entity: _DT, node: _DT, loc: Optional[_DT]=None) -> _DT: ...
    @staticmethod # base
    def simplex_ldof(p: int, iptype: int) -> int: ...
    @staticmethod # base
    def simplex_gdof(p: int, nums: Tuple[int, ...]) -> int: ...
    @staticmethod
    def simplex_measure(entity: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def simplex_shape_function(bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    @staticmethod
    def simplex_grad_shape_function(bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    @staticmethod
    def simplex_hess_shape_function(bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    @staticmethod # base
    def tensor_ldof(p: int, iptype: int) -> int: ...
    @staticmethod # base
    def tensor_gdof(p: int, nums: Tuple[int, ...]) -> int: ...
    @staticmethod
    def tensor_measure(entity: _DT, node: _DT) -> _DT: ...

    @staticmethod
    def interval_grad_lambda(line: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def triangle_area_3d(tri: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def triangle_grad_lambda_2d(tri: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def triangle_grad_lambda_3d(tri: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def quadrangle_grad_lambda_2d(quad: _DT, node: _DT) -> _DT: ...
    @staticmethod
    def tetrahedron_grad_lambda_3d(tet: _DT, node: _DT, local_face: _DT) -> _DT: ...
