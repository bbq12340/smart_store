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
    UnexpectedAlertPresentException,
    ElementNotInteractableException
    )
from bs4 import BeautifulSoup
import pandas as pd
import dask.dataframe as dd
import csv, time, os

class Scraper:
    def __init__(self, browser, name, url, limit=None, delay_pages=0, delay_time=0):
        self.name = name
        print(f"{self.name} ------ 수집 시작합니다.")
        self.url = url
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 15)
        self.limit = limit
        self.delay_pages = delay_pages
        self.delay_time = delay_time
        self.extract()

    def extract(self):
        self.browser.get(self.url)
        self.extract_cols = ['평점', '구매자아이디', '구매날짜', '구매한옵션', '리뷰내용']
        temp_df = pd.DataFrame([], columns=self.extract_cols)
        temp_df.to_csv(f"src/input/data/{self.name}.csv", index=False)
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
                f.write(f"{self.url}---사이트 에러\n")
            os.remove(f"input/data/{self.name}.csv")
            return
        try:
            review_count = self.browser.find_element_by_class_name('q9fRhG-eTG').get_attribute('innerText').replace(',','')
        except NoSuchElementException:
            review_count = self.browser.find_element_by_class_name('_3HJHJjSrNK').get_attribute('innerText').replace(',','')
        review_count = int(review_count)

        if self.limit == None:
            dask_df = self.review_scrape(review_count)

        elif self.limit >= review_count:
            dask_df = self.review_scrape(review_count)

        else:
            dask_df = self.review_scrape(self.limit)

        dask_df = dask_df.compute()
        dask_df.to_csv(f'src/output/data/{self.name}.csv', encoding='utf-8-sig', index=False)
            
    def review_scrape(self, limit):
        print('******목표 수집 수량:'+str(limit))
        index = 0
        while limit > index:
            page_df = pd.DataFrame([], columns=self.extract_cols)
            current_page_df = self.extract_info(page_df)
            current_btn_xpath = '//a[contains(@class,\"UWN4IvaQza\") and contains(@aria-current,\"true\")]'
            next_btn_xpath = current_btn_xpath + '/following-sibling::a'
            next_btn = self.browser.find_element_by_xpath(next_btn_xpath)
            try:
                next_btn.click()
                time.sleep(0.1)
                #delay-by-pages
                if self.delay_pages != 0:
                    try:
                        current_btn = self.browser.find_element_by_xpath(current_btn_xpath)
                        current_btn_num = int(current_btn.get_attribute('innerText'))
                        temp = current_btn_num
                    except StaleElementReferenceException:
                        current_btn_num = temp + 1
                    if current_btn_num % self.delay_pages == 0:
                        time.sleep(self.delay_time)
            except ElementNotInteractableException:
                current_page_df.to_csv(f"src/input/data/{self.name}.csv", mode='a', header=False, index=False)
                index = index + len(current_page_df)
                print("페이지끝!\n수집량: "+str(index))
                dask_df = dd.read_csv(f"src/input/data/{self.name}.csv")
                return dask_df
            next_page_df = self.extract_info(page_df)
            if current_page_df.equals(next_page_df) == True:
                temp_df = self.extract_info(page_df)
                if next_page_df.equals(temp_df) == True:
                    temp_df.to_csv(f"src/input/data/{self.name}.csv", mode='a', header=False, index=False)
                    index = index + len(temp_df)
                    print('#수집불량. 재수집합니다. 현수집량: '+str(index))
                    continue
                else:
                    print('#페이지가 중복 수집되었습니다. 재수집합니다. 현수집량: '+str(index))
                    next_page_df = temp_df
            index = index + len(current_page_df)
            current_page_df.to_csv(f"src/input/data/{self.name}.csv", mode='a', header=False, index=False)
            if index >= limit:
                print("목표수집수량 달성! 수집량:" +str(index))
                dask_df = dd.read_csv(f"src/input/data/{self.name}.csv")
                return dask_df

    def extract_info(self, page_df):
        html_1 = self.browser.execute_script('return document.body.outerHTML;')
        soup_1 = BeautifulSoup(html_1, 'html.parser')
        container = soup_1.select('._1YShY6EQ56')
        for parts in container:
            rate = parts.find('em', {'class': '_15NU42F3kT'}).text
            info = parts.select('._3QDEeS6NLn')
            if len(info) == 4:
                option = info[2].text.replace(',','')
            else:
                option = "None"
            username = info[0].text
            date = info[1].text
            description = info[-1].text.replace(',',' ').replace('~',' ').replace('\n',' ')
            row = [rate, username, date, option, description]
            row_df = pd.DataFrame([row], columns=self.extract_cols)
            page_df = page_df.append(row_df, ignore_index=True)
        #page_df.to_csv(f"src/input/data/{self.name}.csv", mode='a', header=False, index=False)
        return page_df

