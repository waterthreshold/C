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

UPLOADSRV_BIN="/root/PartitionUploadSrv_5.0.21"
check_process_name(){
	PROCESS_NAME=${UPLOADSRV_BIN##*/}
	if pgrep -f "$DAEMON_NAME" > /dev/null; then
		
		return 0
	else
		
		return 1
	fi
}
case "$Action" in 
	"start")
		
		if [ $? -ne 0 ]; then
			eval "${UPLOADSRV_BIN} >/dev/null 2>&1 &"
			code=0
		else 
			code=1
		fi
		;;
	"stop")
		killall ${UPLOADSRV_BIN##*/}
		code=0
		;;
	*)
		code=-1
		;;
esac

echo -e  "Content-type: text/plain\n"
echo "code=${code}"