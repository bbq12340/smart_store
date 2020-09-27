import pandas as pd
import tkinter as tk
import os, time
from tqdm import trange

from SmartStoreReviewScraper import SmartStoreReviewScraper


class Reader:
    def __init__(self, stop_thread, filename, limit=None, delay_time=0):
        self.stop_thread = stop_thread
        self.filename = filename
        self.limit = limit
        self.delay_time = delay_time
        self.target_variable = ['평점', '아이디', '시간', '구매옵션', '리뷰내용']
        self.read_input_file()
        self.extract_file()

    def read_input_file(self):
        request_df = pd.read_csv(self.filename, names=['names', 'link'], sep='*')
        request_df = request_df.set_index('names')
        request_df.index = request_df.index + request_df.groupby(level=0).cumcount().astype(str).replace('0','')
        request_df.to_csv('output/wd.csv', encoding='utf-8', header=False)

    def extract_file(self):
        df = pd.read_csv('output/wd.csv', encoding='utf-8', names=['names', 'link'])
        for i in range(len(df.index)):
            if self.stop_thread.is_set():
                print("program forced to stop!\n")      
                break
            else:
                file_name = list(df['names'])[i]
                store_link = list(df['link'])[i]

                print(f"###################{file_name} 수집 시작###################")

                app = SmartStoreReviewScraper()
                REVIEWS = app.scraped_reviews

                store_data = app.get_store_data(store_link) #스토어 정보 
                json_review = app.get_review_json(store_data['merchant_no'], store_data['product_no'], 1) #리뷰 정보 리퀘스트 
                
                review_data = app.get_review_data(json_review) #해당 아이템 리뷰 (총 아이템수 + 총 페이지수) 정보 
                total_element = review_data['totalElements'] #총 아이템수
                total_pages = review_data['totalPages'] #총 페이지수
                print(f'총 아이템 수: {total_element}\n총 페이지 수: {total_pages}')

                review_content = app.get_review_content(json_review) #목표 데이터
                app.scrape_review_contents(REVIEWS, review_content) #첫 페이지 크롤링

                if self.limit >= total_element or self.limit == 0:
                    self.start_scraper(app, REVIEWS, total_element, total_pages, store_data, file_name)
                else:
                    self.start_scraper(app, REVIEWS, self.limit, total_pages, store_data, file_name)   
        return
                    
                

    def start_scraper(self, app, REVIEWS, LIMIT, PAGES, store_data, file_name):
        print('목표 데이터 양:'+str(LIMIT)) 

        DF = pd.DataFrame([], columns=self.target_variable)

        while len(REVIEWS) < LIMIT:
            for page in trange(2, PAGES+1, desc="크롤링 진행도"): 
                #첫 페이지는 이미 크롤링 완료하였으니 두번째 페이지부터 시작
                json = app.get_review_json(store_data['merchant_no'], store_data['product_no'], page)
                content = app.get_review_content(json)
                app.scrape_review_contents(REVIEWS, content)
                time.sleep(self.delay_time) 
                if len(REVIEWS) >= LIMIT:
                    break

        for i in trange(len(REVIEWS), desc='데이터 변환 중'):
            row = pd.DataFrame([REVIEWS[i]], columns=self.target_variable)
            DF = DF.append(row, ignore_index=True)

        DF.insert(0, column='번호', value=DF.index+1)
        print("<데이터 프레임 샘플>")
        print(DF.head())
        print('데이터 수집 완료! 크롤링된 아이템 수:'+str(len(DF))+'\n')
        DF.to_csv(f'output/data/{file_name}.csv', encoding='utf-8-sig', index=False)