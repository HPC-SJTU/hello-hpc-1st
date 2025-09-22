 															//

#include "calGF.h"

void GravAttraction(const POLYHEDRON &p, double* r, double* F)
{
    int i, j;
    double tmp1, tmp2, omegaf, le;
	double tmpV1[3], tmpV2[3], FF[3] = {0}, EE[3] = {0};
    double tmpVS[9]; // colum has priority: line29~31 
  
    double *RAY = new double[p.NumVerts*4];
    
    for (i=0; i<p.NumVerts; i++)
    {  
		tmpV1[0] = p.Vertices[i];  tmpV1[1] = p.Vertices[i+p.NumVerts];  tmpV1[2] = p.Vertices[i+2*p.NumVerts];
		tmpV2[0] = tmpV1[0]-r[0];  tmpV2[1] = tmpV1[1]-r[1];             tmpV2[2] = tmpV1[2]-r[2];
		tmp1 = sqrt(tmpV2[0]*tmpV2[0]+tmpV2[1]*tmpV2[1]+tmpV2[2]*tmpV2[2]);
		RAY[i] = tmpV2[0];         RAY[i+p.NumVerts] = tmpV2[1];         RAY[i+2*p.NumVerts] = tmpV2[2];        RAY[i+3*p.NumVerts] = tmp1;
    }

    for (i=0; i<p.NumFaces; i++)
    {      
		for (j=0; j<3; j++)
        {
           tmpV1[0] = RAY[p.Faces[i+j*p.NumFaces]];  tmpV1[1] = RAY[p.Faces[i+j*p.NumFaces]+p.NumVerts];  tmpV1[2] = RAY[p.Faces[i+j*p.NumFaces]+2*p.NumVerts]; 		   
		   tmpVS[0+3*j] = tmpV1[0]*(1.0/RAY[p.Faces[i+j*p.NumFaces]+3*p.NumVerts]);
		   tmpVS[1+3*j] = tmpV1[1]*(1.0/RAY[p.Faces[i+j*p.NumFaces]+3*p.NumVerts]);
		   tmpVS[2+3*j] = tmpV1[2]*(1.0/RAY[p.Faces[i+j*p.NumFaces]+3*p.NumVerts]); //r[3][3]
        }	 
		tmpV2[0] = tmpVS[1+1*3]*tmpVS[2+2*3]-tmpVS[2+1*3]*tmpVS[1+2*3];
		tmpV2[1] = tmpVS[2+1*3]*tmpVS[2*3]-tmpVS[0+1*3]*tmpVS[2+2*3];
		tmpV2[2] = tmpVS[0+1*3]*tmpVS[1+2*3]-tmpVS[1+1*3]*tmpVS[2*3];
		tmp1 = tmpV2[0]*tmpVS[0]+tmpV2[1]*tmpVS[1]+tmpV2[2]*tmpVS[2];

		tmp2 = tmpVS[0]*tmpVS[0+3]+tmpVS[1]*tmpVS[1+3]+tmpVS[2]*tmpVS[2+3]+\
			   tmpVS[0+3]*tmpVS[0+2*3]+tmpVS[1+3]*tmpVS[1+2*3]+tmpVS[2+3]*tmpVS[2+2*3]+\
			   tmpVS[0]*tmpVS[0+2*3]+tmpVS[1]*tmpVS[1+2*3]+tmpVS[2]*tmpVS[2+2*3]+1.0;

		omegaf = 2.0*atan2(tmp1, tmp2);
		tmpV2[0] = p.FaceNormVecs[i];  tmpV2[1] = p.FaceNormVecs[i+p.NumFaces];  tmpV2[2] = p.FaceNormVecs[i+2*p.NumFaces];
		tmp1 = tmpV1[0]*tmpV2[0]+tmpV1[1]*tmpV2[1]+tmpV1[2]*tmpV2[2];
		tmpV2[0] *= tmp1*omegaf;  tmpV2[1] *= tmp1*omegaf;  tmpV2[2] *= tmp1*omegaf;
		FF[0] += tmpV2[0]; FF[1] += tmpV2[1]; FF[2] += tmpV2[2];
    }

    for (i=0; i<p.NumEdges; i++)
    {
        tmp1 = RAY[p.Edges[i]+3*p.NumVerts]+RAY[p.Edges[i+p.NumEdges]+3*p.NumVerts];   //tmp
		le = log((tmp1+p.EdgeLens[i])/(tmp1-p.EdgeLens[i]));
		tmpV1[0] = RAY[p.Edges[i]];  tmpV1[1] = RAY[p.Edges[i]+p.NumVerts];  tmpV1[2] = RAY[p.Edges[i]+2*p.NumVerts]; //re        
        
        for (j=0; j<2; j++)
        {
			tmpV2[0] = p.EdgeNormVecs[i+(4*j+1)*p.NumEdges];  tmpV2[1] = p.EdgeNormVecs[i+(4*j+2)*p.NumEdges];  tmpV2[2] = p.EdgeNormVecs[i+(4*j+3)*p.NumEdges]; // ne_data(i,3:5)
			tmp1=tmpV1[0]*tmpV2[0]+tmpV1[1]*tmpV2[1]+tmpV1[2]*tmpV2[2]; //  ne_data(i,3:5)*re'
			tmpV2[0] = p.FaceNormVecs[(int)p.EdgeNormVecs[i+(4*j)*p.NumEdges]];  tmpV2[1] = p.FaceNormVecs[(int)p.EdgeNormVecs[i+(4*j)*p.NumEdges]+p.NumFaces];  tmpV2[2] = p.FaceNormVecs[(int)p.EdgeNormVecs[i+(4*j)*p.NumEdges]+2*p.NumFaces];//nf_data(ne_data(i,2),2:4)			
			tmpV2[0] *= tmp1*le; tmpV2[1] *= tmp1*le; tmpV2[2] *= tmp1*le;
			EE[0] += tmpV2[0]; EE[1] += tmpV2[1]; EE[2] += tmpV2[2];
        }
    }
	F[0] = FF[0] - EE[0];
	F[1] = FF[1] - EE[1];
	F[2] = FF[2] - EE[2];

	delete[] RAY;   RAY = NULL;
}