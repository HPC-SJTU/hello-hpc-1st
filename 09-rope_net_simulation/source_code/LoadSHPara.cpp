 																//

#include "SHPara.h"

void LoadSHPara(const char* filename, double* SurfacePara)
{
	int i, tmp, a=0;

	FILE * infile;
	infile = fopen(filename, "r");

	// input Sperical Harmous Parameters: lmax=25
	tmp=(SHlmax+1)*(SHlmax+2)/2;
	for (i = 0; i < tmp; i++)
	{
		fscanf(infile, "%lf %lf %lf %lf", &SurfacePara[i], &SurfacePara[i+tmp], &SurfacePara[i+2*tmp], &SurfacePara[i+3*tmp]);
	}	

	fclose(infile);
}