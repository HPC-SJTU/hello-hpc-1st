import os, subprocess
import argparse
import socket

parser = argparse.ArgumentParser()
parser.add_argument('-port', type=int, default= 18000)

args = parser.parse_args()

llm_path = "/lustre/share/xflops/amazing_llm/qwen3-8b-m3/"

def check_core(i : int):
    run_res = subprocess.run(["taskset", "-c", str(i), "echo","1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return run_res.returncode
res_lst = []
for i in range(128):
    if check_core(i) == 0:
        res_lst.append(i)
if not len(res_lst) >= 32:
    print(f"No enough cores: need 32 but now is {len(res_lst)}")
    exit(1)
continuous_cores_lst : list[tuple[int, int]] = []
now_ind = 0
queue_start = 0
while now_ind < len(res_lst) - 1:
    if res_lst[now_ind] + 1 == res_lst[now_ind+1]:
        now_ind +=1
    else:
        now_ind +=1
        continuous_cores_lst.append((queue_start, now_ind - queue_start))
        queue_start = now_ind
if queue_start < len(res_lst) - 1:
    continuous_cores_lst.append((queue_start, len(res_lst) - 1))
continuous_cores_lst.sort(key=lambda x: x[1], reverse=True)
if continuous_cores_lst[0][1] < 31:
    print(f"No enough continuous cores: need 32 but now is {continuous_cores_lst[0][1]}"
          f"({res_lst[continuous_cores_lst[0][0]]} - {res_lst[continuous_cores_lst[0][0]+continuous_cores_lst[0][1]]})")
    exit(1)
use_core_char = f"{res_lst[continuous_cores_lst[0][0]]}-{res_lst[continuous_cores_lst[0][0]+31]}"
print(f"will run vllm in {use_core_char}")

def is_port_in_use(port: int, host: str = 'localhost') -> bool:
    try:
        # 创建socket对象
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 尝试绑定端口
            s.bind((host, port))
        # 绑定成功，端口未被占用
        return False
    except socket.error as e:
        if e.errno == 98:
            return True
        return False

use_port = args.port
while is_port_in_use(use_port):
    print(f"{use_port} is used, try to use port {use_port+1}")
    use_port += 1

env_dict = os.environ.copy()

env_dict["VLLM_CPU_KVCACHE_SPACE"] = "20"
env_dict["VLLM_CPU_OMP_THREADS_BIND"] = use_core_char

subprocess.run(["vllm", "serve", llm_path , "--port", 
                str(use_port), "--max-num-seqs", "1024", "-tp", "1", "--max_model_len", "2048",
                "--dtype", "float16", "-O0"], env= env_dict)