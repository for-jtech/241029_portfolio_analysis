import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import plotly.graph_objs as go


def portfolio_analysis(tickers, weights, start_date=None):
    # 종목별로 역사적 종가 데이터를 가져옴
    price_data = pd.DataFrame()
    for ticker in tickers:
        df = fdr.DataReader(ticker)
        price_data[ticker] = df["Close"]

    # 결측값 제거 (자산 간 데이터 정렬)
    price_data.dropna(inplace=True)

    # start_date가 지정되었을 경우 해당 날짜부터 데이터 필터링
    if start_date:
        price_data = price_data[price_data.index >= pd.to_datetime(start_date)]

    # 분석 기간 계산 및 출력
    start_date_formatted = price_data.index.min().strftime("%Y-%m")
    end_date_formatted = price_data.index.max().strftime("%Y-%m")
    analysis_period = f"{start_date_formatted} ~ {end_date_formatted}"
    print(f"Analysis Period: {analysis_period}")

    # 월별 데이터로 리샘플링하여 월말 가격으로 설정
    monthly_prices = price_data.resample("M").last()

    # 각 자산의 월간 수익률 계산
    monthly_returns = monthly_prices.pct_change().dropna()

    # 초기 자본 설정 ($1로 가정)
    initial_capital = 1
    portfolio_values = pd.Series(index=monthly_returns.index)
    portfolio_values.iloc[0] = initial_capital

    # 월별 리밸런싱 수행
    for i in range(1, len(monthly_returns.index)):
        prev_date = monthly_returns.index[i - 1]
        date = monthly_returns.index[i]

        # 이전 달 포트폴리오 가치를 기준으로 목표 비율에 맞춰 리밸런싱
        prev_total_value = portfolio_values[prev_date]
        holdings = prev_total_value * weights

        # 현재 월 수익률 적용
        current_returns = monthly_returns.iloc[i]
        holdings = holdings * (1 + current_returns)

        # 새로운 총 포트폴리오 가치를 저장
        portfolio_values[date] = holdings.sum()

    # CAGR 계산
    n_years = (portfolio_values.index[-1] - portfolio_values.index[0]).days / 365.25
    ending_value = portfolio_values.iloc[-1]
    CAGR = (ending_value / initial_capital) ** (1 / n_years) - 1

    # MDD 계산
    rolling_max = portfolio_values.cummax()
    drawdown = (portfolio_values - rolling_max) / rolling_max
    MDD = drawdown.min()

    # 결과 출력
    print(f"CAGR: {CAGR:.2%}")
    print(f"MDD: {MDD:.2%}")

    # Plotly를 사용한 포트폴리오 가치 시각화
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=portfolio_values.index,
            y=portfolio_values,
            mode="lines",
            name="Portfolio Value",
        )
    )
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
    )
    fig.show()

    # MDD 시각화
    fig_dd = go.Figure()
    fig_dd.add_trace(
        go.Scatter(x=drawdown.index, y=drawdown, mode="lines", name="Drawdown")
    )
    fig_dd.update_layout(
        title="Maximum Drawdown Over Time",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        template="plotly_white",
    )
    fig_dd.show()


# 사용 예시:
start_date = "2022-01"  # 분석 시작 월을 지정합니다.

# 종목 코드와 비중을 입력합니다.
tickers = [
    "379800",
    "308620",
    "411060",
]  # 예: KODEX 미국S&P500TR, KODEX 미국10년국채선물, ACE KRX금현물
weights = np.array([0.5, 0.3, 0.2])  # 각 자산의 비중: 50%, 30%, 20%

portfolio_analysis(tickers, weights, start_date)

tickers = ["379800"]
weights = np.array([1])

portfolio_analysis(tickers, weights, start_date)
