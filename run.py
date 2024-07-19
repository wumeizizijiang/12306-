# -*- coding: utf-8 -*-

import time
import requests
import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 获取selenium版本
import selenium


# print(selenium.__version__)


# open chrome
class TrainInfo:
    def __init__(self, from_station, to_station, train_date):
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date

    def station_table_to_en(self, from_station, to_station):
        path = os.path.join(os.path.dirname(__file__), 'station_name.txt')
        try:
            with open(path, encoding="utf-8") as result:
                info = result.read().split('=')[1].strip("'").split('@')
        except Exception:
            with open(path) as result:
                info = result.read().split('=')[1].strip("'").split('@')
        del info[0]
        station_name = {}
        for i in range(0, len(info)):
            n_info = info[i].split('|')
            station_name[n_info[1]] = n_info[2]
        try:
            from_station_en = station_name[from_station.encode("utf8")]
            to_station_en = station_name[to_station.encode("utf8")]
        except KeyError:
            from_station_en = station_name[from_station]
            to_station_en = station_name[to_station]
        return from_station_en, to_station_en

    def station_info(self):
        from_station_en, to_station_en = self.station_table_to_en(self.from_station, self.to_station)

        # URL可能会随时变动，必要时要更改下
        URL = "https://kyfw.12306.cn/otn/leftTicket/queryG?"
        URL = URL + f"leftTicketDTO.train_date={self.train_date}&leftTicketDTO.from_station={from_station_en}&leftTicketDTO.to_station={to_station_en}&purpose_codes=ADULT"
        headers = {
            # 使用时cookie 根据实际的来
            "Cookie": "_uab_collina=171274396125986918807303; JSESSIONID=6305D5F1A0EE9EE50D21993A8F53488E; BIGipServerpassport=1005060362.50215.0000; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; route=9036359bb8a8a461c164a04f8f50b252; BIGipServerotn=1943601418.24610.0000; _jc_save_fromStation=%u897F%u5B89%2CXAY; _jc_save_toStation=%u97E9%u57CE%2CHCY; _jc_save_fromDate=2024-04-11; _jc_save_toDate=2024-04-10; _jc_save_wfdc_flag=dc",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        resp = requests.get(URL, headers=headers)
        http_status = resp.status_code
        # print(http_status)
        if (http_status == 200):
            json_data = resp.json()
            result = json_data['data']['result']
            list_info = []
            list_train_number = []
            for i in result:
                index = i.split('|')
                # 车次
                num = index[3]
                list_train_number.append(num)
                # 出发站
                from_station = index[6]
                # 到达站
                to_station = index[7]
                # 出发时间
                start_time = index[8]
                # 到达时间
                end_time = index[9]
                # 耗时
                offset_time = index[10]
                # 商务座特等座
                top_seat = index[32]
                # 一等
                first_seat = index[31]
                # 二等座二等包座
                second_seat = index[30]
                # 高级软卧
                # 无座
                no_seat = index[26]
                # 其他
                dit_info = {
                    '车次': num,
                    '出发站': from_station,
                    '到达站': to_station,
                    '出发时间': start_time,
                    '到达时间': end_time,
                    '耗时': offset_time,
                    '商务座特等座': top_seat,
                    '一等座': first_seat,
                    '二等座': second_seat
                }
                list_info.append(dit_info)
            print(datetime.datetime.now())
            # print(list_info)
            print(list_train_number)
            return list_info, list_train_number
        else:
            print(f"http request error, http_status = {http_status}")


def get_usr_info() -> dict:
    config_file_path = 'config'
    config_dict = {}
    with open(config_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and '=' in line:
                key, value = line.split('=', 1)
                config_dict[key.strip()] = value.strip()
    # print(config_dict)
    return config_dict


def station_table(from_station: str, to_station: str) -> tuple:
    path = os.path.join(os.path.dirname(__file__), 'station_name.txt')
    try:
        with open(path, encoding="utf-8") as result:
            info = result.read().split('=')[1].strip("'").split('@')
    except Exception:
        with open(path) as result:
            info = result.read().split('=')[1].strip("'").split('@')
    del info[0]
    station_name = {}
    for i in range(0, len(info)):
        n_info = info[i].split('|')
        station_name[n_info[1]] = n_info[2]
    try:
        from_station = station_name[from_station.encode("utf8")]
        to_station = station_name[to_station.encode("utf8")]
    except KeyError:
        from_station = station_name[from_station]
        to_station = station_name[to_station]
    return from_station, to_station


def get_train_number(train_num: str, list_train_info: list) -> int:
    count = 1
    num = 0
    for item in list_train_info:
        if (item['车次'] == train_num) and (item['一等座'] == '有' or item['一等座'].isdigit()):
            num = count * 2 - 1
            return num
        else:
            count = count + 1
    return num


usr_info = get_usr_info()

open_chrome = webdriver.Chrome('chromedriver.exe')

open_chrome.get('https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc')

open_chrome.find_element(By.ID, 'login_user').click()

input("登录完成点击回车")

# # 账号
# open_chrome.find_element(By.ID, 'J-userName').send_keys(usr_info['用户名'])
# # 密码
# open_chrome.find_element(By.ID, 'J-password').send_keys(usr_info['密码'])
#
# open_chrome.find_element(By.ID, 'J-login').click()
#
# time.sleep(1)


# open_chrome.find_element(By.ID, 'id_card').send_keys(usr_info['id_card'])
# time.sleep(1)
# # input()
# open_chrome.find_element(By.ID, 'verification_code').click()
# code = input('验证码:')

# open_chrome.find_element(By.ID, 'code').send_keys(code)

# open_chrome.find_element(By.ID, 'sureClick').click()
#
# time.sleep(1)

# 点击车票预订
open_chrome.find_element(By.ID, 'link_for_ticket').click()

list_info = []
list_train_number = []
train_num = usr_info['车次']
trainInfo = TrainInfo(usr_info['出发地'], usr_info['目的地'], usr_info['时间'])

# 输出出发站
edit_from_station = open_chrome.find_element(By.ID, 'fromStationText')
edit_from_station.click()
edit_from_station.clear()
edit_from_station.send_keys(usr_info['出发地'])

# 如果需要，使用箭头键在建议列表中导航
edit_from_station.send_keys(Keys.ARROW_DOWN)
edit_from_station.send_keys(Keys.ENTER)

# 输入目的地
edit_to_station = open_chrome.find_element(By.ID, 'toStationText')
edit_to_station.click()
edit_to_station.clear()
edit_to_station.send_keys(usr_info['目的地'])
edit_to_station.send_keys(Keys.ENTER)

# 输入时间
edit_time = open_chrome.find_element(By.ID, 'train_date')
edit_time.click()
edit_time.clear()
edit_time.send_keys(usr_info['时间'])

# input() # 阻塞


while True:

    # 查询
    btn = open_chrome.find_element(By.ID, 'query_ticket')
    btn.click()

    # open_chrome.refresh()
    list_info, list_train_number = trainInfo.station_info()
    num = get_train_number(train_num, list_info)
    print(num)
    if (num != 0):
        # 等待元素的出现
        time.sleep(1)

        open_chrome.find_element(By.CSS_SELECTOR, f'#queryLeftTable tr:nth-child({num}) .btn72').click()

        # 等待元素的出现
        time.sleep(1)

        # 选择一等座， 默认时二等座
        select_seat = open_chrome.find_element(By.ID, 'seatType_1')
        # select_seat.send_keys(Keys.ARROW_DOWN)
        select_seat.send_keys(Keys.ENTER)

        # 选择乘车人
        open_chrome.find_element(By.ID, 'normalPassenger_0').click()
        # open_chrome.find_element(By.ID, 'normalPassenger_2').click()
        open_chrome.find_element(By.ID, 'submitOrder_id').click()

        time.sleep(3)
        # 确认
        open_chrome.find_element(By.ID, 'qr_submit_id').click()
        break
    time.sleep(1)

input("按回车键继续...")
exit()
