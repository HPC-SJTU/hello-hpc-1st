 																//

#include "MatrixOperations.h"

void MatrixMulti(const int arow, const int acolbrow, const int bcol, const double* A, const double* B, double* C)
{
	int i, j, k;
	for (i = 0; i < arow; i++){
		for (j = 0; j < bcol; j++){
			for (k = 0; k < acolbrow; k++){
				C[j*arow+i] += A[k*acolbrow+i]*B[j*acolbrow+k];
			}
		}
	}
}



