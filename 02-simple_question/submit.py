import fnmatch
import os, yaml
import sys
import zipfile
from typing import List, Tuple

def parse_patterns(pattern_lst: List[str]) -> Tuple[List[str], List[str]]:
    include_patterns = []
    exclude_patterns = []
    
    for pattern in pattern_lst:
        if pattern.startswith('!'):
            exclude_patterns.append(pattern[1:])
        else:
            include_patterns.append(pattern)
            
    return include_patterns, exclude_patterns

def match_pattern(path: str, patterns: List[str]) -> bool:
    # 标准化路径，使用/作为分隔符
    normalized_path = path.replace(os.sep, '/')
    
    for pattern in patterns:
        # 处理目录模式（以/结尾）
        if pattern.endswith('/'):
            if not os.path.isdir(path):
                continue
            pattern = pattern[:-1]
            
        # 处理**通配符
        if '**' in pattern:
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                # 检查前缀和后缀是否匹配
                prefix_match = normalized_path.startswith(prefix.replace('/', os.sep)) if prefix else True
                suffix_match = normalized_path.endswith(suffix.replace('/', os.sep)) if suffix else True
                if prefix_match and suffix_match:
                    return True
        else:
            # 普通模式匹配
            if fnmatch.fnmatch(normalized_path, pattern):
                return True
                
    return False

def get_directories_to_check(root_dir: str, include_patterns: List[str]):

    dirs_to_check = {}
    dirs_to_check_recursive = {}
    direct_add_set = set()

    for pattern in include_patterns:
        # 处理包含**的模式，需要递归检查
        if '**' in pattern:
            prefix = pattern.split('**')[0]
            if '/' not in prefix:
                dirs_to_check_recursive[root_dir] = dirs_to_check_recursive.get(root_dir, []) + [pattern]
            else:
                check_dir = os.path.join(root_dir, prefix[:prefix.rfind('/')])
                dirs_to_check_recursive[check_dir] = dirs_to_check_recursive.get(check_dir, []) + [pattern]
            continue

        if '*' in pattern:
            lst = pattern.split('*')
            assert len(lst) == 2, f"Invalid pattern: {pattern}"
            assert '/' not in lst[1], f"Invalid pattern: {pattern}"
            dir_part = lst[0].replace('/', os.sep)
            check_dir = os.path.join(root_dir, dir_part)
            dirs_to_check[check_dir] = dirs_to_check.get(check_dir, []) + [pattern]
            continue

        if pattern.endswith('/'):
            dir_part = os.path.dirname(pattern).replace('/', os.sep)
            check_dir = os.path.join(root_dir, dir_part)
            dirs_to_check_recursive[check_dir] = dirs_to_check_recursive.get(check_dir, []) + [pattern]
        else:
            direct_add_set.add(pattern)
    
    return dirs_to_check, dirs_to_check_recursive, direct_add_set

def find_matching_files(root_dir: str, include_patterns: List[str], exclude_patterns: List[str]) -> set[str]:
    matching_files = set()
    dirs_to_check, dirs_to_check_recursive, direct_add_set = get_directories_to_check(root_dir, include_patterns)
    
    # 遍历需要检查的目录
    for dir_path in dirs_to_check_recursive:
        for root, _, files in os.walk(dir_path):
            # 计算相对路径用于模式匹配
            rel_root = os.path.relpath(root, root_dir)
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.join(rel_root, file)
                
                # 检查是否匹配包含模式且不匹配排除模式
                if match_pattern(rel_path, include_patterns) and \
                   not match_pattern(rel_path, exclude_patterns):
                    matching_files.add(file_path)
    
    for dir_path in dirs_to_check:
        rel_root = os.path.relpath(dir_path, root_dir)
        for fi in os.listdir(dir_path):
            rel_path = os.path.join(rel_root, fi)
            if match_pattern(rel_path, include_patterns) and \
              not match_pattern(rel_path, exclude_patterns):
                matching_files.add(os.path.join(dir_path, fi))
    matching_files.update(direct_add_set)
    return matching_files

def zip_files(file_paths: set[str], zip_filename: str, root_dir: str) -> None:
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            # 计算在zip中的相对路径
            file_path = os.path.join(work_dir, file_path)
            arcname = os.path.relpath(file_path, root_dir)
            zipf.write(file_path, arcname)
            print(f"已添加到zip: {arcname}")

def package_files_by_patterns(root_dir: str, patterns: List[str], zip_filename: str = "output.zip") -> None:
    # 解析模式
    include_patterns, exclude_patterns = parse_patterns(patterns)
    
    # 查找匹配的文件
    print(f"在 {root_dir} 中搜索匹配的文件...")
    matching_files = find_matching_files(root_dir, include_patterns, exclude_patterns)
    
    if not matching_files:
        print("未找到匹配的文件。")
        return
    
    # 打包成zip
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    print(f"正在创建zip文件: {zip_filename}")
    zip_files(matching_files, zip_filename, root_dir)
    
    print(f"成功创建 {zip_filename}，包含 {len(matching_files)} 个文件。")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print('Usage: python submit.py [stage_flag]')
        exit(2)

    if len(sys.argv) == 2:
        stage_flag = sys.argv[1]
        try:
            stage_flag = int(stage_flag)
        except:
            pass
    else:
        stage_flag = 0

    work_dir = os.path.dirname(__file__)

    with open(os.path.join(work_dir, 'submit.yaml')) as f:
        submit_dic = yaml.safe_load(f)

    if stage_flag not in submit_dic:
        print(f'stage_flag: {stage_flag} is not in submit.yaml')
        exit(1)

    pattern_lst = submit_dic[stage_flag]
    package_files_by_patterns(work_dir, pattern_lst, "submit.zip")
