#!/usr/bin/python3
# coding=utf-8

import requests
import time
import re
import os
import json
import hashlib
import time
import random
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

"""
     * 经典模式
     * 技术联系人 陈荣江 17602115638 微信同号
     * 文档地址 https://portal.glocashpayment.com/#/integration/document
     * 商户后台 https://portal.glocashpayment.com/#/login
     *
     * 测试卡
     *   Visa | 4907639999990022 | 12/2020 | 029 paid
     *   MC   | 5546989999990033 | 12/2020 | 464 paid
     *   Visa | 4000000000000002 | 01/2022 | 237 | 14  3ds paid
     *   Visa | 4000000000000028 | 03/2022 | 999 | 54  3ds paid
     *   Visa | 4000000000000051 | 07/2022 | 745 | 94  3ds paid
     *   MC   | 5200000000000007 | 01/2022 | 356 | 34  3ds paid
     *   MC   | 5200000000000023 | 03/2022 | 431 | 74  3ds paid
     *   MC   | 5200000000000106 | 04/2022 | 578 | 104 3ds paid
     *
     *  想测试失败 可以填错年月日或者ccv即可
"""

host = ('0.0.0.0', 81)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        if (self.path == '/pay' or self.path == '/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(Glocash.pay()).encode())
    def do_POST(self):
        if (self.path == '/notify'):
            self.send_response(200)
            self.end_headers()
            l = self.headers['Content-length']
            p = self.rfile.read(int(l))
            self.wfile.write(Glocash.notify(str(p, "utf-8")).encode())
class Glocash():
    #TODO 请仔细查看TODO的注释 请仔细查看TODO的注释 请仔细查看TODO的注释
    SANDBOX_URL = 'https://sandbox.glocashpayment.com/gateway/payment/index' #TODO 测试秘钥 商户后台查看
    LIVE_URL = 'https://pay.glocashpayment.com/gateway/payment/index' #TODO 正式秘钥 商户后台查看(必须材料通过以后才能使用)
    SANDBOX_KEY = '9dc6a0682d7cb718fa140d0b8017a01c4e9a9820beeb45da020601a2e0a63514' #TODO 测试秘钥 商户后台查看
    LIVE_KEY = 'c2e38e7d93dbdd3efaa61028c3d27a1a2577df84fa62ae752df587b4f90b8ef7' #TODO 正式秘钥 商户后台查看(必须材料通过以后才能使用)
    def pay():
        se = requests.session()
        currentTime = str(time.time())
        currentRandom = str(random.randint(1000,9999))
        POST_DATA = {
            'REQ_SANDBOX': 1,  #TODO 是否开启测试模式 0 正式环境 1 测试环境
            'REQ_TIMES': currentTime, #请求时间
            'REQ_EMAIL': '2101653220@qq.com', #商户邮箱 商户后台申请的邮箱
            'REQ_INVOICE': 'TEST' + currentTime + currentRandom, #订单号
            'CUS_EMAIL': 'customer789@gmail.com', #客户邮箱
            'BIL_METHOD': 'C01', #请求方式
            'BIL_PRICE': '37.86', #价格
            'BIL_CURRENCY': 'USD', #币种
            'BIL_CC3DS': '1', #TODO 是否开启3ds 1 开启 0 不开启
            'URL_SUCCESS': 'https://www.merchant77.com/success.php?order=ORDER1234567890', #支付成功跳转地址
            'URL_FAILED': 'https://www.merchant77.com/failed.php?order=ORDER1234567890', #支付失败跳转地址
            'URL_NOTIFY': 'https://www.merchant77.com/notify.php?order=ORDER1234567890', #异步回调跳转地址
            'URL_PENDING': 'https://www.merchant77.com/pending.php?order=ORDER1234567890', #付款处理中的跳转地址
            'REQ_MERCHANT': 'MERCHANT-77 LTD.', #商户名
            'BIL_GOODSNAME': 'Smart Phone P238', #商品名称 必填 否则无法结算
            'BIL_QUANTITY': '1', #商品数量
        }
        if (POST_DATA['REQ_SANDBOX'] == 1):
            SECRET_KEY = Glocash.SANDBOX_KEY
            POST_URL = Glocash.SANDBOX_URL
        else:
            SECRET_KEY = Glocash.LIVE_KEY
            POST_URL = Glocash.LIVE_URL
        data =  SECRET_KEY + POST_DATA['REQ_TIMES'] + POST_DATA['REQ_EMAIL'] + POST_DATA['REQ_INVOICE'] + POST_DATA['CUS_EMAIL'] + POST_DATA['BIL_METHOD'] + POST_DATA['BIL_PRICE'] + POST_DATA['BIL_CURRENCY']
        POST_DATA['REQ_SIGN'] = hashlib.sha256(data.encode('utf-8')).hexdigest()
        text = se.post(POST_URL, data=POST_DATA).text.replace("'", '"').replace('/ ', '/')
        text = json.loads(text)
        return text
    def notify(data):
        jsonData = urllib.parse.parse_qs(data)
        if (jsonData['REQ_SANDBOX'][0] == 'ON' or jsonData['REQ_SANDBOX'][0] == '1'):
           SECRET_KEY = Glocash.SANDBOX_KEY
        else:
           SECRET_KEY = Glocash.LIVE_KEY
        str =  SECRET_KEY + jsonData['REQ_TIMES'][0] + jsonData['REQ_EMAIL'][0] + jsonData['CUS_EMAIL'][0] + jsonData['TNS_GCID'][0] + jsonData['BIL_STATUS'][0] + jsonData['BIL_METHOD'][0] + jsonData['PGW_PRICE'][0] + jsonData['PGW_CURRENCY'][0]
        sign = hashlib.sha256(str.encode('utf-8')).hexdigest()
        #签名校验
        if (sign != jsonData['REQ_SIGN'][0]):
            return 'false'
        #TODO 接下来是业务逻辑操作 比如修改订单状态 以及发货
        return 'true'
if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()






