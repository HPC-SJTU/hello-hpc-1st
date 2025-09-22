import torch
from tqdm import tqdm
import time
import os
from safetensors import safe_open
import sys
import hashlib
def calculate_sha256(input_string):
    # 将字符串转换为字节（使用UTF-8编码）
    byte_data = input_string.encode('utf-8')
    
    # 创建SHA-256哈希对象并更新
    sha256_hash = hashlib.sha256()
    sha256_hash.update(byte_data)
    
    # 获取十六进制表示的哈希值
    return sha256_hash.hexdigest()

if len(sys.argv) != 2:
     print(f"Usage: python {sys.argv[0]} <bound_core>\nex.\tpython {sys.argv[0]} 0-31")
     exit(2)
bound_core = sys.argv[1]
print(f"will bound to {bound_core}")

from vllm.v1.worker.gpu_worker import init_worker_distributed_environment
ret = torch.ops._C_utils.init_cpu_threads_env(bound_core)
if ret:
    print(ret)

res_lst : list[tuple[str, torch.Tensor]] = []
model_path = os.path.expanduser('/lustre/share/xflops/amazing_llm/qwen3-8b-m3/')
hf_weights_files = [os.path.join(model_path, i) for i in os.listdir(model_path)
                    if i.endswith('.safetensors')]
for st_file in tqdm(
        hf_weights_files,
        desc="Loading safetensors checkpoint shards",
):
    with safe_open(st_file, framework="pt") as f:
        res_lst.extend([(namei, f.get_tensor(namei).detach().clone()) for namei in f.keys()])
dequant_bg = time.time()
from q6bit import recover_from_quant
res_lst = recover_from_quant(res_lst)
cal_hash_time = time.time()
res_lst.sort(key=lambda x: x[0])
hash_char = calculate_sha256(''.join([namei+str(parami.flatten()[7].item()) for namei, parami in res_lst]))
dequant_ed = time.time()
print(f"dequant cost {dequant_ed - dequant_bg:.4f} s\n"
        f"cal hash cost {dequant_ed - cal_hash_time:.4f} s\tsha256: {hash_char}")
if hash_char != '6d46f62caef0d415ade2ba0f5d1f1178af39332fba692008c0846417c66550bb':
    print(f"WARNING: hash is not correct, please check")
