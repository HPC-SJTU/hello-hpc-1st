 																		//

#include "LoadFNS.h"

void LoadFNS(const char* filename, FNS &fns)
{
	int i,j;
	//
	FILE * infile;
	infile = fopen(filename, "r");

	// input numbers of points, edges, ropenodes, colum of mateix TP, Radius
	fscanf(infile, "%d %d %d %d %lf", &fns.NP, &fns.NumEdges, &fns.NumRopeNodes, &fns.col_Topo, &fns.Radius);

	FNSMemoryAlloc(fns);

	// input Ed data
	for (i = 0; i<fns.NumEdges; i++)
	{
		fscanf(infile, "%d%d", &fns.Ed[i], &fns.Ed[fns.NumEdges+i]);
	}	

	// input TP data
	for (i = 0; i < fns.NP; i++)
	{
		for (j = 0; j < fns.col_Topo; j++)
		{
			fscanf(infile, "%d", &fns.TP[i+j*fns.NP]);
		}	
	}

	// input Pt data
	for (i = 0; i<fns.NP; i++)
	{
		fscanf(infile, "%lf%lf%lf", &fns.Pt[i], &fns.Pt[i+fns.NP],&fns.Pt[i+2*fns.NP]);
	}

	// input EL data
	for (i = 0; i<fns.NumEdges; i++)
	{
		fscanf(infile, "%lf", &fns.EL[i]);
	}

	// input BL data
	for (i = 0; i < fns.NP; i++)
	{
		for (j = 0; j < fns.NP; j++)
		{
			fscanf(infile, "%lf", &fns.BL[i+j*fns.NP]);
		}	
	}
	fclose(infile);
}

void FNSMemoryAlloc(FNS &fns)
{
	int i;

	// memory for Ed data
	fns.Ed = new int[2*fns.NumEdges];
	for (i = 0; i<2*fns.NumEdges; i++) fns.Ed[i]=0;

	// memory for TP data
	fns.TP = new int[(fns.NP)*(fns.col_Topo)];
	for (i = 0; i<(fns.NP)*(fns.col_Topo); i++) fns.TP[i]=0;

	// memory for Pt data
	fns.Pt = new double[3*fns.NP];
	for (i = 0; i<3*fns.NP; i++) fns.Pt[i]=0.0;

	// memory for EL data
	fns.EL = new double[fns.NumEdges];
	for (i = 0; i<fns.NumEdges; i++) fns.EL[i]=0.0;

	// memory for BL data
	fns.BL = new double[(fns.NP)*(fns.NP)];
	for (i = 0; i<(fns.NP)*(fns.NP); i++) fns.BL[i] = 0.0;
}