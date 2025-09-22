# python setup.py build_ext --inplace
from distutils.core import setup, Extension
module = Extension(
    "fastreq",
    sources=["fastreq.cc"],
    language="c++",
    include_dirs=["."],
    extra_compile_args=['-std=c++20', '-O3', '-Wall']
)

setup(
    name="fastreq",
    version="0.1",
    description="Fast batch HTTP client for m4c server",
    ext_modules=[module],
)