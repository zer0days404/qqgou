#!/usr/bin/env python
import traceback
from flask import Flask, session, request
from flask import render_template
import requests
from bs4 import BeautifulSoup
app = Flask(__name__)

def gen_html(category):
    info = []
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.pinterest.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36'
        }

    url = 'https://www.pinterest.com/categories/' + category
    while True:
        try:
            req = requests.get(url,headers=headers)
            org_soup = BeautifulSoup(req.text,'html.parser')
            soup = org_soup.find('div',attrs={'class':'Grid Module hasFooter'})
            div_soup = soup.find_all('div',attrs={'class':'item'})
            for divs in div_soup:
                try:
                    #div_soup = soup.find('div',attrs={'class':'heightContainer'})
                    div = divs.find('div',attrs={'class':'Image Module pinUiImage'})
                    img_soup = div.find('img')
                    print(img_soup.get('src'))
                    img = img_soup.get('src')
                    div = divs.find('p',attrs={'class':'pinDescription'})
                    print(div.text.replace('\r','').strip().split('\n')[0])
                    des = div.text.replace('\r','').strip().split('\n')[0]
                    li = [img,des]
                    info.append(li)
                except:
                    print("%s" % (traceback.print_exc()))
                    continue
            if len(info) >4:
                break
        except:
            print("%s" % (traceback.print_exc()))
            break

    print(info)
    html_buf = '''<table border="1" cellpadding="0" cellspacing="0"><tr height="352">'''
    try:
        for i in range(0,5):
            html_buf += '''<td width="235" height="352"><img width="235" height="352" src="'''
            html_buf += info[i][0]
            html_buf += '''"</td>'''
        html_buf += '''</tr><tr>'''
        for i in range(0,5):
            html_buf += '''<td width="235">'''
            html_buf += info[i][1]
            html_buf += '''</td>'''
        html_buf += '''</tr></table>'''
    except:
        html_buf = '''抓取失败'''
        print("%s" % (traceback.print_exc()))
    return html_buf

@app.route('/<cate>', methods=['GET'])
def index(cate):
    html = gen_html(category=cate)
    return html

def run():
    app.run(host="192.168.8.108", port=1221,debug=True)

if __name__ == '__main__':
    run()
