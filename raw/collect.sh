#!/bin/sh

FILE=$1

while true; do
    tail -n1 /proc/ath_rate
done | uniq
