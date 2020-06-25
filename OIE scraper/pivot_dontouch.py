import pandas as pd
import openpyxl
import re
df=pd.read_excel(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\oie_reports_200624(full_db).xlsx',sheet_name='번역본')

def fromto():
    a=input('시작일을 입력하세요 예:2020-05-01')
    b=input('종료일을 입력하세요 예:2020-05-31')
    df0=df[(df["보고일"]>=a) & (df["보고일"]<=b)]
    df0=df0.applymap(lambda x:1 if x=="Y"  else x)
    df0=df0.applymap(lambda x:0 if x=="To be" else x)
    df0=df0.applymap(lambda x:diction(x))
    return df0

def diction(x):
    if x in dic_me.keys():
        x=dic_me[x]
    else:x
    return x

def dica():
    a=input("사전으로 만들 단어를 입력하세요")
    b=input("값을 입력하세요")
    dic_me[a]=b
    return dic_me

dic_me={"Birds":"가금",
        "House Crow:Corvus splendens(Corvidae)":"집까마귀",
        'Lion:Panthera leo(Felidae)':'사자',
        'Sheep / goats':'면양/산양',
        'Bees (hives)':'벌',
        'Rabbits':'토끼',
        'Leporidae (unidentified):Leporidae (incognita)(Leporidae)':'토끼목',
        'Cottontail rabbits:Sylvilagus(Leporidae)':'토끼목',
        'Desert Cottontail:Sylvilagus audubonii(Leporidae)':'토끼목',
        'Black-tailed Jackrabbit:Lepus californicus(Leporidae)':'토끼목',
        'Eastern Cottontail:Sylvilagus floridanus(Leporidae)':'토끼목',
        'Accipitridae (unidentified):Accipitridae (incognita)(Accipitridae)':'수리과',
        'Charadriidae (unidentified):Charadriidae (incognita)(Charadriidae)':'물떼새과',
        'Great tit:Parus major(Paridae)':'박새속',
        'Passeridae (unidentified):Passeridae (incognita)(Passeridae)':'집참새',
        'Strigidae (unidentified):Strigidae (incognita)(Strigidae)':'올빼미과',
        'Laridae (unidentified):Laridae (incognita)(Laridae)':'갈매기과',
        'Pelecanidae (unidentified):Pelecanidae (incognita)(Pelecanidae)':'사다새과',
        'Phoenicopteridae (unidentified):Phoenicopteridae (incognita)(Phoenicopteridae)':'홍학과',
        'Snowy Owl:Bubo scandiacus(Strigidae)':'수리부엉이속',
        'Spheniscidae (unidentified):Spheniscidae (incognita)(Spheniscidae)':'펭귄',
        'African Elephant:Loxodonta africana(Elephantidae)':'아프리카코끼리',
        'European Rabbit:Oryctolagus cuniculus(Leporidae)':'유럽토끼',
        'Mountain hare:Lepus timidus(Leporidae)':'고산토끼'}

df0=fromto()
df0['혈청형'].fillna('-',inplace=True)
df0["구분"].fillna('-',inplace=True)
df0["축종"].fillna('-',inplace=True)
dfcol=df0.columns[16:-3]
listcol=dfcol.to_list()
# for i,list in enumerate(df0['축종']):
#     df0.loc[i,'축종']=diction(list)


# for i,list in enumerate(listcol):
#     print('df'+str(i+3)+'=df0.groupby(["질병","국가"])["'+f'{list}'+'"].sum()')
def makepivot():
    try:
        dft=df0.groupby(["질병","국가","혈청형","구분","축종"])["건수"].sum()
        df1=df0.groupby(["질병","국가","혈청형","구분","축종"])["발생일"].first()
        df2=df0.groupby(["질병","국가","혈청형","구분","축종"])["발생일"].last()
        dfa=df0.groupby(["질병","국가","혈청형","구분","축종"])["사육"].sum()
        dfb=df0.groupby(["질병","국가","혈청형","구분","축종"])["감염"].sum()
        dfc=df0.groupby(["질병","국가","혈청형","구분","축종"])["폐사"].sum()
        dfd=df0.groupby(["질병","국가","혈청형","구분","축종"])["살처분"].sum()
        df3=df0.groupby(["질병","국가","혈청형","구분","축종"])["국내이동제한"].sum()
        df4=df0.groupby(["질병","국가","혈청형","구분","축종"])["발생대응 예방접종"].sum()
        df5=df0.groupby(["질병","국가","혈청형","구분","축종"])["봉쇄지역 및/또는 보호지역 외 예찰"].sum()
        df6=df0.groupby(["질병","국가","혈청형","구분","축종"])["봉쇄지역 및/또는 보호지역 내 예찰"].sum()
        df7=df0.groupby(["질병","국가","혈청형","구분","축종"])["스크리닝"].sum()
        df8=df0.groupby(["질병","국가","혈청형","구분","축종"])["이력 추적"].sum()
        df9=df0.groupby(["질병","국가","혈청형","구분","축종"])["격리"].sum()
        df10=df0.groupby(["질병","국가","혈청형","구분","축종"])["동물성 생산물 공식처리"].sum()
        df11=df0.groupby(["질병","국가","혈청형","구분","축종"])["사체·부산물·폐기물 공식처리"].sum()
        df12=df0.groupby(["질병","국가","혈청형","구분","축종"])["생산물 또는 부산물 내 병원체 불활화 처리"].sum()
        df13=df0.groupby(["질병","국가","혈청형","구분","축종"])["살처분*"].sum()
        df14=df0.groupby(["질병","국가","혈청형","구분","축종"])["선택적 살처분"].sum()
        df15=df0.groupby(["질병","국가","혈청형","구분","축종"])["야생보균원 관리"].sum()
        df16=df0.groupby(["질병","국가","혈청형","구분","축종"])["방역대 설정"].sum()
        df17=df0.groupby(["질병","국가","혈청형","구분","축종"])["소독"].sum()
        df18=df0.groupby(["질병","국가","혈청형","구분","축종"])["해충구제"].sum()
        df19=df0.groupby(["질병","국가","혈청형","구분","축종"])["야생매개체 관리"].sum()
        df20=df0.groupby(["질병","국가","혈청형","구분","축종"])["매개체 예찰"].sum()
        df21=df0.groupby(["질병","국가","혈청형","구분","축종"])["생·해체검사"].sum()
        df22=df0.groupby(["질병","국가","혈청형","구분","축종"])["백신접종 허용(백신이 있는 경우)"].sum()
        df23=df0.groupby(["질병","국가","혈청형","구분","축종"])["백신접종 금지"].sum()
        df24=df0.groupby(["질병","국가","혈청형","구분","축종"])["감염동물 미치료"].sum()
        df25=df0.groupby(["질병","국가","혈청형","구분","축종"])["감염동물 치료"].sum()
        df26=df0.groupby(["질병","국가","혈청형","구분","축종"])["도축*"].sum()
    except:pass
    x=pd.concat([dft,df1,df2,dfa,dfb,dfc,dfd,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df18,df19,df20,df21,df22,df23,df24,df25,df26],axis=1,join='outer')
    return x

df_tot=makepivot()

# for i in df_tot['격리']:
listcol=dfcol.to_list()

def deletion(x):
    x=re.sub(r"[,]+",",",x)
    x=x.strip(",")
    return x

for i in listcol:
    df_tot.loc[df_tot[i]>0,i]=i

df_tot=df_tot.applymap(lambda x:"" if x==0 else x)
df_tot['Total']=df_tot[['국내이동제한','발생대응 예방접종','봉쇄지역 및/또는 보호지역 외 예찰',
                       '봉쇄지역 및/또는 보호지역 내 예찰','스크리닝','이력 추적','격리','동물성 생산물 공식처리','사체·부산물·폐기물 공식처리',
                       '생산물 또는 부산물 내 병원체 불활화 처리','살처분*','선택적 살처분','야생보균원 관리','방역대 설정','소독','해충구제',
                       '야생매개체 관리','매개체 예찰','생·해체검사','백신접종 허용(백신이 있는 경우)','백신접종 금지','감염동물 미치료','감염동물 치료','도축*']].apply(lambda x:",".join(x),axis=1)

listcol_mod=['건수', '발생시작', '발생종료', '사육', '감염', '폐사', '살처분', '국내이동제한', '발생대응 예방접종', '봉쇄지역 및/또는 보호지역 외 예찰',
           '봉쇄지역 및/또는 보호지역 내 예찰', '스크리닝', '이력 추적', '격리', '동물성 생산물 공식처리',
           '사체·부산물·폐기물 공식처리', '생산물 또는 부산물 내 병원체 불활화 처리', '살처분*', '선택적 살처분',
           '야생보균원 관리', '방역대 설정', '소독', '해충구제', '야생매개체 관리', '매개체 예찰', '생·해체검사',
           '백신접종 허용(백신이 있는 경우)', '백신접종 금지', '감염동물 미치료', '감염동물 치료', '도축*', 'Total']

df_tot.columns=listcol_mod

df_final=df_tot[['건수', '발생시작', '발생종료', '사육', '감염', '폐사', '살처분','Total']].copy()
df_final['Total']=df_final['Total'].apply(lambda x:deletion(x))

df_final.to_excel(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\final.xlsx')
