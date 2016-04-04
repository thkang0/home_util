#-*- coding: utf-8 -*- 
from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import time
import telepot
from telepot.delegate import per_chat_id, create_open
import json
import feedparser
import codecs
import MySQLdb
import socket
import struct
import math
from urllib.parse import urlencode, quote
import xmltodict

# download pip
# wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
#  python -m pip install BeautifulSoup4
# python3 -m pip install telepot
# https://github.com/nickoala/telepot

class MyHomeHelper(telepot.helper.ChatHandler):
    YES = '1. OK'
    NO = '2. NO'
    MENU0 = '== 홈으로 =='
    MENU1 = '== 날씨 =='
    MENU1_1 = '1. 저장된 지역'
    MENU1_2 = '2. 스케쥴 알림내역'
    MENU2 = '== Wake on Lan =='
    MENU2_1 = '1. 서버 목록'
    MENU2_2 = '2. 서버 등록'
    MENU2_3 = '3. 서버 삭제'
    your_searches = []
    monitoring_status = False
    navi = feedparser.FeedParserDict()
    GREETING = "안녕하세요. 메뉴를 선택해주세요."
    WEATHER = "날씨 메뉴입니다. 지역을 입력하시거나 저장된 지역의 날씨를 확인할 수 있습니다."
    WOL = "Wake On Lan 기능입니다."
    mode = ''

    def __init__(self, seed_tuple, timeout):
        super(MyHomeHelper, self).__init__(seed_tuple, timeout)
        self.menu()

    def open(self, initial_msg, seed):
        self.menu()

    def menu(self):
        show_keyboard = {'keyboard': [[self.MENU1], [self.MENU2]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)
        self.mode = self.MENU0

    def weather_menu(self):
        show_keyboard = {'keyboard': [[self.MENU1_1], [self.MENU1_2], [self.MENU0]]}
        self.sender.sendMessage(self.WEATHER, reply_markup=show_keyboard)
        self.mode = self.MENU1

    def set_mode(self, current_mode):
        self.mode = current_mode 

    def register_location(self, command, chat_id):
        if command is self.MENU1_1:
            self.mode=self.MENU1_1
            self.location_menu(chat_id)
            return
        elif command is self.MENU1_2:
            self.mode=self.MENU1_2
            self.schedule_menu(chat_id)
            return
        elif command is self.MENU0:
            self.menu()
            return

        db = MySQLdb.connect("127.0.0.1","root","root","home_utils",charset='utf8', use_unicode=True)
        # because of latin1 encoding errors
        db.query("set character_set_connection=utf8;")
        db.query("set character_set_server=utf8;")
        db.query("set character_set_client=utf8;")
        db.query("set character_set_results=utf8;")
        db.query("set character_set_database=utf8;")

        cursor = db.cursor()

        sql = "INSERT INTO weather(chat_id,locations) VALUES(%s, '%s')" % (chat_id,  command)
        #cursor.execute("set names utf8")
        #cursor.execute(query.encode('utf8'))
        cursor.execute(sql.encode('utf8'))
        # handle exception of duplicate data

        db.commit()

        select_sql = "SELECT * FROM home_utils.weather where chat_id = %d" % chat_id

        cursor.execute("set names utf8")
        cursor.execute(select_sql.encode('utf8'))
        cursor.fetchall()

        # 튜플이 아닌 사전 형식으로 필드 가져오기
        #cursor = db.cursor(MySQLdb.cursors.DictCursor)
        result_locations = []
        for row in cursor:
            temp_list = []
            temp_list.append(row[2])
            result_locations.append(temp_list)
            
        cursor.close()
        db.close()

        result_locations.append([self.MENU1])
        show_keyboard = {'keyboard': self.put_menu_button(result_locations)}
        self.mode=self.MENU1_1
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)


    def location_menu(self, chat_id):
        self.mode=self.MENU1_1
        db = MySQLdb.connect("127.0.0.1","root","root","home_utils",charset='utf8', use_unicode=True)
        # because of latin1 encoding errors
        db.query("set character_set_connection=utf8;")
        db.query("set character_set_server=utf8;")
        db.query("set character_set_client=utf8;")
        db.query("set character_set_results=utf8;")
        db.query("set character_set_database=utf8;")

        cursor = db.cursor()

        select_sql = "SELECT * FROM home_utils.weather where chat_id = %d" % chat_id

        cursor.execute("set names utf8")
        cursor.execute(select_sql.encode('utf8'))
        cursor.fetchall()

        result_locations = []
        for row in cursor:
            temp_list = []
            temp_list.append(row[2])
            result_locations.append(temp_list)

        cursor.close()
        db.close()

        result_locations.append([self.MENU1])

        show_keyboard = {'keyboard': self.put_menu_button(result_locations)}
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)

    def grid(self, v1, v2):
        RE = 6371.00877 # 지구 반경(km)
        GRID = 5.0      # 격자 간격(km)
        SLAT1 = 30.0    # 투영 위도1(degree)
        SLAT2 = 60.0    # 투영 위도2(degree)
        OLON = 126.0    # 기준점 경도(degree)
        OLAT = 38.0     # 기준점 위도(degree)
        XO = 43         # 기준점 X좌표(GRID)
        YO = 136        # 기1준점 Y좌표(GRID)

        DEGRAD = math.pi / 180.0
        RADDEG = 180.0 / math.pi

        re = RE / GRID;
        slat1 = SLAT1 * DEGRAD
        slat2 = SLAT2 * DEGRAD
        olon = OLON * DEGRAD
        olat = OLAT * DEGRAD

        sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
        sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
        sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
        sf = math.pow(sf, sn) * math.cos(slat1) / sn
        ro = math.tan(math.pi * 0.25 + olat * 0.5)
        ro = re * sf / math.pow(ro, sn);
        rs = {};

        ra = math.tan(math.pi * 0.25 + (v1) * DEGRAD * 0.5)
        ra = re * sf / math.pow(ra, sn)

        theta = v2 * DEGRAD - olon
        if theta > math.pi :
            theta -= 2.0 * math.pi
        if theta < -math.pi :
            theta += 2.0 * math.pi
        theta *= sn
        rs['x'] = math.floor(ra * math.sin(theta) + XO + 0.5)
        rs['y'] = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

        string = "http://www.kma.go.kr/wid/queryDFS.jsp?gridx={0}&gridy={1}".format(str(rs["x"]).split('.')[0], str(rs["y"]).split('.')[0])
        return string

    #get latitude and longitude
    def getXY(self, location):
        google_address = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&language=ko&address='
        address = google_address+quote(location, "euc-kr")
        url_request = Request(address,headers={'User-Agent': 'Mozilla/5.0'})
        llxy = urlopen(url_request).read()
        js = json.loads(llxy.decode('utf8'))
        for i in js['results']:
            lng = i['geometry']['location']['lng']
            lat = i['geometry']['location']['lat']
        return self.grid(lat, lng)


    def show_weather(self, location):
        show_keyboard = {'keyboard': [[self.MENU2_1], [self.MENU2_2], [self.MENU2_3], [self.MENU0]]}
        self.sender.sendMessage('해당 지역의 '+ location + ' 날씨입니다', reply_markup=show_keyboard)
        # show the weather of the location
        print(location)
        url = self.getXY(location)
        url_request = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        weather = urlopen(url_request).read()
        data = xmltodict.parse(weather)
        time = data['wid']['header']['tm']
        temp = data['wid']['body']['data'][0]['temp']
        current = time + ' ' + temp +'도 입니다'
        self.sender.sendMessage(current, reply_markup=show_keyboard)

    def wol_menu(self):
        show_keyboard = {'keyboard': [[self.MENU2_1], [self.MENU2_2], [self.MENU2_3], [self.MENU0]]}
        self.sender.sendMessage(self.WOL, reply_markup=show_keyboard)
        self.mode = self.MENU2

    def list_servers(self):
        db = MySQLdb.connect("127.0.0.1","root","root","home_utils",charset='utf8', use_unicode=True)
        # because of latin1 encoding errors
        db.query("set character_set_connection=utf8;")
        db.query("set character_set_server=utf8;")
        db.query("set character_set_client=utf8;")
        db.query("set character_set_results=utf8;")
        db.query("set character_set_database=utf8;")

        cursor = db.cursor()

        select_sql = "SELECT * FROM home_utils.wol"

        cursor.execute("set names utf8")
        cursor.execute(select_sql.encode('utf8'))
        cursor.fetchall()

        result_servers = []
        for row in cursor:
            temp_list = []
            temp_list.append(row[1] + ' ' + row[2])
            result_servers.append(temp_list)

        cursor.close()
        db.close()

        if not result_servers:
            self.sender.sendMessage('현재 저장된 서버가 없습니다.')

        result_servers.append([self.MENU2])

        show_keyboard = {'keyboard': self.put_menu_button(result_servers)}
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)
        self.mode = self.MENU2_1

    def register_server_menu(self):
        show_keyboard = {'keyboard': [[self.MENU2], [self.MENU0]]}
        self.sender.sendMessage('서버를 등록해 주세요 ex) 데스크탑 aa:bb:cc:dd:ee:ff', reply_markup=show_keyboard)
        self.mode = self.MENU2_2

    def register_server(self, command, chat_id):
        db = MySQLdb.connect("127.0.0.1","root","root","home_utils",charset='utf8', use_unicode=True)
        # because of latin1 encoding errors
        db.query("set character_set_connection=utf8;")
        db.query("set character_set_server=utf8;")
        db.query("set character_set_client=utf8;")
        db.query("set character_set_results=utf8;")
        db.query("set character_set_database=utf8;")

        cursor = db.cursor()

        server = command.split(' ')[0]
        mac_address = command.split(' ')[1]
        print(server, mac_address) 

        sql = "INSERT INTO wol(host,mac) VALUES('%s', '%s')" % (server, mac_address)
        cursor.execute(sql.encode('utf8'))
        # handle exception of duplicate data

        db.commit()

        select_sql = "SELECT * FROM home_utils.wol"

        cursor.execute("set names utf8")
        cursor.execute(select_sql.encode('utf8'))
        cursor.fetchall()

        result_servers = []
        for row in cursor:
            temp_list = []
            temp_list.append(row[1] + ' ' + row[2])
            result_servers.append(temp_list)
            
        cursor.close()
        db.close()

        result_servers.append([self.MENU2])
        show_keyboard = {'keyboard': self.put_menu_button(result_servers)}
        self.mode=self.MENU2_1
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)

    def wol_server(self, command):
        server = command.split(' ')[0]
        mac_address = command.split(' ')[1]

        if len(mac_address) == 12:
            pass
        elif len(mac_address) == 12 + 5:
            sep = mac_address[2]
            mac_address = mac_address.replace(sep, '')
        else:
            self.sender.sendMessage('잘못된 Mac Address 형식입니다.', mac_address)
            return
     
        print("mac_address:", mac_address)
        
        data = ''.join(['FFFFFFFFFFFF', mac_address * 20])
        send_data = '' 

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
           send_data = ''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

        # Broadcast it to the LAN.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('192.168.0.255', 7))

    def wol_server2(self, command):
        server = command.split(' ')[0]
        mac_address = command.split(' ')[1]
        broadcast = ['192.168.0.255']
        wol_port = 9

        add_oct = mac_address.split(':')
        if len(add_oct) != 6:
            self.sender.sendMessage('잘못된 Mac Address 형식입니다.', mac_address)
            return
        hwa = struct.pack('BBBBBB', int(add_oct[0],16),
            int(add_oct[1],16),
            int(add_oct[2],16),
            int(add_oct[3],16),
            int(add_oct[4],16),
            int(add_oct[5],16))

        # Build magic packet
        msg = '\xff'.encode() * 6 + hwa * 16
        print("sending magic packet !!")

        # Send packet to broadcast address using UDP port 9
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        for i in broadcast:
            soc.sendto(msg,(i,wol_port))
        soc.close()

    def check_mac_address(self, mac_addr):
        return True

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def handle_command(self, command, chat_id):
        if command == self.MENU0:
            self.menu()
        elif command == self.MENU1:
            self.weather_menu()
        elif command == self.MENU1_1:
            self.location_menu(chat_id)
        elif command == self.MENU1_2:
            self.schedule_menu(chat_id)
        elif command == self.MENU2:
            self.wol_menu()
        elif command == self.MENU2_1:
            self.list_servers()
        elif command == self.MENU2_2:
            self.register_server_menu()
        elif self.mode == self.MENU1:
            self.register_location(command, chat_id)
        elif self.mode == self.MENU1_1:
            self.show_weather(command)
        elif self.mode == self.MENU1_2:
            self.register_weather_schedule(command, chat_id)
        elif self.mode == self.MENU2_1:
            self.wol_server2(command)
        elif self.mode == self.MENU2_2:
            self.register_server(command, chat_id)

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)

        if not chat_id in VALID_USERS:
            print("Permission Denied %s" % chat_id)
            return

        if content_type is 'text':
            print("recieving : ", msg['text'])
            #self.handle_command(unicode(msg['text']))
            self.handle_command(str(msg['text']), chat_id)
            return
    

CONFIG_FILE = 'setting.json'

def parseConfig(filename):
    f = codecs.open(filename, 'r', "utf-8" )
    js = json.loads(f.read())
    f.close()
    return js

def getConfig(config):
    global TOKEN
    global VALID_USERS
    TOKEN = config['common']['token']
    VALID_USERS = config['common']['valid_users']

config = parseConfig(CONFIG_FILE)

if not bool(config):
    print ("Err: Setting file is not found")
    exit()

getConfig(config)

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MyHomeHelper, timeout=120)),
])

bot.notifyOnMessage(run_forever=True)







