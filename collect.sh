#!/bin/sh

PORT=$1
FILE=$2
SEC=$3
ITER=$((2*SEC))

if [ -f "raw/$FILE.trace" -a "$FILE" != "test" ]; then
    echo "File 'raw/$FILE.trace' already exists; will not overwrite"
    exit 1
fi

echo "Reprobing wifi driver (this may take a while)"
sudo util/reprobe.sh
echo "Starting packet spew"
python util/spew.py "$PORT" &

# Clear the stored buffer
cat /proc/ath_rate >/dev/null

echo "Starting capture"
cat /proc/ath_rate

while [ $ITER -ne 0 ]; do
    cat /proc/ath_rate
    sleep .5
    ITER=$((ITER - 1))
done | tee "raw/$FILE.trace"

echo "Capture done"
kill %python

echo "Check: all numbers from 0 to 11 appear in the right hand column:"
util/packets.sh "raw/$FILE.trace"

echo "Munging data"
python util/munge.py <"raw/$FILE.trace" "data/$FILE.dat"
