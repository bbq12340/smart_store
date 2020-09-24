import requests, bs4
from bs4 import BeautifulSoup
import json, re

class SmartStoreReviewScraper:

    def __init__(self, link):
        self.user_agent = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.API_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews'
        self.scraped_reviews = []
        self.store_data = self.get_store_data(link) #스토어 정보 --- 스토어 번호, 물품 번호
        self.json_review = self.get_review_json(store_data['merchant_no'], store_data['product_no'], 1) #리뷰페이지 정보
        self.total_pages = self.get_review_data(json_review)['totalPages'] #총 페이지
        self.total_elements = self.get_review_data(json_review)['totalElements'] #총 아이템




    def get_store_data(self, link):
        r = requests.get(link, headers=self.user_agent)
        soup = BeautifulSoup(r.text,'html.parser').find('body').find('script').string[27:]
        json_dict=json.loads(str(soup))
        merchant_no = json_dict['smartStore']['channel']['payReferenceKey']
        product_no = json_dict['product']['A']['productNo']
        data = {
            'merchant_no': merchant_no,
            'product_no': product_no
        }
        return data
    
    def get_review_json(self, merchant_no, product_no, page):
        payload = {
            'page': page,
            'pageSize': '20',
            'merchantNo': merchant_no,
            'originProductNo': product_no,
            'sortType': 'REVIEW_RANKING'
        }
        r = requests.get(self.API_url, params=payload, headers=self.user_agent)
        json = r.json(encoding='utf-8')
        return json
    
    def get_review_content(self, review):
        content = review['contents']
        return content
    
    def get_review_data(self, review):
        total_pages = review['totalPages']
        total_elements = review['totalElements']
        data = {
            'totalPages': total_pages,
            'totalElements': total_elements
        }
        return data

    
    