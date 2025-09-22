#!/usr/bin/env bash

# 检查是否提供了参数
if [ $# -ne 1 ]; then
    echo "请提供一个目标文件夹作为参数"
    echo "用法: $0 <目标文件夹>"
    exit 1
fi

target_prefix=$1
echo ====== 开始下载样例（共4组） ======

# 循环处理4个样例
for i in {1..4}; do
    source_dir="/lustre/share/xflops/ocean_sim/Sample$i"
    target_dir="${target_prefix}Sample$i"
    
    cp -r "$source_dir" "$target_dir"
    echo "样例$i 下载完成，保存至 $target_dir"
done

echo ====== 所有样例下载完成 ======