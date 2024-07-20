#!/usr/bin/python
# -*- coding: utf-8 -*-

# 测试分割车站信息格式表
import os
import json

class SaveJson:
    def parse_station_json(self,):
        """
            解析station.txt文档通过python语言解析
        """
        # path = os.path.join(os.path.dirname(__file__), 'station_name.txt')
        path = os.path.join(os.getcwd(), 'station_name.txt') # station文件绝对路径
        
        
        # 获得txt文件内容,并简单解析
        try: 
            with open(path, encoding="utf-8") as f:
                print(f)
                info = f.read().split('=')[1].strip("'").split('@')
        except Exception:
            with open(path) as f:
                info = f.read().split('=')[1].strip("'").split('@')

        del info[0] # 删除第一个没用的元素
        
        # 新建一个空字典
        station_item = {}
        
        # 遍历拿到首字母跟中文信息并保存到dict中
        for i in range(0, len(info)):
            n_info = info[i].split('|')
            station_item[n_info[1]] = n_info[2] # 'sfx|什邡西|SFE|shifangxi|sfx|3339|1704|德阳|||' 

        return station_item # 将保存的信息返回出去 
    
    
    def save_json(self,data):
        """
            将数据保存为本地的json格式 GBK编码(默认)
        """
        
        with open('station.json','w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False)
            
    def main(self,):
        station_json = self.parse_station_json()
        self.save_json(station_json)

if __name__ == '__main__':
    obj = SaveJson()
    obj.main()
