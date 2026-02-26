import pandas as pd
import json
from urllib.parse import urlparse
from unidecode import unidecode

with open('cleanProductInfo.json', encoding='utf-8') as f:
    data = json.load(f)

# Recursive function to convert all strings to ASCII
def to_ascii(obj):
    if isinstance(obj, dict):
        return {k: to_ascii(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_ascii(x) for x in obj]
    elif isinstance(obj, str):
        return unidecode(obj)
    else:
        return obj

data = to_ascii(data)

df = pd.json_normalize(data)

# Explode the history column so each history entry becomes a separate row
df = df.explode('history').reset_index(drop=True)

# Normalize the history dictionary into separate columns
history_df = pd.json_normalize(df['history'])
df = pd.concat([df[['name', 'url', 'quantity']], history_df], axis=1)

df['daySinceEpoch'] = pd.to_datetime(df['daySinceEpoch'], unit='D')

companies = []
urls = []

for idx, row in df.iterrows():
    parsed_url = urlparse(row['url'])
    # Extract company from domain name
    company = parsed_url.netloc.split('.')[0]  # e.g., 'www.coles.com.au' -> 'www'
    if company == 'www' and 'coles' in parsed_url.netloc:
        company = 'coles'
    elif company == 'www' and 'woolworths' in parsed_url.netloc:
        company = 'woolworths'
    elif company == 'www' and 'aldi' in parsed_url.netloc:
        company = 'aldi'
    companies.append(company)
    
    # Keep the path as url
    urls.append(parsed_url.path)

df['company'] = companies
df['url'] = urls

df = df[['name', 'company', 'quantity', 'daySinceEpoch', 'price', 'url']]

df = df.sort_values(by=['company'])

df.to_csv('cleanedData.csv', index=False)