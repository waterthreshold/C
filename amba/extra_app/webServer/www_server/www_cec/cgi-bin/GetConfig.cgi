#!/bin/sh
echo "Content-Type: application/octet-stream"
echo "Content-Disposition: attachment; filename=db.bin"
echo ""   # End of headers
/bin/cat  /var/lib/redis/dump.rdb