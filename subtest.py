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
    driver = webdriver.Chrome('./webdriver/chromedriver.exe')
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
    driver.find_elements_by_class_name("stepSummary-container")  # refresh해서 발생조치가 담긴 class를 소환
    driver.find_elements_by_class_name("stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(1) > div.bottom-detail-container > div:nth-child(1) > div") # refresh해서 세부사항이 담긴 class를 소환
    first  = soup.select_one('.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(1) > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(1) > span.detail')
    second = soup.select_one('.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(1) > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(2) > span.detail')
    third = soup.select_one('.stepSummary-container > div:nth-child(7) > div > div.outbreak-wrapper > div:nth-child(1) > div.bottom-detail-container > div:nth-child(1) > div > div:nth-child(3) > p:nth-child(3) > span.detail')
    return result, first, second, third


a,b,c,d = driver_maker(30500)

