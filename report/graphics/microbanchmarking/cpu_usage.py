#!/usr/bin/python

# https://github.com/Leo-G/DevopsWiki/wiki/How-Linux-CPU-Usage-Time-and-Percentage-is-calculated
import time;
count = 0;
total_idle = 0;
total_idle_prev = 0;
total_prev = 0;
total = 0;

while True:
	time.sleep(1);
	f=open("/proc/stat");
	rec = f.readline().split();
	f.close();
	total_idle = float(rec[4]) + float(rec[5]);
	total = float(rec[1]) + float(rec[2]) + float(rec[3]) + float(rec[4]) + float(rec[5]) + float(rec[6]) + float(rec[7]) + float(rec[8])
	count += 1;
	if count == 1:
		total_prev = total;
		total_idle_prev = total_idle;
		continue;
	else:
		#print total, total_prev, total_idle, total_idle_prev
		print "%f" % (100.0 - ((total_idle - total_idle_prev) / (total - total_prev) * 100.0));
		#print "%f" % ((total_idle - total_idle_prev) / (total - total_prev) * 100.0);
		total_prev = total;
		total_idle_prev =total_idle;
	