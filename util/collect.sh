#!/bin/sh

FILE=$1

cat /proc/ath_rate

while true; do
    cat /proc/ath_rate
    sleep .5
done | tee "$FILE"
