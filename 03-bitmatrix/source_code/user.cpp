#include "common.h"

void masked_bitmatrix_density(
	int             N,
	const uint64_t* matrix,
	const uint64_t* mask,
	uint32_t*       result) {
	const int col_words = N / 64;

	for(int j = 0; j < N; j++) {
		int col_word = j / 64, col_bit = j % 64;
		result[j]  = 0;
		for(int i = 0; i < N; i++) {
			if(mask[i / 64] & (1ULL << (i % 64))) {
				result[j] += (matrix[i * col_words + col_word] >> col_bit) & 1;
			}
		}
	}
}
