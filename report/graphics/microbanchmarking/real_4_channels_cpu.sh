#!/bin/bash

rm -rf cpu_usage_rpi_4_channels.dat; while true; do top -b -n 1 | tail -n +8 | awk -F" " '{sum+=$9} END {print sum}' >> cpu_usage_rpi_4_channels.dat; sleep 0.1; done
