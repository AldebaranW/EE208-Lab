# SJTU EE208

import re
import urllib.parse
import urllib.request
from http import cookiejar

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

chrome= webdriver.Chrome()

# 1. 构建一个CookieJar对象实例来保存cookie
# cookie = cookiejar.CookieJar()
# # 2. 使用HTTPCookieProcessor()来创建cookie处理器对象，参数为CookieJar()对象
# cookie_handler = urllib.request.HTTPCookieProcessor(cookie)
# # 3. 通过build_opener()来构建opener
# opener = urllib.request.build_opener(cookie_handler)
# # 4. addheaders接受一个列表，里面每个元素都是一个headers信息的元组，opener附带headers信息
# opener.addheaders = [("User-Agent", 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')]
# # 5. 需要登陆的账号和密码, 此处需要使用你们自己注册的账号密码
# data = {"username": "plwu0064",
#         "pwd": "Wu_1654088009",
#         # "formhash": "4A95C39D38",
#         "backurl": "https%3A%2F%2Fwww.yaozh.com%2F"}
sign_in_url = "https://www.yaozh.com/login/"
info_url = "https://www.yaozh.com/member/basicinfo/"

# # 6. 通过urlencode转码
# postdata = urllib.parse.urlencode(data).encode("utf8")
# # 7. 构建Request请求对象，包含需要发送的用户名和密码
# request = urllib.request.Request(sign_in_url, data=postdata,headers = dict(Referer = sign_in_url))
# # 8. 通过opener发送这个请求，并获取登陆后的Cookie值
# opener.open(request)
# # 9. opener包含用户登陆后的Cookie值，可以直接访问那些登陆后才能访问的页面
# response = opener.open(info_url).read()

# 10. The rest is done by you

chrome.get(sign_in_url)
input = chrome.find_element(By.ID, "username")
input.send_keys("plwu0064")
input = chrome.find_element(By.ID, "pwd")
input.send_keys("Wu_1654088009")
time.sleep(5)
chrome.find_element(By.ID, "button").click()
time.sleep(5)

chrome.get(info_url)
response = chrome.page_source



soup = BeautifulSoup(response, 'html.parser')

try:
    div = soup.findAll("div", {"class": "U_myinfo clearfix"})[0]
    dls = div.findAll("dl")
    for dl in dls:
        dt = dl.contents[1].string
        if dt == "真实姓名：":
            input = dl.contents[2].contents[0]
            name = input['value']
        elif dt == "用户名：":
            input = dl.contents[2].contents[0]
            username = input['value']
        elif dt == "性别：":
            input = dl.contents[2].find('input', {"checked": "checked"})
            sex = input['value']
        elif dt == "出生年月：":
            input = dl.contents[2].contents[0]
            date = input['value']
        elif dt == "简介：":
            input = dl.contents[2].contents[0]
            resume = input.string
            
    print(f"真实姓名：{name} \n 用户名：{username} \n 性别：{sex} \n 出生年月：{date} \n 简介：{resume}")       
except: 
    pass
