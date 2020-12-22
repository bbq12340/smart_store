
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time, re

# BTN_XPATH = '//*[@id="footer"]/div[2]/div/div[3]/button'
# BY_BTN_XPATH = By.XPATH, BTN_XPATH

# BTN_XPATH2 = '//*[@id="footer"]/div[2]/div[1]/div[4]/button'

class_name = By.CLASS_NAME, "undefinedinfo"
class_name2 = "_3oMcQ3LMwm"

class BusinessScraper():
    def __init__(self, links):
        self.links = list(dict.fromkeys(links))
        self.options = self.headless_browser()
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
        self.wait = WebDriverWait(self.browser, 30)

    def headless_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        return options
    
    def extract_all(self):
        DATA = []
        for l in self.links:
            DATA.append(self.scrape_document(l))

        self.browser.quit()
        df = pd.DataFrame(data=DATA)
        return df

    def scrape_document(self, link):
        print(link)
        try:
            self.browser.get(link)
            # self.wait.until(EC.element_to_be_clickable(class_name))
            time.sleep(1)
            # btn = self.browser.find_element_by_class_name("undefinedinfo")
            # btn.click()
            btn = self.browser.find_elements_by_class_name("_3oMcQ3LMwm")[-1]
            btn.click()
            html = self.browser.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser').find('div',{'class':'_134kp266qc'})

            company = soup.find('span',string="상호명").next_sibling.text
            address = soup.find('span',string="사업장 소재지").next_sibling.text
            phone = soup.find('span',string="고객센터").next_sibling.text.replace('인증','')
            if "010" in phone:
                ind_phone = phone
                comp_phone = None
            else:
                ind_phone = None
                comp_phone = phone
        

            data = {
                '대표자명': soup.find('span', string="대표자").next_sibling.text,
                '회사전화': comp_phone,
                '휴대폰': ind_phone,
                '업체명': company,
                '지역': address.split("(우 : ")[0].split(" ")[0],
                '주소': (" ").join(address.split("(우 : ")[0].split(" ")[1:]),
                '우편번호': address.split("(우 : ")[1].replace(")",""),
                'src': link
            }
        except:
            data = {
            '대표자명': None,
            '회사전화': None,
            '휴대폰': None,
            '업체명': None,
            '지역': None,
            '주소': None,
            '우편번호': None,
            'src': link
            }
        df = pd.DataFrame([data])
        return df