from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import requests
import os
import re

# 设置日期范围
start_date = datetime.strptime("2019-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-10-31", "%Y-%m-%d")

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不显示浏览器界面
driver = webdriver.Chrome(options=options)

# 设置下载路径
download_folder = "./data"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 定义初始页码
page = 1
all_reports = []

# 循环翻页
while True:
    # 构造URL
    url = f"https://www.sgx.com/securities/data-reports?reportType=203&page={page}&pagesize=100"
    driver.get(url)
    time.sleep(2)  # 等待页面加载

    # 抓取当前页所有报告数据
    reports = driver.find_elements(By.CLASS_NAME, "article-list-result")
    if not reports:
        print("No more reports found, stopping.")
        break

    # 处理每个报告
    for report in reports:
        try:
            # 获取报告日期
            date_text = report.find_element(By.CLASS_NAME, "timestamp").text.strip()
            report_date = datetime.strptime(date_text, "%d %b %Y")
            
            # 检查日期范围
            if start_date <= report_date <= end_date:
                # 获取报告标题和链接
                title_element = report.find_element(By.CLASS_NAME, "article-list-result-item-link")
                title = title_element.text.strip()
                link = title_element.get_attribute("href")
                
                # 判断文件类型
                file_extension = ".xlsx" if "xlsx" in link else ".pdf"
                
                # 替换掉文件名中不允许的字符
                safe_title = re.sub(r'[\\/:"*?<>|]', '_', title)
                file_path = os.path.join(download_folder, f"{report_date.date()}_{safe_title}{file_extension}")

                # 下载报告
                response = requests.get(link, stream=True)
                if response.status_code == 200:
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                    print(f"Downloaded: {file_path}")
                else:
                    print(f"Failed to download {title}")

                # 打印报告信息
                print(f"{report_date.date()}: {title} - {link}")

        except Exception as e:
            print("Error processing report:", e)
            continue

    # 移动到下一页
    page += 1
    time.sleep(1)

# 关闭浏览器
driver.quit()

# 打印报告数量
print(f"Total reports found: {len(all_reports)}")
