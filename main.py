import FinanceDataReader as fdr
import pandas as pd
import numpy as np


def portfolio_analysis(tickers, weights, start_date=None):
    # Fetch historical closing prices for each ticker
    price_data = pd.DataFrame()
    for ticker in tickers:
        df = fdr.DataReader(ticker)
        price_data[ticker] = df["Close"]

    # Drop rows with missing values to ensure data alignment across assets
    price_data.dropna(inplace=True)

    # If start_date is specified, filter data from that date
    if start_date:
        price_data = price_data[price_data.index >= pd.to_datetime(start_date)]

    # Calculate the analysis period
    start_date_formatted = price_data.index.min().strftime("%Y-%m")
    end_date_formatted = price_data.index.max().strftime("%Y-%m")
    analysis_period = f"{start_date_formatted} ~ {end_date_formatted}"
    print(f"Analysis Period: {analysis_period}")

    # Resample the data to monthly frequency, taking the last price of each month
    monthly_prices = price_data.resample("M").last()

    # Calculate monthly returns for each asset
    monthly_returns = monthly_prices.pct_change().dropna()

    # Initialize the portfolio with an initial capital of $1
    initial_capital = 1
    portfolio_values = pd.Series(index=monthly_returns.index)
    portfolio_values.iloc[0] = initial_capital

    # Perform monthly rebalancing of the portfolio
    for i in range(1, len(monthly_returns.index)):
        prev_date = monthly_returns.index[i - 1]
        date = monthly_returns.index[i]

        # Calculate portfolio value at the previous month
        prev_total_value = portfolio_values[prev_date]

        # Rebalance holdings to match the target weights
        holdings = prev_total_value * weights

        # Apply the current month's returns to the holdings
        current_returns = monthly_returns.iloc[i]
        holdings = holdings * (1 + current_returns)

        # Calculate new total portfolio value and store it
        portfolio_values[date] = holdings.sum()

    # CAGR calculation
    n_years = (portfolio_values.index[-1] - portfolio_values.index[0]).days / 365.25
    ending_value = portfolio_values.iloc[-1]
    CAGR = (ending_value / initial_capital) ** (1 / n_years) - 1

    # MDD calculation
    rolling_max = portfolio_values.cummax()
    drawdown = (portfolio_values - rolling_max) / rolling_max
    MDD = drawdown.min()

    # Display results
    print(f"CAGR: {CAGR:.2%}")
    print(f"MDD: {MDD:.2%}")


# Example usage:
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
