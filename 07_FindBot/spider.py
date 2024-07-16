from selenium import webdriver 
import time

# 设置 Chrome 的启动选项
options = webdriver.ChromeOptions() 
options.add_argument("--headless") 
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0") 
driver = webdriver.Chrome(options=options)

# 访问指定网页并获取页面内容
driver.get('https://space.bilibili.com/2031883173/dynamic') 
time.sleep(2) 
page = driver.page_source

with open('page1.html', 'w', encoding='utf-8') as file: 
    file.write(page)