import requests
import pdfkit
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import base64
import os
import sys
import urllib.request, json
import yfinance as yf
import yahoo_fin.stock_info as si
from openai import OpenAI
import csv
import json

explanations = {
    'grossProfit': "The gross profit represents the revenue minus the cost of goods sold (COGS). It reflects the profitability of a company's core business activities.",
    'costOfRevenue': "The cost of revenue represents the direct costs associated with producing goods or services sold by a company. It includes expenses such as raw materials, labor, and manufacturing overhead.",
    'operatingIncome': "Operating income, also known as operating profit, is the profit earned from a company's core business operations after deducting operating expenses such as wages, rent, and utilities.",
    'sellingGeneralAndAdministrative': "Selling, general, and administrative (SG&A) expenses represent the indirect costs associated with selling products and managing the day-to-day operations of a business. They include expenses such as salaries, marketing, and administrative overhead.",
    'operatingExpenses': "Operating expenses are the costs associated with running the day-to-day operations of a business, including salaries, rent, utilities, and marketing expenses.",
    'netInterestIncome': "Net interest income is the difference between interest earned from assets and interest paid on liabilities. It reflects the profitability of a company's lending and investment activities.",
    'interestExpense': "Interest expense represents the cost of borrowing money or using credit facilities. It includes interest payments on loans, bonds, and other debt instruments.",
    'interestAndDebtExpense': "Interest and debt expense represent the interest payments and other costs associated with servicing the company's debt obligations.",
    'netIncomeFromContinuingOperations': "Net income from continuing operations is the profit remaining after deducting all expenses, including taxes, interest, and non-operating expenses, from revenue.",
    'comprehensiveIncomeNetOfTax': "Comprehensive income represents the change in equity of a business enterprise during a period from transactions and other events and circumstances from non-owner sources. It includes all changes in equity during a period except those resulting from investments by owners and distributions to owners.",
    'ebit': "EBIT stands for Earnings Before Interest and Taxes. It measures a company's profitability before accounting for interest and tax expenses. It's calculated by subtracting operating expenses from gross profit.",
    'netIncome_x': "Net income represents the total profit earned by the company after subtracting all expenses, including taxes and interest, from revenue.",
    'operatingCashflow': "Operating cash flow represents the cash generated from a company's core business operations. It's a key indicator of a company's ability to generate cash from its primary activities.",
    'changeInOperatingLiabilities': "Change in operating liabilities represents the change in the company's obligations related to its day-to-day operations, such as accounts payable and accrued expenses.",
    'profitLoss': "This metric represents the overall profit or loss earned by the company during a specific period.",
    'cashflowFromFinancing': "Cash flow from financing activities represents the cash inflows and outflows associated with raising and repaying capital, including issuing and repurchasing stocks and bonds.",
    'proceedsFromRepaymentsOfShortTermDebt': "Proceeds from repayments of short-term debt represent the cash received from repaying short-term debt obligations.",
    'proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet': "Proceeds from the issuance of long-term debt and capital securities represent the cash received from issuing long-term debt instruments such as bonds and preferred stock.",
    'netIncome_y': "Net income represents the total profit earned by the company after subtracting all expenses, including taxes and interest, from revenue.",
    'totalAssets': "Total assets represent the total value of all assets owned by the company, including cash, investments, property, plant, equipment, and intangible assets.",
    'totalCurrentAssets': "Total current assets represent the total value of assets that are expected to be converted into cash or used up within one year. It includes assets such as cash, accounts receivable, and inventory.",
    'cashAndCashEquivalentsAtCarryingValue': "Cash and cash equivalents at carrying value represent the value of cash and highly liquid assets that are easily convertible into cash. It includes cash on hand, demand deposits, and short-term investments with maturities of three months or less.",
    'cashAndShortTermInvestments': "Cash and short-term investments represent the value of cash and highly liquid assets that are easily convertible into cash. It includes cash on hand, demand deposits, and short-term investments with maturities of three months or less.",
    'totalLiabilities': "Total liabilities represent the total debts and obligations owed by the company to creditors, including loans, bonds, and accounts payable.",
    'totalCurrentLiabilities': "Total current liabilities represent the total value of debts and obligations that are due within one year. It includes liabilities such as accounts payable, short-term loans, and accrued expenses.",
    'currentDebt': "Current debt represents the portion of the company's total debt that is due within one year. It includes short-term loans, lines of credit, and other obligations.",
    'longTermDebt': "Long-term debt represents the portion of the company's total debt that is due beyond one year. It includes long-term loans, bonds, and other obligations.",
    'currentLongTermDebt': "Current long-term debt represents the portion of the company's long-term debt that is due within one year. It includes long-term loans and bonds with maturities of less than one year.",
    'totalShareholderEquity': "Total shareholder equity represents the residual value of assets after deducting liabilities. It represents the shareholders' ownership interest in the company.",
    'commonStock': "Common stock represents the shares of ownership in a corporation. It represents the ownership stake of the company's shareholders.",
    'commonStockSharesOutstanding': "Common stock shares outstanding represent the total number of shares of common stock issued by the company and held by investors.",
    'Market Cap': "Market capitalization represents the total value of a company's outstanding shares. It's calculated by multiplying the current share price by the total number of outstanding shares.",
    'Price to Sales Ratio': "The price-to-sales ratio measures the company's stock price relative to its revenue per share. It's calculated by dividing the current share price by the revenue per share.",
    'EBITDA': "EBITDA stands for Earnings Before Interest, Taxes, Depreciation, and Amortization. It's a measure of a company's operating performance and is often used as a proxy for cash flow.",
    'Net Debt': "Net debt represents the company's total debt minus its cash and cash equivalents. It reflects the company's debt obligations net of its available cash resources.",
    'Enterprise Value': "Enterprise value represents the total value of a company, including its equity value and debt, minus its cash and cash equivalents.",
    'EV to EBITDA': "The EV/EBITDA ratio compares a company's enterprise value to its EBITDA. It's a measure of valuation that takes into account a company's debt and operating performance.",
    'EBITDA Margin': "The EBITDA margin is the ratio of EBITDA to revenue, indicating the percentage of revenue that translates into EBITDA.",
    'EBIT Margin': "The EBIT margin is the ratio of EBIT (Earnings Before Interest and Taxes) to revenue, indicating the percentage of revenue that translates into EBIT.",
    'PER': "The Price-to-Earnings Ratio (PER) compares a company's stock price to its earnings per share (EPS). It's a measure of valuation that indicates how much investors are willing to pay for each dollar of earnings.",
    'PBV': "The Price-to-Book Value (PBV) ratio compares a company's stock price to its book value per share. It's a measure of valuation that indicates how much investors are paying for each dollar of book value.",
    'ROE': "Return on Equity (ROE) measures a company's profitability relative to its shareholder equity. It's calculated by dividing net income by shareholder equity.",
    'ROIC': "Return on Invested Capital (ROIC) measures a company's profitability relative to its invested capital. It's calculated by dividing operating income by invested capital.",
    'Net Debt to EBITDA': "The Net Debt-to-EBITDA ratio compares a company's net debt to its EBITDA. It's a measure of leverage that indicates how many years it would take for a company to repay its debt using its EBITDA.",
    'Debt to Equity': "The Debt-to-Equity ratio compares a company's total debt to its shareholder equity. It's a measure of leverage that indicates the proportion of a company's financing that is provided by debt.",
    'Dividend Yield': "Dividend yield represents the dividend income earned by an investor relative to the price of the investment. It's calculated by dividing the annual dividend per share by the stock price.",
    'ROA': "Return on Assets (ROA) measures a company's profitability relative to its total assets. It's calculated by dividing net income by total assets.",
    'Shares Buyback Ratio': "The shares buyback ratio represents the proportion of outstanding shares that a company repurchases over a specific period. It's calculated by dividing the number of shares repurchased by the total number of outstanding shares.",
    'Free Cash Flow Margin': "The free cash flow margin is the ratio of free cash flow to revenue, indicating the percentage of revenue that translates into free cash flow.",
    'Net Margin': "The net margin is the ratio of net income to revenue, indicating the percentage of revenue that translates into net income.",
    'Current Ratio': "The current ratio measures a company's ability to pay its short-term liabilities with its short-term assets. It's calculated by dividing current assets by current liabilities.",
    'Quick Ratio': "The quick ratio, also known as the acid-test ratio, measures a company's ability to pay its short-term liabilities with its most liquid assets. It's calculated by subtracting inventory from current assets and then dividing by current liabilities.",
    'Cash Ratio': "The cash ratio measures a company's ability to pay its short-term liabilities with its cash and cash equivalents. It's calculated by dividing cash and cash equivalents by current liabilities."
}

# Dictionary of explanations for each point
explanations_comp = {
    'Revenue vs Net Income': 'Compare the revenue (grossProfit) with the net income (netIncomeFromContinuingOperations) to understand the operational efficiency and profitability of the company.',
    'Operating Expenses vs Revenue': 'Analyze the operating expenses (operatingExpenses) in relation to revenue to assess the company\'s cost efficiency.',
    'Total Liabilities vs Total Shareholder Equity': 'Compare the total liabilities (totalLiabilities) with the total shareholder equity (totalShareholderEquity) to assess the company\'s capital structure and its ability to handle debt obligations.',
    'Net Income vs Operating Cashflow': 'Compare the net income (netIncomeFromContinuingOperations) with the operating cash flow (operatingCashflow) to evaluate the quality of earnings and the company\'s ability to generate cash.',
    'Current Ratio vs Quick Ratio': 'Analyze liquidity metrics such as the current ratio (Current Ratio) and quick ratio (Quick Ratio) in relation to short-term obligations to understand the company\'s ability to pay its short-term debts.',
    'Net Income vs Total Shareholder Equity': 'Compare the net income (netIncomeFromContinuingOperations) with the total shareholder equity (totalShareholderEquity) to calculate the return on equity (ROE) and assess shareholder profitability.',
    'Profit Margins': 'Analyze gross profit margin (grossProfit Margin), operating margin (EBIT Margin), and net profit margin (Net Margin) to understand the operational efficiency and profitability of the company at different levels of its operation.',
    'Valuation Metrics': 'Consider valuation metrics such as the Price to Sales Ratio, EBITDA, and PER (Price to Earnings Ratio) in relation to the company\'s historical performance and industry standards to assess whether the company\'s stocks are overvalued or undervalued.',
    'Gross Profit vs Price to Sales Ratio': 'Compare the gross profit (grossProfit) with the Price to Sales (P/S) ratio to assess how the market values the company\'s profitability relative to its sales performance. A lower P/S ratio relative to peers may suggest potentially higher profitability or operational efficiency, while a higher P/S ratio may suggest potentially lower profitability or operational efficiency.',
    'Liquidity Ratios': 'Compare the liquidity ratios, including the Current Ratio, Quick Ratio, and Cash Ratio, over time to evaluate the company\'s ability to meet its short-term obligations. The Current Ratio measures the company\'s ability to pay its short-term liabilities with its short-term assets, while the Quick Ratio provides a more conservative measure by excluding inventory from current assets. The Cash Ratio focuses solely on the company\'s ability to cover its short-term liabilities with its cash and cash equivalents.'
}

def dict_to_string(dictionary):
    result = ""
    for key, value in dictionary.items():
        result += f"{key}:\n"
        for sub_key, sub_value in value.items():
            result += f"  {sub_key}: {sub_value}\n"
    return result

def generate_response(message):
    # Initialize the OpenAI client
    client = OpenAI()
    
    # Create a completion request with the provided message
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a professional fundamental stock analyst"},
            {"role": "user", "content": "Never use programming code in your response \n"+message}
        ]
    )
    
    # Extract the generated response
    response_content = completion.choices[0].message.content
    
    # Replace newline characters with <br> tags
    response_html = response_content.replace("\n", "<br>")
    
    # Return the formatted HTML content
    return response_html

# Function to fetch company overview from Alpha Vantage API
def get_company_overview(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

# Ensure correct number of arguments
if len(sys.argv) != 3:
    print("Usage: python script.py <company_symbol> <fundamental_data_csv>")
    sys.exit(1)

company_symbol = sys.argv[1]  # Example company symbol from command line argument
api_key = 'API_KEY'  # Replace with your Alpha Vantage API key

company_overview_data = get_company_overview(company_symbol, api_key)

def extract_last_row_as_dict(csv_data):
    # Extract the last row of the DataFrame as a dictionary
    last_row_dict = csv_data.iloc[-1].to_dict()

    # Convert the values to numeric, coercing errors to NaN
    for key, value in last_row_dict.items():
        last_row_dict[key] = pd.to_numeric(value, errors='coerce')

    return last_row_dict

# Read CSV data
csv_data = pd.read_csv(sys.argv[2])
last_row_dict = extract_last_row_as_dict(csv_data)

# Find the index of the 'others_cr' column
start_index = csv_data.columns.get_loc('others_cr') + 1  # Add 1 to exclude the start_index

# Select columns between 'others_cr' and the last column
selected_columns = csv_data.iloc[:, start_index:]

# HTML content for company information and graphs
html_content = f"""
<html>
<head><title>Company Dashboard</title></head>
<body>
<h1>Company Information</h1>
<p><strong>Symbol:</strong> {company_overview_data.get('Symbol', 'N/A')}</p>
<p><strong>Asset Type:</strong> {company_overview_data.get('AssetType', 'N/A')}</p>
<p><strong>Name:</strong> {company_overview_data.get('Name', 'N/A')}</p>
<p><strong>Description:</strong> {company_overview_data.get('Description', 'N/A')}</p>
<p><strong>CIK:</strong> {company_overview_data.get('CIK', 'N/A')}</p>
<p><strong>Exchange:</strong> {company_overview_data.get('Exchange', 'N/A')}</p>
<p><strong>Currency:</strong> {company_overview_data.get('Currency', 'N/A')}</p>
<p><strong>Country:</strong> {company_overview_data.get('Country', 'N/A')}</p>
<p><strong>Sector:</strong> {company_overview_data.get('Sector', 'N/A')}</p>
<p><strong>Industry:</strong> {company_overview_data.get('Industry', 'N/A')}</p>
<p><strong>Address:</strong> {company_overview_data.get('Address', 'N/A')}</p>
<h2>Institutional Ownership</h2>
  <table border="1">
    <tr>
      <th>Date</th>
      <th>Insti Owner</th>
      <th>Shares Outstanding</th>
      <th>Institution Shares Held</th>
    </tr>
"""

api_token = "API_KEY" #gurufocus

# Define custom user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/indicator_history', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))

#print(data)
# Add data to HTML content
for insti_owner, shares_outstanding, institution_shares_held in zip(data['insti_owner'], data['shares_outstanding'], data['InstitutionSharesHeld']):
    html_content += f"""
    <tr>
      <td>{insti_owner[0]}</td>
      <td>{insti_owner[1]}</td>
      <td>{shares_outstanding[1]}</td>
      <td>{institution_shares_held[1]}</td>
    </tr>
    """

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/ownership', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))

html_content += f"""
</table>
  <h2>Ownership Information</h2>
  <ul>
    <li><strong>Exchange:</strong> {data['exchange']}</li>
    <li><strong>Share Outstanding:</strong> {data['Share_Outstanding']['value']}</li>
    <li><strong>Institutional Ownership:</strong> {data['Institutional_Ownership']['percentage']} ({data['Institutional_Ownership']['value']})</li>
    <li><strong>Insider Ownership:</strong> {data['Insider_Ownership']['percentage']} ({data['Insider_Ownership']['value']})</li>
    <li><strong>Float Percentage of Total Share Outstanding:</strong> {data['Float_Percentage_of_TSO']['percentage']} ({data['Float_Percentage_of_TSO']['value']})</li>
  </ul>
  """

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/gurus', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))

if company_symbol in data and 'picks' in data[company_symbol]:
    html_content += f"""
        <h2>Guru Picks</h2>
    <table>
        <tr>
        <td>Guru</td>
        <td>Date</td>
        <td>Action</td>
        <td>Price Range</td>
        <td>Average Price</td>
        <td>Comment</td>
        <td>Current Shares</td>
        </tr>
    """

    # Add data to HTML content
    for pick in data[company_symbol]['picks']:
        html_content += f"""
        <tr>
        <td>{pick['guru']}</td>
        <td>{pick['date']}</td>
        <td>{pick['action']}</td>
        <td>{pick['price_min']} - {pick['price_max']}</td>
        <td>{pick['Avg']}</td>
        <td>{pick['comment']}</td>
        <td>{pick['current_shares']}</td>
        </tr>
        """
    html_content += "</table>"

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/insider', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))

html_content += f"""
<h1>Real-Time Insider Trades for {company_symbol}</h1>
  <table border="1">
    <tr>
      <th>Position</th>
      <th>Date</th>
      <th>Type</th>
      <th>Transaction Shares</th>
      <th>Final Shares</th>
      <th>Price</th>
      <th>Cost</th>
      <th>Insider</th>
      <th>Change (%)</th>
    </tr>
"""

# Add data to HTML content
for insider_trade in data[company_symbol]:
    html_content += f"""
    <tr>
      <td>{insider_trade['position']}</td>
      <td>{insider_trade['date']}</td>
      <td>{insider_trade['type']}</td>
      <td>{insider_trade['trans_share']}</td>
      <td>{insider_trade['final_share']}</td>
      <td>{insider_trade['price']}</td>
      <td>{insider_trade['cost']}</td>
      <td>{insider_trade['insider']}</td>
      <td>{insider_trade['change']}</td>
    </tr>
    """

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/executives', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))

html_content += f"""
</table>
<h1>List of Company Executives for {company_symbol}</h1>
  <table border="1">
    <tr>
      <th>Name</th>
      <th>Position</th>
      <th>Transaction Date</th>
    </tr>
"""

# Add data to HTML content
for executive in data:
    html_content += f"""
    <tr>
      <td>{executive['name']}</td>
      <td>{executive['position']}</td>
      <td>{executive['transaction_date']}</td>
    </tr>
    """

# Get the absolute path to the image file
script_directory = os.path.dirname(os.path.abspath(__file__))
technical_analysis_image_path = os.path.join(script_directory, 'technical_analysis_graph.png')

# Create a candlestick chart
fig = go.Figure(data=[go.Candlestick(x=csv_data['Date'],
                                     open=csv_data['Open'],
                                     high=csv_data['High'],
                                     low=csv_data['Low'],
                                     close=csv_data['Close'])])

# Update the layout of the chart
fig.update_layout(title='Candlestick Chart',
                  xaxis_title='Date',
                  yaxis_title='Price')

pio.write_image(fig, technical_analysis_image_path)
# Read the image file and convert to Base64 string
with open(technical_analysis_image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

try:
    analyst_info = yf.Ticker(company_symbol).get_institutional_holders().to_html()
except KeyError as e:
    print(f"Failed to fetch institutional holder information for {company_symbol}: {e}")
    analyst_info = "<p>Institutional holder information not available.</p>"
except Exception as e:
    print(f"An error occurred while fetching institutional holder information for {company_symbol}: {e}")
    analyst_info = "<p>Error fetching institutional holder information.</p>"

# Include the image as Base64 string in HTML content
html_content += f"""
</table>
<h1>Institutional Holders</h1>
{analyst_info} 
<h1>CandleStick chart</h1>
<img src="data:image/png;base64,{img_base64}" alt="Technical Analysis Graph">
<h1></h1>
<h1>Fundamental Data</h1>
"""

# Create a line plot for each selected column
for column in selected_columns.columns:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=csv_data['Date'], y=selected_columns[column], mode='lines', name=column))
    fig.update_layout(xaxis_title='Date', yaxis_title=column)
    technical_analysis_image_path = f"{column}_technical_analysis_graph.png"
    pio.write_image(fig, technical_analysis_image_path)

    # Read the image file and convert to Base64 string
    with open(technical_analysis_image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Include the image as Base64 string in HTML content
    html_content += f"""
    <h1>{column}</h1>
    <p>{explanations.get(column, "Explanation not available")}</p>
    <img src="data:image/png;base64,{img_base64}" alt="Technical Analysis Graph">
    <h1></h1>
    """

    # Generate response using ChatGPT
    prompt = f"""Provide analysis for the column '{column}' do not forget this is fundamental information from a company:
    {selected_columns[column]}
    """
    analysis = generate_response(prompt)
    html_content += f"""
    <h2>ChatGPT Analysis:</h2>
    <p>{analysis}</p>
    """

# Create comparison plots for each point
comparison_plots = {}
comparion_text = {}

if 'grossProfit' in csv_data.columns and 'netIncomeFromContinuingOperations' in csv_data.columns:
    # Compare Revenue and Net Income
    comparison_plots['Revenue vs Net Income'] = go.Figure()
    comparison_plots['Revenue vs Net Income'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['grossProfit'], mode='lines', name='Gross Profit'))
    comparison_plots['Revenue vs Net Income'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['netIncomeFromContinuingOperations'], mode='lines', name='Net Income'))
    comparison_plots['Revenue vs Net Income'].update_layout(title='Revenue vs Net Income', xaxis_title='Date', yaxis_title='Amount')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns grossProfit and netIncomeFromContinuingOperations do not forget this is fundamental information from a company:
    {csv_data['grossProfit']}\n
    {csv_data['netIncomeFromContinuingOperations']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Revenue vs Net Income'] = analysis

if 'operatingExpenses' in csv_data.columns and 'grossProfit' in csv_data.columns:
    # Operating Expenses as a Percentage of Revenue
    comparison_plots['Operating Expenses vs Revenue'] = go.Figure()
    comparison_plots['Operating Expenses vs Revenue'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['operatingExpenses'] / csv_data['grossProfit'], mode='lines', name='Operating Expenses as % of Revenue'))
    comparison_plots['Operating Expenses vs Revenue'].update_layout(title='Operating Expenses vs Revenue', xaxis_title='Date', yaxis_title='% of Revenue')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns operatingExpenses and grossProfit do not forget this is fundamental information from a company:
    {csv_data['operatingExpenses']}\n
    {csv_data['grossProfit']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Operating Expenses vs Revenue'] = analysis

if 'totalLiabilities' in csv_data.columns and 'totalShareholderEquity' in csv_data.columns:
    # Compare Total Liabilities and Total Shareholder Equity
    comparison_plots['Total Liabilities vs Total Shareholder Equity'] = go.Figure()
    comparison_plots['Total Liabilities vs Total Shareholder Equity'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['totalLiabilities'], mode='lines', name='Total Liabilities'))
    comparison_plots['Total Liabilities vs Total Shareholder Equity'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['totalShareholderEquity'], mode='lines', name='Total Shareholder Equity'))
    comparison_plots['Total Liabilities vs Total Shareholder Equity'].update_layout(title='Total Liabilities vs Total Shareholder Equity', xaxis_title='Date', yaxis_title='Amount')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns totalLiabilities and totalShareholderEquity do not forget this is fundamental information from a company:
    {csv_data['totalLiabilities']}\n
    {csv_data['totalShareholderEquity']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Total Liabilities vs Total Shareholder Equity'] = analysis

if 'operatingCashflow' in csv_data.columns and 'netIncomeFromContinuingOperations' in csv_data.columns:
    # Compare Net Income and Operating Cashflow
    comparison_plots['Net Income vs Operating Cashflow'] = go.Figure()
    comparison_plots['Net Income vs Operating Cashflow'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['netIncomeFromContinuingOperations'], mode='lines', name='Net Income'))
    comparison_plots['Net Income vs Operating Cashflow'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['operatingCashflow'], mode='lines', name='Operating Cashflow'))
    comparison_plots['Net Income vs Operating Cashflow'].update_layout(title='Net Income vs Operating Cashflow', xaxis_title='Date', yaxis_title='Amount')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns operatingCashflow and netIncomeFromContinuingOperations do not forget this is fundamental information from a company:
    {csv_data['operatingCashflow']}\n
    {csv_data['netIncomeFromContinuingOperations']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Net Income vs Operating Cashflow'] = analysis

if 'Current Ratio' in csv_data.columns and 'Quick Ratio' in csv_data.columns:
    # Compare Current Ratio and Quick Ratio
    comparison_plots['Current Ratio vs Quick Ratio'] = go.Figure()
    comparison_plots['Current Ratio vs Quick Ratio'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Current Ratio'], mode='lines', name='Current Ratio'))
    comparison_plots['Current Ratio vs Quick Ratio'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Quick Ratio'], mode='lines', name='Quick Ratio'))
    comparison_plots['Current Ratio vs Quick Ratio'].update_layout(title='Current Ratio vs Quick Ratio', xaxis_title='Date', yaxis_title='Ratio')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns Current Ratio and Quick Ratio do not forget this is fundamental information from a company:
    {csv_data['Current Ratio']}\n
    {csv_data['Quick Ratio']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Current Ratio vs Quick Ratio'] = analysis

if 'netIncomeFromContinuingOperations' in csv_data.columns and 'totalShareholderEquity' in csv_data.columns:
    # Compare Net Income and Total Shareholder Equity for ROE
    comparison_plots['Net Income vs Total Shareholder Equity'] = go.Figure()
    comparison_plots['Net Income vs Total Shareholder Equity'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['netIncomeFromContinuingOperations'], mode='lines', name='Net Income'))
    comparison_plots['Net Income vs Total Shareholder Equity'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['totalShareholderEquity'], mode='lines', name='Total Shareholder Equity'))
    comparison_plots['Net Income vs Total Shareholder Equity'].update_layout(title='Net Income vs Total Shareholder Equity (ROE Calculation)', xaxis_title='Date', yaxis_title='Amount')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns netIncomeFromContinuingOperations and totalShareholderEquity do not forget this is fundamental information from a company:
    {csv_data['netIncomeFromContinuingOperations']}\n
    {csv_data['totalShareholderEquity']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Net Income vs Total Shareholder Equity'] = analysis

if 'grossProfit Margin' in csv_data.columns and 'EBIT Margin' in csv_data.columns and 'Net Margin' in csv_data.columns:
    # Compare Gross Profit Margin, EBIT Margin, and Net Margin
    comparison_plots['Profit Margins'] = go.Figure()
    comparison_plots['Profit Margins'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['grossProfit Margin'], mode='lines', name='Gross Profit Margin'))
    comparison_plots['Profit Margins'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['EBIT Margin'], mode='lines', name='EBIT Margin'))
    comparison_plots['Profit Margins'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Net Margin'], mode='lines', name='Net Margin'))
    comparison_plots['Profit Margins'].update_layout(title='Profit Margins', xaxis_title='Date', yaxis_title='Margin')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns grossProfit Margin and EBIT Margin and Net Margin do not forget this is fundamental information from a company:
    {csv_data['grossProfit Margin']}\n
    {csv_data['EBIT Margin']}\n
    {csv_data['Net Margin']}
    """
    analysis = generate_response(prompt)
    comparion_text['Profit Margins'] = analysis

if 'Price to Sales Ratio' in csv_data.columns and 'EBITDA' in csv_data.columns and 'PER' in csv_data.columns:
    # Compare Valuation Metrics
    comparison_plots['Valuation Metrics'] = go.Figure()
    comparison_plots['Valuation Metrics'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Price to Sales Ratio'], mode='lines', name='Price to Sales Ratio'))
    comparison_plots['Valuation Metrics'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['EBITDA'], mode='lines', name='EBITDA'))
    comparison_plots['Valuation Metrics'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['PER'], mode='lines', name='PER'))
    comparison_plots['Valuation Metrics'].update_layout(title='Valuation Metrics', xaxis_title='Date', yaxis_title='Ratio')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns Price to Sales Ratio and EBITDA and PER do not forget this is fundamental information from a company:
    {csv_data['Price to Sales Ratio']}\n
    {csv_data['EBITDA']}\n
    {csv_data['PER']}
    """
    analysis = generate_response(prompt)
    comparion_text['Valuation Metrics'] = analysis

if 'Price to Sales Ratio' in csv_data.columns and 'grossProfit':
    # Compare Valuation Metrics
    comparison_plots['Gross Profit vs Price to Sales Ratio'] = go.Figure()
    comparison_plots['Gross Profit vs Price to Sales Ratio'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Price to Sales Ratio'], mode='lines', name='Price to Sales Ratio'))
    comparison_plots['Gross Profit vs Price to Sales Ratio'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['grossProfit'], mode='lines', name='Gross Profit'))
    comparison_plots['Gross Profit vs Price to Sales Ratio'].update_layout(title='Gross Profit vs Price to Sales Ratio', xaxis_title='Date', yaxis_title='Value')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns Price to Sales Ratio and grossProfit do not forget this is fundamental information from a company:
    {csv_data['Price to Sales Ratio']}\n
    {csv_data['grossProfit']}\n
    """
    analysis = generate_response(prompt)
    comparion_text['Gross Profit vs Price to Sales Ratio'] = analysis

if 'Current Ratio' in csv_data.columns and 'Quick Ratio' in csv_data.columns and 'Cash Ratio' in csv_data.columns:
    # Compare Liquidity Ratios
    comparison_plots['Liquidity Ratios'] = go.Figure()
    comparison_plots['Liquidity Ratios'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Current Ratio'], mode='lines', name='Current Ratio'))
    comparison_plots['Liquidity Ratios'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Quick Ratio'], mode='lines', name='Quick Ratio'))
    comparison_plots['Liquidity Ratios'].add_trace(go.Scatter(x=csv_data['Date'], y=csv_data['Cash Ratio'], mode='lines', name='Cash Ratio'))
    comparison_plots['Liquidity Ratios'].update_layout(title='Liquidity Ratios', xaxis_title='Date', yaxis_title='Ratio')
    # Generate response using ChatGPT
    prompt = f"""Provide a comparation analysis for the columns Current Ratio and Quick Ratio and Cash Ratio do not forget this is fundamental information from a company:
    {csv_data['Current Ratio']}\n
    {csv_data['Quick Ratio']}\n
    {csv_data['Cash Ratio']}
    """
    analysis = generate_response(prompt)
    comparion_text['Liquidity Ratios'] = analysis


# Create HTML content
html_content += """
<h1>Company Metrics Comparison</h1>
"""

# Include the plots in HTML content
for title, fig in comparison_plots.items():
    # Save the plot as an image
    pio.write_image(fig, technical_analysis_image_path)

    # Read the image file and convert to Base64 string
    with open(technical_analysis_image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Include the image as Base64 string in HTML content
    html_content += f"""
    <h1>{title}</h1>
    <p>{explanations_comp[title]}</p>
    <img src="data:image/png;base64,{img_base64}" alt="{title} Plot">
    <p>{comparion_text[title]}</p>
    <h1></h1>
    """

# Construct request with custom user agent
request = urllib.request.Request(f'https://api.gurufocus.com/public/user/{api_token}/stock/{company_symbol}/analyst_estimate', headers=headers)

# Open URL with the custom request
response = urllib.request.urlopen(request)
content = response.read()
data = json.loads(content.decode('utf8'))
#print(data)

html_content += f"""
    <h1>Analyst Estimate Data for {company_symbol} from GuruFocus</h1>
    """
# Check if annual estimate data is available
if any(data['annual'].values()):
    html_content += """
    <h2>Annual Estimates</h2>
    <table border="1">
      <tr>
        <th>Date</th>
        <th>Revenue Estimate</th>
        <th>EBIT Estimate</th>
        <th>EBITDA Estimate</th>
        <th>Dividend Estimate</th>
        <th>Per Share EPS Estimate</th>
        <th>EPS NRI Estimate</th>
        <th>Long Term Growth Rate Mean</th>
        <th>Long Term Revenue Growth Rate Mean</th>
      </tr>
    """

    # Add annual estimate data to HTML content
    if not all(not x for x in data['annual'].values()):
        for i in range(len(data['annual']['date'])):
            html_content += f"""
            <tr>
              <td>{data['annual']['date'][i]}</td>
              <td>{data['annual']['revenue_estimate'][i]}</td>
              <td>{data['annual']['ebit_estimate'][i]}</td>
              <td>{data['annual']['ebitda_estimate'][i]}</td>
              <td>{data['annual']['dividend_estimate'][i]}</td>
              <td>{data['annual']['per_share_eps_estimate'][i]}</td>
              <td>{data['annual']['eps_nri_estimate'][i]}</td>
              <td>{data['annual']['long_term_growth_rate_mean']}</td>
              <td>{data['annual']['long_term_revenue_growth_rate_mean']}</td>
            </tr>
            """
    else:
        html_content += "<tr><td colspan='9'>No annual estimates available.</td></tr>"

    html_content += """
    </table>
    """
else:
    html_content += "<p>Annual estimates data is not available.</p>"

html_content += "<h1>Estimates from yahoo finance</h1>"
analysts = si.get_analysts_info(company_symbol)

html_content += "<table border='1'>"

# Iterate over each section
for section, data in analysts.items():
    html_content += f"<tr><th colspan='6'>{section}</th></tr>"

    # Iterate over each row
    for key, values in data.items():
        html_content += "<tr>"
        html_content += f"<td>{key}</td>"
        for value in values:
            html_content += f"<td>{value}</td>"
        html_content += "</tr>"
html_content += "</table>"

analysts = dict_to_string(analysts)
last_row_json_string = json.dumps(last_row_dict)

# Generate response using ChatGPT
prompt = f"""Provide analysis for the estimates values and also share your opinion if this has a pontential to be a good company to buy and what price could it get. Do not forget this is fundamental information from a company:
estimates:\n
{analysts}
Current Fundamental Data:\n
{last_row_json_string}
"""
analysis = generate_response(prompt)
html_content += f"""
<h2>ChatGPT Analysis:</h2>
<p>{analysis}</p>
"""

html_content += """
</body>
</html>
"""

# Remove the PNG file
if os.path.exists(technical_analysis_image_path):
    os.remove(technical_analysis_image_path)
else:
    print("The file does not exist")

# Convert HTML to PDF
pdfkit.from_string(html_content, f'company_{company_symbol}.pdf')
