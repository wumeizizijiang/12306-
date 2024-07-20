#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import requests
import os
import datetime
import json
import selenium
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # 异常处理
from SaveStationData import SaveJson


# 获取selenium版本
# print(selenium.__version__)


# open chrome
class TrainInfo:
    def __init__(self, from_station, to_station, train_date):
        self.from_station = from_station  # 起始车站
        self.to_station = to_station  # 目标车站
        self.train_date = train_date  # 发车时间
        # self.ticket_mod = ticket_mod  # 学生票

    @staticmethod
    def to_initial(station_name):
        """
        根据起始站和目标站的中文名字 在本地文件中找到对应的 字母
        :param station_name: 车站中文名字
        :return: 车站英文简写
        """

        # 判断有无本地文件
        if not os.path.exists('./station.json'):
            saveJson_obj = SaveJson()
            saveJson_obj.main()

        # 打开本地文件获得json数据
        with open('./station.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 拿数据
        try:
            initial = json_data[station_name.encode("utf-8")]
        except KeyError:
            initial = json_data[station_name]

        # print(initial)
        # 拿到数据之后返回
        return initial

    def station_info(self, ):
        """
        :return:
            list_info: 车票信息列表
        """

        # URL可能会随时变动，必要时要更改下
        URL = "https://kyfw.12306.cn/otn/leftTicket/query?"
        # URL = URL + f"leftTicketDTO.train_date={self.train_date}&leftTicketDTO.from_station={from_station_en}&leftTicketDTO.to_station={to_station_en}&purpose_codes=ADULT"

        headers = {
            # 使用时cookie 根据实际的来
            "Cookie": "_uab_collina=171274396125986918807303; JSESSIONID=6305D5F1A0EE9EE50D21993A8F53488E; BIGipServerpassport=1005060362.50215.0000; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; route=9036359bb8a8a461c164a04f8f50b252; BIGipServerotn=1943601418.24610.0000; _jc_save_fromStation=%u897F%u5B89%2CXAY; _jc_save_toStation=%u97E9%u57CE%2CHCY; _jc_save_fromDate=2024-04-11; _jc_save_toDate=2024-04-10; _jc_save_wfdc_flag=dc",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        params = {  # 网页参数
            'leftTicketDTO.train_date': self.train_date,
            'leftTicketDTO.from_station': self.to_initial(self.from_station),
            'leftTicketDTO.to_station': self.to_initial(self.to_station),
            'purpose_codes':  'ADULT',
            # 'purpose_codes': '0X00' if self.ticket_mod == '1' else 'ADULT',  # 0X00 学生票; ADULT 成人票
        }

        r = requests.get(URL, headers=headers, params=params)
        status = r.status_code
        # print(status)
        if status == 200:
            json_data = r.json()
            # print(json_data)

            result = json_data['data']['result']
            list_info = []
            # list_train_number = []
            for i in result:
                # print(i)
                index = i.split('|')

                num = index[3]  # 车次
                fs = index[6]  # 出发站
                ts = index[7]  # 到达站
                s_date = index[8]  # 出发时间
                e_date = index[9]  # 到达时间
                ofs_date = index[10]  # 耗时

                first_lie = index[24]  # 一等软卧
                second_lie = index[25]  # 二等硬卧
                no_seat = index[26]  # 无座
                first_seat = index[31]  # 一等
                second_seat = index[30]  # 二等座二等包座
                top_seat = index[32]  # 商务座特等座

                dit_info = {
                    '车次': num,
                    '出发站': fs,
                    '到达站': ts,
                    '出发时间': s_date,
                    '到达时间': e_date,
                    '耗时': ofs_date,
                    '商务座特等座': top_seat,
                    '一等座': first_seat,
                    '二等座': second_seat,
                    '一等软卧': first_lie,
                    '二等硬卧铺': second_lie,
                    '无座': no_seat,
                }
                list_info.append(dit_info)
            print(datetime.datetime.now())

            # pprint(list_train_number)

            return list_info
        else:
            print(f"http request error, http_status = {status}")


class RobTicket:
    def __init__(self):
        pass

    def get_user_info(self) -> dict:
        """
        获得本地的配置：车次，出发地，目的地，时间，票类型，座类型
        :return: 返回一个字典,包含了配置
        """
        config_path = './config'
        config_dict = dict()

        # 打开用户输入的配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            for i in f:
                key, ves = i.strip(' \n').split('=', 1)
                config_dict[key] = ves

        # 更改格式 转换成列表
        config_dict['乘车人'] = list(config_dict['乘车人'].split(' '))

        # print(config_dict)
        return config_dict

    def get_train_number(self, config_dict: dict, list_info: list) -> int:

        """
        拿到车次的序号，让selenium点击
        //tbody[@id="queryLeftTable"]/TR[1]

        :param config_dict:  用户的配置的字典
        :param list_info:  车站信息列表
        :return:  在列表中实际要请求的id
        """
        count = 1

        seat_name = ['商务座特等座', '一等座', '二等座', '一等软卧', '二等硬卧铺']
        seat_id = config_dict['0商务1一等2二等3软卧4硬卧']

        for item in list_info:
            if item['车次'] == config_dict['车次'] and \
                    item['出发站'] == TrainInfo.to_initial(config_dict['出发站']) and \
                    item['到达站'] == TrainInfo.to_initial(config_dict['到达站']) and \
                    (item[seat_name[int(seat_id)]] == '有' or
                     item[seat_name[int(seat_id)]].isdigit() or
                     item['无座'] == '有' or
                     item['无座'].isdigit()
                    ):
                print(count)
                pprint(item)
                return count * 2 - 1
            count += 1

    def run_selenium(cls, ids: int, fs: str, ts: str, date: str, name_list: list):

        """
        通过selenium一直刷新抢票
        :param ids: selenium选择购买的时候的标签id
        :param fs:起始站（中文）
        :param ts:终点站（中文）
        :param date:发车日期
        :param name_list:购票人->list
        :return:
        """
        # selenium 参数
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 无头模式
        options.add_experimental_option("detach", True)  # 禁止浏览器自动退出

        # 启动浏览器
        browser = webdriver.Chrome(options=options)
        browser.maximize_window()  # 最大化浏览器

        # get请求
        browser.get('https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc')
        browser.find_element(By.ID, 'login_user').click()

        input("登录完成按回车按键继续")

        browser.get(
            f'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={fs},{TrainInfo.to_initial(fs)}&ts={ts},{TrainInfo.to_initial(ts)}&date={date}&flag=N,N,Y')

        # 等待对象
        wait = WebDriverWait(browser, 20)

        while True:
            # 查询
            try:
                wait.until(EC.presence_of_element_located((By.ID, "t-list-bd")))

                btn = browser.find_element(By.XPATH, f'//tbody[@id="queryLeftTable"]/TR[{ids}]/TD/A')
                btn.click()
                break
            except:
                browser.refresh()

        # 等待提交按钮出现
        wait.until(EC.presence_of_element_located((By.ID, 'submitOrder_id')))

        for usr in name_list:
            browser.find_element(By.XPATH,f'//ul[@id="normal_passenger_id"]/li/label[text()="{usr}"]').click()


        # 提交
        browser.find_element(By.ID, 'submitOrder_id').click()

        # 确认提交
        wait.until(EC.presence_of_element_located((By.ID, 'qr_submit_id')))
        while True:
            try:
                # ok_submit = browser.find_element(By.ID, 'qr_submit_id')
                ok_submit = browser.find_element(By.XPATH, '//div[@id="confirmDiv"]/a[@class="btn92s"]')
                time.sleep(0.1)
                ok_submit.click()
                break
            except :
                continue


def main():
    rob = RobTicket()  # 抢票类

    config_data = rob.get_user_info()  # 获得用户信息

    t = TrainInfo(  # 车票类
        config_data['出发站'],
        config_data['到达站'],
        config_data['出发时间'],
        # config_data['1学生/2普通']
    )

    ticket_list_info = t.station_info()  # 查找信息

    # 自动识别
    ids = rob.get_train_number(config_data, ticket_list_info)

    # 手动模式
    # ids = 3 # ID*2-1
    # rob.run_selenium(ids,'威海,WKK','青岛北,QHK','2024-07-30')

    rob.run_selenium(
        ids,
        config_data['出发站'],
        config_data['到达站'],
        config_data['出发时间'],
        config_data['乘车人']
    )


if __name__ == '__main__':
    main()


