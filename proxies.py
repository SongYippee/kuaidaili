# -*- coding: utf-8 -*-
# @Time    : 2018/11/20 14:36
# @Software: PyCharm

import sys
import time
import requests
from pyquery import PyQuery


class ProxyUtil(object):
    '''
    解析快代理网站，爬取代理ip信息
    '''

    def __init__(self):
        self.session = requests.Session()
        headers = {}
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Cache-Control'] = 'max-age=0'
        headers['DNT'] = '1'
        headers['Host'] = 'www.kuaidaili.com'
        headers['Pragma'] = 'no-cache'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        self.headers = headers
        self.total = None  # 一共多少页
        self.last_url = None  # 上一次爬取的网页的地址
        self.last_page_number = None  # 上一次爬取的网页的编号

    def __index(self):
        index_url = "https://www.kuaidaili.com/"
        response = self.session.get(index_url, headers=self.headers)
        print response.status_code, response.url
        free_url = "https://www.kuaidaili.com/free/"
        self.headers['Referer'] = index_url
        time.sleep(2)  # 必须休息，否则访问拒绝
        response = self.session.get(free_url, headers=self.headers)
        print response.status_code, response.url
        try:
            if response.status_code == 200:
                _, total = self.getTotalPages(response.content)
                self.total = int(total)
                lastPage, lastUrl = self.getLastPage()
                if not lastPage:
                    '''未曾访问过，解析网页内容'''
                    lines = self.parseIpInfo(response.content)
                    self.update_proxies(lines)
                    self.last_url = response.url
                    self.last_page_number = 1
                else:
                    '''访问过'''
                    self.last_url = lastUrl
                    self.last_page_number = lastPage
            else:
                print response.content
                self.exit()
        except:
            self.exit()

    def __retrive(self, pageIndex):
        url = "https://www.kuaidaili.com/free/inha/" + str(pageIndex) + "/"
        self.headers['Referer'] = self.last_url
        response = self.session.get(url, headers=self.headers)
        print response.status_code, response.url
        try:
            if response.status_code == 200:
                lines = self.parseIpInfo(response.content)
                self.update_proxies(lines)
                self.last_url = response.url
                self.last_page_number = pageIndex
            else:
                print response.content
                self.exit()
        except:
            self.exit()

    def retrive(self):
        try:
            self.__index()
            while self.last_page_number <= self.total:
                time.sleep(1)  # 必须休息，否则访问被拒绝
                self.__retrive(self.last_page_number + 1)
        except KeyboardInterrupt:
            self.exit()

    def parseIpInfo(self, htmlContent):
        lines = []
        try:
            page = PyQuery(htmlContent)
            trs = page('tbody tr')
            for tr in trs.items():
                line = tr('td').eq(0).text() + "," + tr('td').eq(1).text() + "," + tr('td').eq(2).text() + "," + tr(
                    'td').eq(
                    3).text() + "," + tr(
                    'td').eq(4).text() + "," + tr('td').eq(5).text() + "," + tr('td').eq(6).text() + "\n"
                line = line.encode('utf-8')
                lines.append(line)
        except:
            print "parse html content ERROR"
            print htmlContent
            self.exit()
        return lines

    def getTotalPages(self, htmlContent):
        current = None
        total = None
        try:
            page = PyQuery(htmlContent)
            hrefs = page('#listnav ul li a')
            for href in hrefs.items():
                if href('.active'):
                    current = href.text()
                else:
                    total = href.text()
        except:
            print "parse total page ERROR"
            print htmlContent
            self.exit()
        return (current, total)

    def update_history(self, url):
        '''
        将爬取过的url写入last_url文件，下次启动跳过爬过的url
        :param url:
        :return:
        '''
        with open('last_url', 'w') as file:
            file.write(url)
            file.close()

    def update_proxies(self, lines):
        '''
        将解析后的lines写入proxies.csv文件
        :param lines:
        :return:
        '''
        with open('proxies.csv', 'a') as file:
            file.writelines(lines)
            file.close()

    def getLastPage(self):
        line = None
        with open('last_url', 'r') as file:
            line = file.read(-1)
            file.close()
        if line:
            temp = line.split('/')
            return int(temp[-2]), line
        else:
            return None, None

    def exit(self):
        self.update_history(self.last_url)
        sys.exit(0)


p = ProxyUtil()
p.retrive()
