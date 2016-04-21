# home_util

# install mysql
sudo apt-get install mysql-server-5.6
* add some configuration for mysql to enable Korean characters
refer my.cnf

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;
flush privileges;

# install python module
sudo apt-get install python3-pip
sudo apt-get install libmysqlclient-dev
sudo pip3 install mysqlclient telepot BeautifulSoup4 feedparser xmltodict

