from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
import os

def driver_maker(link_number):
    link_number = link_number
    driver = webdriver.Chrome('./driver/chromedriver.exe')
    driver.implicitly_wait(3)
    url = 'https://wahis.oie.int/#/report-info?reportId={}'.format(str(link_number))
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "summary-bottom-detail")))
    element =driver.find_element_by_xpath("//*[@class='expand-all']")
    driver.execute_script('arguments[0].click();', element)
    time.sleep(1)
    driver.find_elements_by_class_name("reporter-summary-data-key")  # 테이블 태그를 모두 추출하기 위한 driver 탐색 구문
    time.sleep(1)
    result = driver.page_source
    soup = BeautifulSoup(result,'html.parser')
    number = len(soup.find_all("div", {"class": "summary-top"})) - 5
    report_type = soup.select_one('.report-number-section > div.report-number')
    report_id = soup.select_one('.reporter-summary-wrap > div > div:nth-child(2) > div:nth-child(1) > div.reporter-summary-data-val>span')
    country = soup.select_one('.report-number-section > div.report-desc')
    serotype = soup.select_one('.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(1) > span.detail')
    causal_agent = soup.select_one('.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(2) > p:nth-child(4) > span:nth-child(2)')
    report_date =  soup.select_one('.stepSummary-container > div:nth-child(2) > div > div.summary-bottom.active > div > div:nth-child(3) > p:nth-child(3) > span.detail')
    t = len(driver.find_elements_by_class_name("step-title"))
    # 세부 발생정보에 관한 데이터 모음
    specific_list = []
    for i in range(1,number):
        specific_dict = {}
        driver.find_elements_by_class_name("stepSummary-container > div:nth-child("+str(t)+") > div > div.outbreak-wrapper > div:nth-child(" + str(i) + ") > div.bottom-detail-container > div:nth-child(1) > div")  # refresh해서 세부사항이 담긴 class를 소환
        outbreak_date111 = soup.select('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div>div:nth-child(1)')
        outbreak_date = soup.select_one('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(2) > span.detail')
        epidimiological_unit = soup.select_one('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(1) > p:nth-child(3) > span.detail')
        first_div  = soup.select_one('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(1) > span.detail')
        second_div = soup.select_one('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(2) > span.detail')
        third_div = soup.select_one('.stepSummary-container > div:nth-child('+str(t)+') > div > div.outbreak-wrapper > div:nth-child('+str(i)+') > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(3) > span.detail')
        driver.find_elements_by_class_name("stepSummary-container > div:nth-child("+str(t)+") > div > div.outbreak-wrapper > div:nth-child(" + str(i) + ") > div.bottom-detail-container > div:nth-child(1) > div")  # refresh해서 세부사항이 담긴 class를 소환
        specific_dict['Date of start of the outbreak'] = outbreak_date.text
        specific_dict['Region'] = '{},{},{}'.format(third_div.text,second_div.text,first_div.text)
        specific_dict['Epidemiological unit'] = epidimiological_unit.text
        specific_df = pd.Series(specific_dict)
        specific_list.append(specific_df)


    total_dict = {}
    total_dict['Link number'] = link_number

    # 전체 질병명에서 질병명과 국가명을 분리 (split함)
    total_dict['Disease'] = country.text.split(',')[0]
    total_dict['Country'] = country.text.split(',')[1]
    total_dict['Serotype'] = serotype.text
    total_dict['Report date'] = report_date.text
    total_dict['Number of outbreaks'] = ""

    Total_df = pd.DataFrame(total_dict,index=[0])
    if len(specific_list) ==1:
        specific_total = pd.Series(specific_list)
    else:
        specific_total = pd.concat(specific_list,axis=1)
    specific_total_df = specific_total.T
    sub_total = pd.concat([Total_df,specific_total_df],axis=1)
    sub_total = sub_total.fillna(method='ffill')

    return sub_total

a = driver_maker(30463)
