# -*- coding: utf-8 -*- 
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException, 
    TimeoutException, 
    NoSuchElementException, 
    JavascriptException, 
    UnexpectedAlertPresentException
    )
from bs4 import BeautifulSoup
import pandas as pd
import csv, time, os

class scraper:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        with open(f"output/data/{self.name}.csv", "w") as f:
            f.write("")
        self.browser = self.open_browser()
        self.wait = WebDriverWait(self.browser, 15)
        self.extract()


    def open_browser(self):
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(self.url)
        return browser
    
    def extract(self):
        extract_cols = ['평점', '구매자아이디', '구매날짜', '구매한옵션', '리뷰내용']
        DF = pd.DataFrame([], columns=extract_cols)
        page_df = pd.DataFrame([], columns=extract_cols)
        try:
            review_tab_class = By.CLASS_NAME, '_11xjFby3Le'
            self.wait.until(EC.presence_of_element_located(review_tab_class))
            review_tab = self.browser.find_elements_by_class_name('_11xjFby3Le')[1]
            review_tab.click()
        except (NoSuchElementException, TimeoutException):
            for i in range(0,3):
                self.browser.refresh()
                time.sleep(1)
                try: 
                    review_tab = self.browser.find_elements_by_class_name('_11xjFby3Le')[1]
                    review_tab.click()
                    break
                except NoSuchElementException:
                    try:
                        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        review_tab = self.browser.find_elements_by_class_name('_11xjFby3Le')[1]
                        review_tab.click()
                    except NoSuchElementException:
                        continue
            print("리뷰 탭이 클릭 불가능합니다. 버그 리포트 하겠습니다.")
            with open("output/bug_report.txt", 'a') as f:
                f.write(f"{self.url}\n")
            os.remove(f"output/data/{self.name}.csv")
            return
        review_count = self.browser.find_element_by_class_name('q9fRhG-eTG').get_attribute('innerText').replace(',','')
        review_count = int(review_count)
        while review_count > len(DF.index):
            html_1 = self.browser.execute_script('return document.body.outerHTML;')
            soup_1 = BeautifulSoup(html_1, 'html.parser')

        return
            