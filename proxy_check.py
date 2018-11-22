# -*- coding: utf-8 -*-
# @Time    : 2018/11/21 15:18
# @Software: PyCharm

import requests
from pyquery import PyQuery


def get_host_public_ip():
    url = 'https://www.ip.cn/'
    headers = {}
    headers[
        'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

    response = requests.get(url, headers=headers, timeout=6)
    if response.status_code == 200:
        page = PyQuery(response.content)
        for code in page('p code').items():
            if code.text().strip().find('.') > -1:
                return code.text().strip()
    else:
        print response.status_code


local_ip = get_host_public_ip()
print 'local ip is %s ' % (local_ip)


class ProxyUtil(object):
    def __init__(self):
        self.session = requests.session()
        self.headers = {}
        self.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        self.proxies = None

    def __check_https_proxy_active(self, proxy):
        try:
            url = "https://www.ipip.net/ip.html"
            response = self.session.get(url, headers=self.headers, proxies=proxy, timeout=10)

            def parse_html(http_status, htmlContent):
                page = PyQuery(htmlContent)
                if http_status == 403:
                    spans = page('body p span.cf-footer-item').items()
                    for span in spans:
                        if span.text().find('Your IP:') > -1:
                            parsed_ip = span.text().split(':')[1].strip()
                            if parsed_ip != local_ip:
                                print "this proxy %s is active" % (proxy.values()[0])
                                return True
                            else:
                                print "this proxy %s is active but not useful" % (proxy.values()[0])
                        else:
                            pass
                    return False
                elif http_status == 200:
                    hrefs = page("form input").items()
                    for href in hrefs:
                        parsed_ip = href.attr("value")
                        if parsed_ip != local_ip:
                            print "this proxy %s is active" % (proxy.values()[0])
                            return True
                        else:
                            print "this proxy %s is active but not useful" % (proxy.values()[0])
                    return False
                else:
                    print http_status
                    print htmlContent
                    return False

            return parse_html(response.status_code, response.content)
        except:
            print "this proxy %s is not active" % (proxy.values()[0])
            return False

    def __check_http_proxy_active(self, proxy):
        try:
            url = 'http://www.ip38.com/'
            response = requests.get(url, proxies=proxy,
                                    headers=self.headers, timeout=6)

            def parse_html(htmlContent):
                page = PyQuery(htmlContent)
                hrefs = page("span.right a").items()
                for href in hrefs:
                    parsed_ip = href.text().strip()
                    if parsed_ip != local_ip:
                        if parsed_ip != local_ip:
                            print "this proxy %s is active" % (proxy.values()[0])
                            return True
                else:
                    print "this proxy %s is active but not useful" % (proxy.values()[0])

            if response.status_code == 200:
                return parse_html(response.content)
            else:
                print response.status_code
                print response.content
                return False
        except:
            print "this proxy %s is not active" % (proxy.values()[0])
            return False

    def check_proxy_active(self, proxy):
        if 'http' in proxy.keys():
            return self.__check_http_proxy_active(proxy)
        else:
            return self.__check_https_proxy_active(proxy)


if __name__ == '__main__':
    proxy_util = ProxyUtil()
    proxy_util.check_proxy_active({'https': 'https://62.232.62.238:8080'})
    proxy_util.check_proxy_active({'https': 'https://115.154.135.174:1080'})
    proxy_util.check_proxy_active({'http': 'http://119.28.203.242:8000'})
