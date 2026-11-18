#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BOUNDARY 256
#define BUFFER_SIZE 65536   // 64 KB chunks

int main(void) {
    char *content_length_str = getenv("CONTENT_LENGTH");
    if (!content_length_str) {
        printf("Content-Type: text/plain\n\nMissing CONTENT_LENGTH\n");
        return 1;
    }

    long content_length = atol(content_length_str);
    if (content_length <= 0) {
        printf("Content-Type: text/plain\n\nInvalid CONTENT_LENGTH\n");
        return 1;
    }

    // Get boundary from Content-Type header
    char *content_type = getenv("CONTENT_TYPE");
    char boundary[MAX_BOUNDARY] = {0};
    if (content_type && sscanf(content_type, "multipart/form-data; boundary=%255s", boundary) != 1) {
        printf("Content-Type: text/plain\n\nMissing boundary\n");
        return 1;
    }

//	long final_boundarylen = strlen (boundary) + 2 * strlen("\r\n");
//	printf ("%d %d \n",final_boundarylen,strlen(boundary));
    // Skip the initial boundary and headers
    char buf[BUFFER_SIZE];
    long remaining = content_length -46  ;//- final_boundarylen;
    FILE *outfile = fopen("/tmp/uploaded.bin", "wb");
    if (!outfile) {
        printf("Content-Type: text/plain\n\nCannot open output file\n");
        return 1;
    }

    // Simple method: skip headers until blank line (CRLF)
    int in_file = 0;
    while (remaining > 0) {
        size_t to_read = remaining > BUFFER_SIZE ? BUFFER_SIZE : remaining;
        size_t n = fread(buf, 1, to_read, stdin);
        if (n == 0) break;
        remaining -= n;
		
    	    if (!in_file) {
    	        // Look for double CRLF (\r\n\r\n)
    	        char *p = strstr(buf, "\r\n\r\n");
				//char *b = strstr(buf, boundary);
    	        if (p) {
    	            in_file = 1;
    	            size_t offset = (p - buf) + 4;
    	            fwrite(buf + offset, 1, n - offset, outfile);
            	}
				/*else if (b)
				{
					char *s = strstr(buf,"\r\n");
					char *e = strstr(s,"\r\n");
			//sizeof (*(e-s))i;
					size_t offset_len = e - s + 2;
					fwrite (buf , 1, n - offset_len, outfile);
					break;
				}*/
 
        } else {
            fwrite(buf, 1, n, outfile);
        }
    }

    fclose(outfile);
    // Respond to browser
    printf("Content-Type: text/html\n\n");
    //>printf("<html><Upload complete\n");
	printf("<html><body>Upload complete<script>setTimeout(function() {window.location.href = \"/progress.html\";}, 1000);</script></body></html>\n");
//	system("/usr/local/bin/upgradeCecFW.sh");
    return 0;
}

