#include <iostream>
#include <random>
#include <chrono>
#include <cmath>
#include <fstream>
#include <numeric>
#include "query_sum.h"
using namespace std;
using namespace std::chrono;

// const size_t MAX_N = 1000000;
size_t TEST_COUNT = 100; // 测试次数

double measure_performance(size_t (*func)(short[], size_t, size_t, double), 
                         short A[], size_t n, size_t m, double k, 
                         size_t& result_out) {
    vector<long> durations;
    size_t result = 0;
    
    for (size_t i = 0; i < TEST_COUNT; ++i) {
        auto start = high_resolution_clock::now();
        result = func(A, n, m, k);
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(end - start);
        durations.push_back(duration.count());
    }
    
    // 保存结果
    result_out = result;
    
    // 计算平均时间（忽略第一次可能存在的冷启动）
    long sum = accumulate(durations.begin() + 1, durations.end(), 0L);
    double average = static_cast<double>(sum) / (TEST_COUNT - 1);
    
    return average;
}

// 从参考文件中读取预期结果
size_t read_expected_result(const string& filename) {
    ifstream ref_file(filename);
    if (!ref_file) {
        return 0;
    }
    
    size_t expected_result;
    ref_file >> expected_result;
    ref_file.close();
    
    return expected_result;
}

int main(int argc, char* argv[]) {
    // 检查命令行参数
    if (argc < 3) {
        return 1;
    }

    // 获取数据文件路径
    std::string filename = argv[1];
    std::string ref_filename = argv[2];
    // 获取测试次数（如果提供）
    if (argc > 3) {
        try {
            TEST_COUNT = std::stoul(argv[3]);
        } catch (...) {
            return 1;
        }
    }

    std::ifstream in(filename);
    if (!in) {
        return 1;
    }

    
    // 读取n和k
    size_t n;
    double k;
    in >> n >> k;
    size_t m = ((int)std::pow(n, k) + 10);
    short *A = new short[(n + 1) * m + 10];
    
    // 读取数组A
    size_t i = 1, j = 1;
    short value;
    while (in >> value) {
        A[i * m + j] = value;
        if (++j > pow(i, k)) {
            i++;
            j = 1;
        }
    }
    in.close();
    
    size_t actual_result;
    double avg_time = measure_performance(sum, A, n, m, k, actual_result);
    
    // 构建参考文件名
    string base_filename = filename.substr(filename.find_last_of("/\\") + 1);
    // 读取预期结果
    size_t expected_result = read_expected_result(ref_filename);
    
    // 输出最终结果（两行）
    cout << avg_time << endl; // 第一行：平均时间
    // 第二行：PASS或FAIL
    if (actual_result == expected_result) {
        cout << "PASS" << endl;
    } else {
        cout << "FAIL" << endl;
    }
    
    delete[] A;
    return 0;
}