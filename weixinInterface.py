#!/usr/bin/python
#coding:utf-8
import hashlib
import web
import lxml
import time
import os
import json
import urllib
import re
import urllib2
from lxml import etree
import requests

class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="doushijiaxiang" #这里填写在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
    
    def POST(self):
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        mstype = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        
        #事件（订阅等）发生时，自动回复
        if mstype == "event":
            mscontent = xml.find("Event").text
            if mscontent == "subscribe":
                replayText = u'亲爱的朵，我爱你！   -亚飞'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
        
        #当用户发送文本内容时，机器人自动回复（调用图灵机器人网页api）
        if mstype == 'text':
            content=xml.find("Content").text #获得用户所输入的内容
        	
            if content ==u'知友':
				title1 = '知友们，中秋快乐！'
				description1 = '给知友的祝福。'
				xc = 'http://viewer.maka.im/k/J64391B8'
				pic = 'http://pic33.nipic.com/20130923/11927319_180343313383_2.jpg'
				return self.render.reply_pic(fromUser,toUser,title1,description1,pic,xc)
            
            if content ==u'朵' or content==u'朵朵':
				title1 = '亲爱的，端午快乐！'
				description1 = '给朵的祝福。'
				xct = 'http://viewer.maka.im/k/J64391B8'
				picurl1='http://meng-pic.stor.sinaapp.com/Capture.JPG'
				return self.render.reply_pic(fromUser,toUser,title1,description1,picurl1,xct)
			
    		#爬取心理FM的电台：心理FM。比如当用户输入关键字“电台”的时候，我们就自动回复心理FM的当天的电台音频
            if content==u'电台' or content == 'fm' or content == 'Fm' or content == 'FM':
                url = 'http://m.xinli001.com/fm/'
                fmre = urllib.urlopen(url).read()
                pa1 = re.compile(r'<head>.*?<title>(.*?)-心理FM</title>',re.S)
                ts1 = re.findall(pa1,fmre)
                pa3 = re.compile(r'var broadcast_url = "(.*?)", broadcastListUrl = "/fm/items/',re.S)
                ts3 = re.findall(pa3,fmre)
                
                req = urllib2.Request(ts3[0])
                response = urllib2.urlopen(req)
                redirectUrl = response.geturl()
                musicTitle = ts1[0]
                musicDes = ''
                musicURL = redirectUrl
                HQURL = 'http://m.xinli001.com/fm/'
                return self.render.reply_fm(fromUser,toUser,musicTitle,musicDes,musicURL,HQURL)
            
            if content==u'汽车':
            	replayText1=u'这是一篇汽车类文章'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replayText1)
            
            elif content==u'电影' or content==u'电影排行':
                douban_url = 'https://movie.douban.com/'
                douban_html = requests.get(douban_url).text
                c = re.compile(r' <a onclick="moreurl.*?href="(.*?)"[\s\S]*?src="(.*?)" alt="(.*?)" [\s\S]*?class="subject-rate">(.*?)</span>', re.S)
                DOUBAN = re.findall(c, douban_html)
                piaofang_url = 'http://www.cbooo.cn/boxOffice/GetHourBoxOffice?d=%s'%str(time.time()).split('.')[0]
                piaofang_json = requests.get(piaofang_url).text
                PIAOFANG = json.loads(piaofang_json)['data2']
                
                PIAOFANGS = []
                for piaofang in PIAOFANG:
                    PIAOFANGS.append((piaofang['MovieName'], float(piaofang['sumBoxOffice'])))
                PIAOFANGS = sorted(PIAOFANGS, key=lambda x: x[1], reverse=True)
                INFOS = []
                for piao in PIAOFANGS:
                    piaofang_name = piao[0]
                    for douban in DOUBAN:
                        douban = list(douban)
                        douban_name = douban[2]
                        if piaofang_name == douban_name:
                            douban.append(str("%.3f"%(piao[1]/10000.0)))
                            INFOS.append(douban)
                            break
                total_num = len(INFOS)
                if total_num>10:
                	num = 10
                else:
                	num = total_num
                return self.render.reply_morepic(fromUser,toUser,INFOS,num)
            
            
            else:
                key = '9fff84bd7a7f48f392b4d02233155246' ###图灵机器人的key
                api = 'http://www.tuling123.com/openapi/api?key=' + key + '&info='
                info = content.encode('UTF-8')
                url = api + info
                page = urllib.urlopen(url)
                html = page.read()
                dic_json = json.loads(html)
                reply_content = dic_json['text']
                return self.render.reply_text(fromUser,toUser,int(time.time()),reply_content)
    		