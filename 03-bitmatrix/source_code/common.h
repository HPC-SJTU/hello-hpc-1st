#pragma once

#include <cstdint>

void masked_bitmatrix_density(
	int             N,
	const uint64_t* matrix,
	const uint64_t* mask,
	uint32_t*       result);
