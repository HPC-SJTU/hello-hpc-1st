 																	//

#include "LoadPolyhedron.h"

void PolyhedronMemoryAlloc(POLYHEDRON& p)
{
    p.Vertices = new double[3 * p.NumVerts]();
    p.Faces = new int[3 * p.NumFaces]();
    p.Edges = new int[4 * p.NumEdges]();
    p.EdgeLens = new double[p.NumEdges]();
    p.EdgeNormVecs = new double[8 * p.NumEdges]();
    p.FaceNormVecs = new double[3 * p.NumFaces]();
}

void LoadPolyhedron(const char* filename, POLYHEDRON& p)
{
	int i;
	//
	FILE* infile;
	infile = fopen(filename, "r");

	// input numbers of vertices, faces, edges
	fscanf(infile, "%d %d %d %lf", &p.NumVerts, &p.NumFaces, &p.NumEdges, &p.Density);

	//
	PolyhedronMemoryAlloc(p);

	// input vertices data
	for (i = 0; i < p.NumVerts; i++)
	{
		fscanf(infile, "%lf%lf%lf", &p.Vertices[i], &p.Vertices[p.NumVerts + i], &p.Vertices[2 * p.NumVerts + i]);
	}

	// input faces data
	for (i = 0; i < p.NumFaces; i++)
	{
		fscanf(infile, "%d%d%d", &p.Faces[i], &p.Faces[p.NumFaces + i], &p.Faces[2 * p.NumFaces + i]);
	}

	// input edges data
	for (i = 0; i < p.NumEdges; i++)
	{
		fscanf(infile, "%d%d%d%d", &p.Edges[i], &p.Edges[p.NumEdges + i], &p.Edges[2 * p.NumEdges + i], &p.Edges[3 * p.NumEdges + i]);
	}

	// input len data
	for (i = 0; i < p.NumEdges; i++)
	{
		fscanf(infile, "%lf", &p.EdgeLens[i]);
	}

	// input ne data
	for (i = 0; i < p.NumEdges; i++)
	{
		fscanf(infile, "%lf%lf%lf%lf%lf%lf%lf%lf", &p.EdgeNormVecs[i], &p.EdgeNormVecs[p.NumEdges + i], &p.EdgeNormVecs[2 * p.NumEdges + i], &p.EdgeNormVecs[3 * p.NumEdges + i], \
			& p.EdgeNormVecs[4 * p.NumEdges + i], &p.EdgeNormVecs[5 * p.NumEdges + i], \
			& p.EdgeNormVecs[6 * p.NumEdges + i], &p.EdgeNormVecs[7 * p.NumEdges + i]);
	}

	// input nf data
	for (i = 0; i < p.NumFaces; i++)
	{
		fscanf(infile, "%lf%lf%lf", &p.FaceNormVecs[i], &p.FaceNormVecs[p.NumFaces + i], &p.FaceNormVecs[2 * p.NumFaces + i]);
	}

	fclose(infile);
}
