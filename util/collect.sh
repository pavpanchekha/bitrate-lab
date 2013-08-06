#!/bin/sh

PORT=$1
FILE=$2
SEC=$3
ITER=$((2*SEC))

echo "Reprobing wifi driver (this may take a while)"
sudo ./reprobe.sh
echo "Starting packet spew"
python ./spew.py "$PORT" &

# Clear the stored buffer
cat /proc/ath_rate >/dev/null

echo "Starting capture"
cat /proc/ath_rate

while [ $ITER -ne 0 ]; do
    cat /proc/ath_rate
    sleep .5
    ITER=$((ITER - 1))
done | tee "$FILE"

echo "Capture done"
kill %python

echo "Check: all numbers from 0 to 11 appear in the right hand column:"
./packets.sh "$FILE"
