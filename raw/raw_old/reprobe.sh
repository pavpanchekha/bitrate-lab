#!/bin/sh

netctl stop mit
rmmod ath9k ath9k_common ath9k_hw ath
modprobe ath9k
netctl start mit
