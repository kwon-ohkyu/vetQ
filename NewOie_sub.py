from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
import os


class OieSubPage:
    def __init__(self):
        self.result = []
        self.result_concate = []
        self.driver = webdriver.Chrome('./driver/chromedriver.exe')
        self.driver.implicitly_wait(3)
        self.total_dict = {}
        self.specific_total_df = None
        self.specific_outbreak = None
        self.link_number = ""
        self.sub_total = None

    def driver_maker(self,link_number):
        self.link_number = link_number
        '''
        크롬 웹드라이버 생성 및 페이지 창 열기 작업용 함수
        '''
        url = 'https://wahis.oie.int/#/report-info?reportId={}'.format(str(self.link_number))
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
            a_list=a.columns
            if a_list[0]!='SPECIES':
                pass
            else:
                b = a[(a['SPECIES'] != '-') & (a['Unnamed: 1'] == 'NEW')]
                self.result_concate.append(b)
        self.specific_outbreak = pd.concat(self.result_concate)
        self.specific_outbreak.reset_index(inplace=True)

        self.driver.find_elements_by_class_name("reporter-summary-data-key")  # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
        time.sleep(1)

        result = self.driver.page_source
        soup = BeautifulSoup(result, 'html.parser')
        number = len(soup.find_all("div", {"class": "summary-top"})) - 5
        report_type = soup.select_one('.report-number-section > div.report-number')
        report_id = soup.select_one(
            '.reporter-summary-wrap > div > div:nth-child(2) > div:nth-child(1) > div.reporter-summary-data-val>span')
        country = soup.select_one('.report-number-section > div.report-desc')
        serotype = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(1) > span.detail')
        causal_agent = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(4) > span:nth-child(2)')
        report_date = soup.select_one(
            '.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(3) > p:nth-child(3) > span.detail')
        t = len(self.driver.find_elements_by_class_name("step-title"))
        # 세부 발생정보에 관한 데이터 모음
        specific_list = []
        for i in range(1, number):
            self.driver.find_elements_by_class_name(
                "stepSummary-container > div:nth-child({}}) > div > div.outbreak-wrapper > div:nth-child(" + str(
                    i) + ") > div.bottom-detail-container > div:nth-child(1) > div")  # refresh해서 세부사항이 담긴 class를 소환
            specific_dict = {}
            outbreak_date = soup.select_one(
                '.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(' + str(
                    i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(2) > span.detail')
            epidimiological_unit = soup.select_one(
                '.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(' + str(
                    i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(3) > span.detail')
            first_div = soup.select_one(
                '.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(' + str(
                    i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(1) > span.detail')
            second_div = soup.select_one(
                '.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(' + str(
                    i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(2) > span.detail')
            third_div = soup.select_one(
                '.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(' + str(
                    i) + ') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(3) > span.detail')
            specific_dict['Date of start of the outbreak'] = outbreak_date.text
            specific_dict['Region'] = '{},{},{}'.format(third_div.text, second_div.text, first_div.text)
            specific_dict['Epidemiological unit'] = epidimiological_unit.text
            specific_df = pd.Series(specific_dict)
            specific_list.append(specific_df)

        self.total_dict = {}
        self.total_dict['Link number'] = self.link_number

        # 전체 질병명에서 질병명과 국가명을 분리 (split함)
        self.total_dict['Disease'] = country.text.split(',')[0]
        self.total_dict['Country'] = country.text.split(',')[1]
        self.total_dict['Serotype'] = serotype.text
        self.total_dict['Report date'] = report_date.text
        self.total_dict['Number of outbreaks'] = ""

        Total_df = pd.DataFrame(self.total_dict, index=[0])

        specific_total = pd.concat(specific_list, axis=1)
        self.specific_total_df = specific_total.T
        self.sub_total = pd.concat([Total_df, self.specific_total_df], axis=1)
        self.sub_total = self.sub_total.fillna(method='ffill')

        self.page_df = pd.concat([self.sub_total,self.specific_outbreak], axis=1)
        return  self.page_df

    def driver_close(self):
        self.driver.close()

    def driver_quit(self):
        self.driver.quit()

    def _reset_(self):
        self.result = []
        self.result_concate = []
        self.total_dict = {}
        self.specific_total_df = None
        self.specific_outbreak = None
        self.link_number = ""
        self.sub_total = None