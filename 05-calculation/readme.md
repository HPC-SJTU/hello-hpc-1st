# Calculation
## 问题描述

在本题中，你需要优化一个计算函数，并选择合适的编译器和给出合适的编译命令。

我们已经提供了基本的代码框架，你需要将核心的求和函数更新部分代码`query_sum.h`，可以在`source_code`目录下找到。**其他部分的代码不允许修改。**

同时，你需要完成`source_code`目录下的`compile.sh`，写出你的编译命令。

其中，核心求和函数的baseline如下：
```cpp
size_t sum(short A[], size_t n, size_t m, double k) {
    size_t answer = 0;
    for (size_t i = 1; i <= n; ++i) {
        size_t j_limit = std::pow(i, k);
        double sum = 0.0;
        for (size_t j = 1; j <= j_limit; ++j) {
            if (A[i * m + j] % 2) answer += A[i * m + j];
            else answer += (A[i * m + j] << 1);
            double sum_sin = 0.0;
            for (size_t p = 1; p <= j; ++p) 
                sum_sin += std::sin(p) * std::cos(p);
            sum += j * sum_sin * std::sin(j);
        }
        answer -= size_t(sum);
    }
    return answer;
}
```

## 测试数据
由于本题的测试数据较大，需要选手自行下载测试数据，下载完测试数据后，请把数据放到本题目的`data/`目录下。
运行提供的`download.sh`即可获取数据。在`./download.sh`前，请先`chmod +x download.sh`添加下载权限。

## 输入输出格式

从输入文件 `conf<i>.data` （其中i=1, 2, 3, 4，具体看`data/`）中读取如下内容：

| 项目 | 类型 | 范围 |
| --- | --- | --- |
| `n` | size_t | $$1 <= n <= 2 \times 10^6$$ |
| `k` | double | $$\frac{1}{3} <= k <= \frac{3}{5}$$ |
| `A` | short [] | $$0 <= A[i] <= 99$$ |

运行结果的`main.cpp`已经给出，请不要修改相关代码。

对于每一个算例`conf<i>.data`，你都可以在data/的`ref<i>.data`找到对应的正确计算结果。

## 编译运行

### 编译
使用编译命令进行编译。

在比赛提供的集群上，有可供选择的两个编译器：
1. g++
2. clang++

如果在比赛提供的集群上希望使用clang++，请使用 `module load bisheng/2.5.0` 加载 bisheng 编译器。

### 运行
我们提供了`which_core.py`来检测当前可用核心的编号。
假设返回的编号是0到15，那么在编译出`source_code/calculation`后，你可以使用命令`taskset -c 0-15 source_code/calculation data/conf<i>.data data/ref<i>.data`来运行第i个算例（其他算例同理），一般来说，输出包括两行：第一行为该算例平均运行时间，第二行为`PASS`或`FAIL`表示程序得出的结果是否匹配`ref<i>.data`。

## 评分标准

**本题你需要提交包括`query_sum.h`和`compile.sh`文件**，我们会将你提交的`query_sum.h`替换原有的文件并使用`compile.sh`编译你的程序。我们会在在每个样例上先进行一次warm up，然后重复运行25次，计算运行时间的平均值。每个样例的输出会与参考输出进行比较，以验证程序正确性。

你的任务将被分配在**同一个NUMA节点内的8个物理CPU核心**上运行，限制内存占用为**16G**。
| 算例  | 分数占比 | 满分时间(μs) | 基础时间(μs) |
| --- | ---- | ----| -----|
| 1 | 25% | 1200 | 27500 |
| 2 | 35% | 6000 | 35000 |
| 3 | 15% | 80 | 2600 |
| 4 | 25% | 1350 | 34000 |

每个算例的分数计算公式为

$$\min((\frac{ln(基础时间)-ln(运行时间)}{ln(基础时间)-ln(满分时间)}),1) \times 100$$

## 评测脚本使用

我们提供了`evaluate.py`用于自测你当前的答题情况。直接运行
``` bash
python evaluate.py
```
将对你目前的答案进行评测，并输出你的得分。

默认情况下将会按照最终的评测标准进行测试，这将会让每个算例运行80次。如果你希望测试过程更快，可以添加参数`-t <num>`
例如
``` bash
python evaluate.py -t 2 # 参数至少写2
```

输出的信息有着几种情况：
1. Success: 当前算例答案正确。
2. Accepted: 当前算例答案正确，并且达成了满分时间限制的要求。
3. Wrong Answer: 当前算例答案错误。
4. Time Limit Exceeded: 当前算例运行超出时间限制。

## 提交
### 你需要提交的东西
1. `writeup.md` (请放在和`evaluate.py`同级的目录下)。请把你的做题思路和代码实现写到里面。
2. `compile.sh` (请放到`source_code/`)。请把你的编译命令写进去。
3. `query_sum.h` (请放到`source_code/`)。请把你的sum函数实现写进去。
### 提交方法
运行
```bash
python submit.py
```
新生成的`submit.zip`即为本题所需提交的东西。

## 提示
1. 请不要修改除`compile.sh`和`query_sum.h`之外的内容。
2. 本题可优化的点很多。
3. 直接用`./compile.sh`可能不能正常编译，要先`chmod +x compile.sh`给脚本加上运行权限。
4. 建议先进行一些优化再进行测试，不然会等待时间很久。