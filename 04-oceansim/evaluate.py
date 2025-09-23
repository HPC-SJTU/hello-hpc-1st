import subprocess
import time
import os
import sys
import shutil
import yaml  # 用于生成YAML文件

def check_core(i : int):
    run_res = subprocess.run(["taskset", "-c", str(i), "echo","1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return run_res.returncode

def calculate_score(run_time, full_time, base_time, max_score):
    """根据运行时间计算得分"""
    if run_time <= full_time:
        return max_score  # 满分时间内得满分
    elif run_time > base_time:
        return 0  # 超过基础时间得0分
    else:
        # 线性插值计算得分
        ratio = ( (base_time - run_time) / (base_time - full_time) ) ** 2
        return round(max_score * ratio, 2)

def process_case(sample_id, case_config, binary_name, core_chars):
    """处理单个测试案例并返回得分、详细信息和YAML条目"""
    # 案例配置
    weight = case_config['weight']
    full_time = case_config['full_time']
    base_time = case_config['base_time']
    
    print(f"\n===== 开始测试算例 {sample_id} =====")
    print(f"配置: 满分时间={full_time}s, 基础时间={base_time}s, 权重={weight}%")
    
    # 初始化YAML条目
    yaml_entry = {
        "performance": 0.0,
        "zero_flag": 1,  # 默认触发0分
        "info": "Unknown error"
    }
    
    # 定义样例文件夹和文件路径
    sample_dir = f"Sample{sample_id}"
    input_files = [os.path.join(sample_dir, "OceanSimInput.txt")]
    ref_output_file = os.path.join(sample_dir, "OceanSimOutputRef.txt")
    
    # 检查样例文件夹是否存在
    if not os.path.isdir(sample_dir):
        error_msg = f"找不到测试样例文件夹: {os.path.abspath(sample_dir)}"
        print(f"错误: {error_msg}")
        yaml_entry["info"] = f"Folder not found: {sample_dir}"
        return 0, f"算例{sample_id}：文件夹不存在，得分0分", yaml_entry
    
    # 复制输入文件到当前工作目录（source_code）
    print(f"正在准备测试样例 {sample_id} 的输入文件...")
    input_ready = True
    for file_path in input_files:
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            if os.path.exists(file_name):
                os.remove(file_name)
            # 复制文件
            shutil.copy2(file_path, file_name)
            # 输出原始文件路径（Sample文件夹下的地址）
            print(f"已复制输入文件: {os.path.abspath(file_path)}")
        else:
            error_msg = f"样例文件夹中缺少输入文件 {file_path}"
            print(f"错误: {error_msg}")
            input_ready = False
            yaml_entry["info"] = f"Missing input file: {file_path}"
    
    # 复制参考输出文件
    if os.path.isfile(ref_output_file):
        dest_ref_file = "OceanSimOutputRef.txt"
        if os.path.exists(dest_ref_file):
            os.remove(dest_ref_file)
        shutil.copy2(ref_output_file, dest_ref_file)
        # 输出原始文件路径（Sample文件夹下的地址）
        print(f"已复制参考输出文件: {os.path.abspath(ref_output_file)}")
    else:
        error_msg = f"样例文件夹中缺少参考输出文件 {ref_output_file}"
        print(f"错误: {error_msg}")
        input_ready = False
        yaml_entry["info"] = f"Missing reference file: {ref_output_file}"
    
    if not input_ready:
        return 0, f"算例{sample_id}：输入文件不完整，得分0分", yaml_entry
    
    # 执行程序并计时（设置超时）
    print(f"开始执行程序，最大允许时间{base_time}s...")
    start_time = time.time()
    run_success = False
    run_time = 0
    
    try:
        run_result = subprocess.run(
            f"taskset -c {core_chars} ./{binary_name}",
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=base_time  # 超过基础时间自动终止
        )
        run_time = time.time() - start_time
        run_success = (run_result.returncode == 0)
        yaml_entry["performance"] = round(run_time, 4)
        
        if not run_success:
            error_msg = "程序执行出错！"
            print(f"{error_msg}错误信息:")
            print(run_result.stderr)
            yaml_entry["info"] = f"Runtime Error (code {run_result.returncode})"
            return 0, f"算例{sample_id}：{error_msg}得分0分", yaml_entry
            
    except subprocess.TimeoutExpired:
        run_time = base_time + 1  # 标记为超过基础时间
        yaml_entry["performance"] = run_time
        error_msg = f"程序执行超时！超过基础时间{base_time}s"
        print(error_msg)
        yaml_entry["info"] = "Time Limit Exceeded"
        return 0, f"算例{sample_id}：{error_msg}得分0分", yaml_entry
    
    # 执行验证程序（仅当程序正常结束时）
    verify_passed = False
    if run_success and run_time <= base_time:
        print("开始执行正确性检验...")
        verify_result = subprocess.run(
            f"./verify OceanSimOutputRef.txt OceanSimOutput.txt",
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True
        )
        verify_passed = (verify_result.returncode == 0)

        if not verify_passed:
            print(f"正确性检验不通过！运行时间{run_time:.4f}s")
            yaml_entry["info"] = "Wrong Answer"
            return 0, f"算例{sample_id}：验证不通过，得分0分", yaml_entry
    
    # 计算得分（到这里说明所有检查都通过）
    score = calculate_score(run_time, full_time, base_time, weight)
    yaml_entry["zero_flag"] = 0  # 未触发0分
    yaml_entry["info"] = "Accepted"
    detail = f"算例{sample_id}：运行时间{run_time:.4f}s，得分{score}分"
    
    print(detail)
    return score, detail, yaml_entry

def main():
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(f"测试脚本所在目录: {script_dir}")
    os.system(f"chmod +x {script_dir}/source_code/verify")
    # 定义算例配置
    case_configs = {
        1: {'weight': 25, 'full_time': 0.84, 'base_time': 8.4},
        2: {'weight': 25, 'full_time': 1.6, 'base_time': 16},
        3: {'weight': 25, 'full_time': 2.4, 'base_time': 24},
        4: {'weight': 25, 'full_time': 4.8, 'base_time': 48}
    }
    
    # 检查参数
    sample_ids = []
    if len(sys.argv) == 1:
        # 没有指定算例ID，测试所有1-4
        sample_ids = [1, 2, 3, 4]
        print("未指定测试样例ID，将依次测试算例1-4")
    elif len(sys.argv) == 2:
        # 测试指定算例
        try:
            sample_id = int(sys.argv[1])
            if sample_id < 1 or sample_id > 4:
                print("测试样例ID必须是1到4之间的整数")
                return
            sample_ids = [sample_id]
        except ValueError:
            print("测试样例ID必须是整数")
            return
    else:
        print("参数过多")
        print("使用方法1: python script.py  # 测试所有算例1-4")
        print("使用方法2: python script.py [测试样例ID，1-4]  # 测试单个算例")
        return
    
    
    # find cores
    res_lst = []
    for i in range(128):
        if check_core(i) == 0:
            res_lst.append(i)
    if not len(res_lst) >= 4:
        print(f"No enough cores: need 4 but now is {len(res_lst)}")
        exit(1)
    
    core_chars = ','.join([str(i) for i in res_lst[:4]])
    print(f"Using cores: {core_chars}")


    # 保存原始目录路径（用于后续操作）
    original_dir = os.getcwd()
    
    # 检查并切换到source_code目录
    source_dir = "source_code"
    if not os.path.isdir(source_dir):
        print(f"错误: 找不到source_code目录: {os.path.abspath(source_dir)}")
        # 在脚本所在目录生成错误的YAML文件
        result_yaml = {}
        for sample_id in sample_ids:
            result_yaml[str(sample_id)] = {
                "performance": 0.0,
                "zero_flag": 1,
                "info": "Source code directory not found"
            }
        yaml_path = os.path.join(script_dir, "result.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(result_yaml, f, sort_keys=False)
        print(f"已在脚本所在目录生成result.yaml文件: {yaml_path}")
        return
    
    try:
        os.chdir(source_dir)
        print(f"已切换到工作目录: {os.getcwd()}")
    except Exception as e:
        print(f"切换到source_code目录失败: {e}")
        # 在脚本所在目录生成错误的YAML文件
        result_yaml = {}
        for sample_id in sample_ids:
            result_yaml[str(sample_id)] = {
                "performance": 0.0,
                "zero_flag": 1,
                "info": "Failed to enter source code directory"
            }
        yaml_path = os.path.join(script_dir, "result.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(result_yaml, f, sort_keys=False)
        print(f"已在脚本所在目录生成result.yaml文件: {yaml_path}")
        return
    
    try:
        # 固定源文件和二进制文件名称
        source_file = "OceanSim.cpp"
        binary_name = "OceanSim"
        verify_binary = "verify"
        
        # 初始化YAML结果字典
        result_yaml = {}
        
        # 检查源文件是否存在
        if not os.path.isfile(source_file):
            error_msg = f"错误: 找不到源文件 {source_file}"
            print(error_msg)
            # 为所有要测试的算例记录编译错误
            for sample_id in sample_ids:
                result_yaml[str(sample_id)] = {
                    "performance": 0.0,
                    "zero_flag": 1,
                    "info": "Compile Error: Source file not found"
                }
            # 生成YAML文件到脚本所在目录
            yaml_path = os.path.join(script_dir, "result.yaml")
            with open(yaml_path, "w") as f:
                yaml.dump(result_yaml, f, sort_keys=False)
            print(f"已在脚本所在目录生成result.yaml文件: {yaml_path}")
            return
        
        # 查找verify二进制文件
        if not os.path.isfile(verify_binary):
            error_msg = f"错误: 找不到二进制文件 {verify_binary}"
            print(error_msg)
            # 为所有要测试的算例记录编译错误
            for sample_id in sample_ids:
                result_yaml[str(sample_id)] = {
                    "performance": 0.0,
                    "zero_flag": 1,
                    "info": "Verify Binary Not Found",
                    "score": 0
                }
            # 生成YAML文件到脚本所在目录
            Gen_yaml(result_yaml)
            return
        
        
        # 步骤1: 加载环境并编译主程序
        print("\n===== 开始编译程序 =====")
        compile_commands = f"""
        g++ {source_file} -o {binary_name} -fopenmp -O3 -std=c++20
        """
        
        print(f"\n编译命令为：{compile_commands}")

        compile_result = subprocess.run(
            compile_commands,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=300  # 编译超时设为5分钟
        )
        
        if compile_result.returncode != 0:
            error_msg = "编译失败！错误信息:"
            print(f"{error_msg}")
            print(compile_result.stderr)
            # 为所有要测试的算例记录编译错误
            for sample_id in sample_ids:
                result_yaml[str(sample_id)] = {
                    "performance": 0.0,
                    "zero_flag": 1,
                    "info": "Compile Error"
                }
            # 生成YAML文件到脚本所在目录
            yaml_path = os.path.join(script_dir, "result.yaml")
            with open(yaml_path, "w") as f:
                yaml.dump(result_yaml, f, sort_keys=False)
            print(f"已在脚本所在目录生成result.yaml文件: {yaml_path}")
            return
        
        print("主程序和验证程序编译成功！")
        
        # 执行所有算例测试（使用已编译好的程序）
        total_score = 0
        details = []
        
        for sample_id in sample_ids:
            score, detail, yaml_entry = process_case(sample_id, case_configs[sample_id], binary_name, core_chars)
            total_score += score
            details.append(detail)
            result_yaml[str(sample_id)] = yaml_entry
        
        # 输出最终结果
        print("\n===== 测试总结 =====")
        for detail in details:
            print(detail)
        print(f"\n总得分: {total_score}/100分")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        # 错误情况下也生成YAML文件
        result_yaml = {}
        for sample_id in sample_ids:
            result_yaml[str(sample_id)] = {
                "performance": 0.0,
                "zero_flag": 1,
                "info": f"Test process error: {str(e)}"
            }
    finally:
        # 生成YAML文件到脚本所在目录
        yaml_path = os.path.join(script_dir, "result.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(result_yaml, f, sort_keys=False)
        # 切换回原始目录
        os.chdir(original_dir)
        print(f"\n已切换回原目录: {os.getcwd()}")
        print(f"已在脚本所在目录生成result.yaml结果文件: {yaml_path}")

if __name__ == "__main__":
    main()
    