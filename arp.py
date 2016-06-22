#!/usr/bin/env python
# -*- coding: utf-8 -*-

 
import sys
import os
import telepot
import time
from scapy.all import *
 
if len(sys.argv) != 2:
    print "Usage: python arp.py 192.168.1.0/24"
    sys.exit(1)

bot = telepot.Bot("")
my_chat_id = ''
 
while True:
	try:
		alive,dead=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=sys.argv[1]), iface="eth0", timeout=2)
		for i in range(0,len(alive)):
			# need wifi mac address
			if alive[i][1].hwsrc == '14:32:d1:a8:80:be':
				result = "마눌님이 집에 오셨습니다"
				bot.sendMessage(my_chat_id, result)
				sys.exit(1)
	except SystemExit as e:
		sys.exit(e)
	time.sleep(5)
