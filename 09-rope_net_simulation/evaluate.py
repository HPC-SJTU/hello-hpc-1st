import subprocess,os
import yaml
import shutil
import time
import math
import logging
import re

from dataclasses import dataclass, asdict

@dataclass
class CaseRes:
    performance: float
    info: str
    score: float
    zero_flag: bool

    @classmethod
    def from_perf(cls, performance: float):
        score = calculate_score(performance)/2
        if score == 50:
            info = "Accepted"
        else:
            info = "Success"
        return cls(performance = performance, info = info, score = score, zero_flag = False)
    
    @classmethod
    def from_zero_flag(cls, info: str, performance: float = 0):
        return cls(performance = performance, info = info, score = 0, zero_flag = True)
    
test_cases = [
        {
            'id': 1,
            'params': '0.001 0.0 5.0',
            'reference': './comparison1.dat'
        },
        {
            'id': 2,
            'params': '0.0001 0.0 0.5',
            'reference': './comparison2.dat'
        }
    ]


def calculate_score(run_time):
    """13s is the full score 100, 420s is 73, 2000s is the zero. A polynomial is used
    to calculate. if a zero-flag or wrong_answer_flag == 1, give a 0. Else, use time to calculate."""
    
    full_score = 100
    full_score_rel_time = 14.8
    middle_score = 73
    middle_score_rel_time = 420
    low_score = 0
    low_score_rel_time = 2000


    if run_time <= 0:
        return low_score
    
    # Define scoring curve: 14.8s = 100, 420s = 73, 2000s = 0
    if run_time <= full_score_rel_time:
        score = full_score
    elif run_time >= low_score_rel_time:
        score = low_score
    else:
        # Polynomial curve fitting points (14.8, 100), (420, 80), (2000, 0)
        t = run_time
        if t <= middle_score_rel_time:
            # Linear interpolation between (14.8, 100) and (420, 73)
            score = (full_score - middle_score) * (math.log(t) - math.log(middle_score_rel_time)) / (math.log(full_score_rel_time)-math.log(middle_score_rel_time)) + middle_score
        else:
            # Quadratic decay from (420, 73) to (2000, 0)
            ratio = (t - middle_score_rel_time) / (low_score_rel_time - middle_score_rel_time)
            score = middle_score * (1 - ratio * ratio)
    
    result = max(0.0, min(full_score, score))
    logging.info(f"Calculated score: {result:.1f} for runtime {run_time:.2f}s")
    return result

def save_data(case_dic: dict[str, CaseRes]):
    """Generate checksum for result file using salt"""
    chars = yaml.safe_dump({k:asdict(v) for k,v in case_dic.items()})
    # Read the result file
    with open('./result.yaml', 'w', encoding='utf-8') as f:
        f.write(chars)

def load_res() -> 'dict[str,CaseRes] | None':
    result_path='./result.yaml'
        
    if not os.path.exists(result_path):
        logging.error("Result file not found")
        return None
        
    # Read the result file
    with open(result_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify
    data_dic = yaml.safe_load(content)
    return {k:CaseRes(**v) for k,v in data_dic.items()}

        
def sanitize_path(path):
    return os.path.abspath(path)
    
def compile():
    """Run the compilation. Use cmake to generate makefile from CMakeLists.txt, then make clean and make."""
    try:
        logging.info("Starting compilation process")
        source_dir = sanitize_path('./source_code')
        
        # Change to source directory
        original_cwd = os.getcwd()
        os.chdir(source_dir)
        
        try:
            logging.info("Cleaning previous temp files...")

            # Clean previous builds
            if os.path.exists('RopeSimulator'):
                os.remove('RopeSimulator')
                logging.info("Removed previous binary")
            
            # Clean previous CMakeCache
            if os.path.exists('build'):
                shutil.rmtree('build')

            # Use cmake to parse CMakeLists.txt and then make
            logging.info("Running cmake and make...")
            res = subprocess.run('cmake -B build && cd build && make && cp ./RopeSimulator ../ && cd ../', shell=True, timeout=120, 
                                 capture_output=True, text=True, cwd=source_dir)

            if res.returncode == 0 and os.path.exists('RopeSimulator'):
                logging.info("Compilation successful")
                return 1
            else:
                logging.error(f"Compilation failed: {res.stderr}")
                return 0
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        logging.error(f"Error in compile(): {str(e)}")
        return 0

def check_correctness(case_id):
    """check the correctness by compare the ./source_code/Solution/result.txt with reference file
    For every number in the file, the reference to minus the result.txt. Obtain the maximum error.
    If this is large than 0.01%, then a zero flag is given. 
    OUTPUT: [wrong-answer-flag(if wrong, give a 1)]."""
    reference_file = f"./comparison{case_id}.dat"
    try:
        logging.info(f"Starting correctness check with reference file: {reference_file}")
        result_path = sanitize_path(f'./result{case_id}.txt')
        reference_path = sanitize_path(reference_file)
        
        if not os.path.isfile(result_path):
            logging.error("Result file not found")
            return [1]
        
        if not os.path.isfile(reference_path):
            logging.error(f"Reference file {reference_file} not found")
            return [1]
        
        # Read result file
        with open(result_path, 'r') as f:
            result_content = f.read().strip()
        
        # if os.path.isfile(result_path):
        #     os.remove(result_path) 
        #     # automatically remove result files after check()

        # Read reference file
        with open(reference_path, 'r') as f:
            reference_content = f.read().strip()
        
        # Parse numbers from both files - line by line comparison
        try:
            result_lines = result_content.strip().split('\n')
            reference_lines = reference_content.strip().split('\n')
            
            if len(result_lines) == 0:
                logging.error("No lines found in result file")
                return [1]
            
            if len(reference_lines) == 0:
                logging.error("No lines found in reference file")
                return [1]
            
            # logging.info(f"Result file has {len(result_lines)} lines")
            # logging.info(f"Reference file has {len(reference_lines)} lines")
            
            # Check if number of lines match
            if len(result_lines) != len(reference_lines):
                logging.warning(f"Line count mismatch: result={len(result_lines)}, reference={len(reference_lines)}")
                # Use minimum number of lines for comparison
            
            min_lines = min(len(result_lines), len(reference_lines))
            max_relative_error = 0.0
            valid_line_comparisons = 0
            
            for line_idx in range(min_lines):
                result_line = result_lines[line_idx].strip()
                reference_line = reference_lines[line_idx].strip()
                
                # Skip empty lines
                if not result_line or not reference_line:
                    continue
                
                # Parse numbers from each line
                result_nums = []
                reference_nums = []
                
                try:
                    result_tokens = result_line.split()
                    for token in result_tokens:
                        try:
                            num = float(token)
                            if not (math.isnan(num) or math.isinf(num)):
                                result_nums.append(num)
                        except ValueError:
                            continue
                    
                    reference_tokens = reference_line.split()
                    for token in reference_tokens:
                        try:
                            num = float(token)
                            if not (math.isnan(num) or math.isinf(num)):
                                reference_nums.append(num)
                        except ValueError:
                            continue
                    
                    # Skip lines with no valid numbers
                    if len(result_nums) == 0 or len(reference_nums) == 0:
                        continue
                    
                    # Calculate sum of numbers in each line
                    result_sum = sum(result_nums)
                    reference_sum = sum(reference_nums)
                    
                    # Calculate relative error for this line
                    if abs(reference_sum) > 1e-10:
                        line_relative_error = abs(reference_sum - result_sum) / abs(reference_sum)
                    else:
                        line_relative_error = abs(reference_sum - result_sum)
                    
                    max_relative_error = max(max_relative_error, line_relative_error)
                    valid_line_comparisons += 1
                    
                    # Log details for first few lines and lines with large errors
                    # if line_idx < 5 or line_relative_error > 0.01:
                    #     logging.info(f"Line {line_idx}: result_sum={result_sum:.6f}, reference_sum={reference_sum:.6f}, "
                    #                f"rel_error={line_relative_error:.6f} ({line_relative_error*100:.4f}%)")
                
                except Exception as line_error:
                    logging.warning(f"Error processing line {line_idx}: {str(line_error)}")
                    continue
            
            if valid_line_comparisons == 0:
                logging.error("No valid line comparisons could be made")
                return [1]
            
            logging.info(f"Maximum relative error (line sums): {max_relative_error:.6f} ({max_relative_error*100:.4f}%)")
            logging.info(f"Valid line comparisons: {valid_line_comparisons}")
            
            # Check if error exceeds 0.01%
            if max_relative_error > 0.0001:  # 0.01%
                logging.warning("Error exceeds 0.5% threshold")
                return [1]
            else:
                logging.info("Correctness check passed")
                return [0]
                
        except Exception as e:
            logging.error(f"Error parsing numbers: {str(e)}")
            return [1]
            
    except Exception as e:
        logging.error(f"Error in check_correctness(): {str(e)}")
        return [1]

def evaluate_single_test_case(test_case_id, test_params:str, reference_file) -> CaseRes:
    """Evaluate a single test case"""
    logging.info(f"=== Evaluating Test Case {test_case_id} ===")
    logging.info(f"Parameters: {test_params}")
    logging.info(f"Reference file: {reference_file}")
    
    # Execute the test case
    try:
        bg_t = time.time()
        subprocess.run(['chmod','+x', "source_code/RopeSimulator"])
        res = subprocess.run(["./RopeSimulator"] + test_params.split() , timeout=1000, cwd=os.path.abspath("source_code"))
        ed_t = time.time()
        run_time = ed_t - bg_t
    except subprocess.TimeoutExpired:
        logging.error(f"Test case {test_case_id} timed out after {2000} seconds.")
        return CaseRes.from_zero_flag("Time Limit Exceeded")
    except Exception as e:
        logging.error(f"Test case {test_case_id} failed with error: {e}")
    if res.returncode != 0:
        return CaseRes.from_zero_flag("Runtime Error")
    
    shutil.move('source_code/Solution/result.txt', f'./result{test_case_id}.txt')
    # Check correctness, now this has been moved to check() part
    # wrong_answer_flag = check_correctness(reference_file)[0]

    return CaseRes.from_perf(run_time)


def run():
    if not compile():
        result_dic = {"compile": CaseRes.from_zero_flag("Compile Error")}
        save_data(result_dic)
        return
    result_dic = {}
    for test_case in test_cases:
        logging.info(f"\n3.{test_case['id']}. Executing Test Case {test_case['id']}...")
        
        # Run the test case
        result = evaluate_single_test_case(
            test_case['id'], 
            test_case['params'], 
            test_case['reference']
        )
        
        result_dic[test_case['id']] = result
    save_data(result_dic)

def check():
    data = load_res()
    if data is None:
        new_data = {"check": CaseRes.from_zero_flag("Check Error")}
        save_data(new_data)
        return
    for caseid, resi in data.items():
        if not resi.zero_flag:
            wa_flag = check_correctness(caseid)[0]
            if wa_flag:
                data[caseid] = CaseRes.from_zero_flag("Wrong Answer", resi.performance)
        
    save_data(data)

def print_summary():
    # Read and print result information
    try:
        data = load_res()
        if data is not None:
            print(f"\n{Colors.BOLD}=== Test Results Summary ==={Colors.RESET}")
            total_score = 0
            for case_id, result in data.items():
                print(f"{Colors.BLUE}Case {case_id}:{Colors.RESET}")
                
                # Performance with color based on time
                perf_time = result.performance
                if perf_time <= 14.8:
                    perf_color = Colors.GREEN  # Good performance
                elif perf_time <= 420:
                    perf_color = Colors.YELLOW  # Moderate performance
                else:
                    perf_color = Colors.RED     # Poor performance
                print(f"  Performance: {perf_color}{result.performance:.3f}s{Colors.RESET}")
                
                # Status with color
                status_color = Colors.GREEN if result.info in ["Accepted", "Success"] else Colors.RED
                print(f"  Status: {status_color}{result.info}{Colors.RESET}")
                
                # Score with color based on value
                score_color = Colors.GREEN if result.score >= 40 else Colors.YELLOW if result.score > 0 else Colors.RED
                print(f"  Score: {score_color}{result.score:.1f}{Colors.RESET}")
                
                # Zero Flag with color
                flag_color = Colors.GREEN if not result.zero_flag else Colors.RED
                flag_text = "False" if not result.zero_flag else "True"
                print(f"  Zero Flag: {flag_color}{flag_text}{Colors.RESET}")
                print()
                
                if not result.zero_flag:
                    total_score += result.score
            
            # Total Score with color and emphasis
            total_color = Colors.GREEN if total_score >= 80 else Colors.YELLOW if total_score >= 50 else Colors.RED
            print(f"{Colors.BOLD}Total Score: {total_color}{total_score:.1f}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Failed to load result data{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error reading result file: {e}{Colors.RESET}")

class Colors:
    # having a colourful logging infos!
    R, G, Y, B, M, C, W = '\033[31m', '\033[32m', '\033[33m', '\033[34m', '\033[35m', '\033[36m', '\033[37m'
    RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = R, G, Y, B, M, C, W
    BOLD, RESET = '\033[1m', '\033[0m'

class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {'DEBUG': Colors.C, 'INFO': Colors.G, 'WARNING': Colors.Y, 'ERROR': Colors.R, 'CRITICAL': Colors.R + Colors.BOLD}
    
    def format(self, record):
        log_color = self.LEVEL_COLORS.get(record.levelname, Colors.W)
        time_str = self.formatTime(record, self.datefmt)
        level_str = log_color + record.levelname + Colors.RESET
        message = record.getMessage()

        # colouring, matching by expresions
        message = re.sub(r'(Correctness check passed)', Colors.G + r'\1' + Colors.RESET, message)
        message = re.sub(r'(Error exceeds 0\.5% threshold)', Colors.R + r'\1' + Colors.RESET, message)
        message = re.sub(r'(score:?\s*)(\d+\.?\d*)', r'\1' + Colors.Y + r'\2' + Colors.RESET, message)
        message = re.sub(r'(\w+\.(txt|dat|yaml|py|cpp|h|cmake|yml))', Colors.B + r'\1' + Colors.RESET, message)
        message = re.sub(r'([\./\w-]+/[\w.-]+)', Colors.B + r'\1' + Colors.RESET, message)
        message = re.sub(r'\b(RopeSimulator|CMakeFiles|Makefile|cmake_install\.cmake|CMakeCache\.txt)\b', Colors.B + r'\1' + Colors.RESET, message)
        message = re.sub(r'(\d+\.?\d*)(s|%)', Colors.M + r'\1' + Colors.RESET + r'\2', message)
        
        return f"{time_str} - {level_str} - {message}"

def setup_colored_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]: logger.removeHandler(handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

setup_colored_logging()
    
if __name__ == "__main__":
    run()
    check()
    print_summary()
    