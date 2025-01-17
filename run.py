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
with open("data.json", "w") as f:
    f.write(json_data)
data = json.loads(json_data)
driver.quit()

dataSetAll = data['props']['pageProps']['dataSetAll']

selected_column_to_index = {
    "Rank": 0,
    "Symbol": 1,
    "Name": 3,
    "SmartProb": 5,
    "SmartScore": 6,
    "ScoreChange": 7,
    "FundaProb": 8,
    "FundaScore": 9,
    "TechProb": 10,
    "TechScore": 11,
    "SentiProb": 12,
    "SentiScore": 13,
    "Sector": 15,
    "Industry": 16,
    "RiskScore": 19,
    "RiskProb": 20,
    "Accuracy": 29,
}

index_to_processors = {
    3: lambda x: x if len(x) < 30 else x[:30] + "...",
    5: lambda x: str(float(x) * 100) + "%",
}

TECHNICAL_DATA_INDEX = 28

technical_data_keys = list(dataSetAll[1][TECHNICAL_DATA_INDEX].keys())

columns = list(selected_column_to_index.keys()) + technical_data_keys

selected_data = []

for row in dataSetAll[1:]:
    selected_row = []
    for column, index in selected_column_to_index.items():
        selected_row.append(row[index])
    for key in technical_data_keys:
        selected_row.append(row[TECHNICAL_DATA_INDEX].get(key, None))
    selected_data.append(selected_row)

df = pd.DataFrame(selected_data, columns=columns)

df.to_csv(OUTPUT, index=False, encoding='utf-8')