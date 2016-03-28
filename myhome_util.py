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

# download pip
# wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
#  python -m pip install BeautifulSoup4
# python3 -m pip install telepot
# https://github.com/nickoala/telepot

class MyHomeHelper(telepot.helper.ChatHandler):
    YES = '1. OK'
    NO = '2. NO'
    MENU0 = '홈으로'
    MENU1 = '1. 날씨'
    MENU1_1 = '1. 저장된 지역'
    MENU1_2 = '2. 스케쥴 알림내역'
    MENU2 = '2. Wake on Lan'
    MENU2_1 = '1. 서버 목록'
    MENU2_2 = '1. 서버 등록'
    MENU2_3 = '2. 서버 삭제'
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
        print(command)
        db = MySQLdb.connect("127.0.0.1","root","root","home_utils")
        cursor = db.cursor()

        sql = "INSERT INTO weather(chat_id,command) VALUES(%s, '%s')" % (chat_id,  command)
        cursor.execute(sql)
        # handle exception of duplicate data

        db.commit()

        select_sql = "SELECT * FROM home_utils.command where chat_id = %d" % chat_id
        cursor.execute(select_sql)
        result = cursor.fetchall()

        db.close()
        print(result)
        self.show_weather(result)


    def show_weather(self, location):
        show_keyboard = {'keyboard': self.put_menu_button(location)}
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)
        self.mode=self.MENU1_2

    def wol_menu(self):
        show_keyboard = {'keyboard': [[self.MENU2_1], [self.MENU2_2], [self.MENU2_3], [self.MENU0]]}
        self.sender.sendMessage(self.WOL, reply_markup=show_keyboard)
        self.mode = self.MENU2

    def answer(self, comment):
        show_keyboard = {'keyboard': [[self.YES, self.NO], [self.MENU0]]}
        self.sender.sendMessage(comment, reply_markup=show_keyboard)

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
            self.set_mode(self.MENU1_1)
        elif command == self.MENU1_2:
            self.set_mode(self.MENU1_2)
        elif command == self.MENU2:
            self.wol_menu()
        elif command == self.MENU2_1:
            self.stop_marketMonitor()
        elif command == self.MENU2_2:
            self.stop_marketMonitor()
        elif self.mode == self.MENU1:
            self.register_location(command, chat_id)
        elif self.mode == self.MENU1_2:
            self.weather_menu(command, chat_id)

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)

        if not chat_id in VALID_USERS:
            print("Permission Denied")
            return

        if content_type is 'text':
            print(content_type, msg['text'])
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







