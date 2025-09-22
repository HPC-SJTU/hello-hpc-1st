import subprocess
import time
import os
import math
import yaml

def run_command_with_output(cmd, cwd=None, timeout=None):
    """运行命令并实时输出到命令行"""
    try:
        print(f"执行命令: {cmd}")
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True, 
            bufsize=1,
            universal_newlines=True,
            cwd=cwd
        )
        
        # 实时输出stdout
        start_time = time.time()
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
            
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                process.terminate()
                return -1, "", f"命令执行超时（{timeout}秒）"
        
        return_code = process.wait()
        return return_code, "", ""
        
    except Exception as e:
        return -1, "", str(e)

def evaluate_wrf():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_code_dir = os.path.join(script_dir, "source_code")
    
    # 超时设置（单位：秒）
    build_wrf_timeout = 60 * 60  # 60分钟
    run_timeout = 20 * 60   # 20分钟
    
    # 初始化两个评测部分的结果
    string_match_result = {
        'performance': 0.0,
        'zero_flag': False,
        'info': '',
        'score': 0.0
    }
    
    time_performance_result = {
        'performance': 0.0,
        'zero_flag': False,
        'info': '',
        'score': 0.0
    }
    
    # 检查 source_code 目录是否存在
    if not os.path.exists(source_code_dir):
        error_msg = f"source_code目录不存在于{script_dir}"
        print(f"错误: {error_msg}")
        string_match_result.update({
            'zero_flag': True,
            'info': 'Compile Error',
            'score': 0.0
        })
        time_performance_result.update({
            'zero_flag': True,
            'info': 'Compile Error',
            'score': 0.0
        })
        return string_match_result, time_performance_result
    
    print(f"工作目录: {source_code_dir}")
    
    # 运行 ./build
    print("=" * 50)
    print("正在运行 ./build ...")
    print("=" * 50)
    
    return_code, stdout, stderr = run_command_with_output("./build", cwd=source_code_dir, timeout=build_wrf_timeout)
    if return_code != 0:
        error_msg = "wrf编译失败"
        if "超时" in stderr:
            error_msg = "wrf编译超时（60分钟）"
        print(f"\n{error_msg}，返回码: {return_code}")
        string_match_result.update({
            'zero_flag': True,
            'info': 'Compile Error',
            'score': 0.0
        })
        time_performance_result.update({
            'zero_flag': True,
            'info': 'Compile Error',
            'score': 0.0
        })
        return string_match_result, time_performance_result
    
    print("\n" + "=" * 50)
    print("build wrf 完成")
    print("=" * 50)
    
    # 运行 ./run 并计时
    print("\n正在运行 ./run ...")
    start_time = time.time()
    return_code, stdout, stderr = run_command_with_output("./run", cwd=source_code_dir, timeout=run_timeout)
    end_time = time.time()
    
    run_time = end_time - start_time
    run_time_minutes = run_time / 60
    
    if return_code != 0:
        error_msg = f"run运行时失败，返回码: {return_code}"
        if "超时" in stderr:
            error_msg = "run运行超时（20分钟）"
        print(error_msg)
        string_match_result.update({
            'zero_flag': True,
            'info': 'Runtime Error',
            'score': 0.0
        })
        time_performance_result.update({
            'zero_flag': True,
            'info': 'Runtime Error',
            'score': 0.0
        })
        return string_match_result, time_performance_result
    
    print(f"./run 完成，运行时间: {run_time_minutes:.2f} 分钟 ({run_time:.2f} 秒)")
    
    # 检查 rsl.out.0000 的最后一行
    rsl_file = os.path.join(source_code_dir, "conus12km", "conus12km", "rsl.out.0000")
    if not os.path.exists(rsl_file):
        error_msg = f"文件 {rsl_file} 不存在"
        print(error_msg)
        string_match_result.update({
            'zero_flag': True,
            'info': 'Log not found',
            'score': 0.0
        })
        time_performance_result.update({
            'zero_flag': True,
            'info': 'Log not found',
            'score': 0.0
        })
        return string_match_result, time_performance_result
    
    with open(rsl_file, 'r') as f:
        lines = f.readlines()
        if not lines:
            error_msg = "rsl.out.0000 文件为空"
            print(error_msg)
            string_match_result.update({
                'zero_flag': True,
                'info': 'Wrong Answer',
                'score': 0.0
            })
            time_performance_result.update({
                'zero_flag': True,
                'info': 'Wrong Answer',
                'score': 0.0
            })
            return string_match_result, time_performance_result
        
        last_line = lines[-1].strip()
    
    # 第一部分：字符串匹配评测
    success_string = "wrf: SUCCESS COMPLETE WRF"
    if success_string in last_line:
        string_match_result.update({
            'performance': 1.0,
            'zero_flag': False,
            'info': 'Accepted',
            'score': 50.0
        })
        print("WRF 运行成功，正确性测试通过，获得50分")
    else:
        string_match_result.update({
            'performance': 0.0,
            'zero_flag': True,
            'info': 'Wrong Answer',
            'score': 0.0
        })
        time_performance_result.update({
            'zero_flag': True,
            'info': 'Wrong Answer',
            'score': 0.0
        })
        print("WRF 运行失败，正确性测试不通过")
        return string_match_result, time_performance_result
    
    # 第二部分：运行时间性能评测
    time_performance_result['performance'] = run_time
    
    # 计算时间得分（线性插值）
    min_time = 10.5 * 60  # 10.5分钟
    max_time = 15.0 * 60  # 15分钟

    if run_time <= min_time:
        time_score = 50.0
        time_performance_result.update({
            'zero_flag': False,
            'info': 'Accepted',
            'score': time_score
        })
    elif run_time >= max_time:
        time_score = 0.0
        time_performance_result.update({
            'zero_flag': False,  # 时间超时但不是zero_flag的情况
            'info': 'Time Limit Exceeded',
            'score': time_score
        })
    else:
        # 线性插值公式
        time_score = 50.0 * (math.log(max_time) - math.log(run_time)) / (math.log(max_time) - math.log(min_time))
        time_performance_result.update({
            'zero_flag': False,
            'info': 'Accepted',
            'score': time_score
        })
    
    print(f"\n=== 评分结果 ===")
    print(f"运行时间: {run_time:.2f} 秒 ({run_time_minutes:.2f} 分钟)")
    print(f"字符串匹配得分: {string_match_result['score']}/50")
    print(f"运行时间得分: {time_performance_result['score']:.2f}/50")
    print(f"总得分: {string_match_result['score'] + time_performance_result['score']:.2f}/100")
    
    return string_match_result, time_performance_result

def save_result_to_yaml(string_result, time_result, filename="result.yaml"):
    """保存结果到YAML文件"""
    # 构建完整的result字典
    final_result = {
        "correctness": string_result,
        "performance": time_result
    }
    
    with open(filename, 'w') as f:
        yaml.dump(final_result, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n结果已保存到 {filename}")

if __name__ == "__main__":
    print("开始评估 WRF 运行...")
    string_result, time_result = evaluate_wrf()
    
    total_score = string_result['score'] + time_result['score']
    print(f"\n最终得分: {total_score:.2f}/100")
    
    # 保存结果到YAML文件
    save_result_to_yaml(string_result, time_result)
    
    print("\n评测完成！")