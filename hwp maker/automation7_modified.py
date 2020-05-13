import shutil  # 파일복사할때 필요한 모듈
import win32com.client as win32  # 한/글 열기 위한 모듈
import pandas as pd  # 판다스 모듈
from datetime import datetime as dt  # 작업시간을 측정
import win32gui  # 한/글 창을 백그라운드로 숨기기 위한 모듈
#
def chng(a):
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindType = 1
    hwp.HParameterSet.HFindReplace.FindString = a
    hwp.HParameterSet.HFindReplace.ReplaceString = ""
    hwp.HParameterSet.HFindReplace.ReplaceMode = 1
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    return
# #
excel = pd.read_excel(r"C:\Users\kwonok59\Desktop\python project\hwp maker\oie_reports_200513.xlsx",sheet_name='해동(총 두수)')  # 엑셀로 데이터프레임 생성
#
hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")  # 한/글 열기

## hwnd = win32gui.FindWindow(None, '빈 문서 1 - 한글')  # 한/글 창의 윈도우핸들값을 알아내서
## win32gui.ShowWindow(hwnd, 0)  # 한/글 창을 백그라운드로 숨김
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 보안모듈 적용(파일 열고닫을 때 팝업이 안나타남)
# #
shutil.copyfile(r"C:\Users\kwonok59\Desktop\python project\hwp maker\data.hwp",  # 원본은 그대로 두고,
                r"C:\Users\kwonok59\Desktop\python project\hwp maker\data2.hwp")  # 복사한 파일을 수정하려고 함.
# #
hwp.Open(r"C:\Users\kwonok59\Desktop\python project\hwp maker\data2.hwp")  # 수정할 한/글 파일 열기
# #
#
a=excel['국가명']
b=a.index[a.isnull()].to_list() #isnull의 값 리스트화b#
# start_time = dt.now()  # 작업시간을 측정하기 위해 현재 시각을 start_time 변수에 저장. 없어도 됨...
field_list = [i for i in hwp.GetFieldList().split("\x02")]  # 한/글 안의 누름틀 목록 불러오기# # # #
print('페이지 복사를 시작합니다.')
# #
for i in range(len(a)-1):
    i=i+1
    if i not in b:
        hwp.MovePos(2)
        hwp.HAction.Run("Select");
        hwp.HAction.Run('MovePageEnd')
        hwp.Run('Copy')  # Ctrl-C (복사)
        hwp.MovePos(3)  # 문서 끝으로 이동
        hwp.Run("BreakPage")
        hwp.Run('Paste')  # Ctrl-V (붙여넣기)
        hwp.MovePos(3)
    else:
        a=int(i)-1
        hwp.MoveToField('발생일'f'{{{{{a}}}}}')
        hwp.HAction.Run("TableAppendRow")
        hwp.HAction.Run("TableCellBlock")
        hwp.HAction.Run("TableUpperCell")
        hwp.HAction.Run("TableCellBlock")
        hwp.HAction.Run("TableCellBlockExtend")
        hwp.HAction.Run("TableColEnd")
        hwp.HAction.Run("TableLowerCell")
        hwp.HAction.Run("TableAutoFill")

print(f'{len(excel)}페이지 복사를 완료하였습니다.')
# # # # #
for page in range(len(excel)):  # 한/글 모든 페이지를 전부 순회하면서,
    for field in field_list:  # 모든 누름틀에 각각,
        hwp.MoveToField(f'{field}{{{{{page}}}}}')
        if page not in b:
            hwp.MoveToField('링크번호'f'{{{{{page}}}}}')  # 커서를 해당 누름틀로 이동(작성과정을 지켜보기 위함. 없어도 무관)
            hwp.PutFieldText(f'{field}{{{{{page}}}}}',
                            excel[field].iloc[page])   # f"{{{{{page}}}}}"는 "{{1}}"로 입력된다. {를 출력하려면 {{를 입력.
        else:
            hwp.PutFieldText(f'{field}{{{{{page}}}}}',
                            excel[field].iloc[page])   # f"{{{{{page}}}}}"는 "{{1}}"로 입력된다. {를 출력하려면 {{를 입력.

    chng("nan") # a값 바꿔쓰기
    chng("00:00:00")
# #
#
#
#     # hwp.PutFieldText("index{{1}}") 식으로 실행될 것
#     # print(f'{page + 1}:{excel.name[page]}')    # 현재 입력이 진행되고 있는 한/글문서 페이지번호를 콘솔창에 출력
# # # # hwp.Save()  # 한/글 파일(award_result.hwp)을 저장하고,
# # # hwp.Quit()  # 한/글 종료. (저장하지 않고 종료하는 방법은 7강에서~)
# #
# end_time = dt.now()  # 작업종료 시각. 없어도 무관.
# 소요시간 = end_time - start_time  # 전체 작업시간을 기록. 없어도 무관.
#
# print(f'작업을 완료하였습니다. 약 {소요시간.seconds}초 소요되었습니다.')  # 작업완료된 후 출력. 끝.
