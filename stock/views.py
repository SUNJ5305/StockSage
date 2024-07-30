# myapp/views.py
import base64
import io

from django.shortcuts import render
import pandas as pd

import datetime
import FinanceDataReader as fdr

from datetime import datetime, timedelta
import requests
from matplotlib import pyplot as plt
import yfinance as yf


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

def info(request) :
    ticker = request.GET.get('ticker')
    if ticker:
        try:
            # KOSPI 주식을 위해 ".KS" 추가
            kospi_ticker = f"{ticker}.KS"
            stock = yf.Ticker(kospi_ticker)
            hist = stock.history(period="1mo")  # 1달 데이터

            if hist.empty:
                return render(request, 'stock/info.html', {'error': '데이터를 가져올 수 없습니다.'})

            # 그래프 생성
            plt.figure(figsize=(10,5))
            plt.plot(hist.index, hist['Close'])
            plt.title(f"{ticker} 주가")
            plt.xlabel('날짜')
            plt.ylabel('종가')
            plt.xticks(rotation=45)
            plt.tight_layout()

            # 그래프를 이미지로 변환
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')

            plt.close()  # 메모리 누수 방지를 위해 plt 객체 닫기

            # 주식 정보 가져오기
            info = stock.info
            company_name = info.get('longName', 'N/A')
            current_price = info.get('currentPrice', 'N/A')
            previous_close = info.get('previousClose', 'N/A')

            return render(request, 'stock/info.html', {
                'graphic': graphic,
                'ticker': ticker,
                'company_name': company_name,
                'current_price': current_price,
                'previous_close': previous_close
            })

        except Exception as e:
            return render(request, 'stock/info.html', {'error': f'오류 발생: {str(e)}'})
    else:
        return render(request, 'stock/info.html')

