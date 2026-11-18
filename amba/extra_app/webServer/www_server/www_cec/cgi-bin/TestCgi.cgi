#!/bin/sh

# echo  "Accept-Ranges: bytes"

COUNT=$(wc -c <<EOF
<html>
<body>
Processing...
<script>
setTimeout(function() {
    window.location.href = "/progress.html";
}, 1000);
</script>
</body>
</html>
EOF
)
echo  "Content-Type: text/html"
echo "Content-Length: ${COUNT}"
echo ""

/bin/cat <<EOF
<html>
<body>
Processing...
<script>
setTimeout(function() {
    window.location.href = "/progress.html";
}, 1000);
</script>
</body>
</html>
EOF