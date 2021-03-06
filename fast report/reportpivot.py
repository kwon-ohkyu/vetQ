import pandas as pd
import os

table=pd.read_excel(r"C:\Users\kwonok59\Desktop\python project\fast report\oie_reports_200916(논리적용).xlsx",sheet_name="번역본")


first_list=['리포트 번호','혈청형','발생일','발생 지역','국내이동제한','발생대응 예방접종', '봉쇄지역 및/또는 보호지역 외 예찰',
          '봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝','이력 추적', '격리', '동물성 생산물 공식처리', '사체·부산물·폐기물 공식처리',
          '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분', '야생보균원 관리', '방역대 설정','소독',
          '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사', '백신접종 허용(백신이 있는 경우)','백신접종 금지',
          '감염동물 미치료', '감염동물 치료', '도축*']

last_list=['보고일','발생일']
sum_list=['구분','건수','사육', '감염', '폐사', '살처분']


def first_groupby():
    total_first_list = []
    for x in first_list:
        total=table.groupby(['질병','국가','축종'])[x].first()
        if total.name=='발생일':
            total.name='시작일'
        else: pass
        total_first_list.append(total)
    return total_first_list

def last_groupby():
    total_last_list = []
    for x in last_list:
        total=table.groupby(['질병','국가','축종'])[x].last()
        if total.name=='발생일':
            total.name='종료일'
        else: pass
        total_last_list.append(total)
    return total_last_list

def sum_groupby():
    total_sum_list = []
    for x in sum_list:
        if x == '구분':
            total = table.groupby(['질병', '국가','축종'])[x].apply(lambda x: "%s"%','.join(x))

        else:
            total = table.groupby(['질병', '국가','축종'])[x].sum()
        total_sum_list.append(total)
    return total_sum_list

def immediate_followup(x):
    if type(x) == str:
        return "긴급"
    else:
        return "추가"

def wild_livestock(x):
    if '사육'in x and '야생' in x:
        return "사육,야생"
    elif '사육' in x and '야생' not in x :
        return "사육"
    else:
        return "야생"

total_list = first_groupby()+last_groupby()+sum_groupby()
total_df =pd.concat([i for i in total_list],axis=1)
total_data=total_df.copy()


total_data = total_data[['리포트 번호','구분','보고일','시작일','발생 지역','종료일','혈청형', '건수', '사육', '감염', '폐사', '살처분', '국내이동제한', '발생대응 예방접종',
                     '봉쇄지역 및/또는 보호지역 외 예찰','봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리',
                     '사체·부산물·폐기물 공식처리', '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분',
                     '야생보균원 관리', '방역대 설정', '소독', '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사',
                     '백신접종 허용(백신이 있는 경우)', '백신접종 금지', '감염동물 미치료', '감염동물 치료', '도축*']]

total_data['리포트 번호']=total_data['리포트 번호'].apply(immediate_followup)
total_data['구분']=total_data['구분'].apply(wild_livestock)
total_data[['시작일','보고일','종료일']]=total_data[['시작일','보고일','종료일']].applymap(lambda x:str(x))

i=0
while i<len(total_data['시작일']):
    if total_data['시작일'][i]!=total_data['종료일'][i]:
        total_data['시작일'][i]=str(total_data['시작일'][i])+'~'+str(total_data['종료일'][i])
    else:pass
    i+=1

del total_data['종료일']

desktop_path = f'C:\\Users\\{os.getlogin()}\\Desktop\\'

with pd.ExcelWriter(desktop_path + '엑셀보고서.xlsx') as writer:
    total_data.to_excel(writer, sheet_name='엑셀보고서', index=True)
