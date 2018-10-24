#!/usr/bin/env python
#-*- coding: utf-8 -*-

#Created by DevDoge on 2018/3/23
import http.cookiejar as cookielib
import requests
import re
import time
import pymysql
import sys

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")

log_arr = []

def add2Log(log):
    log_arr.append(log)

# 保存至数据库
def save_db(log, status):
    db = pymysql.connect("localhost", "acfun", "acfun123", "acfun",charset="utf8")
    cursor = db.cursor()

    sql = "INSERT sign_table (log,`status`,time) VALUES ('{}',{},NOW())".format(log, status==200)

    print(log)

    # cursor.execute(sql)
    # db.commit()

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print("error")

    db.close()



agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"

headers = {
    "Host": "www.acfun.cn",
    "Origin": "http://www.acfun.cn",
    "Referer": "http://www.acfun.cn/login/",
    "User-Agent": agent
}

# 加载Cookies
try:
    session.cookies.load(ignore_discard=True)
    add2Log("use cookies")
except:
    add2Log("cookies can not be loaded")

# 检查Cookies的有效性
def check_status():
    response = session.get("http://www.acfun.cn/member/", headers=headers, allow_redirects=False)
    add2Log("check status:" + str(response.status_code))
    return response.status_code == 200


# 签到
def sign_action(username, password):
    if check_status():
        # 1521788623848
        # 1521789490.016982
        sign_url = "http://www.acfun.cn/webapi/record/actions/signin?channel=0&date="+str(int(time.time() * 1000))
        res = session.post(sign_url, headers=headers)

        add2Log("sign result:" + res.text)

        save_db('\n'.join(log_arr[::-1]), res.json()["code"])
    else:
        acfun_login(username, password)


# 登录
def acfun_login(username, password):

    if re.match("\w{6,}",username):
        post_url = "http://www.acfun.cn/login.aspx"
        post_data = {
            "username": username,
            "password": password
        }

        response = session.post(post_url, data=post_data, headers=headers)

        add2Log("login result" + response.text)

        session.cookies.save()
        print(session.cookies)
        print(response.cookies)

    sign_action(username, password)

if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) == 2:
        acfun_login(argv[0],argv[1])
    else:
        print("argv count should be 2")

sign_action("","")