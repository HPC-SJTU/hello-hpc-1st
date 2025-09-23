# 小交问答

## 背景

“我是零基础小白也能参赛吗？” 在听闻的众多自称“小白”的同学的疑问后，小交同学决定在校内赛插入一道简单的选择填空题来让真正的零基础小白有参与感。但是如果只是选择填空题怎么体现 HPC 的主题的呢？小交陷入了沉思，或许可以让大家使用一些独特的方式提交答案。

## 题目

本题共有11道小题，你需要将每个题目的答案按照规定的格式写入一个 `yaml` 文件中并提交，每道题目的题号对应键，每个题目的所有的空组织成一个列表。示例的 yaml 文件已经给出，当然其中的答案并不正确。

小交为了避免大家作弊，要求在提交的 `writeup.md` 中简要说明你4-11小题的解题过程（如果你没有进行任何实操就得到了答案则不需要写）。

> 你可能感觉下面的题目非常陌生，但是不要担心。本题主要考察你的信息素养，只要你学会使用搜索引擎与AI，零基础小白也能获得满分～

小交同学的11道题如下：
1. (5')[单选] 在高性能计算集群中，哪个工具通常用于作业调度和资源管理？（  ）
   
    <ul style="list-style-type: none; padding-left: 20px;">
     <li>A. 微信群</li>
     <li>B. Slurm</li>
     <li>C. Docker Swarm</li>
     <li>D. Apache Mesos</li>
    </ul>

2. (5')[不定项] 下面哪些语言是编译型语言：（  ）
    
    <ul style="list-style-type: none; padding-left: 20px;">
     <li>A. C/C++</li>
     <li>B. Python</li>
     <li>C. Fortran</li>
     <li>D. Go</li>
     <li>E. Rust</li>
     <li>F. JavaScript</li>
     <li>G. Java</li>
     <li>H. Shell Script</li>
     <li>I. C#</li>
   </ul>

3. (5') 假设 SJTUG 镜像站存储服务器发生变更，社长任命你为存储迁移负责人，聪明的你决定先估算一下需要迁移多久以安排迁移时间。你先使用 `du -sh` 命令统计得出共需搬迁 20T 的数据，迁移时将使用千兆有线网传输，估算最快需要（  ）小时完成搬迁。（四舍五入保留1位小数）
4. (3 x 5') 在交我算 arm 集群的登录节点（kplogin1）上运行 `ping huge1` 时发送的 ICMP 报文的源 MAC 地址为（  ），目标 MAC 地址为（  ），源 IP 地址为（  ）。 
5. (10') 计算 Xflops 官网的 banner (如图所示)对应的原文件（.svg文件）的 sha512 哈希值为（  ）。

![](https://xflops.sjtu.edu.cn/oj/files/banner_pic.png)

6. (2 x 5') 网址“net.sjtu.edu.cn”的 IPv4 地址为（  ），IPv6 地址为（  ）。
7. (10') 交我算集群使用 module 工具管理环境，在 arm 集群上已使用此工具安装了华为毕昇编译器，可使用 `module load bisheng` 加载。其用于编译 C++ 的编译器的可执行文件路径是（  ）。
8. (5') 截至 2025 年 8 月 20 日，NVIDIA ConnectX-8 C8180 网卡固件 (Firmware) 的最新版本的版本号是（  ）？
9.  (2 x 5') 交我算集群上有几个 a800 节点？（  ）名称分别是什么？（  ）（如果有多个结果请用半角逗号隔开）
10. (10')截止 2025 年 6 月，TOP500 榜单第 3 名超级计算机使用的数学库是？（  ）（注：请勿使用缩写，填写全称，如 BLAS 请写成 Basic Linear Algebra Subprograms）
11. (3 x 5') arm128c256g 计算节点 cpu socket 有（  ）个，NUMA node有（  ）个。NUMA node distance 矩阵第一行为（  ）？（数字之间用半角逗号隔开）

## 自测文件

本题目的自测文件不会给出得分信息，只用于帮助你预览你填写的答案，运行 `python evaluate.py` 后将打印出将你的答案填写到题目中的预览效果。