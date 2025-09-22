#include "common.h"
#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <memory>
#include <random>
#include <tuple>

static std::mt19937_64 rng;

uint32_t compute_checksum(const uint32_t* data, int N, uint32_t key) {
	constexpr uint32_t prime  = 0x9e3779b9; // (sqrt(5)-1)/2 * 2^32
	uint32_t           result = 0;
	for(int i = 0; i < N; i++) {
		result ^= data[i] * prime + key;
		result = (result << 13) | (result >> 19);
	}
	return result;
}

auto gen_data(int N) {
	auto matrix_size = N * N / 64, mask_size = N / 64;
	auto matrix = std::make_unique<uint64_t[]>(matrix_size);
	auto mask   = std::make_unique<uint64_t[]>(mask_size);
	for(int i = 0; i < matrix_size; ++i) {
		matrix[i] = rng();
	}
	for(int i = 0; i < mask_size; ++i) {
		mask[i] = rng();
	}
	return std::make_tuple(std::move(matrix), std::move(mask));
}

auto bench(size_t rep, double warmup_rate = 0.0, double ignore_rate = 0.0) {
	return [=](auto&& func) {
		size_t              count        = rep;
		size_t              warmup_count = static_cast<size_t>(count * warmup_rate);
		size_t              ignore_count = static_cast<size_t>(count * ignore_rate);
		double              mean, stddev;
		std::vector<double> durations(count);
		for(size_t i = 0; i < warmup_count; ++i) {
			func(); // Warmup to avoid cold start effects
		}
		for(size_t i = 0; i < count; ++i) {
			auto start = std::chrono::steady_clock::now();
			func();
			durations[i] = (std::chrono::steady_clock::now() - start).count() / 1e6; // Convert to milliseconds
		}
		std::sort(durations.begin(), durations.end());
		if(ignore_count > 0) {
			durations.erase(durations.begin(), durations.begin() + ignore_count);
			durations.erase(durations.end() - ignore_count, durations.end());
		}
		count -= 2 * ignore_count; // Adjust count after ignoring extremes
		mean   = std::accumulate(durations.begin(), durations.end(), 0.0) / count;
		stddev = std::accumulate(durations.begin(), durations.end(), 0.0, [mean](double acc, double val) {
			return acc + (val - mean) * (val - mean);
		});
		stddev = std::sqrt(stddev / count);
		return std::make_tuple(mean, stddev);
	};
}

int main(int argc, char* argv[]) {
	if(argc < 2 || argc > 5) {
		fprintf(stderr, "Usage: %s <N> [rep = 1000] [seed = 42] [key = 0xDEADBEAF]\n", argv[0]);
		return 1;
	}
	int      N    = std::atoi(argv[1]);
	uint32_t rep  = (argc > 2) ? std::atoi(argv[2]) : 1000;
	uint32_t seed = (argc > 3) ? std::atoi(argv[3]) : 42;
	uint32_t key  = (argc > 4) ? std::atoi(argv[4]) : 0xDEADBEAF;

	rng.seed(seed);

	assert(N % 64 == 0);

	auto [matrix_, mask_] = gen_data(N);
	// Fix for old clang complaining about 'reference to local binding declared in enclosing function'
	auto matrix = std::move(matrix_), mask = std::move(mask_);
	auto result = std::make_unique<uint32_t[]>(N);

	auto [mean, stddev] = bench(rep, 0.05, 0.01)([&]() {
		memset(result.get(), 0, N * sizeof(uint32_t)); // Clear result buffer
		masked_bitmatrix_density(N, matrix.get(), mask.get(), result.get());
	});

	uint32_t checksum = compute_checksum(result.get(), N, key);
	printf("Checksum: 0x%08X\tMean: %f us\tStddev: %f us\n", checksum, mean * 1000.0, stddev * 1000.0);

	return 0;
}
