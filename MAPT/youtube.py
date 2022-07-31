from typing import final
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime

def youtube_search(keyword):
    SEARCH_KEYWORD = keyword.replace(' ', '+')

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    # path는 이용자의 브라우저 드라이버가 설치된 경로
    path = 'MAPT/chromedriver'
    
    driver = webdriver.Chrome(path, options=options)
    
    # 위의 코드에서 driver 오류 뜬다면 아래의 코드로 수정
    #from selenium.webdriver.chrome.service import Service
    #service = Service(ChromeDriverManager().install())
    #driver = webdriver.Chrome(service=service, options=options)

    URL = "https://www.youtube.com/results?search_query=" + SEARCH_KEYWORD
    driver.get(URL)
    time.sleep(1)

    html0 = driver.page_source
    html = BeautifulSoup(html0, 'html.parser')
    df_title = []
    df_link = []
    df_thumbnail = []

    title_list = html.select('a#video-title') # 영상 제목
    link_list = html.select('a#video-title') # 영상 링크
    thumbnail_list = html.select('a#thumbnail>yt-img-shadow>img') # 영상 썸네일

    for i in range(3):
        title = title_list[i].text.strip() 
        link = '{}{}'.format('https://www.youtube.com',link_list[i].get('href')) 
        df_title.append(title)
        df_link.append(link)

    for i in range(4):    
        thumbnail = thumbnail_list[i].get('src') 
        df_thumbnail.append(thumbnail)

    del df_thumbnail[0]
    
    final_list = [df_title, df_link, df_thumbnail]
    driver.close()
    
    return final_list
