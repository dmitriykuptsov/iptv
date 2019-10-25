#!/usr/bin/python

# Copyright (C) 2019 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from config import config
from HLSCrypto import HLSCipher
from HLSCrypto import KEY_SIZE
from HLSCrypto import IV_SIZE
import datetime
import os
import re
import threading
import time
import ctypes
import fcntl
import ioctl
import ioctl.linux
from time import sleep
import copy
import pwd
import grp
import binascii
from crccheck.crc import Crc32, Crc32Mpeg2
import array

# General config
MAX_BUFFER_SIZE_IN_BYTES   = config["SEQUENCE_LENGTH_IN_BYTES"];
MAX_SEQUENCE_PER_FOLDER    = config["NUMBER_OF_SEQUENCIES_PER_FOLDER"];
WEB_PATH                   = config["WEB_PATH"];

# Offsets and lengths
TS_PACKET_SIZE             = 0xBC;
CRC32_LENGTH               = 0x4;
TS_HEADER_SIZE             = 0x4;
PMT_OFFSET                 = 0x9;
PROGRAM_INFO_LENGTH_OFFSET = 0xA;
SECTION_LENGTH_OFFSET      = 0x1;
PMT_RECORD_LENGTH          = 0x4;
SECTION_OFFSET             = 0xD;
PAT_PREHEADER_LENGTH       = 0x8;
PMT_PREHEADER_LENGTH       = 0xC;

# Synchronization
SYNC_PACKET_AMOUNT         = 0x5;
UNSYNC_PACKET_AMOUNT       = 0x3;

# Predefined field values
SYNC_BYTE                  = 0x47;

# Adaptation field types
TS_PACKET_PAYLOAD_ONLY           = 0x1;
TS_PACKET_ADAPTATION_ONLY        = 0x2;
TS_PACKET_ADAPTATION_AND_PAYLOAD = 0x3;

# Stream Types
# See http://www.atsc.org/cms/standards/Code-Points-Registry-Rev-35.xlsx
STREAM_TYPE_MPEG1_VIDEO    = 0x01;
STREAM_TYPE_MPEG2_VIDEO    = 0x02;
STREAM_TYPE_MPEG1_AUDIO    = 0x03;
STREAM_TYPE_MPEG2_AUDIO    = 0x04;
STREAM_TYPE_PRIVATE        = 0x06;
STREAM_TYPE_AUDIO_ADTS     = 0x0f;
STREAM_TYPE_H264           = 0x1b;
STREAM_TYPE_MPEG4_VIDEO    = 0x10;
STREAM_TYPE_METADATA       = 0x15;
STREAM_TYPE_AAC            = 0x11;
STREAM_TYPE_MPEG2_VIDEO_2  = 0x80;
STREAM_TYPE_AC3            = 0x81;
STREAM_TYPE_PCM            = 0x83;
STREAM_TYPE_SCTE35         = 0x86;

# Descriptors
VIDEO_STREAM_DESCRIPTOR          = 0x02;
AUDIO_STREAM_DESCRIPTOR          = 0x03;
DATA_STREAM_ALIGNMENT_DESCRIPTOR = 0x06;
CA_DESCRIPTOR                    = 0x09;
TELETEXT_SUBTITLE_DESCRIPTOR     = 0x56;
DVB_SUBTITLE_DESCRIPTOR          = 0x59;

# Well known PIDs
PAT_PID                    = 0x0;

# Modulation
FE_QPSK                    = 0x0;
FE_QAM                     = 0x1;
FE_OFDM                    = 0x2;

# Default tuning parameters
SYMBOLRATE_DEFAULT         = 27500;
DISEQC_DEFAULT             = 0;
SEC_TONE_DEFAULT           = -1;
INVERSION_DEFAULT          = 0x2; # INVERSION_AUTO
BANDWIDTH_DEFAULT          = 0x0; # 0 MHz
CODERATE_HP_DEFAULT        = 0x3; # FEC_3_4
CODERATE_LP_DEFAULT        = 0x3; # FEC_3_4
FEC_INNER_DEFAULT          = 0x9; # FEC_AUTO
MODULATON_DEFAULT          = 0x3; # QAM_16
HIERARCHY_DEFAULT          = 0x0; # HIERARCHY_NONE
TRANSMISSION_MODE_DEFAULT  = 0x0; # TRANSMISSION_MODE_2K
GUARD_INTERVAL_DEFAULT     = 0x0; # GUARD_INTERVAL_1_32

# Statuses
FE_NONE                    = 0x00;
FE_HAS_SIGNAL              = 0x01;
FE_HAS_CARRIER             = 0x02;
FE_HAS_VITERBI             = 0x04;
FE_HAS_SYNC                = 0x08;
FE_HAS_LOCK                = 0x10;
FE_TIMEDOUT                = 0x20;
FE_REINIT                  = 0x40;

# Capabilities 
FE_IS_STUPID                   = 0;
FE_CAN_INVERSION_AUTO          = 0x1;
FE_CAN_FEC_1_2                 = 0x2;
FE_CAN_FEC_2_3                 = 0x4;
FE_CAN_FEC_3_4                 = 0x8;
FE_CAN_FEC_4_5                 = 0x10;
FE_CAN_FEC_5_6                 = 0x20;
FE_CAN_FEC_6_7                 = 0x40;
FE_CAN_FEC_7_8                 = 0x80;
FE_CAN_FEC_8_9                 = 0x100;
FE_CAN_FEC_AUTO                = 0x200;
FE_CAN_QPSK                    = 0x400;
FE_CAN_QAM_16                  = 0x800;
FE_CAN_QAM_32                  = 0x1000;
FE_CAN_QAM_64                  = 0x2000;
FE_CAN_QAM_128                 = 0x4000;
FE_CAN_QAM_256                 = 0x8000;
FE_CAN_QAM_AUTO                = 0x10000;
FE_CAN_TRANSMISSION_MODE_AUTO  = 0x20000;
FE_CAN_BANDWIDTH_AUTO          = 0x40000;
FE_CAN_GUARD_INTERVAL_AUTO     = 0x80000;
FE_CAN_HIERARCHY_AUTO          = 0x100000;
FE_CAN_8VSB                    = 0x200000;
FE_CAN_16VSB                   = 0x400000;
FE_HAS_EXTENDED_CAPS           = 0x800000;
FE_CAN_MULTISTREAM             = 0x4000000;
FE_CAN_TURBO_FEC               = 0x8000000;
FE_CAN_2G_MODULATION           = 0x10000000;
FE_NEEDS_BENDING               = 0x20000000;
FE_CAN_RECOVER                 = 0x40000000;
FE_CAN_MUTE_TS                 = 0x80000000;

# Demux
DMX_PES_OTHER                  = 0x14;
DMX_PES_AUDIO                  = 0x0; 
DMX_PES_VIDEO                  = 0x1; 

# Input types
DMX_IN_FRONTEND                = 0x0;
DMX_IN_DVR                     = 0x1;

DMX_IMMEDIATE_START            = 0x4;
DMX_OUT_TS_TAP                 = 0x2;
DMX_OUT_TSDEMUX_TAP            = 0x3;

DTV_DELIVERY_SYSTEM	           = 0x11;

# DVBv5 property Commands 
DTV_UNDEFINED                  = 0x0;
DTV_TUNE                       = 0x1;
DTV_CLEAR                      = 0x2;
DTV_FREQUENCY                  = 0x3;
DTV_MODULATION                 = 0x4;
DTV_BANDWIDTH_HZ               = 0x5;
DTV_INVERSION                  = 0x6;
DTV_DISEQC_MASTER              = 0x7;
DTV_SYMBOL_RATE                = 0x8;
DTV_INNER_FEC                  = 0x9;
DTV_VOLTAGE                    = 0xA;
DTV_TONE                       = 0xB;
DTV_PILOT                      = 0xC;
DTV_ROLLOFF                    = 0xD;
DTV_DISEQC_SLAVE_REPLY         = 0xE;

SYS_DVBC_ANNEX_B               = 0x2;
SYS_DVBC_ANNEX_A               = 0x1;
SYS_DVBC_ANNEX_C               = 0x12;
SYS_DVBC_ANNEX_AC              = SYS_DVBC_ANNEX_A;

# Maximum value for the CC
MAX_CC_COUNTER                 = 0x10;

# H264
H264_NAL_NONIDR_SLICE          = 0x1;
H264_NAL_IDR_SLICE             = 0x5;
H264_NAL_SPS                   = 0x7;
H264_NAL_PPS                   = 0x8;

IDR_FRAME_REVERSE_ENGINEERED   = 0x65;
IDR_2_FRAME_REVERSE_ENGINEERED = 0x41;
SPS_FRAME_REVERSE_ENGINEERED   = 0x67;
PPS_FRAME_REVERSE_ENGINEERED   = 0x68;

# PES header
PES_HEADER_LENGTH_OFFSET       = 0x8;

def TS_PACKET_SYNC_BYTE(b):
	return (b[0]);
def TS_PACKET_TRANS_ERROR(b):
	return ((b[1]&0x80)>>7);
def TS_PACKET_PAYLOAD_START(b):
	return ((b[1]&0x40)>>6);
def TS_PACKET_PRIORITY(b):
	return ((b[1]&0x20)>>5);
def TS_PACKET_PID(b):
	return (((b[1]&0x1F)<<8) | b[2]);
def TS_PACKET_SCRAMBLING(b):
	return ((b[3]&0xC0)>>6);
def TS_PACKET_ADAPTATION(b):
	return ((b[3]&0x30)>>4);
def TS_PACKET_CONT_COUNT(b):
	return ((b[3]&0x0F)>>0);
def TS_PACKET_ADAPTATION_LENGTH(b):
	return (b[4]);

# This was reverse engineered
# PES header
# https://en.wikipedia.org/wiki/Packetized_elementary_stream
# NAL header
def is_key_frame(b):
	offset = TS_HEADER_SIZE;
	if TS_PACKET_ADAPTATION(b) == TS_PACKET_ADAPTATION_ONLY or TS_PACKET_ADAPTATION(b) == TS_PACKET_ADAPTATION_AND_PAYLOAD:
		adaptation_field_length = b[offset];
		offset += (adaptation_field_length + 1);
	#print "PES header length.... %d" % b[TS_HEADER_SIZE + PES_HEADER_LENGTH_OFFSET];
	#print "Start code.... %d" % (b[offset] << 16 | b[offset + 1] << 8 | b[offset + 2]);
	#print "Stream id.... %d" % (b[offset + 3]);
	offset += PES_HEADER_LENGTH_OFFSET + b[offset + PES_HEADER_LENGTH_OFFSET] + 1;
	# Simply loop through all the bytes, this is rather slow but I did not find other method to search for IDR frame
	# Thanks to the Internet and reverse engineering effort of the existing IPTV streaming service I inderstood how the
	# key frame should look like. 
	sps_found = False;
	pps_found = False;
	idr_found = False;
	#i = offset
	#import sys
	#print "Looking for key frame >>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	#while i < TS_PACKET_SIZE:
	#	sys.stdout.write("%02x" % b[i]);
	#	i += 1;
	#sys.stdout.write("\n");
	while offset + 4 < TS_PACKET_SIZE:
		# Most likely it is possible to avoid the loop if the NALU headers and NALU payload lengths
		# do not change from I-Frame to I-Frame. This can save quite some CPU cycles
		sync_word = ((b[offset] & 0x1F) << 24 | b[offset + 1] << 16 | b[offset + 2] << 8 | b[offset + 3]);
		#sync_word = (b[offset] << 16 | b[offset + 1] << 8 | b[offset + 2]);
		if sync_word == 0x1:
			# The NALU type are the first 5 bits 
			nal_type = (b[offset + 4] & 0x1F);
			#if nal_type == IDR_FRAME_REVERSE_ENGINEERED or nal_type == IDR_2_FRAME_REVERSE_ENGINEERED:
			if nal_type == H264_NAL_IDR_SLICE or nal_type == H264_NAL_NON_IDR_SLICE:
				idr_found = True;
			#if nal_type == SPS_FRAME_REVERSE_ENGINEERED:
			if nal_type == H264_NAL_SPS:
				sps_found = True;
			if nal_type == H264_NAL_PPS:
				pps_found = True;
		offset += 1;
	return idr_found and sps_found and pps_found;

def print_status(festatus):
	print "Frontend Status:";
	if (festatus & FE_HAS_SIGNAL):
		print "FE_HAS_SIGNAL";
	if (festatus & FE_TIMEDOUT):
		print "FE_TIMEDOUT";
	if (festatus & FE_HAS_LOCK):
		print "FE_HAS_LOCK";
	if (festatus & FE_HAS_CARRIER):
		print "FE_HAS_CARRIER";
	if (festatus & FE_HAS_VITERBI):
		print "FE_HAS_VITERBI";
	if (festatus & FE_HAS_SYNC):
		print "FE_HAS_SYNC";

def print_capabilities(caps):
	print "Device has the following capabilities"
	if caps & FE_IS_STUPID:
		print "FE_IS_STUPID";
	if caps & FE_CAN_INVERSION_AUTO:
		print "FE_CAN_INVERSION_AUTO"
	if caps & FE_CAN_FEC_1_2:
		print "FE_CAN_FEC_1_2"
	if caps & FE_CAN_FEC_2_3:
		print "FE_CAN_FEC_2_3"
	if caps & FE_CAN_FEC_3_4:
		print "FE_CAN_FEC_3_4"
	if caps & FE_CAN_FEC_4_5:
		print "FE_CAN_FEC_4_5"
	if caps & FE_CAN_FEC_5_6:
		print "FE_CAN_FEC_5_6"
	if caps & FE_CAN_FEC_6_7:
		print "FE_CAN_FEC_6_7"
	if caps & FE_CAN_FEC_7_8:
		print "FE_CAN_FEC_7_8"
	if caps & FE_CAN_FEC_8_9:
		print "FE_CAN_FEC_8_9"
	if caps & FE_CAN_FEC_AUTO:
		print "FE_CAN_FEC_AUTO"
	if caps & FE_CAN_QPSK:
		print "FE_CAN_QPSK"
	if caps & FE_CAN_QAM_16:
		print "FE_CAN_QAM_16"
	if caps & FE_CAN_QAM_32:
		print "FE_CAN_QAM_32"
	if caps & FE_CAN_QAM_64:
		print "FE_CAN_QAM_64"
	if caps & FE_CAN_QAM_128:
		print "FE_CAN_QAM_128"
	if caps & FE_CAN_QAM_256:
		print "FE_CAN_QAM_256"
	if caps & FE_CAN_QAM_AUTO:
		print "FE_CAN_QAM_AUTO"
	if caps & FE_CAN_TRANSMISSION_MODE_AUTO:
		print "FE_CAN_TRANSMISSION_MODE_AUTO"
	if caps & FE_CAN_BANDWIDTH_AUTO:
		print "FE_CAN_BANDWIDTH_AUTO"
	if caps & FE_CAN_GUARD_INTERVAL_AUTO:
		print "FE_CAN_GUARD_INTERVAL_AUTO"
	if caps & FE_CAN_HIERARCHY_AUTO:
		print "FE_CAN_HIERARCHY_AUTO"
	if caps & FE_CAN_8VSB:
		print "FE_CAN_8VSB"
	if caps & FE_CAN_16VSB:
		print "FE_CAN_16VSB"
	if caps & FE_HAS_EXTENDED_CAPS:
		print "FE_HAS_EXTENDED_CAPS"
	if caps & FE_CAN_MULTISTREAM:
		print "FE_CAN_MULTISTREAM"
	if caps & FE_CAN_TURBO_FEC:
		print "FE_CAN_TURBO_FEC"
	if caps & FE_CAN_2G_MODULATION:
		print "FE_CAN_2G_MODULATION"
	if caps & FE_NEEDS_BENDING:
		print "FE_NEEDS_BENDING"
	if caps & FE_CAN_RECOVER:
		print "FE_CAN_RECOVER"
	if caps & FE_CAN_MUTE_TS:
		print "FE_CAN_MUTE_TS"

# Sets the filter 
def set_pesfilter(fd, pid, pes_type):
	pesfilter = dmx_pes_filter_params();
	buffersize = 64 * 1024;
	#buffersize = 188 * 10;
	#if (fcntl.ioctl(fd, DMX_SET_BUFFER_SIZE(), buffersize) == -1):
	#	print "DMX_SET_BUFFER_SIZE failed";
	#	return -1;
	pesfilter.pid = pid;
	pesfilter.input = DMX_IN_FRONTEND;
	#pesfilter.output = DMX_OUT_TS_TAP;
	pesfilter.output = DMX_OUT_TSDEMUX_TAP;
	pesfilter.pes_type = pes_type;
	pesfilter.flags = DMX_IMMEDIATE_START;

	if (fcntl.ioctl(fd, DMX_SET_PES_FILTER(), pesfilter) == -1):
		print "DMX_SET_PES_FILTER failed";
		return -1;
	return 0;

def add_pidfilter(fd, pid):
	buf = array.array('H', [0]);
	buf[0] = pid;
	if (fcntl.ioctl(fd, DMX_ADD_PID(), buf) == -1):
		print "DMX_ADD_PID failed";
		return -1;
	return 0;

# Description of ctypes structures
# https://wingware.com/psupport/python-manual/2.5/lib/ctypes-structured-data-types.html
# DVB structures
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/dvb/frontend.h
class dmx_pes_filter_params(ctypes.Structure):
	_fields_ = [
		('pid', ctypes.c_ushort),
		('input', ctypes.c_uint),
		('output', ctypes.c_uint),
		('pes_type', ctypes.c_uint),
		('flags', ctypes.c_uint)
	]

class dvb_frontend_info(ctypes.Structure):
	_fields_ = [
		('name', ctypes.c_char * 128),
		('type', ctypes.c_uint),
		('frequency_min', ctypes.c_uint),
		('frequency_max', ctypes.c_uint),
		('frequency_stepsize', ctypes.c_uint),
		('frequency_tolerance', ctypes.c_uint),
		('symbol_rate_min', ctypes.c_uint),
		('symbol_rate_max', ctypes.c_uint),
		('symbol_rate_tolerance', ctypes.c_uint),
		('notifier_delay', ctypes.c_uint),
		('caps', ctypes.c_uint)
	]

class dvb_frontend_status(ctypes.Structure):
	_fields_ = [
		('status', ctypes.c_uint)
	]

class dvb_qpsk_parameters(ctypes.Structure):
	_fields_ = [
		('symbol_rate', ctypes.c_uint),
		('fec_inner', ctypes.c_uint)
	]

class dvb_qam_parameters(ctypes.Structure):
	_fields_ = [
		('symbol_rate', ctypes.c_uint),
		('fec_inner', ctypes.c_uint),
		('modulation', ctypes.c_uint)
	]

class dvb_vsb_parameters(ctypes.Structure):
	_fields_ = [
		('modulation', ctypes.c_uint)
	]

class dvb_ofdm_parameters(ctypes.Structure):
	_fields_ = [
		('bandwidth', ctypes.c_uint),
		('code_rate_HP', ctypes.c_uint),
		('code_rate_LP', ctypes.c_uint),
		('constellation', ctypes.c_uint),
		('transmission_mode', ctypes.c_uint),
		('guard_interval', ctypes.c_uint),
		('hierarchy_information', ctypes.c_uint)
	]

class dvb_modulation_parameters(ctypes.Union):
	_fields_ = [
		('qpsk', dvb_qpsk_parameters),
		('qam', dvb_qam_parameters),
		('ofdm', dvb_ofdm_parameters),
		('vsb', dvb_vsb_parameters)
	]

class dvb_frontend_parameters(ctypes.Structure):
	_fields_ = [
		('frequency', ctypes.c_uint),
		('inversion', ctypes.c_uint),
		('u', dvb_modulation_parameters)
	]

class tuning_params(ctypes.Structure):
	_fields_ = [
		('card', ctypes.c_char),
		('type', ctypes.c_char),
		('frequency', ctypes.c_int),
		('polarity', ctypes.c_char),
		('symbol_rate', ctypes.c_int),
		('diseqc', ctypes.c_int),
		('tone', ctypes.c_int),
		('inversion', ctypes.c_uint),
		('bandwidth', ctypes.c_uint),
		('code_rate_hp', ctypes.c_uint),
		('code_rate_lp', ctypes.c_uint),
		('fec_inner', ctypes.c_uint),
		('modulation', ctypes.c_uint),
		('hierarchy', ctypes.c_uint),
		('transmission_mode', ctypes.c_uint),
		('guard_interval', ctypes.c_uint)
	]

class dvb_frontend_event(ctypes.Structure):
	_fields_ = [
		('status', ctypes.c_uint),
		('parameters', dvb_frontend_parameters)
	]

class dvb_frontend_signal_strength(ctypes.Structure):
	_fields_ = [
		('strength', ctypes.c_ushort)
	]

MAX_DTV_STATS                     = 0x4;

class dvb_buffer(ctypes.Structure):
	_fields_ = [
		('data', ctypes.c_uint8 * 32),
		('len', ctypes.c_uint),
		('reserved1', ctypes.c_uint * 3),
		('reserved2', ctypes.c_void_p)
	]

class dtv_stats_value(ctypes.Union):
	_fields_ = [
		('uvalue', ctypes.c_ulonglong),
		('svalue', ctypes.c_longlong)
	]

class dtv_stats(ctypes.Structure):
	_pack_ = 1;
	_fields_ = [
		('scale', ctypes.c_uint8),
		('u', dtv_stats_value)
	]
	_anonymous_ = ('u',)

class dtv_fe_stats(ctypes.Structure):
	_pack_ = 1;
	_fields_ = [
		('len', ctypes.c_uint8),
		('stat', dtv_stats * MAX_DTV_STATS)
	]

class dvb_property_union(ctypes.Union):
	_fields_ = [
		('data', ctypes.c_uint),
		('st', dtv_fe_stats),
		('buffer', dvb_buffer)
	]

class dtv_property(ctypes.Structure):
	_pack_ = 1;
	_fields_ = [
		('cmd', ctypes.c_uint),
		('reserved', ctypes.c_uint * 3),
		('u', dvb_property_union),
		('result', ctypes.c_int)
	]

class dtv_properties(ctypes.Structure):
	_fields_ = [
		('num', ctypes.c_uint),
		('props', ctypes.POINTER(dtv_property))
	]

def DMX_SET_BUFFER_SIZE():
	return ioctl.linux.IO('o', 45);

def DMX_SET_PES_FILTER():
	return ioctl.linux.IOW('o', 44, ctypes.sizeof(dmx_pes_filter_params));

def FE_READ_SIGNAL_STRENGTH():
	return ioctl.linux.IOR('o', 71, ctypes.sizeof(dvb_frontend_signal_strength));

def FE_GET_INFO():
	return ioctl.linux.IOR('o', 61, ctypes.sizeof(dvb_frontend_info));

def FE_READ_STATUS():
	return ioctl.linux.IOR('o', 69, ctypes.sizeof(dvb_frontend_status));

def FE_SET_FRONTEND():
	return ioctl.linux.IOW('o', 76, ctypes.sizeof(dvb_frontend_parameters));

def FE_GET_FRONTEND():
	return ioctl.linux.IOR('o', 77, ctypes.sizeof(dvb_frontend_parameters));

def FE_GET_EVENT():
	return ioctl.linux.IOR('o', 78, ctypes.sizeof(dvb_frontend_event));

def FE_SET_PROPERTY():
	return ioctl.linux.IOW('o', 82, ctypes.sizeof(dtv_properties));

def DMX_ADD_PID():
	return ioctl.linux.IOW('o', 51, ctypes.sizeof(ctypes.c_uint16));

# Sets the device into DVB-C mode
def set_delivery_system(fd, params):
	# Set the delivery system to DVB-C type
	# This is a copy from w_scan code
	# https://github.com/stefantalpalaru/w_scan2/blob/master/src/scan.c
	print "Setting the delivery system to DVB-C type...";
	NUM_PROPERTIES = 8;
	property_array = (dtv_property * NUM_PROPERTIES)();
	properties = dtv_properties();
	properties.num = NUM_PROPERTIES;
	properties.props = ctypes.cast(property_array, ctypes.POINTER(dtv_property));

	# Clear the settings
	properties.props[0].cmd = DTV_CLEAR;
	properties.props[0].u.data = DTV_UNDEFINED;

	# Set delivery system
	# Only this parameter is important
	properties.props[1].cmd = DTV_DELIVERY_SYSTEM;
	properties.props[1].u.data = SYS_DVBC_ANNEX_AC;

	# This code looks like a duplicate of the actual tuning, which is done later on
	# Set frequency
	properties.props[2].cmd = DTV_FREQUENCY;
	properties.props[2].u.data = params.frequency;

	# Set inversion
	properties.props[3].cmd = DTV_INVERSION;
	properties.props[3].u.data = params.inversion;

	# Set modulation
	properties.props[4].cmd = DTV_MODULATION;
	properties.props[4].u.data = params.modulation;

	# Set symbol rate
	properties.props[5].cmd = DTV_SYMBOL_RATE;
	properties.props[5].u.data = params.symbol_rate;

	# Set error correction
	properties.props[6].cmd = DTV_INNER_FEC;
	properties.props[6].u.data = params.fec_inner;

	# Tune
	properties.props[7].cmd = DTV_TUNE;
	properties.props[7].u.data = DTV_UNDEFINED;

	properties.props = ctypes.cast(property_array, ctypes.POINTER(dtv_property));
	if fcntl.ioctl(fd, FE_SET_PROPERTY(), properties) < 0:
		print "Failed to set the tuner into DVB-C mode";
	else:
		print "The device should be now in DVB-C mode of operation";
		print "Results for the commands are:";
		for i in range(0, properties.num):
			print "----------------------------------------------------------------";
			print "CMD: %d" % (properties.props[i].cmd);
			print "DATA: %d" % (properties.props[i].u.data);
			print "RESULT: %d" % (properties.props[i].result);
			print "----------------------------------------------------------------";

#Writing to device using ioctl https://stackoverflow.com/questions/8244887/writing-to-usb-device-with-python-using-ioctl
#devicehandle = open('/dev/dvb/frontend0', 'rw')
#fcntl.ioctl(devicehandle, operation, Args)

# Tunes the device using parameters, such as frequence, modulation, etc.
# Tuning was ported from https://github.com/njh/dvbshout/blob/master/src/tune.c
def tune(fd, params):
	set_delivery_system(fd, params);
	feparams = dvb_frontend_parameters();
	fe_info = dvb_frontend_info();
	if fcntl.ioctl(fd, FE_GET_INFO(), fe_info) < 0:
		print "FE_GET_INFO Error:";
		exit(-1);
	print "DVB card name:", fe_info.name;
	print_capabilities(fe_info.caps);
	if fe_info.type == FE_QAM:
		print "Tuning DVB-C to %d Hz, srate=%d\n" % (params.frequency, params.symbol_rate);
		feparams.frequency = params.frequency;
		feparams.inversion = params.inversion;
		feparams.u.qam.symbol_rate = params.symbol_rate;
		feparams.u.qam.fec_inner = params.fec_inner;
		feparams.u.qam.modulation = params.modulation;
	elif fe_info.type == FE_OFDM:
		print "Unsupported DVB-T\n";
		exit(-1);
	elif fe_info.type == FE_QPSK:
		print "Unsupported DVB-S\n";
		exit(-1);
	else:
		print "Unknown frontend type. Aborting.";
		exit(-1);
	#return fcntl.ioctl(fd, FE_SET_FRONTEND(), feparams);
	return (check_status(fd, feparams, params.tone));

# Sets up the frontend (tunes the card) and checks whether the device is locked to the signal
def check_status(fd, feparams, tone):
	fe_info = dvb_frontend_info();
	event = dvb_frontend_event();
	if fcntl.ioctl(fd, FE_SET_FRONTEND(), feparams) < 0:
		print "Error while tuning the frontend";
		return -1;
	if fcntl.ioctl(fd, FE_GET_INFO(), fe_info) < 0:
		print "Error getting the information";
		return -1;
	event.status = 0;
	while (((event.status & FE_TIMEDOUT) == 0) and ((event.status & FE_HAS_LOCK) == 0)):
		#if (poll (pfd, 1, 10000)):
		#	if (pfd[0].revents & POLLIN):
		if (fcntl.ioctl(fd, FE_GET_EVENT(), event)) < 0:
			print "Error getting event info";
		#else:
		#	print "Status", event.status
		sleep(1);
	if (event.status & FE_HAS_LOCK):
		print "Gained lock";
		if fe_info.type == FE_QAM:
			print "Frequency: %d Hz" % (event.parameters.frequency)
			print "Inversion: %d" % (event.parameters.inversion)
			print "SymbolRate: %d" % (event.parameters.u.qam.symbol_rate)
			print "FEC Inner: %d" % (event.parameters.u.qam.fec_inner)
			print "Modulation: %d" % (event.parameters.u.qam.modulation)
		else:
			print "Unsupported modulation type";
	else:
		print "Not able to lock to the signal on the given frequency";
	festatus = dvb_frontend_status();
	if fcntl.ioctl(fd, FE_READ_STATUS(), festatus) < 0:
		print "Error occured while reading status from the device";
	else:
		print_status(festatus.status);
	festrength = dvb_frontend_signal_strength();
	if fcntl.ioctl(fd, FE_READ_SIGNAL_STRENGTH(), festrength) < 0:
		print "Cannot read signal strength from the device"
	else:
		print "Signal strength: %d" % (festrength.strength)
	return 0;

# Initializes the tuning parameters with the default values
def init_tuning_defaults():
	params = tuning_params();
	#params.card = '';
	#params.type = 's';
	params.frequency = config["CENTER_FREQUENCY_HZ"];
	#params.polarity = 'v';
	params.symbol_rate = config["SYMBOL_RATE"];
	#params.diseqc = DISEQC_DEFAULT;
	#params.tone = SEC_TONE_DEFAULT;
	params.inversion = config["INVERSION"];
	params.bandwidth = config["BANDWIDTH"];
	#params.code_rate_hp = CODERATE_HP_DEFAULT;
	#params.code_rate_lp = CODERATE_LP_DEFAULT;
	params.fec_inner = config["FEC"];
	params.modulation = config["MODULATION"];
	#params.hierarchy = HIERARCHY_DEFAULT;
	#params.transmission_mode = TRANSMISSION_MODE_DEFAULT;
	#params.guard_interval = GUARD_INTERVAL_DEFAULT;
	return params;

# Sets owner of the folder/file to www-data
def set_ownership(path):
	uid = pwd.getpwnam("www-data").pw_uid;
	gid = grp.getgrnam("www-data").gr_gid;
	os.chown(path, uid, gid);

# Creates the folder and sets the owner of the folder to www-data
def create_folder(path):
	try:
		os.makedirs(path);
		set_ownership(path)
		return True;
	except Exception as e:
		print str(e);
		return False;

# Removes the file from the filesystem
def remove_file(path):
	try:
		os.remove(path);
		return True;
	except:
		return False;

class LookupTable():
	def __init__(self, channels):
		self.pmt_packets = {};
		self.pat_packets = {};
		self.stream_id_pmt_pid = {};
		self.pmt_pid_stream_id = {};
		self.stream_id_video_pid = {};
		self.stream_id_audio_pid = {};
		self.audio_pid_stream_id = {};
		self.video_pid_stream_id = {};
		self.streams = [];
		for stream_id in channels.keys():
			self.streams.append(stream_id);
	def get_stream_ids(self):
		return self.streams;
	def is_stream_id_in_list(self, stream_id):
		return stream_id in self.streams;
	def set_pat_packet(self, stream_id, packet):
		self.pat_packets[stream_id] = packet;
	def set_pmt_pid_stream_id(self, stream_id, pmt_pid):
		self.pmt_pid_stream_id[pmt_pid] = stream_id;
		self.stream_id_pmt_pid[stream_id] = pmt_pid;
	def get_stream_id_by_pmt_pid(self, pmt_pid):
		return self.pmt_pid_stream_id.get(pmt_pid);
	def is_valid_pmt_pid(self, pmt_pid):
		#print "Processing PMT pid %d" % pmt_pid;
		stream_id = self.pmt_pid_stream_id.get(pmt_pid, None)
		if stream_id != None:
			return True;
		return False;
	def set_pmt_packet(self, stream_id, packet):
		self.pmt_packets[stream_id] = packet;
	def set_video_pid_stream_id(self, stream_id, video_pid):
		self.stream_id_video_pid[stream_id] = video_pid;
		self.video_pid_stream_id[video_pid] = stream_id;
	def set_audio_pid_stream_id(self, stream_id, audio_pid):
		self.stream_id_audio_pid[stream_id] = audio_pid;
		self.audio_pid_stream_id[audio_pid] = stream_id;
	def get_pat_packet(self, video_pid):
		stream_id = self.video_pid_stream_id[video_pid];
		return self.pat_packets[stream_id];
	def get_pmt_packet(self, video_pid):
		stream_id = self.video_pid_stream_id[video_pid];
		return self.pmt_packets[stream_id];
	def get_stream_id_by_video_pid(self, video_pid):
		return self.video_pid_stream_id.get(video_pid, -1);
	def get_stream_id_by_audio_pid(self, audio_pid):
		return self.audio_pid_stream_id.get(audio_pid, -1);
	def is_valid_video_pid(self, video_pid):
		return self.video_pid_stream_id.get(video_pid, None) != None;
	def is_valid_audio_pid(self, audio_pid):
		return self.audio_pid_stream_id.get(audio_pid, None) != None;

# Performs capturing of the stream from the device
# Once the buffer size reaches certain limit the
# buffer is written to an output file
# The function also analyzes the structure 
# of PAT and PMT tables in order to find 
# the PIDs of the audio and video elementary 
# streams
def capture(fd):
	lookup = LookupTable(config["VALID_CHANNELS"]);
	# Precreate buffer twice the size of the maximum buffer size
	#sequence_buffer = bytearray(MAX_BUFFER_SIZE_IN_BYTES * 2);
	sequence_buffer = {};
	for stream_id in config["VALID_CHANNELS"].keys():
		sequence_buffer[stream_id] = bytearray(MAX_BUFFER_SIZE_IN_BYTES * 2);
	base_dir = config["TS_OUTPUT_FOLDER"];
	#program = config["STREAM_ID"];
	#output_folder = "".join([base_dir, "/", str(filling_timestamp)]);
	playing_timestamp = {};
	waiting_timestamp = {};
	filling_timestamp = {};
	buffer_fill = {};
	sequence = {};
	playlist_constructed = {};
	output_folder = {};
	stream_ids = lookup.get_stream_ids();
	for stream_id in stream_ids:
		playlist_constructed[stream_id] = False;
		playing_timestamp[stream_id] = -1;
		waiting_timestamp[stream_id] = -1;
		filling_timestamp[stream_id] = int(time.time());
		sequence[stream_id] = 1;
		buffer_fill[stream_id] = 0;
		output_folder[stream_id] = "".join([base_dir, "/", str(stream_id), "/", str(filling_timestamp[stream_id])]);
		if not create_folder(output_folder[stream_id]):
			print "Could not create folder. Exiting...";
			exit(-1);
	sync_count = 0;
	lost_packets = 0;
	pmt_pid = 0x0;
	pmt_packet_processed = {};
	video_pid = 0x0;
	audio_pid = 0x0;
	stream_synchronized = False;
	cc_counter = -1;
	pat_commited = False;
	pmt_commited = False;
	end_of_pes = False;
	pat_packet_processed = False;
	#pmt_packet = None;
	#playlist_constructed = False;
	while True:
		buf = None;
		try:
			buf = bytearray(fd.read(TS_PACKET_SIZE));
		except IOError:
			continue;
		if len(buf) != TS_PACKET_SIZE:
			continue;
		if TS_PACKET_SYNC_BYTE(buf) != SYNC_BYTE:
			continue;
		if TS_PACKET_TRANS_ERROR(buf):
			# Skip the packet if we have an error
			continue;
		pid = TS_PACKET_PID(buf);
		#print "PID of the packet %d" % (pid);
		#Have no idea how and why we have here extra byte but it seems to work that way
		offset = TS_HEADER_SIZE;
		#print "Adaptation header %d" % (TS_PACKET_ADAPTATION(buf));
		#print "PUSI %d" % (TS_PACKET_PAYLOAD_START(buf));
		#Parser is implemented according to the https://github.com/jeoliva/mpegts-basic-parser/blob/master/tsparser.c
		payload_unit_start_indicator = TS_PACKET_PAYLOAD_START(buf);
		if TS_PACKET_ADAPTATION(buf) == TS_PACKET_ADAPTATION_AND_PAYLOAD or TS_PACKET_ADAPTATION(buf) == TS_PACKET_ADAPTATION:
			#print "Adaptation header present and its length is %d" % (TS_PACKET_ADAPTATION_LENGTH(buf));
			offset += (TS_PACKET_ADAPTATION_LENGTH(buf) + 1);
		if pid == PAT_PID and not pat_packet_processed:
		#if pid == PAT_PID and not pat_commited:
			pat_packet_processed = True;
			print "**************** PAT PID ******************";
			# Program association table (PAT)
			# Lets look into the contents and find the PID of the program map table first
			if payload_unit_start_indicator:
				print "PUSI bit is set. Skipping %d bytes" % (buf[offset]);
				offset += ((buf[offset] & 0xFF) + 1);
			table_id = buf[offset];
			print "Table ID %d" % (table_id);
			section_syntax_indicator = ((buf[offset + 1] & 0x80) >> 7);
			print "Section syntax indicator %d" % (section_syntax_indicator);
			section_length = (((buf[offset + 1] & 0x0F) << 8) | (buf[offset + 2] & 0xFF));
			print "SECTION LENGTH: %d" % (section_length);
			transport_stream_id = (((buf[offset + 3] & 0x0F) << 8) | (buf[offset + 4] & 0xFF));
			print "Transport stream id %d" % (transport_stream_id);
			version_id = (buf[offset + 5] & 0x3e);
			current_next_section_inicator = (buf[offset + 5] & 0x1);
			pmt_pid_found  = False;
			num_programs   = (section_length - 5 - 4) / 4;
			index = offset + PAT_PREHEADER_LENGTH;
			print "Number of programs %d " % (num_programs);
			for i in range(num_programs):
				stream_id = (((buf[index] & 0xFF) << 8) | ((buf[index + 1] & 0xFF)));
				#pmt_pid = (((buf[index + 2] & 0x1F) << 8) | ((buf[index + 3] & 0xFF)));
				pmt_pid = (((buf[index + 2] & 0x1F) << 8) | (buf[index + 3] & 0xFF));
				print "Program number: %d, PMT PID %d" % (stream_id, pmt_pid);
				if lookup.is_stream_id_in_list(stream_id):
					#if not pmt_synced:
					#pmt_fd = open(config["DEMUX"], "w+");
					#if pmt_fd < 0:
					#	print "Opening demux file failed";
					#	exit(-1);
					print "Seting up filter for PMT %d...." % (pmt_pid);
					#if set_pesfilter(pmt_fd, pmt_pid, DMX_PES_OTHER) < 0:
					if add_pidfilter(fd, (pmt_pid & 0xFFFF)):
						print "Cannot set PMT filter. Exiting...";
						exit(-1);
					#pmt_pid_found = True;
					#pmt_synced = True;
					# Rewriting the PAT
					section_length = 5 + PMT_RECORD_LENGTH + CRC32_LENGTH;
					# Header offset, adaptation length field, actual length of the adaptation
					# Set the payload unit start indicator to 1
					buf[1] = (buf[1] | 0x40);
					if TS_PACKET_ADAPTATION(buf) == TS_PACKET_ADAPTATION_AND_PAYLOAD or TS_PACKET_ADAPTATION(buf) == TS_PACKET_ADAPTATION:
						pointer_length = TS_PACKET_SIZE - CRC32_LENGTH - (TS_PACKET_ADAPTATION_LENGTH(buf) + 1) -  PMT_RECORD_LENGTH - PAT_PREHEADER_LENGTH - 1;
						offset = TS_HEADER_SIZE + (TS_PACKET_ADAPTATION_LENGTH(buf) + 1);
					else:
						pointer_length = TS_PACKET_SIZE - CRC32_LENGTH - PMT_RECORD_LENGTH - PAT_PREHEADER_LENGTH - TS_HEADER_SIZE - 1;
						offset = TS_HEADER_SIZE;
					buf[offset] = pointer_length;
					offset += 1;
					# Pad with 1's
					for i in range(0, pointer_length):
						buf[offset] = 0xFF;
					offset += pointer_length;
					offset_table = offset;
					buf[offset] = table_id;
					# Section syntax indicator
					buf[offset + 1] = 0;
					buf[offset + 1] = (buf[offset + 1] | (section_syntax_indicator << 7));
					# Section length
					#print "SECTION LENGTH: %d" % (section_length);
					buf[offset + 1] = (buf[offset + 1] | ((section_length >> 8) & 0xF));
					#print buf[offset + 1], ((section_length >> 8) & 0xF);
					buf[offset + 2] = (section_length & 0xFF);
					section_length = (((buf[offset + 1] & 0x0F) << 8) | (buf[offset + 2] & 0xFF));
					#print "SECTION LENGTH: %d" % (section_length);
					# Transport stream id
					buf[offset + 3] = ((transport_stream_id >> 8) & 0xFF);
					buf[offset + 4] = (transport_stream_id & 0xFF);
					# Version number
					buf[offset + 5] = 0;
					buf[offset + 5] = (buf[offset + 5] | ((version_id << 1) & 0x3e));
					# Current next section indicator
					buf[offset + 5] = (buf[offset + 5] | (current_next_section_inicator & 0x1));
					# Set the first section number and last section number to 0x0
					buf[offset + 6] = 0x0;
					buf[offset + 7] = 0x0;
					offset += PAT_PREHEADER_LENGTH;
					buf[offset] = ((stream_id & 0xFF00) >> 8);
					buf[offset + 1] = (stream_id & 0xFF);
					buf[offset + 2] = ((pmt_pid & 0x1F00) >> 8);
					buf[offset + 3] = (pmt_pid & 0xFF);
					offset += PMT_RECORD_LENGTH;
					# Compute the checksum
					#crc32 = binascii.crc32(buffer(buf[offset_table:offset]));
					crc32 = Crc32Mpeg2.calc(buf[offset_table:offset]);
					buf[offset] = ((crc32 & 0xff000000) >> 24);
			  		buf[offset + 1] = ((crc32 & 0x00ff0000) >> 16);
					buf[offset + 2] = ((crc32 & 0x0000ff00) >>  8);
					buf[offset + 3] = (crc32 & 0x000000ff);
					pat_packet = copy.deepcopy(buf);
					lookup.set_pat_packet(stream_id, pat_packet);
					lookup.set_pmt_pid_stream_id(stream_id, pmt_pid);
					#break;
				index += PMT_RECORD_LENGTH;
			#if not pmt_pid_found:
			#	print "Program was not found in the PAT table";
			#	continue; # Or should we exit
			continue;
		elif pid == PAT_PID and pat_packet_processed:
			continue;
		# We have found the PMT PID lets look into the internals
		# to find out the PIDs for audio and video elementary streams
		#print pmt_pid == pid, pmt_synced, (not pat_commited)
		#if pid == pmt_pid and pmt_synced and (not pmt_commited):
		#if pid == pmt_pid and pmt_packet_processed:
		if lookup.is_valid_pmt_pid(pid) and not pmt_packet_processed.get(pid, False):
			pmt_packet_processed[pid] = True;
			pmt_packet = copy.deepcopy(buf);
			stream_id = lookup.get_stream_id_by_pmt_pid(pid)
			lookup.set_pmt_packet(stream_id, pmt_packet);
			print "**************** PMT PID ******************";
			if payload_unit_start_indicator:
				print "PUSI bit is set. Skipping %d bytes" % (buf[offset]);
				offset += ((buf[offset] & 0xFF) + 1);
			print "Offset is %d" % (offset);
			section_syntax_indicator = ((buf[offset + 1] & 0x80) >> 7);
			print "Section syntax indicator %d" % (section_syntax_indicator);
			print "PMT Table ID %d" % (buf[offset]);
			program_info_length = (((buf[offset + PROGRAM_INFO_LENGTH_OFFSET] & 0xF) << 8) |
						(buf[offset + PROGRAM_INFO_LENGTH_OFFSET + 1]));
			print "PMT program info length %d" % (program_info_length);
			section_length      = (((buf[offset + SECTION_LENGTH_OFFSET] & 0xF) << 8) |
						(buf[offset + SECTION_LENGTH_OFFSET + 1]));
			print "PMT section length %d" % (section_length);
			print "PCR PID: %d" % ((((buf[offset + 8] & 0x1F) << 8) | 
						(buf[offset + 9])))
			index               = offset + PMT_PREHEADER_LENGTH + program_info_length;
			counter             = 0;
			num                 = section_length - 9 - program_info_length - 4;
			while counter < num:
				stream_type    = buf[index + counter] & 0xFF;
				elementary_pid = (((buf[index + counter + 1] & 0x1F) << 8) | 
							(buf[index + counter + 2] & 0xFF));
				es_info_length = (((buf[index + counter + 3] & 0xF) << 8) | 
							(buf[index + counter + 4]));
				counter += (5 + es_info_length);
				# Find the PIDs for audio and video elementary streams
				# The assumption is such that the H264 codec is being used for video
				# and MPEG2 audio codec is being used for audio compression
				print "Stream type: %d" % (stream_type);
				print "Elementary PID: %d" % (elementary_pid); 
				if stream_type == STREAM_TYPE_H264:
					#if not video_pid:
					video_pid = elementary_pid;
					lookup.set_video_pid_stream_id(stream_id, video_pid);
					#video_fd = open(config["DEMUX"], "w+");
					print "Seting up filter for video elementary stream %d for stream %d" % (video_pid, stream_id)
					#if video_fd < 0:
					#	print "Cannot open file";
					#	exit(-1);
					#if set_pesfilter(video_fd, video_pid, DMX_PES_VIDEO) < 0:
					if add_pidfilter(fd, video_pid):
						print "Cannot set video filter. Exiting...";
						exit(-1);
				if stream_type == STREAM_TYPE_MPEG2_AUDIO or stream_type == STREAM_TYPE_AAC or stream_type == STREAM_TYPE_AC3 or stream_type == STREAM_TYPE_MPEG1_AUDIO:
					#if not audio_pid:
					audio_pid = elementary_pid;
					lookup.set_audio_pid_stream_id(stream_id, audio_pid);
					print "Seting up filter for audio elementary stream %d" % audio_pid 
					#audio_fd = open(config["DEMUX"], "w+");
					#if audio_fd < 0:
					#	print "Cannot open file";
					#	exit(-1);
					#if set_pesfilter(audio_fd, audio_pid, DMX_PES_AUDIO) < 0:
					if add_pidfilter(fd, audio_pid):
						print "Cannot set video filter. Exiting...";
						exit(-1);
		elif lookup.is_valid_pmt_pid(pid) and pmt_packet_processed.get(pid, False):
			continue;
		#if pid == PAT_PID:
		#	print "Storing the PAT in the buffer... This should occur only once"
		#	sequence_buffer[buffer_fill:buffer_fill + TS_PACKET_SIZE] = buf;
		#	buffer_fill += TS_PACKET_SIZE;
		#	continue;
		#if pid == pmt_pid:
		#	print "Storing the PMT packet in the buffer... This should occur only once"
		#	sequence_buffer[buffer_fill:buffer_fill + TS_PACKET_SIZE] = buf;
		#	buffer_fill += TS_PACKET_SIZE;
		#	continue;
		# Slice the MPEG-TS stream at I-frame boundary
		#print "PID of the packet %d" % pid;
		#print "Stream ID %d" % (lookup.get_stream_id_by_video_pid(pid));
		#print "lookup.is_valid_video_pid(pid) %d " % lookup.is_valid_video_pid(pid)
		#print "payload_unit_start_indicator %d " % payload_unit_start_indicator
		#if lookup.is_valid_video_pid(pid) and payload_unit_start_indicator == 0x1:
		#	print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
		#	print "Is key frame %d" % is_key_frame(buf);
		#	print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
		if lookup.is_valid_video_pid(pid) and payload_unit_start_indicator == 0x1 and is_key_frame(buf):
			stream_id = lookup.get_stream_id_by_video_pid(pid);
			#print "Stream ID %d, Buffer fill level %d, Maximum buffer size %d " % (stream_id, buffer_fill[stream_id], MAX_BUFFER_SIZE_IN_BYTES);
			#print "Stream id %d" % stream_id;
			if buffer_fill[stream_id] >= MAX_BUFFER_SIZE_IN_BYTES:
				# We need to copy the sequence buffer otherwise some packets can be overwritten
				sequence_buffer_copy = copy.deepcopy(sequence_buffer[stream_id][0:buffer_fill[stream_id]]);
				threading.Thread(target=save_buffer, args=(sequence_buffer_copy, output_folder[stream_id], sequence[stream_id])).start();
				sequence[stream_id] = sequence[stream_id] + 1;
				if sequence[stream_id] > MAX_SEQUENCE_PER_FOLDER:
					sequence[stream_id] = 1;
					playlist_constructed[stream_id] = False;
					playing_timestamp[stream_id] = waiting_timestamp[stream_id];
					waiting_timestamp[stream_id] = filling_timestamp[stream_id];
					filling_timestamp[stream_id] = int(time.time());
					output_folder[stream_id] = "".join([base_dir, "/", str(stream_id), "/", str(filling_timestamp[stream_id])]);
					create_folder(output_folder[stream_id]);
				# Copy PAT, PMT and first packet of a new PES carrying video data
				# First two packets of a segment MUST be PAT and PMT packets 
				# as described in https://tools.ietf.org/html/rfc8216#section-3
				buffer_fill[stream_id] = 0;
				sequence_buffer[stream_id][buffer_fill[stream_id]:buffer_fill[stream_id] + TS_PACKET_SIZE] = pat_packet;
				buffer_fill[stream_id] += TS_PACKET_SIZE;
				sequence_buffer[stream_id][buffer_fill[stream_id]:buffer_fill[stream_id] + TS_PACKET_SIZE] = pmt_packet;
				buffer_fill[stream_id] += TS_PACKET_SIZE;
				continue;
			if (sequence[stream_id] == MAX_SEQUENCE_PER_FOLDER / 2) and buffer_fill[stream_id] >= (MAX_BUFFER_SIZE_IN_BYTES * 0.1) and not playlist_constructed[stream_id] and playing_timestamp[stream_id] > 0:
				playlist_constructed[stream_id] = True;
				print "Constructing playlist (timestamp %d)" % (playing_timestamp[stream_id]);
				threading.Thread(target=construct_playlist, args=("".join([base_dir, "/", str(stream_id), "/", str(playing_timestamp[stream_id])]), "".join([base_dir, "/", str(stream_id), "/"]), WEB_PATH, stream_id, playing_timestamp[stream_id], config["ENABLE_STREAM_ENCRYPTION"], )).start();
			sequence_buffer[stream_id][buffer_fill[stream_id]:buffer_fill[stream_id] + TS_PACKET_SIZE] = buf;
			buffer_fill[stream_id] += TS_PACKET_SIZE;
			continue;
			#elif pid == video_pid and pid != 0x0:
		elif lookup.is_valid_video_pid(pid):
			stream_id = lookup.get_stream_id_by_video_pid(pid);
			#print "Stream id %d, buffer fill %d" % (stream_id, buffer_fill[stream_id]);
			sequence_buffer[stream_id][buffer_fill[stream_id]:buffer_fill[stream_id] + TS_PACKET_SIZE] = buf;
			buffer_fill[stream_id] += TS_PACKET_SIZE;
			continue;
		if lookup.is_valid_audio_pid(pid):
			stream_id = lookup.get_stream_id_by_audio_pid(pid);
			#if pid == audio_pid and pid != 0x0:
			#print "Stream id %d, buffer fill %d" % (stream_id, buffer_fill[stream_id]);
			sequence_buffer[stream_id][buffer_fill[stream_id]:buffer_fill[stream_id] + TS_PACKET_SIZE] = buf;
			buffer_fill[stream_id] += TS_PACKET_SIZE;

# Saves the buffer into the output folder
def save_buffer(buf, output_folder, sequence):
	#print "Saving the buffer of size %d" % (len(buf));
	try:
		# Obtain the lock
		#fd = open("".join([output_folder, "/", "lock"]), "w+");
		#fd.write("processing...");
		#fd.flush();
		#fd.close();
		fd = open("".join([output_folder, "/", str(sequence), ".raw"]), "wb");
		print "Saving the buffer..."
		fd.write(buf);
		fd.flush();
		fd.close();
		#I think there is no need to do extra conversion since we already have MPEG2-TS stream which should be readable by the players
		#The conversion is needed if we need to use different container type for example MPEG-4 contaiener.
		#Also Flash does not support MPEG2 audio, so we need to transcode audio signal to AAC for example 
		ts_path_no_extension = "".join([output_folder, "/", str(sequence)]);
		result=os.popen("".join([config["EXEC_DIR"], "/", config["CONVERT_RAW_TS"], " ", ts_path_no_extension])).read().strip();
		#os.remove("".join([output_folder, "/", "sequence", str(sequence), ".raw"]));
		set_ownership("".join([ts_path_no_extension, ".ts"]));
		# Release the lock
		#remove_file("".join([output_folder, "/", "lock"]));
		#set_ownership("".join([output_folder, "/", "sequence", str(sequence), ".ts"]));
	except Exception as e:
		print "Error saving the buffer..."
		print str(e);
		exit(-1);

def construct_playlist(source_folder, output_folder, current_web_path, stream_id, timestamp, encrypt):
	# Wait until the lock from the directory is removed by other concurrent thread
	#while os.path.isfile("".join([source_folder, "/lock"])):
	#	sleep(0.1);
	sequence_file_name = "".join([output_folder + "/sequence.dat"]);
	#print "Constructing the playlist. Sequence file is %s" % (sequence_file_name);
	if not os.path.isfile(sequence_file_name):
		sequence_file = open("".join([output_folder + "/sequence.dat"]), "w+");
	else:
		sequence_file = open("".join([output_folder + "/sequence.dat"]), "r+");
	try:
		sequence = int(sequence_file.readline().rstrip());
	except Exception as e:
		#print "Exception occured while reading the file %s" % (str(e));
		sequence = 0;
	# print "Using next sequence %d " % (sequence);
	# This solves the problem with continous streaming of the video,
	# We should increment the sequence by number of segments in the file NOT by 1
	# as discussed in https://tools.ietf.org/html/rfc8216#section-3
	sequence += config["NUMBER_OF_SEQUENCIES_PER_FOLDER"];
	sequence_file.seek(0);
	sequence_file.write(str(sequence) + "\n");
	sequence_file.flush();
	sequence_file.close();
	ts_files = [];
	print "Listing the current directory... %s" % (source_folder);
	for file in os.listdir(source_folder):
		print file
	durations = [];
	for i in range(1, MAX_SEQUENCE_PER_FOLDER + 1):
		#ts_file = "sequence" + str(i) + ".ts";
		ts_file = str(i) + ".ts";
		ts_files.append(ts_file);
		ts_file_full_path = "".join([source_folder, "/", ts_file]);
		#print ts_file_full_path;
		result=os.popen("".join([config["EXEC_DIR"], "/", config["EXTRACT_DURATION_SCRIPT"], " ", ts_file_full_path])).read().strip();
		durations.append(result);
		# Does not work yet
		if encrypt:
			fd = open(ts_file_full_path, "rb");
			buf = fd.read();
			fd.close();
			enc_key_file_name = "".join([source_folder, "/enc.key"]);
			iv_file_name = "".join([source_folder, "/enc.iv"]);
			if not os.path.isfile(enc_key_file_name):
				fd = open(enc_key_file_name, "wb");
				key = HLSCipher.generateKey();
				fd.write(key);
				fd.flush();
				fd.close();
				fd = open(iv_file_name, "wb");
				iv = HLSCipher.generateIV();
				fd.write(iv);
				fd.flush();
				fd.close();
				buf = HLSCipher.encrypt(buf, key, iv);
			else:
				fd = open(enc_key_file_name, "rb");
				key=fd.read(KEY_SIZE);
				fd.close();
				fd = open(iv_file_name, "rb");
				iv=fd.read(IV_SIZE);
				fd.close();
				buf = HLSCipher.encrypt(buf, key, iv);
			fd = open(ts_file_full_path, "wb");
			fd.write(buf);
			fd.flush();
			fd.close();
	max_duration = max(durations);
	playlist = "#EXTM3U\r\n";
	playlist += "#EXT-X-TARGETDURATION:" + str(max_duration) + "\r\n";
	playlist += "#EXT-X-VERSION:" + str(config["M3U8_VERSION"]) + "\r\n";
	playlist += "#EXT-X-MEDIA-SEQUENCE:" + str(sequence) + "\r\n";
	playlist += "#EXT-X-PROGRAM-DATE-TIME:" + datetime.datetime.fromtimestamp(timestamp).isoformat() + "Z\r\n";
	if encrypt:
		iv_file_name = "".join([source_folder, "/enc.iv"]);
		fd = open(iv_file_name, "rb");
		iv = fd.read(IV_SIZE);
		fd.close();
		iv_hex = HLSCipher.encodeIV(iv);
		# https://tools.ietf.org/html/draft-pantos-hls-rfc8216bis-02#section-4.4.2.4
		#/streaming/keyfile/<int:stream_id>/<int:timestamp>/enc.key
		playlist += "#EXT-X-KEY:METHOD=AES-128,URI=/streaming/keyfile/" + str(stream_id) + "/" + str(timestamp) + "/enc.key,IV=" + iv_hex + "\r\n";
	for i in range(0, len(durations)):
		playlist += "#EXTINF:" + str(durations[i]) + ",\r\n";
		playlist += current_web_path + str(stream_id) + "/" + str(timestamp) + "/" +  str(i + 1) + ".ts\r\n";
	stream_file = open("".join([output_folder + "/stream.m3u8"]), "w");
	stream_file.write(playlist);
	stream_file.flush();
	stream_file.close();
	set_ownership("".join([output_folder + "/stream.m3u8"]));

class cron_task():
	def __init__(self, name, script, params, interval):
		self.name = name;
		self.script = script;
		self.params = params;
		self.interval = interval;
		self.next_scheduled_execution = int(time.time());

	def execute_task(self):
		print "Executing the cron task: %s" % (self.name);
		print os.popen("".join(["python ", self.script, " ", self.params])).read().strip();

	def run(self):
		now = time.time()
		if now >= self.next_scheduled_execution:
			self.next_scheduled_execution = now + self.interval;
			threading.Thread(target=self.execute_task).start();

def cron_loop(poll_interval, tasks):
	print "Starting cron loop execution..."
	while True:
		for task in tasks:
			task.run();
		sleep(poll_interval);

def run_cron_tasks():
	poll_interval = config["CRON"]["POLL_INTERVAL"];
	tasks = [];
	for task_config in config["CRON"]["TASKS"]:
		task = cron_task(task_config["NAME"], task_config["SCRIPT"], task_config["PARAMS"], task_config["INTERVAL_IN_SECONDS"]);
		tasks.append(task);
	threading.Thread(target=cron_loop, args=(poll_interval, tasks, )).start();

def set_up_demux(pid, type):
	fd = open(config["DEMUX"], "w+");
	if fd < 0:
		print "Opening demux file failed";
		return None;
	if set_pesfilter(fd, pid, type) < 0:
		print "Cannot set filter. Exiting...";
		return False;
	return fd;

params = init_tuning_defaults();
print "Tuning the device..."
tune(open(config["FRONTEND"], "w+"), params);
print "Setting DEMUX filters";
fd = set_up_demux(PAT_PID, DMX_PES_OTHER)
if not fd:
	print "Could not set the filter. We should exit now...";
	exit(-1);
print "Running the cron task loop...";
run_cron_tasks();
print "The device is tuned. Starting to capture the stream from device %s" % (config["DVR"]);
#capture(open(config["DVR"], "rb"));
capture(fd);
#print "Adding PID filter: %d" % add_pidfilter(fd, 2201);
