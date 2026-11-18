#!/bin/sh

code=-1
source ./global.sh


while IFS= read -r cmd; do
    # echo "eval $cmd"
    eval "$cmd"
done <<EOF
$(echo "$QUERY_STRING" | awk '{
    n = split($0, pairs, "&");
    for (i = 1; i <= n; i++) {
        split(pairs[i], kv, "=");
        print kv[1] "=" kv[2];
    }
}')
EOF

hostnamectl set-hostname ${hostname}
redis-cli SET hostname "${hostname}" > /dev/null
# shmoo_setting ${shmoo}
redis-cli SET shmoo "${shmoo}" > /dev/null
# redis-cli SET timestamp ${timestamp} > /dev/null
code=$?

echo -e  "Content-type: text/plain\n"
echo "code=${code}"


timestamp.sh ${timestamp}