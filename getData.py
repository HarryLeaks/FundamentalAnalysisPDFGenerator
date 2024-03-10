import requests
import pandas as pd
import yfinance as yf
from ta import add_all_ta_features
import sys

def fetch_and_save_data(function, symbol, file_name):
    api_key = "API_KEY"
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    
    if function == 'TIME_SERIES_DAILY':
        time_series_data = data.get("Time Series (Daily)")
        if time_series_data:
            df = pd.DataFrame.from_dict(time_series_data, orient='index')
            df.to_csv(file_name, index_label='Date')
        else:
            print("Daily data not found.")
    else:
        if 'AnnualReports' in data:
            data = data['AnnualReports']
        elif 'quarterlyReports' in data:
            data = data['quarterlyReports']
        else:
            print("Data not found.")
            return
        
        df = pd.DataFrame.from_dict(data)
        df.to_csv(file_name, index=False)

def fetch_and_save_ohlc(symbol, file_name):
    try:
        df = yf.download(symbol, start="1900-01-01", end="2100-01-01")
        df.to_csv(file_name)
        print(f"OHLCV data for {symbol} saved to {file_name}")
    except Exception as e:
        print(f"Failed to fetch OHLCV data for {symbol}: {e}")

def add_technical_indicators(file_name):
    try:
        df = pd.read_csv(file_name)
        indicator_columns = [col for col in df.columns if 'trend_' in col or 'momentum_' in col or 'volatility_' in col]
        df.drop(columns=indicator_columns, inplace=True, errors='ignore')
        df = add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume")
        new_file_name = f'indicators_{file_name}'
        df.to_csv(new_file_name, index=False)
        print(f"Technical indicators added to {file_name} and saved to {new_file_name}")
    except Exception as e:
        print(f"Failed to add technical indicators to {file_name}: {e}")

def calculate_financial_ratios(balance_sheet_file, cash_flow_file, income_statement_file, indicators_file, output_file):
    balance_sheet = pd.read_csv(balance_sheet_file)
    cash_flow = pd.read_csv(cash_flow_file)
    income_statement = pd.read_csv(income_statement_file)
    indicators = pd.read_csv(indicators_file)

    balance_sheet.replace("None", None, inplace=True)
    cash_flow.replace("None", None, inplace=True)
    income_statement.replace("None", None, inplace=True)
    indicators.replace("None", None, inplace=True)

    balance_sheet.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)
    cash_flow.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)
    income_statement.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)

    balance_sheet.fillna(0, inplace=True)
    cash_flow.fillna(0, inplace=True)
    income_statement.fillna(0, inplace=True)
    indicators.fillna(0, inplace=True)

    merged_data = pd.merge(income_statement, cash_flow, on='Date')
    merged_data = pd.merge(merged_data, balance_sheet, on='Date')
    merged_data = pd.merge(merged_data, indicators, on='Date')

    merged_data['dividendPayoutCommonStock'] = pd.to_numeric(merged_data['dividendPayoutCommonStock'], errors='coerce')
    merged_data['paymentsForRepurchaseOfCommonStock'] = pd.to_numeric(merged_data['paymentsForRepurchaseOfCommonStock'], errors='coerce')
    merged_data['totalRevenue'] = pd.to_numeric(merged_data['totalRevenue'], errors='coerce')
    merged_data['commonStockSharesOutstanding'] = pd.to_numeric(merged_data['commonStockSharesOutstanding'], errors='coerce')
    merged_data['Adj Close'] = pd.to_numeric(merged_data['Adj Close'], errors='coerce')
    merged_data['ebitda'] = pd.to_numeric(merged_data['ebitda'], errors='coerce')
    merged_data['totalLiabilities'] = pd.to_numeric(merged_data['totalLiabilities'], errors='coerce')
    merged_data['cashAndCashEquivalentsAtCarryingValue'] = pd.to_numeric(merged_data['cashAndCashEquivalentsAtCarryingValue'], errors='coerce')
    merged_data['totalAssets'] = pd.to_numeric(merged_data['totalAssets'], errors='coerce')
    merged_data['netIncome_y'] = pd.to_numeric(merged_data['netIncome_y'], errors='coerce')
    merged_data['totalShareholderEquity'] = pd.to_numeric(merged_data['totalShareholderEquity'], errors='coerce')
    merged_data['ebit'] = pd.to_numeric(merged_data['ebit'], errors='coerce')
    merged_data['operatingCashflow'] = pd.to_numeric(merged_data['operatingCashflow'], errors='coerce')
    merged_data['capitalExpenditures'] = pd.to_numeric(merged_data['capitalExpenditures'], errors='coerce')
    merged_data['totalCurrentLiabilities'] = pd.to_numeric(merged_data['totalCurrentLiabilities'], errors='coerce')
    merged_data['totalCurrentAssets'] = pd.to_numeric(merged_data['totalCurrentAssets'], errors='coerce')


    merged_data['Date'] = pd.to_datetime(merged_data['Date'])

    market_cap = merged_data['commonStockSharesOutstanding'] * merged_data['Adj Close']
    price_to_sales_ratio = market_cap / merged_data['totalRevenue']
    ebitda = merged_data['ebitda']
    net_debt = merged_data['totalLiabilities'] - merged_data['cashAndCashEquivalentsAtCarryingValue']
    enterprise_value = market_cap + net_debt
    ev_to_ebitda = enterprise_value / ebitda
    ebitda_margin = (merged_data['ebitda'] / merged_data['totalRevenue']) * 100
    ebit_margin = (merged_data['ebit'] / merged_data['totalRevenue']) * 100
    per = market_cap / merged_data['netIncome_y']
    pbv = market_cap / merged_data['totalAssets']
    roe = (merged_data['netIncome_y'] / merged_data['totalShareholderEquity']) * 100
    roic = (merged_data['ebit'] / (merged_data['totalAssets'] - merged_data['totalLiabilities'])) * 100
    net_debt_to_ebitda = net_debt / ebitda
    debt_to_equity = merged_data['totalLiabilities'] / merged_data['totalShareholderEquity']
    dividend_yield = merged_data['dividendPayoutCommonStock'] / market_cap
    roa = merged_data['netIncome_y'] / merged_data['totalAssets']
    shares_buyback_ratio = merged_data['paymentsForRepurchaseOfCommonStock'] / merged_data['netIncome_y']
    free_cash_flow = merged_data['operatingCashflow'] - merged_data['capitalExpenditures']
    free_cash_flow_margin = (free_cash_flow / merged_data['totalRevenue']) * 100

    # Additional Ratios
    net_margin = (merged_data['netIncome_y'] / merged_data['totalRevenue']) * 100
    current_ratio = merged_data['totalCurrentAssets'] / merged_data['totalCurrentLiabilities']
    quick_ratio = (merged_data['totalCurrentAssets'] - merged_data['cashAndCashEquivalentsAtCarryingValue']) / merged_data['totalCurrentLiabilities']
    cash_ratio = merged_data['cashAndCashEquivalentsAtCarryingValue'] / merged_data['totalCurrentLiabilities']

    # Create a new dataframe for financial ratios
    financial_ratios = pd.DataFrame({
        'Date': merged_data['Date'],
        'Market Cap': market_cap,
        'Price to Sales Ratio': price_to_sales_ratio,
        'EBITDA': ebitda,
        'Net Debt': net_debt,
        'Enterprise Value': enterprise_value,
        'EV to EBITDA': ev_to_ebitda,
        'EBITDA Margin': ebitda_margin,
        'EBIT Margin': ebit_margin,
        'PER': per,
        'PBV': pbv,
        'ROE': roe,
        'ROIC': roic,
        'Net Debt to EBITDA': net_debt_to_ebitda,
        'Debt to Equity': debt_to_equity,
        'Dividend Yield': dividend_yield,
        'ROA': roa,
        'Shares Buyback Ratio': shares_buyback_ratio,
        'Free Cash Flow Margin': free_cash_flow_margin,
        'Net Margin': net_margin,
        'Current Ratio': current_ratio,
        'Quick Ratio': quick_ratio,
        'Cash Ratio': cash_ratio
    })

    financial_ratios.to_csv(output_file, index=False)

def merge_and_filter_data(balance_sheet_file, financial_metrics_file, cash_flow_file, income_statement_file, indicators_ohlc_file, output_file):
    balance_sheet = pd.read_csv(balance_sheet_file).iloc[::-1].reset_index(drop=True)
    financial_metrics = pd.read_csv(financial_metrics_file).iloc[::-1].reset_index(drop=True)
    cash_flow = pd.read_csv(cash_flow_file).iloc[::-1].reset_index(drop=True)
    income_statement = pd.read_csv(income_statement_file).iloc[::-1].reset_index(drop=True)
    indicators_ohlc = pd.read_csv(indicators_ohlc_file)

    balance_sheet.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)
    cash_flow.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)
    income_statement.rename(columns={'fiscalDateEnding': 'Date'}, inplace=True)

    merged_data = pd.merge(income_statement, cash_flow, on='Date')
    merged_data = pd.merge(merged_data, balance_sheet, on='Date')
    merged_data = pd.merge(merged_data, financial_metrics, on='Date')

    final_data = pd.merge(indicators_ohlc, merged_data, on='Date', how='left')

    final_data.fillna(method='ffill', inplace=True)
    final_data.dropna(axis=0, how='any', inplace=True)

    non_numeric_cols = [col for col in final_data.columns if not pd.to_numeric(final_data[col], errors='coerce').notnull().all() and col != 'Date']
    final_data.drop(non_numeric_cols, axis=1, inplace=True)

    final_data.to_csv(output_file, index=False)

def main(argv):
    if len(argv) < 2:
        print("Usage: python script.py symbols_list")
        sys.exit(1)

    symbols = argv[1:]
    functions = ['INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'TIME_SERIES_DAILY']

    for symbol in symbols:
        file_names = [f'income_statement_{symbol}.csv', f'balance_sheet_{symbol}.csv', f'cash_flow_{symbol}.csv', f'ohlc_{symbol}.csv']
        for function, file_name in zip(functions, file_names):
            fetch_and_save_data(function, symbol, file_name)
            if function == 'TIME_SERIES_DAILY':
                fetch_and_save_ohlc(symbol, file_name)
                add_technical_indicators(file_name)

        calculate_financial_ratios(
            f'balance_sheet_{symbol}.csv',
            f'cash_flow_{symbol}.csv',
            f'income_statement_{symbol}.csv',
            f'indicators_ohlc_{symbol}.csv',
            f'financial_ratios_{symbol}.csv'
        )

        merge_and_filter_data(
            f'balance_sheet_{symbol}.csv',
            f'financial_ratios_{symbol}.csv',
            f'cash_flow_{symbol}.csv',
            f'income_statement_{symbol}.csv',
            f'indicators_ohlc_{symbol}.csv',
            f'final_data_{symbol}.csv'
        )

if __name__ == "__main__":
    main(sys.argv)
