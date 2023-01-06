import os
import csv
from matplotlib import pyplot as plt
from collections import defaultdict
import pandas as pd
from datetime import datetime
import time

class StatisticsAndDraw:

    def __init__(self,CondictionsRoute:str,RowDataRoute:str):
        self.Condictions={}
        self.stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.LoadCondictions(CondictionsRoute)
        self.LoadRowData(RowDataRoute)

    def LoadCondictions(self,Route:str)->list:
        with open(Route,'r') as f:
            rows = csv.reader(f)
            for row in rows:
                if row:
                    if len(row)>1:
                        self.Condictions[row[0]] = sorted(list(map(float,[_ for _ in row[1:] if _])))
                    else:
                        print('測試項{}區間設定錯誤已自動忽略'.format(row[0]))
        return self.Condictions.keys()

    def LoadRowData(self,Route:str)->dict:
        rowdata = os.listdir(Route)
        for d in rowdata:
            self.mkdirForOutput(d[:-4])
            StartTime=time.time()
            IndexInfo={}
            dataset=defaultdict(list)
            flag=False
            checknull=False
            check=[]
            with open(os.path.join(Route,d),'r') as f:
                rows = csv.reader(f)
                for row in rows:
                    if row:
                        if checknull:
                            for item in self.Condictions.keys():
                                if not row[IndexInfo[item]]:
                                    check.append(item)
                            for todel in check:
                                self.Condictions.pop(todel)
                                print('條件{}紀錄到為空白,已從Condictions中刪除'.format(todel))
                            check=[]
                            checknull = False
                        if row[0] == 'PosX' or row[0] == 'TEST':
                            row = [_.strip() for _ in row]
                            for item in self.Condictions.keys():
                                try:
                                    IndexInfo[item]=row.index(item)
                                except:
                                    print('測試項{ITEM}不在RowData內,已自動忽略'.format(ITEM=item))
                                    check.append(item)
                            flag = True
                            checknull=True
                            for todel in check:
                                self.Condictions.pop(todel)
                                print('條件{}已從Condictions中刪除'.format(todel))
                            check=[]
                        elif flag:
                            for item in self.Condictions.keys():
                                dataset[item].append(float(row[IndexInfo[item]]))
            #self.BigData[d[:-4]] = dataset
            self.CutEverything(d[:-4],dataset)
            EndTime=time.time()
            print('載入片號{}完成\t使用時間{:.3f}秒'.format(d,EndTime-StartTime))

    def mkdirForOutput(self,WaferId):
        if not os.path.isdir('FigureOutput/{}'.format(self.stamp)):
            os.mkdir('FigureOutput/{}'.format(self.stamp))
        os.mkdir('FigureOutput/{}/{}'.format(self.stamp,WaferId))

    def CutEverything(self,WaferId,thedata):
        for item , rowdata in thedata.items():
            print('現正統計{WAFERID}測試項{ITEM}'.format(WAFERID=WaferId,ITEM=item))
            title = 'Wafer ID:{} Test Item:{}'.format(WaferId,item)
            label = list(map(str,self.Condictions[item][:-1]))
            label[0] = '0.0'
            label= ['>'+_ for _ in label]
            seg = pd.cut(rowdata,self.Condictions[item],labels=label)
            counts = pd.value_counts(seg,sort=False)
            plt.figure(figsize=(12,10))
            plt.title(title)
            b = plt.bar(counts.index.astype(str),counts,width=0.4)
            plt.bar_label(b,counts)
            plt.savefig('FigureOutput/{}/{}/{}.png'.format(self.stamp,WaferId,item))
            #plt.show()
            plt.close()
        print('片號:{WAFERID}完成'.format(WAFERID=WaferId))
