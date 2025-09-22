# Hello HPC

> 完成此题获取交我算账号，开启你迈向HPC的第一步！

小交同学希望你已经阅读了[HPC入门指南-SSH](https://xflops.sjtu.edu.cn/hpc-start-guide/network/SSH/)与[HPC入门指南-登录交我算集群](https://xflops.sjtu.edu.cn/hpc-start-guide/network/login-HPC/)，并了解了如何使用 OJ。因此他准备测试一下你的掌握情况再决定是否将交我算账号发给你。

## 任务要求

你需要完成如下步骤获取交我算账号：

1. 找到在运行 `ssh armlogin.hpc.sjtu.edu.cn` 与对端主机建立连接时对端主机的 `ED25519` 公钥的指纹（通过 SHA256 算法得到，该字符串应为一串未经过填充处理的 Base64 编码字符串），运行 `python submit.py <指纹内容>` 得到提交文件。
2. 提交步骤1中得到的提交文件，在本次提交的算例信息中会返回本题的正确答案，正确答案的格式应该是 `hellohpc{...}`。运行 `python submit.py <正确答案>` 即可得到正确答案的提交文件。
3. 提交步骤2中得到的提交文件，在本次提交的算例信息中会返回你分配得到的交我算的账号与密码。

**拿到交我算账号后请第一时间修改密码！**