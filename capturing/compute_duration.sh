#!/bin/bash
ffmpeg -i "$1" 2>&1 | grep -Pi "Duration" | awk -F: '/Duration:/{print $2*3600+$3*60+$4}';