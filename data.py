from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import pandas as pd
import os

from scraper import Scraper

class Reader:
    def __init__(self, filename, limit=None, delay_pages=0, delay_time=0):
        self.filename = filename
        self.limit = limit
        self.delay_pages = delay_pages
        self.delay_time = delay_time
        self.read_file()
        self.browser = self.open_browser()
        self.extract_file()
        self.browser.quit()

    def read_file(self):
        request_df = pd.read_csv(self.filename, names=['names', 'link'], sep='*')
        request_df = request_df.set_index('names')
        request_df.index = request_df.index + request_df.groupby(level=0).cumcount().astype(str).replace('0','')
        request_df.to_csv('src/output/wd.csv', encoding='utf-8', header=False)
        
    def open_browser(self):
        browser = webdriver.Chrome(ChromeDriverManager().install())
        return browser

    def extract_file(self):
        df = pd.read_csv('src/output/wd.csv', encoding='utf-8', names=['names', 'link'])
        for i in range(len(df.index)):
            Scraper(self.browser, list(df['names'])[i], list(df['link'])[i], self.limit, self.delay_pages, self.delay_time)
            output_filename = list(df['names'])[i]
            result = pd.read_csv(f'src/output/data/{output_filename}.csv')
            num = result.index+1
            result.insert(0,column='번호',value=num)
            result.to_csv(f'src/output/data/{output_filename}.csv', encoding='utf-8-sig', index=False)
            os.remove(f'src/input/data/{output_filename}.csv')
