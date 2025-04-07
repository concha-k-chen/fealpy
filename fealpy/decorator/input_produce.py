from functools import wraps
from ..backend.base import TensorLike

def multi_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 判断只有一个参数传入，并且它是一个列表，且其中的每个元素也是列表或元组
        if len(args) == 1 and isinstance(args[0], (list, tuple, TensorLike)) and all(isinstance(item, (list, tuple, TensorLike)) for item in args[0]):
            results = []
            for param_set in args[0]:
                # param_set 应该是一个列表或元组，使用 *param_set 来解包调用原函数
                results.append(func(*param_set, **kwargs))
            return results
        # 如果都不是序列，直接调用
        return func(*args, **kwargs)
    return wrapper