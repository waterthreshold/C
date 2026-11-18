#!/bin/sh
echo -e  "Content-type: text/plain\n"

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
if [ "$method" = "Reboot" ]; then
	systemctl reboot
elif [ "$method" = "Loaddefault" ]; then
	loaddefault
elif [ "$method" = "SMTTest" ]; then
	echo "code=1"
fi

