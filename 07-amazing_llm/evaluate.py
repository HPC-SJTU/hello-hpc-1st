import hashlib
import math
import os
import re
import subprocess
import requests
import time
import socket
import signal
import yaml
from openai import OpenAI
from dataclasses import dataclass, asdict

work_dir = os.path.dirname(__file__)

# find cores
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



def stream_completion(prompt, model_name, port:int):
    client = OpenAI(api_key="111", base_url= f'http://localhost:{port}/v1')
    try:
        stream = client.completions.create(
            model=model_name,
            prompt= prompt,
            stream=True,
            temperature=0.8,
            seed= 42,
            max_tokens= 200 ,
        )
        
        answer_chars = []
        for chunk in stream:
            if chunk.choices[0].text is not None:
                print(chunk.choices[0].text, end="", flush=True)
                answer_chars.append(chunk.choices[0].text)
        print()
    except Exception as e:
        print(f"发生错误: {e}")
    return ''.join(answer_chars)

@dataclass
class CaseConfig:
    case_name: 'str|int'
    case_full_score: float
    case_full_time: float
    case_base_time: float

    def case_score(self, performance: float):
        score_ratio = (math.log(self.case_base_time) - math.log(performance))/ \
                    (math.log(self.case_base_time) - math.log(self.case_full_time))
        return self.case_full_score * min(max(0, score_ratio), 1)

@dataclass
class CaseRes:
    performance: float
    info: str
    score: float
    zero_flag: bool

    @classmethod
    def from_perf(cls, case_cfg: CaseConfig, performance: float):
        score = case_cfg.case_score(performance)
        if score == case_cfg.case_full_score:
            info = "Accepted"
        else:
            info = "Success"
        return cls(performance = performance, info = info, score = score, zero_flag = False)
    
    @classmethod
    def from_zero_flag(cls, info: str, performance: float = 0):
        return cls(performance = performance, info = info, score = 0, zero_flag = True)

def calculate_string_sha3_512(input_string: str, encoding: str = 'utf-8') -> str:
    byte_data = input_string.encode(encoding)
    sha3_512_hash = hashlib.sha3_512(byte_data)
    return sha3_512_hash.hexdigest()

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

def eval_case1():
    ans_path = os.path.join(work_dir, 'source_code/ans.txt')
    if not os.path.exists(ans_path):
        print(f"{ans_path} is not exist!")
        return CaseRes.from_zero_flag("Wrong Answer")
    with open(ans_path,'r') as f:
        chars = f.read()
    res_hash = calculate_string_sha3_512(chars)
    if res_hash != ans_hash:
        return CaseRes.from_zero_flag("Wrong Answer")
    else:
        return CaseRes(performance=0, info="Accepted", score=case_cfg_lst[0].case_full_score,
                        zero_flag=False)

def eval_case2(use_port: int, test_times = 3):
    env_dict = os.environ.copy()
    try:
        print("="*20, "installing q6bit", "="*20)
        res = subprocess.run(["pip", "install", ".", "--no-build-isolation"], cwd= os.path.join(work_dir, "source_code/quant"))
        if res.returncode != 0:
            return CaseRes.from_zero_flag("Compile Error")
    except:
        return CaseRes.from_zero_flag("Compile Error")
    print("="*20, "install q6bit finished", "="*20)
    env_dict["VLLM_CPU_KVCACHE_SPACE"] = "20"
    env_dict["VLLM_CPU_OMP_THREADS_BIND"] = use_core_char
    test_time_lst = []
    for i in range(test_times+1):
        p = subprocess.Popen(["vllm", "serve", llm_path , "--port", 
                                str(use_port), "--max-num-seqs", "1024", "-tp", "1", "--max_model_len", "2048",
                                "--dtype", "float16", "-O0"], stderr= subprocess.PIPE, stdout = subprocess.PIPE,
                                env= env_dict, text=True)
        bg_time = time.time()
        print("wait for vllm start cost 0 s", end="")
        while 1:
            try:
                res = requests.get(f"http://localhost:{use_port}")
                if res.status_code == 404:
                    break
            except:
                pass
            time.sleep(1)
            wait_time = time.time() - bg_time
            print(f"\rwait for vllm start cost {wait_time:.2f} s", end="")
            if wait_time > 750:
                return CaseRes.from_zero_flag("Runtime Error (vllm start timeout)")
            if p.poll():
                stdout, stderr = p.communicate()
                print(f"\nvllm start failed!\nstdout=\n{stdout}\nstderr=\n{stderr}")
                return CaseRes.from_zero_flag("Runtime Error (vllm start failed)")
        print()
        print("="*20, "vllm start finished", "="*20)
        ans = stream_completion(test_question, llm_path, use_port)
        now_hash = calculate_string_sha3_512(ans)
        if now_hash != ans_hash:
            print(f"{now_hash=} not match {ans_hash=}")
            return CaseRes.from_zero_flag("Wrong Answer")
        else:
            p.send_signal(signal.SIGINT)
            stdout, stderr = p.communicate()
            dequant_time = re.findall(r'dequant cost (\d+\.\d+) s', stdout)
            if not dequant_time or len(dequant_time) > 1:
                return CaseRes.from_zero_flag("Runtime Error")
            else:
                test_time_lst.append(float(dequant_time[0]))
                if i>0:
                    print(f"finished eval: {i} / {test_times}, result {dequant_time[0]} s")
                else:
                    print(f"finished warmup, result {dequant_time[0]} s")
    avg_times = sum(test_time_lst[1:])/test_times
    if test_time_lst[0] > max(1.5 * test_times, test_times + 1.5):
        return CaseRes.from_zero_flag("Cold Start too Long")
    assert len(test_time_lst) == test_times + 1
    return CaseRes.from_perf(case_cfg_lst[1], avg_times)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18000)
    parser.add_argument('--stage', type=int, default=0)
    args = parser.parse_args()
    ans_hash = "8c3f35a74625c55f6480f892905c9dbac23f714f7f4e686f534f3af9e02c0b5d9c7884ef44647119e4d050b2a1414268f1f60cc2b685fdf33b93c27c8df24ab5"
    llm_path = "/lustre/share/xflops/amazing_llm/qwen3-8b-m3/"
    test_question = "The meaning of life is"
    case_cfg_lst = [CaseConfig("install", 30, 0, 0), CaseConfig("optimize", 70, 0.9, 6.2)]

    res_dict : dict['str|int', CaseRes]= {}
    res1 = eval_case1()
    print(f"case {case_cfg_lst[0].case_name}: {res1.score} / {case_cfg_lst[0].case_full_score}")
    res_dict[case_cfg_lst[0].case_name] = res1
    if args.stage == 1:
        use_port = args.port
        while is_port_in_use(use_port):
            print(f"{use_port} is used, try port {use_port+1}")
            use_port += 1
        res2 = eval_case2(use_port)
        print(f"case {case_cfg_lst[1].case_name}: {res2.score} / {case_cfg_lst[1].case_full_score}")
        res_dict[case_cfg_lst[1].case_name] = res2
    print(f"your score: {sum(v.score for v in res_dict.values()):.2f} / 100")
    yaml.dump({k:asdict(v) for k,v in res_dict.items()}, open(os.path.join(work_dir, "result.yaml"), "w"))
