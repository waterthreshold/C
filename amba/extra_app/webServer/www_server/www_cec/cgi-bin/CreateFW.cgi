#!/bin/sh
# /usr/local/bin/GenCECfw.sh > /dev/null
# source ./global.sh
echo "Content-Type: application/octet-stream"
echo "Content-Disposition: attachment; filename=db.bin"
echo ""   # End of headers


# /bin/cat /tmp/`/bin/ls -1 /tmp/ | grep -E Larnaca2*.bin`
/bin/cat /tmp/uploaded.bin
