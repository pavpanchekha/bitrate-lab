#!/bin/sh

netctl store
netctl stop-all
rmmod ath9k ath9k_common ath9k_hw ath
modprobe ath9k
netctl restore
