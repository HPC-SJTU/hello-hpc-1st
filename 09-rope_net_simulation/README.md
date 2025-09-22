# Rope-Net-Simulation

## 问题描述

系绳网络是指绳缆经过打结交织形成的网格，在近些年来越来越受到研究者的关注。

由于其柔性和被动阻尼的特性，许多研究者认为绳网进行捕获目标（如罪犯、汽车、无人机、小行星）、防治山体滑坡上有着卓越的效果。

本题模拟了一个方形的绳网在`10m/s`的初速度和微重力环境下捕获一个较大的不规则目标的工况，使用节点法离散绳网系统，力学仿真包括了绳网内应力动力学、绳网受到微重力影响和绳网与目标的接触动力学。

你可以修改`CMakeLists.txt`, `OdeEuler.cpp`, `calGF.cpp` 和 `acceleration.cpp`，使用任何优化方式，比如并行化、向量化。

hint: 本题没有清晰地给出计算热点，请根据常识或`profiling`手段自行判断。如果你是`HPC`新手，在并行化的时候需要注意数据依赖关系。

## 输入

`./source_code/const.h`包含了物理常数。`./source_code/poly.txt`，`./source_code/topo.txt`，`./source_code/Shp.txt`保存了需要的`结构和拓扑学`模型。`./source_code/solution`文件夹存储最终会得到输出。
`./source_code/RopeSimulator`为编译后的二进制文件。调用时需要三个`args`, 分别是：`dt`, `t0`, `tf`, 都以浮点数的方式输入。如：
```bash
./RopeSimulator 时间步长 开始模拟时间 结束模拟时间
```


## 编译运行

本题需要以128核心运行，以获得最好的性能。

```bash
module load bisheng
cd ./source_code/
cmake -B build
cd build && make && cp ./RopeSimulator ../ && cd ../
# 第一个算例
./RopeSimulator 0.001 0.0 5.0
# 算例会自动输出运行时间等信息，如需校验正确性，可以和comparison1.dat比较。我推荐使用evaluate.py自动校验。
# 第二个算例
./RopeSimulator 0.0001 0.0 0.5
```

后一次运行会覆盖前一次运行的输出。另外请不要在`./source_code/main.cpp`中修改输出文件的名字。

另外，你可以直接用`python evaluate.py`测评。测试算例与本地算例**不**相同，请不要试图使用打表等方式。

## 自动评测脚本

本体配备了python自动评测脚本，

```bash
python evaluate.py
```

运行`evaluate.py`后，`result.yaml`会自动生成在同级目录下，`result1.txt`和`result2.txt`作为两个算例的结果会被移动到同级目录下以供参考。

自动评测脚本仅供参考分数，比赛的评测过程在OJ平台云端完成，你并不需要提交`result.yaml`, `result1.txt`和`result2.txt`。

(请在128cores的节点运行)

## 提交

运行`submit.py`会自动从`./source_code`和`.`中打包所需文件，并在同级目录生成`submit.zip`。你需要将`submit.zip`传输到你的电脑上并提交到OJ平台。

请确保你的文件夹下有，否则无法正常进行打包：

```yaml
# in submit.yaml，请不要修改这个表。
0:
- source_code/CMakeLists.txt
- source_code/OdeEuler.cpp
- source_code/calGF.cpp
- source_code/acceleration.cpp
- writeup.md
```

## 评分标准

**本题你需要提交源代码文件**，我们会将你提交的`CMakeLists.txt`, `OdeEuler.cpp`, `calGF.cpp` 和 `acceleration.cpp`替换原有的文件并运行评测程序。

本题目评测包含**两个测试算例**，基于程序运行时间进行评分。

| 算例  | 分数占比 | 参数(dt, t0, tf) | 参考文件            |
| --- | ---- | -------------- | --------------- |
| 算例0 | 50%  | 0.001 0.0 5.0  | comparison.dat  |
| 算例1 | 50%  | 0.0001 0.0 0.5 | comparison2.dat |

### 评分规则

1. **正确性检查**   程序输出结果与参考文件的**平均**相对误差不得超过**0.001%**，否则该算例得0分
2. **运行时间限制** 单个算例最大运行时间为**2000秒**，超时得0分
3. **评分公式**     基于运行时间的分段函数计算

| 运行时间(秒)        | 得分                               |
| -------------- | -------------------------------- |
| ≤ 14.8          | 100分                             |
| 14.8 < t ≤ 420  | $$ \frac{27}{\ln14.8-\ln420}\left(\ln x-\ln420\right)+73 $$           |
| 420 < t < 2000 | 73 × (1 - ((t-420)/(2000-420))²) |
| ≥ 2000         | 0分                               |

本题的`baseline`没有经过任何优化，评测为0分。

#### 最终得分计算

最终得分 = 算例0得分 + 算例1得分

**注意事项:**

- 编译错误、运行时错误(如段错误)、输出错误等情况均得0分
- 程序必须在指定时间内完成且输出正确结果才能获得分数

即可运行。结果会保存到`result.yaml`中。此结果仅供参考，实机测评与本地测评成绩不同。


