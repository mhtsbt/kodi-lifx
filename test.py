import socket


sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sender.bind(('',56700))

#sender.connect(('255.255.255.255', 56700));

##listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
#sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#sender.bind(('',56700));

ownIp = socket.gethostbyname(socket.gethostname());

packetArray = bytearray([0x24, 0x00, 0x00, 0x34, 0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00])

sender.sendto(packetArray,('255.255.255.255', 56700));

deviceIp = ownIp;

sender.setblocking(0)

#while deviceIp == ownIp:
while True:
	try:
		m =sender.recvfrom(1024);
		print(m);
	except socket.error:
		'''no data yet..'''
#	deviceIp = addr[0];


print("hello world");

#listener.close();

#sender.close();