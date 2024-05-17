from datetime import datetime, timedelta
import pytz
from curl_cffi import requests
import csv
from collections import defaultdict
import time

def fetch_all_data(url_template):
    page = 1
    all_data = []
    retry_after = 5  # 对于503错误，可能需要设置更长的初始重试等待时间

    while True:
        url = url_template.format(page=page)
        response = requests.get(url, impersonate='chrome110')

        if response.status_code == 200:
            data = response.json()
            if not data["items"]:
                break  # 没有更多数据，结束循环
            all_data.extend(data["items"])
            page += 1
            retry_after = 5  # 重置重试等待时间
        elif response.status_code in [429, 503]:
            print(f"Received status code {response.status_code}. Retrying after {retry_after} seconds...")
            print(page, len(all_data))
            time.sleep(retry_after)
            retry_after *= 2  # 指数退避策略，每次等待时间加倍
        else:
            print(f"Failed to fetch page {page}: Status code {response.status_code}")
            break  # 遇到其他错误，结束循环

    return all_data

url_template = "https://api.openloot.com/v2/market/listings?gameId=56a149cf-f146-487a-8a1c-58dc9ff3a15c&onSale=true&page={page}&sort=name%3Aasc"
all_data = fetch_all_data(url_template)

csv_file_path = 'market_prices.csv'
# 创建并写入CSV文件
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入标题行
    writer.writerow(['Name', 'MinPrice'])
    # 遍历all_data列表，写入每个物品的名称和最低价格
    for item in all_data:
        name = item.get("metadata", {}).get("name", "Unknown")
        minPrice = item.get("minPrice", "N/A")  # 如果minPrice不存在，使用"N/A"
        writer.writerow([name, minPrice])
print(f"Data has been saved to {csv_file_path}")

