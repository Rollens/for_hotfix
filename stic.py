import csv
import os
from collections import defaultdict
from datetime import datetime
import re

#DataRoute = r'Tocal'
#DataToCal = os.listdir(DataRoute)
#ToDeter = ['VF4','VZ1']
#Boundary={'VF4':(2.35,2.45),'VZ1':(46.5,53.5)}
#TheFirst = 'TEST'

class YieldStatistic:
    
    def __init__(self,BoundaryRoute:str,TheFirst:str) -> None:
        self.ToDeter={}
        self.Boundary={}
        self.BigForm=[]
        self.TheFirst=TheFirst
        self.stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.startTime=0.0
        self.endTime=0.0
        self.LoadBoundary(BoundaryRoute)
        self.headerInfo=[]
        self.root=''

    def LoadData(self,DataRoute)->None:
        sta=[]
        DataToCal = os.listdir(DataRoute)
        self.root=DataRoute
        filename ='StatisticOutput/{}_{}.txt'.format(DataRoute,self.stamp)
        with open(filename,'a') as f:
            f.write('<-----設定資訊----->\n')
            for t in self.ToDeter.keys():
                if t:
                    f.write('測試項{}:卡控下限{};卡控上限{}\n'.format(t,*self.Boundary[t]))
                    self.headerInfo.append('{},{},{}\r\n'.format(t,*self.Boundary[t]))
            f.write('=================================================\n')
        for d in DataToCal:
            sepYield=[]
            sepRSD=[]
            indexInfo={}
            check=[]
            checkFirst=False
            print('現正計算%s'%d)
            ng = 0
            counter = 0
            ng_table =defaultdict(int)
            valueTable = defaultdict(list)
            with open(os.path.join(DataRoute,d),'r') as f:
                flag=False
                timeflag=True
                endTimeflag=True
                rows = csv.reader(f)
                for row in rows:
                    if row:
                        if (row[0] == 'TestTime' or row[0] == 'StartTime' or row[0] == 'TestStartTime') and timeflag:
                            #startTime = datetime.timestamp(datetime.strptime(row[2],self.TimeFormat))
                            self.startTime,timeflag = self.checkTime(row)
                            continue
                        if (row[0] == 'TestEndTime') and endTimeflag:
                            self.endTime,endTimeflag = self.checkTime(row)
                            continue
                        if checkFirst:
                            for index in self.ToDeter.keys():
                                if not row[indexInfo[index]]:
                                    check.append(index)
                            for todel in check:
                                self.ToDeter.pop(todel)
                                print('條件{}紀錄到為空白,已從Condictions中刪除'.format(todel))
                            check=[]
                            checkFirst = False
                        if row[0] == 'PosX' or row[0] == 'TEST':
                            row = [_.strip() for _ in row] #刪除TesterData內莫名其妙的空格
                            for i in self.ToDeter.keys():
                                try:
                                    indexInfo[i]=row.index(i)
                                except:
                                    print('測試項{}不在RowData內'.format(i))
                                    check.append(i)
                            checkFirst=True
                            flag = True
                            for i in check:
                                self.ToDeter.pop(i)
                                print('測試項{}已從ToDeter中刪除'.format(i))
                            check=[]
                        elif flag:
                            flag2 = True #避免重複計算
                            counter += 1
                            for item in self.ToDeter.keys():
                                val = float(row[indexInfo[item]])
                                bnd = (val < self.Boundary[item][0] or val > self.Boundary[item][1])
                                if bnd:
                                    ng_table[item] += 1
                                    if flag2:
                                        ng += 1
                                    flag2 = False #算過一次後打False避免同一晶粒算到多次ng
                                else:
                                    valueTable[item].append(val)
            if endTimeflag:
                self.endTime = os.path.getmtime(os.path.join(DataRoute,d))
            ct =(self.endTime-self.startTime)*1000/counter
            yd = 1-ng/counter
            sta.append([d[:-4],round(ct,3),'{:.3%}'.format(yd)])
            with open(filename,'a') as f:
                f.write('片號:{}\t經過時間(s): {:.0f}\t總顆粒數: {}\n'.format(d[:-4],self.endTime-self.startTime,counter))
                f.write('良率: {:.3%}\t平均CycleTime: {:.2f}ms\n'.format(yd,ct))
                f.write('-------------------<單獨測試項良率>--------------------------\n')
                print('片號:{}'.format(d[:-4]))
                for t in self.ToDeter:
                    pres = self.checkPrecision(t,valueTable[t])
                    sepYield.append(1-ng_table[t]/counter)
                    sepRSD.append(pres)
                    print('測試項{}\t良率為: {:.3%}\t相對標準偏差:{:.3%}'.format(t,1-ng_table[t]/counter,pres))
                    f.write('測試項{}\t良率為: {:.3%}\t相對標準偏差:{:.3%}\n'.format(t,1-ng_table[t]/counter,pres))
                print('總良率為: {:.3%}'.format(yd))
                f.write('=================================================\n')
                self.printTimeInfo()
                self.BigForm.append(self.BigFormCheck(d[:-4],counter,yd,self.endTime-self.startTime,ct,sepYield,sepRSD))#片號,總晶粒數,總量率,總時間,平均Cycle Time,
                del valueTable

    def checkTime(self,row):
        row = [x for x in row if x]#去掉所有的低能空格
        try:
            outTime = datetime.timestamp(datetime.strptime(row[1],self.TimeFormatChecker(row[1])))
        except:
            print('時間格式不在列表內,請找Rollens\t 格式:{}'.format(row[1]))
            exit()
        """
        if len(row) > 2:
            try:
                outTime = datetime.timestamp(datetime.strptime(row[2],self.TimeFormatChecker(row[2])))
            except:
                print('時間格式不在列表內,請找Rollens\t 格式:{}'.format(row[2]))
                exit()
        elif len(row) == 2:
            try:
                outTime = datetime.timestamp(datetime.strptime(row[1],self.TimeFormatChecker(row[1])))
            except:
                print('時間格式不在列表內,請找Rollens\t 格式:{}'.format(row[1]))
                exit()
        else:
            raise BaseException('時間格式標新立異,直接找Rollens')"""
        return outTime,False

    def BigFormCheck(self,WaferID,TotalChip,TotalYield,TotalTime,AverageCycleTime,sepYield,sepRSD)->list:
        temp_str='{},{},{:.3%},{:.0f},{:.2f}'.format(WaferID,TotalChip,TotalYield,TotalTime,AverageCycleTime)
        tempY = list(map(lambda x:'{:.3%}'.format(x),sepYield))
        tempR = list(map(lambda x:'{:.3%}'.format(x),sepRSD))
        temp=temp_str.split(',')
        return temp+tempY+tempR

    def MakeBigForm(self)->None:
        with open('StatisticOutput/{}_Statistics_{}.csv'.format(self.root,self.stamp),'a',newline='') as f:
            f.write('Item,Lower Boundary,Upper Boundary\r\n')
            f.writelines(self.headerInfo)
            f.write('\n\n')
            col = ['WaferID','Total Chips','Average Yield','Total Time(s)','Single Chip Cycle Time']+['{} Yield'.format(_) for _ in self.ToDeter]+['{} RSD'.format(_) for _ in self.ToDeter]
            writer = csv.writer(f)
            writer.writerow(col)
            writer.writerows(self.BigForm)
        #df = pd.DataFrame(self.BigForm,columns=col)
        #df.to_csv('Statistics_{}.csv'.format(self.stamp),index=False)
        print('大表完成,時間戳記:{}'.format(self.stamp))

    def LoadBoundary(self,Route:str)->dict:
        with open(Route,'r') as f:
            rows = csv.reader(f)
            for row in rows:
                self.Boundary[row[0]] = (float(row[1]),float(row[2]))
                self.ToDeter[row[0]]=0

    def ShowBoundaryInfo(self)->None:
        for index,data in self.Boundary.items():
            print('測試項{}:卡控下限{}，卡控上限{}'.format(index,data[0],data[1]))

    def checkPrecision(self,item:str,Data:list)->float:
        if not Data:
            raise BaseException('卡控條件設定錯誤,請確認{}卡控範圍'.format(item))
        avg = sum(Data)/len(Data)
        var = sum((d-avg)**2 for d in Data)/len(Data)
        return var**0.5/avg if var**0.5/avg < 10 else 0

    def LoadTimeFormat(self):
        with open('TimeFormat.csv','r') as f:
            rows = csv.reader(f)
            for row in rows:
                return row[0],row[1]

    def TimeFormatChecker(self,original:str):
        FormatStyle={'%Y/%m/%d %H:%M:%S':r'\d{4}\/\d{1,2}\/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%y/%m/%d %H:%M:%S':r'\d{2}\/\d{1,2}\/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%Y-%m-%d %H:%M:%S':r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%y-%m-%d %H:%M:%S':r'\d{2}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%m/%d/%Y %H:%M:%S':r'\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%m/%d/%y %H:%M:%S':r'\d{1,2}\/\d{1,2}\/\d{2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%m-%d-%Y %H:%M:%S':r'\d{1,2}-\d{1,2}-\d{4} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%m-%d-%y %H:%M:%S':r'\d{1,2}-\d{1,2}-\d{2} \d{1,2}:\d{1,2}:\d{1,2}',
                    '%Y/%m/%d %H:%M':r'\d{4}\/\d{1,2}\/\d{1,2} \d{1,2}:\d{1,2}',
                    '%Y-%m-%d %H:%M':r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}',
        }
        for format,reg in FormatStyle.items():
            if re.match(reg,original):
                return format

    def printTimeInfo(self):
        print('開始時間:{}\t結束時間:{}'.format(datetime.fromtimestamp(self.startTime),datetime.fromtimestamp(self.endTime)))