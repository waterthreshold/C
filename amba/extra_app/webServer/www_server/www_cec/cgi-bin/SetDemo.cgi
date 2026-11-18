#!/bin/sh

# Output HTTP header
echo "Content-type: text/plain"
echo ""

# Get PATH_INFO (e.g., /Camera=1)
path="$PATH_INFO"

# Remove leading slash
path="${path#/}"

# Split into key=value
key="${path%%=*}"
value="${path#*=}"

# Output result
echo "Key: $key"
echo "Value: $value"
echo "$PATH_INFO"
echo "Query_string: $QUERY_STRING"