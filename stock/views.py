# myapp/views.py
from django.shortcuts import render
import pandas as pd

import datetime
import FinanceDataReader as fdr

from datetime import datetime, timedelta
import requests

def index(request):
    # 상위 10개

    # 날짜 설정
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # KOSPI 주식 목록 가져오기
    all_stocks = fdr.StockListing('KOSPI')

    # 상위 10개 종목 선택 (등락률 기준)
    top_10_ChagesRatio = all_stocks.sort_values(by='ChagesRatio', ascending=False).head(10)

    # 하위 10개 종목 선택 (등락률 기준)
    row_10_ChagesRatio = all_stocks.sort_values(by='ChagesRatio', ascending=True).head(10)

    # 상위 10개 종목 선택 (시가총액 기준)
    top_10_Marcap = all_stocks.sort_values(by='Marcap', ascending=False).head(10)
    
    # 환율정보 가져오기 (open API)
    # API 인증키 : DPModF9KEpqknLkTe9GxHGp8k1me31CC
    url = 'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey=DPModF9KEpqknLkTe9GxHGp8k1me31CC&searchdate=20240701&data=AP01'
    req = requests.get(url, verify=False)
    # 받은 정보(req)에서 json 데이터를 가져 옴
    json_data = req.json()
    # json 데이터를 DataFrame에 넣기
    df = pd.DataFrame(json_data)
    # 유로 정보
    eur = df.iloc[8]
    # 위안화 정보
    cnh = df.iloc[6]
    # 엔 정보
    jpy = df.iloc[12]
    # 달러 정보
    usd = df.iloc[22]

    # 등락 상위 10개 종목 주식 데이터 리스트로 준비
    top_10_stocks = []
    for i in range(len(top_10_ChagesRatio)):
        stock_data = {
            'code': top_10_ChagesRatio.iloc[i].Code,
            'name': top_10_ChagesRatio.iloc[i].Name,
            'close': top_10_ChagesRatio.iloc[i].Close,
            'change': top_10_ChagesRatio.iloc[i].Changes,
            'chagesRatio':top_10_ChagesRatio.iloc[i].ChagesRatio,
        }
        top_10_stocks.append(stock_data)

    # 등락 하위 10개 종목 주식 데이터 리스트로 준비
    row_10_stocks = []
    for i in range(len(row_10_ChagesRatio)):
        stock_data = {
            'code': row_10_ChagesRatio.iloc[i].Code,
            'name': row_10_ChagesRatio.iloc[i].Name,
            'close': row_10_ChagesRatio.iloc[i].Close,
            'change': row_10_ChagesRatio.iloc[i].Changes,
            'chagesRatio':row_10_ChagesRatio.iloc[i].ChagesRatio,
        }
        row_10_stocks.append(stock_data)

    # 상위 10개 종목 주식 데이터 리스트로 준비
    top_10_tot = []
    for i in range(len(top_10_Marcap)):
        stock_data = {
            'code': top_10_Marcap.iloc[i].Code,
            'name': top_10_Marcap.iloc[i].Name,
            'close': top_10_Marcap.iloc[i].Close,
            'change': top_10_Marcap.iloc[i].Changes,
            'chagesRatio':top_10_Marcap.iloc[i].ChagesRatio,
            'marcap':top_10_Marcap.iloc[i].Marcap,
        }
        top_10_tot.append(stock_data)

    context = {
        'top_10_stocks': top_10_stocks,
        'row_10_stocks': row_10_stocks,
        'top_10_tot': top_10_tot,
        'eur' : eur,
        'cnh' : cnh,
        'jpy' : jpy,
        'usd' : usd,
    }

    return render(request, 'index.html', context)

def list(request):
    # 날짜 설정
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # KOSPI 주식 목록 가져오기
    all_stocks = fdr.StockListing('KOSPI')

    '''
    # 모든 종목의 데이터를 가져오기
    stock_symbols = all_stocks['Code'].tolist()

    # 어제와 오늘의 데이터 불러오기
    data_today = fdr.DataReader(stock_symbols, start=today, end=today)
    data_yesterday = fdr.DataReader(stock_symbols, start=yesterday, end=yesterday)    

    # 어제와 오늘의 데이터 병합 (같은 종목끼리 병합)
    merged_data = pd.merge(data_today, data_yesterday, on='Code', suffixes=('_today', '_yesterday'))    

    # 등락률 계산
    merged_data['Change'] = merged_data['Close_today'] - merged_data['Close_yesterday']
    merged_data['ChangePercent'] = (merged_data['Change'] / merged_data['Close_yesterday']) * 100
    
    # NaN 값 제거
    merged_data = merged_data.dropna()
    '''
    
    # 상위 10개 종목 선택 (등락률 기준)
    top_10 = all_stocks.sort_values(by='ChagesRatio', ascending=False).head(10)

    # 주식 데이터 리스트로 준비
    stocks = []
    for i in range(len(top_10)):
        stock_data = {
            'code': top_10.iloc[i].Code,
            'name': top_10.iloc[i].Name,
            'close': top_10.iloc[i].Close,
            'change': top_10.iloc[i].Changes,
            'chagesRatio':top_10.iloc[i].ChagesRatio,
        }
        stocks.append(stock_data)
    # 템플릿에 데이터 전달
    return render(request, 'stock/list.html', {'stocks': stocks})

def predict(request) :
    if request.method != 'POST':
        return render(request, 'stock/predict.html')
