import requests
from bs4 import BeautifulSoup
import json


################ 네이버 뉴스 #################
# naver open api keys
client_id = "19W9cffg97TbZB3JwOfA"
client_secret = "xV_ZvtDSHU"
header_param = {
    'X-Naver-Client-Id': client_id, 
    'X-Naver-Client-Secret': client_secret,
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    }
wanted_politician = ['정치', '이재명', '윤석열', '홍준표', '이준석', '문재인', '허경영', '김남국', '한동훈', '조국', '노무현', '전두환', '박정희', '노태우', '이승만', '김대중', '박근혜', '이명박', '원희룡', '추미애', '김기현', '나경원', '권성동', '민형배', '유시민', '김어준', '전원책', '김정은', '푸틴', '시진핑', '바이든', '트럼프']
display = 100
page_start = 10
page_end = 20
def get_naver_news():
    news_list = list()
    aleady_done_title = set()
    for politician in wanted_politician:
        for page in range(page_start, page_end):
            url = f'https://openapi.naver.com/v1/search/news.json?query={politician}&display={display}&start={page}'
            try:
                requests_get = requests.get(url, headers=header_param)
                requests_get_json = requests_get.json()
                for e in requests_get_json['items']:
                    # 네이버 뉴스 기사만 가져옴. 다른 언론사는 요청하면 차단당함.
                    if 'naver' in e['link']:
                        soup = BeautifulSoup(requests.get(e['link']).content, 'html.parser')
                        news_title_tag = soup.find('div', {'class': 'media_end_head_title'}).find('h2', {'id': 'title_area'})
                        news_contents_tag = soup.find('div', {'id': 'newsct_article'})
                        # 제목 태그와 컨텐츠 태그가 전부 존재해야 가능
                        if news_title_tag and news_contents_tag:
                            news_title = news_title_tag.find('span').text.strip() 
                            # 중복된 기사 필터링
                            if news_title in aleady_done_title:
                                continue
                            news = dict()
                            news['title'] = news_title
                            news['contents'] = news_contents_tag.text.strip().replace("\n", "")
                            news['pubDate'] = e['pubDate']
                            aleady_done_title.add(news_title)
                            news_list.append(news)
            except:
                continue
    print('news list size =', len(news_list))
    return news_list
