#!/bin/bash

# For now lets only copy the stream
#mv $1.raw $1.ts

# Flash player does not support the MPEG2 audio 
# and only AAC can be decoded. So we need to 
# reencode the stream
# One important thing. We need to pass parameter copyts
# otherwise the timestampts are not copied correctly 
# and the video cannot be decoded correctly in the browser
ffmpeg -f mpegts -i "$1.raw" -copyts -vcodec copy -c:a aac -ignore_unknown -f mpegts -metadata service_provider="Vizly.net" -metadata service_name="TV stream" "$1.ts" > /dev/null 2>&1
rm "$1.raw"
#ffmpeg -v error -i $1.ts -f null - &> corruptions.log
