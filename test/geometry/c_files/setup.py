from distutils.core import setup, Extension
from Cython.Build import cythonize
import os
from distutils import sysconfig

# 编译配置
ext = Extension(
    name="cgal_cython",
    sources=["cgal_cython.pyx", "cgal_wrapper.cpp"],
    include_dirs=["/usr/include",
                  "/usr/local/include",
                  "/home/concha/.local/cgal/include",
                  ],  # 确保包含 CGAL 头文件路径
    language="c++",
    extra_compile_args=["-std=c++17", "-fPIC"],
    library_dirs=["/usr/lib/gcc/x86_64-linux-gnu"],  # 添加库路径
    libraries=["gmp", "mpfr"],
)

setup(
    name="cgal_cython",
    ext_modules=cythonize(ext, compiler_directives={'language_level': "3"}),
    script_args=["build_ext", "--inplace"]
)