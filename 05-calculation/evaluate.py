#!/usr/bin/env python3
import os
import subprocess
import argparse
import re
import yaml
import signal
import threading
import time
import math
from statistics import mean
from which_core import get_cores
# 测试配置
TEST_CASES = [1, 2, 3, 4]
BASE_TIMES = {1: 27500, 2: 35000, 3: 2600, 4: 34000}
# FULL_TIMES = {1: 1050, 2: 6600, 3: 140, 4: 1450}
FULL_TIMES = {1: 1200, 2: 6000, 3: 80, 4: 1350}
WEIGHTS = {1: 0.25, 2: 0.35, 3: 0.15, 4: 0.25}
TIMEOUT_MULTIPLIER = 100  # 超时倍数

# 全局变量用于进程控制
# current_process = None
# process_timed_out = False

# def get_cores():
#     """获取可用的CPU核心列表"""
#     try:
#         result = subprocess.run(['python', 'which_core.py'], 
#                               capture_output=True, text=True, check=True)
#         match = re.search(r'\[([\d,\s-]+)\]', result.stdout)
#         if match:
#             core_str = match.group(1)
#             cores = []
#             for part in core_str.split(','):
#                 part = part.strip()
#                 if '-' in part:
#                     start, end = map(int, part.split('-'))
#                     cores.extend(range(start, end + 1))
#                 else:
#                     cores.append(int(part))
#             return cores
#     except:
#         return list(range(0, 16))  # 默认返回0-15核心

def compile_program():
    """编译程序"""
    if not os.path.exists('source_code'):
        print("Error: source_code directory not found!")
        return False
    
    os.chdir('source_code')
    if not os.path.exists('compile.sh'):
        print("Error: compile.sh not found!")
        return False
    
    os.chmod('compile.sh', 0o755)
    result = subprocess.run(['./compile.sh'], capture_output=True)
    if result.returncode != 0:
        print("Compilation failed!")
        print(result.stderr.decode())
        return False
    
    if not os.path.exists('calculation'):
        print("Error: calculation executable not generated!")
        return False
    
    os.chdir('..')
    return True

def timeout_monitor(process, timeout_sec, case_id, timeout_flag):
    """超时监控线程函数"""
    # global process_timed_out
    
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        if process.poll() is not None:  # 进程已经结束
            return
        time.sleep(0.1)  # 每100ms检查一次
    
    # 超时处理
    # process_timed_out = True
    timeout_flag[0] = True  # 使用列表作为可变的引用
    print(f"Case {case_id} timed out after {timeout_sec} seconds, terminating...")
    
    # 终止进程
    try:
        process.terminate()
        # 等待进程结束
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        print("Process did not terminate gracefully, killing...")
        process.kill()

def run_test_case(case_id, cores, num_runs):
    """运行测试算例并返回结果"""
    # global current_process, process_timed_out
    
    data_file = os.path.join('data', f'conf{case_id}.data')
    ref_file = os.path.join('data', f'ref{case_id}.data')
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found!")
        return None

    core_str = ','.join(map(str, cores))
    cmd = ['taskset', '-c', core_str, 'source_code/calculation', data_file, ref_file, str(num_runs)]
    
    # process_timed_out = False
    timeout_flag = [False]  # 使用列表以便在线程中修改
    
    try:
        # 计算超时时间（毫秒转换为秒）
        timeout_sec = BASE_TIMES[case_id] * TIMEOUT_MULTIPLIER * 10 / 1000000  # 微秒转换为秒
        
        # 启动进程
        process = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        # current_process = process
        
        # 启动超时监控线程
        timeout_thread = threading.Thread(
            target=timeout_monitor, 
            args=(process, timeout_sec, case_id, timeout_flag)
        )
        timeout_thread.daemon = True
        timeout_thread.start()
        
        # 等待进程完成
        stdout, stderr = process.communicate()
        
        # if process_timed_out:
        if timeout_flag[0]:
            return {'timeout': True}
        
        # if process.returncode != 0:
        #     print(f"Error running case {case_id}: {stderr}")
        #     return None
        if process.returncode != 0:
            error_msg = stderr.strip()
            if not error_msg:
                # 如果没有stderr输出，根据返回码判断错误类型
                if process.returncode < 0:
                    # 负的返回码通常表示被信号终止
                    signal_num = -process.returncode
                    if signal_num == signal.SIGSEGV:
                        error_msg = "Segmentation fault"
                    elif signal_num == signal.SIGABRT:
                        error_msg = "Aborted"
                    elif signal_num == signal.SIGFPE:
                        error_msg = "Floating point exception"
                    else:
                        error_msg = f"Process terminated by signal {signal_num}"
                else:
                    error_msg = f"Process exited with code {process.returncode}"
            
            print(f"Error running case {case_id}: {error_msg}")
            return {'error': error_msg, 'returncode': process.returncode}
        
        # return parse_output(stdout)
        result = parse_output(stdout)
        if result:
            result['case_id'] = case_id
        return result
        
    except Exception as e:
        print(f"Exception running case {case_id}: {str(e)}")
        return None
    # finally:
    #     current_process = None

def parse_output(output):
    """解析程序输出（新的两行格式）"""
    lines = output.strip().split('\n')
    result = {
        'avg_time': None,
        'pass_fail': None,
        'timeout': False
    }
    
    if len(lines) >= 2:
        # 第一行是平均时间
        try:
            result['avg_time'] = float(lines[0].strip())
        except ValueError:
            print(f"无法解析时间: {lines[0]}")
            return None
        
        # 第二行是PASS/FAIL
        result['pass_fail'] = lines[1].strip().upper()
    
    return result if all([result['avg_time'] is not None, result['pass_fail']]) else None

def calculate_score(case_id, avg_time, pass_fail, timeout=False):
    """计算得分并返回结果字典"""
    result = {
        'performance': avg_time if not timeout else BASE_TIMES[case_id] * TIMEOUT_MULTIPLIER,
        'zero_flag': False,
        'info': 'Success',
        'score': 0.0
    }
    
    # 检查是否超时
    if timeout:
        result['zero_flag'] = True
        result['info'] = 'Time Limit Exceeded'
        result['score'] = 0.0
        return result
    
    # 检查答案是否正确
    if pass_fail != 'PASS':
        result['zero_flag'] = True
        result['info'] = 'Wrong Answer'
        result['score'] = 0.0
        return result
    
    # 答案正确，计算性能得分
    full_time = FULL_TIMES[case_id]
    base_time = BASE_TIMES[case_id]
    if full_time >= result['performance']:
        result['info'] = 'Accepted'
    
    if avg_time <= full_time:
        result['score'] = 100.0 * WEIGHTS[case_id]
    elif avg_time >= base_time:
        result['zero_flag'] = True
        result['info'] = 'Time Limit Exceeded'
        result['score'] = 0.0
    else:
        # ratio = (full_time * (base_time - avg_time)) / (avg_time * (base_time - full_time))
        # result['score'] = min(max(ratio, 0), 1) * 100 * WEIGHTS[case_id]
        ln = math.log
        result['score'] = min(1, (ln(base_time) - ln(avg_time)) / (ln(base_time) - ln(full_time))) * 100 * WEIGHTS[case_id]
    return result

def generate_yaml(results):
    """生成YAML结果文件"""
    yaml_data = {}
    for case_id in TEST_CASES:
        if case_id in results:
            yaml_data[case_id] = results[case_id]
        else:
            # 如果测试算例失败，添加默认的失败结果
            yaml_data[case_id] = {
                'performance': 0,
                'zero_flag': True,
                'info': 'Test Failed',
                'score': 0.0
            }
    
    with open('result.yaml', 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(description='性能评测脚本')
    parser.add_argument('-t', '--num-runs', type=int, default=80,
                      help='每个测试算例的运行次数')
    args = parser.parse_args()
    
    print("="*50)
    print("开始评测")
    print("="*50)
    
    # 获取CPU核心
    cores = get_cores()
    print(f"使用的CPU核心: {cores}")
    
    # 编译程序
    print("\n编译程序中...")
    if not compile_program():
        return
    
    total_score = 0.0
    results = {}
    yaml_results = {}
    
    # 运行所有测试算例
    for case_id in TEST_CASES:
        print(f"\n{'='*20} 测试算例 {case_id} {'='*20}")
        
        result = run_test_case(case_id, cores, args.num_runs)
        if not result:
            print(f"测试算例 {case_id} 失败，跳过")
            # 为失败的测试算例创建默认结果
            yaml_results[case_id] = {
                'performance': 0,
                'zero_flag': True,
                'info': 'Test Failed',
                'score': 0.0
            }
            continue
        # 如果是错误结果（包含error字段）
        if 'error' in result:
            print(f"测试算例 {case_id} 执行错误: {result['error']}")
            yaml_results[case_id] = {
                'performance': 0,
                'zero_flag': True,
                'info': f"Runtime Error: {result['error']}",
                'score': 0.0
            }
            continue
        if result.get('timeout', False):
            # 计算得分（超时情况）
            score_result = calculate_score(case_id, 0, 'FAIL', True)
            total_score += score_result['score']
            
            yaml_results[case_id] = score_result
            print(f"测试算例 {case_id} 超时")
            continue
        # 计算得分
        # timeout = result.get('timeout', False)
        score_result = calculate_score(
            case_id, 
            result.get('avg_time', 0), 
            result.get('pass_fail', 'FAIL'),
            False
        )
        total_score += score_result['score']
        
        results[case_id] = {
            'avg_time': result.get('avg_time', 0),
            'pass_fail': result.get('pass_fail', 'FAIL'),
            'score': score_result['score'],
            'timeout': False
        }
        
        yaml_results[case_id] = score_result
        
        # 打印结果
        print(f"\n测试算例 {case_id} 结果:")
        # if timeout:
        #     timeout_ms = BASE_TIMES[case_id] * TIMEOUT_MULTIPLIER
        #     print(f"- 状态: 超时 (超过 {timeout_ms} μs)")
        # else:
        #     print(f"- 时间: {result['avg_time']:.2f} μs")
        #     print(f"- 结果: {result['pass_fail']}")
        print(f"- 时间: {result['avg_time']:.2f} μs")
        print(f"- 结果: {result['pass_fail']}")
        print(f"- 得分: {score_result['score']:.2f}")
        print(f"- 本算例分值: {(WEIGHTS[case_id] * 100):.2f}")
        print(f"- 信息: {score_result['info']}")
        print(f"- 零分标志: {score_result['zero_flag']}")
    
    # 生成YAML文件
    generate_yaml(yaml_results)
    print(f"\n结果已保存到 result.yaml")
    
    # 打印最终结果
    print("\n" + "="*50)
    print("最终评测结果")
    print("="*50)
    
    for case_id in TEST_CASES:
        if case_id in results:
            print(f"算例 {case_id}: {results[case_id]['score']:.2f}")
    
    print(f"\n总得分: {total_score:.2f}")
    print("="*50)

if __name__ == "__main__":
    main()