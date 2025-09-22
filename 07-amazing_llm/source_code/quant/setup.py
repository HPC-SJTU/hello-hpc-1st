from setuptools import setup, find_packages
from torch.utils import cpp_extension
import json, os

work_dir = os.path.dirname(__file__)
with open(os.path.join(work_dir, "setup.json"), "r") as f:
    cfg = json.load(f)

setup(
    name="q6bit",
    version="0.1.0",
    packages=find_packages(), 
    ext_modules=[
        cpp_extension.CppExtension(
            "q6bit." + cfg["extension_name"],  # 扩展模块名称
            cfg["src"],  # 源文件
            extra_compile_args=cfg["compile_args"]  # 优化选项
        )
    ],
    cmdclass={
        "build_ext": cpp_extension.BuildExtension
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
    ],
)
