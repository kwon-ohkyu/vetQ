# coding = UTF-8
import requests, time, re, sqlite3, pandas as pd, datetime  # url 불러오는 라이브러리
from bs4 import BeautifulSoup  # html 불러오는 라이브러리
import geocoder
import folium
import time
import webbrowser
from selenium import webdriver
from urllib.request import urlretrieve
import win32com.client as win32  # 한/글 열기 위한 모듈
import win32clipboard
import pandas as pd  # 판다스 모듈
from datetime import datetime as dt  # 작업시간을 측정
from io import BytesIO
from PIL import Image

# #
def make_report(data):
    excel = data
    urlretrieve("https://kwon-ohkyu.github.io/webservice/fastreport.hwp","C:/Users/kwonok59/Desktop/python project/OIE scraper/fastreport1.hwp")
    time.sleep(1.0)

    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")  # 한/글 열기
    # # hwnd = win32gui.FindWindow(None, '빈 문서 1 - 한글')  # 한/글 창의 윈도우핸들값을 알아내서
    # # win32gui.ShowWindow(hwnd, 0)  # 한/글 창을 백그라운드로 숨김
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 보안모듈 적용(파일 열고닫을 때 팝업이 안나타남)
    hwp.Open(r"C:/Users/kwonok59/Desktop/python project/OIE scraper/fastreport1.hwp")  # 수정할 한/글 파일 열기

    field_list = [i for i in hwp.GetFieldList(0).split("\x02")]

    for field in field_list:  # 모든 누름틀에 각각,
        hwp.MoveToField(field)  # 커서를 해당 누름틀로 이동(작성과정을 지켜보기 위함. 없어도 무관)
        hwp.PutFieldText(field, excel[field][0])  # f"{{{{{page}}}}}"는 "{{1}}"로 입력된다. {를 출력하려면 {{를 입력.

    hwp.MovePos(3)
    hwp.Run("MoveLeft")
    hwp.InsertPicture(r"C:\Users\kwonok59\Desktop\python project\OIE scraper\screenshot_name.png",True,2)

    def chng(a):
        hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindType = 1
        hwp.HParameterSet.HFindReplace.FindString = a
        hwp.HParameterSet.HFindReplace.ReplaceString = ""
        hwp.HParameterSet.HFindReplace.ReplaceMode = 1
        hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
        hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
        return

    chng("00:00:00")
    chng(".0")
    chng("nan")

def get_hangul():
        ### 한글화
    print('시작합니다.\n잠시만 기다려주세요.')
#         ## 칼럼명 한글로 재설정
    header_kor = ['리포트 번호','세부축종','링크 번호', '국가명', '원인체', '혈청형', '보고일', '건수', '발생일', '지역', '지역*','지역**','구분', '축종', '사육', '감염', '폐사',
                  '살처분','도축','실험실명','진단법','검사축종','검사일자','검사결과']

    kor_df =  get_oie_report()
    kor_df.columns = header_kor

    ## 숫자 문자열 float화
    def float_convert(df, col):
        try:  # float화 시도
            float_convert_values = [float(value) for value in df[col]]
        except ValueError:  # 오류 시 정규식으로 숫자만 추출. 만약 추출 후의 값이 ''이면 nan로 바꾸기
            number_extract_values = [re.search('[0-9]*', value).group() for value in df[col]]
            float_convert_values = [float('nan') if number_extract_value == '' else float(number_extract_value) for number_extract_value in number_extract_values]
        df[col] = float_convert_values

    float_columns = ['링크 번호', '건수', '사육', '감염', '폐사', '살처분', '도축']
    for float_column in float_columns:
        float_convert(df=kor_df, col=float_column)

    ## 날짜 문자열 date화
    # 한국 날짜 형식(shape)으로 변환
    def date_convert(df, col):  # dd/mm/yy를 yy-mm-dd로 변환
        old_dates = [datetime.datetime.strptime(value, '%d/%m/%Y') if type(value) == str else value
                     for value in df[col]]  # 날짜 문자열을 날짜 객체로 변환(y,m,d값이 설정됨). nan값은 변환이 안 되므로 그대로 둠
        new_dates_str = [f"'"+old_date.strftime('%y-%m-%d') if type(old_date) == datetime.datetime else old_date
                         for old_date in old_dates]  # 위 객체를 다시 날짜 문자열로 변환(y,m,d 위치 조정 후 문자열로 바꿈).

        df[col] = new_dates_str  # 변환한 날짜 문자열 리스트를 기존 열에 대입

    date_columns = ['보고일', '발생일','검사일자']
    for date_col in date_columns:
        date_convert(df=kor_df, col=date_col)

    ## 나머지 값 한글화
    # 한글화 리스트에서 찾아서 바꿀 때
    # - df의 col열에서 값이 eng_list에서의 n번째 원소와 같으면 kor_list에서의 n번째 원소로 변환
    def kor_find_convert(df, col, eng_list, kor_list):
        for n in range(len(eng_list)):
            df.loc[df[col] == eng_list[n], col] = kor_list[n]
    # 특정 한글 단어로 바꿀 때
    def kor_convert(df, col1, col2, search_list1, search_list2, kor1, kor2):
        for search1 in search_list1:
            df.loc[df[col1] == search1, col2] = kor1
        for search2 in search_list2:
            df.loc[df[col1] == search2, col2] = kor2

    '''리스트 작성하여 한글로 변환하기 위한 목록화'''

    countries_eng = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia And Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African (Rep.)', 'Ceuta', 'Chad', 'Chile', "China (People's Rep. of)", 'Colombia', 'Comoros', 'Congo (Dem. Rep. of The)', 'Congo (Rep. of The)', 'Costa Rica', "Cote D'Ivoire", 'Croatia', 'Cuba', 'Curacao', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'Former Yug. Rep. of Macedonia', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong (SAR - PRC)', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', "Korea (Dem. People's Rep.)", 'Korea (Rep. of)', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia (Federated States Of)', 'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nepal', 'Netherlands (The)', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Macedonia (Rep. of)', 'Norway', 'Oman', 'Pakistan', 'Palestinian Auton. Territories', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Lucia', 'San Marino', 'Sao Tome And Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South Africa', 'South Sudan (Rep. of)', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Chinese Taipei', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Trinidad And Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States of America', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

    countries_kor = ['아프가니스탄', '알바니아', '알제리', '안도라', '앙골라', '아르헨티나', '아르메니아', '호주', '오스트리아', '아제르바이잔', '바하마', '바레인', '방글라데시', '바베이도스', '벨라루스', '벨기에', '벨리즈', '베냉', '부탄', '볼리비아', '보스니아 헤르체고비나', '보츠와나', '브라질', '브룬디', '불가리아', '부르키나파소', '브루나이', '카보베르데', '캄보디아', '카메룬', '캐나다', '중앙아프리카공화국', '세우타', '차드', '칠레', '중국', '콜롬비아', '코모르', '콩고민주공화국', '콩고', '코스타리카', '코트디부아르', '크로아티아', '쿠바', '큐라소', '사이프러스', '체코공화국', '덴마크', '지부티', '도미니카공화국', '에쿠아도르', '이집트', '엘살바도르', '적도 기니', '에리트레아', '에스토니아', '에스와티니', '이디오피아', '피지', '핀란드', '북마케도니아', '프랑스', '가봉', '감비아', '구루지아', '독일', '가나', '그리스', '과테말라', '기니', '기네비쏘', '가이아나', '아이티', '온두라스', '홍콩', '헝가리', '아이슬랜드', '인도', '인도네시아', '이란', '이라크', '아일랜드', '이스라엘', '이탈리아', '자메이카', '일본', '요르단', '카자흐스탄', '케냐', '북한', '대한민국', '쿠웨이트', '키르기스스탄', '라오스', '라트비아', '레바논', '레소토', '라이베리아', '리비아', '리히텐슈타인', '리투아니아', '룩셈부르크', '마다가스카르', '말라위', '말레이지아', '몰디브', '말리', '몰타', '모리타니', '모리셔스', '멕시코', '미크로네시아 연방', '몰도바', '몽골', '몬테네그로', '모로코', '모잠비크', '미얀마', '나미비아', '네팔', '네덜란드', '뉴칼레도니아', '뉴질랜드', '니카라과', '니제르', '나이지리아', '북마케도니아', '노르웨이', '오만', '파키스탄', '팔레스타인', '파나마', '파푸아뉴기니', '파라과이', '페루', '필리핀', '폴란드', '포르투갈', '카타르', '루마니아', '러시아', '르완다', '세인트 루시아', '산마리노', '쌍투메 프린시페', '사우디아라비아', '세네갈', '세르비아', '세이셸', '시에라리온', '싱가포르', '슬로바키아', '슬로베니아', '소말리아', '남아프리카공화국', '남수단', '스페인', '스리랑카', '수단', '수리남', '에스와티니', '스웨덴', '스위스', '시리아', '대만', '타지키스탄', '탄자니아', '태국', '동티모르', '토고', '트리니다드토바고', '튀니지', '터키', '투르크메니스탄', '우간다', '우크라이나', '아랍에미리트', '영국', '미국', '우루과이', '우즈베키스탄', '바누아투', '베네수엘라', '베트남', '예멘', '잠비아', '짐바브웨']
    kor_find_convert(df=kor_df, col='국가명', eng_list=countries_eng, kor_list=countries_kor)

    # 원인체 한글화
    agent_eng = ['Adenovirus infection', 'Aeromonas infection', 'African horse sickness', 'African swine fever', 'Aino virus infection', 'Akabane disease', 'Aleutian disease in mink', 'American foulbrood disease', 'Anaplasmasis', 'Anthrax', 'Aspergillosis', 'Atrophic rhinitis', "Aujeszky's disease", 'Aujeszkys disease', 'Avian encephalomyelitis', 'Avian mycoplasmosis', 'Avian mycoplasmosis (M. gallisepticum)', 'Babesiosis', 'Blackleg', 'Bluetongue', 'Bovine ephemeral fever', 'Bovine leukemia', 'Bovine respiratory syncytial virus infection', 'Bovine rotavirus infection', 'Bovine spongiform encephalopathy', 'Bovine viral diarrhoea', 'Brucellosis', 'Brucellosis (Brucella abortus)', 'Brucellosis (Brucella melitensis)', 'Brucellosis (Brucella suis)', 'Candidiasis', 'Canine coronavirus infection', 'Canine distemper', 'Canine parvovirus infection', 'Caprine arthritis/encephalitis', 'Chalkbrood disease', 'Chronic wasting disease', 'Chuzan disease', 'Classical swine fever', 'Clostridium botulinum', 'Coccidiosis', 'Coccidiosis', 'Colibacillosis', 'Contagious bovine pleuropneumonia', 'Contagious equine metritis', 'Cryptosporidiosis', 'Cysticercosis', 'Duck virus hepatitis', 'Edwardsiellosis', 'Encephalomyocarditis', 'Enterotoxemia', 'Eperythrozoonosis', 'Equid herpesvirus-1 (EHV-1)', 'Equid herpesvirus-1 (EHV-1) (Infection with)', 'Equine encephalomyelitis (Western)', 'Equine infectious anaemia', 'Equine influenza', 'Equine piroplasmosis', 'Equine viral arteritis', 'European foulbrood of honey bees', 'Foot and mouth disease', 'Foot rot', 'Foot rot', 'Fowl cholera', 'Fowl pox', 'Fowl typhoid', 'Genital campylobacteriosis', 'Glanders', "Glasser's disease", 'Highly pathogenic avian influenza', 'Highly pathogenic influenza A viruses (infection with) (non-poultry including wild birds)', 'Ibaraki disease', 'Inclusion body hepatitis', 'Infectiious bursal disease', 'Infectious bursal disease (Gumboro disease)', 'Infectious bovine rhinotracheitis', 'Infectious bronchitis', 'Infectious laryngotracheitis', 'Japanese b encephalitis', "Johne's disease", 'Leishmaniosis', 'Leptospirosis', 'Leucocytozoonosis', 'Listeriosis', 'Liver fluke or fascioliasis', 'Low pathogenic avian influenza (poultry)', 'Lumpy skin disease', 'Lymphoid leukosis', 'Maedi-visna', 'Mange or scabs', "Marek's disease", 'Mastitis', 'MERS-CoV', 'Middle East Respiratory Syndrome (MERS) ', 'Middle East Respiratory Syndrome Coronavirus (MERS-Cov) ', 'Mink viral enteritis', 'Mycobacterium tuberculosis', 'Mycobacterium tuberculosis complex (Infection with)', 'Mycoplasmal pneumonia', 'Myxomatosis', 'Neosporosis', 'Newcastle disease', 'Nipahvirus infection', 'Nosema disease', 'Pcv-2 infection', 'Peste des petits ruminants', 'Pneumonic bordetellosis of dogs', 'Porcine epidemic diarrhea', 'Porcine getahvirus disease', 'Porcine parvovirus infection', 'Porcine reproductive and respiratory syndrome', 'Porcine respiratory coronaviral infection', 'Porcine rotavirus infection', 'Pullorum disease', 'Q fever', 'Rabies', 'Rabbit haemorrhagic disease', 'Remerella infection', 'Reovirus infection', 'Reticuloendotheliosis', 'Richinosis', 'Rift valley fever', 'Rift Valley fever', 'Rinderpest', 'Salmonellosis', 'Scrapie', 'Sheep pox and goat pox', 'Small hive beetle infestation (Aethina tumida)', 'Snuffles', 'Spirochetosis', 'Strangles', 'Streptococcosis', 'Swine dysentery', 'Swine erysipelas', 'Swine vesicular disease', 'Transmissible gastroenteritis', 'Tuberculosis', 'Tularemia', 'Varroosis of honey bees', 'Vesicular stomatitis', 'West nile fever', 'West Nile Fever']

    agent_kor = ['소아데노바이러스감염증', '에로모나스증', '아프리카마역', '아프리카돼지열병', '아이노바이러스감염증', '소아까바네병', '밍크알류샨병', '부저병', '아나플라즈마병', '탄저', '곰팡이성폐렴', '위축성비염', '오제스키병', '오제스키병', '뇌척수염', '닭 마이코플라즈마병', '닭 마이코플라즈마병', '소바베시아병', '기종저', '블루텅', '소유행열', '소백혈병', '소RS바이러스병', '소로타바이러스감염증', '소해면상뇌증', '소바이러스성설사', '브루셀라병', '브루셀라병(소유산균)', '브루셀라병(말타열균)', '브루셀라병(돈유산균)', '칸디다증', '개코로나바이러스감염증', '개디스템퍼', '개파보바이러스감염증', '산양관절염-뇌염', '꿀벌백묵병', '사슴만성소모성질병', '소츄잔병', '돼지열병', '보툴리즘', '닭콕시듐증', '소콕시듐증', '대장균증', '우폐역', '말전염성 자궁염', '크립토스포리디움증', '낭미충증', '오리바이러스성간염', '에드워드병', '돼지뇌심근염', '장독혈증', '에페리스로조아병', '말헤르페스바이러스-1', '말헤르페스바이러스-1', '서부말뇌염바이러스', '말전염성빈혈', '말인플루엔자', '말파이로플라즈마증', '말바이러스성동맥염', '유럽 부저병', '구제역', '지간부란', '소부제병', '가금콜레라', '계두', '가금티푸스', '소캄필로박터증', '말비저', '글래서씨병', '고병원성조류인플루엔자', '고병원성조류인플루엔자', '이바라기병', '봉입체성간염', '전염성F낭병', '전염성F낭병', '소전염성비기관염', '전염성기관지염', '전염성후두기관염', '돼지일본뇌염', '요네병', '리슈만편모충증', '렙토스피라병', '류코사이토준병', '리스테리아병', '간질증', '저병원성조류인플루엔자', '럼피스킨병', '닭백혈병', '메디-비스나 바이러스', '개선충증', '마렉병', '유방염', '중동호흡기증후군 코로나바이러스', '중동호흡기증후군', '중동호흡기증후군 코로나바이러스', '밍크바이러스성장염', '마이코박테리움결핵균', '마이코박테리움결핵복합체', '마이코플라즈마폐렴', '점액종증', '네오스포라병', '뉴캣슬병', '니파바이러스감염증', '노제마병', '돼지써코바이러스감염증', '가성우역', '개보데텔라폐렴', '돼지유행성설사병', '돼지게타바이러스감염증', '돼지파보바이러스감염증', '돼지생식기호흡기증후군', '돼지호흡기코로나바이러스감염증', '돼지로타바이러스감염증', '추백리', '큐열', '광견병', '토끼 바이러스성 출혈열', '오리패혈증', '레오바이러스감염증', '닭세망내피증', '선모충증', '리프트계곡열', '리프트계곡열', '우역', '살모넬라균증', '스크래피', '양두·산양두', '작은벌집딱정벌레감염증', '전염성비염', '스피로헤타증', '말선역', '연쇄상구균감염증', '돼지적리', '돼지단독', '돼지수포병', '돼지전염성위장염', '소결핵병', '야토병', '꿀벌바로아응애', '수포성구내염', '웨스트나일열', '웨스트나일열']

    species_eng = ['Swine', 'Wild boar:Sus scrofa(Suidae)', 'Dogs', 'Cats', 'Cattle', 'Equidae', 'Sheep', 'Goats']
    species_kor = ['돼지', '멧돼지', '개', '고양이', '소', '말과', '면양', '산양']

    stock_species = ['돼지']
    wild_species = ['멧돼지']

    stock_place_list = ['Apiary', 'Backyard', 'Farm', 'Livestock market', 'Slaughterhouse', 'Village', 'Zoo']
    wild_place_list = ['Forest', 'Natural park']

    '''여기까지가 목록화 작업된 부분임'''

    # 구분 한글화
    kor_find_convert(df=kor_df, col='원인체', eng_list=agent_eng, kor_list=agent_kor)
    kor_find_convert(df=kor_df, col='축종', eng_list=species_eng, kor_list=species_kor)
    kor_convert(df=kor_df, col1='축종', col2='구분', search_list1=stock_species, search_list2=wild_species, kor1='사육', kor2='야생')
    kor_convert(df=kor_df, col1='구분', col2='구분', search_list1=stock_place_list, search_list2=wild_place_list, kor1='사육', kor2='야생')


    # kor_totalhead df에서 '건수'열의 값이 1 이상인 행은 '지역'열 값에 문자열' 등'을 추가
    kor_df.loc[kor_df['건수'] > 1, '지역'] = kor_df.loc[kor_df['건수'] > 1, '지역'] + ' 등'
    region_query=kor_df.iloc[0,10]
    region_query1=kor_df.iloc[0,11]
    try:
        g=geocoder.osm(region_query) or geocoder.osm(resion_query1)
        a=g.osm
        long=a['x']
        lat=a['y']
    except:print("주소 값이 정확하지 않습니다")




    try: name=a['addr:city'] or a['addr:state']
    except:pass

    fast_map=folium.Map(location=[lat,long],zoom_start=6,tiles='cartodbpositron')
    folium.CircleMarker([lat,long],radius=30,color='brown',
                        fill=True,fill_color='coral',
                        fill_opacity=0.3,popup=region_query
                        ).add_to(fast_map)

    fast_map.save(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\fast.html')
    time.sleep(5)

    driver = webdriver.Chrome(r'C:\Users\kwonok59\Desktop\python project\maps\chromedriver.exe')
    driver.get(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\fast.html')
    driver.save_screenshot(r'C:\Users\kwonok59\Desktop\python project\OIE scraper\screenshot_name.png')
    driver.close()

    #
    # def save_excel(df_list, path):
    #     with pd.ExcelWriter(path) as writer:
    #         df_list.to_excel(writer, index=False)
    #
    # sheetnames = ['보고서']
    # save_excel(df_list=kor_df, path=r'C:\Users\kwonok59\Desktop\python project\OIE scraper\fast report.xlsx')

    time.sleep(5)
    make_report(kor_df)
    print('완료되었습니다')


def get_oie_report() :
    time.sleep(3)  # 작업을 멈춤. 초 단위
    # format 메소드 이용하여 new_linknumber를 넣는 url를 만듦
    linknumber=input("보고서 번호를 입력하세요")
    url = f'http://www.oie.int/wahis_2/public/wahid.php/Reviewreport/Review?page_refer=MapFullEventReport&reportid={linknumber}'
    # table 태그만을 뽑아 이를 각각 데이터프레임(df)으로 만들어 하나의 리스트에 넣음. flavor='lxml' : html5lib not found 오류를 미연에 방지
    table = pd.read_html(url, flavor='lxml')

    # table[0] : 모든 박스 내용을 텍스트만 뽑아놓은 df
    ## Summary 박스
     # T : 행 열 전환
    summary_df = table[3].T
    summary_header = summary_df.loc[0]  # Summary 데이터프레임(df)의 칼럼명으로 지정하기 위함
    summary_df = summary_df.loc[1:].rename(columns=summary_header)

    if not 'Serotype' in list(summary_header):  # '포함(in)'구문을 쓰기 위해 Series 타입을 list로 바꿈
        summary_df['Serotype'] = float('nan')  # Serotype 열을 추가. 값은 nan으로 넣기
    # 국가명, 원인체, 링크 번호
    country_name = table[0].loc[0, 0].split(',')[-1]
    agent = table[0].loc[0, 0].split(',')[0]
    summary_df['Country'] = [country_name]
    summary_df['Agent'] = [agent]
    summary_df['Link number'] = [linknumber]

    total_idx = table[0][table[0][0].str.contains('Total outbreaks')].index.to_list()[0]
    ## 발생 건 박스
    # table[0]에서 Total outbreaks 문자열 들어간 위치
    total_table_num = (total_idx - 4) * 2 + 4

    for n in range(4, total_table_num, 2):
        table[n].loc[0, 0] = 'Region'
    # table[n].loc[0, 0] : 'Outbreak 1'부분을 'Region'으로 바꿈. 발생 건 박스별로 칼럼 수가 다를 수 있으므로 전체 박스 다 변환
    # table[4]부터 발생 건 박스. table[n+1] : Affected animals df. 두 df를 가로로 합치는 코드를 반복
    outbreaks_df = [pd.concat([table[n].T, table[n + 1]], axis=1, ignore_index=True) for n in
                    range(4, total_table_num, 2)]    # 박스별로 칼럼 수가 다를 수 있으므로 칼럼명에 반복문
    outbreaks_df = [outbreak_df.loc[1:].rename(columns=outbreak_df.loc[0]) for outbreak_df in outbreaks_df]
    # summary df와 outbreaks df 합치기
    a=table[-3]
    a=a.loc[1:].rename(columns=a.loc[0])
    a.rename(columns={'Species':'testspecies'},inplace=True)
    a.reset_index(inplace=True,drop=True)
    summary_outbreaks_df_list = [pd.concat([summary_df, outbreak_df], axis=1) for outbreak_df in outbreaks_df]
    summary_outbreaks_df = pd.concat(summary_outbreaks_df_list, ignore_index=True, sort=False)  # sort : 칼럼명 정렬
    summary_outbreaks_df = pd.concat([summary_outbreaks_df,a], axis=1)
    summary_outbreaks_df['Number of outbreaks_df'] = float('nan')
    summary_outbreaks_df=summary_outbreaks_df.reset_index(drop=True)
    outbreaks_number = re.search('[0-9]+', table[0].loc[3, 0]).group()
    summary_outbreaks_df.loc[0, 'Number of outbreaks_df'] = outbreaks_number  # 첫 행에만 건 수 넣기
    if not 'Affected population' in list(summary_outbreaks_df.columns):
        summary_outbreaks_df['Affected population'] = float('nan')
    # Region 열의 값 가공
    summary_outbreaks_df['Region*'] = float('nan')
    summary_outbreaks_df['Region**'] = float('nan')

    for n, region in enumerate(summary_outbreaks_df.loc[:, 'Region']):
        try:
            region_slice = region.split(',')
            summary_outbreaks_df.loc[n, 'Region*'] = region_slice[-2] + ', ' + region_slice[-1]
            summary_outbreaks_df.loc[n,'Region**'] = region_slice[-1]
        except AttributeError:pass

    # 필요한 열만 뽑기('Affected population'와 'Report type'열은 후에 맨 뒤로 옮길 것임)
    header_need = ['Report type', 'Affected population', 'Link number', 'Country', 'Agent', 'Serotype', 'Report date',
                   'Number of outbreaks_df', 'Date of start of the outbreak', 'Region', 'Region*', 'Epidemiological unit',
                   'Species', 'Susceptible', 'Cases', 'Deaths', 'Killed and disposed of', 'Slaughtered',
                   'Laboratory name and type','Test','testspecies','Test date','Result']
    summary_outbreaks_df = summary_outbreaks_df[header_need]

    return summary_outbreaks_df


if __name__ == "__main__":
    get_hangul()
