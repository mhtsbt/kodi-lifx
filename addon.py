import xbmc
import xbmcaddon
import xbmcgui
import os

import socket
import sys
import binascii
import colorsys
import struct

from binascii import unhexlify

addon = xbmcaddon.Addon();
def long_to_bytes (val):
   
    val = long(val);  
    val = struct.pack('<Q',val);
    val = val[::-1]
    val = ''.join( [ "%02X" % ord( x ) for x in val ] ).strip();
    return val[12:16]

def get_bulb_ip (bulbCount): 

	devices = []

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.bind(('', 56700))

	ownIp = socket.gethostbyname(socket.gethostname());

	packetArray = bytearray([0x24, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x65, 0x00, 0x00, 0x00])

	for x in range(0, 10):
		s.sendto(packetArray,('255.255.255.255', 56700));

	deviceCount = 0;

	while (deviceCount < bulbCount):
		data, addr =s.recvfrom(2048);
		deviceIp = addr[0];
		if (deviceIp <> ownIp and deviceIp not in devices):
			devices.append(deviceIp)
			deviceCount += 1
			print deviceIp

	s.close();

	return devices;

def send_to_devices (socket,hosts,message):

	for host in hosts:
		socket.sendto(message,(host, 56700));


bulbCount = int(addon.getSetting("bulbcount"));
refreshRate = int(addon.getSetting("refreshrate"));
min_brightness = int(addon.getSetting("minbrightness"))*655;

useLegacyApi   = True
capture = xbmc.RenderCapture()

if useLegacyApi:
	capture.capture(32, 32, xbmc.CAPTURE_FLAG_CONTINUOUS)

hosts = get_bulb_ip(2)

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

class PlayerMonitor( xbmc.Player ):
	def __init__( self, *args, **kwargs ):
		xbmc.Player.__init__( self )

	def onPlayBackStarted( self ):
		if not useLegacyApi:
			capture.capture(32, 32)


while not xbmc.abortRequested:
	xbmc.sleep(refreshRate)
	if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
		width = capture.getWidth();
		height = capture.getHeight();
		pixels = capture.getImage(1000);

		if useLegacyApi:
			capture.waitForCaptureStateChangeEvent(1000)
			
		pixels = capture.getImage(1000)

		red = [];
		green = [];
		blue = [];

		for y in range(height):
			row = width * y * 4
			for x in range(width):
				red.append(pixels[row + x * 4 + 2]);
				green.append(pixels[row + x * 4 + 1]);
				blue.append(pixels[row + x * 4]);


		red = (sum(red)/len(red))/255.00;
		green = (sum(green)/len(green))/255.00;
		blue = (sum(blue)/len(blue))/255.00;

		hsb = colorsys.rgb_to_hsv(red, green, blue);

		huevalue = int(hsb[0]*65535);
		huevalueHex = long_to_bytes(huevalue);
		satvalue = int(hsb[1]*65535);
		satvalueHex = long_to_bytes(satvalue);
		brightnessvalue = int(hsb[2]*65535);

		if brightnessvalue > min_brightness:
			brightnessvalueHex = long_to_bytes(brightnessvalue);
		else:
			brightnessvalueHex = long_to_bytes(min_brightness);


		packetArray = bytearray([0x31,0x00,0x00,0x34,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x66,0x00,0x00,0x00,0x00,0x55,0x55,0xFF,0xFF,0xFF,0xFF,0xAC,0x0D,0x00,0x00,0x00,0x00])

		packetArray[38] = unhexlify(huevalueHex[0:2]);
		packetArray[37] = unhexlify(huevalueHex[2:4]);

		packetArray[40] = unhexlify(satvalueHex[0:2]);
		packetArray[39] = unhexlify(satvalueHex[2:4]);

		packetArray[43] = unhexlify(brightnessvalueHex[0:2]);
		packetArray[42] = unhexlify(brightnessvalueHex[2:4]);

		try:			
			send_to_devices(s,hosts,packetArray)
		except:
			print "Caught exception socket.error"

s.close()

if ( __name__ == "__main__" ):

	player_monitor = PlayerMonitor()

	try:
		capture.getCaptureState()
	except AttributeError:
		useLegacyApi = False
