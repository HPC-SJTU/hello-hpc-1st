#!/usr/bin/env bash

echo ====== 开始下载样例至当前工作目录（共4组） ======

dirpath=$(dirname $0)

# 循环处理4个样例
for i in {1..4}; do
    source_dir="/lustre/share/xflops/ocean_sim/Sample$i"
    target_dir="$dirpath/Sample$i"
    
    cp -r "$source_dir" "$target_dir"
    echo "样例$i 下载完成，保存至 $target_dir"
done

echo ====== 所有样例下载完成 ======