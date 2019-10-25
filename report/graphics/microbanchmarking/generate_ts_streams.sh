#!/bin/bash

rm -f results.dat

czap -r 'Uzbekiston(uctv)' -c channels.conf > /dev/null 2>&1&
sleep 5;

for i in 10 20 30 40 50 60 70 80 90 100;
do
        echo "Capturing stream for $i seconds...";
        cat /dev/dvb/adapter0/dvr0 > sequence.ts &
        sleep $i;
        pid=`ps aux | grep -P "cat \/dev\/dvb" | awk -F" " '{print $2}'`
        kill -9 $pid > /dev/null 2>&1;
        print "Converting the file 100 times...";
        for ((j=0;j<100;j++));
        do
                ts=$(date +%s%N);
                ffmpeg -i sequence.ts -c:v copy -c:a copy sequence.m2ts > /dev/null 2>&1
                duration=`echo $((($(date +%s%N) - $ts)/1000000));`
                rm sequence.m2ts
                echo "$duration $i $j" >> results.dat
        done
done

pid=`ps aux | grep -P "czap" | awk -F" " '{print $2}'`
kill -9 -1 $pid;