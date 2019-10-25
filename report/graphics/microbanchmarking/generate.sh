#!/bin/bash

rm -f results.dat

for i in 1 2 4 8 16 32 64 128;
do
	if [ $i == 1 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 2 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 4 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 8 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 16 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 32 ]; then
		dd bs="${i}"M count=1 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 64 ]; then
		dd bs=32M count=2 if=/dev/urandom of="${i}"M.dat
	fi
	if [ $i == 128 ]; then
		dd bs=32M count=4 if=/dev/urandom of="${i}"M.dat
	fi
	#ls -lash "${i}"M.dat
	for ((j=0;j<100;j++));
	do
		ts=$(date +%s%N)
		openssl aes-128-cbc -md sha1 -in "${i}"M.dat -out "${i}"M.dat.enc -pass pass:12345
		duration=`echo $((($(date +%s%N) - $ts)/1000000));`
		echo "$duration $i $j" >> results.dat
	done
	rm "${i}"M.dat "${i}"M.dat.enc
done
