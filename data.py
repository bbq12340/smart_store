import pandas as pd

from scraper import Scraper

class Reader:
    def __init__(self, limit):
        self.limit = limit
        self.read_file()
        self.extract_file()

    def read_file(self):
        request_df = pd.read_csv('src/input/request.txt', names=['names', 'link'], sep='*')
        request_df = request_df.set_index('names')
        request_df.index = request_df.index + request_df.groupby(level=0).cumcount().astype(str).replace('0','')
        request_df.to_csv('src/output/wd.csv', encoding='utf-8', header=False)

    def extract_file(self):
        df = pd.read_csv('src/output/wd.csv', encoding='utf-8', names=['names', 'link'])
        for i in range(len(df.index)):
            Scraper(list(df['names'])[i], list(df['link'])[i], self.limit)
