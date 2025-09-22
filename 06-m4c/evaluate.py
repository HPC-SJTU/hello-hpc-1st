#!/usr/bin/env python3
"""
evaluate.py  –  run build, time start, check stdout
"""

import subprocess, time, sys, yaml, os, pathlib

WORK_DIR = pathlib.Path(__file__).resolve().parent

BUILD_SCRIPT = "./build"
START_SCRIPT = "./start"
CWD          = str(WORK_DIR/"source_code")
REFOUT       = "f1edf6c378fb4fdfccdf3cb3f79551232b3c5c6b"

BUILD_TIMEOUT = 5*60
RUN_TIMEOUT = 30

def write_result(score, perf: float, zero_flag: bool, info: str, code: int):
    print(info)
    if not zero_flag:
        print(f"Score: {score:.2f}")
        print(f"Perf: {perf:.2f} s")
    with open(WORK_DIR / "result.yaml", 'w', encoding='utf-8') as f:
        yaml.dump({"m4c":{
            "score": score,
            "performance": perf,
            "zero_flag": zero_flag,
            "info": info,
        }}, f, allow_unicode=True)
    sys.exit(code)

def run(cmd, cwd=CWD, timeout=None):
    """Run `cmd` (a list or str) and return CompletedProcess."""
    if isinstance(cmd, str):
        cmd = [cmd]
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,   # merge stderr into stdout
            text=True,                  # decode bytes → str
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as te:
        write_result(0, 0, True, f"Time Limit Exceeded: {te}", 1)
        raise AssertionError("unreachable")
    except:
        write_result(0, 0, True, f"Runtime Error", 1)
        raise AssertionError("unreachable")

def bindcore():
    res = [i for i in range(128) if subprocess.run(
        ["taskset","-c",str(i),"echo","1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0][:8]
    if len(res) < 8:
        raise RuntimeError(f"Not enough cores: need 8 but only {len(res)} available")
    return ",".join(map(str, res))

def main():
    # build step
    print("Building …")
    build_proc = run([BUILD_SCRIPT], timeout=BUILD_TIMEOUT)
    if build_proc.returncode != 0:
        print(build_proc.stdout)
        write_result(0, 0, True, f"Compile Error", build_proc.returncode)

    # Run and time the program
    print("Running …")
    t0 = time.perf_counter()
    available_cores = bindcore()
    os.environ["M4C_CORES"] = available_cores
    run_proc = run(["taskset", "-c", available_cores, START_SCRIPT], timeout=RUN_TIMEOUT)
    elapsed = time.perf_counter() - t0
    if run_proc.returncode != 0:
        print(run_proc.stdout)
        write_result(0, 0, True, f"Runtime Error", run_proc.returncode)

    score = (1-min(max(((elapsed-5)/20), 0), 1)**1.5) * 100
    out = run_proc.stdout.splitlines()[-1]

    if out == REFOUT:
        write_result(score, elapsed, False, "Accepted", 0)
    else:
        print(run_proc.stdout)
        write_result(0, elapsed, True, "Wrong Answer", 0)

if __name__ == "__main__":
    main()
