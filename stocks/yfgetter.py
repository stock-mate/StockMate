import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

async def get_per(ticker):
    stock = yf.Ticker(ticker)

    financials = stock.financials
    info = stock.info

    diluted_eps: float

    diluted_eps = financials.loc["Diluted EPS"][0]
    if pd.isna(diluted_eps):
        diluted_eps = financials.loc["Diluted EPS"][1]

    current_price = info["currentPrice"]
    per = round(float(current_price) / float(diluted_eps), 2)

    result_dict = {
        "Diluted_EPS": diluted_eps,
        "Current_Price": current_price,
        "PER": per
    }

    return result_dict


async def get_info(ticker):
    stock = yf.Ticker(ticker)

    info = stock.info

    return info


async def get_price_realtime(ticker):
    stock = yf.Ticker(ticker)

    data = stock.history(period="1d", interval="1m")

    return data["Close"]


async def get_price_range(ticker, start, end):
    stock = yf.Ticker(ticker)

    data = stock.history(start=start, end=end)

    return data["Close"]


async def find_ticker_by_name(company_name):

    try:
        # Selenium 드라이버 설정
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # excutable_path는 chromdriver가 위치한 경로를 적어주면 된다. code와 동일한 경로일 경우 아래처럼 'chromdriver' 만 적어주거나 아예 excutable_path 자체가 없어도 된다. 이해를 위해 써놓았을 뿐.
        # ex) driver = webdriver.Chrome(chrome_options=chrome_options)
        driver = webdriver.Chrome()
        # Yahoo Finance에서 종목명으로 검색하는 URL 구성
        search_url = f"https://finance.yahoo.com/lookup/?s={company_name}"

        # Yahoo Finance 검색 페이지로 이동
        driver.get(search_url)

        # 페이지 로딩 대기
        driver.implicitly_wait(10)  # 필요에 따라 시간 조정

        # 페이지의 HTML 소스 가져오기
        html = driver.page_source

        # BeautifulSoup 객체 생성
        soup = BeautifulSoup(html, 'html.parser')

        ticker: str = ""

        # 'data-symbol' 속성을 찾습니다.
        a_tag = soup.find('a', class_='Fw(b)', attrs={'data-symbol': True})
        # 'data-symbol' 속성의 값을 추출합니다.
        ticker = a_tag['data-symbol'] if a_tag else 'Not Found'

        driver.close()

        return ticker
    except AttributeError:
        # 검색 결과가 없거나 구조가 예상과 다를 때
        return "Ticker not found or search page structure has changed."