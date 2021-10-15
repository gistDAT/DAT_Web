from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from selenium import webdriver
import time
# Create your views here.
from homeapp.models import places,kywords
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
def home_view(request):

    if request.method == "POST":
        temp = request.POST.get('place_input')

        new_place = places()
        new_place.text = temp
        new_place.save()

        # 크롬 웹브라우저 실행
        # 크롬 버전 94.0.4606.61

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        driver = webdriver.Chrome("homeapp/chromedriver.exe", chrome_options=options)
        url_list = []
        content_list = ""

        search = temp

        for i in range(1, 3):  # 1~2페이지까지의 블로그 내용을 읽어옴
            url = 'https://section.blog.naver.com/Search/Post.nhn?pageNo=' + str(
                i) + '&rangeType=ALL&orderBy=sim&keyword=' + search
            driver.get(url)
            time.sleep(0.5)
            print(url)
            for j in range(1, 6):  # 각 블로그 주소 저장
                titles = driver.find_element_by_xpath(
                    '/html/body/ui-view/div/main/div/div/section/div[2]/div[' + str(j) + ']/div/div[1]/div[1]/a[1]')
                title = titles.get_attribute('href')
                url_list.append(title)
                print(title)
        print("url 수집 끝, 해당 url 데이터 크롤링")
        for url in url_list:  # 수집한 url 만큼 반복
            driver.get(url)  # 해당 url로 이동

            driver.switch_to.frame('mainFrame')
            overlays = ".se-component.se-text.se-l-default"  # 내용 크롤링
            contents = driver.find_elements_by_css_selector(overlays)

            for content in contents:
                content_list = content_list + content.text  # content_list 라는 값에 + 하면서 점점 누적
        driver.quit()
        new_keyword = kywords()
        new_keyword.test_set = content_list
        new_keyword.save()

        # 모델링 C:\Users\Park JuHwan\PycharmProjects\DAT\homeapp\views.py
        orig_stdout = sys.stdout
        f_name = 'C://Users//Park JuHwan//PycharmProjects//DAT//blog2.txt'  # 연관분석시 필요한 txt
        f = open(f_name, 'a', encoding='UTF-8')
        sys.stdout = f

        sys.stdout = orig_stdout
        f.close

        from pykospacing import Spacing
        spacing = Spacing()
        content_list = spacing(content_list)

        orig_stdout = sys.stdout
        f_name = 'C://Users//Park JuHwan//PycharmProjects//DAT//blog.txt'  # 상위 단어 20개 추출시 필요한 txt
        f = open(f_name, 'a', encoding='UTF-8')
        sys.stdout = f
        print(content_list)
        sys.stdout = orig_stdout
        f.close

        from konlpy.tag import Okt

        f = open('blog.txt', 'r', encoding='UTF-8')  # 파일 열기
        text = f.readlines()
        content = text[0]

        # from nltk.tokenize import word_tokenize
        def keyword_extractor(tagger, text, word_list):
            text = tagger.normalize(text)

            tokens = tagger.nouns(text)

            tokens = [item for item in tokens if item not in word_list]

            tokens = [token for token in tokens if len(token) > 1]  # 한 글자인 단어는 제외
            # 불용어 삭제
            f = open('homeapp/한국어불용어100.txt', 'r', encoding='UTF-8')  # 전처리를 위한 불용어 사전
            ko_f = f.readlines()
            ko_f = [word.strip('\n') for word in ko_f]

            stop_words = ko_f
            tokens = [word for word in tokens if not word in stop_words]

            count_dict = [(token, text.count(token)) for token in tokens]

            ranked_words = sorted(set(count_dict), key=lambda x: x[1], reverse=True)[:20]
            return [keyword for keyword, freq in ranked_words]

        search_list = search.split()
        search_list.append(search)
        # if __name__ == '__main__':
        twit = Okt()

        word = keyword_extractor(twit, content, search_list)

        # 1. word2Vec
        from gensim.models.word2vec import Word2Vec
        from konlpy.tag import Okt
        okt = Okt()

        f = open('blog2.txt', 'r', encoding='UTF-8')
        lines = f.readlines()
        dataset = []
        for i in range(len(lines)):
            dataset.append(okt.nouns(lines[i]))
        dataset = [[y for y in x if not len(y) == 1] for x in dataset]

        con_dataset = []
        for element in dataset:
            con_dataset += element

        word_list = [W for W in word if W in con_dataset]
        # import pandas as pd
        model = Word2Vec(dataset, sg=1, window=5, min_count=1)
        model.init_sims(replace=True)
        list_A = []
        for W in word_list:
            for w in word_list:
                if W != w:
                    list_A.append(model.wv.similarity(W, w))
        list_A = sorted(set(list_A), reverse=True)
        real_Keyword = []
        for A in list_A[:2]:
            for W in word_list:
                for w in word_list:
                    if W != w:
                        if model.wv.similarity(W, w) == A:
                            real_Keyword.append(W)
                            real_Keyword.append(w)
        real_Keyword = set(real_Keyword)
        print(real_Keyword)  ## 찐 키워드 검색할 단어
        # output

        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        real_Keyword = list(real_Keyword)
        Q = real_Keyword[0] + ',' + real_Keyword[1] + ',' + real_Keyword[2] + ',' + 'playlist'
        DEVELOPER_KEY = "AIzaSyD4joaYpY6VGQZ1-klJel3pk5ppeAQ8K9w"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        search_response = youtube.search().list(
            q=Q,
            part="snippet",

            maxResults=30,

        ).execute()

        ID_list = []
        print(search_response['items'][0]['id'])
        for search_result in search_response.get("items", []):
            ID_list.append(search_result["id"]["videoId"])
        print(ID_list[0])
        path = "homeapp/chromedriver.exe"
        driver = webdriver.Chrome(path)
        url = 'https://www.youtube.com/watch?v=' + ID_list[0]
        driver.get(url)
        return render(request,'homeapp/home_view.html', context={},)
    else:
        return render(request,'homeapp/home_view.html', context={'text': '장소 입력 후 잠시만 기다려주세요!'})
