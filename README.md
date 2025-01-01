<a href='https://github.com/Junwu0615/Web-Crawler-FamilyMart-Shop'><img alt='GitHub Views' src='https://views.whatilearened.today/views/github/Junwu0615/Web-Crawler-FamilyMart-Shop.svg'> 
<a href='https://github.com/Junwu0615/Web-Crawler-FamilyMart-Shop'><img alt='GitHub Clones' src='https://img.shields.io/badge/dynamic/json?color=success&label=Clone&query=count_total&url=https://gist.githubusercontent.com/Junwu0615/6d7399737815a21d2dce1ad86f2937c2/raw/Web-Crawler-FamilyMart-Shop_clone.json&logo=github'> <br>
[![](https://img.shields.io/badge/Project-Web_Crawler-blue.svg?style=plastic)](https://github.com/Junwu0615/Crawler-Keywords-And-Use-LineBot) 
[![](https://img.shields.io/badge/Language-Python_3.12.0-blue.svg?style=plastic)](https://www.python.org/) <br>
[![](https://img.shields.io/badge/Package-BeautifulSoup_4.12.2-green.svg?style=plastic)](https://pypi.org/project/beautifulsoup4/) 
[![](https://img.shields.io/badge/Package-Requests_2.31.0-green.svg?style=plastic)](https://pypi.org/project/requests/) 
[![](https://img.shields.io/badge/Package-Pandas_2.1.4-green.svg?style=plastic)](https://pypi.org/project/pandas/) 


## STEP.1　CLONE
```python
git clone https://github.com/Junwu0615/Web-Crawler-FamilyMart-Shop.git
```

## STEP.2　INSTALL PACKAGES
```python
pip install -r requirements.txt
```

## STEP.3　RUN
```python
python Entry.py -h
```
#If you encounter the following problems :
> ModuleNotFoundError: No module named 'python'.<br/>
> ModuleNotFoundError: No module named 'pip'. 
1. 去檢查 C:\Users\xxx\AppData\Local\Programs\Python 是否有檔案。
1. 若無，則去 [Python](https://www.python.org/downloads/) 官網下載並安裝。
1. 接著再次執行該指令；若一樣出現同樣錯誤，去 `系統環境變數` 當中新增 `2` 個路徑 ( Path ) 即可 :
    - C:\Users\ `xxx` \AppData\Local\Programs\Python\ `Python版本`
    - C:\Users\ `xxx` \AppData\Local\Programs\Python\ `Python版本` \Scripts

## STEP.4　EXAMPLE
```python
python Entry.py
```
  - ![family_mart.csv](/sample/00.PNG)

## 抓取資訊來源
- [全家便利商店](https://www.family.com.tw/Marketing/zh/Map)
- [經濟部商工登記公示資料查詢](https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do)