#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>
#include <string.h>

void print_usage(){
	printf("filecut decription input file trucate file\n ");
	printf("-i input file (must need)\n");
	printf("-o output file (option) default stdout\n");
	printf("-s start postion (option) start from 0\n");
	printf("-f offest (option) end to EOF\n");
}
enum ERR_TYPE
{
	ENUM_FILENOTEXIST_ERR=1,
	ENUM_FILEOPENHNDLE_ERR,
	ENUM_NOTDEFINEOFFSET_ERR,
	ENUM_NOTSUPPORTOPT_ERR,
	ENUM_ENDOFFILE_ERR
};


int main (int argc ,char **argv){
	int  ch;
	char inputfile[256]={0};
	char output_name[256]={0};
	char *buffer=NULL;
	unsigned int offset =0;
	unsigned int start=0;
	FILE *fp=NULL,*fp_out=NULL;
	//int use_stdout=0;
	unsigned int n;
	while ((ch = getopt(argc, argv, "i:o:s:f:")) != -1) {
	 	switch (ch){
			case 'i':
					strncpy(inputfile,optarg,sizeof(inputfile));
					break;
			case 'o':
					strncpy(output_name,optarg,sizeof(output_name));
					break;
			case 's':
//						printf("s=%s\n",optarg);
					start=atoi(optarg);
					break;
			case 'f':
//						printf("f=%s\n",optarg);
					offset=atoi(optarg);
					break;
			default:
					print_usage();
					exit(ENUM_NOTSUPPORTOPT_ERR);
					break;
			
		}
	 }

//	printf("input=%s %d %d \n",inputfile,start,offset);

	if (strlen(inputfile)<=0){
			print_usage ();
			exit( ENUM_FILENOTEXIST_ERR); 
	}

	fp=fopen(inputfile,"r");
	if (fp ==NULL){
		perror ("open input file:");
		exit(ENUM_FILEOPENHNDLE_ERR);
	}
	fseek(fp,start,SEEK_SET);

	if (strlen(output_name)<=0){
		fp_out=stdout;

	}
	else {
		fp_out= fopen (output_name,"w");
		if (fp_out==NULL){
			perror("out file error:");
			exit(ENUM_FILEOPENHNDLE_ERR);
		}
	}
	if (offset>0 ) { 
		buffer= (char* )malloc (offset);
	} else {
		exit( ENUM_NOTDEFINEOFFSET_ERR);
	}
	if ( feof(fp) ){
		exit(ENUM_ENDOFFILE_ERR);
	}
	unsigned int remaining = offset;
	printf ("offset = %u\n",offset );
	while (remaining > 0 ){
		n= fread (buffer,1,offset,fp);	
		int n1 = fwrite (buffer,1,n,fp_out);
		//printf ("Write %d Bytes\n",n1);
		remaining -= n;
		//printf ("remaining=%d\n",remaining);
	}
		//offset-=1;
		// printf ("expectation only one times!!\n");
	// }
	if (fp!=NULL)
		fclose (fp);
	if (fp_out!=NULL)
		fclose (fp_out);
	return 0;
}
