from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import time
import telepot
from telepot.delegate import per_chat_id, create_open
import json
import feedparser
import codecs


# download pip
# wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
#  python -m pip install BeautifulSoup4
# python3 -m pip install telepot
# https://github.com/nickoala/telepot

class ClienHelper(telepot.helper.ChatHandler):
    YES = '1. OK'
    NO = '2. NO'
    MENU0 = '홈으로'
    MENU1 = '1. 클리앙 장터 모니터링 검색어'
    MENU1_1 = '모니터링 키워드'
    MENU2 = '2. 모니터링 시작'
    MENU3 = '3. 모니터링 정지'
    #base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"
    your_searches = []
    monitoring_status = False
    navi = feedparser.FeedParserDict()
    GREETING = "안녕하세요. 메뉴를 선택해주세요."
    mode = ''

    def __init__(self, seed_tuple, timeout):
        print("Init..")
        super(ClienHelper, self).__init__(seed_tuple, timeout)

        #self.sender.sendMessage('

    def open(self, initial_msg, seed):
        self.menu()

    def menu(self):
        show_keyboard = {'keyboard': [[self.MENU1], [self.MENU2], [self.MENU0]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def answer(self, comment):
        show_keyboard = {'keyboard': [[self.YES, self.NO], [self.MENU0]]}
        self.sender.sendMessage(comment, reply_markup=show_keyboard)

    def get_search_keyword(self):
        self.mode = self.MENU1_1
        self.sender.sendMessage('모니터링 키워드를 입력하세요.')

    def set_search_keyword(self, keyword):
        self.your_searches.append(keyword)
        # need to put keywords into mysql db
        self.monitoring_status = True
        self.sender.sendMessage('현재 모니터링중인 항목은 ')
        self.sender.sendMessage(self.your_searches)

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def handle_command(self, command):
        if command == self.MENU0:
            self.menu()
        elif command == self.MENU1:
            self.get_search_keyword()
        elif command == self.MENU2:
            self.marketMonitor()
        elif command == self.MENU3:
            self.stop_marketMonitor()
        elif self.mode == self.MENU1_1:
            self.set_search_keyword(command)

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)

        if not chat_id in VALID_USERS:
            print("Permission Denied")
            return

        if content_type is 'text':
            print(content_type, msg['text'])
            #self.handle_command(unicode(msg['text']))
            self.handle_command(str(msg['text']))
            return
    
    def stopmarketMonitor(self):
        self.monitoring_status = False
        self.sender.sendMessage('모니터링을 정지합니다.')
        self.mode = ''
        return

    def marketMonitor(self):
        if self.your_searches is None:
            self.sender.sendMessage('현재 모니터링 항목이 없습니다.')
            return

        if self.monitoring_status is False:
            return

        self.sender.sendMessage('모니터링을 시작합니다.')
        self.mode = 'self.MENU2'
        base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"

        url_request = Request(base_url,headers={'User-Agent': 'Mozilla/5.0'})

        for x in range(10): # Always limit number of retries
            try:
                clien_market_board = urlopen(url_request).read()
            except URLError:
                time.sleep(2)
                raise # re-raise any other error
            else:
                break 

        bs4_clien = BeautifulSoup(clien_market_board,"html.parser")
        find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

        base_id = int(find_mytr[0].find('td').get_text(strip=True))

        while self.monitoring_status is True:
            while True:
                try:
                    clien_market_board = urlopen(url_request).read()
                    break;
                except URLError:
                    time.sleep(10)
                    print("URL Open Error and now retrying")
                    #bot.sendMessage(my_chat_id, "URL Open Error and now retrying")
                    pass

            try:
                bs4_clien = BeautifulSoup(clien_market_board,"html.parser")
                find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

                top_id = int(find_mytr[0].find('td').get_text(strip=True))
            except:
                print("top_id = %s" % top_id)
                pass

            for t in find_mytr:
                current_id = int(t.find('td').get_text(strip=True))
                category = t.find('td',attrs={'class':'post_category'}).get_text(strip=True)
                item = t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949')

                if current_id > base_id and category == "[판매]":
                    for your_search in self.your_searches:
                        if your_search in item:
                            title = "제목 : "+t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949')+"\n"
                            url_result = urljoin(base_url,t.find('td',attrs={'post_subject'}).a.get('href'))
                            result = title + url_result
                            self.sender.sendMessage(result)
                            break

            base_id = top_id
            time.sleep(60)

#my_chat_id = 62233150
#TOKEN = '175881767:AAG6nfgAprdHkTjbK6JZdZdsE76cbu5kMhE'

CONFIG_FILE = 'setting2.json'

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

#TOKEN = '199048259:AAGtyE1_vvXFMEPQ24a3-qf8s4ifqPpP85U'
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(ClienHelper, timeout=120)),
])

print(bot)
bot.notifyOnMessage(run_forever=True)





#curl "https://api.telegram.org/bot199048259:AAGtyE1_vvXFMEPQ24a3-qf8s4ifqPpP85U/sendMessage?chat_id=62233150&text=$startMsg"

#bot.sendMessage(my_chat_id, startMsg)


#show_keyboard = {'keyboard': [['Yes','No'], ['Maybe','Maybe not']]}
#bot.sendMessage(my_chat_id, 'This is a custom keyboard', reply_markup=show_keyboard)


