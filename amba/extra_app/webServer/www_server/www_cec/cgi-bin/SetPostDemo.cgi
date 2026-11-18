#!/bin/sh
# POST SetNetwork.cgi 
# curl -X POST -d "ip=camerea&ping=pong" http://admin:admin@172.16.7.82/cgi-bin/SetPostDemo.cgi
echo "Content-type: text/plain"
echo ""
read -n "$CONTENT_LENGTH" POST_STRING
echo "CONTENT LENGTH: $CONTENT_LENGTH"
echo "Data: ${POST_STRING}"
env