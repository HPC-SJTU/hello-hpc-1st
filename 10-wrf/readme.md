# WRF Challenge

## 题目背景

随着高性能计算（HPC）技术的不断发展，科学研究中越来越多的问题依赖于大规模数值模拟。科学计算通过构建数学模型和数值算法，在超级计算机上对复杂自然现象进行模拟和预测，已成为现代科研不可或缺的重要工具。**天气预报**是科学计算应用中最典型、最具挑战性的领域之一。气象模拟涉及海量数据、高复杂度的物理过程，对计算性能的极高要求。高性能并行计算平台，为提升气象模拟的空间分辨率和预报准确度提供了坚实基础。

WRF（Weather Research and Forecasting Model）是当前国际上广泛应用的大气数值模拟和天气预报系统。它采用Fortran和C语言开发，高度依赖于科学计算库和并行计算环境。需要依赖MPI、NetCDF（科学数据格式）、HDF5等基础库，以及编译器选项的支持，WRF才能高效地在超算平台上实现大规模并行计算。它集成了复杂的动力学、物理过程和高效的数值算法，能够模拟和预测从全球到区域尺度的大气演变过程。WRF支持三维大气环流模拟，能够处理包括降水、风场、温度、湿度等在内的多种气象要素，对极端天气、台风路径、空气质量、气候变化等科研和实际业务均具有重要价值。WRF结构灵活、可配置性强，具备高度模块化和可扩展性，便于集成不同的物理过程参数化方案，也支持多种网格和分辨率设置，适应从学术研究到实际业务预报的多样化需求。作为全球气象、环境和气候模拟的重要工具，WRF已被广泛应用于高校、科研院所和业务部门，是检验计算平台性能、熟悉科学应用软件优化能力的典型案例。

本题目需要在华为鲲鹏平台上从依赖开始编译WRF并运行conus12km算例，这是一件比较有挑战性的工作，不过好在华为官方提供了[编译文档](https://www.hikunpeng.com/document/detail/zh/kunpenghpcs/hpcindapp/prtg-osc/openmind_kunpengwrf_02_0001.html)供我们参考。只不过在我们的平台上，**完全按照文档编译会遇见一些错误**。这种面对文档编译复杂应用的场景，往往是超算比赛拿到题目之后的第一步。本题编译时间限制为60min，超时将视为编译失败。选手可以自行选择编译器（HMPI、OpenMPI等，其中OpenMPI相对编译更快）,也可以自定义编译选项。

## 目录格式与提交要求

在`source_code`目录下，通过`bash ./download.sh`可以下载到题目的所有文件。下载以后的目录树如下：其中`conus12km`目录为最终运行输入算例目录，`dependencies`目录中包含所需依赖的压缩包，`WRF-4.2.tar.gz`为WRF-4.2本体。

```bash
source_code
├── conus12km
│   └── conus12km.tar.gz
├── dependencies
│   ├── hdf5-1.10.1.tar
│   ├── netcdf-c-4.4.1.1.tar.gz
│   ├── netcdf-fortran-4.4.1.tar.gz
│   ├── parallel-netcdf-1.9.0.tar.gz
│   ├── pnetcdf-1.14.0.tar.gz
│   └── zlib-1.2.11.tar.gz
├── WRF-4.2.tar.gz
└── download.sh
```

你需要提交 `writeup.md`、`source_code/build`、`source_code/run` 和 `source_code/build_scripts/` 文件夹。我们提供了 `submit.py`，只需运行 `python submit.py` 即可一键生成提交文件提交到 OJ。请将编译依赖与wrf本体的逻辑写在`build`中，将运行wrf的逻辑写在`run`中，`build_scripts/`路径下可以放一些辅助编译的其他脚本，如没有这些脚本，只需要创建一个空目录即可。

评测机将在`source_code`目录下，运行`./build`以及`./run`，并对后者计时。要求最终 `wrf` 生成的日志文件`rsl.out.0000`应当位于 `source_code/conus12km/conus12km/`（如果运行生成日志在其他路径，请在run脚本中包括将`rsl.out.0000`拷贝到`source_code/conus12km/conus12km/`的命令）。

## evaluate.py

我们提供的评测脚本`evaluate.py`可以自动评测你的得分，可以直接 `python evaluate.py` 使用脚本。

## 参考编译流程

### 依赖编译

WRF有四个依赖软件：`HDF5`，`PNetCDF`，`zlib`，`NetCDF`，本题目需要手动编译并合理配置环境变量与编译选项以管理依赖。这些依赖均通过configure文件编译。参考configure的参数可见华为官方文档[配置编译环境](https://www.hikunpeng.com/document/detail/zh/kunpenghpcs/hpcindapp/prtg-osc/openmind_kunpengwrf_02_0005.html)一节内容。

### WRF编译

WRF编译请参考[编译和安装](https://www.hikunpeng.com/document/detail/zh/kunpenghpcs/hpcindapp/prtg-osc/openmind_kunpengwrf_02_0012.html)一节内容，

### 运行基准测试

基准测试的输入文件可以通过解压`conus12km.tar.gz` 得到，运行方法可以参考华为文档的[运行和验证](https://www.hikunpeng.com/document/detail/zh/kunpenghpcs/hpcindapp/prtg-osc/openmind_kunpengwrf_02_0001.html)部分。

提示：如果遇见运行失败，可以通过`rsl.error.0000` 文件的内容debug。

## 评分准则

编译完成并能运行出正确结果得到50分，剩余50分由算例运行时间在`10min30s`到`15min`内对数线性插值得到（运行超过15min得0分，小于10min30s得50分）。插值公式如下：

$$
score = 50 \times \frac{ln(t_{zero})−ln(t_{your})}{ln(t_{zero})−ln(t_{full})}
$$

## 资源限制
最终提交的编译流程会独占128核心运行，编译超时时间为60min，运行超时时间为20min。本题编译部分并行度不高，故可以直接在`kp_interact`队列里测试，但实际运行wrf程序请在`kp_run`队列中进行。