#!/usr/bin/env python
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

app = Flask(__name__)

@app.route('/crawler/', methods=['GET', 'POST'])
def crawler():
    global sess,lgToken,user_name
    error = ''
    error_code = 0
    button_name = "重新登录"
    if request.method == 'POST': 
        print(request.form)
        url = request.form['url']
        p = re.compile(r'^http.+')
        m = p.match(url)
        if m == None:
            error = "请输入合法url!"
            return render_template('crawler.html', error1=error,button_name=button_name,user_name = user_name)

        subtitle = request.form['subtitle']
        if subtitle:
            shangpin['data']['subtitle'] = subtitle[0:27]
        category1 = request.form['category1']
        if category1:
            shangpin['params_sub_category']['category1'] = category1
            category2 = request.form['category2']
            if category2:
                shangpin['params_sub_category']['category2'] = category2
                categoryId = request.form['categoryId']
                shangpin['data']['categoryId'] = categoryId
            else:  
                error = "请选择二级分类!"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

        parser_url(url)
        #return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
        error_code = pub_shangpin_final()
        if error_code == 1:
            error = "打开buyer首页失败，一般是因为登录失败造成"
        elif error_code == 2:
            error = "提交类别错误，一般是因为登录失败或类别选择失败"
        elif error_code == 3:
            error = "商品发布失败，一般是因为登录失败或表单构造出错"
        elif error_code == 0:
            error = "商品发布成功，请查看"

    return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

@app.route('/relogin/', methods=['GET', 'POST'])
def relogin():
    global sess,lgToken,user_name
    error = ''
    qr_img = ''
    print(request.form)
    if request.method == 'POST':
        relogin_is = request.form['relogin_button']
        if relogin_is == "扫描完成":
            button_name = "重新登录"
            url = qrcode_check_url + lgToken
            url += qrcode_check_params 
            rsp = sess.get(url)
            b = json.loads(rsp.text)
            print(b)
            if b['success'] == True:
                rsp = sess.get(b['url'])
                #print(sess.cookies.get_dict().get('lgc')) 
                #print(sess.cookies.get_dict().get('_nk_')) 
                user_name = sess.cookies.get_dict().get('_nk_')
                user_name = urllib.parse.unquote(user_name)
                user_name = codecs.decode(user_name,'unicode-escape')
                error = "登陆成功！"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
            else:
                button_name = "重新登录"
                error = "登录超时"
                return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)
                
        rsp = sess.get(generate_qrcode)
        if rsp == None:
            error = "获取二维码失败，请再次点击登录！" 
            button_name = "重新登录"
            return render_template('crawler.html', error1=error,button_name=button_name,user_name=user_name)

        b = json.loads(rsp.text)
        print(b)
        qr_img = b['url']
        lgToken = b['lgToken']
        button_name = "扫描完成"
        return render_template('crawler.html', qr_img=qr_img,button_name=button_name,user_name=user_name)

    button_name = "重新登录"
    return render_template('crawler.html', qr_img=qr_img,button_name=button_name,user_name=user_name)

def befor_pub_shangpin():
    global sess
    shangpin['params_sub_category']['_tb_token_'] = sess.cookies['_tb_token_']
    rsp = sess.get(shangpin['pub_url'],params=shangpin['params_sub_category'])
    #fle = open("step3.html", 'w')
    #fle.write(rsp.text)
    #fle.close()

def pub_shangpin():
    global sess
    shangpin['params_sub_category']['_tb_token_'] = sess.cookies['_tb_token_']
    rsp = sess.post(shangpin['pub_url'],params=shangpin['params_sub_category'],data=shangpin['data'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    if soup.title.text != "全球购官网直购":
        print("step4 failed\n")
        fle = open("step4.html", 'w')
        fle.write(rsp.text)
        fle.close()
        return None
    else:
        print("step4 success\n")
        return rsp

def get_choose_category():
    #提交url,进入选择类目页面
    global sess
    shangpin['params_sub_url']['_tb_token_'] = sess.cookies['_tb_token_']
    rsp = sess.get(shangpin['buyer_url'],params=shangpin['params_sub_url'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    soup_ = soup.find('div',attrs={'class':'form-group'})    
    if soup_ == None:
        print("step2 failed\n")
        fle = open("step2.html", 'w')
        fle.write(rsp.text)
        fle.close()
        return None
    else:
        print("step2 success\n")
        return rsp
    return None


def get_index():
    global sess
    rsp = sess.get(shangpin['buyer_url'])
    soup = BeautifulSoup(rsp.text,'html.parser')
    if soup.title.text != "全球购官网直购":
        print("step1 failed\n")
        fle = open("step1.html", 'w')
        fle.write(rsp.text)
        fle.close()
        return None
    else:
        print("step1 success\n")
        return rsp

def login_status(text):
    soup = BeautifulSoup(text,'html.parser')
    soup_ = soup.find('div',attrs={'id':'J_QuickLogin'})    
    print(soup)
    if soup_:
        return False   #offline
    else:
        return True    #online

def login_tb():
    global sess
    lsp = sess.post(tb_login['login_url'],
                       params=tb_login['login_params'],
                       data=tb_login['data'],
                       headers=tb_login['login_headers'])
    soup = BeautifulSoup(lsp.text,'html.parser')
    #if soup.title.text != "淘宝网 - 淘！我喜欢" or login_status(lsp.text) == False:
    if login_status(lsp.text) == False:
        fle = open("step0.html", 'w')
        fle.write(lsp.text)
        fle.close()
        print("login failed\n")
        return None
    else:
        print("login success\n")
        return lsp

def pub_shangpin_final():
    error_code = 0
    rsp = get_index()
    if rsp == None:
        error_code = 1
        return error_code
    rsp = get_choose_category()
    if rsp == None:
        error_code = 2
        return error_code
    befor_pub_shangpin()
    rsp = pub_shangpin()
    if rsp == None:
        error_code = 3
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
        app.run(host="192.168.8.198", port=8756, debug=True)
