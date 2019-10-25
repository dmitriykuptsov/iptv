# Useful links

Structure of the M3U8 file, which is used in HLS to retrieve the next chunk containing encoded video and audio from the server, is discussed in the following proposal.

https://tools.ietf.org/html/draft-pantos-http-live-streaming-19

The encryption and decryption of Transport Streams (TS) is discussed in the following paper:

https://ris.utwente.nl/ws/portalfiles/portal/24821147/Breaking_DVB_CSA.pdf

Geniatech T230C2 drivers and firmware:

https://www.linuxtv.org/wiki/index.php/Geniatech_T230C2

Once the Geniatech T230C2 DVB card is inserted into the USB port, follow the instructions provided in the link above to compile and install the drivers and firmware for the card. After installation reboot the system and the DVB card should be attached to the Linux system. We can then run w_scan tool to scan the spectrum for TV channels.  

If the compilation fails on Raspberry PI, with missing build folder, follow these instructions

https://www.linuxtv.org/wiki/index.php/Talk:How_to_Obtain,_Build_and_Install_V4L-DVB_Device_Drivers

Make sure you use sudo when building and installing the kernel drivers, otherwise the build will fail due to lack of permissions to read header files.

If you will get kernel version mismatch upon inserting the modules follow these instructions to install proper kernel and header files:

https://raspberrypi.stackexchange.com/questions/63879/installed-kernel-headers-and-uname-r-differ

Installing ffmpeg on Raspberry PI:

https://www.jeffreythompson.org/blog/2014/11/13/installing-ffmpeg-for-raspberry-pi/

Installing latest Flask:
pip install -U https://github.com/pallets/flask/archive/master.tar.gz

# Architecture

The architecture of the IPTV streaming service is simple, and comprises four different modules:
<ul>
<li>(i) capturing device (or apparatus), such as a DVB-C card;</li>
<li>(ii) capturing service (a small application), which:
  <ul><li>(a) tunes the capturing device;</li>
  <li>(b) reads the TS stream from the device</li>
  <li>(c) writes the stream as it is into the files;</li>
  <li>(d) once the data is written into file, (do we need transcoding?) the playlist file .M3U8 is also updated;</li>
</ul></li>
<li>(iii) streaming service, which is responsible for:
  <ul><li>(a) authenticating clients;</li>
  <li>(b) delivering TS files to clients;</li>
  <li>(c) delivering .M3U8 files to clients;<li>
  </ul>
</li>
<li>(iv) web application, which allows the clients to interact with the services and play media;</li>
</ul>

# Deploying the infrastructure

```
# cd deployment
# bash deploy.sh <sql user> <sql password>
```

# Running the infrastructure

Basically we need to run three pieces of software. The first one is the DVB device tuning, 
transport stream capturing and filtering software. The second piece of software is the streaming 
service: it is essentially an Nginx, which will serve the playlists and media files, as well as 
the authentication middleware which will authenticate and account the requests from the clients 
based on supplied cookie. And finally the web interface, which will allow authenticated users to 
receive the TV schedule, select channels and play the live streams. In order to surve multiple 
channels at the same time, an array of DVB tuners is need - one tuner per channel. Of course, 
multiple programs can be multiplexed into a stream, and so potentially several channels can be served
with a single device.

Essentially, when you deploy the infrasturcture it should be running already and you need to 
just open the browser and input the following URL http://<ip address>/index.html

If, for some reason, the services are not running execute the following two commands in the 
console:

```
$ sudo service iptv-capturing start
$ sudo service iptv-backend start
```