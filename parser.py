#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import sys
import os
import re
import random
import string
from bs4 import BeautifulSoup
shangpin = {
        'brand':'',
        'pub_url':"http://daigou.taobao.com/buyer/item/publishItem.htm",
        'buyer_url':"http://daigou.taobao.com/buyer/index.htm",
        'params_sub_url':{
            "action":"/buyer/submit_url_action", 
            "event_submit_do_submit_url":"anything", 
            "_tb_token_":'',    #
            "itemUrl":'',   #
        },

         'params_sub_category':{
            "encodeUrl":'', #
            "itemId":'0',   #固定
            "_tb_token_":'',    #
            'category1':'2',  #暂固定为鞋包饰品
            'category2':'201', #暂固定为女士箱包
            'categoryId':400002, #暂时为女士手提包
            "确认":"开始发布"
        },

        'data':{
            "_tb_token_":'',    #
            "action":"/buyer/save_action",
            "event_submit_do_submit":"anything",
            "itemUrl":'',#
            "itemId":'0', #
            'categoryId':'400002',#暂时为女士手提包
            "shopId":"1",                       #暂时固定为Amazon
            "shopName":"Amazon",                #暂时固定为Amazon
            "transportTemplate":"2",            #暂时固定为笨鸟转运美国线
            "overseasTransportFee":"0",      #暂时固定为0
            "title":'',     #暂时固定为空
            "titleCn":'',   #
            "subtitle":'',  #
            "mobileTitle":'',   #
            "itemPrice":'',   #
            "weight":'',    # 
            "stock":'1',     #暂时固定为1
            "limitNum":'1', # 暂时固定为1 
            "brandSelect":'8947490',#
            "pictureUrl":'',#
            "pic1":'',#
            "pic2":'',# 
            "pic3":'',#
            "pic4":'',#
            "pic5":'',#
            "internalPrice":'',#
            "description":''#
            }
        }

SHOP_LIST = {
        "Amazon" : '1',
        "eBay" : '2',
        "6PM" : '3',
        "jomashop" : '47',
        "Ashford" : '16',
        "Amazon.jp" : '49'
        }

ua_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        }


def get_org_url(content_soup,shop_id):
    org_url_soup = content_soup.find('a',text='直达官网链接')
    org_url = org_url_soup.get('href')
    org_url = 'http://daigou.taobao.com'+ org_url
    rsp = requests.get(org_url,headers=ua_headers)
    if rsp.status_code == 200:
    #    return "http://www.amazon.com/gp/aw/d/" + rsp.url.split('/')[-1] + ('?ref=mp_s_a_1_1?qid=1460111142&sr=8-1&keywords=%s' % (rsp.url.split('/')[-1]))
    
        if shop_id == SHOP_LIST["Amazon"]:
            #shop_code = rsp.url.split('/')[-1]
            shop_code = rsp.url.split("dp/")[-1].split('/')[0]
            url = 'http://www.amazon.com/gp/aw/d/' + shop_code + '/' + ''.join(random.sample(string.ascii_letters + string.digits, 10))
        elif shop_id == SHOP_LIST["eBay"]:
            url = rsp.url.split('?')[0] + '/' + ''.join(random.sample(string.digits, 10))
        elif shop_id == SHOP_LIST["6PM"]:
            url = rsp.url + '?' + ''.join(random.sample(string.digits, 7))
        elif shop_id == SHOP_LIST["jomashop"]:
            url = rsp.url + '?' + ''.join(random.sample(string.digits, 7))
        elif shop_id == SHOP_LIST["Ashford"]:
        #    url = rsp.url + "?ref=http://www.guanggoo.com/t/5777"
            url = rsp.url.split('?')[0].split('.pid')[0] + ''.join(random.sample(string.ascii_letters, 2)) + '.pid'
        elif shop_id == SHOP_LIST["Amazon.jp"]:
            url=rsp.url
            if "/product/" in rsp.url:
                shop_code = rsp.url.split("product/")[-1].split('/')[0]
                url = 'http://www.amazon.co.jp/gp/aw/d/' + shop_code + '/' + ''.join(random.sample(string.ascii_letters + string.digits, 10))
            elif "/dp/" in rsp.url:
                shop_code = rsp.url.split("dp/")[-1].split('/')[0]
                url = 'http://www.amazon.co.jp/gp/aw/d/' + shop_code + '/' + ''.join(random.sample(string.ascii_letters + string.digits, 10))
            shangpin['data']['transportTemplate'] = '17'
        return url
    else:
        return None

def parser_url(url):
    target = requests.get(url,headers=ua_headers)
    #html_file = open("html_file.html",'r')
    #org_soup = BeautifulSoup(html_file,"html.parser")
    org_soup = BeautifulSoup(target.text,"html.parser")

    soup_shop = org_soup.find('div',attrs={'class':'hd'})
    shangpin['data']['shopName'] = soup_shop.a.text
    shangpin['data']['shopId'] = SHOP_LIST[shangpin['data']['shopName']]

#    print("shopName:%s shopId:%s" % (shangpin['data']['shopName'],shangpin['data']['shopId']))

    content_soup = org_soup.find('div',attrs={'class':'content clearfix'}) 
    org_url = get_org_url(content_soup,shangpin['data']['shopId'])
    if org_url == None:
        return False
    shangpin['params_sub_url']['itemUrl'] = org_url
    shangpin['params_sub_category']['encodeUrl'] = org_url
    shangpin['data']['itemUrl'] = org_url
    
    
    info_soup = org_soup.find('div',attrs={'class':'detail-info'}) 
    title_soup = info_soup.find('h1',attrs={'class':'title'})
    #shangpin['data']['titleCn'] = title_soup.text.split('】')[1]
    shangpin['data']['titleCn'] = re.sub(r"【直购】",'',title_soup.text)
    shangpin['data']['titleCn'] = re.sub(r"【可用券】",'',shangpin['data']['titleCn'])
    #p = re.compile(r'^[\u4e00-\u9fa5]*[A-Za-z,【]{0}')
    p1 = re.compile(r'^.*[A-Za-z,【]')
    m = p1.match(shangpin['data']['titleCn'])
    if m:
        p = re.compile(r'^[^A-Za-z,【]+')
        shangpin['data']['titleCn'] =  p.sub('',shangpin['data']['titleCn'])
    shangpin['data']['titleCn']= shangpin['data']['titleCn'][0:52]
    shangpin['data']['mobileTitle'] = shangpin['data']['titleCn']
    if shangpin['data']['subtitle'] == '':
        subtitle_soup = info_soup.find('div',attrs={'class':'info-adwords'})
        shangpin['data']['subtitle'] = subtitle_soup.text[0:52]
    brand_soup = info_soup.find('span')
    shangpin['brand'] = brand_soup.text
    #for line in brand_list.readlines():
    #    m  = re.findall(brand,line,re.I)
    #    if m:
    #        shangpin['data']['brandSelect']=line.split(' ')[0]

    price_soup = info_soup.find('div',attrs={'class':'price-info'})
    price_soup = price_soup.find('span',attrs={'class':'lb-value usd-price J-usd-price'})
    shangpin['data']['itemPrice'] = price_soup.text.split(' ')[0].split('（')[1]
    price_soup = info_soup.find('div',attrs={'class':'price-plus'})
    price_soup = price_soup.find('span',attrs={'class':'lb-value J-ref-price'})
    #shangpin['data']['internalPrice'] = price_soup.text.split('￥')[1]
    #shangpin['data']['internalPrice'] = str(float(shangpin['data']['itemPrice'])*6.5*2.5)
    if shangpin['data']['shopId'] == SHOP_LIST["Amazon.jp"]:
        price_min = int(float(shangpin['data']['itemPrice'])*0.0598*2)
        price_max = int(float(shangpin['data']['itemPrice'])*0.0598*3)
        price = random.randint(price_min,price_max)
        shangpin['data']['internalPrice'] = str(price)
    else:
        price_min = int(float(shangpin['data']['itemPrice'])*6.5*2)
        price_max = int(float(shangpin['data']['itemPrice'])*6.5*3)
        price = random.randint(price_min,price_max)
        shangpin['data']['internalPrice'] = str(price)

    weight_soup = org_soup.find('div',attrs={'class':'weight-info'})
    weight_soup = weight_soup.find('span',attrs={'class':'lb-value J-weight'})
    #shangpin['data']['weight'] = weight_soup.text.split('磅')[0]
    shangpin['data']['weight'] = "2"

    product_soup = org_soup.find('div',attrs={'class':'nav-list-wrapper'})
    img_soup = product_soup.find_all('img')
    img = ['','','','','','','','','','']
    p=re.compile(r'_\d{3}x\d{3}.+\d$')
    for k,v in enumerate(img_soup):
        img[k] = "http:"+(v.get('data-ks-imagezoom'))
        img[k] = p.split(img[k])[0]
    shangpin['data']['pictureUrl'] = img[0]
    shangpin['data']['pic1'] = img[1]
    shangpin['data']['pic2'] = img[2]
    shangpin['data']['pic3'] = img[3]
    shangpin['data']['pic4'] = img[4]
    
    product_soup = org_soup.find('div',attrs={'class':'product-desc-wrapper'})
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'img.alicdn.com/tps/')})
    for i in del_img:
        i.decompose()
    '''
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'TB1NInJHVXXXXaOXVXXXXXXXXXX')})
    for i in del_img:
        i.decompose()
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'TB1gCBbJVXXXXb0XXXXXXXXXXXX')})
    for i in del_img:
        i.decompose()
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'TB12BcrJFXXXXXZapXXXXXXXXXX')})
    for i in del_img:
        i.decompose()
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'TB2Csz7gFXXXXblXXXXXXXXXXXX')})
    for i in del_img:
        i.decompose()
    del_img = product_soup.find_all('img',attrs={"src":re.compile(r'TB1nMsIIXXXXXXsaXXXXXXXXXXX')})
    for i in del_img:
        i.decompose()
    '''
    del_a = product_soup.find_all('a')
    for i in del_a:
        i.decompose()
    shangpin['data']['description'] = str(product_soup)
    if shangpin['data']['shopId'] != SHOP_LIST["Amazon.jp"]:
        p=re.compile(r'<span style=".+;">')
        shangpin['data']['description'] = p.sub('',shangpin['data']['description'])
        p=re.compile(r'</span>')
        shangpin['data']['description'] = p.sub('',shangpin['data']['description'])

    p=re.compile(r'<strong>')
    shangpin['data']['description'] = p.sub('',shangpin['data']['description'])
    p=re.compile(r'</strong>')
    shangpin['data']['description'] = p.sub('',shangpin['data']['description'])

    p=re.compile(r'<font [^>]+>')
    shangpin['data']['description'] = p.sub('',shangpin['data']['description'])
    p=re.compile(r'</font>')
    shangpin['data']['description'] = p.sub('',shangpin['data']['description'])

    p = re.compile(r'style="[^>]+;"')
    shangpin['data']['description'] = p.sub('',shangpin['data']['description'])
    p=re.compile(r'class="product-desc-wrapper"')
    shangpin['data']['description'] = p.sub('''class="product-desc-wrapper" align="center"''',shangpin['data']['description'])

    #for k,v in shangpin['data'].items():
    #   print('%s=%s' % (k,v))
    #print("-------------parser end--------------\r\n")
    return True

if __name__ == '__main__':
    url = sys.argv[1]
    parser_url(url)
