from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from urllib.error import URLError
import time
import telepot
import json
import sys
import codecs


# download pip
# wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
#  python -m pip install BeautifulSoup4
# python3 -m pip install telepot
# python3 -m pip install feedparser

CONFIG_FILE = 'setting.json'

def parseConfig(filename):
    f = codecs.open(filename, 'r', "utf-8" )
    js = json.loads(f.read())
    f.close()
    return js

def getConfig(config):
    global TOKEN
    global VALID_USERS
    global SEARCH_KEYWORDS
    global my_chat_id
    TOKEN = config['common']['token']
    VALID_USERS = config['common']['valid_users']
    my_chat_id = VALID_USERS[0]
    SEARCH_KEYWORDS = config['search_keywords']

config = parseConfig(CONFIG_FILE)
print(config)

if not bool(config):
    print ("Err: Setting file is not found")
    exit()

getConfig(config)

bot = telepot.Bot(TOKEN)

startMsg="Clien Monitor 서비스가 시작되었습니다."
bot.sendMessage(my_chat_id, startMsg)

#hide_keyboard = {'hide_keyboard': True}
#bot.sendMessage(my_chat_id, 'I am hiding it', reply_markup=hide_keyboard)

# 장터
base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"
# 모두의 공원
#base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=park"


# @retry(URLError, tries=4, delay=3, backoff=2)
# def urlopen_with_retry(url_request):
#     return urlopen(url_request).read()

# @retry(urllib2.URLError, tries=4, delay=3, backoff=2)
# def urlopen_with_retry():
#     return urllib2.urlopen("http://example.com")

url_request = Request(base_url,headers={'User-Agent': 'Mozilla/5.0'})

for x in range(10): # Always limit number of retries
    try:
        clien_market_board = urlopen(url_request).read()
    #    resp = urllib.request.urlopen(req)
    except URLError:
        if e.reason[0] == 104: # Will throw TypeError if error is local, but we probably don't care
            time.sleep(2)
        else:
            raise # re-raise any other error
    else:
        break # We've got resp sucessfully, stop iteration

#clien_market_board = urlopen(url_request).read()

#clien_market_board = urlopen_with_retry(url_request)

bs4_clien = BeautifulSoup(clien_market_board,"html.parser")
find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

base_id = int(find_mytr[0].find('td').get_text(strip=True))

while True:
    #print("Read Clien board %s" % base_id)
    #clien_market_board = urlopen(url_request).read()

    for x in range(10): # Always limit number of retries
        try:
            clien_market_board = urlopen(url_request).read()
        #    resp = urllib.request.urlopen(req)
        except URLError:
            if e.reason[0] == 104: # Will throw TypeError if error is local, but we probably don't care
                time.sleep(2)
            else:
                raise # re-raise any other error
                bot.sendMessage(my_chat_id, "URL Open Error and now retrying")
        else:
            break # We've got resp sucessfully, stop iteration


    bs4_clien = BeautifulSoup(clien_market_board,"html.parser")
    find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

    #print(find_mytr[0].find('td').get_text(strip=True))
    top_id = int(find_mytr[0].find('td').get_text(strip=True))

    for t in find_mytr:
        #print(t.find('wr_id').get_text(strip=True))
        current_id = int(t.find('td').get_text(strip=True))
        category = t.find('td',attrs={'class':'post_category'}).get_text(strip=True)
        item = t.find('td',attrs={'class':'post_subject'}).get_text(strip=True).encode('cp949','ignore').decode('cp949')
        print(item)

#        print(current_id, base_id, category, your_search, item)
        if current_id > base_id and category == "[판매]":
            for your_search in SEARCH_KEYWORDS:
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

    time.sleep(30)
