import pandas as pd
import numpy as np
import seaborn as sns
import time

df=pd.read_excel(r'C:\Users\kwonok59\Desktop\python project\data analysis\import data_0420 (1).xlsx')
df.set_index('국가',inplace=True)
# df.info()

"""(입국 국가)*(국내 검역 공항)_불법 수화물 총량"""

df0=df.iloc[:,18:25]
len(df0.index)

"""generating v_od distribution

매개변수
> o: 수입국가 행인덱스 번호, e=국내공항 위치

> Triangular Distribution parameter : min=최저값, mode=최빈값, max=최대값

> k=시뮬레이션 수 - 분포 도출을 위하여 일반적으로 5,000을 사용하는 것이 적절함

결과
> 입국국가 1개, 국내 공항 1개의 진단되지 않은 불법 수화물 분포임

"""

df0.columns

"""KDE : 분포에 대한 Kernel density 추정 결과임"""


def v_od(o,d,min,mode,max,k):
  v_od=df0.iloc[o,d]*np.random.triangular(min,mode,max,k)
  sns.kdeplot(v_od)
  print('수출국=%s 입항=%s : 평균=%.2f, 표준편차=%.2f' % (df0.index[o], df0.columns[d],v_od.mean(),v_od.std()))
  return v_od

for i in range(len(df0.index)):
    for j in range(len(df0.columns)):
        v_od(i,j,0.2,0.5,0.9,1000)
        time.sleep(.5)
