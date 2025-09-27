import os
import re
import subprocess
import sys
from typing import Dict, Optional, Tuple
from types import SimpleNamespace

import argparse
import yaml


def parse_args():
    # Fixed, not configurable via CLI
    timeout = 40 * 60  # 2400 seconds
    script = os.path.join(os.path.dirname(__file__), "source_code", "graph.sh")
    return SimpleNamespace(timeout=timeout, script=script)



# Scoring config per README
CASE_DEF = {
    1: {
        "name": "bfs",
        "ratio": 0.60,
        "full": 1.4e9,
        "base": 3.0e8,
        "label_patterns": [
            # Match like: bfs  harmonic_mean_TEPS:     !  5.28466e+08
            r"\bbfs\b\s*harmonic[_\s-]*mean[_\s-]*teps\s*[:=]\s*[^0-9eE+\-.]*([0-9eE+\-.]+)",
            r"harmonic\s*mean.*teps.*bfs\s*[:=]\s*[^0-9eE+\-.]*([0-9eE+\-.]+)",
        ],
    },
    2: {
        "name": "sssp",
        "ratio": 0.40,
        "full": 4.5e8,
        "base": 6.0e7,
        "label_patterns": [
            r"\bsssp\b\s*harmonic[_\s-]*mean[_\s-]*teps\s*[:=]\s*[^0-9eE+\-.]*([0-9eE+\-.]+)",
            r"harmonic\s*mean.*teps.*sssp\s*[:=]\s*[^0-9eE+\-.]*([0-9eE+\-.]+)",
        ],
    },
}


def run_script(script_path: str, timeout: int) -> Tuple[int, str, str]:
    """Run the provided shell script and capture output."""
    if not os.path.isfile(script_path):
        return 127, "", f"Script not found: {script_path}"

    # Prefer bash; fallback to sh
    shell = "bash"
    try:
        proc = subprocess.run(
            [shell, script_path],
            cwd=os.path.join(os.path.dirname(__file__),"source_code"),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:

        try:
            proc = subprocess.run(
                ["source", script_path],
                cwd=os.path.join(os.path.dirname(__file__),"source_code"),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except FileNotFoundError as e:
            return 127, "", f"No shell to run script: {e}"

    except subprocess.TimeoutExpired:
        return 124, "", "Time Limit Exceeded"


def parse_teps(output: str) -> Tuple[Dict[str, Optional[str]], Dict[str, Optional[float]]]:
    """Extract BFS/SSSP harmonic mean TEPS values from output.
    Returns (raw_strings, numeric_values).
    """
    raw: Dict[str, Optional[str]] = {"bfs": None, "sssp": None}
    vals: Dict[str, Optional[float]] = {"bfs": None, "sssp": None}
    # Normalize case for regex with IGNORECASE
    for _, cfg in CASE_DEF.items():
        name = cfg["name"]
        for pat in cfg["label_patterns"]:
            m = re.search(pat, output, flags=re.IGNORECASE)
            if m:
                token = m.group(1).strip()
                raw[name] = token
                try:
                    vals[name] = float(token)
                except ValueError:
                    vals[name] = None
                break
    return raw, vals


def score_value(actual: Optional[float], base: float, full: float) -> float:
    if actual is None:
        return 0.0
    # Formula: ((actual-base)/(full-base))^3
    denom = (full - base)
    if denom <= 0:
        return 0.0
    x = (actual - base) / denom
    if x < 0:
        x = 0.0
    return min(max(x ** 2, 0.0), 1.0)


def main():
    args = parse_args()
    script_path = args.script

    # Initialize result dict
    res_dict: Dict[int, Dict[str, object]] = {
        i: {"info": "Success", "performance": 0.0, "zero_flag": 0} for i in CASE_DEF.keys()
    }

    # Run the user script
    print(f"Running script: {os.path.relpath(script_path, os.path.dirname(__file__))}")
    code, out, err = run_script(script_path, timeout=args.timeout)

    if code != 0:
        print(f"Script failed with code {code}")
        if err:
            print(err.strip())
        for i in CASE_DEF.keys():
            res_dict[i]["info"] = f"Runtime Error"
            res_dict[i]["zero_flag"] = 1
        # Write result and exit
        with open(os.path.join(os.path.dirname(__file__), "result.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(res_dict, f, allow_unicode=True, sort_keys=True)
        sys.exit(1)

    # Parse TEPS from output
    raw_teps, teps = parse_teps(out)
    print("Parsed TEPS:")
    print({k: (raw_teps[k] or teps[k]) for k in ["bfs", "sssp"]})

    # Compute scores
    total_score = 0.0
    for i, cfg in CASE_DEF.items():
        name = cfg["name"]
        perf = teps.get(name)
        res_dict[i]["performance"] = float(perf) if perf is not None else 0.0
        if perf is None:
            res_dict[i]["info"] = "Wrong Answer"
            res_dict[i]["zero_flag"] = 1
            res_dict[i]["score"] = 0.0
            continue

        s = score_value(perf, base=cfg["base"], full=cfg["full"])  # 0..1
        if s >= 1.0 - 1e-12:
            res_dict[i]["info"] = "Accepted"
        weighted = cfg["ratio"] * s 
        res_dict[i]["score"] = weighted*100
        total_score += weighted
        # Display original scientific notation if available
        display_val = raw_teps.get(name)
        if not display_val and perf is not None:
            # Fallback to a compact representation without thousands separators
            display_val = f"{perf:.4g}"
        max_points = int(round(cfg["ratio"] * 100))  # 60 for bfs, 40 for sssp
        case_points = weighted * 100  # weighted score in points
        print(
            f"Case {name} score: {case_points:.2f}/{max_points}\t {name}_harmonic_mean_TEPS: {display_val}"
        )

    print(f"Your total score: {total_score*100:.2f}/100")

    # Write YAML result in the project root to match prior behavior
    with open(os.path.join(os.path.dirname(__file__), "result.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(res_dict, f, allow_unicode=True, sort_keys=True)


if __name__ == "__main__":
    main()
