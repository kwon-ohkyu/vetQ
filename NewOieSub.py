from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
import os

os.getcwd()

class OieSubPage:
    def __init__(self):
        self.result = []
        self.result_concate = []
        self.driver = None
        self.specific_outbreak = None

    def driver_maker(self,link_number):
        '''
        크롬 웹드라이버 생성 및 페이지 창 열기 작업용 함수
        '''
        self.driver = webdriver.Chrome('./webdriver/chromedriver.exe')
        self.driver.implicitly_wait(3)
        url = 'https://wahis.oie.int/#/report-info?reportId={}'.format(str(link_number))
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "summary-bottom-detail")))
        element = self.driver.find_element_by_xpath("//*[@class='expand-all']")
        self.driver.execute_script('arguments[0].click();',element)
        time.sleep(1)


    def table_data(self,result):
        self.driver.find_elements_by_class_name("species-name") # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
        time.sleep(1)
        self.result = self.driver.page_source
        # 세부 테이블 정보만 불러오는 함수
        result = self.result
        try:
            self.df = pd.read_html(result, flavor='lxml')[2:]
        except:
            print('발생건이 없습니다')

        for i, j in enumerate(self.df):
            a = self.df[i]
            b = a[(a['SPECIES'] != '-') & (a['Unnamed: 1'] == 'NEW') & (a['CASES'] != '-')]
            self.result_concate.append(b)
        self.specific_outbreak = pd.concat(self.result_concate)
        return self.specific_outbreak

    def specific_data(self,result):
        self.driver.find_elements_by_class_name("reporter-summary-data-key") # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
        time.sleep(1)
        self.result = self.driver.page_source
        # 세부 테이블 정보만 불러오는 함수
        result = self.result
        try:
            self.df = pd.read_html(result, flavor='lxml')[2:]
        except:
            print('발생건이 없습니다')

        for i, j in enumerate(self.df):
            a = self.df[i]
            b = a[(a['SPECIES'] != '-') & (a['Unnamed: 1'] == 'NEW') & (a['CASES'] != '-')]
            self.result_concate.append(b)
        self.specific_outbreak = pd.concat(self.result_concate)
        return self.specific_outbreak

    def driver_quit(self):
        self.driver.quit()


a = OieSubPage()
b = a.driver_maker(30500)
c = a.table_data(b)

