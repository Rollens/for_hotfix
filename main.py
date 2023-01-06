
import os
from stic import YieldStatistic
from barchart import StatisticsAndDraw
import time

def InitVar():
    while True:
        if os.path.isdir(DataRoute:=input('請輸入資料夾名稱(預設Data):') or 'Data'):
            print('包含%d片測試資料'%len(os.listdir(DataRoute)))
            break
        else:
            if input('資料夾{}不存在,按c跳出程式,按任意鍵重新輸入:'.format(DataRoute)) == 'c':
                os.system('cls')
                print('好好設定!')
                exit()

    TheFirst = input('請輸入表頭第一項:') or 'PosX'

    if table:=input('輸出報表(y/n)?') == 'y':
        while True:
            item = input('請輸入卡控設定檔名(預設Boundary.csv):') or 'Boundary.csv'
            if '.csv' not in item:
                item += '.csv'
            if os.path.isfile(item):
                print('使用卡控條件檔{}'.format(item))
                break
            else:
                if input('卡控檔{}不存在= =,按c跳出程式,按任意鍵重新輸入:'.format(item)) =='c':
                    os.system('cls')
                    print('好好設定!')
                    exit()
    if graph := input('輸出長條圖(y/n)?') == 'y':
        while True:
            cond = input('請輸入分類條件檔路徑(預設Scale.csv):') or 'Scale.csv'
            if '.csv' not in cond:
                cond += '.csv'
            if os.path.isfile(cond):
                print('使用分類條件{}'.format(cond))
                break
            else:
                if input('條件檔{}不存在,按Enter跳出程式,按c跳出程式,按任意鍵重新輸入:'.format(cond)) == 'c':
                    os.system('cls')
                    print('好好設定!')
                    exit()


    if table:
        ys = YieldStatistic(item,TheFirst)

        ys.ShowBoundaryInfo()
        ys.LoadData(DataRoute)
        ys.MakeBigForm()
        del ys
    if graph:
        sad = StatisticsAndDraw(cond,DataRoute)
        del sad

    if not (table or graph):
        print('那你開程式幹嘛= =')
        exit()
        
    return input('請問是否繼續執行(繼續:y/停止:Enter):')

def FitTech():
    os.system('cls')
    print('<惠特信仰>\n誠信負責\t以客為尊\n專注創新\t積極向前\n合理流程\t持續改善\n提升效能\t追求卓越\n知行合一\t日起有功')
    exit()    

if __name__ == '__main__':
    while True:
        if InitVar() != 'y':
            break
    FitTech()