#!/bin/bash
rm -rf out.cap
tcpdump -i any -s 1518 -w out.cap 'tcp port 80' &
ts=$(date +%s%N);
sleep 300;
killall tcpdump;
duration=`echo $((($(date +%s%N) - $ts)/1000000000));`
bytes=`ls -las out.cap | awk -F" " '{print $6}'`
tp=`echo "$bytes/$duration*8/1024/1024" | bc -l`
echo "Bytes transmitted: $bytes";
echo "Duration: $duration";
echo "Throughput: $tp Mb/s";
rm -rf out.cap
