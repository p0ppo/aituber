import urllib.robotparser
import urllib.request
 
# urllibにデフォルトと異なるユーザーエージェントを使う
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', UA)]
urllib.request.install_opener(opener)
 
# robots.txtをrobotparserで読み込み許可されているか確認
url_base = "https://ffxiv.consolegameswiki.com"
main_scenario = "wiki/Main_Scenario_Quests"


import requests
from bs4 import BeautifulSoup
import os

res_list = [["quest", "journal"]]
def get_quest_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for item in soup.find_all("table", class_="pve table"):
        #print(item)
        thead = item.find('tbody')  # theadタグを探す  
        #print(thead)
        for i in thead.find_all("tr"):
            if i.find("a") is not None:
                print("---------------")
                wiki = i.find("a").get("href")
                print(os.path.basename(wiki))
                journal = get_journal(url_base + i.find("a").get("href"))
                #dialogue = get_dialogue(url_base + i.find("a").get("href"))
                print("---------------")
                res_list.append([wiki, journal])
        print(res_list)
        import pdb; pdb.set_trace()

import re

def get_journal(url):
    start_s = '<span class="mw-headline" id="Journal">Journal</span></h2>\n'
    end_s = '<h2><span class="mw-headline" id="Dialogue">'
    response = requests.get(url)
    html = response.content.decode("utf-8")
    text = html.split(start_s)[1].split(end_s)[0]
    text_re = re.sub(re.compile('<.*?>'), '', text)
    return text_re


def get_dialogue(url):
    start_s = '<h2><span class="mw-headline" id="Dialogue">Dialogue</span></h2>\n'
    end_s = '</pre>\n<h3><span class="mw-headline" id="Conjurer">Conjurer</span></h3>'
    response = requests.get(url)
    html = response.content.decode("utf-8")
    text = html.split(start_s)[1].split(end_s)[0]
    text_re = re.sub(re.compile('<.*?>'), '', text)
    return text_re

get_quest_links(url_base + "/" + main_scenario)