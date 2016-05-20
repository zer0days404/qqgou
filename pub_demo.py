#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, session, request
from flask.ext.session import Session
from flask import render_template
import copy
import requests
import sys
import json
import base64
import sys
from parser import *
from tb_config import *
import re
import codecs
import urllib.parse
import time
import random
import datetime

app = Flask(__name__)

@app.route('/crawler/', methods=['GET', 'POST'])
def crawler():
    global sess,lgToken,user_name
    error = ''
    button_name = "重新登录"
    loop_time = 1
    sleep_min = 1
    sleep_max = 3
    if request.method == 'POST': 
        #print(request.form)
        url = request.form['url']
        shop_list = request.form['shop_list']
        sleep = request.form['sleep_time']
        if request.form['loop_time']:
            loop_time = int(request.form['loop_time'])
            if loop_time > 10 or loop_time < 0:
                    error = "请输入合法循环次数，最多不能超过10次"
                    return render_template('crawler.html', error1=error,button_name=button_name,user_name = user_name)

        if sleep: 
            if sleep.split('-')[0].isdigit() and sleep.split('-')[1].isdigit():
                sleep_min = sleep.split('-')[0]
                sleep_max = sleep.split('-')[1]
            else:
                error = "请输入合法sleep区间"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name = user_name)


        if shop_list:
            rv = shop_list.replace('|','').isdigit()
            if rv == False: 
                error = "请输入合法商品列表，以|隔开!"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name = user_name)
            else:
                shop_list = shop_list.split('|')

        p = re.compile(r'^http.+')
        m = p.match(url)
        if url and m == None:
            error = "请输入合法url!"
            return render_template('crawler.html', error1=error,button_name=button_name,user_name = user_name)

        subtitle = request.form['subtitle']
        if subtitle:
            shangpin['data']['subtitle'] = subtitle[0:52]
        category1 = request.form['category1']
        if category1:
            shangpin['params_sub_category']['category1'] = category1
            category2 = request.form['category2']
            if category2:
                shangpin['params_sub_category']['category2'] = category2
                categoryId = request.form['categoryId']
                shangpin['data']['categoryId'] = categoryId
                shangpin['params_sub_category']['categoryId'] = categoryId
            else:  
                error = "请选择二级分类!"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

        if url:
            rv = parser_url(url)
            if rv == False:
                error = "官网直达链接不可达，请检查"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

            error_code = pub_shangpin_final()
            now = datetime.datetime.now()
            tm = now.strftime("%Y-%m-%d %H:%M:%S")
            if error_code:
                print("pub failed:[%s] [%s] [%s]\n" % (url,tm,error_code))
                error = error_code
            else:
                error = "发布成功！"
                print("pub success:[%s] [%s]\n" % (url,tm))
            return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
        #print(sleep_min,sleep_max,loop_time)
        if shop_list:
            success_ = []
            failed_ = []
            for i in range(0,loop_time):
                for id in shop_list:
                    try:
                        url = "http://daigou.taobao.com/item.htm?&id=" + id
                        rv = parser_url(url)
                        if rv == False:
                            failed_.append(id)
                            continue

                        error_code = pub_shangpin_final()
                        now = datetime.datetime.now()
                        tm = now.strftime("%Y-%m-%d %H:%M:%S")
                        if error_code:
                            print("pub failed:[%s] [%s] [%s]\n" % (url,tm,error_code))
                            failed_.append(id)
                        else:
                            print("pub success:[%s] [%s]\n" % (url,tm))
                            success_.append(id)
                        tm = random.randint(int(sleep_min),int(sleep_max))
                        time.sleep(tm)
                        continue
                    except:
                        continue
                error = "success:%s" % success_
                error += "\n"
                error += "failed:%s" % failed_
            return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)


    return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

@app.route('/relogin/', methods=['GET', 'POST'])
def relogin():
    global sess,lgToken,user_name
    error = ''
    qr_img = ''
    #print(request.form)
    if request.method == 'POST':
        relogin_is = request.form['relogin_button']
        if relogin_is == "扫描完成":
            button_name = "重新登录"
            url = qrcode_check_url + lgToken
            url += qrcode_check_params 
            rsp = sess.get(url)
            b = json.loads(rsp.text)
            now = datetime.datetime.now()
            tm = now.strftime("%Y-%m-%d %H:%M:%S")
            if b['success'] == True:
                if b.get('url'):
                    rsp = sess.get(b['url'])
                else:
                    error = "登陆失败"
                    print("login failed:[%s] [%s]\n" % (user_name,tm))
                    return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
                #print(sess.cookies.get_dict().get('lgc')) 
                #print(sess.cookies.get_dict().get('_nk_')) 
                user_name = sess.cookies.get_dict().get('_nk_')
                user_name = urllib.parse.unquote(user_name)
                user_name = codecs.decode(user_name,'unicode-escape')
                error = "登陆成功！"
                print("login success:[%s] [%s]\n" % (user_name,tm))
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
            else:
                button_name = "重新登录"
                error = "登录超时"
                print("login failed:[%s] [%s]\n" % (user_name,tm))
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
                
        rsp = sess.get(generate_qrcode)
        if rsp == None:
            error = "获取二维码失败，请再次点击登录！" 
            button_name = "重新登录"
            return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

        b = json.loads(rsp.text)
        #print(b)
        qr_img = b['url']
        lgToken = b['lgToken']
        button_name = "扫描完成"
        return render_template('crawler.html', qr_img=qr_img,button_name=button_name,user_name=user_name)

    button_name = "重新登录"
    return render_template('crawler.html', qr_img=qr_img,button_name=button_name,user_name=user_name)

def befor_pub_shangpin():
    global sess
    shangpin['params_sub_category']['_tb_token_'] = sess.cookies['_tb_token_']
    #print(shangpin['params_sub_category'])
    rsp = sess.get(shangpin['pub_url'],params=shangpin['params_sub_category'])
    org_soup = BeautifulSoup(rsp.text,"html.parser")
    if shangpin['brand']:
        content_soup = org_soup.find('select',attrs={'id':'brandSelect'})
        tag = content_soup.find(text=re.compile(shangpin['brand']))
        #print(content_soup)
        if tag:
            shangpin['data']['brandSelect'] = tag.parent.get('value')
        else:
            p1 = re.compile(r'^[A-Za-z, ]+[A-Za-z]')
            m = p1.match(shangpin['brand'])
            #print(m.group())
            if m:
                tag2 = content_soup.find(text=re.compile(m.group()))
                if tag2:
                    shangpin['data']['brandSelect'] = tag2.parent.get('value')
                else:
                    option_soup = content_soup.find_all('option')
                    if option_soup:
                        shangpin['data']['brandSelect'] = option_soup[-1].get('value')
    #print("brand:%s brandSelect:%s\n" % (shangpin['brand'],shangpin['data']['brandSelect']))
    soup_ = org_soup.find('div',attrs={'class':'container'})
    if soup_:
        error = "error3:" + soup_.text
        return error
    else:
        return None

def pub_shangpin():
    global sess
    shangpin['params_sub_category']['_tb_token_'] = sess.cookies['_tb_token_']
    rsp = sess.post(shangpin['pub_url'],params=shangpin['params_sub_category'],data=shangpin['data'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    tag = soup.find(text=re.compile('代拍买手后台'))
    if tag:
        return None
    else:
        soup_ = soup.find('div',attrs={'class':'container'})
        if soup_:
            error = "error4:" + soup_.text
        else:
            error = "error4"
        return error

def get_choose_category():
    #提交url,进入选择类目页面
    global sess
    shangpin['params_sub_url']['_tb_token_'] = sess.cookies['_tb_token_']
    rsp = sess.get(shangpin['buyer_url'],params=shangpin['params_sub_url'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    soup_ = soup.find('div',attrs={'class':'form-group'})    
    if soup_ == None:
        soup_ = soup.find('div',attrs={'class':'container'})
        if soup_:
            error = "error2" + soup_.text
        else:
            error = "error2:"
        return error
    else:
        return None


def get_index():
    global sess
    rsp = sess.get(shangpin['buyer_url'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    if soup.title.text != "全球购官网直购":
        error = "error1:no login,please login"
        return error
    else:
        return None

def pub_shangpin_final():
    error_code = None
    error_code = get_index()
    if error_code != None:
        return error_code

    error_code = get_choose_category()
    if error_code != None:
        return error_code

    tm = random.randint(1,3)
    time.sleep(tm)
    error_code = befor_pub_shangpin()
    if error_code != None:
        return error_code
    error_code = pub_shangpin()
    if error_code != None:
        return error_code
    return error_code

if __name__ == '__main__':
    global sess,lgToken,user_name
    user_name = ''
    lgToken = ''
    sess = requests.session()
    if len(sys.argv) > 1:
        lsp = login_tb()
        if lsp == None:
            sys.exit(-1)
        url = sys.argv[1]
        parser_url(url)
        pub_shangpin_final()
    else:
        app.run(host="0.0.0.0", port=8757, debug=True)
