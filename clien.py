from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import time
import telepot

# download pip
# wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
#  python -m pip install BeautifulSoup4
# python3 -m pip install telepot

bot = telepot.Bot('your bot key')

my_chat_id = 'your chat id'
startMsg="Clien Monitor 서비스가 시작되었습니다."

bot.sendMessage(my_chat_id, startMsg)

# 장터
base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=sold"
# 모두의 공원
#base_url = "http://www.clien.net/cs2/bbs/board.php?bo_table=park"

url_request = Request(base_url,headers={'User-Agent': 'Mozilla/5.0'})


clien_tip_board = urlopen(url_request).read()

bs4_clien = BeautifulSoup(clien_tip_board,"html.parser")
find_mytr = bs4_clien.find_all("tr",attrs={'class':"mytr"})

base_id = int(find_mytr[0].find('td').get_text(strip=True))

your_searchs = ["맥북", "레티나"]

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
            for your_search in your_searchs:
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

    time.sleep(60)
