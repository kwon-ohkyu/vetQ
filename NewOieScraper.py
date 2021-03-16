
print('로딩 중입니다.\n')

from NewOie_sub import OieSubPage
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import sqlite3
import pandas as pd
import tqdm

os.getcwd()
os.chdir('C:\\Users\\kwono\\Documents\\python project')

def get_oie_data():
    '''각 report의 링크를 목록화'''
    dr = webdriver.Chrome('./driver/chromedriver.exe') # Webdriver에서 네이버 페이지 접속

    try:
        dr.get('https://wahis.oie.int/#/events')
        WebDriverWait(dr, 10).until(lambda x: x.find_element_by_class_name('filled-in childCheck'))
    except: pass
    finally:
        soup = BeautifulSoup(dr.page_source,'html.parser')
        k = str(soup.findAll('label'))
        want_linknumbers=re.findall(r'[0-9]{5}',k)
        print(want_linknumbers)
    dr.quit()
    con = sqlite3.connect('oie_reports.db')

    # 기존 db의 링크번호 가져옴
    # try:
    #     linknumber_db_df = pd.read_sql("SELECT [링크 번호] FROM oie_reports_kr", con)  # []: 칼럼명이나 테이블명에 공백이 있을 때
    #     linknumber_db_df.drop_duplicates(inplace=True)
    #
    #     linknumber_db_series = linknumber_db_df['링크 번호'].astype(str)  # 숫자형식을 문자형식으로 바꿈
    #
    # except: pass

    new_linknumbers = []
    new_error_linknumbers = []
    oie_reports = pd.DataFrame()

    for want_linknumber in want_linknumbers:

        # if not (want_linknumber in list(linknumber_db_series)):
        new_linknumbers.append(want_linknumber)

    '''새로 올라온 리포트의 데이터 추출'''

    print('데이터를 추출하고 있습니다.\n잠시만 기다려주세요.\n')


    for new_linknumber in new_linknumbers:  # tqdm: 반복문에서의 리스트 원소 수를 백분율로 나타내어 진행표시줄을 만듦
        BOT = OieSubPage()

        report_ready = BOT.driver_maker(new_linknumber)

        # 서버 오류로 인해 timeout 에러가 났을 때 회피
        try:
            oie_report = BOT.table_data(report_ready)

        except TimeoutError:
            new_error_linknumbers.append(new_linknumber)
            break

        # 추출한 데이터 및 링크번호 추가
        oie_reports = oie_reports.append(oie_report, ignore_index=True)  # df.append 사용 시 무조건 ignore_index=True!

        BOT._reset_()
        BOT.driver_quit()

    oie_reports.to_excel('hello.xlsx',sheet_name='hello')

    return oie_reports


if __name__ == '__main__':
    get_oie_data()