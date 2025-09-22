import subprocess

def check_core(i : int):
    run_res = subprocess.run(["taskset", "-c", str(i), "echo","1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return run_res.returncode

def get_cores():
    res_lst = []
    for i in range(128):
        if check_core(i) == 0:
            res_lst.append(i)
            if len(res_lst) >= 8:  # 找到16个就停止
                break
    # print(f"get cores: {res_lst}")
    return res_lst

if __name__ == '__main__':
    print(f"get cores: {get_cores()}")