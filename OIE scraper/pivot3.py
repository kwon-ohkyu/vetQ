import pandas as pd
import openpyxl
df=pd.read_excel(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\oie_reports_200513(1month).xlsx',sheet_name='번역본')

def fromto():
    a=input('시작일을 입력하세요 예:2020-05-01')
    b=input('종료일을 입력하세요 예:2020-05-31')
    df0=df[(df["보고일"]>=a) & (df["보고일"]<=b)]
    df0=df0.applymap(lambda x:1 if x=="Y"  else x)
    df0=df0.applymap(lambda x:0 if x=="To be" else x)
    return df0

df0=fromto()
df0['혈청형']
df0[['혈청형',"구분","축종"]].fillna('n/a')
dfcol=df0.columns[15:-2]
listcol=dfcol.to_list()

# for i,list in enumerate(listcol):
#     print('df'+str(i+3)+'=df0.groupby(["원인체","국가명"])["'+f'{list}'+'"].sum()')
def makepivot():
    try:
        dft=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["건수"].sum()
        df1=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["발생일"].first()
        df2=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["발생일"].last()
        df3=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["국내이동제한"].sum()
        df4=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["발생대응 예방접종"].sum()
        df5=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["봉쇄지역 및/또는 보호지역 외 예찰"].sum()
        df6=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["봉쇄지역 및/또는 보호지역 내 예찰"].sum()
        df7=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["스크리닝"].sum()
        df8=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["이력 추적"].sum()
        df9=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["격리"].sum()
        df10=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["동물성 생산물 공식처리"].sum()
        df11=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["사체·부산물·폐기물 공식처리"].sum()
        df12=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["생산물 또는 부산물 내 병원체 불활화 처리"].sum()
        df13=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["살처분*"].sum()
        df14=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["선택적 살처분"].sum()
        df15=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["야생보균원 관리"].sum()
        df16=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["방역대 설정"].sum()
        df17=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["소독"].sum()
        df18=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["해충구제"].sum()
        df19=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["야생매개체 관리"].sum()
        df20=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["매개체 예찰"].sum()
        df21=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["생·해체검사"].sum()
        df22=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["백신접종 허용(백신이 있는 경우)"].sum()
        df23=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["백신접종 금지"].sum()
        df24=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["감염동물 미치료"].sum()
        df25=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["감염동물 치료"].sum()
        df26=df0.groupby(["원인체","국가명","혈청형","구분","축종"])["도축*"].sum()
    except:pass
    x=pd.concat([dft,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df18,df19,df20,df21,df22,df23,df24,df25,df26],axis=1,join='outer')
    return x

df_tot=makepivot()
df_tot
# for i in df_tot['격리']:
listcol=dfcol.to_list()
listcol
for i in listcol:
    df_tot.loc[df_tot[i]>0,i]=i

df_tot=df_tot.applymap(lambda x:"" if x==0 else x)
df_tot['Total']=df_tot[['국내이동제한','발생대응 예방접종','봉쇄지역 및/또는 보호지역 외 예찰',
                       '봉쇄지역 및/또는 보호지역 내 예찰','스크리닝','이력 추적','격리','동물성 생산물 공식처리','사체·부산물·폐기물 공식처리',
                       '생산물 또는 부산물 내 병원체 불활화 처리','살처분*','선택적 살처분','야생보균원 관리','방역대 설정','소독','해충구제',
                       '야생매개체 관리','매개체 예찰','생·해체검사','백신접종 허용(백신이 있는 경우)','백신접종 금지','감염동물 미치료','감염동물 치료','도축*']].apply(lambda x:",".join(x),axis=1)

listcol_mod=['건수', '발생시작', '발생종료', '국내이동제한', '발생대응 예방접종', '봉쇄지역 및/또는 보호지역 외 예찰',
           '봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리',
           '사체·부산물·폐기물 공식처리', '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분',
           '야생보균원 관리', '방역대 설정', '소독', '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사',
           '백신접종 허용(백신이 있는 경우)', '백신접종 금지', '감염동물 미치료', '감염동물 치료', '도축*', 'Total']
df_tot.columns=listcol_mod

#
# def diction(x):
#     dic_me={"Birds":"가금","House Crow:Corvus splendens(Corvidae)":"집까마귀"}
#     x=dic_me[f'{x}']
#     return x


df_final=df_tot[['건수','발생시작','발생종료','Total']]
df_final
# try:df0 = df0.applymap(lambda x:diction('x'))
# except:pass

df_final.to_excel(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\final.xlsx')
