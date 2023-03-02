# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 14:07:05 2021

@author: jiahachen
"""

import requests 
import pandas as pd
import os
import numpy as np
import time

import math
def geo_distance(origin, destination):
    '''origin = (48.1372, 11.5756)  # Munich
    destination = (52.5186, 13.4083)  # Berlin
    round(distance(origin, destination), 1)
    504.2'''
    
    lat1, lon1 = origin
    lat2, lon2 = destination
    lat1, lon1 = float(lat1), float(lon1)
    lat2, lon2 = float(lat2), float(lon2)
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

root = r'C:\Users\jiahachen\Desktop\Working Desk\July. 2021 - Project GB\Database\VS'
os.chdir(root)

hospital_list = pd.read_csv('公司名单.csv', encoding='gbk')

####

target_keyword = hospital_list['名称'][0]
city = '全国'
parameters = {'query':target_keyword, 'region':city, 'scope':'2', 'ak':AK, 'output':'json', \
              'ret_coordtype':coor_base}
response = requests.get(URL, parameters)
res = response.json()
res_dt_detail = pd.DataFrame({'uid':[], 'detail_str':[]})
temp = pd.DataFrame({'uid':[uid_slct], 'detail_str':[res['results']['address']]})

res_dt_detail = pd.DataFrame({'name':[], 'address_name':[], 'detail_str':[]})

for i in range(lens_res):

    response = requests.get(URL, parameters)
    res = response.json()
    try:
        temp = pd.DataFrame({'name':target_keyword , 'address_name':[res['results'][0]['detail_info']['children'][0]['name']], 'detail_str':[res['results'][0]['detail_info']['children'][0]['address']]})
    except KeyError:
        temp = pd.DataFrame({'name':target_keyword , 'address_name':[res['results'][0]['detail_info']['children'][0]['name']], 'detail_str':[res['results'][0]['detail_info']['children'][0]['address']]})
    res_dt_detail = res_dt_detail.append(temp)
    time.sleep(0.5)


####

target_keyword = 'XXXXX医院'
target_ls = hospital_list['名称']
city_ls = hospital_list['市']
poitypes = '090100|090101|090200|090201|090202|090203|090204|090205|090206|090207|090208|090209|090210|090211'
URL = 'http://api.map.baidu.com/place/v2/search?parameters'
URL3 = 'http://api.map.baidu.com/place/v2/search?parameters'
URL4 = 'http://api.map.baidu.com/place/v2/detail?parameters'
AK = 'XXXXXXXX'
coor_base = 'bd09ll'

res_dt = pd.DataFrame()

for target_keyword, city in zip(target_ls, city_ls):
    
    parameters = {'query':target_keyword, 'region':city, 'tag':'医疗', 'scope':'2', 'ak':AK, 'output':'json', \
                  'ret_coordtype':coor_base}
    response = requests.get(URL, parameters)
    res = response.json()
    if res['results'] == []:
        print(target_keyword+' cannot be searched in Baidu Map')
        continue
    gps = res['results'][0]['location']
    searched_name = res['results'][0]['name']
    gps1 = str(gps['lat'])+','+str(gps['lng'])
    print('Get the GPS of '+target_keyword)
    
    for i in range(100):
        parameters3 = {'query':'医院', 'location':gps1, 'tag':'医疗', 'radius':'5000', 'radius_limit':'true',\
                       'output':'json', 'scope':'2',\
                       'ak':AK, 'page_size':'20', 'page_num':str(i),'ret_coordtype':coor_base}
        response3 = requests.get(URL3, parameters3)
        res3 = response3.json()
        
        if res3['results'] == []:
            print(target_keyword+' no competitor in 5KM')
            break
        
        lens_res = len(res3['results'])
        res_dt_detail = pd.DataFrame({'uid':[], 'detail_str':[]})

        for i in range(lens_res):
            uid_slct = res3['results'][i]['uid']
            parameters4 = {'uid':uid_slct, 'output':'json', 'scope':'2', 'ak':AK}
            response4 = requests.get(URL4, parameters4)
            res4 = response4.json()
            try:
                temp = pd.DataFrame({'uid':[uid_slct], 'detail_str':[res4['result']['detail_info']['content_tag']]})
            except KeyError:
                temp = pd.DataFrame({'uid':[uid_slct], 'detail_str':[res4['result']['detail_info']['tag']]})
            res_dt_detail = res_dt_detail.append(temp)

        
        data1 = res3['results']
        data2 = pd.DataFrame.from_dict(data1)
        data2 = pd.merge(data2, res_dt_detail, how='left', on=['uid'])
        data2['target_hospital'] = target_keyword
        data2['searched_name'] = searched_name
        data2['vs_gps'] = gps1       
        res_dt = res_dt.append(data2)
        print('Done for '+target_keyword)
        
        if len(res3['results']) < 25:
            break
        
        time.sleep(0.5)


res_dt['location_trans'] = res_dt.apply(lambda rows: str(rows['location']['lat'])+','+str(rows['location']['lng']),axis=1)
res_dt['distance'] = res_dt.apply(lambda col: geo_distance(col['vs_gps'].split(','), col['location_trans'].split(',')), axis=1)

res_dt.to_csv('DR_full_BDMAP_full.csv', encoding='gbk')

proc_data = res_dt[~res_dt['name'].str.contains('住院|急诊|急救|挂号|门诊|美容|视力|口腔|生殖|健康管理|室|楼|服务站|区|牙|药业|药房|药店|卫生院|诊所')]
proc_data = proc_data[~proc_data['detail_str'].str.contains('其他')]
proc_data = proc_data[proc_data['name'].str.contains('医院')]
proc_data2 = proc_data[proc_data['detail_str'].str.contains('三级|二级|三甲|三乙|三丁|二甲|二乙|二丁')]

proc_data.to_csv('DR_full_BDMAP_full3.csv', encoding='gbk')

proc_data2.to_csv('DR_full_BDMAP_full_selected3.csv', encoding='gbk')










######

URL4 = 'http://api.map.baidu.com/place/v2/detail?parameters'
lens_res = len(res3['results'])
res_dt_detail = pd.DataFrame({'uid':[], 'detail':[]})

for i in range(lens_res):
    uid_slct = res3['results'][i]['uid']
    parameters4 = {'uid':uid_slct, 'output':'json', 'scope':'2', 'ak':AK}
    response4 = requests.get(URL4, parameters4)
    res4 = response4.json()
    temp = pd.DataFrame({'uid':[uid_slct], 'detail':[res4['result']['detail_info']['content_tag']]})
    res_dt_detail = res_dt_detail.append(temp)
    

