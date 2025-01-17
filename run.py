#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser()
parser.add_argument("--login", required=True)
parser.add_argument("--id", required=True)
parser.add_argument("--password", required=True)
parser.add_argument("--url", required=True)
parser.add_argument("--element", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

LOGIN_URL = args.login
ID = args.id
PASSWORD = args.password
ELEMENT = args.element
URL = args.url
OUTPUT = args.output

driver = webdriver.Chrome()

driver.get(LOGIN_URL)

email_input = driver.find_element(By.ID, "email") 
email_input.send_keys(ID)

time.sleep(1)

password_input = driver.find_element(By.ID, "password") 
password_input.send_keys(PASSWORD)

time.sleep(1)

login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
login_button.click()

time.sleep(10)

driver.get(URL)

time.sleep(10) 

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

script_tag = soup.find("script", id=ELEMENT)
json_data = script_tag.string
driver.quit()

data = json.loads(json_data)
with open("data.json", "w") as f:
    json.dump(data, f)

dataSetAll = data['props']['pageProps']['dataSetAll']

# dataSetAll
# 0 "ranking",
# 1 "ticker",
# 2 "img_tooltip_ticker",
# 3 "company",
# 4 "ticker_id",
# 5 "smartscore_tooltip",
# 6 "smartscore",
# 7 "change",
# 8 "fundamental_score_tooltip",
# 9 "fundamental_score",
# 10 "technical_score_tooltip",
# 11 "technical_score",
# 12 "sentiment_score_tooltip",
# 13 "sentiment_score",
# 14 "isin",
# 15 "sector",
# 16 "industry",
# 17 "sector_url",
# 18 "industry_url",
# 19 "risk_score",
# 20 "risk_score_tooltip",
# 21 "have_changes",
# 22 "country_flag_img",
# 23 "country_name",
# 24 "country_numcode",
# 25 "fundamental_signals_ids",
# 26 "sentiment_signals_ids",
# 27 "technical_signals_ids",
# 28 "technical_data",
# 29 "tids",
# 30 "in_portfolio",
# 31 "portfolios"

# Example of dataSetAll[1]
# 0 "1",
# 1 "USB",
# 2 "http://finviz.com/chart.ashx?s=m\u0026amp;t=USB",
# 3 "U.S. Bancorp",
# 4 "6775",
# 5 "0.558493",
# 6 "10",
# 7 "0",
# 8 "0.497815",
# 9 "10",
# 10 "0.429846",
# 11 "9",
# 12 "0.432873",
# 13 "9",
# 14 "US9029733048",
# 15 "Financials",
# 16 "Banks",
# 17 "financials",
# 18 "banks",
# 19 "5",
# 20 "0.014944434184671585",
# 21 0,
# 22 "https://cdn.danelfin.com/assets/images/flags/svg/US.svg",
# 23 "United States",
# 24 "840",
# 25 ["866","870","872","876","879","889","912","1061","1080","1086"],
# 26 ["107","109","114","125","129","135","136","174"],
# 27 ["87","5","103","235","293","564","589","592","593","623","646","656","793"],
# 28 {"pe":"12.68","market_cap":"74.93B","roe":"11.01%","dividend_yield":"4.23%","pfcf":"10.82","roi":"5.14%","high_52w":"-11.02%","low_52w":"27.03%","avg_volume":"7.94M","price":"48.03","beta":"1.06","perf_week":"-1.01%","perf_month":"-5.88%","perf_quarter":"2.19%","perf_halfyear":"6.12%","perf_year":"16.07%","perf_ytd":"0.42%","alpha_week":"-1.37%","alpha_month":"-3.80%","alpha_quarter":"0.14%","alpha_halfyear":"-0.44%","alpha_year":"-9.29%","alpha_ytd":"-0.53%"},
# 29 false,
# 30 false,
# 31 null

selected_column_to_index = {
    "Rank": 0,
    "Symbol": 1,
    "Name": 3,
    "Country": 22,
    "SmartScore": 6,
    "SmartProb": 5,
    "FundaScore": 9,
    "FundaProb": 8,
    "TechScore": 11,
    "TechProb": 10,
    "SentiScore": 13,
    "SentiProb": 12,
    "RiskScore": 19,
    "RiskProb": 20,
    "Sector": 15,
    "Industry": 16,
    "Accurate": 29,
}

def convert_to_percent(value: str) -> str:
    try:
        float_num = float(value)
        percent_num = float_num * 100
        formatted_string = f"{percent_num:.1f}%"
        return formatted_string
    except ValueError:
        return "-"

def extract_filename(url):
  basename = os.path.basename(url)
  filename_without_extension = os.path.splitext(basename)[0]
  return filename_without_extension

def truncate_string(text, length=30):
  if isinstance(text, str):
    if len(text) > length:
      return text[:length - 3] + "..."
    else:
      return text
  else:
    return "-"

def bold_text(text):
  if isinstance(text, str):
    return f"<b>{text}</b>"
  else:
    return "-"

def create_stock_link(ticker):
  url = f"https://tossinvest.com/stocks/{ticker}/analytics"
  html = f"<b><a href='{url}'>{ticker}</a></b>"
  return html

def color_percentage(percentage_str):
  try:
    percentage_num = float(percentage_str.strip('%'))
    if percentage_num > 0:
      color = "green"
    elif percentage_num < 0:
      color = "red"
    else:
      color = "black"  # 0%일 경우
    html = f"<span style='color: {color};'>{percentage_str}</span>"
    return html

  except ValueError:
    return "-"

index_to_processors = {
    0: bold_text,
    1: create_stock_link,
    3: lambda x: truncate_string(x, 35),
    22: extract_filename,
    5: convert_to_percent,
    8: convert_to_percent,
    10: convert_to_percent,
    12: convert_to_percent,
    20: convert_to_percent,
    16: lambda x: truncate_string(x, 25),
}

TECHNICAL_DATA_INDEX = 28

selected_tech_data_keys = [
    "pe",
    "market_cap",
    "perf_week",
    "perf_month",
    "perf_quarter",
    "perf_halfyear",
    "perf_year",
    "perf_ytd",
    "roe",
    "dividend_yield",
    "roi",
    "high_52w",
    "low_52w",
    "avg_volume",
    "beta",
]

tech_data_processors = {
    "pref_week": color_percentage,
    "perf_month": color_percentage,
    "perf_quarter": color_percentage,
    "perf_halfyear": color_percentage,
    "perf_year": color_percentage,
    "perf_ytd": color_percentage,
}

columns = list(selected_column_to_index.keys()) + selected_tech_data_keys

selected_data = []

for row in dataSetAll[1:]:
    selected_row = []
    for column, index in selected_column_to_index.items():
        if index in index_to_processors:
            selected_row.append(index_to_processors[index](row[index]))
        else:
            selected_row.append(row[index])
    for key in selected_tech_data_keys:
        data = row[TECHNICAL_DATA_INDEX].get(key, None)
        if key in tech_data_processors:
            selected_row.append(tech_data_processors[key](data))
        else:
            selected_row.append(row[TECHNICAL_DATA_INDEX].get(key, None))
    selected_data.append(selected_row)

df = pd.DataFrame(selected_data, columns=columns)

df.to_csv(OUTPUT, index=False, encoding='utf-8')