from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import time
import telepot
from telepot.delegate import per_chat_id, create_open
import json
import feedparser


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
    MENU2 = '2. 모니터링 시작'
    #base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"
    your_searchs = []
    monitoring_status = False
    navi = feedparser.FeedParserDict()

    def __init__(self, seed_tuple, timeout):
        print("Init..")
        super(ClienHelper, self).__init__(seed_tuple, timeout)\

        #self.sender.sendMessage('

    def menu(self):
        monitoring_status =''
        show_keyboard = {'keyboard': [[self.MENU1], [self.MENU2], [self.MENU0]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def answer(self, comment):
        show_keyboard = {'keyboard': [[self.YES, self.NO], [self.MENU0]]}
        self.sender.sendMessage(comment, reply_markup=show_keyboard)

    def set_search_keyword(self):
        self.mode = self.MENU1_1
        self.sender.sendMessage('모니터링 키워드를 입력하세요.')

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def handle_command(self, command):
        if command == self.MENU0:
            self.menu()
        elif command == self.MENU1:
            self.set_search_keyword()

    def on_message(self, msg):
        print("on message")
        content_type, chat_type, chat_id = telepot.glance2(msg)
        if content_type is 'text':
            self.handle_command(unicode(msg['text']))
            return

    def marketMonitor():
        base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"
        #base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=park"

        url_request = Request(base_url,headers={'User-Agent': 'Mozilla/5.0'})

        clien_tip_board = urlopen(url_request).read()

        bs4_clien = BeautifulSoup(clien_tip_board,"html.parser")
        find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

        base_id = int(find_mytr[0].find('td').get_text(strip=True))

        #base_id = 1225523

        #your_searchs = ["맥북", "에어", "레티나", "스마트"]
        self.your_searchs = ["에어", "맥북", "레티나", "스마트"]

        while True:
            print("Read Clien board %s" % base_id)
            clien_tip_board = urlopen(url_request).read()

            bs4_clien = BeautifulSoup(clien_tip_board,"html.parser")
            find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

            #print(find_mytr[0].find('td').get_text(strip=True))
            top_id = int(find_mytr[0].find('td').get_text(strip=True))

            for t in find_mytr:
                #print(t.find('wr_id').get_text(strip=True))
                current_id = int(t.find('td').get_text(strip=True))
                category = t.find('td',attrs={'class':'post_category'}).get_text(strip=True)
                item = t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949')

        #        print(current_id, base_id, category, your_search, item)
                if current_id > base_id and category == "[판매]":
                    for your_search in self.your_searchs:
                        #print(your_search)
                        if your_search in item:
                            #print(t)
                            #print(t.find('td',attrs={'class':'post_category'}).get_text(strip=True))
                            print("제목 : "+t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949'))
                            title = "제목 : "+t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949')+"\n"
                            print("url : "+urljoin(base_url,t.find('td',attrs={'post_subject'}).a.get('href')))
                            url_result = urljoin(base_url,t.find('td',attrs={'post_subject'}).a.get('href'))
                            result = title + url_result
                    #        print("글쓴이 : "+t.find('td',attrs={'class' : 'post_name'}).get_text(strip=True))
                            bot.sendMessage(my_chat_id, result)
                            break
                elif current_id == base_id:
                    base_id = top_id
                    #print("base id is %s %s" % (base_id, top_id))

            time.sleep(60)

#my_chat_id = 62233150
#TOKEN = '175881767:AAG6nfgAprdHkTjbK6JZdZdsE76cbu5kMhE'

CONFIG_FILE = '../setting.json'

def parseConfig(filename):
    f = open(filename, 'r')
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

TOKEN = '199048259:AAGtyE1_vvXFMEPQ24a3-qf8s4ifqPpP85U'
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(ClienHelper, timeout=120)),
])

print(bot)
bot.notifyOnMessage(run_forever=True)





#curl "https://api.telegram.org/bot199048259:AAGtyE1_vvXFMEPQ24a3-qf8s4ifqPpP85U/sendMessage?chat_id=62233150&text=$startMsg"

#bot.sendMessage(my_chat_id, startMsg)


#show_keyboard = {'keyboard': [['Yes','No'], ['Maybe','Maybe not']]}
#bot.sendMessage(my_chat_id, 'This is a custom keyboard', reply_markup=show_keyboard)


