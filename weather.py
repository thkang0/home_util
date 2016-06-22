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
    navi = feedparser.FeedParserDict()
    GREETING = "안녕하세요. 메뉴를 선택해주세요."
    WEATHER = "날씨 메뉴입니다. 지역을 입력하시거나 저장된 지역의 날씨를 확인할 수 있습니다."
    mode = ''

    def __init__(self, seed_tuple, timeout):
        super(MyHomeHelper, self).__init__(seed_tuple, timeout)
        #self.menu()

    def open(self, initial_msg, seed):
        #self.sender.sendMessage('동네 예보를 기반으로 한 날씨 예보입니다.')
        pass
#        self.menu()

    def menu(self):
        show_keyboard = {'keyboard': [[self.MENU1], [self.MENU2]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)
        self.mode = self.MENU0


    def weather(self, command):
        location = command.split(' ')[0]
        try:
            tomorrow = command.split(' ')[1] 
        except:
            tomorrow = None
        self.show_weather(location, tomorrow)

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
        #llxy.close()
        return self.grid(lat, lng)


    def show_weather(self, location, tomorrow):
        #show_keyboard = {'keyboard': [[self.MENU2_1], [self.MENU2_2], [self.MENU2_3], [self.MENU0]]}
        #self.sender.sendMessage('해당 지역의 '+ location + ' 날씨입니다', reply_markup=show_keyboard)
        self.sender.sendMessage(location + ' 날씨입니다')
        # show the weather of the location
        url = self.getXY(location)
        url_request = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        weather = urlopen(url_request).read()
        data = xmltodict.parse(weather)
        #time = data['wid']['header']['tm']+"\n"
        hour = data['wid']['body']['data'][0]['hour']
        temp = "현재 기온 : " + data['wid']['body']['data'][0]['temp']+"도\n"
        sky = "현재 날씨 : " + data['wid']['body']['data'][0]['wfKor']+"\n"
        pop = "강수 확율 : " + data['wid']['body']['data'][0]['pop']+"%\n"
        #print(data['wid']['body']['data'])
        index = 0
        current_index = 0
        if hour == '21':
            index = 4
        elif hour == '24':
            index = 3
        elif hour == '3':
            index = 2
        elif hour == '6':
            index = 1
        elif hour == '9':
            index = 8
            current_index = 4
        elif hour == '12':
            index = 7
            current_index = 3
        elif hour == '15':
            index = 6
            current_index = 2
        elif hour == '18':
            index = 5
            current_index = 1
        #print(hour, index)
        #current = temp + sky+ pop
        if tomorrow is None:
            current = "금일 날씨는 \n" + hour + "시 기준 ==> " +  data['wid']['body']['data'][0]['temp']+"도, " + data['wid']['body']['data'][0]['wfKor'] \
                  + ", 강수확율은 " + data['wid']['body']['data'][0]['pop']+"%, 최대기온은 " + data['wid']['body']['data'][0]['tmx']+"도 \n"
            inc = 1
            for i in range(current_index):
                next_time = int(hour)+ inc*3
                current +=  str(next_time) + "시 기준 ==> "  +  data['wid']['body']['data'][inc]['temp']+"도, " + data['wid']['body']['data'][inc]['wfKor'] \
                    + ", 강수확율은 " + data['wid']['body']['data'][inc]['pop']+"%, 최대기온은 " + data['wid']['body']['data'][inc]['tmx']+"도 \n"
                inc += 1
            self.sender.sendMessage(current)

        if tomorrow is None:
            return

        tomorrow_temp = "현재 기온 : " + data['wid']['body']['data'][index]['temp']+"도\n"
        tomorrow_sky = "현재 날씨 : " + data['wid']['body']['data'][index]['wfKor']+"\n"
        tomorrow_pop = "강수 확율 : " + data['wid']['body']['data'][index]['pop']+"%\n"
        tomorrow_tmx = "최고 온도 : " + data['wid']['body']['data'][index]['tmx']+"도\n"
        tomorrow_tmn = "최저 온도 : " + data['wid']['body']['data'][index]['tmn']+"도\n"
        #tomorrow = "내일 오전(9시) 날씨는 \n" + tomorrow_temp + tomorrow_sky + tomorrow_pop + tomorrow_tmx + tomorrow_tmn
        
        tomorrow = "내일 날씨는 \n" + "오전 9시 ==> " +  data['wid']['body']['data'][index]['temp']+"도, " + data['wid']['body']['data'][index]['wfKor'] \
              + ", 강수확율은 " + data['wid']['body']['data'][index]['pop']+"%, 최대 " + data['wid']['body']['data'][index]['tmx']+"도, 최저 " \
              + data['wid']['body']['data'][index]['tmn']+"도 \n" \
              + "오후 12시 ==> " +  data['wid']['body']['data'][index+1]['temp']+"도, " + data['wid']['body']['data'][index+1]['wfKor'] \
              + ", 강수확율은 " + data['wid']['body']['data'][index+1]['pop']+"%, 최대 " + data['wid']['body']['data'][index+1]['tmx']+"도, 최저 " \
              + data['wid']['body']['data'][index+1]['tmn']+"도 \n" \
              + "오후 3시 ==> " +  data['wid']['body']['data'][index+2]['temp']+"도, " + data['wid']['body']['data'][index+2]['wfKor'] \
              + ", 강수확율은 " + data['wid']['body']['data'][index+2]['pop']+"%, 최대 " + data['wid']['body']['data'][index+2]['tmx']+"도, 최저 " \
              + data['wid']['body']['data'][index+2]['tmn']+"도 \n" \
              + "오후 6시 ==> " +  data['wid']['body']['data'][index+3]['temp']+"도, " + data['wid']['body']['data'][index+3]['wfKor'] \
              + ", 강수확율은 " + data['wid']['body']['data'][index+3]['pop']+"%, 최대 " + data['wid']['body']['data'][index+3]['tmx']+"도, 최저 " \
              + data['wid']['body']['data'][index+3]['tmn']+"도 \n" \

        self.sender.sendMessage(tomorrow)
        #url_request.close()

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def handle_command(self, command, chat_id):
        self.weather(command) 

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
    TOKEN = config['weather']['token']
    VALID_USERS = config['weather']['valid_users']

config = parseConfig(CONFIG_FILE)

if not bool(config):
    print ("Err: Setting file is not found")
    exit()

getConfig(config)

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MyHomeHelper, timeout=120)),
])

bot.notifyOnMessage(run_forever=True)







