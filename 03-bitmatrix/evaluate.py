import argparse
import os
import random
import re
import subprocess
import yaml
from dataclasses import dataclass

argparser = argparse.ArgumentParser()
argparser.add_argument("--seed", type=int, default=0, help="Random seed")
argparser.add_argument("--key", type=int, default=0, help="Checksum key")
args = argparser.parse_args()

random.seed()
if args.seed == 0:
    args.seed = random.randint(0, 2**31 - 1)
if args.key == 0:
    args.key = random.randint(2**30, 2**31 - 1)
print(f"Using seed: {args.seed}, key: {args.key}")
cwd = os.path.dirname(__file__)


@dataclass
class TestCase:
    score: float
    size: int
    rep: int
    tmin: float  # μs
    tmax: float  # μs


test_cases = [
    TestCase(score=20, size=512, rep=10000, tmin=9.5, tmax=237.5),
    TestCase(score=20, size=1024, rep=5000, tmin=32, tmax=800),
    TestCase(score=30, size=2048, rep=1000, tmin=123, tmax=3075),
    TestCase(score=30, size=4096, rep=500, tmin=495, tmax=12375),
]
n_case = len(test_cases)


def check_clang():
    try:
        subprocess.run(["clang++", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_core(i: int):
    run = subprocess.run(["taskset", "-c", str(i), "echo", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return run.returncode


def run_compile():
    os.makedirs(f"{cwd}/build", exist_ok=True)
    run = subprocess.run(
        ["clang++", "-O3", "-std=c++20", "source_code/main.cpp", "source_code/ref.cpp", "-o", "build/ref"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    assert run.returncode == 0, "Reference Compile Error, PLEASE DO NOT MODIFY ref.cpp or main.cpp"
    run = subprocess.run(
        ["clang++", "-O3", "-std=c++20", "source_code/main.cpp", "source_code/user.cpp", "-o", "build/user"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    assert run.returncode == 0, "Compile Error"


def run_case(i):
    test_case = test_cases[i]
    try:
        run = subprocess.run(
            ["taskset", "-c", core_chars, "build/user", str(test_case.size), str(test_case.rep), str(args.seed), str(args.key)],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=test_case.rep * test_case.tmax / 1e6 * 1.5 + 5,  # timeout in seconds
        )
        ref_run = subprocess.run(
            ["taskset", "-c", core_chars, "build/ref", str(test_case.size), "1", str(args.seed), str(args.key)],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError("Time Limit Exceeded")
    assert run.returncode == 0 and ref_run.returncode == 0, f"Runtime Error"
    checksum, time = re.match(r"Checksum: 0x([0-9A-F]+)\tMean: ([\d.]+) us", run.stdout).group(1, 2)
    ref_checksum = re.match(r"Checksum: 0x([0-9A-F]+)", ref_run.stdout).group(1)
    assert checksum == ref_checksum, "Wrong Answer"
    print(f"Checksum: 0x{checksum}\tMean: {time} us")
    return float(time)


if __name__ == "__main__":
    if not check_clang():
        print(f"make sure you have run `module load bisheng/2.5.0`")
        exit(1)

    # find cores
    res_lst = []
    for i in range(128):
        if check_core(i) == 0:
            res_lst.append(i)
    if not len(res_lst) >= 1:
        print(f"No enough cores: need 1 but now is {len(res_lst)}")
        exit(1)

    core_chars = ",".join([str(i) for i in res_lst[:1]])
    print(f"Using cores: {core_chars}")

    res_dict = {
        i: {
            "info": "Success",
            "performance": 0.0,
            "zero_flag": 0,
            "score": 0.0,
        }
        for i in range(1, n_case + 1)
    }
    try:
        try:
            run_compile()
        except AssertionError as e:
            print(e)
            for i in range(1, n_case + 1):
                res_dict[i]["info"] = e.args[0]
                res_dict[i]["zero_flag"] = 1
            raise

        for i in range(1, n_case + 1):
            print(f"Running case {i}/{n_case}")
            try:
                time = run_case(i - 1)
            except AssertionError as e:
                print(f"Running case {i} failed: {e}")
                res_dict[i]["info"] = e.args[0]
                res_dict[i]["zero_flag"] = 1
                continue

            res_dict[i]["performance"] = time

        score = 0
        for i in range(1, n_case + 1):
            test_case = test_cases[i - 1]
            time = res_dict[i]["performance"]
            if res_dict[i]["zero_flag"] or test_case.score == 0:
                continue
            if time > test_case.tmax:
                res_dict[i]["info"] = "Time Limit Exceeded"
                case_score = 0.0
            elif time <= test_case.tmin:
                res_dict[i]["info"] = "Accepted"
                case_score = 1.0
            else:
                r1 = test_case.tmin / time
                r2 = (test_case.tmax - time) / (test_case.tmax - test_case.tmin)
                p = 0.5
                case_score = (r1**p) * r2
            score += test_case.score * case_score
            res_dict[i]["score"] = test_case.score * case_score
            print(f"Case {i} score: {case_score * 100:6.2f}/100 \ttime: {time:.3f} us")
        print(f"Total  score: {score:6.2f}/100")
    finally:
        yaml.dump(res_dict, open(f"{cwd}/result.yaml", "w"))
