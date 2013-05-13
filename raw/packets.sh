cat "$1" | grep -v : | cut -f10 -d\  | sort -n | uniq -c
