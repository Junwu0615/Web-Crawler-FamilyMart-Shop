# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-01-01
"""
import unicodedata
import pandas as pd
import os, json, requests, time, copy

from tqdm import tqdm
from urllib import parse
from bs4 import BeautifulSoup

class FamilyMart:
    def __init__(self):
        self.path = './sample/'
        self.file_name = 'family_mart'
        self.source_base = 'https://api.map.com.tw/net/familyShop.aspx?search'
        self.session = requests.Session()
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                        'referer': 'https://www.family.com.tw/Marketing/zh/Map',
                        'accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5',
                        'cookie': '_ga=GA1.1.1898593150.1735713970; _ga_KBLNFSSS3J=GS1.1.1735713970.1.1.1735720041.59.0.0; RT="z=1&dm=www.family.com.tw&si=f3aed557-c445-4991-abd8-9a4df2f7b937&ss=m5dja67b&sl=14&tt=a6v&obo=q&rl=1&nu=40mgb2cg&cl=3mr5f&ld=3njyf&r=u9sh6k5&ul=3njyg"',
                        }

    @staticmethod
    def check_folder(path: str):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    @staticmethod
    def full_to_half(text: str) -> str:
        """ 將全形字符轉換為半形字符 """
        result = []
        for char in text:
            # 使用 unicodedata 獲取字符類型
            if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
                # 將全形字符轉為半形
                result.append(unicodedata.normalize('NFKC', char))
            else:
                # 非全形字符直接保留
                result.append(char)
        return ''.join(result)

    def get_key(self) -> str:
        url = 'https://www.family.com.tw/Marketing/StoreMap/?v=1'
        res = self.session.get(url, headers=self.headers)
        idx = res.text.find('key=')
        key = res.text[idx + 4:idx + 200].split('"')[0]
        return key

    def get_city(self) -> list:
        city_list = []
        url = 'https://api.map.com.tw/js/API_JS/Geocoding.js'
        res = self.session.get(url, headers=self.headers)
        idx = res.text.find('function')
        trans = res.text[:idx]
        todo = [i for i in trans.split(';') if '\\' in i and '[0]' in i]
        for i in todo:
            city = i.split('=')[-1][1:-1]
            city_list += [city.encode('utf-8').decode('unicode_escape')]
        return city_list

    def get_area(self, key: str, city: str) -> list:
        url = (f'{self.source_base}'
               'Type=ShowTownList&'
               'type=&'
               f'city={city}&'
               'fun=storeTownList&'
               f'key={key}')
        res = self.session.get(url, headers=self.headers)
        loader = json.loads(res.text.replace('storeTownList(', '')[:-1])
        loader = [i['town'] for i in loader]
        return loader

    def trans_area_name(self, text) -> str:
        name_dict = {
            '台北市': '臺北市',
            '台中市': '臺中市',
            '台東市': '臺東市',
            '台南市': '臺南市',
        }
        if text in name_dict:
            return name_dict[text]
        else:
            return text

    def get_detail(self, city_list: list) -> dict:
        data_dict = {}
        try:
            for city in tqdm(city_list, position=0):
                key = self.get_key()
                area_list = self.get_area(key, city)
                for area in area_list:
                    search_type = 'ShopList'
                    fun = 'showStoreList'
                    road = ''
                    url = (f'{self.source_base}'
                           f'Type={search_type}&'
                           f'type=&'
                           f'city={parse.quote(city)}&'
                           f'area={parse.quote(area)}&'
                           f'road={parse.quote(road)}&'
                           f'fun={fun}&'
                           f'key={key}')
                    res = self.session.get(url, headers=self.headers)
                    loader = json.loads(res.text.replace('showStoreList(','')[:-1])
                    for i in loader:
                        data_key = i['NAME']
                        adr = FamilyMart.full_to_half(i['addr'])
                        adr = self.trans_area_name(adr[:3])+ adr[3:]
                        data_dict[data_key] = {
                            '直營店': '',
                            '加盟店': '',
                            '縣市': adr[:3],
                            '地區': area,
                            '店鋪名稱': self.trans_symbol(data_key, ['全家', '店']),
                            '店鋪號': i['pkey'],
                            '服務編號': int(i['SERID']),
                            '地址': adr,
                            '電話-1': i['POSTel'],
                            '電話-2': i['TEL'],
                        }
        except Exception as e:
            print(e)
        finally:
            return data_dict

    def trans_symbol(self, target: str, symbol_list: list) -> str:
        for symbol in symbol_list:
            target = target.replace(symbol, '')
        return target

    def gov_search_sub(self) -> dict:
        data_dict = {}
        self.headers['referer'] = 'https://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do'
        self.headers['cookie'] = 'isAlive=all; cityScope=; busiItemMain=; busiItemSub=; vTable=false; type=cmpyType%2CbrCmpyType%2CbusmType%2CfactType%2ClmtdType%2C; infoType=D; qryCond=%25u5168%25u5BB6%25u4FBF%25u5229%25u5546%25u5E97%25u80A1%25u4EFD%25u6709%25u9650%25u516C%25u53F8%25u57FA%25u9686%25u4EC1%25u4E09; surveytimes=43; JSESSIONID=DF31EAF3D829D32A942C32521D1FC062; _ga_LYEDNVWP49=GS1.1.1716629958.1.1.1716630353.0.0.0; __Secure-YIoDyjvsmH6aGnMzijXn5g__=v14g8+JQ__CKt; _gid=GA1.3.312906813.1735724239; _ga_0LXPDEZR5N=GS1.1.1735724525.1.0.1735724525.0.0.0; _ga=GA1.3.2075010471.1716629959; JSESSIONID=9730DF47C8F8F93B05C0009680A7450C; _gat=1; _ga_63JSK5083P=GS1.3.1735726637.20.1.1735728092.0.0.0'
        try:
            page = 1
            schedule = tqdm(position=0, desc=f'工商登記 全家 [分工司資料] 搜索頁數 ')
            while page > 0:
                try:
                    url = 'https://findbiz.nat.gov.tw/fts/query/QueryCmpyDetail/queryCmpyDetail.do'
                    payload = {
                        'banNo': '23060248', # 全家統編
                        'brBanNo':  '',
                        'banKey':  '',
                        'estbId':  '',
                        'objectId':  '',
                        'CPage': page, # 換頁
                        'brCmpyPage': 'Y',
                        'CPageFactory':  '',
                        'factoryPage':  '',
                        'eng': 'false',
                        'disj': '1749EF421F8ED2345189CF97309825DD',
                        'fhl': 'zh_TW',
                        'CPageHistory':  '',
                        'historyPage':  '',
                        'chgAppDate':  '',
                        'translateAddress':  '',
                        'regUnitCode':  '',
                    }
                    res = self.session.post(url, data=payload, headers=self.headers)
                    soup = BeautifulSoup(res.text, 'html.parser')

                    temp = []
                    div = soup.find_all('div', {'class', 'tab-pane'})[3]
                    for td in div.find_all('td'):
                        trans = self.trans_symbol(td.text, ['\n', '\r', '\t', ''])
                        if '頁' not in trans:
                            temp += [trans]

                    page += 1
                    if '依您的查詢條件，查無符合結果。' in temp:
                        break
                    else:
                        # 收集分公司統編 用統編進去各細節
                        count = 0
                        for i in range(int(len(temp)/6)):
                            key = temp[count]
                            data_dict[key] = {
                                '序號': temp[count],
                                '統編': temp[count + 1],
                                '分公司名稱': temp[count + 2],
                                '登記現況': temp[count + 3],
                                '核准設立日期': temp[count + 4],
                                '最後變更日期': temp[count + 5],
                            }
                            count = count + 6
                    schedule.update(1)
                    time.sleep(2)
                except Exception as e:
                    print(e)
        finally:
            return data_dict

    def gov_search_detail(self, loader: dict) -> dict:
        self.headers['referer'] = 'https://findbiz.nat.gov.tw/fts/query/QueryCmpyDetail/queryCmpyDetail.do'
        self.headers['cookie'] = 'isAlive=all; cityScope=; busiItemMain=; busiItemSub=; vTable=false; type=cmpyType%2CbrCmpyType%2CbusmType%2CfactType%2ClmtdType%2C; infoType=D; qryCond=%25u5168%25u5BB6%25u4FBF%25u5229%25u5546%25u5E97%25u80A1%25u4EFD%25u6709%25u9650%25u516C%25u53F8%25u57FA%25u9686%25u4EC1%25u4E09; surveytimes=43; JSESSIONID=DF31EAF3D829D32A942C32521D1FC062; _ga_LYEDNVWP49=GS1.1.1716629958.1.1.1716630353.0.0.0; __Secure-YIoDyjvsmH6aGnMzijXn5g__=v14g8+JQ__CKt; _gid=GA1.3.312906813.1735724239; _ga_0LXPDEZR5N=GS1.1.1735724525.1.0.1735724525.0.0.0; _ga=GA1.3.2075010471.1716629959; JSESSIONID=9730DF47C8F8F93B05C0009680A7450C; _gat=1; _ga_63JSK5083P=GS1.3.1735726637.20.1.1735728092.0.0.0'
        try:
            schedule = tqdm(total=len(loader), position=0, desc=f'工商登記 全家 [分工司資料] 細節搜索 ')
            for k,v in copy.deepcopy(loader).items():
                try:
                    if v['登記現況'] in ['廢止', '撤銷']:
                        del loader[k]
                    else:
                        url = 'https://findbiz.nat.gov.tw/fts/query/QueryBrCmpyDetail/queryBrCmpyDetail.do'
                        payload = {
                            'banNo': '',
                            'brBanNo':  v['統編'], # 子公司統編
                            'banKey':  '',
                            'estbId':  '',
                            'objectId':  '',
                            'CPage': '',
                            'brCmpyPage': 'N',
                            'CPageFactory':  '',
                            'factoryPage':  '',
                            'eng': 'false',
                            'disj': '1749EF421F8ED2345189CF97309825DD',
                            'fhl': 'zh_TW',
                            'CPageHistory':  '',
                            'historyPage':  '',
                            'chgAppDate':  '',
                            'translateAddress':  '',
                            'regUnitCode':  '',
                        }
                        res = self.session.post(url, data=payload, headers=self.headers)
                        soup = BeautifulSoup(res.text, 'html.parser')

                        temp = []
                        div = soup.find_all('div', {'class', 'table-responsive'})[0]
                        for td in div.find_all('td'):
                            # symbol_list = ['\n', '\r', '\t', ' ', '\xa0', '關閉', '已了解，開始查詢']
                            symbol_list = ['\n', '\r', '\t', ' ', '\xa0', '已了解，開始查詢']
                            trans = self.trans_symbol(td.text, symbol_list)
                            # if '頁' not in trans and 'span' not in str(td):
                            temp += [trans]

                        temp = [i for i in temp if i != '']
                        count = 0
                        for i in range(int(len(temp) / 2)):
                            # print(temp[count], temp[count + 1])
                            if temp[count] == '分公司經理姓名':
                                loader[k][temp[count]] = temp[count + 1]
                            elif temp[count] == '分公司所在地':
                                loader[k][temp[count]] = self.trans_symbol(temp[count + 1], ['電子地圖'])

                            count = count + 2

                        print(f'\n{loader[k]}')
                        time.sleep(2)

                    schedule.update(1)

                except Exception as e:
                    print(e)
        finally:
            return loader

    def preprocess(self):
        if not os.path.exists(self.path):
            FamilyMart.check_folder(self.path)

        origin = self.path + self.file_name + '.json'
        if not os.path.exists(origin):
            city_list = self.get_city()
            data_dict = self.get_detail(city_list)
            json.dump(data_dict, open(origin, 'w', encoding='utf-8'), ensure_ascii=False)

        origin_gov = self.path + self.file_name + '_gov.json'
        if not os.path.exists(origin_gov):
            data_dict = self.gov_search_sub()
            json.dump(data_dict, open(origin_gov, 'w', encoding='utf-8'), ensure_ascii=False)

        gov = self.path + self.file_name + '_gov_detail.json'
        if not os.path.exists(gov):
            origin_gov = [json.loads(i) for i in open(origin_gov, 'r')][0]
            data_dict = self.gov_search_detail(origin_gov)
            json.dump(data_dict, open(gov, 'w', encoding='utf-8'), ensure_ascii=False)

        file = self.path + self.file_name + '.csv'
        if not os.path.exists(file):
            origin = [json.loads(i) for i in open(origin, 'r')][0]
            gov = [json.loads(i) for i in open(gov, 'r')][0]
            del_list = [v['分公司所在地'] for k, v in gov.items() if '分公司所在地' in v]
            # print(f'原先: {len(origin)}')

            for k, v in copy.deepcopy(origin).items():
                if v['地址'] in del_list:
                    origin[k]['直營店'] = 'O'
                else:
                    origin[k]['加盟店'] = 'O'

            # print(f'調整: {len(origin)}')

            df = pd.DataFrame(origin).T
            df.to_csv(file, encoding='utf-8-sig', index=True)

    def main(self):
        self.preprocess()